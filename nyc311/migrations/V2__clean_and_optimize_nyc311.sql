-- V2__clean_and_optimize_nyc311.sql
-- Safe to run before ETL; table is empty now.
DELETE FROM service_requests WHERE complaint_type IS NULL;

-- Create indexes (MySQL doesn't support IF NOT EXISTS here)
CREATE INDEX idx_borough ON service_requests(borough);
CREATE INDEX idx_complaint_type ON service_requests(complaint_type);
