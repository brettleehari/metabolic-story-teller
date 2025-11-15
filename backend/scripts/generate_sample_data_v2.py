"""
Generate comprehensive synthetic health data for GlucoLens ML pipeline validation.

This script creates realistic glucose, sleep, activity, meal, medication, insulin,
blood pressure, body metrics, and HbA1c data with built-in correlations for
PCMCI causal discovery and STUMPY pattern detection.

Usage:
    python scripts/generate_sample_data_v2.py --days 90 --user-id <uuid>
"""
import asyncio
import argparse
from datetime import datetime, timedelta, date, time
import random
import numpy as np
from uuid import UUID
from typing import List, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.glucose import GlucoseReading
from app.models.sleep import SleepData
from app.models.activity import Activity
from app.models.meal import Meal
from app.models.hba1c import HbA1c
from app.models.medication import Medication
from app.models.insulin import InsulinDose
from app.models.blood_pressure import BloodPressure
from app.models.body_metrics import BodyMetrics


# =====================================================
# Configuration & Constants
# =====================================================

INSULIN_TO_CARB_RATIO = 10  # 1 unit per 10g carbs
CORRECTION_FACTOR = 50  # 1 unit drops glucose 50 mg/dL
TARGET_GLUCOSE = 120  # Target for corrections
INSULIN_PEAK_HOURS = 2  # Insulin peaks at 2 hours
INSULIN_DURATION_HOURS = 4  # Insulin active for 4 hours

# User profile characteristics
USER_STARTING_WEIGHT = 85.0  # kg
WEEKLY_WEIGHT_LOSS = -0.3  # kg/week (healthy rate)
STARTING_BODY_FAT = 28.0  # percent

# Medication adherence
MEDICATION_ADHERENCE_RATE = 0.90  # 90% adherence (10% missed doses)


# =====================================================
# Helper Functions
# =====================================================

def calculate_hba1c_from_glucose(avg_glucose_mgdl: float) -> Tuple[float, int]:
    """
    Calculate HbA1c from average glucose using ADAG formula.

    ADAG Formula: eAG (mg/dL) = 28.7 × A1C − 46.7
    Reversed: A1C = (eAG + 46.7) / 28.7

    Returns:
        (hba1c_percent, hba1c_mmol_mol)
    """
    hba1c_percent = (avg_glucose_mgdl + 46.7) / 28.7
    # Add realistic noise: ±0.2%
    hba1c_percent += random.uniform(-0.2, 0.2)
    hba1c_percent = max(4.0, min(15.0, hba1c_percent))

    # Convert to mmol/mol: (DCCT% - 2.15) × 10.929
    hba1c_mmol_mol = int((hba1c_percent - 2.15) * 10.929)

    return round(hba1c_percent, 1), hba1c_mmol_mol


def is_medication_taken(adherence_rate: float = MEDICATION_ADHERENCE_RATE) -> bool:
    """Simulate medication adherence (90% take meds, 10% forget)."""
    return random.random() < adherence_rate


# =====================================================
# Glucose Generation
# =====================================================

