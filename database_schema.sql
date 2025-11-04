-- ================================================================
-- CLOUDBURST MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ================================================================
-- DBMS Lab Project
-- Author: Mahad (@mahad2810)
-- Description: Complete database schema for disaster management system
-- ================================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS cloudburst_management;
USE cloudburst_management;

-- ================================================================
-- TABLE 1: RAINFALL DATA
-- Stores historical rainfall measurements and weather conditions
-- ================================================================
CREATE TABLE IF NOT EXISTS rainfall_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    region VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    rainfall_mm DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    temperature_c DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for query optimization
    INDEX idx_region (region),
    INDEX idx_date (date),
    INDEX idx_rainfall (rainfall_mm)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Historical rainfall and weather data';

-- ================================================================
-- TABLE 2: AFFECTED REGIONS
-- Tracks regions affected by cloudbursts with risk assessments
-- ================================================================
CREATE TABLE IF NOT EXISTS affected_regions (
    region_id INT PRIMARY KEY AUTO_INCREMENT,
    region_name VARCHAR(100) NOT NULL UNIQUE,
    population INT DEFAULT 0,
    risk_level ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Low',
    warning_status BOOLEAN DEFAULT FALSE,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    report_date DATE,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Indexes for query optimization
    INDEX idx_risk_level (risk_level),
    INDEX idx_warning_status (warning_status),
    INDEX idx_region_name (region_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Regions affected by disasters';

-- ================================================================
-- TABLE 3: ALERTS
-- Manages disaster alerts and warnings for different regions
-- ================================================================
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    region VARCHAR(100) NOT NULL,
    alert_message TEXT NOT NULL,
    severity ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Low',
    date_issued DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATETIME,
    status ENUM('Active', 'Expired', 'Resolved') DEFAULT 'Active',
    
    -- Indexes for query optimization
    INDEX idx_severity (severity),
    INDEX idx_region (region),
    INDEX idx_status (status),
    INDEX idx_date_issued (date_issued),
    INDEX idx_expiry_date (expiry_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Disaster alerts and warnings';

-- ================================================================
-- TABLE 4: RESOURCES
-- Inventory management for disaster relief resources
-- ================================================================
CREATE TABLE IF NOT EXISTS resources (
    resource_id INT PRIMARY KEY AUTO_INCREMENT,
    resource_type VARCHAR(100) NOT NULL,
    quantity_available INT NOT NULL DEFAULT 0,
    location VARCHAR(100),
    status ENUM('Available', 'Low Stock', 'Depleted') DEFAULT 'Available',
    last_restocked DATE,
    unit VARCHAR(50) DEFAULT 'units',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for query optimization
    INDEX idx_location (location),
    INDEX idx_status (status),
    INDEX idx_resource_type (resource_type),
    INDEX idx_quantity (quantity_available)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Disaster relief resource inventory';

-- ================================================================
-- TABLE 5: DISTRIBUTION LOG
-- Tracks resource distribution to affected areas
-- ================================================================
CREATE TABLE IF NOT EXISTS distribution_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    region_id INT,
    resource_id INT,
    quantity_sent INT NOT NULL,
    date_distributed DATE NOT NULL,
    received_date DATE,
    status ENUM('Pending', 'In Transit', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints for referential integrity
    FOREIGN KEY (region_id) REFERENCES affected_regions(region_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes for query optimization
    INDEX idx_status (status),
    INDEX idx_date_distributed (date_distributed),
    INDEX idx_region_id (region_id),
    INDEX idx_resource_id (resource_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Resource distribution tracking';

-- ================================================================
-- SAMPLE DATA INSERTION
-- ================================================================

-- Insert sample regions
INSERT INTO affected_regions (region_name, population, risk_level, warning_status, report_date, latitude, longitude) VALUES
('Uttarakhand', 10116752, 'Critical', TRUE, '2024-01-15', 30.0668, 79.0193),
('Himachal Pradesh', 6856509, 'High', TRUE, '2024-01-15', 31.1048, 77.1734),
('Jammu and Kashmir', 12548926, 'High', TRUE, '2024-01-16', 33.7782, 76.5762),
('Maharashtra', 112374333, 'Medium', FALSE, '2024-01-18', 19.7515, 75.7139),
('Kerala', 33406061, 'Medium', FALSE, '2024-01-20', 10.8505, 76.2711),
('Karnataka', 61130704, 'Low', FALSE, '2024-01-22', 15.3173, 75.7139);

-- Insert sample resources
INSERT INTO resources (resource_type, quantity_available, location, status, last_restocked, unit) VALUES
('Food Packets', 5000, 'Dehradun Warehouse', 'Available', '2024-01-10', 'packets'),
('Water Bottles', 10000, 'Dehradun Warehouse', 'Available', '2024-01-10', 'bottles'),
('Medical Kits', 500, 'Shimla Hospital', 'Available', '2024-01-12', 'kits'),
('Blankets', 2000, 'Srinagar Camp', 'Available', '2024-01-08', 'pieces'),
('Tents', 300, 'Mumbai Relief Center', 'Low Stock', '2024-01-05', 'units'),
('Medicines', 1500, 'Kochi Medical Center', 'Available', '2024-01-14', 'boxes');

-- Insert sample alerts
INSERT INTO alerts (region, alert_message, severity, date_issued, expiry_date, status) VALUES
('Uttarakhand', 'Heavy rainfall expected in next 48 hours. High risk of flash floods and landslides.', 'Critical', NOW(), DATE_ADD(NOW(), INTERVAL 2 DAY), 'Active'),
('Himachal Pradesh', 'Moderate to heavy rainfall forecasted. Travel advisory issued for hilly areas.', 'High', NOW(), DATE_ADD(NOW(), INTERVAL 3 DAY), 'Active'),
('Jammu and Kashmir', 'Cloudburst warning for upper regions. Residents advised to stay alert.', 'High', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), 'Active'),
('Maharashtra', 'Monsoon activity intensifying. Coastal areas on watch.', 'Medium', NOW(), DATE_ADD(NOW(), INTERVAL 5 DAY), 'Active');

-- Insert sample rainfall data
INSERT INTO rainfall_data (region, date, rainfall_mm, temperature_c, humidity) VALUES
('Uttarakhand', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 145.5, 18.5, 85.2),
('Uttarakhand', DATE_SUB(CURDATE(), INTERVAL 2 DAY), 98.3, 19.2, 82.1),
('Himachal Pradesh', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 112.8, 16.8, 88.5),
('Himachal Pradesh', DATE_SUB(CURDATE(), INTERVAL 2 DAY), 87.5, 17.5, 84.3),
('Jammu and Kashmir', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 95.2, 15.2, 86.7),
('Maharashtra', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 42.3, 28.5, 75.4),
('Kerala', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 68.9, 26.8, 82.5),
('Karnataka', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 35.7, 25.3, 70.2);

-- ================================================================
-- USEFUL VIEWS
-- ================================================================

-- View: Active alerts with region details
CREATE OR REPLACE VIEW active_alerts_view AS
SELECT 
    a.alert_id,
    a.region,
    a.alert_message,
    a.severity,
    a.date_issued,
    a.expiry_date,
    ar.population,
    ar.risk_level
FROM alerts a
LEFT JOIN affected_regions ar ON a.region = ar.region_name
WHERE a.status = 'Active' AND a.expiry_date >= CURDATE()
ORDER BY 
    CASE a.severity
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;

-- View: Resource inventory summary
CREATE OR REPLACE VIEW resource_inventory_summary AS
SELECT 
    resource_type,
    SUM(quantity_available) as total_quantity,
    COUNT(DISTINCT location) as locations,
    COUNT(*) as stock_entries,
    MAX(last_restocked) as last_restocked_date
FROM resources
GROUP BY resource_type;

-- View: Distribution statistics by region
CREATE OR REPLACE VIEW distribution_stats_by_region AS
SELECT 
    ar.region_name,
    ar.population,
    ar.risk_level,
    COUNT(dl.log_id) as total_distributions,
    SUM(dl.quantity_sent) as total_quantity_sent,
    COUNT(CASE WHEN dl.status = 'Delivered' THEN 1 END) as completed_distributions,
    COUNT(CASE WHEN dl.status = 'Pending' THEN 1 END) as pending_distributions
FROM affected_regions ar
LEFT JOIN distribution_log dl ON ar.region_id = dl.region_id
GROUP BY ar.region_id, ar.region_name, ar.population, ar.risk_level;

-- ================================================================
-- STORED PROCEDURES
-- ================================================================

-- Procedure: Add new alert
DELIMITER //
CREATE PROCEDURE add_alert(
    IN p_region VARCHAR(100),
    IN p_message TEXT,
    IN p_severity ENUM('Low', 'Medium', 'High', 'Critical'),
    IN p_expiry_days INT
)
BEGIN
    INSERT INTO alerts (region, alert_message, severity, expiry_date)
    VALUES (p_region, p_message, p_severity, DATE_ADD(NOW(), INTERVAL p_expiry_days DAY));
END //
DELIMITER ;

-- Procedure: Update resource stock
DELIMITER //
CREATE PROCEDURE update_resource_stock(
    IN p_resource_id INT,
    IN p_quantity_change INT
)
BEGIN
    DECLARE new_quantity INT;
    
    UPDATE resources 
    SET quantity_available = quantity_available + p_quantity_change
    WHERE resource_id = p_resource_id;
    
    SELECT quantity_available INTO new_quantity
    FROM resources 
    WHERE resource_id = p_resource_id;
    
    -- Update status based on quantity
    UPDATE resources
    SET status = CASE
        WHEN new_quantity = 0 THEN 'Depleted'
        WHEN new_quantity < 100 THEN 'Low Stock'
        ELSE 'Available'
    END
    WHERE resource_id = p_resource_id;
END //
DELIMITER ;

-- ================================================================
-- TRIGGERS
-- ================================================================

-- Trigger: Update resource status after distribution
DELIMITER //
CREATE TRIGGER after_distribution_insert
AFTER INSERT ON distribution_log
FOR EACH ROW
BEGIN
    UPDATE resources
    SET quantity_available = quantity_available - NEW.quantity_sent
    WHERE resource_id = NEW.resource_id;
    
    UPDATE resources
    SET status = CASE
        WHEN quantity_available = 0 THEN 'Depleted'
        WHEN quantity_available < 100 THEN 'Low Stock'
        ELSE 'Available'
    END
    WHERE resource_id = NEW.resource_id;
END //
DELIMITER ;

-- ================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ================================================================

-- Composite indexes for common queries
CREATE INDEX idx_region_date ON rainfall_data(region, date);
CREATE INDEX idx_severity_status ON alerts(severity, status);
CREATE INDEX idx_location_status ON resources(location, status);

-- ================================================================
-- GRANT PERMISSIONS (Adjust as needed)
-- ================================================================

-- Create application user (optional)
-- CREATE USER 'cloudburst_app'@'localhost' IDENTIFIED BY 'secure_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON cloudburst_management.* TO 'cloudburst_app'@'localhost';
-- FLUSH PRIVILEGES;

-- ================================================================
-- END OF SCHEMA
-- ================================================================
