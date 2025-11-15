"""
Validate ML inference results from PCMCI and STUMPY.

This script checks if the expected causal relationships and patterns
were discovered by the ML pipeline, validating the synthetic data correlations.

Usage:
    python scripts/validate_inference.py --user-id <uuid>
"""
import argparse
from uuid import UUID
from typing import List, Dict, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.correlation import Correlation
from app.models.pattern import Pattern


# Default test user ID
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


# Expected causal relationships (from sample data correlations)
EXPECTED_RELATIONSHIPS = [
    {
        "from": "insulin",
        "to": "glucose",
        "expected_sign": "negative",  # Insulin lowers glucose
        "min_strength": 0.3,
        "description": "Insulin doses → Lower glucose"
    },
    {
        "from": "carbs",
        "to": "glucose",
        "expected_sign": "positive",  # Carbs raise glucose
        "min_strength": 0.3,
        "description": "Carbohydrate intake → Higher glucose"
    },
    {
        "from": "sleep",
        "to": "glucose",
        "expected_sign": "negative",  # Good sleep → better control
        "min_strength": 0.2,
        "description": "Sleep quality → Glucose control"
    },
    {
        "from": "exercise",
        "to": "glucose",
        "expected_sign": "negative",  # Exercise lowers glucose
        "min_strength": 0.2,
        "description": "Exercise → Lower glucose"
    },
    {
        "from": "weight",
        "to": "glucose",
        "expected_sign": "positive",  # Weight loss → better control (but stored as positive correlation with weight)
        "min_strength": 0.15,
        "description": "Body weight → Glucose levels"
    },
]


# Expected pattern types
EXPECTED_PATTERNS = [
    "morning_routine",
    "meal_pattern",
    "exercise_pattern",
    "weekend_pattern",
]


def validate_causal_discoveries(user_id: UUID, session: Session) -> Tuple[int, int, List[str]]:
    """
    Validate PCMCI causal discoveries against expected relationships.

    Returns:
        (found_count, expected_count, details)
    """
    print("\n" + "=" * 70)
    print("🔗 Validating PCMCI Causal Discoveries")
    print("=" * 70)

    correlations = session.query(Correlation).filter(
        Correlation.user_id == user_id
    ).all()

    if not correlations:
        print("   ❌ No causal relationships found in database!")
        print("   💡 Make sure to run: python scripts/run_ml_pipeline.py")
        return 0, len(EXPECTED_RELATIONSHIPS), []

    print(f"\n   Total relationships discovered: {len(correlations)}")
    print(f"   Expected key relationships: {len(EXPECTED_RELATIONSHIPS)}")

    found_count = 0
    details = []

    for expected in EXPECTED_RELATIONSHIPS:
        # Search for matching correlation
        matches = [
            c for c in correlations
            if (expected["from"].lower() in c.primary_metric.lower() or
                expected["from"].lower() in c.secondary_metric.lower()) and
               (expected["to"].lower() in c.primary_metric.lower() or
                expected["to"].lower() in c.secondary_metric.lower())
        ]

        if matches:
            match = matches[0]
            strength = abs(match.correlation_coefficient)
            sign = "negative" if match.correlation_coefficient < 0 else "positive"

            # Check if sign matches
            sign_match = sign == expected["expected_sign"]

            # Check if strength is significant
            strength_ok = strength >= expected["min_strength"]

            # Check p-value
            p_value_ok = match.p_value < 0.05

            if sign_match and strength_ok and p_value_ok:
                status = "✅"
                found_count += 1
                details.append(f"{status} {expected['description']}")
                details.append(f"   Found: {match.primary_metric} → {match.secondary_metric}")
                details.append(f"   Strength: {match.correlation_coefficient:.3f}, p={match.p_value:.4f}")
            else:
                status = "⚠️ "
                issues = []
                if not sign_match:
                    issues.append(f"wrong sign (expected {expected['expected_sign']}, got {sign})")
                if not strength_ok:
                    issues.append(f"weak (strength {strength:.3f} < {expected['min_strength']})")
                if not p_value_ok:
                    issues.append(f"not significant (p={match.p_value:.4f})")

                details.append(f"{status} {expected['description']}")
                details.append(f"   Found but: {', '.join(issues)}")
        else:
            details.append(f"❌ {expected['description']}")
            details.append(f"   Not discovered")

    # Print summary
    print(f"\n   Expected relationships found: {found_count}/{len(EXPECTED_RELATIONSHIPS)}")

    for detail in details:
        print(f"   {detail}")

    return found_count, len(EXPECTED_RELATIONSHIPS), details


