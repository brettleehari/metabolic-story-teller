# Recommended Health Data Additions

## 🎯 Core Additions (Requested)

### 1. **HbA1c (Glycated Hemoglobin)**
- Track 3-month average glucose
- Critical diabetes management metric
- Typically measured quarterly

### 2. **Biometric Data**
- Height (cm/inches)
- Weight (kg/lbs) - track over time
- Gender (male/female/other)
- BMI (auto-calculated)

---

## 💡 Highly Recommended Additions

### 3. **Medications & Insulin**
- Insulin doses (basal, bolus)
- Oral medications (Metformin, etc.)
- Dosage and timing
- **ML Benefit**: Correlate insulin/meds with glucose patterns

### 4. **Blood Pressure**
- Systolic/Diastolic
- Heart rate
- **ML Benefit**: Cardiovascular health correlation

### 5. **Body Metrics Timeline**
- Weight tracking (daily/weekly)
- Body fat percentage
- Waist circumference
- **ML Benefit**: Weight trends vs glucose control

### 6. **Lab Results**
- Cholesterol (Total, LDL, HDL, Triglycerides)
- Kidney function (Creatinine, eGFR)
- Liver enzymes
- Vitamin D levels
- **ML Benefit**: Comprehensive health picture

### 7. **Lifestyle Factors**
- Stress level (1-10 scale)
- Alcohol consumption
- Caffeine intake
- Water intake
- **ML Benefit**: PCMCI can find "stress → higher glucose" patterns

### 8. **Women's Health**
- Menstrual cycle tracking
- Pregnancy status
- **ML Benefit**: Hormonal effects on glucose

### 9. **Ketone Levels**
- Blood ketones (mmol/L)
- Urine ketones
- **ML Benefit**: DKA risk detection

### 10. **Insulin Doses**
- Basal insulin (long-acting)
- Bolus insulin (rapid-acting)
- Correction doses
- Insulin-to-carb ratio
- **ML Benefit**: Insulin sensitivity tracking

### 11. **CGM Sensor Info**
- Sensor start date
- Sensor expiry
- Calibration data
- **ML Benefit**: Sensor accuracy tracking

### 12. **Environmental Data**
- Weather (temperature, humidity)
- Altitude
- Time zone changes
- **ML Benefit**: Environmental effects on glucose

---

## 📊 Suggested Database Schema

### User Profile Enhancements
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS
    height_cm NUMERIC(5,2),              -- 150.5 cm
    weight_kg NUMERIC(5,2),              -- 70.5 kg
    gender VARCHAR(20),                   -- 'male', 'female', 'other', 'prefer_not_to_say'
    ethnicity VARCHAR(50),                -- Risk factor for diabetes
    diagnosis_date DATE,                  -- When diagnosed with diabetes
    insulin_dependent BOOLEAN DEFAULT false,
    cgm_type VARCHAR(50);                 -- 'dexcom_g7', 'freestyle_libre', etc.