def generate_glucose_readings(
    user_id: UUID,
    date: datetime,
    base_level: float,
    variability: float,
    insulin_doses: List[InsulinDose] = None
) -> List[GlucoseReading]:
    """
    Generate CGM readings for a day (every 5 minutes = 288 readings/day).

    Includes insulin effects on glucose levels.
    """
    readings = []
    start_time = datetime.combine(date, datetime.min.time())
    insulin_doses = insulin_doses or []

    for minute in range(0, 1440, 5):  # Every 5 minutes
        timestamp = start_time + timedelta(minutes=minute)
        hour = timestamp.hour

        # Circadian rhythm (lower at night, higher after meals)
        if 0 <= hour < 6:  # Night - lower and stable
            circadian_factor = 0.85
        elif 7 <= hour < 9:  # Breakfast spike
            circadian_factor = 1.2
        elif 12 <= hour < 14:  # Lunch spike
            circadian_factor = 1.15
        elif 18 <= hour < 20:  # Dinner spike
            circadian_factor = 1.1
        else:
            circadian_factor = 1.0

        # Calculate insulin effect
        insulin_effect = 0.0
        for dose in insulin_doses:
            hours_since_dose = (timestamp - dose.timestamp).total_seconds() / 3600
            if 0 <= hours_since_dose <= INSULIN_DURATION_HOURS:
                # Insulin effect curve: peaks at 2 hours, then tapers off
                if hours_since_dose <= INSULIN_PEAK_HOURS:
                    effect_multiplier = hours_since_dose / INSULIN_PEAK_HOURS
                else:
                    effect_multiplier = 1.0 - ((hours_since_dose - INSULIN_PEAK_HOURS) /
                                               (INSULIN_DURATION_HOURS - INSULIN_PEAK_HOURS))

                # Each unit drops glucose by CORRECTION_FACTOR at peak
                insulin_effect += float(dose.dose_units) * CORRECTION_FACTOR * effect_multiplier

        # Generate value with all factors
        value = (base_level * circadian_factor) - insulin_effect + random.gauss(0, variability)
        value = max(70.0, min(250.0, value))  # Clamp to realistic range

        readings.append(GlucoseReading(
            user_id=user_id,
            timestamp=timestamp,
            value=round(value, 1),
            source="synthetic_cgm"
        ))

    return readings


# =====================================================
# Sleep Generation
# =====================================================

def generate_sleep_data(user_id: UUID, date: date) -> Tuple[SleepData, float]:
    """Generate sleep session for a night."""
    # Random sleep duration (5-9 hours)
    duration_minutes = random.randint(300, 540)

    # Sleep quality (0-10)
    quality_score = random.uniform(5.0, 10.0)

    # Sleep stages
    deep_sleep = int(duration_minutes * random.uniform(0.15, 0.25))
    rem_sleep = int(duration_minutes * random.uniform(0.20, 0.25))
    light_sleep = int(duration_minutes * random.uniform(0.40, 0.50))
    awake = duration_minutes - (deep_sleep + rem_sleep + light_sleep)

    # Sleep time (typically 10 PM - 7 AM)
    sleep_start = datetime.combine(date, time(22, 0)) + timedelta(minutes=random.randint(-30, 30))
    sleep_end = sleep_start + timedelta(minutes=duration_minutes)

    return SleepData(
        user_id=user_id,
        date=date,
        sleep_start=sleep_start,
        sleep_end=sleep_end,
        duration_minutes=duration_minutes,
        deep_sleep_minutes=deep_sleep,
        rem_sleep_minutes=rem_sleep,
        light_sleep_minutes=light_sleep,
        awake_minutes=awake,
        quality_score=round(quality_score, 1),
        source="synthetic"
    ), quality_score


# =====================================================
# Activity Generation
# =====================================================

def generate_activities(user_id: UUID, date: date, sleep_quality: float) -> Tuple[List[Activity], int]:
    """
    Generate exercise activities for a day.

    Correlation: Poor sleep (quality < 6) → 50% chance of skipping exercise
    """
    activities = []

    # Sleep affects exercise motivation
    if sleep_quality < 6.0 and random.random() < 0.5:
        return activities, 0  # Skip exercise due to poor sleep

    # 70% chance of exercise on any given day
    if random.random() < 0.7:
        activity_types = ["walking", "running", "cycling", "strength", "yoga"]
        activity_type = random.choice(activity_types)

        duration = random.randint(20, 90)
        timestamp = datetime.combine(date, time(0, 0)) + timedelta(
            hours=random.choice([7, 12, 18])  # Morning, lunch, or evening
        )

        intensities = ["light", "moderate", "vigorous"]
        weights = [0.3, 0.5, 0.2]
        intensity = random.choices(intensities, weights=weights)[0]

        # Calories based on intensity
        cal_per_min = {"light": 3, "moderate": 6, "vigorous": 10}
        calories = duration * cal_per_min[intensity]

        activities.append(Activity(
            user_id=user_id,
            timestamp=timestamp,
            activity_type=activity_type,
            duration_minutes=duration,
            intensity=intensity,
            calories_burned=calories,
            heart_rate_avg=random.randint(90, 170),
            source="synthetic"
        ))

        return activities, duration
    else:
        return activities, 0


# =====================================================
# Meal Generation
# =====================================================

