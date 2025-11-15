"""Celery background tasks for ML analysis and data processing."""
from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta, date
from typing import List
import pandas as pd
import numpy as np
from uuid import UUID

from app.config import settings

# Create Celery app
celery_app = Celery(
    "glucolens",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    'aggregate-daily-data': {
        'task': 'app.tasks.aggregate_daily_data_for_all_users',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
    'compute-correlations': {
        'task': 'app.tasks.compute_correlations_for_all_users',
        'schedule': crontab(hour=4, minute=0),  # 4 AM daily
    },
    'discover-patterns': {
        'task': 'app.tasks.discover_patterns_for_all_users',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),  # Sunday midnight
    },
}


# ==================== DATA AGGREGATION ====================

@celery_app.task
def aggregate_daily_data(user_id: str, target_date: str = None):
    """
    Aggregate daily statistics for a user.

    Args:
        user_id: UUID string of the user
        target_date: ISO date string (default: yesterday)
    """
    from sqlalchemy import create_engine, select, func
    from sqlalchemy.orm import Session
    from app.models.glucose import GlucoseReading
    from app.models.sleep import SleepData
    from app.models.activity import Activity
    from app.models.meal import Meal
    from app.models.aggregate import DailyAggregate
    from app.models.user import User

    # Create sync engine for Celery
    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        user_uuid = UUID(user_id)

        # Determine target date
        if target_date:
            target_dt = datetime.fromisoformat(target_date).date()
        else:
            target_dt = (datetime.now() - timedelta(days=1)).date()

        start_dt = datetime.combine(target_dt, datetime.min.time())
        end_dt = datetime.combine(target_dt, datetime.max.time())

        # Get user's target ranges
        user = session.query(User).filter(User.id == user_uuid).first()
        target_min = float(user.target_glucose_min) if user else 70.0
        target_max = float(user.target_glucose_max) if user else 180.0

        # Aggregate glucose data
        glucose_query = (
            select(
                func.avg(GlucoseReading.value).label("avg_glucose"),
                func.min(GlucoseReading.value).label("min_glucose"),
                func.max(GlucoseReading.value).label("max_glucose"),
                func.stddev(GlucoseReading.value).label("std_glucose"),
                func.count(GlucoseReading.id).label("total_readings")
            )
            .where(
                GlucoseReading.user_id == user_uuid,
                GlucoseReading.timestamp >= start_dt,
                GlucoseReading.timestamp <= end_dt
            )
        )
        glucose_stats = session.execute(glucose_query).one()

        # Calculate time in range
        tir_query = select(func.count(GlucoseReading.id)).where(
            GlucoseReading.user_id == user_uuid,
            GlucoseReading.timestamp >= start_dt,
            GlucoseReading.timestamp <= end_dt,
            GlucoseReading.value >= target_min,
            GlucoseReading.value <= target_max
        )
        in_range_count = session.execute(tir_query).scalar()

        time_in_range_pct = (in_range_count / glucose_stats.total_readings * 100) if glucose_stats.total_readings > 0 else 0

        # Aggregate sleep data
        sleep_query = (
            select(
                func.sum(SleepData.duration_minutes).label("total_sleep"),
                func.avg(SleepData.quality_score).label("avg_quality")
            )
            .where(
                SleepData.user_id == user_uuid,
                SleepData.date == target_dt
            )
        )
        sleep_stats = session.execute(sleep_query).one()

        # Aggregate activities
        activity_query = select(func.sum(Activity.duration_minutes)).where(
            Activity.user_id == user_uuid,
            Activity.timestamp >= start_dt,
            Activity.timestamp <= end_dt
        )
        total_exercise = session.execute(activity_query).scalar() or 0

        # Aggregate meals
        meal_query = (
            select(
                func.sum(Meal.carbs_grams).label("total_carbs"),
                func.sum(Meal.calories).label("total_calories")
            )
            .where(
                Meal.user_id == user_uuid,
                Meal.timestamp >= start_dt,
                Meal.timestamp <= end_dt
            )
        )
        meal_stats = session.execute(meal_query).one()

        # Create or update daily aggregate
        existing = session.query(DailyAggregate).filter(
            DailyAggregate.user_id == user_uuid,
            DailyAggregate.date == target_dt
        ).first()

        if existing:
            # Update existing
            existing.avg_glucose = glucose_stats.avg_glucose
            existing.min_glucose = glucose_stats.min_glucose
            existing.max_glucose = glucose_stats.max_glucose
            existing.std_glucose = glucose_stats.std_glucose
            existing.time_in_range_percent = time_in_range_pct
            existing.total_sleep_minutes = sleep_stats.total_sleep
            existing.sleep_quality_score = sleep_stats.avg_quality
            existing.total_exercise_minutes = total_exercise
            existing.total_carbs_grams = meal_stats.total_carbs
            existing.total_calories = meal_stats.total_calories
            existing.computed_at = datetime.now()
        else:
            # Create new
            aggregate = DailyAggregate(
                user_id=user_uuid,
                date=target_dt,
                avg_glucose=glucose_stats.avg_glucose,
                min_glucose=glucose_stats.min_glucose,
                max_glucose=glucose_stats.max_glucose,
                std_glucose=glucose_stats.std_glucose,
                time_in_range_percent=time_in_range_pct,
                total_sleep_minutes=sleep_stats.total_sleep,
                sleep_quality_score=sleep_stats.avg_quality,
                total_exercise_minutes=total_exercise,
                total_carbs_grams=meal_stats.total_carbs,
                total_calories=meal_stats.total_calories
            )
            session.add(aggregate)

        session.commit()

    return {"status": "success", "user_id": user_id, "date": str(target_dt)}


