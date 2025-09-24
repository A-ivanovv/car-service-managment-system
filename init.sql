-- Initialize database with proper settings
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'Europe/Sofia';

-- Create database if not exists (this will be handled by POSTGRES_DB)
-- But we can set some initial configurations here
