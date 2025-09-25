-- Car Service Management System Database Initialization
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (this is handled by POSTGRES_DB env var)
-- But we can add any additional setup here

-- Set timezone
SET timezone = 'Europe/Sofia';

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO car_service_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO car_service_user;

-- Log the initialization
DO $$
BEGIN
    RAISE NOTICE 'Car Service Management System database initialized successfully!';
    RAISE NOTICE 'Database: car_service_db';
    RAISE NOTICE 'User: car_service_user';
    RAISE NOTICE 'Timezone: Europe/Sofia';
    RAISE NOTICE 'Character encoding: UTF-8';
END $$;
