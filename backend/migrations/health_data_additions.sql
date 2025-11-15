-- Health Data Additions Migration
-- Adds HbA1c tracking, medications, insulin doses, blood pressure, and body metrics

-- =====================================================
-- 1. Update users table with biometric data
-- =====================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS height_cm NUMERIC(5, 2);
ALTER TABLE users ADD COLUMN IF NOT EXISTS weight_kg NUMERIC(5, 2);
ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS diagnosis_date DATE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS insulin_dependent BOOLEAN DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS ethnicity VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS cgm_type VARCHAR(50);

COMMENT ON COLUMN users.height_cm IS 'Height in centimeters (e.g., 170.5)';
COMMENT ON COLUMN users.weight_kg IS 'Current weight in kilograms (e.g., 70.5)';
COMMENT ON COLUMN users.gender IS 'Gender: male, female, other, prefer_not_to_say';
COMMENT ON COLUMN users.diagnosis_date IS 'Date when diabetes was diagnosed';
COMMENT ON COLUMN users.insulin_dependent IS 'Whether user requires insulin';
COMMENT ON COLUMN users.ethnicity IS 'Ethnicity (risk factor for diabetes)';
COMMENT ON COLUMN users.cgm_type IS 'CGM device type: dexcom_g7, freestyle_libre, etc.';

-- =====================================================
-- 2. HbA1c readings table
-- =====================================================

