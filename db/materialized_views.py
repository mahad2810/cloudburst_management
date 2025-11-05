"""
Materialized Views utilities for Cloudburst Management System

Provides two approaches to maintain a precomputed, query-friendly summary
table (a.k.a. a materialized view pattern):

1) From the live MySQL database (recommended in production)
   - Creates and refreshes a summary table `mv_region_dashboard`
   - Intended to be called on a schedule (cron/Task Scheduler) or manually

2) From local CSVs (useful for offline demos or when DB is unavailable)
   - Reads CSVs from csv_sheets/
   - Produces the same summary either as a CSV or inserts into MySQL

Schema notes (expected columns based on README):
 - affected_regions(region_id, region_name, population, risk_level, warning_status, last_update, report_date)
 - alerts(alert_id, region, alert_message, severity, date_issued, expiry_date)
 - resources(resource_id, resource_type, quantity_available, location, status, last_restocked)
 - rainfall_data(id, region, date, rainfall_mm, temperature_c, humidity)
 - distribution_log(log_id, region_id, resource_id, quantity_sent, date_distributed, distributed_by, received_date)

The summary table `mv_region_dashboard` aggregates by region and includes:
 - region_name
 - population
 - risk_level
 - active_alerts_count (expiry_date >= CURDATE())
 - highest_active_severity (derived by a rank of Low<Moderate<High<Critical)
 - total_resources_available (sum by resources.location == region_name)
 - distributions_last_7d (sum quantity_sent in last 7 days)
 - latest_rainfall_mm
 - avg_rainfall_7d

"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple
import os
import pandas as pd
from datetime import datetime, timedelta

from .connection import DatabaseConnection, init_connection


MV_TABLE_NAME = "mv_region_dashboard"


@dataclass
class MVRow:
    region_name: str
    population: Optional[int]
    risk_level: Optional[str]
    active_alerts_count: int
    highest_active_severity: Optional[str]
    total_resources_available: int
    distributions_last_7d: int
    latest_rainfall_mm: Optional[float]
    avg_rainfall_7d: Optional[float]


def create_mv_table(db: DatabaseConnection) -> bool:
    """Create the materialized view table if it doesn't exist."""
    ddl = f"""
        CREATE TABLE IF NOT EXISTS {MV_TABLE_NAME} (
            region_name VARCHAR(255) PRIMARY KEY,
            population INT NULL,
            risk_level VARCHAR(50) NULL,
            active_alerts_count INT NOT NULL DEFAULT 0,
            highest_active_severity VARCHAR(20) NULL,
            total_resources_available INT NOT NULL DEFAULT 0,
            distributions_last_7d INT NOT NULL DEFAULT 0,
            latest_rainfall_mm DECIMAL(10,2) NULL,
            avg_rainfall_7d DECIMAL(10,2) NULL,
            last_refreshed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    """
    return db.execute_update(ddl)


def refresh_mv_from_db(db: DatabaseConnection) -> bool:
    """Refresh the MV by recomputing from base tables via SQL only.

    This uses a TRUNCATE + INSERT pattern to simulate a materialized view.
    """
    # Ensure table exists
    if not create_mv_table(db):
        return False

    # Clear existing data
    if not db.execute_update(f"TRUNCATE TABLE {MV_TABLE_NAME}"):
        return False

    # Insert recomputed rows
    insert_sql = f"""
        INSERT INTO {MV_TABLE_NAME} (
            region_name, population, risk_level,
            active_alerts_count, highest_active_severity,
            total_resources_available, distributions_last_7d,
            latest_rainfall_mm, avg_rainfall_7d, last_refreshed
        )
        SELECT 
            ar.region_name,
            ar.population,
            ar.risk_level,
            -- Active alerts count for region_name
            COALESCE(a.alerts_active, 0) AS active_alerts_count,
            -- Highest active severity label via rank mapping
            CASE COALESCE(a.max_sev_rank, 0)
                WHEN 4 THEN 'Critical'
                WHEN 3 THEN 'High'
                WHEN 2 THEN 'Moderate'
                WHEN 1 THEN 'Low'
                ELSE NULL
            END AS highest_active_severity,
            -- Total resources available mapped by location==region_name
            COALESCE(r.total_qty, 0) AS total_resources_available,
            -- Distributions last 7 days by region_id
            COALESCE(d.qty_last_7d, 0) AS distributions_last_7d,
            -- Latest rainfall and 7d average
            rain.latest_mm AS latest_rainfall_mm,
            rain.avg_7d AS avg_rainfall_7d,
            NOW() AS last_refreshed
        FROM affected_regions ar
        LEFT JOIN (
            SELECT 
                al.region AS region_name,
                COUNT(*) AS alerts_active,
                MAX(
                    CASE al.severity
                        WHEN 'Critical' THEN 4
                        WHEN 'High' THEN 3
                        WHEN 'Moderate' THEN 2
                        WHEN 'Low' THEN 1
                        ELSE 0
                    END
                ) AS max_sev_rank
            FROM alerts al
            WHERE al.expiry_date >= CURDATE()
            GROUP BY al.region
        ) a ON a.region_name = ar.region_name
        LEFT JOIN (
            SELECT location AS region_name, SUM(quantity_available) AS total_qty
            FROM resources
            GROUP BY location
        ) r ON r.region_name = ar.region_name
        LEFT JOIN (
            SELECT dl.region_id, SUM(dl.quantity_sent) AS qty_last_7d
            FROM distribution_log dl
            WHERE dl.date_distributed >= (CURDATE() - INTERVAL 7 DAY)
            GROUP BY dl.region_id
        ) d ON d.region_id = ar.region_id
        LEFT JOIN (
            -- Latest rainfall and 7-day avg per region
            SELECT x.region_name,
                   x.latest_mm,
                   y.avg_7d
            FROM (
                SELECT rd.region AS region_name,
                       SUBSTRING_INDEX(
                           GROUP_CONCAT(rd.rainfall_mm ORDER BY rd.date DESC), ',', 1
                       ) + 0.0 AS latest_mm
                FROM rainfall_data rd
                GROUP BY rd.region
            ) x
            LEFT JOIN (
                SELECT rd.region AS region_name,
                       AVG(rd.rainfall_mm) AS avg_7d
                FROM rainfall_data rd
                WHERE rd.date >= (CURDATE() - INTERVAL 7 DAY)
                GROUP BY rd.region
            ) y ON x.region_name = y.region_name
        ) rain ON rain.region_name = ar.region_name
    """

    return db.execute_update(insert_sql)


