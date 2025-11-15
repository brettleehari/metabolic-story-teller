# Sample Data Pipeline Plan - GlucoLens ML Inference

## 🎯 Objective
Generate comprehensive synthetic health data with realistic correlations that flows through the entire ML pipeline (PCMCI + STUMPY) to produce meaningful causal insights and pattern discoveries.

---

## 📊 Current State Analysis

### Existing Sample Data Generator
**File:** `backend/scripts/generate_sample_data.py`

**Current Coverage:**
- ✅ Glucose readings (288/day, 5-min intervals)
- ✅ Sleep data (duration, quality, stages)
- ✅ Activities (type, duration, intensity, calories)
- ✅ Meals (macros, calories, glycemic load)

**Built-in Correlations:**
```
Good sleep (>7hrs, quality>8) → -10 mg/dL glucose
Exercise (>30min)              → -8 mg/dL glucose
High carbs (>200g)             → +15 mg/dL glucose
```

**Data Volume:** 90 days × 288 glucose readings = 25,920 CGM readings + ~360 lifestyle events

---

## 🆕 New Health Data to Add

### 1. **HbA1c Readings** (Quarterly Lab Results)
**Frequency:** Every 90-120 days (3-4 readings over 90 days)
**Fields:** test_date, hba1c_percent, hba1c_mmol_mol, lab_name

**Correlation Design:**
```python
avg_glucose = average(glucose_readings, period=90_days)
hba1c_percent = (avg_glucose + 46.7) / 28.7  # ADAG formula
# With realistic noise: ±0.3%
```

**Expected Pattern:** HbA1c should track the 90-day average glucose level accurately, validating long-term glycemic control.

---

### 2. **Medications** (Active Prescriptions)
**Frequency:** 2-5 active medications (static for 90 days)
**Types:**
- Insulin (basal): "Lantus 20 units daily"
- Insulin (bolus): "Humalog with meals"
- Oral medication: "Metformin 1000mg twice daily"
- BP medication: "Lisinopril 10mg daily" (if BP elevated)

**Correlation Design:**
- Medication adherence affects glucose stability
- BP medication presence correlates with BP readings

---

### 3. **Insulin Doses** (Time-series)
**Frequency:** 4-6 times per day
- **Basal:** 1x daily (usually evening, ~20 units)
- **Bolus:** 3x daily with meals (5-15 units, proportional to carbs)
- **Correction:** Occasional when glucose >180 mg/dL

**Correlation Design:**
```python
# Bolus calculation
insulin_to_carb_ratio = 10  # 1 unit per 10g carbs
bolus_dose = meal_carbs / insulin_to_carb_ratio

# Correction calculation
correction_factor = 50  # 1 unit drops glucose 50 mg/dL
if glucose > 180:
    correction_dose = (glucose - 120) / correction_factor

# Effect: Insulin dose → -50 mg/dL per unit over 3-4 hours
```

**Expected Pattern:**
- PCMCI should discover: `insulin_bolus(lag=-1 hour) → glucose_drop`
- STUMPY should find recurring meal-insulin-glucose patterns

---

### 4. **Blood Pressure** (Time-series)
**Frequency:** Daily (morning readings)
**Fields:** systolic, diastolic, heart_rate

**Correlation Design:**
```python
base_systolic = 125  # Slightly elevated (pre-hypertension)
base_diastolic = 82

# Correlations:
if stress_day:
    systolic += 10
    diastolic += 5

if exercise_yesterday:
    systolic -= 5
    diastolic -= 3

if high_sodium_meal:
    systolic += 8

# BP medication effect
if on_bp_medication:
    systolic -= 10
    diastolic -= 6
```

**Expected Pattern:**
- PCMCI: `stress → BP_increase`, `exercise(lag=-1 day) → BP_decrease`
- Potential discovery: `high_BP → glucose_variability` (stress hormone effect)

---

