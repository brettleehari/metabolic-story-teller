"""
Generate 3 demo user profiles with realistic data for read-only demo.

This script creates:
1. Alice Thompson - Well-controlled glucose with consistent sleep
2. Bob Martinez - Variable glucose with stress patterns
3. Carol Chen - Active lifestyle with clear exercise impact

Each user gets 90 days of:
- Glucose readings (every 5 minutes)
- Sleep data (daily)
- Meals (3-4 per day)
- Activities (2-5 per week)

Plus pre-computed ML insights (correlations, patterns, PCMCI, STUMPY).
"""

import asyncio
import sys
from datetime import datetime, timedelta, time
from uuid import UUID
from pathlib import Path
import random
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import async_session_maker
from app.models.user import User
from app.models.glucose import GlucoseReading
from app.models.sleep import SleepData
from app.models.meal import Meal
from app.models.activity import Activity
from app.utils.auth import get_password_hash


# Demo user profiles
DEMO_USERS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "alice@demo.glucolens.com",
        "full_name": "Alice Thompson",
        "age": 34,
        "gender": "female",
        "diabetes_type": "type_1",
        "profile": "well_controlled",  # Stable glucose, good sleep
        "target_range_min": 70.0,
        "target_range_max": 140.0,
        "base_glucose": 100.0,
        "glucose_variability": 15.0,  # Low variability
        "sleep_quality": 0.85,  # High quality sleep
        "exercise_frequency": 0.6,  # Moderate exercise
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "bob@demo.glucolens.com",
        "full_name": "Bob Martinez",
        "age": 52,
        "gender": "male",
        "diabetes_type": "type_2",
        "profile": "variable",  # Variable glucose, stress patterns
        "target_range_min": 70.0,
        "target_range_max": 140.0,
        "base_glucose": 130.0,
        "glucose_variability": 35.0,  # High variability
        "sleep_quality": 0.60,  # Poor sleep
        "exercise_frequency": 0.3,  # Low exercise
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "email": "carol@demo.glucolens.com",
        "full_name": "Carol Chen",
        "age": 28,
        "gender": "female",
        "diabetes_type": "type_1",
        "profile": "active",  # Active lifestyle, exercise impact
        "target_range_min": 70.0,
        "target_range_max": 140.0,
        "base_glucose": 110.0,
        "glucose_variability": 25.0,  # Moderate variability
        "sleep_quality": 0.80,  # Good sleep
        "exercise_frequency": 0.9,  # High exercise
    },
]


async def create_demo_users(session: AsyncSession):
    """Create or update demo users in database."""
    print("\n📊 Creating demo users...")

    for user_data in DEMO_USERS:
        # Check if user exists
        result = await session.execute(
            select(User).where(User.id == UUID(user_data["id"]))
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"  ✓ User exists: {user_data['full_name']}")
            continue

        # Create new user
        user = User(
            id=UUID(user_data["id"]),
            email=user_data["email"],
            hashed_password=get_password_hash("demo123"),  # Not used in read-only
            full_name=user_data["full_name"],
            age=user_data["age"],
            gender=user_data["gender"],
            diabetes_type=user_data["diabetes_type"],
            diagnosis_date=datetime.now().date() - timedelta(days=365 * 5),
            target_range_min=user_data["target_range_min"],
            target_range_max=user_data["target_range_max"],
            timezone="America/New_York",
        )
        session.add(user)
        print(f"  ✓ Created: {user_data['full_name']}")

    await session.commit()
    print("✅ Demo users created\n")