def generate_meals(user_id: UUID, date: date) -> Tuple[List[Meal], float]:
    """Generate meals for a day."""
    meals = []
    total_carbs = 0

    meal_templates = [
        {"type": "breakfast", "hour": 8, "carbs": (30, 60), "protein": (10, 25), "fat": (5, 20)},
        {"type": "lunch", "hour": 13, "carbs": (40, 80), "protein": (20, 40), "fat": (10, 30)},
        {"type": "dinner", "hour": 19, "carbs": (40, 80), "protein": (25, 50), "fat": (15, 35)},
    ]

    for template in meal_templates:
        carbs = random.uniform(*template["carbs"])
        protein = random.uniform(*template["protein"])
        fat = random.uniform(*template["fat"])

        calories = int(carbs * 4 + protein * 4 + fat * 9)

        timestamp = datetime.combine(date, time(0, 0)) + timedelta(
            hours=template["hour"], minutes=random.randint(-30, 30)
        )

        meals.append(Meal(
            user_id=user_id,
            timestamp=timestamp,
            meal_type=template["type"],
            carbs_grams=round(carbs, 1),
            protein_grams=round(protein, 1),
            fat_grams=round(fat, 1),
            calories=calories,
            glycemic_load=round(carbs * random.uniform(0.5, 0.8), 1),
            source="synthetic"
        ))

        total_carbs += carbs

    # 50% chance of snack
    if random.random() < 0.5:
        carbs = random.uniform(15, 30)
        total_carbs += carbs

        meals.append(Meal(
            user_id=user_id,
            timestamp=datetime.combine(date, time(0, 0)) + timedelta(
                hours=random.randint(10, 16)
            ),
            meal_type="snack",
            carbs_grams=round(carbs, 1),
            protein_grams=round(random.uniform(2, 10), 1),
            fat_grams=round(random.uniform(3, 15), 1),
            calories=int(carbs * 4 + random.uniform(20, 60)),
            source="synthetic"
        ))

    return meals, total_carbs


# =====================================================
# Insulin Dose Generation
# =====================================================

def generate_insulin_doses(
    user_id: UUID,
    date: date,
    meals: List[Meal],
    medication_taken: bool
) -> List[InsulinDose]:
    """
    Generate insulin doses synchronized with meals.

    Types:
    - Basal: 1x daily (evening)
    - Bolus: With each meal (proportional to carbs)
    - Correction: When needed for high glucose
    """
    doses = []

    # Basal insulin (evening, once daily)
    if medication_taken:
        basal_time = datetime.combine(date, time(20, 0)) + timedelta(minutes=random.randint(-30, 30))
        basal_dose = random.uniform(18, 22)  # 18-22 units

        doses.append(InsulinDose(
            user_id=user_id,
            timestamp=basal_time,
            insulin_type="basal",
            medication_name="Lantus",
            dose_units=round(basal_dose, 1),
            source="synthetic"
        ))

    # Bolus insulin (with meals)
    for meal in meals:
        if meal.meal_type == "snack":
            continue  # Usually don't bolus for small snacks

        if medication_taken or random.random() < 0.95:  # 95% adherence for bolus
            # Calculate bolus dose based on carbs
            bolus_dose = meal.carbs_grams / INSULIN_TO_CARB_RATIO

            # Pre-bolus 15-30 minutes before meal (good practice)
            bolus_timing = random.choice([-25, -20, -15, 0, 5])  # Minutes relative to meal
            bolus_time = meal.timestamp + timedelta(minutes=bolus_timing)

            doses.append(InsulinDose(
                user_id=user_id,
                timestamp=bolus_time,
                insulin_type="bolus",
                medication_name="Humalog",
                dose_units=round(bolus_dose, 1),
                carbs_grams=meal.carbs_grams,
                source="synthetic"
            ))

    # Occasional correction doses (20% of days)
    if random.random() < 0.2:
        correction_time = datetime.combine(date, time(0, 0)) + timedelta(
            hours=random.randint(10, 22)
        )
        # Simulated high glucose: 180-220 mg/dL
        simulated_glucose = random.uniform(180, 220)
        correction_dose = (simulated_glucose - TARGET_GLUCOSE) / CORRECTION_FACTOR

        doses.append(InsulinDose(
            user_id=user_id,
            timestamp=correction_time,
            insulin_type="correction",
            medication_name="Humalog",
            dose_units=round(correction_dose, 1),
            correction_target=TARGET_GLUCOSE,
            source="synthetic"
        ))

    return sorted(doses, key=lambda d: d.timestamp)


