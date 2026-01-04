-- Create databases for evo-ai and evolution-api (PostgreSQL 15 compatible)
-- This script runs as the 'postgres' superuser

-- Create evo_ai database (if it doesn't exist)
-- Note: This will fail if the database already exists, but that's OK during init
CREATE DATABASE evo_ai;

-- Create evolution_db database (if it doesn't exist)
-- Note: This will fail if the database already exists, but that's OK during init
CREATE DATABASE evolution_db;
