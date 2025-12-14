-- Create Iceberg database
CREATE DATABASE IF NOT EXISTS local.db;

-- Create sample Iceberg table
CREATE TABLE IF NOT EXISTS local.db.sample_data (
    id BIGINT,
    name STRING,
    value DOUBLE,
    category STRING,
    created_at TIMESTAMP,
    year INT,
    month INT,
    day INT
) USING iceberg
PARTITIONED BY (year, month, day);

-- Create events table
CREATE TABLE IF NOT EXISTS local.db.events (
    event_id STRING,
    user_id STRING,
    event_type STRING,
    event_data STRING,
    timestamp TIMESTAMP,
    date DATE
) USING iceberg
PARTITIONED BY (days(date));

-- Create users table
CREATE TABLE IF NOT EXISTS local.db.users (
    user_id STRING,
    username STRING,
    email STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) USING iceberg;