def refresh_mv_from_csv(
    csv_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv_sheets"),
    db: Optional[DatabaseConnection] = None,
    output_csv_path: Optional[str] = None,
) -> pd.DataFrame:
    """Build the MV dataframe from CSVs. Optionally write to DB and/or to a CSV.

    Args:
        csv_dir: directory containing rainfall_data.csv, affected_regions.csv, alerts.csv, resources.csv, distribution_log.csv
        db: if provided, will upsert rows into mv_region_dashboard
        output_csv_path: if provided, writes the MV to this CSV path
    Returns:
        The computed pandas DataFrame
    """
    # Load CSVs
    def _read(name):
        path = os.path.join(csv_dir, name)
        if not os.path.exists(path):
            return pd.DataFrame()
        return pd.read_csv(path)

    df_regions = _read("affected_regions.csv")
    df_alerts = _read("alerts.csv")
    df_resources = _read("resources.csv")
    df_rain = _read("rainfall_data.csv")
    df_dist = _read("distribution_log.csv")

    # Normalize column names that we rely on
    # Expected: region_name in affected_regions; alerts.region; resources.location; rainfall_data.region
    # Gracefully handle missing columns
    for df, cols in (
        (df_regions, ["region_id", "region_name", "population", "risk_level"]),
        (df_alerts, ["region", "severity", "expiry_date"]),
        (df_resources, ["location", "quantity_available"]),
        (df_rain, ["region", "date", "rainfall_mm"]),
        (df_dist, ["region_id", "quantity_sent", "date_distributed"]),
    ):
        for c in cols:
            if c not in df.columns:
                df[c] = pd.NA

    # Alerts aggregation
    if not df_alerts.empty:
        # ensure date parsing
        df_alerts["expiry_date"] = pd.to_datetime(df_alerts["expiry_date"], errors="coerce").dt.date
        today = pd.Timestamp("today").date()
        df_alerts_active = df_alerts[df_alerts["expiry_date"] >= today].copy()
        sev_rank = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4}
        df_alerts_active["sev_rank"] = df_alerts_active["severity"].map(sev_rank).fillna(0).astype(int)
        ag_alerts = df_alerts_active.groupby("region").agg(
            alerts_active=("region", "count"),
            max_sev_rank=("sev_rank", "max"),
        ).reset_index().rename(columns={"region": "region_name"})
    else:
        ag_alerts = pd.DataFrame(columns=["region_name", "alerts_active", "max_sev_rank"]) 

    # Resources aggregation
    if not df_resources.empty:
        ag_res = df_resources.groupby("location", dropna=False)["quantity_available"].sum().reset_index()
        ag_res = ag_res.rename(columns={"location": "region_name", "quantity_available": "total_qty"})
    else:
        ag_res = pd.DataFrame(columns=["region_name", "total_qty"]) 

    # Distribution aggregation (last 7 days)
    if not df_dist.empty:
        df_dist["date_distributed"] = pd.to_datetime(df_dist["date_distributed"], errors="coerce")
        cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=7)
        df_dist7 = df_dist[df_dist["date_distributed"] >= cutoff]
        ag_dist = df_dist7.groupby("region_id")["quantity_sent"].sum().reset_index().rename(columns={"quantity_sent": "qty_last_7d"})
    else:
        ag_dist = pd.DataFrame(columns=["region_id", "qty_last_7d"]) 

    # Rainfall aggregation: latest and 7d avg by region
    if not df_rain.empty:
        df_rain["date"] = pd.to_datetime(df_rain["date"], errors="coerce")
        latest = df_rain.sort_values(["region", "date"], ascending=[True, False]).drop_duplicates(["region"]) \
                        [["region", "rainfall_mm"]].rename(columns={"region": "region_name", "rainfall_mm": "latest_mm"})
        cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=7)
        rain7 = df_rain[df_rain["date"] >= cutoff]
        ag_rain7 = rain7.groupby("region")["rainfall_mm"].mean().reset_index().rename(columns={"region": "region_name", "rainfall_mm": "avg_7d"})
        rain = latest.merge(ag_rain7, on="region_name", how="left")
    else:
        rain = pd.DataFrame(columns=["region_name", "latest_mm", "avg_7d"]) 

    # Combine with regions (left anchor)
    mv = df_regions[["region_id", "region_name", "population", "risk_level"]].copy()
    mv = mv.merge(ag_alerts, on="region_name", how="left")
    mv = mv.merge(ag_res, on="region_name", how="left")
    mv = mv.merge(ag_dist, on="region_id", how="left")
    mv = mv.merge(rain, on="region_name", how="left")

    # Map sev rank to label
    rank_to_label = {4: "Critical", 3: "High", 2: "Moderate", 1: "Low"}
    mv["highest_active_severity"] = mv["max_sev_rank"].map(rank_to_label)

    # Final column selection and defaults
    mv = mv.rename(columns={
        "alerts_active": "active_alerts_count",
        "total_qty": "total_resources_available",
        "qty_last_7d": "distributions_last_7d",
        "latest_mm": "latest_rainfall_mm",
        "avg_7d": "avg_rainfall_7d",
    })

    for col, default in (
        ("active_alerts_count", 0),
        ("total_resources_available", 0),
        ("distributions_last_7d", 0),
    ):
        mv[col] = mv[col].fillna(default).astype(int)

    # Optionally persist to CSV
    if output_csv_path:
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        mv.to_csv(output_csv_path, index=False)

    # Optionally upsert into DB
    if db is not None:
        create_mv_table(db)
        db.execute_update(f"TRUNCATE TABLE {MV_TABLE_NAME}")

        # Prepare batch insert
        insert_stmt = f"""
            INSERT INTO {MV_TABLE_NAME}
            (region_name, population, risk_level, active_alerts_count, highest_active_severity,
             total_resources_available, distributions_last_7d, latest_rainfall_mm, avg_rainfall_7d, last_refreshed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        rows: List[Tuple] = []
        for _, r in mv.iterrows():
            rows.append((
                r.get("region_name"),
                None if pd.isna(r.get("population")) else int(r.get("population")),
                None if pd.isna(r.get("risk_level")) else str(r.get("risk_level")),
                int(r.get("active_alerts_count", 0)),
                None if pd.isna(r.get("highest_active_severity")) else str(r.get("highest_active_severity")),
                int(r.get("total_resources_available", 0)),
                int(r.get("distributions_last_7d", 0)),
                None if pd.isna(r.get("latest_rainfall_mm")) else float(r.get("latest_rainfall_mm")),
                None if pd.isna(r.get("avg_rainfall_7d")) else float(r.get("avg_rainfall_7d")),
            ))

        # Use the underlying cursor for executemany for performance
        try:
            db.cursor.executemany(insert_stmt, rows)
            db.connection.commit()
        except Exception as e:
            # Fallback row-by-row if needed
            for row in rows:
                db.execute_update(insert_stmt, row)

    return mv


if __name__ == "__main__":
    # Optional ad-hoc runner for local testing
    # Example: python -m db.materialized_views
    import argparse
    parser = argparse.ArgumentParser(description="Refresh materialized view (DB and/or CSV)")
    parser.add_argument("--from", dest="source", choices=["db", "csv"], default="db")
    parser.add_argument("--csv-dir", dest="csv_dir", default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "csv_sheets"))
    parser.add_argument("--output-csv", dest="output_csv", default=None)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--database", default="cloudburst_management")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    args = parser.parse_args()

    if args.source == "db":
        db = DatabaseConnection()
        if db.connect(host=args.host, database=args.database, user=args.user, password=args.password):
            ok = refresh_mv_from_db(db)
            print(f"Refresh from DB: {'OK' if ok else 'FAILED'}")
        else:
            print("DB connection failed")
    else:
        # CSV path; optionally write to CSV and/or DB if credentials provided
        df = refresh_mv_from_csv(csv_dir=args.csv_dir, output_csv_path=args.output_csv)
        print(f"Built MV from CSV with {len(df)} rows")