CREATE TABLE IF NOT EXISTS hba1c_readings (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    test_date DATE NOT NULL,
    hba1c_percent NUMERIC(3, 1) NOT NULL,
    hba1c_mmol_mol INTEGER,
    lab_name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hba1c_user_id ON hba1c_readings(user_id);
CREATE INDEX IF NOT EXISTS idx_hba1c_test_date ON hba1c_readings(user_id, test_date DESC);

COMMENT ON TABLE hba1c_readings IS 'HbA1c test results tracking 3-month average glucose';
COMMENT ON COLUMN hba1c_readings.hba1c_percent IS 'HbA1c percentage (e.g., 6.5%)';
COMMENT ON COLUMN hba1c_readings.hba1c_mmol_mol IS 'HbA1c in mmol/mol (e.g., 48) - alternative unit';

-- =====================================================
-- 3. Medications table
-- =====================================================

CREATE TABLE IF NOT EXISTS medications (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    medication_name VARCHAR(100) NOT NULL,
    medication_type VARCHAR(50),
    dosage VARCHAR(50),
    frequency VARCHAR(50),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_medications_user_id ON medications(user_id);
CREATE INDEX IF NOT EXISTS idx_medications_active ON medications(user_id, is_active);

COMMENT ON TABLE medications IS 'Medications and insulin prescriptions';
COMMENT ON COLUMN medications.medication_type IS 'Type: insulin_basal, insulin_bolus, oral, other';
COMMENT ON COLUMN medications.frequency IS 'Frequency: daily, twice_daily, with_meals, etc.';

-- =====================================================
-- 4. Insulin doses table (time-series)
-- =====================================================

CREATE TABLE IF NOT EXISTS insulin_doses (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    insulin_type VARCHAR(50) NOT NULL,
    medication_name VARCHAR(100),
    dose_units NUMERIC(5, 2) NOT NULL,
    carbs_grams NUMERIC(6, 1),
    correction_target NUMERIC(5, 1),
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

-- Create TimescaleDB hypertable
SELECT create_hypertable('insulin_doses', 'timestamp', if_not_exists => TRUE);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_insulin_user_time ON insulin_doses(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_insulin_type ON insulin_doses(user_id, insulin_type, timestamp DESC);

COMMENT ON TABLE insulin_doses IS 'Time-series insulin dose records';
COMMENT ON COLUMN insulin_doses.insulin_type IS 'Type: basal, bolus, correction';
COMMENT ON COLUMN insulin_doses.dose_units IS 'Insulin dose in units (e.g., 10.5)';
COMMENT ON COLUMN insulin_doses.carbs_grams IS 'Carbohydrates for bolus dose calculation';
COMMENT ON COLUMN insulin_doses.correction_target IS 'Target glucose level for correction dose';

-- =====================================================
-- 5. Blood pressure table (time-series)
-- =====================================================

CREATE TABLE IF NOT EXISTS blood_pressure (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    systolic INTEGER NOT NULL,
    diastolic INTEGER NOT NULL,
    heart_rate INTEGER,
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

-- Create TimescaleDB hypertable
SELECT create_hypertable('blood_pressure', 'timestamp', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_blood_pressure_user_time ON blood_pressure(user_id, timestamp DESC);

COMMENT ON TABLE blood_pressure IS 'Time-series blood pressure readings';
COMMENT ON COLUMN blood_pressure.systolic IS 'Systolic pressure in mmHg (e.g., 120)';
COMMENT ON COLUMN blood_pressure.diastolic IS 'Diastolic pressure in mmHg (e.g., 80)';
COMMENT ON COLUMN blood_pressure.heart_rate IS 'Heart rate in BPM';

-- =====================================================
-- 6. Body metrics table (time-series)
-- =====================================================

CREATE TABLE IF NOT EXISTS body_metrics (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    weight_kg NUMERIC(5, 2),
    body_fat_percent NUMERIC(4, 1),
    muscle_mass_kg NUMERIC(5, 2),
    waist_cm NUMERIC(5, 1),
    bmi NUMERIC(4, 1),
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

-- Create TimescaleDB hypertable
SELECT create_hypertable('body_metrics', 'timestamp', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_body_metrics_user_time ON body_metrics(user_id, timestamp DESC);

COMMENT ON TABLE body_metrics IS 'Time-series body composition and weight tracking';
COMMENT ON COLUMN body_metrics.weight_kg IS 'Weight in kilograms';
COMMENT ON COLUMN body_metrics.body_fat_percent IS 'Body fat percentage';
COMMENT ON COLUMN body_metrics.muscle_mass_kg IS 'Muscle mass in kilograms';
COMMENT ON COLUMN body_metrics.waist_cm IS 'Waist circumference in centimeters';
COMMENT ON COLUMN body_metrics.bmi IS 'Body Mass Index (auto-calculated or manual)';

-- =====================================================
-- Grant permissions (adjust as needed)
-- =====================================================

-- Grant permissions on new tables to your application user
-- GRANT ALL PRIVILEGES ON TABLE hba1c_readings TO glucolens_app;
-- GRANT ALL PRIVILEGES ON TABLE medications TO glucolens_app;
-- GRANT ALL PRIVILEGES ON TABLE insulin_doses TO glucolens_app;
-- GRANT ALL PRIVILEGES ON TABLE blood_pressure TO glucolens_app;
-- GRANT ALL PRIVILEGES ON TABLE body_metrics TO glucolens_app;

-- =====================================================
-- Rollback script (if needed)
-- =====================================================

-- To rollback this migration, run:
-- DROP TABLE IF EXISTS body_metrics CASCADE;
-- DROP TABLE IF EXISTS blood_pressure CASCADE;
-- DROP TABLE IF EXISTS insulin_doses CASCADE;
-- DROP TABLE IF EXISTS medications CASCADE;
-- DROP TABLE IF EXISTS hba1c_readings CASCADE;
-- ALTER TABLE users DROP COLUMN IF EXISTS height_cm;
-- ALTER TABLE users DROP COLUMN IF EXISTS weight_kg;
-- ALTER TABLE users DROP COLUMN IF EXISTS gender;
-- ALTER TABLE users DROP COLUMN IF EXISTS diagnosis_date;
-- ALTER TABLE users DROP COLUMN IF EXISTS insulin_dependent;
-- ALTER TABLE users DROP COLUMN IF EXISTS ethnicity;
-- ALTER TABLE users DROP COLUMN IF EXISTS cgm_type;
