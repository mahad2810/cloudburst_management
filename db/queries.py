"""
SQL Query Helpers
Pre-defined queries for common database operations
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd


class QueryHelper:
    """Helper class containing SQL queries for the Cloudburst Management System"""
    
    # ==================== RAINFALL DATA QUERIES ====================
    
    @staticmethod
    def get_all_rainfall_data():
        """Get all rainfall records"""
        return """
            SELECT id, region, date, rainfall_mm, temperature_c, humidity
            FROM rainfall_data
            ORDER BY date DESC
        """
    
    @staticmethod
    def get_rainfall_by_region(region: str):
        """Get rainfall data for a specific region"""
        return f"""
            SELECT id, region, date, rainfall_mm, temperature_c, humidity
            FROM rainfall_data
            WHERE region = '{region}'
            ORDER BY date DESC
        """
    
    @staticmethod
    def get_rainfall_by_date_range(start_date: str, end_date: str):
        """Get rainfall data within date range"""
        return f"""
            SELECT id, region, date, rainfall_mm, temperature_c, humidity
            FROM rainfall_data
            WHERE date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY date DESC
        """
    
    @staticmethod
    def get_rainfall_summary():
        """Get rainfall statistics summary"""
        return """
            SELECT 
                COUNT(DISTINCT region) as total_regions,
                AVG(rainfall_mm) as avg_rainfall,
                MAX(rainfall_mm) as max_rainfall,
                MIN(rainfall_mm) as min_rainfall,
                COUNT(*) as total_records
            FROM rainfall_data
        """
    
    @staticmethod
    def get_top_rainfall_regions(limit: int = 10):
        """Get regions with highest rainfall"""
        return f"""
            SELECT region, SUM(rainfall_mm) as total_rainfall
            FROM rainfall_data
            GROUP BY region
            ORDER BY total_rainfall DESC
            LIMIT {limit}
        """
    
    @staticmethod
    def get_rainfall_trends():
        """Get rainfall trends over time"""
        return """
            SELECT 
                DATE_FORMAT(date, '%Y-%m') as month,
                region,
                AVG(rainfall_mm) as avg_rainfall
            FROM rainfall_data
            GROUP BY month, region
            ORDER BY month DESC
        """
    
    # ==================== AFFECTED REGIONS QUERIES ====================
    
    @staticmethod
    def get_all_affected_regions():
        """Get all affected regions"""
        return """
            SELECT region_id, region_name, population, risk_level, 
                   warning_status, last_update, report_date
            FROM affected_regions
            ORDER BY risk_level DESC, region_name
        """
    
    @staticmethod
    def get_high_risk_regions():
        """Get regions with high or critical risk"""
        return """
            SELECT region_id, region_name, population, risk_level, 
                   warning_status, last_update
            FROM affected_regions
            WHERE risk_level IN ('High', 'Critical')
            ORDER BY risk_level DESC
        """
    
    @staticmethod
    def get_regions_with_warnings():
        """Get regions with active warnings"""
        return """
            SELECT region_id, region_name, population, risk_level, last_update
            FROM affected_regions
            WHERE warning_status = 1
            ORDER BY risk_level DESC
        """
    
    @staticmethod
    def get_region_risk_distribution():
        """Get distribution of regions by risk level"""
        return """
            SELECT risk_level, COUNT(*) as count
            FROM affected_regions
            GROUP BY risk_level
        """
    
    # ==================== RESOURCES QUERIES ====================
    
    @staticmethod
    def get_all_resources():
        """Get all resources"""
        return """
            SELECT resource_id, resource_type, quantity_available, 
                   location, status, last_restocked
            FROM resources
            ORDER BY resource_type, location
        """
    
    @staticmethod
    def get_resources_by_status(status: str):
        """Get resources by status"""
        return f"""
            SELECT resource_id, resource_type, quantity_available, 
                   location, status, last_restocked
            FROM resources
            WHERE status = '{status}'
            ORDER BY resource_type
        """
    
    @staticmethod
    def get_resources_by_location(location: str):
        """Get resources at a specific location"""
        return f"""
            SELECT resource_id, resource_type, quantity_available, 
                   status, last_restocked
            FROM resources
            WHERE location = '{location}'
            ORDER BY resource_type
        """
    
    @staticmethod
    def get_resource_summary():
        """Get resource statistics"""
        return """
            SELECT 
                COUNT(*) as total_resource_types,
                SUM(quantity_available) as total_quantity,
                COUNT(DISTINCT location) as total_locations
            FROM resources
        """
    
    @staticmethod
    def get_low_stock_resources(threshold: int = 100):
        """Get resources with low stock"""
        return f"""
            SELECT resource_id, resource_type, quantity_available, 
                   location, status
            FROM resources
            WHERE quantity_available < {threshold} AND status != 'Depleted'
            ORDER BY quantity_available ASC
        """
    
    @staticmethod
    def get_resource_distribution():
        """Get resource distribution by type"""
        return """
            SELECT resource_type, SUM(quantity_available) as total_quantity
            FROM resources
            GROUP BY resource_type
            ORDER BY total_quantity DESC
        """
    
    # ==================== ALERTS QUERIES ====================
    
    @staticmethod
    def get_all_alerts():
        """Get all alerts"""
        return """
            SELECT alert_id, region, alert_message, severity, 
                   date_issued, expiry_date
            FROM alerts
            ORDER BY date_issued DESC
        """
    
    @staticmethod
    def get_active_alerts():
        """Get currently active alerts"""
        return """
            SELECT alert_id, region, alert_message, severity, 
                   date_issued, expiry_date
            FROM alerts
            WHERE expiry_date >= CURDATE()
            ORDER BY severity DESC, date_issued DESC
        """
    
    @staticmethod
    def get_alerts_by_severity(severity: str):
        """Get alerts by severity level"""
        return f"""
            SELECT alert_id, region, alert_message, severity, 
                   date_issued, expiry_date
            FROM alerts
            WHERE severity = '{severity}'
            ORDER BY date_issued DESC
        """
    
    @staticmethod
    def get_alerts_by_region(region: str):
        """Get alerts for a specific region"""
        return f"""
            SELECT alert_id, region, alert_message, severity, 
                   date_issued, expiry_date
            FROM alerts
            WHERE region = '{region}'
            ORDER BY date_issued DESC
        """
    
    @staticmethod
    def get_alert_severity_distribution():
        """Get distribution of alerts by severity"""
        return """
            SELECT severity, COUNT(*) as count
            FROM alerts
            WHERE expiry_date >= CURDATE()
            GROUP BY severity
        """
    
    # ==================== DISTRIBUTION LOG QUERIES ====================
    
    @staticmethod
    def get_all_distributions():
        """Get all distribution records"""
        return """
            SELECT 
                dl.log_id,
                ar.region_name,
                r.resource_type,
                dl.quantity_sent,
                dl.date_distributed,
                dl.distributed_by,
                dl.received_date
            FROM distribution_log dl
            JOIN affected_regions ar ON dl.region_id = ar.region_id
            JOIN resources r ON dl.resource_id = r.resource_id
            ORDER BY dl.date_distributed DESC
        """
    
    @staticmethod
    def get_distributions_by_region(region_id: int):
        """Get distributions for a specific region"""
        return f"""
            SELECT 
                dl.log_id,
                r.resource_type,
                dl.quantity_sent,
                dl.date_distributed,
                dl.distributed_by,
                dl.received_date
            FROM distribution_log dl
            JOIN resources r ON dl.resource_id = r.resource_id
            WHERE dl.region_id = {region_id}
            ORDER BY dl.date_distributed DESC
        """
    
    @staticmethod
    def get_distributions_by_date_range(start_date: str, end_date: str):
        """Get distributions within date range"""
        return f"""
            SELECT 
                dl.log_id,
                ar.region_name,
                r.resource_type,
                dl.quantity_sent,
                dl.date_distributed,
                dl.distributed_by
            FROM distribution_log dl
            JOIN affected_regions ar ON dl.region_id = ar.region_id
            JOIN resources r ON dl.resource_id = r.resource_id
            WHERE dl.date_distributed BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY dl.date_distributed DESC
        """
    
    @staticmethod
    def get_distribution_summary():
        """Get distribution statistics"""
        return """
            SELECT 
                COUNT(*) as total_distributions,
                SUM(quantity_sent) as total_quantity_distributed,
                COUNT(DISTINCT region_id) as regions_served
            FROM distribution_log
        """
    
    @staticmethod
    def get_region_distribution_summary():
        """Get distribution summary by region"""
        return """
            SELECT 
                ar.region_name,
                COUNT(*) as distribution_count,
                SUM(dl.quantity_sent) as total_received
            FROM distribution_log dl
            JOIN affected_regions ar ON dl.region_id = ar.region_id
            GROUP BY ar.region_name
            ORDER BY total_received DESC
        """
    
    # ==================== INSERT QUERIES ====================
    
    @staticmethod
    def insert_rainfall_data():
        """Insert new rainfall record"""
        return """
            INSERT INTO rainfall_data 
            (region, date, rainfall_mm, temperature_c, humidity)
            VALUES (%s, %s, %s, %s, %s)
        """
    
    @staticmethod
    def insert_resource():
        """Insert new resource"""
        return """
            INSERT INTO resources 
            (resource_type, quantity_available, location, status, last_restocked)
            VALUES (%s, %s, %s, %s, %s)
        """
    
    @staticmethod
    def insert_alert():
        """Insert new alert"""
        return """
            INSERT INTO alerts 
            (region, alert_message, severity, date_issued, expiry_date)
            VALUES (%s, %s, %s, %s, %s)
        """
    
    @staticmethod
    def insert_distribution():
        """Insert new distribution log"""
        return """
            INSERT INTO distribution_log 
            (region_id, resource_id, quantity_sent, date_distributed, distributed_by, received_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
    
    # ==================== UPDATE QUERIES ====================
    
    @staticmethod
    def update_resource_quantity():
        """Update resource quantity"""
        return """
            UPDATE resources 
            SET quantity_available = %s, status = %s, last_restocked = %s
            WHERE resource_id = %s
        """
    
    @staticmethod
    def update_region_risk():
        """Update region risk level"""
        return """
            UPDATE affected_regions 
            SET risk_level = %s, warning_status = %s, last_update = %s
            WHERE region_id = %s
        """
    
    # ==================== DELETE QUERIES ====================
    
    @staticmethod
    def delete_alert():
        """Delete alert"""
        return "DELETE FROM alerts WHERE alert_id = %s"
    
    @staticmethod
    def delete_resource():
        """Delete resource"""
        return "DELETE FROM resources WHERE resource_id = %s"
    
    # ==================== UTILITY QUERIES ====================
    
    @staticmethod
    def get_unique_regions():
        """Get list of unique regions from rainfall_data"""
        return """
            SELECT DISTINCT region 
            FROM rainfall_data 
            ORDER BY region
        """
    
    @staticmethod
    def get_unique_locations():
        """Get list of unique resource locations"""
        return """
            SELECT DISTINCT location 
            FROM resources 
            ORDER BY location
        """
