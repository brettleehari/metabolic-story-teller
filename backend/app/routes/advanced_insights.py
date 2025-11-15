"""Advanced insights endpoints for PCMCI and STUMPY analysis."""
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta
import pandas as pd

from app.models.base import get_db
from app.models.user import User
from app.models.correlation import Correlation
from app.models.pattern import Pattern
from app.models.aggregate import DailyAggregate
from app.models.glucose import GlucoseReading
from app.dependencies import get_current_user
from app.schemas.advanced_insights import (
    CausalAnalysisResponse,
    CausalLink,
    CausalGraph,
    RecurringPatternsResponse,
    RecurringPattern,
    AnomaliesResponse,
    Anomaly,
    TopCausesResponse,
    TopCause
)
from app.services import PCMCIAnalyzer, StumpyPatternDetector

router = APIRouter(prefix="/insights/advanced", tags=["advanced-insights"])


@router.get("/causal-graph", response_model=CausalAnalysisResponse)
async def get_causal_graph(
    lookback_days: int = Query(90, le=365, description="Days of data to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get causal graph showing relationships between factors and glucose.

    Uses PCMCI algorithm to discover time-lagged causal relationships.
    """
    # Fetch daily aggregates
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=lookback_days)

    query = select(DailyAggregate).where(
        DailyAggregate.user_id == current_user.id,
        DailyAggregate.date >= start_date,
        DailyAggregate.date <= end_date
    ).order_by(DailyAggregate.date)

    result = await db.execute(query)
    aggregates = result.scalars().all()

    if len(aggregates) < 30:
        return CausalAnalysisResponse(
            method="PCMCI",
            causal_links=[],
            variables=[],
            tau_max=7,
            alpha_level=0.05,
            sample_size=len(aggregates)
        )

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

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').dropna()

    if len(df) < 30:
        return CausalAnalysisResponse(
            method="PCMCI",
            causal_links=[],
            variables=[],
            tau_max=7,
            alpha_level=0.05,
            sample_size=len(df)
        )

    # Run PCMCI analysis
    pcmci_analyzer = PCMCIAnalyzer(tau_max=7, alpha_level=0.05)
    variables = ['sleep_hours', 'sleep_quality', 'exercise_minutes', 'carbs_grams', 'avg_glucose', 'glucose_variability']

    results = pcmci_analyzer.analyze_causality(
        data=df,
        variables=variables,
        min_data_points=30
    )

    # Format causal links
    causal_links = [
        CausalLink(
            **{"from": link['from'], "to": link['to']},
            lag=link['lag'],
            strength=link['strength'],
            p_value=link['p_value'],
            confidence=link['confidence'],
            sample_size=link.get('sample_size', results['sample_size'])
        )
        for link in results.get('causal_links', [])
    ]

    # Format causal graph
    causal_graph = pcmci_analyzer.format_causal_graph(results.get('causal_links', []))

    return CausalAnalysisResponse(
        method=results['method'],
        causal_links=causal_links,
        causal_graph=CausalGraph(**causal_graph) if causal_graph else None,
        variables=results['variables'],
        tau_max=results['tau_max'],
        alpha_level=results['alpha_level'],
        sample_size=results['sample_size'],
        computed_at=datetime.now().isoformat()
    )


@router.get("/recurring-patterns", response_model=RecurringPatternsResponse)
async def get_recurring_patterns(
    lookback_days: int = Query(90, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recurring glucose patterns discovered by STUMPY.

    Returns patterns that occur multiple times in the data.
    """
    # Fetch glucose readings
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)

    query = select(GlucoseReading).where(
        GlucoseReading.user_id == current_user.id,
        GlucoseReading.timestamp >= start_date,
        GlucoseReading.timestamp <= end_date
    ).order_by(GlucoseReading.timestamp)

    result = await db.execute(query)
    readings = result.scalars().all()

    if len(readings) < 1000:
        return RecurringPatternsResponse(
            method="STUMPY",
            window_size_hours=24,
            patterns_found=0,
            patterns=[],
            total_data_points=len(readings)
        )

    # Convert to pandas Series
    glucose_series = pd.Series(
        [float(r.value) for r in readings],
        index=[r.timestamp for r in readings]
    )

    # Run STUMPY pattern detection
    stumpy_detector = StumpyPatternDetector(window_size_hours=24)
    pattern_results = stumpy_detector.detect_recurring_patterns(
        glucose_series=glucose_series,
        reading_interval_minutes=5,
        top_k=5
    )

    # Format patterns
    patterns = [
        RecurringPattern(
            pattern_id=p['pattern_id'],
            occurrences=p['occurrences'],
            example_dates=p['example_dates'],
            example_times=p.get('example_times'),
            pattern_summary=p['pattern_summary'],
            pattern_values=p.get('pattern_values'),
            description=f"Pattern occurs {p['occurrences']} times with avg glucose {p['pattern_summary']['mean']:.1f} mg/dL"
        )
        for p in pattern_results.get('patterns', [])
    ]

    return RecurringPatternsResponse(
        method=pattern_results['method'],
        window_size_hours=pattern_results['window_size_hours'],
        patterns_found=pattern_results['patterns_found'],
        patterns=patterns,
        total_data_points=pattern_results['total_data_points']
    )


@router.get("/anomalies", response_model=AnomaliesResponse)
async def get_anomalies(
    lookback_days: int = Query(30, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get anomalous glucose patterns detected by STUMPY.

    Returns unusual patterns that don't match the normal behavior.
    """
    # Fetch glucose readings
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)

    query = select(GlucoseReading).where(
        GlucoseReading.user_id == current_user.id,
        GlucoseReading.timestamp >= start_date,
        GlucoseReading.timestamp <= end_date
    ).order_by(GlucoseReading.timestamp)

    result = await db.execute(query)
    readings = result.scalars().all()

    if len(readings) < 500:
        return AnomaliesResponse(
            method="STUMPY",
            anomalies_found=0,
            anomalies=[],
            total_data_points=len(readings)
        )

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

    # Format anomalies
    anomalies = [
        Anomaly(
            anomaly_id=a['anomaly_id'],
            timestamp=a['timestamp'],
            date=a['date'],
            time=a['time'],
            distance=a.get('distance'),
            z_score=a.get('z_score'),
            severity=a['severity'],
            pattern_summary=a.get('pattern_summary'),
            values=a.get('values'),
            description=f"Anomalous pattern on {a['date']} at {a['time']} (severity: {a['severity']})"
        )
        for a in anomaly_results.get('anomalies', [])
    ]

    return AnomaliesResponse(
        method=anomaly_results['method'],
        window_size_hours=anomaly_results.get('window_size_hours'),
        anomalies_found=anomaly_results['anomalies_found'],
        anomalies=anomalies,
        total_data_points=anomaly_results['total_data_points']
    )


@router.get("/top-causes/{target}", response_model=TopCausesResponse)
async def get_top_causes(
    target: str,
    lookback_days: int = Query(90, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get top causes affecting a target variable (e.g., 'avg_glucose').

    Uses PCMCI causal discovery to find what most influences the target.
    """
    # Fetch correlations from database
    query = select(Correlation).where(
        Correlation.user_id == current_user.id,
        Correlation.factor_y == target
    ).order_by(Correlation.correlation_coefficient.desc()).limit(10)

    result = await db.execute(query)
    correlations = result.scalars().all()

    # Format top causes
    top_causes = []
    for corr in correlations:
        # Generate interpretation
        direction = "increases" if corr.correlation_coefficient > 0 else "decreases"
        lag_text = f"{corr.lag_days} days earlier" if corr.lag_days > 0 else "on the same day"

        interpretation = (
            f"{corr.factor_x.replace('_', ' ').title()} {lag_text} "
            f"{direction} {target.replace('_', ' ')}"
        )

        top_causes.append(TopCause(
            cause=corr.factor_x,
            lag_days=corr.lag_days,
            strength=float(corr.correlation_coefficient),
            p_value=float(corr.p_value),
            confidence=corr.confidence_level,
            interpretation=interpretation
        ))

    explanation = (
        f"Top factors that influence {target.replace('_', ' ')} based on "
        f"causal analysis of the last {lookback_days} days."
    )

    return TopCausesResponse(
        target_variable=target,
        top_causes=top_causes,
        explanation=explanation
    )


@router.post("/trigger")
async def trigger_ml_analysis(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger advanced ML analysis (PCMCI + STUMPY).

    This runs in the background and may take several minutes.
    """
    from app.tasks_ml import run_full_ml_analysis

    # Queue the ML analysis task
    task = run_full_ml_analysis.delay(str(current_user.id))

    return {
        "status": "ml_analysis_queued",
        "task_id": task.id,
        "message": "Advanced ML analysis started. Check back in a few minutes."
    }