def validate_pattern_discoveries(user_id: UUID, session: Session) -> Tuple[int, List[str]]:
    """
    Validate STUMPY pattern discoveries.

    Returns:
        (pattern_count, details)
    """
    print("\n" + "=" * 70)
    print("🔍 Validating STUMPY Pattern Discoveries")
    print("=" * 70)

    patterns = session.query(Pattern).filter(
        Pattern.user_id == user_id
    ).all()

    if not patterns:
        print("   ❌ No patterns found in database!")
        return 0, []

    print(f"\n   Total patterns discovered: {len(patterns)}")

    details = []

    # Group by pattern type
    pattern_types = {}
    for p in patterns:
        pattern_types[p.pattern_type] = pattern_types.get(p.pattern_type, 0) + 1

    print(f"\n   Pattern breakdown:")
    for ptype, count in sorted(pattern_types.items(), key=lambda x: x[1], reverse=True):
        print(f"      • {ptype}: {count}")

    # Check for recurring patterns with high occurrences
    high_occurrence_patterns = [p for p in patterns if p.occurrences >= 10]

    details.append(f"\n   High-frequency patterns (≥10 occurrences): {len(high_occurrence_patterns)}")

    for pattern in sorted(high_occurrence_patterns, key=lambda p: p.occurrences, reverse=True)[:5]:
        details.append(f"      • {pattern.pattern_type}: {pattern.occurrences} times (confidence: {pattern.confidence_score:.2f})")
        if pattern.description:
            details.append(f"        {pattern.description}")

    for detail in details:
        print(detail)

    return len(patterns), details


def validate_anomaly_discoveries(user_id: UUID, session: Session) -> Tuple[int, List[str]]:
    """
    Validate STUMPY anomaly discoveries.

    Returns:
        (anomaly_count, details)
    """
    print("\n" + "=" * 70)
    print("⚠️  Validating STUMPY Anomaly Discoveries")
    print("=" * 70)

    # Anomalies are stored as patterns with pattern_type containing "anomaly" or "discord"
    anomalies = session.query(Pattern).filter(
        Pattern.user_id == user_id,
        Pattern.pattern_type.contains("anomaly") | Pattern.pattern_type.contains("discord")
    ).all()

    if not anomalies:
        print("   ⚠️  No anomalies found in database")
        print("   💡 This may be normal if the synthetic data is very regular")
        return 0, []

    print(f"\n   Total anomalies discovered: {len(anomalies)}")

    details = []

    for anomaly in sorted(anomalies, key=lambda a: a.confidence_score, reverse=True)[:5]:
        details.append(f"      • {anomaly.pattern_type} (confidence: {anomaly.confidence_score:.2f})")
        if anomaly.description:
            details.append(f"        {anomaly.description}")

    for detail in details:
        print(detail)

    return len(anomalies), details