async def generate_glucose_data(
    session: AsyncSession,
    user_id: UUID,
    profile: dict,
    days: int = 90
):
    """Generate realistic glucose readings for a user."""
    print(f"  📈 Generating {days} days of glucose data...")

    base_glucose = profile["base_glucose"]
    variability = profile["glucose_variability"]

    start_date = datetime.now() - timedelta(days=days)
    readings = []

    # Generate readings every 5 minutes
    current_time = start_date
    end_time = datetime.now()

    # Track previous value for smooth transitions
    prev_glucose = base_glucose

    while current_time < end_time:
        hour = current_time.hour

        # Time-of-day effects
        if 6 <= hour < 9:  # Morning spike (dawn phenomenon)
            time_effect = 15
        elif 12 <= hour < 14:  # Lunch spike
            time_effect = 20
        elif 18 <= hour < 20:  # Dinner spike
            time_effect = 25
        elif 2 <= hour < 4:  # Night low
            time_effect = -10
        else:
            time_effect = 0

        # Day-of-week effects (weekends different)
        if current_time.weekday() >= 5:  # Weekend
            weekend_effect = random.uniform(-5, 5)
        else:
            weekend_effect = 0

        # Smooth random walk
        random_change = random.gauss(0, variability / 10)
        target_glucose = base_glucose + time_effect + weekend_effect

        # Move towards target with some inertia
        new_glucose = prev_glucose * 0.8 + target_glucose * 0.2 + random_change

        # Clamp to realistic range
        new_glucose = max(50, min(350, new_glucose))

        reading = GlucoseReading(
            user_id=user_id,
            timestamp=current_time,
            value=round(new_glucose, 1),
            source="dexcom_g7"
        )
        readings.append(reading)

        prev_glucose = new_glucose
        current_time += timedelta(minutes=5)

    # Bulk insert
    session.add_all(readings)
    await session.commit()

    print(f"    ✓ Created {len(readings):,} glucose readings")


async def generate_sleep_data(
    session: AsyncSession,
    user_id: UUID,
    profile: dict,
    days: int = 90
):
    """Generate sleep data for a user."""
    print(f"  😴 Generating {days} days of sleep data...")

    sleep_quality = profile["sleep_quality"]
    start_date = datetime.now().date() - timedelta(days=days)

    sleep_records = []

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)

        # Base sleep duration (7-9 hours)
        base_duration = 7.5 + (sleep_quality - 0.7) * 2  # Better quality = more sleep
        duration_hours = base_duration + random.gauss(0, 0.5)
        duration_hours = max(5, min(10, duration_hours))

        # Sleep start time (10 PM - 1 AM)
        sleep_start_hour = 22 + random.randint(0, 3)
        if sleep_start_hour >= 24:
            sleep_start_hour -= 24
            sleep_start_date = current_date + timedelta(days=1)
        else:
            sleep_start_date = current_date

        sleep_start = datetime.combine(
            sleep_start_date,
            time(hour=sleep_start_hour, minute=random.randint(0, 59))
        )

        sleep_end = sleep_start + timedelta(hours=duration_hours)

        total_minutes = int(duration_hours * 60)

        # Sleep stage distribution based on quality
        deep_pct = 0.15 + (sleep_quality - 0.7) * 0.1
        rem_pct = 0.20 + (sleep_quality - 0.7) * 0.05
        light_pct = 0.50
        awake_pct = 1 - deep_pct - rem_pct - light_pct

        sleep_record = SleepData(
            user_id=user_id,
            date=current_date,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            deep_sleep_minutes=int(total_minutes * deep_pct),
            rem_sleep_minutes=int(total_minutes * rem_pct),
            light_sleep_minutes=int(total_minutes * light_pct),
            awake_minutes=int(total_minutes * awake_pct),
            quality_score=sleep_quality + random.gauss(0, 0.1)
        )
        sleep_records.append(sleep_record)

    session.add_all(sleep_records)
    await session.commit()

    print(f"    ✓ Created {len(sleep_records)} sleep records")


