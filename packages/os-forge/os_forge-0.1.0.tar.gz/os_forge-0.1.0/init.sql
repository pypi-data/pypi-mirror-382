-- OS Forge Database Initialization Script
-- This script is run when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (already handled by POSTGRES_DB env var)
-- CREATE DATABASE os_forge;

-- Connect to the os_forge database
\c os_forge;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tables (these will be created by the application, but we can add indexes here)
-- The actual table creation is handled by SQLAlchemy in main.py

-- Create indexes for better performance
-- These will be created after the tables are created by the application

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE policy_guard TO policy_guard;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO policy_guard;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO policy_guard;

-- Set timezone
SET timezone = 'UTC';