def generate_validation_report(
    user_id: UUID,
    causal_found: int,
    causal_expected: int,
    pattern_count: int,
    anomaly_count: int
) -> None:
    """Generate final validation report with pass/fail status."""
    print("\n" + "=" * 70)
    print("📊 Validation Report")
    print("=" * 70)

    total_score = 0
    max_score = 100

    # Causal discovery score (40 points)
    causal_score = (causal_found / causal_expected) * 40 if causal_expected > 0 else 0
    total_score += causal_score

    print(f"\n   1. PCMCI Causal Discovery: {causal_score:.1f}/40")
    print(f"      Found {causal_found}/{causal_expected} expected relationships")

    if causal_score >= 30:
        print(f"      ✅ Excellent causal discovery")
    elif causal_score >= 20:
        print(f"      ✅ Good causal discovery")
    elif causal_score >= 10:
        print(f"      ⚠️  Moderate causal discovery")
    else:
        print(f"      ❌ Poor causal discovery")

    # Pattern discovery score (40 points)
    if pattern_count >= 10:
        pattern_score = 40
    elif pattern_count >= 5:
        pattern_score = 30
    elif pattern_count >= 3:
        pattern_score = 20
    elif pattern_count >= 1:
        pattern_score = 10
    else:
        pattern_score = 0

    total_score += pattern_score

    print(f"\n   2. STUMPY Pattern Detection: {pattern_score:.1f}/40")
    print(f"      Found {pattern_count} recurring patterns")

    if pattern_score >= 30:
        print(f"      ✅ Excellent pattern detection")
    elif pattern_score >= 20:
        print(f"      ✅ Good pattern detection")
    elif pattern_score >= 10:
        print(f"      ⚠️  Moderate pattern detection")
    else:
        print(f"      ❌ Poor pattern detection")

    # Anomaly detection score (20 points)
    if anomaly_count >= 5:
        anomaly_score = 20
    elif anomaly_count >= 3:
        anomaly_score = 15
    elif anomaly_count >= 1:
        anomaly_score = 10
    else:
        anomaly_score = 5  # Not finding anomalies in synthetic data is somewhat expected

    total_score += anomaly_score

    print(f"\n   3. STUMPY Anomaly Detection: {anomaly_score:.1f}/20")
    print(f"      Found {anomaly_count} anomalous patterns")

    if anomaly_score >= 15:
        print(f"      ✅ Good anomaly detection")
    elif anomaly_score >= 10:
        print(f"      ✅ Moderate anomaly detection")
    else:
        print(f"      ⚠️  Few anomalies (expected for regular synthetic data)")

    # Final score
    print("\n" + "=" * 70)
    print(f"   🎯 Total Score: {total_score:.1f}/{max_score}")
    print("=" * 70)

    if total_score >= 80:
        print("\n   ✅ EXCELLENT - ML pipeline is working optimally!")
        print("      All major correlations and patterns discovered successfully.")
    elif total_score >= 60:
        print("\n   ✅ GOOD - ML pipeline is functioning well")
        print("      Most expected patterns discovered.")
    elif total_score >= 40:
        print("\n   ⚠️  MODERATE - ML pipeline needs improvement")
        print("      Some expected patterns missing. Check data quality and parameters.")
    else:
        print("\n   ❌ POOR - ML pipeline has issues")
        print("      Most expected patterns not found. Review implementation.")

    print("\n" + "=" * 70)
    print("💡 Recommendations:")
    print("=" * 70)

    if causal_score < 20:
        print("   • PCMCI: Increase data volume (more days) or adjust tau_max parameter")
        print("   • Check if correlations are strong enough in synthetic data")

    if pattern_score < 20:
        print("   • STUMPY: Adjust window size (try 24-hour or 12-hour windows)")
        print("   • Ensure sufficient glucose variability in data")

    if anomaly_count == 0:
        print("   • Anomalies: Add more irregular events to synthetic data (missed doses, stress)")

    print("\n   📚 For more details, check:")
    print("      • PCMCI documentation: https://github.com/jakobrunge/tigramite")
    print("      • STUMPY documentation: https://stumpy.readthedocs.io/")


def validate_ml_inference(user_id: UUID):
    """Main validation function."""
    print("=" * 70)
    print("🧪 GlucoLens ML Inference Validation")
    print("=" * 70)
    print(f"   User ID: {user_id}")
    print("=" * 70)

    sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_db_url)

    with Session(engine) as session:
        # Validate causal discoveries
        causal_found, causal_expected, causal_details = validate_causal_discoveries(user_id, session)

        # Validate pattern discoveries
        pattern_count, pattern_details = validate_pattern_discoveries(user_id, session)

        # Validate anomaly discoveries
        anomaly_count, anomaly_details = validate_anomaly_discoveries(user_id, session)

        # Generate report
        generate_validation_report(
            user_id,
            causal_found,
            causal_expected,
            pattern_count,
            anomaly_count
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate ML inference results"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=str(DEFAULT_USER_ID),
        help=f"User UUID (default: {DEFAULT_USER_ID})"
    )

    args = parser.parse_args()

    user_uuid = UUID(args.user_id)
    validate_ml_inference(user_uuid)
