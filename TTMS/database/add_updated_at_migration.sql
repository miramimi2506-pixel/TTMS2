-- Migration to add updated_at column to timetable table
-- Run this after backing up your database

USE timetable_db4;

-- Add updated_at column to timetable table
ALTER TABLE timetable
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Update existing records to have a timestamp
UPDATE timetable SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL;

-- Create index on updated_at for better query performance
CREATE INDEX idx_timetable_updated_at ON timetable(updated_at);

-- Optional: Add trigger to automatically update timestamp (if not using ON UPDATE)
-- DELIMITER //
-- CREATE TRIGGER update_timetable_timestamp BEFORE UPDATE ON timetable
--     FOR EACH ROW SET NEW.updated_at = CURRENT_TIMESTAMP;
-- //
-- DELIMITER ;