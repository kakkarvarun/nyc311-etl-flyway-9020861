-- V2__clean_and_optimize_nyc311.sql
DELETE FROM service_requests WHERE complaint_type IS NULL;
CREATE INDEX IF NOT EXISTS idx_borough ON service_requests(borough);
CREATE INDEX IF NOT EXISTS idx_complaint_type ON service_requests(complaint_type);