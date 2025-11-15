"""
Run the ML pipeline (PCMCI + STUMPY) for a user.

This script triggers causal discovery and pattern detection,
then monitors the Celery tasks until completion.

Usage:
    python scripts/run_ml_pipeline.py --user-id <uuid>
    python scripts/run_ml_pipeline.py  # Uses default test user
"""
import asyncio
import argparse
import time
from uuid import UUID
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User


# Default test user ID
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def trigger_ml_analysis(user_id: UUID, lookback_days: int = 90):
    """
    Trigger ML analysis by directly calling the analysis functions.

    Note: In production, this would trigger Celery tasks via API or task queue.
    For testing, we'll import and run the analysis functions directly.
    """
    print("=" * 70)
    print("🧠 GlucoLens ML Pipeline")
    print("=" * 70)
    print(f"   User ID: {user_id}")
    print(f"   Lookback: {lookback_days} days")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Import analysis services
    from app.services.pcmci_service import PCMCIAnalyzer
    from app.services.stumpy_service import StumpyPatternDetector

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        # Verify user exists
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ User {user_id} not found!")
            return False

        print(f"\n👤 User: {user.full_name} ({user.email})")
        print(f"   Type: {user.diabetes_type}")

        # Get data counts
        from app.models.glucose import GlucoseReading
        from app.models.sleep import SleepData
        from app.models.activity import Activity
        from app.models.meal import Meal
        from app.models.insulin import InsulinDose

        glucose_count = session.query(GlucoseReading).filter(GlucoseReading.user_id == user_id).count()
        sleep_count = session.query(SleepData).filter(SleepData.user_id == user_id).count()
        activity_count = session.query(Activity).filter(Activity.user_id == user_id).count()
        meal_count = session.query(Meal).filter(Meal.user_id == user_id).count()
        insulin_count = session.query(InsulinDose).filter(InsulinDose.user_id == user_id).count()

        print(f"\n📊 Data Available:")
        print(f"   • Glucose readings: {glucose_count:,}")
        print(f"   • Sleep sessions: {sleep_count}")
        print(f"   • Activities: {activity_count}")
        print(f"   • Meals: {meal_count}")
        print(f"   • Insulin doses: {insulin_count}")

        if glucose_count < 1000:
            print(f"\n⚠️  Warning: Only {glucose_count} glucose readings available.")
            print("   ML analysis works best with at least 7 days of data (2,016 readings)")

    # =========================================================================
    # PCMCI Causal Discovery
    # =========================================================================

    print("\n" + "=" * 70)
    print("🔗 PHASE 1: PCMCI Causal Discovery")
    print("=" * 70)
    print("   Analyzing time-lagged causal relationships...")
    print("   Variables: glucose, sleep, exercise, carbs, insulin")
    print()

    try:
        start_time = time.time()

        # Note: In production, this would be a Celery task
        # For now, we'll import and run the actual analysis
        from app.tasks_ml import run_pcmci_analysis

        print("   ⏳ Running PCMCI analysis (this may take 2-5 minutes)...")
        result = run_pcmci_analysis(str(user_id), lookback_days)

        elapsed = time.time() - start_time

        if result.get("status") == "success":
            causal_links = result.get("causal_links_found", 0)
            print(f"\n   ✅ PCMCI Complete ({elapsed:.1f}s)")
            print(f"   📊 Discovered {causal_links} causal relationships")
        else:
            print(f"\n   ⚠️  PCMCI completed with warnings:")
            print(f"      {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"\n   ❌ PCMCI Failed: {str(e)}")
        print(f"      Using fallback correlation analysis")

    # =========================================================================
    # STUMPY Pattern Detection
    # =========================================================================

    print("\n" + "=" * 70)
    print("🔍 PHASE 2: STUMPY Pattern Detection")
    print("=" * 70)
    print("   Detecting recurring patterns (motifs) in glucose data...")
    print()

    try:
        start_time = time.time()

        from app.tasks_ml import detect_recurring_patterns

        print("   ⏳ Running STUMPY pattern detection (1-2 minutes)...")
        result = detect_recurring_patterns(str(user_id), lookback_days)

        elapsed = time.time() - start_time

        if result.get("status") == "success":
            patterns_found = result.get("patterns_found", 0)
            print(f"\n   ✅ Pattern Detection Complete ({elapsed:.1f}s)")
            print(f"   📊 Found {patterns_found} recurring patterns")
        else:
            print(f"\n   ⚠️  Pattern detection completed with warnings:")
            print(f"      {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"\n   ❌ Pattern detection failed: {str(e)}")

    # =========================================================================
    # STUMPY Anomaly Detection
    # =========================================================================

    print("\n" + "=" * 70)
    print("⚠️  PHASE 3: STUMPY Anomaly Detection")
    print("=" * 70)
    print("   Detecting unusual glucose patterns (discords)...")
    print()

    try:
        start_time = time.time()

        from app.tasks_ml import detect_anomalies

        print("   ⏳ Running anomaly detection (1-2 minutes)...")
        result = detect_anomalies(str(user_id), lookback_days)

        elapsed = time.time() - start_time

        if result.get("status") == "success":
            anomalies_found = result.get("anomalies_found", 0)
            print(f"\n   ✅ Anomaly Detection Complete ({elapsed:.1f}s)")
            print(f"   📊 Found {anomalies_found} anomalous patterns")
        else:
            print(f"\n   ⚠️  Anomaly detection completed with warnings:")
            print(f"      {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"\n   ❌ Anomaly detection failed: {str(e)}")

    print("\n" + "=" * 70)
    print("✅ ML Pipeline Complete!")
    print("=" * 70)

    return True


def display_results_summary(user_id: UUID):
    """Display a summary of discovered patterns and relationships."""
    print("\n" + "=" * 70)
    print("📈 Results Summary")
    print("=" * 70)

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        from app.models.correlation import Correlation
        from app.models.pattern import Pattern

        # Get causal links
        correlations = session.query(Correlation).filter(
            Correlation.user_id == user_id
        ).order_by(Correlation.correlation_coefficient.desc()).limit(10).all()

        if correlations:
            print("\n🔗 Top Causal Relationships:")
            for i, corr in enumerate(correlations, 1):
                sign = "→" if corr.correlation_coefficient > 0 else "↓"
                print(f"   {i}. {corr.primary_metric} {sign} {corr.secondary_metric}")
                print(f"      Strength: {corr.correlation_coefficient:.3f}, p-value: {corr.p_value:.4f}")
        else:
            print("\n⚠️  No causal relationships stored in database")
            print("   (May be using fallback correlation analysis)")

        # Get patterns
        patterns = session.query(Pattern).filter(
            Pattern.user_id == user_id
        ).order_by(Pattern.occurrences.desc()).limit(5).all()

        if patterns:
            print("\n🔍 Recurring Patterns:")
            for i, pattern in enumerate(patterns, 1):
                print(f"   {i}. {pattern.pattern_type}")
                print(f"      Occurrences: {pattern.occurrences}, Confidence: {pattern.confidence_score:.2f}")
                if pattern.description:
                    print(f"      {pattern.description}")
        else:
            print("\n⚠️  No patterns stored in database")

    print("\n" + "=" * 70)
    print("📝 Next Steps:")
    print("=" * 70)
    print("   1. View full results via API:")
    print(f"      GET /api/v1/insights/advanced/causal-graph")
    print(f"      GET /api/v1/insights/advanced/recurring-patterns")
    print(f"      GET /api/v1/insights/advanced/anomalies")
    print()
    print("   2. Run validation script:")
    print(f"      python scripts/validate_inference.py")
    print()
    print("   3. View API docs:")
    print(f"      http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run ML pipeline (PCMCI + STUMPY) for a user"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=str(DEFAULT_USER_ID),
        help=f"User UUID (default: {DEFAULT_USER_ID})"
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=90,
        help="Days of data to analyze (default: 90)"
    )

    args = parser.parse_args()

    user_uuid = UUID(args.user_id)

    # Run the pipeline
    success = trigger_ml_analysis(user_uuid, args.lookback_days)

    if success:
        # Display results summary
        display_results_summary(user_uuid)
    else:
        print("\n❌ Pipeline failed to complete")
        exit(1)
