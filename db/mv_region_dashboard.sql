-- Materialized View pattern for MySQL (simulated via table + refresh proc + event)
-- Creates/refreshes `mv_region_dashboard` summarizing key KPIs per region

-- 1) Create table (idempotent)
CREATE TABLE IF NOT EXISTS mv_region_dashboard (
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

DELIMITER $$

-- 2) Refresh procedure: recompute MV from base tables
CREATE PROCEDURE sp_refresh_mv_region_dashboard()
BEGIN
    TRUNCATE TABLE mv_region_dashboard;

    INSERT INTO mv_region_dashboard (
        region_name, population, risk_level,
        active_alerts_count, highest_active_severity,
        total_resources_available, distributions_last_7d,
        latest_rainfall_mm, avg_rainfall_7d, last_refreshed
    )
    SELECT 
        ar.region_name,
        ar.population,
        ar.risk_level,
        COALESCE(a.alerts_active, 0) AS active_alerts_count,
        CASE COALESCE(a.max_sev_rank, 0)
            WHEN 4 THEN 'Critical'
            WHEN 3 THEN 'High'
            WHEN 2 THEN 'Moderate'
            WHEN 1 THEN 'Low'
            ELSE NULL
        END AS highest_active_severity,
        COALESCE(r.total_qty, 0) AS total_resources_available,
        COALESCE(d.qty_last_7d, 0) AS distributions_last_7d,
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
        SELECT x.region_name, x.latest_mm, y.avg_7d
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
    ) rain ON rain.region_name = ar.region_name;
END $$

DELIMITER ;

-- 3) Optional: schedule auto-refresh every 15 minutes
-- Note: requires event_scheduler enabled (SET GLOBAL event_scheduler = ON;)
CREATE EVENT IF NOT EXISTS ev_refresh_mv_region_dashboard
ON SCHEDULE EVERY 15 MINUTE
DO CALL sp_refresh_mv_region_dashboard();