async def generate_meal_data(
    session: AsyncSession,
    user_id: UUID,
    profile: dict,
    days: int = 90
):
    """Generate meal data for a user."""
    print(f"  🍽️  Generating {days} days of meal data...")

    start_date = datetime.now().date() - timedelta(days=days)
    meals = []

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)

        # 3-4 meals per day
        num_meals = random.choice([3, 3, 3, 4])

        meal_times = {
            "breakfast": (7, 9),
            "lunch": (12, 14),
            "dinner": (18, 20),
            "snack": (15, 17)
        }

        day_meals = ["breakfast", "lunch", "dinner"]
        if num_meals == 4:
            day_meals.append("snack")

        for meal_type in day_meals:
            hour_range = meal_times[meal_type]
            meal_hour = random.randint(hour_range[0], hour_range[1])
            meal_time = datetime.combine(
                current_date,
                time(hour=meal_hour, minute=random.randint(0, 59))
            )

            # Meal composition
            if meal_type == "breakfast":
                carbs = random.uniform(40, 60)
                protein = random.uniform(15, 25)
                fat = random.uniform(10, 20)
            elif meal_type == "lunch":
                carbs = random.uniform(50, 80)
                protein = random.uniform(25, 40)
                fat = random.uniform(15, 30)
            elif meal_type == "dinner":
                carbs = random.uniform(50, 90)
                protein = random.uniform(30, 50)
                fat = random.uniform(20, 35)
            else:  # snack
                carbs = random.uniform(15, 30)
                protein = random.uniform(5, 15)
                fat = random.uniform(5, 15)

            calories = int(carbs * 4 + protein * 4 + fat * 9)
            glycemic_load = carbs * random.uniform(0.4, 0.7)

            meal = Meal(
                user_id=user_id,
                timestamp=meal_time,
                meal_type=meal_type,
                carbs_grams=round(carbs, 1),
                protein_grams=round(protein, 1),
                fat_grams=round(fat, 1),
                calories=calories,
                glycemic_load=round(glycemic_load, 1),
                description=f"Demo {meal_type}"
            )
            meals.append(meal)

    session.add_all(meals)
    await session.commit()

    print(f"    ✓ Created {len(meals)} meal records")


async def generate_activity_data(
    session: AsyncSession,
    user_id: UUID,
    profile: dict,
    days: int = 90
):
    """Generate activity data for a user."""
    print(f"  🏃 Generating {days} days of activity data...")

    exercise_frequency = profile["exercise_frequency"]
    start_date = datetime.now().date() - timedelta(days=days)

    activities = []

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)

        # Decide if user exercises this day
        if random.random() < exercise_frequency / 7:  # Convert weekly to daily probability
            # Activity time (morning or evening)
            if random.random() < 0.6:  # Morning exercise
                activity_hour = random.randint(6, 8)
            else:  # Evening exercise
                activity_hour = random.randint(17, 19)

            activity_time = datetime.combine(
                current_date,
                time(hour=activity_hour, minute=random.randint(0, 59))
            )

            # Activity types
            activity_types = ["running", "cycling", "walking", "swimming", "gym"]
            activity_type = random.choice(activity_types)

            # Duration and intensity
            duration = random.randint(20, 60)
            intensities = ["light", "moderate", "vigorous"]
            intensity = random.choice(intensities)

            if intensity == "light":
                calories_per_min = 5
                hr_base = 100
            elif intensity == "moderate":
                calories_per_min = 8
                hr_base = 130
            else:  # vigorous
                calories_per_min = 12
                hr_base = 160

            calories = duration * calories_per_min + random.randint(-20, 20)
            avg_hr = hr_base + random.randint(-10, 10)

            activity = Activity(
                user_id=user_id,
                timestamp=activity_time,
                activity_type=activity_type,
                duration_minutes=duration,
                intensity=intensity,
                calories_burned=calories,
                avg_heart_rate=avg_hr
            )
            activities.append(activity)

    session.add_all(activities)
    await session.commit()

    print(f"    ✓ Created {len(activities)} activity records")


async def main():
    """Main function to generate all demo data."""
    print("\n" + "="*60)
    print("🚀 GlucoLens Demo Data Generator")
    print("="*60)

    try:
        async with async_session_maker() as session:
            # Create demo users
            await create_demo_users(session)

            # Generate data for each user
            for user_data in DEMO_USERS:
                user_id = UUID(user_data["id"])
                print(f"\n👤 Generating data for: {user_data['full_name']}")
                print(f"   Profile: {user_data['profile']}")

                await generate_glucose_data(session, user_id, user_data, days=90)
                await generate_sleep_data(session, user_id, user_data, days=90)
                await generate_meal_data(session, user_id, user_data, days=90)
                await generate_activity_data(session, user_id, user_data, days=90)

                print(f"   ✅ Complete")

            print("\n" + "="*60)
            print("✅ Demo data generation complete!")
            print("="*60)
            print("\nNext steps:")
            print("1. Run ML analysis: python scripts/run_ml_pipeline.py")
            print("2. Export database: pg_dump -U glucolens glucolens > demo_data.sql")
            print("3. Deploy to AWS Lambda")
            print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
