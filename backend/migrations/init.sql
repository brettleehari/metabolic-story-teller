-- GlucoLens Database Initialization Script
-- This script creates all tables and sets up TimescaleDB hypertables

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ==================== USERS TABLE ====================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    date_of_birth DATE,
    diabetes_type VARCHAR(20),
    target_glucose_min NUMERIC(5,1) DEFAULT 70.0,
    target_glucose_max NUMERIC(5,1) DEFAULT 180.0,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== TIME-SERIES TABLES ====================

-- Glucose readings
CREATE TABLE IF NOT EXISTS glucose_readings (
    id BIGSERIAL,
    user_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    value NUMERIC(5,1) NOT NULL,
    source VARCHAR(50),
    device_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

-- Convert to hypertable
SELECT create_hypertable('glucose_readings', 'timestamp', if_not_exists => TRUE);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_glucose_user_time ON glucose_readings (user_id, timestamp DESC);

-- Sleep data
CREATE TABLE IF NOT EXISTS sleep_data (
    id BIGSERIAL,
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    sleep_start TIMESTAMPTZ NOT NULL,
    sleep_end TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER,
    deep_sleep_minutes INTEGER,
    rem_sleep_minutes INTEGER,
    light_sleep_minutes INTEGER,
    awake_minutes INTEGER,
    quality_score NUMERIC(3,1),
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, sleep_start)
);

SELECT create_hypertable('sleep_data', 'sleep_start', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_sleep_user_date ON sleep_data (user_id, date DESC);

-- Activities
CREATE TABLE IF NOT EXISTS activities (
    id BIGSERIAL,
    user_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    activity_type VARCHAR(50),
    duration_minutes INTEGER,
    intensity VARCHAR(20),
    calories_burned INTEGER,
    heart_rate_avg INTEGER,
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('activities', 'timestamp', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_activities_user_time ON activities (user_id, timestamp DESC);

-- Meals
CREATE TABLE IF NOT EXISTS meals (
    id BIGSERIAL,
    user_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    meal_type VARCHAR(20),
    carbs_grams NUMERIC(6,1),
    protein_grams NUMERIC(6,1),
    fat_grams NUMERIC(6,1),
    calories INTEGER,
    glycemic_load NUMERIC(4,1),
    description TEXT,
    photo_url VARCHAR(500),
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('meals', 'timestamp', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_meals_user_time ON meals (user_id, timestamp DESC);

-- ==================== ANALYTICS TABLES ====================

-- Daily aggregates
CREATE TABLE IF NOT EXISTS daily_aggregates (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    avg_glucose NUMERIC(5,1),
    min_glucose NUMERIC(5,1),
    max_glucose NUMERIC(5,1),
    std_glucose NUMERIC(5,2),
    time_in_range_percent NUMERIC(5,2),
    time_above_range_percent NUMERIC(5,2),
    time_below_range_percent NUMERIC(5,2),
    total_sleep_minutes INTEGER,
    sleep_quality_score NUMERIC(3,1),
    total_exercise_minutes INTEGER,
    total_carbs_grams NUMERIC(7,1),
    total_calories INTEGER,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_daily_agg_user_date ON daily_aggregates (user_id, date DESC);

-- Correlations
CREATE TABLE IF NOT EXISTS correlations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    factor_x VARCHAR(100),
    factor_y VARCHAR(100),
    correlation_coefficient NUMERIC(4,3),
    p_value NUMERIC(10,8),
    lag_days INTEGER DEFAULT 0,
    sample_size INTEGER,
    confidence_level VARCHAR(10),
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, factor_x, factor_y, lag_days)
);

-- Patterns
CREATE TABLE IF NOT EXISTS patterns (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    pattern_type VARCHAR(50),
    description TEXT,
    confidence NUMERIC(5,4),
    support NUMERIC(5,4),
    occurrences INTEGER,
    example_dates DATE[],
    metadata JSONB,
    discovered_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== SEED DATA ====================

-- Insert a test user
INSERT INTO users (id, email, password_hash, full_name, diabetes_type)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'test@glucolens.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyB.oK8fQu3e',  -- password: "test123"
    'Test User',
    'type1'
)
ON CONFLICT (id) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ GlucoLens database initialized successfully!';
END $$;