# =====================================================
# Blood Pressure Generation
# =====================================================

def generate_blood_pressure(
    user_id: UUID,
    date: date,
    exercise_yesterday: bool,
    high_sodium_meal: bool,
    on_bp_medication: bool,
    stress_day: bool
) -> BloodPressure:
    """
    Generate blood pressure reading (daily morning reading).

    Correlations:
    - Exercise yesterday → -5/-3
    - High sodium → +8/+4
    - BP medication → -10/-6
    - Stress → +10/+5
    """
    base_systolic = 128  # Slightly elevated
    base_diastolic = 84

    # Apply correlations
    if exercise_yesterday:
        base_systolic -= 5
        base_diastolic -= 3

    if high_sodium_meal:
        base_systolic += 8
        base_diastolic += 4

    if on_bp_medication:
        base_systolic -= 10
        base_diastolic -= 6

    if stress_day:
        base_systolic += 10
        base_diastolic += 5

    # Add random variation
    systolic = int(base_systolic + random.gauss(0, 5))
    diastolic = int(base_diastolic + random.gauss(0, 3))

    # Clamp to realistic ranges
    systolic = max(90, min(160, systolic))
    diastolic = max(60, min(100, diastolic))

    # Morning reading (7-8 AM)
    timestamp = datetime.combine(date, time(7, 30)) + timedelta(minutes=random.randint(-20, 20))

    heart_rate = random.randint(60, 85)

    return BloodPressure(
        user_id=user_id,
        timestamp=timestamp,
        systolic=systolic,
        diastolic=diastolic,
        heart_rate=heart_rate,
        source="synthetic"
    )


# =====================================================
# Body Metrics Generation
# =====================================================

def generate_body_metrics(
    user_id: UUID,
    date: date,
    weeks_elapsed: int,
    avg_exercise_minutes: float,
    height_cm: float
) -> BodyMetrics:
    """
    Generate body metrics (weekly weigh-in).

    Correlation: Gradual weight loss -0.3 kg/week
    """
    # Calculate current weight with gradual loss
    current_weight = USER_STARTING_WEIGHT + (WEEKLY_WEIGHT_LOSS * weeks_elapsed)

    # Extra weight loss for active weeks (avg > 200 min/week exercise)
    if avg_exercise_minutes > 200 / 7:  # Average per day
        current_weight -= 0.2

    # Add realistic daily variation
    current_weight += random.uniform(-0.3, 0.3)
    current_weight = max(60.0, current_weight)

    # Body composition changes with weight loss
    body_fat_percent = STARTING_BODY_FAT - (weeks_elapsed * 0.2)
    body_fat_percent = max(15.0, body_fat_percent)

    # Calculate muscle mass (total weight - fat weight)
    fat_kg = current_weight * (body_fat_percent / 100)
    muscle_mass_kg = current_weight - fat_kg

    # Calculate BMI
    height_m = height_cm / 100
    bmi = current_weight / (height_m ** 2)

    # Morning weigh-in (same day each week for pattern)
    timestamp = datetime.combine(date, time(7, 0))

    return BodyMetrics(
        user_id=user_id,
        timestamp=timestamp,
        weight_kg=round(current_weight, 1),
        body_fat_percent=round(body_fat_percent, 1),
        muscle_mass_kg=round(muscle_mass_kg, 1),
        bmi=round(bmi, 1),
        source="synthetic"
    )


# =====================================================
# Medication Generation
# =====================================================

