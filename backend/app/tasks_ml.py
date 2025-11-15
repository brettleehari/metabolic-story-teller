"""
Celery tasks for advanced ML analysis (PCMCI and STUMPY).

These tasks run PCMCI causal discovery and STUMPY pattern detection.
"""
from celery import shared_task
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from uuid import UUID
from typing import Dict, Any
import json

from app.config import settings
from app.services import PCMCIAnalyzer, StumpyPatternDetector


@shared_task(name='app.tasks_ml.run_pcmci_analysis')
def run_pcmci_analysis(user_id: str, lookback_days: int = 90) -> Dict[str, Any]:
    """
    Run PCMCI causal discovery analysis for a user.

    Args:
        user_id: UUID string of the user
        lookback_days: Number of days to analyze (default 90)

    Returns:
        Dictionary with analysis results
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
            'glucose_variability': float(agg.std_glucose) if agg.std_glucose else None,
            'sleep_hours': float(agg.total_sleep_minutes) / 60 if agg.total_sleep_minutes else None,
            'sleep_quality': float(agg.sleep_quality_score) if agg.sleep_quality_score else None,
            'exercise_minutes': float(agg.total_exercise_minutes) if agg.total_exercise_minutes else None,
            'carbs_grams': float(agg.total_carbs_grams) if agg.total_carbs_grams else None,
        } for agg in aggregates])

        # Set date as index
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        # Drop rows with missing values
        df = df.dropna()

        if len(df) < settings.PCMCI_MIN_DATA_POINTS:
            return {"status": "insufficient_clean_data", "records": len(df)}

        # Run PCMCI analysis
        pcmci_analyzer = PCMCIAnalyzer(tau_max=7, alpha_level=0.05)
        variables = [
            'sleep_hours',
            'sleep_quality',
            'exercise_minutes',
            'carbs_grams',
            'avg_glucose',
            'glucose_variability'
        ]

        results = pcmci_analyzer.analyze_causality(
            data=df,
            variables=variables,
            min_data_points=settings.PCMCI_MIN_DATA_POINTS
        )

        if 'error' in results:
            return results

        # Store causal links in database
        causal_links = results.get('causal_links', [])
        correlations_stored = 0

        for link in causal_links:
            # Update or create correlation record
            existing = session.query(Correlation).filter(
                Correlation.user_id == user_uuid,
                Correlation.factor_x == link['from'],
                Correlation.factor_y == link['to'],
                Correlation.lag_days == link['lag']
            ).first()

            if existing:
                existing.correlation_coefficient = link['strength']
                existing.p_value = link['p_value']
                existing.sample_size = results['sample_size']
                existing.confidence_level = link['confidence']
                existing.computed_at = datetime.now()
            else:
                correlation = Correlation(
                    user_id=user_uuid,
                    factor_x=link['from'],
                    factor_y=link['to'],
                    correlation_coefficient=link['strength'],
                    p_value=link['p_value'],
                    lag_days=link['lag'],
                    sample_size=results['sample_size'],
                    confidence_level=link['confidence']
                )
                session.add(correlation)

            correlations_stored += 1

        session.commit()

        return {
            "status": "success",
            "user_id": user_id,
            "method": results['method'],
            "causal_links_found": len(causal_links),
            "correlations_stored": correlations_stored,
            "sample_size": results['sample_size']
        }


@shared_task(name='app.tasks_ml.detect_recurring_patterns')
def detect_recurring_patterns(user_id: str, lookback_days: int = 90) -> Dict[str, Any]:
    """
    Detect recurring glucose patterns using STUMPY.

    Args:
        user_id: UUID string of the user
        lookback_days: Number of days to analyze

    Returns:
        Dictionary with detected patterns
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.glucose import GlucoseReading
    from app.models.pattern import Pattern

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        user_uuid = UUID(user_id)

        # Fetch glucose readings
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        query = select(GlucoseReading).where(
            GlucoseReading.user_id == user_uuid,
            GlucoseReading.timestamp >= start_date,
            GlucoseReading.timestamp <= end_date
        ).order_by(GlucoseReading.timestamp)

        readings = session.execute(query).scalars().all()

        if len(readings) < 1000:
            return {"status": "insufficient_data", "records": len(readings)}

        # Convert to pandas Series
        glucose_series = pd.Series(
            [float(r.value) for r in readings],
            index=[r.timestamp for r in readings]
        )

        # Run STUMPY pattern detection
        stumpy_detector = StumpyPatternDetector(window_size_hours=24)

        # Detect recurring patterns
        pattern_results = stumpy_detector.detect_recurring_patterns(
            glucose_series=glucose_series,
            reading_interval_minutes=5,
            top_k=5
        )

        if 'error' in pattern_results:
            return pattern_results

        # Store patterns in database
        patterns_stored = 0

        for pattern in pattern_results.get('patterns', []):
            # Create pattern description
            summary = pattern['pattern_summary']
            description = (
                f"Recurring {summary['duration_hours']}h pattern: "
                f"avg {summary['mean']:.1f} mg/dL, "
                f"occurs on {pattern['occurrences']} days"
            )

            # Create pattern record
            db_pattern = Pattern(
                user_id=user_uuid,
                pattern_type='recurring',
                description=description,
                confidence=0.8,  # High confidence for STUMPY motifs
                support=pattern['occurrences'] / pattern_results['total_data_points'],
                occurrences=pattern['occurrences'],
                example_dates=[pd.to_datetime(d).date() for d in pattern['example_dates'][:5]],
                metadata={
                    "pattern_id": pattern['pattern_id'],
                    "pattern_summary": summary,
                    "method": "STUMPY",
                    "window_size_hours": pattern_results['window_size_hours']
                }
            )
            session.add(db_pattern)
            patterns_stored += 1

        session.commit()

        return {
            "status": "success",
            "user_id": user_id,
            "method": pattern_results['method'],
            "patterns_found": pattern_results['patterns_found'],
            "patterns_stored": patterns_stored
        }


