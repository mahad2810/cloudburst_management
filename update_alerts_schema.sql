-- Update alerts table to support new severity levels
ALTER TABLE alerts MODIFY COLUMN severity ENUM('Low', 'Medium', 'High', 'Critical', 'Info', 'Warning', 'Severe') DEFAULT 'Low';

-- Truncate existing alerts to reload fresh data
TRUNCATE TABLE alerts;