def generate_medications(user_id: UUID, start_date: date, on_bp_medication: bool) -> List[Medication]:
    """Generate user's medication list (stays constant for 90 days)."""
    medications = []

    # Insulin medications (always for Type 1)
    medications.extend([
        Medication(
            user_id=user_id,
            medication_name="Lantus",
            medication_type="insulin_basal",
            dosage="20 units",
            frequency="once_daily_evening",
            start_date=start_date - timedelta(days=365),
            is_active=True,
            notes="Long-acting basal insulin"
        ),
        Medication(
            user_id=user_id,
            medication_name="Humalog",
            medication_type="insulin_bolus",
            dosage="Variable with meals",
            frequency="with_meals",
            start_date=start_date - timedelta(days=365),
            is_active=True,
            notes="Rapid-acting mealtime insulin"
        )
    ])

    # Optional: Metformin (for insulin resistance)
    if random.random() < 0.3:
        medications.append(Medication(
            user_id=user_id,
            medication_name="Metformin",
            medication_type="oral",
            dosage="1000mg",
            frequency="twice_daily",
            start_date=start_date - timedelta(days=180),
            is_active=True,
            notes="Helps with insulin sensitivity"
        ))

    # Blood pressure medication (if indicated)
    if on_bp_medication:
        medications.append(Medication(
            user_id=user_id,
            medication_name="Lisinopril",
            medication_type="other",
            dosage="10mg",
            frequency="once_daily",
            start_date=start_date - timedelta(days=90),
            is_active=True,
            notes="ACE inhibitor for blood pressure control"
        ))

    return medications


# =====================================================
# HbA1c Generation
# =====================================================

def generate_hba1c_readings(
    user_id: UUID,
    glucose_readings: List[GlucoseReading],
    test_dates: List[date]
) -> List[HbA1c]:
    """
    Generate HbA1c readings calculated from glucose averages.

    Uses ADAG formula: HbA1c% = (avg_glucose + 46.7) / 28.7
    """
    hba1c_readings = []

    for test_date in test_dates:
        # Calculate average glucose for 90 days before test
        test_end = datetime.combine(test_date, time(23, 59))
        test_start = test_end - timedelta(days=90)

        period_readings = [
            r for r in glucose_readings
            if test_start <= r.timestamp <= test_end
        ]

        if not period_readings:
            continue

        avg_glucose = sum(float(r.value) for r in period_readings) / len(period_readings)
        hba1c_percent, hba1c_mmol_mol = calculate_hba1c_from_glucose(avg_glucose)

        hba1c_readings.append(HbA1c(
            user_id=user_id,
            test_date=test_date,
            hba1c_percent=hba1c_percent,
            hba1c_mmol_mol=hba1c_mmol_mol,
            lab_name="Quest Diagnostics",
            notes=f"Calculated from {len(period_readings)} CGM readings over 90 days"
        ))

    return hba1c_readings


# =====================================================
# Main Data Generation
# =====================================================