### 5. **Body Metrics** (Weight & Composition)
**Frequency:** Weekly (every 7 days)
**Fields:** weight_kg, body_fat_percent, bmi, muscle_mass_kg

**Correlation Design:**
```python
starting_weight = 85.0 kg
starting_body_fat = 28.0%

# Gradual weight loss trend: -0.3 kg/week (healthy rate)
# Influenced by:
weekly_weight_change = -0.3  # Base trend

if avg_exercise_minutes > 200:  # Active week
    weekly_weight_change -= 0.2

if avg_calories < 2000:  # Calorie deficit
    weekly_weight_change -= 0.15

# Weight loss improves glucose control
if weight_change < -2.0:  # Lost 2+ kg
    glucose_improvement = -5 mg/dL
```

**Expected Pattern:**
- PCMCI: `weight_decrease(lag=-2 weeks) → glucose_improvement`
- STUMPY: Weekly weigh-in pattern on same day

---

## 🔗 Multi-Variable Causal Relationships

### Complex Correlations to Build In:

1. **Sleep → Exercise → Glucose Cascade**
   ```
   Poor sleep (quality<6) → 50% less exercise next day
   Less exercise → +5 mg/dL glucose
   Total effect: Poor sleep(lag=-1) → +7 mg/dL glucose
   ```

2. **Insulin Timing & Meal Sync**
   ```
   Bolus insulin 15-30 min before meal → Better glucose control
   Late insulin (>30 min after meal) → Glucose spike +30 mg/dL
   ```

3. **Weight Loss → HbA1c Improvement**
   ```
   Weight loss >3 kg → -0.5% HbA1c improvement
   Visible after 60-90 days
   ```

4. **Medication Adherence Impact**
   ```
   Random "missed dose" days (10% of days)
   Missed basal insulin → +15 mg/dL avg glucose next day
   Missed BP med → +8 mmHg systolic
   ```

5. **Exercise Type Effects**
   ```
   Aerobic (running, cycling) → -12 mg/dL (immediate)
   Strength training → -5 mg/dL (delayed, next 24h)
   Yoga/walking → -4 mg/dL
   ```

---

## 🧠 Expected ML Discovery Results

### PCMCI Causal Graph (Time-Lagged Relationships)

**Expected Discoveries:**
```
1. insulin_bolus(t-1h) → glucose_level(t)     [strength: -0.65, p<0.001]
2. meal_carbs(t-2h) → glucose_level(t)        [strength: +0.58, p<0.001]
3. sleep_quality(t-1d) → glucose_avg(t)       [strength: -0.42, p<0.01]
4. exercise_minutes(t-3h) → glucose_level(t)  [strength: -0.38, p<0.01]
5. weight_kg(t-14d) → glucose_avg(t)          [strength: +0.35, p<0.05]
6. bp_systolic(t) → glucose_variability(t)    [strength: +0.28, p<0.05]
```

**Key Insight:** Multi-lag analysis showing:
- Immediate effects: Insulin (1h), Meals (2h)
- Same-day effects: Exercise (3h), Sleep (previous night)
- Long-term effects: Weight (2 weeks)

---

### STUMPY Pattern Detection (Recurring Motifs)

**Expected Patterns:**

1. **Weekday Morning Pattern** (Mon-Fri, 7-9 AM)
   - Motif: Consistent breakfast routine → predictable glucose curve
   - Occurrences: ~60 times over 90 days
   - Description: "Wake → breakfast → glucose spike → insulin → return to baseline"

2. **Weekend Brunch Pattern** (Sat-Sun, 10 AM-12 PM)
   - Motif: Later, higher-carb meals → larger glucose excursion
   - Occurrences: ~26 times over 90 days
   - Description: "Delayed eating → higher spike → slower return"

3. **Evening Exercise Pattern** (Mon/Wed/Fri, 6-8 PM)
   - Motif: Post-work exercise → sustained lower glucose overnight
   - Occurrences: ~40 times over 90 days
   - Description: "Exercise → gradual glucose decline → stable overnight"