@shared_task(name='app.tasks_ml.detect_anomalies')
def detect_anomalies(user_id: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Detect anomalous glucose patterns using STUMPY.

    Args:
        user_id: UUID string of the user
        lookback_days: Number of days to analyze

    Returns:
        Dictionary with detected anomalies
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.glucose import GlucoseReading
    from app.models.pattern import Pattern

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        user_uuid = UUID(user_id)

        # Fetch glucose readings
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        query = select(GlucoseReading).where(
            GlucoseReading.user_id == user_uuid,
            GlucoseReading.timestamp >= start_date,
            GlucoseReading.timestamp <= end_date
        ).order_by(GlucoseReading.timestamp)

        readings = session.execute(query).scalars().all()

        if len(readings) < 500:
            return {"status": "insufficient_data", "records": len(readings)}

        # Convert to pandas Series
        glucose_series = pd.Series(
            [float(r.value) for r in readings],
            index=[r.timestamp for r in readings]
        )

        # Run STUMPY anomaly detection
        stumpy_detector = StumpyPatternDetector(window_size_hours=24)
        anomaly_results = stumpy_detector.detect_anomalies(
            glucose_series=glucose_series,
            reading_interval_minutes=5,
            top_k=5
        )

        if 'error' in anomaly_results:
            return anomaly_results

        # Store anomalies in database
        anomalies_stored = 0

        for anomaly in anomaly_results.get('anomalies', []):
            summary = anomaly.get('pattern_summary', {})
            description = (
                f"Anomalous pattern detected on {anomaly['date']}: "
                f"unusual glucose behavior (severity: {anomaly['severity']})"
            )

            if summary:
                description += f", avg {summary.get('mean', 0):.1f} mg/dL"

            # Create pattern record for anomaly
            db_pattern = Pattern(
                user_id=user_uuid,
                pattern_type='anomaly',
                description=description,
                confidence=0.9 if anomaly['severity'] == 'high' else 0.7,
                support=1 / anomaly_results['total_data_points'],
                occurrences=1,
                example_dates=[pd.to_datetime(anomaly['date']).date()],
                metadata={
                    "anomaly_id": anomaly['anomaly_id'],
                    "severity": anomaly['severity'],
                    "timestamp": anomaly['timestamp'],
                    "method": "STUMPY Discord",
                    "pattern_summary": summary
                }
            )
            session.add(db_pattern)
            anomalies_stored += 1

        session.commit()

        return {
            "status": "success",
            "user_id": user_id,
            "method": anomaly_results['method'],
            "anomalies_found": anomaly_results['anomalies_found'],
            "anomalies_stored": anomalies_stored
        }


@shared_task(name='app.tasks_ml.run_full_ml_analysis')
def run_full_ml_analysis(user_id: str) -> Dict[str, Any]:
    """
    Run complete ML analysis pipeline for a user.

    This includes:
    1. PCMCI causal discovery
    2. STUMPY recurring pattern detection
    3. STUMPY anomaly detection

    Args:
        user_id: UUID string of the user

    Returns:
        Summary of all analyses
    """
    results = {}

    # Run PCMCI causal analysis
    pcmci_result = run_pcmci_analysis.delay(user_id)
    results['pcmci'] = f"Task queued: {pcmci_result.id}"

    # Run STUMPY pattern detection
    pattern_result = detect_recurring_patterns.delay(user_id)
    results['patterns'] = f"Task queued: {pattern_result.id}"

    # Run anomaly detection
    anomaly_result = detect_anomalies.delay(user_id)
    results['anomalies'] = f"Task queued: {anomaly_result.id}"

    return {
        "status": "ml_analysis_queued",
        "user_id": user_id,
        "tasks": results
    }


@shared_task(name='app.tasks_ml.run_ml_analysis_for_all_users')
def run_ml_analysis_for_all_users() -> Dict[str, Any]:
    """
    Run ML analysis for all users (scheduled task).

    This can be scheduled to run weekly.
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.user import User

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        users = session.execute(select(User.id)).scalars().all()

        for user_id in users:
            run_full_ml_analysis.delay(str(user_id))

    return {"status": "success", "users_queued": len(users)}