@celery_app.task
def aggregate_daily_data_for_all_users():
    """Run daily aggregation for all users (scheduled task)."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.user import User

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        users = session.execute(select(User.id)).scalars().all()

        for user_id in users:
            aggregate_daily_data.delay(str(user_id))

    return {"status": "success", "users_queued": len(users)}


# ==================== CORRELATION ANALYSIS ====================

@celery_app.task
def compute_correlations(user_id: str, lookback_days: int = 90):
    """
    Compute correlations using PCMCI causal discovery.

    Args:
        user_id: UUID string
        lookback_days: Number of days to analyze
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.aggregate import DailyAggregate
    from app.models.correlation import Correlation

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        user_uuid = UUID(user_id)

        # Fetch daily aggregates
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=lookback_days)

        query = select(DailyAggregate).where(
            DailyAggregate.user_id == user_uuid,
            DailyAggregate.date >= start_date,
            DailyAggregate.date <= end_date
        ).order_by(DailyAggregate.date)

        aggregates = session.execute(query).scalars().all()

        if len(aggregates) < settings.PCMCI_MIN_DATA_POINTS:
            return {"status": "insufficient_data", "records": len(aggregates)}

        # Convert to DataFrame
        df = pd.DataFrame([{
            'date': agg.date,
            'avg_glucose': float(agg.avg_glucose) if agg.avg_glucose else None,
            'std_glucose': float(agg.std_glucose) if agg.std_glucose else None,
            'sleep_duration': float(agg.total_sleep_minutes) / 60 if agg.total_sleep_minutes else None,
            'sleep_quality': float(agg.sleep_quality_score) if agg.sleep_quality_score else None,
            'exercise_minutes': float(agg.total_exercise_minutes) if agg.total_exercise_minutes else None,
            'carbs_grams': float(agg.total_carbs_grams) if agg.total_carbs_grams else None,
        } for agg in aggregates])

        # Drop rows with missing values
        df = df.dropna()

        if len(df) < settings.PCMCI_MIN_DATA_POINTS:
            return {"status": "insufficient_clean_data", "records": len(df)}

        # Simple correlation analysis (replace with PCMCI in production)
        # Note: PCMCI requires more setup - using Pearson correlation for MVP
        features = ['sleep_duration', 'sleep_quality', 'exercise_minutes', 'carbs_grams']
        targets = ['avg_glucose', 'std_glucose']

        correlations_found = 0

        for feature in features:
            for target in targets:
                if feature in df.columns and target in df.columns:
                    corr = df[feature].corr(df[target])

                    # Statistical significance (simple t-test)
                    n = len(df)
                    t_stat = corr * np.sqrt(n - 2) / np.sqrt(1 - corr**2)
                    from scipy import stats
                    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))

                    # Confidence level
                    if p_value < 0.01:
                        confidence = "high"
                    elif p_value < 0.05:
                        confidence = "medium"
                    else:
                        confidence = "low"

                    # Save correlation
                    existing = session.query(Correlation).filter(
                        Correlation.user_id == user_uuid,
                        Correlation.factor_x == feature,
                        Correlation.factor_y == target,
                        Correlation.lag_days == 0
                    ).first()

                    if existing:
                        existing.correlation_coefficient = corr
                        existing.p_value = p_value
                        existing.sample_size = n
                        existing.confidence_level = confidence
                        existing.computed_at = datetime.now()
                    else:
                        correlation = Correlation(
                            user_id=user_uuid,
                            factor_x=feature,
                            factor_y=target,
                            correlation_coefficient=corr,
                            p_value=p_value,
                            lag_days=0,
                            sample_size=n,
                            confidence_level=confidence
                        )
                        session.add(correlation)

                    correlations_found += 1

        session.commit()

    return {"status": "success", "correlations_computed": correlations_found}


