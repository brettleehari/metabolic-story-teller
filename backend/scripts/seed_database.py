"""
Seed the database with a test user and comprehensive sample data.

This script:
1. Creates a test user with realistic profile
2. Runs the comprehensive data generator
3. Verifies data integrity

Usage:
    python scripts/seed_database.py --days 90
"""
import asyncio
import argparse
from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.utils.auth import get_password_hash
from generate_sample_data_v2 import generate_comprehensive_data


# Test user configuration
TEST_USER_CONFIG = {
    "id": UUID("00000000-0000-0000-0000-000000000001"),
    "email": "demo@glucolens.io",
    "password": "demo123",  # Will be hashed
    "full_name": "John Doe",
    "date_of_birth": date(1985, 6, 15),  # 38 years old
    "height_cm": 175.0,
    "weight_kg": 85.0,  # Initial weight (will decrease over time)
    "gender": "male",
    "diabetes_type": "type1",
    "diagnosis_date": date(2020, 3, 1),
    "insulin_dependent": True,
    "ethnicity": "caucasian",
    "cgm_type": "dexcom_g7",
    "target_glucose_min": 70.0,
    "target_glucose_max": 180.0,
    "timezone": "America/New_York",
}


def create_test_user(session: Session) -> User:
    """Create or update test user in database."""
    print("👤 Creating test user...")

    # Check if user already exists
    existing_user = session.query(User).filter(User.id == TEST_USER_CONFIG["id"]).first()

    if existing_user:
        print(f"  ⚠️  User already exists: {existing_user.email}")
        print("  ℹ️  Updating user profile...")

        # Update fields
        for key, value in TEST_USER_CONFIG.items():
            if key == "password":
                existing_user.password_hash = get_password_hash(value)
            elif key != "id":
                setattr(existing_user, key, value)

        session.commit()
        session.refresh(existing_user)
        return existing_user

    # Create new user
    user_data = TEST_USER_CONFIG.copy()
    password = user_data.pop("password")

    user = User(
        **user_data,
        password_hash=get_password_hash(password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    print(f"  ✅ Created test user: {user.email}")
    print(f"     ID: {user.id}")
    print(f"     Password: demo123")
    print(f"     Type: {user.diabetes_type}")
    print(f"     Height: {user.height_cm} cm")
    print(f"     Weight: {user.weight_kg} kg")
    print(f"     BMI: {float(user.weight_kg) / ((float(user.height_cm)/100)**2):.1f}")

    return user


def verify_data_integrity(session: Session, user_id: UUID):
    """Verify that all data was generated correctly."""
    print("\n🔍 Verifying data integrity...")

    from app.models.glucose import GlucoseReading
    from app.models.sleep import SleepData
    from app.models.activity import Activity
    from app.models.meal import Meal
    from app.models.insulin import InsulinDose
    from app.models.blood_pressure import BloodPressure
    from app.models.body_metrics import BodyMetrics
    from app.models.hba1c import HbA1c
    from app.models.medication import Medication

    checks = [
        ("Glucose readings", GlucoseReading),
        ("Sleep sessions", SleepData),
        ("Activities", Activity),
        ("Meals", Meal),
        ("Insulin doses", InsulinDose),
        ("Blood pressure", BloodPressure),
        ("Body metrics", BodyMetrics),
        ("HbA1c readings", HbA1c),
        ("Medications", Medication),
    ]

    all_passed = True

    for name, model in checks:
        count = session.query(model).filter(model.user_id == user_id).count()
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {name}: {count} records")

        if count == 0:
            all_passed = False

    if all_passed:
        print("\n✅ All data integrity checks passed!")
    else:
        print("\n⚠️  Some data types are missing!")

    return all_passed


def seed_database(days: int = 90, force: bool = False):
    """Main seeding function."""
    print("=" * 60)
    print("🌱 GlucoLens Database Seeding")
    print("=" * 60)

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        # Step 1: Create test user
        user = create_test_user(session)

        # Step 2: Check if data already exists
        from app.models.glucose import GlucoseReading
        existing_data = session.query(GlucoseReading).filter(
            GlucoseReading.user_id == user.id
        ).count()

        if existing_data > 0 and not force:
            print(f"\n⚠️  User already has {existing_data} glucose readings!")
            print("   Use --force to regenerate data (will delete existing data)")
            return

        if existing_data > 0 and force:
            print(f"\n🗑️  Deleting existing data ({existing_data} glucose readings)...")
            # Note: Other data will cascade delete due to foreign keys
            session.query(GlucoseReading).filter(GlucoseReading.user_id == user.id).delete()
            session.commit()
            print("   ✅ Existing data deleted")

    # Step 3: Generate comprehensive data
    print(f"\n📊 Generating {days} days of comprehensive health data...")
    print("   (This may take a few minutes...)\n")

    generate_comprehensive_data(
        user_id=user.id,
        days=days,
        height_cm=float(user.height_cm)
    )

    # Step 4: Verify data integrity
    with Session(engine) as session:
        verify_data_integrity(session, user.id)

    print("\n" + "=" * 60)
    print("✅ Database seeding complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("   2. Login with: demo@glucolens.io / demo123")
    print("   3. Run ML pipeline: python scripts/run_ml_pipeline.py")
    print("   4. View insights: http://localhost:8000/docs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed GlucoLens database with test data")
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days to generate (default: 90)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration (deletes existing data)"
    )

    args = parser.parse_args()

    seed_database(days=args.days, force=args.force)
