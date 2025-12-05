-- Create backend database if it doesn't exist
SELECT 'CREATE DATABASE backend'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'backend')\gexec

-- Create mayan database if it doesn't exist
SELECT 'CREATE DATABASE mayan'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mayan')\gexec