@celery_app.task
def compute_correlations_for_all_users():
    """Run correlation analysis for all users (scheduled task)."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.user import User

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        users = session.execute(select(User.id)).scalars().all()

        for user_id in users:
            compute_correlations.delay(str(user_id))

    return {"status": "success", "users_queued": len(users)}


# ==================== PATTERN DISCOVERY ====================

@celery_app.task
def discover_patterns(user_id: str, lookback_days: int = 90):
    """
    Discover patterns using association rules and STUMPY.

    Args:
        user_id: UUID string
        lookback_days: Number of days to analyze
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.aggregate import DailyAggregate
    from app.models.pattern import Pattern
    from mlxtend.frequent_patterns import apriori, association_rules

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        user_uuid = UUID(user_id)

        # Fetch daily aggregates
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=lookback_days)

        query = select(DailyAggregate).where(
            DailyAggregate.user_id == user_uuid,
            DailyAggregate.date >= start_date,
            DailyAggregate.date <= end_date
        ).order_by(DailyAggregate.date)

        aggregates = session.execute(query).scalars().all()

        if len(aggregates) < settings.PATTERN_DISCOVERY_MIN_DAYS:
            return {"status": "insufficient_data", "records": len(aggregates)}

        # Convert to binary features for association rules
        binary_df = pd.DataFrame([{
            'date': agg.date,
            'good_glucose': bool(agg.time_in_range_percent and agg.time_in_range_percent > 70),
            'high_sleep': bool(agg.total_sleep_minutes and agg.total_sleep_minutes > 420),
            'good_sleep_quality': bool(agg.sleep_quality_score and agg.sleep_quality_score > 7),
            'exercised': bool(agg.total_exercise_minutes and agg.total_exercise_minutes > 30),
            'low_carbs': bool(agg.total_carbs_grams and agg.total_carbs_grams < 150),
        } for agg in aggregates])

        # Association rules mining
        try:
            # Prepare data for apriori (boolean DataFrame)
            features_df = binary_df.drop('date', axis=1)

            # Find frequent itemsets
            frequent_itemsets = apriori(features_df, min_support=0.3, use_colnames=True)

            if len(frequent_itemsets) > 0:
                # Generate association rules
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)

                patterns_found = 0

                for _, rule in rules.iterrows():
                    # Extract antecedents and consequents
                    antecedent = list(rule['antecedents'])
                    consequent = list(rule['consequents'])

                    description = f"IF {', '.join(antecedent)} THEN {', '.join(consequent)}"

                    # Find example dates
                    mask = features_df[antecedent].all(axis=1) & features_df[consequent].all(axis=1)
                    example_dates = binary_df[mask]['date'].tolist()[:5]

                    # Save pattern
                    pattern = Pattern(
                        user_id=user_uuid,
                        pattern_type="association_rule",
                        description=description,
                        confidence=float(rule['confidence']),
                        support=float(rule['support']),
                        occurrences=len(example_dates),
                        example_dates=example_dates,
                        metadata={
                            "antecedents": antecedent,
                            "consequents": consequent,
                            "lift": float(rule['lift'])
                        }
                    )
                    session.add(pattern)
                    patterns_found += 1

                session.commit()
                return {"status": "success", "patterns_found": patterns_found}
            else:
                return {"status": "no_patterns", "message": "No frequent patterns found"}

        except Exception as e:
            return {"status": "error", "message": str(e)}


@celery_app.task
def discover_patterns_for_all_users():
    """Run pattern discovery for all users (scheduled task)."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.user import User

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        users = session.execute(select(User.id)).scalars().all()

        for user_id in users:
            discover_patterns.delay(str(user_id))

    return {"status": "success", "users_queued": len(users)}


# ==================== FULL ANALYSIS ====================

@celery_app.task
def run_full_analysis(user_id: str):
    """Run complete analysis pipeline for a user."""
    # Aggregate recent data
    for days_ago in range(7):
        target_date = (datetime.now() - timedelta(days=days_ago)).date()
        aggregate_daily_data.delay(user_id, str(target_date))

    # Compute correlations
    compute_correlations.delay(user_id)

    # Discover patterns
    discover_patterns.delay(user_id)

    return {"status": "analysis_queued", "user_id": user_id}