def generate_comprehensive_data(user_id: UUID, days: int = 90, height_cm: float = 175.0):
    """
    Generate comprehensive health data with realistic correlations.

    Correlations:
    1. Good sleep → More exercise → Lower glucose
    2. Insulin timing & meals → Glucose control
    3. Weight loss → HbA1c improvement
    4. Exercise → Lower blood pressure
    5. Medication adherence → Glucose stability
    """
    print(f"🎲 Generating {days} days of comprehensive health data...")
    print(f"   User: {user_id}")
    print(f"   Height: {height_cm} cm")
    print(f"   Starting weight: {USER_STARTING_WEIGHT} kg")

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Determine if user is on BP medication (30% chance)
        on_bp_medication = random.random() < 0.3

        # Generate medications (stays constant)
        medications = generate_medications(user_id, start_date, on_bp_medication)
        session.add_all(medications)
        print(f"  ✓ Generated {len(medications)} medications")

        # Track data for HbA1c calculation
        all_glucose_readings = []

        # Track exercise for body metrics
        recent_exercise_minutes = []

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            weeks_elapsed = day_offset / 7

            # Generate sleep data
            sleep, sleep_quality = generate_sleep_data(user_id, current_date)
            session.add(sleep)

            # Generate activities (affected by sleep)
            activities, exercise_minutes = generate_activities(user_id, current_date, sleep_quality)
            session.add_all(activities)
            recent_exercise_minutes.append(exercise_minutes)
            if len(recent_exercise_minutes) > 7:
                recent_exercise_minutes.pop(0)

            # Generate meals
            meals, total_carbs = generate_meals(user_id, current_date)
            session.add_all(meals)

            # Check if medications taken today (90% adherence)
            medication_taken = is_medication_taken()

            # Generate insulin doses (synchronized with meals)
            insulin_doses = generate_insulin_doses(user_id, current_date, meals, medication_taken)
            session.add_all(insulin_doses)

            # Calculate base glucose level with correlations
            base_glucose = 100

            # Sleep correlation
            if sleep.duration_minutes > 420 and sleep_quality > 8:
                base_glucose -= 10

            # Exercise correlation
            if exercise_minutes > 30:
                base_glucose -= 8

            # Carbs correlation
            if total_carbs > 200:
                base_glucose += 15

            # Medication adherence (missed doses → higher glucose)
            if not medication_taken:
                base_glucose += 15

            # Weight loss effect (gradual improvement)
            weight_loss_kg = abs(WEEKLY_WEIGHT_LOSS * weeks_elapsed)
            if weight_loss_kg > 2.0:
                base_glucose -= 5

            # Add random variation
            base_glucose += random.gauss(0, 5)

            # Variability (lower with good control)
            variability = 15 if base_glucose < 110 else 20

            # Generate CGM readings (with insulin effects)
            glucose_readings = generate_glucose_readings(
                user_id, current_date, base_glucose, variability, insulin_doses
            )
            session.add_all(glucose_readings)
            all_glucose_readings.extend(glucose_readings)

            # Generate blood pressure (daily)
            exercise_yesterday = day_offset > 0 and recent_exercise_minutes[-2] > 30 if len(recent_exercise_minutes) > 1 else False
            high_sodium_meal = total_carbs > 200  # Proxy for high sodium
            stress_day = sleep_quality < 6.0  # Poor sleep = stress

            bp_reading = generate_blood_pressure(
                user_id, current_date, exercise_yesterday, high_sodium_meal,
                on_bp_medication, stress_day
            )
            session.add(bp_reading)

            # Generate body metrics (weekly, on Sundays)
            if current_date.weekday() == 6:  # Sunday
                avg_exercise = sum(recent_exercise_minutes) / len(recent_exercise_minutes)
                body_metrics = generate_body_metrics(
                    user_id, current_date, int(weeks_elapsed), avg_exercise, height_cm
                )
                session.add(body_metrics)

            # Commit every 10 days
            if (day_offset + 1) % 10 == 0:
                session.commit()
                print(f"  ✓ Generated {day_offset + 1}/{days} days")

        # Generate HbA1c readings (quarterly: day 30, 60, 90)
        hba1c_test_dates = [
            start_date + timedelta(days=30),
            start_date + timedelta(days=60),
            start_date + timedelta(days=90) if days >= 90 else None
        ]
        hba1c_test_dates = [d for d in hba1c_test_dates if d]

        hba1c_readings = generate_hba1c_readings(user_id, all_glucose_readings, hba1c_test_dates)
        session.add_all(hba1c_readings)
        print(f"  ✓ Generated {len(hba1c_readings)} HbA1c readings")

        # Final commit
        session.commit()

        # Summary
        body_metrics_count = days // 7
        print(f"\n✅ Successfully generated comprehensive health data!")
        print(f"   📊 Glucose readings: {len(all_glucose_readings)}")
        print(f"   😴 Sleep sessions: {days}")
        print(f"   🏃 Activities: {len([a for a in activities])}")
        print(f"   🍽️  Meals: {len(meals) * days // 10}")
        print(f"   💉 Insulin doses: {len(insulin_doses) * days // 10}")
        print(f"   ❤️  Blood pressure: {days}")
        print(f"   ⚖️  Body metrics: {body_metrics_count}")
        print(f"   🩸 HbA1c readings: {len(hba1c_readings)}")
        print(f"   💊 Medications: {len(medications)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate comprehensive sample data for GlucoLens ML pipeline"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days to generate (default: 90)"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="00000000-0000-0000-0000-000000000001",
        help="User UUID (default: test user)"
    )
    parser.add_argument(
        "--height",
        type=float,
        default=175.0,
        help="User height in cm (default: 175.0)"
    )

    args = parser.parse_args()

    user_uuid = UUID(args.user_id)
    generate_comprehensive_data(user_uuid, args.days, args.height)
