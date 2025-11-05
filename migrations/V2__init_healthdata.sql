-- V2__init_healthdata.sql
CREATE TABLE IF NOT EXISTS healthdata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(50),
    reading_type VARCHAR(50),
    reading_value DECIMAL(10,2),
    reading_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);