```

### HbA1c Tracking (Time-series)
```sql
CREATE TABLE hba1c_readings (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    test_date DATE NOT NULL,
    hba1c_percent NUMERIC(3,1) NOT NULL,  -- 6.5%
    hba1c_mmol_mol INTEGER,               -- 48 mmol/mol (alternative unit)
    lab_name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Body Metrics Timeline
```sql
CREATE TABLE body_metrics (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL,
    weight_kg NUMERIC(5,2),
    body_fat_percent NUMERIC(4,1),
    muscle_mass_kg NUMERIC(5,2),
    waist_cm NUMERIC(5,1),
    bmi NUMERIC(4,1),                     -- Auto-calculated
    source VARCHAR(50),                    -- 'manual', 'smart_scale', 'apple_health'
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('body_metrics', 'timestamp');
```

### Blood Pressure
```sql
CREATE TABLE blood_pressure (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL,
    systolic INTEGER NOT NULL,            -- 120 mmHg
    diastolic INTEGER NOT NULL,           -- 80 mmHg
    heart_rate INTEGER,                   -- BPM
    source VARCHAR(50),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('blood_pressure', 'timestamp');
```

### Medications
```sql
CREATE TABLE medications (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    medication_name VARCHAR(100) NOT NULL,
    medication_type VARCHAR(50),          -- 'insulin_basal', 'insulin_bolus', 'oral', 'other'
    dosage VARCHAR(50),                   -- '10 units', '500mg', etc.
    frequency VARCHAR(50),                -- 'daily', 'twice_daily', 'with_meals'
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Insulin Doses (Time-series)
```sql
CREATE TABLE insulin_doses (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL,
    insulin_type VARCHAR(50) NOT NULL,    -- 'basal', 'bolus', 'correction'
    medication_name VARCHAR(100),         -- 'Humalog', 'Lantus', 'Novolog'
    dose_units NUMERIC(5,2) NOT NULL,
    carbs_grams NUMERIC(6,1),            -- For bolus doses
    correction_target NUMERIC(5,1),       -- Target glucose for correction
    source VARCHAR(50),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('insulin_doses', 'timestamp');
```

### Lab Results
```sql
CREATE TABLE lab_results (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    test_date DATE NOT NULL,
    test_type VARCHAR(100) NOT NULL,      -- 'lipid_panel', 'kidney_function', etc.
    results JSONB NOT NULL,               -- Flexible structure
    lab_name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Example results JSONB:
-- {
--   "total_cholesterol": 180,
--   "ldl": 100,
--   "hdl": 60,
--   "triglycerides": 100,
--   "unit": "mg/dL"
-- }
```

### Lifestyle Factors (Time-series)
```sql
CREATE TABLE lifestyle_logs (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL,
    stress_level INTEGER,                 -- 1-10 scale
    alcohol_units NUMERIC(4,1),           -- Standard drink units
    caffeine_mg INTEGER,                  -- mg of caffeine
    water_ml INTEGER,                     -- ml of water
    sleep_quality INTEGER,                -- 1-10 (redundant with sleep_data but for quick logging)
    notes TEXT,
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('lifestyle_logs', 'timestamp');
```

### Ketone Readings
```sql
CREATE TABLE ketone_readings (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL,
    ketone_level NUMERIC(4,1) NOT NULL,   -- mmol/L
    measurement_type VARCHAR(20),         -- 'blood', 'urine', 'breath'
    source VARCHAR(50),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('ketone_readings', 'timestamp');
```

### Menstrual Cycle (for women)
```sql
CREATE TABLE menstrual_cycles (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    cycle_start_date DATE NOT NULL,
    cycle_end_date DATE,
    period_length_days INTEGER,
    cycle_length_days INTEGER,
    flow_intensity VARCHAR(20),           -- 'light', 'moderate', 'heavy'
    symptoms JSONB,                       -- ['cramps', 'mood_changes', 'fatigue']
    notes TEXT
);
```

### Environmental Data
```sql
CREATE TABLE environmental_data (
    id BIGSERIAL,
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL,
    temperature_celsius NUMERIC(4,1),
    humidity_percent INTEGER,
    air_pressure_hpa INTEGER,
    altitude_meters INTEGER,
    location VARCHAR(100),                -- City/region
    timezone VARCHAR(50),
    source VARCHAR(50),                   -- 'weather_api', 'manual'
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('environmental_data', 'timestamp');
```

---

## 🤖 ML Benefits

### With These Additions, PCMCI Can Discover:

1. **"Weight loss → Better glucose control"**
2. **"Stress level → Higher glucose variability"**
3. **"Insulin dose timing → Post-meal glucose"**
4. **"Blood pressure medication → Glucose levels"**
5. **"Menstrual cycle phase → Glucose resistance"**
6. **"Caffeine intake → Afternoon glucose spike"**
7. **"Weather (hot days) → Dehydration → Higher glucose"**
8. **"Vitamin D levels → HbA1c improvement"**

### STUMPY Can Find:

1. **Recurring patterns in insulin sensitivity**
2. **Menstrual cycle glucose patterns**
3. **Medication timing patterns**
4. **Weight fluctuation patterns**

---

## 📱 Data Sources

These fields can be populated from:

1. **Apple HealthKit**: Weight, blood pressure, heart rate, steps
2. **Google Fit**: Similar to HealthKit
3. **Smart Scales**: Weight, body fat, muscle mass (Withings, Fitbit Aria)
4. **Blood Pressure Monitors**: Omron, Withings
5. **Lab Reports**: Manual entry or photo upload (OCR)
6. **Weather APIs**: OpenWeather, Weather.com
7. **Manual Entry**: User input forms

---

## 🎯 Priority Recommendations

### **Tier 1 (Must Have)**
- ✅ HbA1c tracking
- ✅ Height, Weight, Gender
- ✅ Insulin doses
- ✅ Medications

### **Tier 2 (High Value)**
- Blood pressure
- Body metrics timeline
- Stress levels
- Lab results

### **Tier 3 (Nice to Have)**
- Ketones
- Menstrual cycle
- Environmental data
- Caffeine/alcohol tracking

---

## 🔄 Implementation Plan

1. **Phase 1**: User profile + HbA1c + Body metrics
2. **Phase 2**: Medications + Insulin doses
3. **Phase 3**: Blood pressure + Lab results
4. **Phase 4**: Lifestyle factors + Advanced tracking

---

**Shall I proceed with implementing all Tier 1 and Tier 2 additions?**

This would give you:
- Complete biometric tracking
- Medication/insulin management
- Lab results tracking
- Comprehensive ML analysis capabilities