4. **Meal-Insulin Coordination Pattern**
   - Motif: Well-timed bolus → minimal spike → quick return
   - Occurrences: ~180 times (2x daily on good days)
   - Description: "Pre-bolus 15min → meal → controlled rise → smooth descent"

**Anomalies (Discords):**
- Missed insulin dose days → unusual glucose spike pattern
- Illness/stress days → elevated baseline with more variability
- High-carb "cheat meals" → prolonged elevation pattern

---

## 🛠️ Implementation Plan

### Phase 1: Extend Sample Data Generator
**File:** `backend/scripts/generate_sample_data_v2.py`

**Tasks:**
1. ✅ Import new models (HbA1c, Medication, InsulinDose, BloodPressure, BodyMetrics)
2. ⬜ Create `generate_hba1c_readings()` function
3. ⬜ Create `generate_medications()` function
4. ⬜ Create `generate_insulin_doses()` function (sync with meals)
5. ⬜ Create `generate_blood_pressure()` function
6. ⬜ Create `generate_body_metrics()` function
7. ⬜ Update `generate_data_for_user()` to orchestrate all generators
8. ⬜ Add correlation logic for complex multi-variable relationships

**Key Functions:**
```python
def generate_insulin_doses(user_id, date, meals, glucose_readings):
    """Generate insulin doses synchronized with meals and glucose levels."""

def calculate_hba1c_from_glucose(glucose_readings, period_days=90):
    """Calculate HbA1c using ADAG formula from glucose average."""

def apply_weight_loss_effect(current_weight, weeks_elapsed):
    """Apply gradual weight loss trend with exercise/diet influence."""
```

---

### Phase 2: Database Seeding
**File:** `backend/scripts/seed_database.py`

**Tasks:**
1. ⬜ Create test user with realistic profile
2. ⬜ Run sample data generator v2
3. ⬜ Verify data integrity (foreign keys, timestamps)
4. ⬜ Create data validation checks

**User Profile:**
```python
test_user = {
    "email": "demo@glucolens.io",
    "full_name": "John Doe",
    "date_of_birth": "1985-06-15",
    "height_cm": 175.0,
    "weight_kg": 85.0,  # Will decrease over time
    "gender": "male",
    "diabetes_type": "type1",
    "diagnosis_date": "2020-03-01",
    "insulin_dependent": True,
    "target_glucose_min": 70.0,
    "target_glucose_max": 180.0,
}
```

---

### Phase 3: ML Pipeline Trigger
**File:** `backend/scripts/run_ml_pipeline.py`

**Tasks:**
1. ⬜ Trigger PCMCI causal discovery
2. ⬜ Trigger STUMPY pattern detection
3. ⬜ Trigger STUMPY anomaly detection
4. ⬜ Wait for Celery task completion
5. ⬜ Query and display results

**Execution:**
```bash
# Option 1: Via Celery tasks
python scripts/run_ml_pipeline.py --user-id <uuid>

# Option 2: Via API endpoint
curl -X POST http://localhost:8000/api/v1/insights/advanced/trigger \
  -H "Authorization: Bearer <token>"
```

---

### Phase 4: Inference Validation
**File:** `backend/scripts/validate_inference.py`

**Tasks:**
1. ⬜ Query PCMCI causal links from database
2. ⬜ Verify expected relationships are discovered
3. ⬜ Check p-values and correlation strengths
4. ⬜ Query STUMPY patterns
5. ⬜ Verify recurring motifs found
6. ⬜ Generate validation report

