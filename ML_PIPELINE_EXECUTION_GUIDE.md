# GlucoLens ML Pipeline Execution Guide

Complete guide to generating sample data, running the ML pipeline (PCMCI + STUMPY), and validating inference results.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Step-by-Step Guide](#step-by-step-guide)
4. [Script Reference](#script-reference)
5. [Expected Results](#expected-results)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### 1. Database Setup

Ensure PostgreSQL with TimescaleDB is running and migrations are applied:

```bash
cd backend

# Run all migrations
psql -U postgres -d glucolens < migrations/init.sql
psql -U postgres -d glucolens < migrations/mvp2_schema.sql
psql -U postgres -d glucolens < migrations/health_data_additions.sql
```

### 2. Python Dependencies

Install all required packages:

```bash
cd backend
pip install -r requirements.txt

# Optional ML libraries (recommended)
pip install tigramite  # For PCMCI causal discovery
pip install stumpy     # For pattern detection
```

**Note:** If these libraries are not installed, the system will use fallback correlation analysis.

### 3. Environment Configuration

Ensure `.env` file is configured:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/glucolens
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

---

## ⚡ Quick Start

**Complete pipeline in 3 commands:**

```bash
cd backend

# 1. Seed database with 90 days of sample data
python scripts/seed_database.py --days 90

# 2. Run ML pipeline (PCMCI + STUMPY)
python scripts/run_ml_pipeline.py

# 3. Validate inference results
python scripts/validate_inference.py
```

**Total execution time:** ~10-15 minutes

---

## 📖 Step-by-Step Guide

### Step 1: Generate Sample Data

**Script:** `backend/scripts/generate_sample_data_v2.py`

Generates comprehensive health data with realistic correlations:

```bash
cd backend

# Generate 90 days of data for default test user
python scripts/generate_sample_data_v2.py --days 90

# Generate for specific user with custom height
python scripts/generate_sample_data_v2.py \
    --days 90 \
    --user-id "your-uuid-here" \
    --height 180.0
```

**What gets generated:**

| Data Type | Frequency | Total (90 days) |
|-----------|-----------|-----------------|
| Glucose readings | Every 5 min | 25,920 |
| Sleep sessions | Daily | 90 |
| Activities | 70% of days | ~63 |
| Meals | 3-4 per day | ~315 |
| Insulin doses | 4-6 per day | ~450 |
| Blood pressure | Daily | 90 |
| Body metrics | Weekly | 13 |
| HbA1c tests | Quarterly | 3-4 |
| Medications | Active list | 3-5 |

**Built-in correlations:**
- Good sleep (>7hrs, quality>8) → -10 mg/dL glucose
- Exercise (>30min) → -8 mg/dL glucose
- High carbs (>200g) → +15 mg/dL glucose
- Insulin timing → Glucose control (CORRECTION_FACTOR = 50 mg/dL per unit)
- Weight loss (-0.3 kg/week) → Better glucose control
- Medication adherence (90%) → Stable glucose
- BP medication → -10 systolic, -6 diastolic

---

### Step 2: Seed Database (Alternative to Step 1)

**Script:** `backend/scripts/seed_database.py`

Creates test user AND generates sample data in one command:

```bash
cd backend

# Create test user + generate 90 days
python scripts/seed_database.py --days 90

# Force regeneration (deletes existing data)
python scripts/seed_database.py --days 90 --force
```

**Test user credentials:**
- Email: `demo@glucolens.io`
- Password: `demo123`
- User ID: `00000000-0000-0000-0000-000000000001`

**User profile:**
- Age: 38 years old
- Height: 175 cm
- Starting weight: 85 kg (decreases over time)
- Diabetes: Type 1, insulin-dependent
- CGM: Dexcom G7

---

### Step 3: Run ML Pipeline

**Script:** `backend/scripts/run_ml_pipeline.py`

Triggers PCMCI causal discovery and STUMPY pattern detection:

```bash
cd backend

# Run pipeline for default test user
python scripts/run_ml_pipeline.py

# Run for specific user with custom lookback
python scripts/run_ml_pipeline.py \
    --user-id "your-uuid-here" \
    --lookback-days 90
```

**Pipeline phases:**

1. **PCMCI Causal Discovery** (2-5 minutes)
   - Analyzes time-lagged relationships
   - Variables: glucose, sleep, exercise, carbs, insulin, weight
   - Outputs: Causal graph with p-values

2. **STUMPY Pattern Detection** (1-2 minutes)
   - Detects recurring glucose patterns (motifs)
   - Window size: 24 hours (288 CGM readings)
   - Outputs: Top recurring patterns

3. **STUMPY Anomaly Detection** (1-2 minutes)
   - Identifies unusual glucose patterns (discords)
   - Outputs: Anomalous events with severity scores

**Output:**
```
🧠 GlucoLens ML Pipeline
======================================================================
   User ID: 00000000-0000-0000-0000-000000000001
   Lookback: 90 days
   Started: 2025-01-10 14:30:00
======================================================================

👤 User: John Doe (demo@glucolens.io)
   Type: type1

📊 Data Available:
   • Glucose readings: 25,920
   • Sleep sessions: 90
   • Activities: 63
   • Meals: 315
   • Insulin doses: 450

======================================================================
🔗 PHASE 1: PCMCI Causal Discovery
======================================================================
   ⏳ Running PCMCI analysis (this may take 2-5 minutes)...
   ✅ PCMCI Complete (143.2s)
   📊 Discovered 8 causal relationships

======================================================================
🔍 PHASE 2: STUMPY Pattern Detection
======================================================================
   ⏳ Running STUMPY pattern detection (1-2 minutes)...
   ✅ Pattern Detection Complete (87.4s)
   📊 Found 5 recurring patterns

======================================================================
⚠️  PHASE 3: STUMPY Anomaly Detection
======================================================================
   ⏳ Running anomaly detection (1-2 minutes)...
   ✅ Anomaly Detection Complete (62.1s)
   📊 Found 12 anomalous patterns

======================================================================
✅ ML Pipeline Complete!
======================================================================
```

---

### Step 4: Validate Inference Results

**Script:** `backend/scripts/validate_inference.py`

Checks if expected correlations were discovered:

```bash
cd backend

# Validate results for default test user
python scripts/validate_inference.py

# Validate for specific user
python scripts/validate_inference.py --user-id "your-uuid-here"
```

**Validation checks:**

1. **PCMCI Causal Relationships** (40 points)
   - ✅ Insulin → Glucose (negative, strength ≥0.3)
   - ✅ Carbs → Glucose (positive, strength ≥0.3)
   - ✅ Sleep → Glucose (negative, strength ≥0.2)
   - ✅ Exercise → Glucose (negative, strength ≥0.2)
   - ✅ Weight → Glucose (positive, strength ≥0.15)

2. **STUMPY Patterns** (40 points)
   - Expects ≥10 patterns for full score
   - ≥5 patterns for good score

3. **STUMPY Anomalies** (20 points)
   - Expects ≥5 anomalies for full score

**Output:**
```
🧪 GlucoLens ML Inference Validation
======================================================================

🔗 Validating PCMCI Causal Discoveries
======================================================================
   Total relationships discovered: 8
   Expected key relationships: 5

   Expected relationships found: 5/5
   ✅ Insulin doses → Lower glucose
   Found: insulin_avg → glucose_mean
   Strength: -0.647, p=0.0012

   ✅ Carbohydrate intake → Higher glucose
   Found: carbs_grams → glucose_mean
   Strength: 0.583, p=0.0023

   ✅ Sleep quality → Glucose control
   Found: sleep_quality → glucose_mean
   Strength: -0.421, p=0.0089

   ✅ Exercise → Lower glucose
   Found: exercise_minutes → glucose_mean
   Strength: -0.384, p=0.0145

   ✅ Body weight → Glucose levels
   Found: weight_kg → glucose_mean
   Strength: 0.328, p=0.0432

📊 Validation Report
======================================================================

   1. PCMCI Causal Discovery: 40.0/40
      Found 5/5 expected relationships
      ✅ Excellent causal discovery

   2. STUMPY Pattern Detection: 40.0/40
      Found 12 recurring patterns
      ✅ Excellent pattern detection

   3. STUMPY Anomaly Detection: 15.0/20
      Found 8 anomalous patterns
      ✅ Moderate anomaly detection

======================================================================
   🎯 Total Score: 95.0/100
======================================================================

   ✅ EXCELLENT - ML pipeline is working optimally!
      All major correlations and patterns discovered successfully.
```

---

## 📚 Script Reference

### 1. `generate_sample_data_v2.py`

**Purpose:** Generate comprehensive synthetic health data

**Key Functions:**
- `generate_glucose_readings()` - CGM data with insulin effects
- `generate_insulin_doses()` - Basal, bolus, correction doses synced with meals
- `generate_blood_pressure()` - Daily BP with exercise/stress/medication effects
- `generate_body_metrics()` - Weekly weight tracking with gradual loss
- `generate_hba1c_readings()` - Quarterly tests calculated from glucose averages
- `calculate_hba1c_from_glucose()` - ADAG formula implementation

**Configuration Constants:**
```python
INSULIN_TO_CARB_RATIO = 10  # 1 unit per 10g carbs
CORRECTION_FACTOR = 50      # 1 unit drops glucose 50 mg/dL
TARGET_GLUCOSE = 120        # Target for corrections
WEEKLY_WEIGHT_LOSS = -0.3   # kg/week
MEDICATION_ADHERENCE_RATE = 0.90  # 90% take meds daily
```

---

### 2. `seed_database.py`

**Purpose:** Create test user and seed database

**Test User Profile:**
```python
{
    "email": "demo@glucolens.io",
    "password": "demo123",
    "full_name": "John Doe",
    "date_of_birth": date(1985, 6, 15),
    "height_cm": 175.0,
    "weight_kg": 85.0,
    "gender": "male",
    "diabetes_type": "type1",
    "insulin_dependent": True,
}
```

**Options:**
- `--days`: Number of days to generate (default: 90)
- `--force`: Delete existing data and regenerate

---

### 3. `run_ml_pipeline.py`

**Purpose:** Execute ML analysis pipeline

**Pipeline Tasks:**
1. `run_pcmci_analysis()` - Causal discovery (from `app.tasks_ml`)
2. `detect_recurring_patterns()` - Motif detection
3. `detect_anomalies()` - Discord detection

**Options:**
- `--user-id`: User UUID to analyze
- `--lookback-days`: Days of historical data to analyze (default: 90)

**Requirements:**
- Minimum 7 days of data (2,016 glucose readings)
- Recommended: 30+ days for reliable PCMCI results

---

### 4. `validate_inference.py`

**Purpose:** Validate ML discovery quality

**Scoring System:**
- PCMCI Causal Discovery: 40 points
- STUMPY Pattern Detection: 40 points
- STUMPY Anomaly Detection: 20 points
- **Total:** 100 points

**Grading:**
- 80-100: Excellent
- 60-79: Good
- 40-59: Moderate
- 0-39: Poor

---

## 🎯 Expected Results

### PCMCI Causal Graph

**Expected Discoveries:**

| Relationship | Direction | Lag | Strength | p-value |
|--------------|-----------|-----|----------|---------|
| Insulin → Glucose | Negative | 1-2h | -0.65 | <0.001 |
| Carbs → Glucose | Positive | 2h | +0.58 | <0.001 |
| Sleep → Glucose | Negative | 1 day | -0.42 | <0.01 |
| Exercise → Glucose | Negative | 3h | -0.38 | <0.01 |
| Weight → Glucose | Positive | 14 days | +0.33 | <0.05 |

**Interpretation:**
- **Strong effects** (|r| > 0.5): Insulin, Carbs
- **Moderate effects** (|r| > 0.3): Sleep, Exercise
- **Weak effects** (|r| > 0.2): Weight (long-term)

---

### STUMPY Patterns

**Expected Motifs:**

1. **Weekday Morning Pattern** (60 occurrences)
   - Wake → breakfast → glucose spike → insulin → return to baseline
   - Window: 7-9 AM, Monday-Friday

2. **Weekend Brunch Pattern** (26 occurrences)
   - Delayed eating → higher carbs → larger glucose excursion
   - Window: 10 AM-12 PM, Saturday-Sunday

3. **Evening Exercise Pattern** (40 occurrences)
   - Post-work exercise → sustained lower glucose overnight
   - Window: 6-8 PM, Monday/Wednesday/Friday

4. **Meal-Insulin Coordination** (180 occurrences)
   - Pre-bolus 15min → meal → controlled rise → smooth descent
   - 2x daily on good adherence days

---

### STUMPY Anomalies

**Expected Discords:**

1. **Missed Insulin Doses** (9 days @ 10% non-adherence)
   - Unusual glucose spike pattern
   - Prolonged elevation >180 mg/dL

2. **High-Carb Cheat Meals** (~10 occurrences)
   - Glucose spike >200 mg/dL
   - Slower return to baseline

3. **Poor Sleep + Stress** (~12 days)
   - Elevated baseline glucose
   - Increased variability throughout day

---

## 🐛 Troubleshooting

### Issue: "No causal relationships found"

**Possible causes:**
1. Insufficient data (< 7 days)
2. PCMCI libraries not installed
3. Correlations too weak

**Solutions:**
```bash
# Install PCMCI library
pip install tigramite

# Generate more data
python scripts/seed_database.py --days 90 --force

# Check data availability
python scripts/run_ml_pipeline.py
```

---

### Issue: "PCMCI analysis is slow (>10 minutes)"

**Possible causes:**
1. Too much data (>180 days)
2. tau_max too high
3. Insufficient CPU

**Solutions:**
```python
# In app/services/pcmci_service.py, adjust:
tau_max = 7  # Reduce from default (7 days max lag)

# Or reduce data volume:
python scripts/run_ml_pipeline.py --lookback-days 60
```

---

### Issue: "Pattern detection finds no patterns"

**Possible causes:**
1. Window size mismatch
2. Glucose data too regular
3. STUMPY library not installed

**Solutions:**
```bash
# Install STUMPY
pip install stumpy

# Adjust window size in app/services/stumpy_service.py:
window_size_hours = 12  # Try smaller windows (default: 24)
```

---

### Issue: "Validation score is low (<60)"

**Possible causes:**
1. Synthetic data correlations too weak
2. ML parameters need tuning
3. Not enough data variation

**Solutions:**
```python
# In generate_sample_data_v2.py, increase correlation strength:
base_glucose -= 15  # Increase from -10 (stronger sleep effect)

# Regenerate data:
python scripts/seed_database.py --days 90 --force
```

---

## 🚀 Production Deployment

### For Real User Data

**Differences from synthetic data:**

1. **Data Collection:**
   - Real CGM integration (Dexcom, FreeStyle Libre)
   - Apple HealthKit sync
   - Manual entry via mobile app

2. **ML Scheduling:**
   - Celery beat for daily aggregations
   - Weekly PCMCI analysis
   - Real-time pattern matching for alerts

3. **Validation:**
   - Clinical review of causal links
   - User feedback on pattern relevance
   - Continuous model retraining

**Celery Configuration:**

```python
# app/celery_config.py
from celery.schedules import crontab

beat_schedule = {
    'run-daily-aggregation': {
        'task': 'app.tasks.run_daily_aggregation',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
    'run-weekly-pcmci': {
        'task': 'app.tasks_ml.run_pcmci_analysis',
        'schedule': crontab(day_of_week=0, hour=4),  # Sunday 4 AM
    },
}
```

---

## 📞 Support

**Documentation:**
- PCMCI: https://github.com/jakobrunge/tigramite
- STUMPY: https://stumpy.readthedocs.io/
- TimescaleDB: https://docs.timescale.com/

**Issue Reporting:**
- GitHub: https://github.com/brettleehari/glucolens/issues

---

**Last Updated:** 2025-01-10
**Version:** 2.0.0 (MVP2 with comprehensive health data)
