"""
Generate synthetic data for GlucoLens MVP testing.

This script creates realistic glucose, sleep, activity, and meal data
with built-in correlations for pattern discovery.

Usage:
    python scripts/generate_sample_data.py --days 90 --user-id <uuid>
"""
import asyncio
import argparse
from datetime import datetime, timedelta
import random
import numpy as np
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.glucose import GlucoseReading
from app.models.sleep import SleepData
from app.models.activity import Activity
from app.models.meal import Meal


def generate_glucose_readings(user_id: UUID, date: datetime, base_level: float, variability: float):
    """
    Generate CGM readings for a day (every 5 minutes = 288 readings/day).

    Args:
        user_id: User UUID
        date: Date to generate data for
        base_level: Base glucose level (influenced by sleep, exercise, meals)
        variability: Standard deviation
    """
    readings = []
    start_time = datetime.combine(date, datetime.min.time())

    for minute in range(0, 1440, 5):  # Every 5 minutes
        timestamp = start_time + timedelta(minutes=minute)

        # Add circadian rhythm (lower at night, higher after meals)
        hour = timestamp.hour
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

        # Generate value
        value = base_level * circadian_factor + random.gauss(0, variability)
        value = max(70.0, min(200.0, value))  # Clamp to realistic range

        readings.append(GlucoseReading(
            user_id=user_id,
            timestamp=timestamp,
            value=round(value, 1),
            source="synthetic_cgm"
        ))

    return readings


def generate_sleep_data(user_id: UUID, date: datetime):
    """
    Generate sleep session for a night.

    Returns:
        SleepData object and quality score
    """
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
    sleep_start = datetime.combine(date, datetime.min.time()) + timedelta(hours=22)
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


def generate_activities(user_id: UUID, date: datetime):
    """
    Generate exercise activities for a day.

    Returns:
        List of Activity objects and total minutes
    """
    activities = []

    # 70% chance of exercise on any given day
    if random.random() < 0.7:
        activity_types = ["walking", "running", "cycling", "strength", "yoga"]
        activity_type = random.choice(activity_types)

        duration = random.randint(20, 90)
        timestamp = datetime.combine(date, datetime.min.time()) + timedelta(
            hours=random.randint(6, 20)
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


def generate_meals(user_id: UUID, date: datetime):
    """
    Generate meals for a day.

    Returns:
        List of Meal objects and total carbs
    """
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

        timestamp = datetime.combine(date, datetime.min.time()) + timedelta(
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
            timestamp=datetime.combine(date, datetime.min.time()) + timedelta(
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


def generate_data_for_user(user_id: UUID, days: int = 90):
    """
    Generate comprehensive data for a user with realistic correlations.

    Correlations built-in:
    - Good sleep (>7hrs, quality>8) -> Lower avg glucose
    - Exercise (>30min) -> Lower glucose next day
    - High carbs (>200g) -> Higher glucose
    """
    print(f"🎲 Generating {days} days of data for user {user_id}...")

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)

            # Generate sleep data
            sleep, sleep_quality = generate_sleep_data(user_id, current_date)
            session.add(sleep)

            # Generate activities
            activities, exercise_minutes = generate_activities(user_id, current_date)
            session.add_all(activities)

            # Generate meals
            meals, total_carbs = generate_meals(user_id, current_date)
            session.add_all(meals)

            # Generate glucose with correlations
            # Base glucose level influenced by lifestyle factors
            base_glucose = 100  # Start at 100 mg/dL

            # Sleep correlation: good sleep -> -10 mg/dL
            if sleep.duration_minutes > 420 and sleep_quality > 8:
                base_glucose -= 10

            # Exercise correlation: exercised -> -8 mg/dL
            if exercise_minutes > 30:
                base_glucose -= 8

            # Carbs correlation: high carbs -> +15 mg/dL
            if total_carbs > 200:
                base_glucose += 15

            # Add random variation
            base_glucose += random.gauss(0, 5)

            # Variability (lower with good control)
            variability = 15 if base_glucose < 110 else 20

            # Generate CGM readings
            glucose_readings = generate_glucose_readings(
                user_id, current_date, base_glucose, variability
            )
            session.add_all(glucose_readings)

            # Commit every 10 days to avoid memory issues
            if (day_offset + 1) % 10 == 0:
                session.commit()
                print(f"  ✓ Generated {day_offset + 1}/{days} days")

        # Final commit
        session.commit()
        print(f"✅ Successfully generated {days} days of data!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sample data for GlucoLens")
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

    args = parser.parse_args()

    user_uuid = UUID(args.user_id)
    generate_data_for_user(user_uuid, args.days)