**Expected Output:**
```
✅ PCMCI Causal Discovery Results:
  ✓ Found insulin → glucose relationship (strength: -0.67, p<0.001)
  ✓ Found meal → glucose relationship (strength: +0.61, p<0.001)
  ✓ Found sleep → glucose relationship (strength: -0.44, p<0.01)
  ✓ Found exercise → glucose relationship (strength: -0.39, p<0.01)
  ✓ Found weight → glucose relationship (strength: +0.33, p<0.05)

✅ STUMPY Pattern Detection Results:
  ✓ Found 4 recurring motifs
  ✓ Morning routine pattern: 58 occurrences
  ✓ Weekend brunch pattern: 24 occurrences
  ✓ Evening exercise pattern: 38 occurrences
  ✓ Meal-insulin pattern: 174 occurrences

✅ Anomaly Detection Results:
  ✓ Found 12 anomalous patterns
  ✓ High glucose events: 5
  ✓ Missed insulin events: 4
  ✓ Unusual variability: 3
```

---

## 📈 Data Volume Summary

### 90 Days of Comprehensive Data:

| Data Type | Frequency | Total Records |
|-----------|-----------|---------------|
| Glucose readings | Every 5 min | 25,920 |
| Sleep sessions | Daily | 90 |
| Activities | 70% of days | ~63 |
| Meals | 3-4 per day | ~315 |
| **HbA1c tests** | Quarterly | **3-4** |
| **Medications** | Active list | **3-5** |
| **Insulin doses** | 4-6 per day | **~450** |
| **Blood pressure** | Daily | **90** |
| **Body metrics** | Weekly | **13** |

**Total:** ~27,000 time-series data points

---

## 🎬 Execution Timeline

### Sprint 1: Sample Data Generation (2-3 hours)
- [x] Analyze existing generator
- [ ] Design correlations
- [ ] Extend generator for new health types
- [ ] Test data generation locally

### Sprint 2: Database Seeding (1 hour)
- [ ] Create seed script
- [ ] Seed test database
- [ ] Verify data integrity

### Sprint 3: ML Pipeline Integration (1-2 hours)
- [ ] Trigger PCMCI analysis
- [ ] Trigger STUMPY detection
- [ ] Monitor Celery tasks

### Sprint 4: Validation & Documentation (1 hour)
- [ ] Create validation script
- [ ] Generate inference report
- [ ] Document findings

**Total Estimated Time:** 5-7 hours

---

## 🚀 Success Criteria

### ✅ Pipeline Validated When:

1. **Data Generation:**
   - All 5 new health data types generated successfully
   - Realistic correlations present in raw data
   - No data integrity errors

2. **ML Discovery:**
   - PCMCI finds ≥5 significant causal relationships (p<0.05)
   - STUMPY finds ≥3 recurring patterns
   - STUMPY finds ≥5 anomalies

3. **Inference Quality:**
   - Discovered relationships match expected correlations
   - Causal strengths are reasonable (-0.2 to -0.7 for negative, +0.2 to +0.7 for positive)
   - Patterns make clinical sense (morning routines, meal patterns, etc.)

4. **API Integration:**
   - All advanced insights endpoints return valid data
   - Frontend can visualize causal graphs
   - Pattern descriptions are human-readable

---

## 📝 Next Steps

1. **Review & Approve Plan** ✋ (User confirmation needed)
2. Implement extended sample data generator
3. Run end-to-end pipeline test
4. Iterate based on results
5. Document best practices for production data collection

---

## 🔬 Research Value

This synthetic data pipeline validates:
- **Algorithm Correctness:** PCMCI and STUMPY work on realistic health data
- **Correlation Detection:** Expected relationships are discovered automatically
- **Clinical Relevance:** Insights match known diabetes management principles
- **System Integration:** Full stack from data → ML → API → frontend works

**Future Use:** Template for onboarding real users with initial ML insights.

---

**Questions for Discussion:**
1. Should we generate multiple user profiles (good control vs. poor control)?
2. Do we want to simulate medication changes mid-period?
3. Should we add missing data days to test robustness?
4. What's the priority: PCMCI validation or STUMPY pattern discovery?
