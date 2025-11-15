"""
STUMPY Pattern Detection Service

Uses matrix profile (STUMPY library) for discovering recurring patterns
and anomalies in glucose time-series data.
"""
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import stumpy
    STUMPY_AVAILABLE = True
except ImportError:
    STUMPY_AVAILABLE = False
    print("⚠️  STUMPY not available. Pattern detection will use fallback method.")


class StumpyPatternDetector:
    """
    Pattern detector using STUMPY's matrix profile algorithm.

    Finds:
    - Recurring patterns (motifs)
    - Anomalies (discords)
    - Similar day patterns
    """

    def __init__(self, window_size_hours: int = 24):
        """
        Initialize STUMPY pattern detector.

        Args:
            window_size_hours: Size of pattern window in hours (default 24h = 1 day)
        """
        self.window_size_hours = window_size_hours
        self.use_fallback = not STUMPY_AVAILABLE

    def detect_recurring_patterns(
        self,
        glucose_series: pd.Series,
        reading_interval_minutes: int = 5,
        top_k: int = 3
    ) -> Dict[str, any]:
        """
        Detect recurring patterns (motifs) in glucose data.

        Args:
            glucose_series: Time-series of glucose values (DatetimeIndex)
            reading_interval_minutes: Time between readings (for CGM, typically 5 min)
            top_k: Number of top patterns to return

        Returns:
            Dictionary with detected patterns
        """
        if len(glucose_series) < 100:
            return {
                "error": "Insufficient data for pattern detection",
                "data_points": len(glucose_series)
            }

        # Calculate window size in data points
        points_per_hour = 60 // reading_interval_minutes
        window_size = self.window_size_hours * points_per_hour

        if len(glucose_series) < 2 * window_size:
            return {
                "error": f"Need at least {2 * window_size} data points",
                "data_points": len(glucose_series),
                "window_size": window_size
            }

        if self.use_fallback or not STUMPY_AVAILABLE:
            return self._fallback_pattern_detection(glucose_series, window_size, top_k)

        try:
            # Prepare data
            values = glucose_series.values.astype(float)

            # Remove NaN
            if np.isnan(values).any():
                # Interpolate missing values
                values = pd.Series(values).interpolate(method='linear').values

            # Compute matrix profile
            mp = stumpy.stump(values, m=window_size)

            # Find motifs (recurring patterns)
            motifs = stumpy.motifs(
                values,
                mp[:, 0],  # Matrix profile values
                min_neighbors=1,
                max_distance=np.percentile(mp[:, 0], 10)  # Top 10% similar
            )

            patterns = []
            for k in range(min(top_k, len(motifs[0]))):
                if k >= len(motifs[0]):
                    break

                motif_idx = motifs[0][k]
                neighbor_indices = motifs[1][k]

                # Get timestamps
                pattern_times = [
                    glucose_series.index[idx] for idx in [motif_idx] + list(neighbor_indices)
                ]

                # Get pattern values
                pattern_values = values[motif_idx:motif_idx + window_size]

                patterns.append({
                    "pattern_id": k + 1,
                    "occurrences": len(pattern_times),
                    "example_dates": [t.date().isoformat() for t in pattern_times[:5]],
                    "example_times": [t.time().isoformat() for t in pattern_times[:5]],
                    "pattern_summary": {
                        "mean": float(np.mean(pattern_values)),
                        "std": float(np.std(pattern_values)),
                        "min": float(np.min(pattern_values)),
                        "max": float(np.max(pattern_values)),
                        "duration_hours": self.window_size_hours
                    },
                    "pattern_values": pattern_values.tolist()
                })

            return {
                "method": "STUMPY Matrix Profile",
                "window_size_hours": self.window_size_hours,
                "patterns_found": len(patterns),
                "patterns": patterns,
                "total_data_points": len(glucose_series)
            }

        except Exception as e:
            print(f"⚠️  STUMPY pattern detection failed: {str(e)}. Using fallback.")
            return self._fallback_pattern_detection(glucose_series, window_size, top_k)

    def detect_anomalies(
        self,
        glucose_series: pd.Series,
        reading_interval_minutes: int = 5,
        top_k: int = 5
    ) -> Dict[str, any]:
        """
        Detect anomalous patterns (discords) in glucose data.

        Args:
            glucose_series: Time-series of glucose values
            reading_interval_minutes: Time between readings
            top_k: Number of top anomalies to return

        Returns:
            Dictionary with detected anomalies
        """
        if len(glucose_series) < 100:
            return {
                "error": "Insufficient data for anomaly detection",
                "data_points": len(glucose_series)
            }

        points_per_hour = 60 // reading_interval_minutes
        window_size = self.window_size_hours * points_per_hour

        if self.use_fallback or not STUMPY_AVAILABLE:
            return self._fallback_anomaly_detection(glucose_series, window_size, top_k)

        try:
            values = glucose_series.values.astype(float)

            # Interpolate NaN
            if np.isnan(values).any():
                values = pd.Series(values).interpolate(method='linear').values

            # Compute matrix profile
            mp = stumpy.stump(values, m=window_size)

            # Find discords (anomalous patterns)
            # Highest matrix profile values = most unusual patterns
            discord_indices = np.argsort(mp[:, 0])[-top_k:][::-1]

            anomalies = []
            for rank, idx in enumerate(discord_indices):
                timestamp = glucose_series.index[idx]
                anomaly_values = values[idx:idx + window_size]
                distance = mp[idx, 0]

                anomalies.append({
                    "anomaly_id": rank + 1,
                    "timestamp": timestamp.isoformat(),
                    "date": timestamp.date().isoformat(),
                    "time": timestamp.time().isoformat(),
                    "distance": float(distance),
                    "severity": "high" if distance > np.percentile(mp[:, 0], 95) else "medium",
                    "pattern_summary": {
                        "mean": float(np.mean(anomaly_values)),
                        "std": float(np.std(anomaly_values)),
                        "min": float(np.min(anomaly_values)),
                        "max": float(np.max(anomaly_values)),
                        "duration_hours": self.window_size_hours
                    },
                    "values": anomaly_values.tolist()
                })

            return {
                "method": "STUMPY Discord Discovery",
                "window_size_hours": self.window_size_hours,
                "anomalies_found": len(anomalies),
                "anomalies": anomalies,
                "total_data_points": len(glucose_series)
            }

        except Exception as e:
            print(f"⚠️  STUMPY anomaly detection failed: {str(e)}. Using fallback.")
            return self._fallback_anomaly_detection(glucose_series, window_size, top_k)

    def _fallback_pattern_detection(
        self,
        glucose_series: pd.Series,
        window_size: int,
        top_k: int
    ) -> Dict[str, any]:
        """
        Fallback pattern detection using simple correlation.

        Args:
            glucose_series: Time-series data
            window_size: Window size in data points
            top_k: Number of patterns to find

        Returns:
            Pattern detection results
        """
        values = glucose_series.values

        # Find similar windows using correlation
        patterns = []

        # Compare each window with all others
        num_windows = len(values) - window_size + 1
        correlations = np.zeros((num_windows, num_windows))

        for i in range(num_windows):
            window_i = values[i:i + window_size]
            for j in range(i + 1, num_windows):
                window_j = values[j:j + window_size]
                corr = np.corrcoef(window_i, window_j)[0, 1]
                correlations[i, j] = corr
                correlations[j, i] = corr

        # Find windows with high correlation (similar patterns)
        threshold = 0.7
        for i in range(num_windows):
            similar_indices = np.where(correlations[i] > threshold)[0]
            if len(similar_indices) >= 2:  # At least 2 occurrences
                pattern_times = [glucose_series.index[idx] for idx in [i] + list(similar_indices[:4])]
                pattern_values = values[i:i + window_size]

                patterns.append({
                    "pattern_id": len(patterns) + 1,
                    "occurrences": len(similar_indices) + 1,
                    "example_dates": [t.date().isoformat() for t in pattern_times],
                    "pattern_summary": {
                        "mean": float(np.mean(pattern_values)),
                        "std": float(np.std(pattern_values)),
                        "min": float(np.min(pattern_values)),
                        "max": float(np.max(pattern_values))
                    }
                })

                if len(patterns) >= top_k:
                    break

        return {
            "method": "Fallback Correlation",
            "patterns_found": len(patterns),
            "patterns": patterns
        }

    def _fallback_anomaly_detection(
        self,
        glucose_series: pd.Series,
        window_size: int,
        top_k: int
    ) -> Dict[str, any]:
        """
        Fallback anomaly detection using statistical methods.

        Args:
            glucose_series: Time-series data
            window_size: Window size
            top_k: Number of anomalies

        Returns:
            Anomaly detection results
        """
        values = glucose_series.values

        # Calculate moving statistics
        moving_mean = pd.Series(values).rolling(window_size).mean()
        moving_std = pd.Series(values).rolling(window_size).std()

        # Z-score for anomaly detection
        z_scores = np.abs((values - moving_mean) / (moving_std + 1e-6))

        # Find top anomalies
        anomaly_indices = np.argsort(z_scores)[-top_k:][::-1]

        anomalies = []
        for rank, idx in enumerate(anomaly_indices):
            if np.isnan(z_scores[idx]):
                continue

            timestamp = glucose_series.index[idx]
            anomalies.append({
                "anomaly_id": rank + 1,
                "timestamp": timestamp.isoformat(),
                "value": float(values[idx]),
                "z_score": float(z_scores[idx]),
                "severity": "high" if z_scores[idx] > 3 else "medium"
            })

        return {
            "method": "Fallback Z-Score",
            "anomalies_found": len(anomalies),
            "anomalies": anomalies
        }

    def find_similar_days(
        self,
        glucose_series: pd.Series,
        target_date: datetime,
        reading_interval_minutes: int = 5,
        top_k: int = 5
    ) -> Dict[str, any]:
        """
        Find days with similar glucose patterns to a target date.

        Args:
            glucose_series: Time-series of glucose values
            target_date: Date to find similar days for
            reading_interval_minutes: Reading interval
            top_k: Number of similar days to return

        Returns:
            Similar days with similarity scores
        """
        # Extract 24h window for target date
        target_start = pd.Timestamp(target_date).normalize()
        target_end = target_start + timedelta(days=1)

        target_data = glucose_series[target_start:target_end]

        if len(target_data) < 100:
            return {
                "error": "Insufficient data for target date",
                "target_date": target_date.date().isoformat()
            }

        # Group by date and find similar days
        similar_days = []

        for date in glucose_series.index.normalize().unique():
            if date == target_start:
                continue

            day_end = date + timedelta(days=1)
            day_data = glucose_series[date:day_end]

            if len(day_data) < 100:
                continue

            # Calculate similarity (correlation)
            min_len = min(len(target_data), len(day_data))
            corr = np.corrcoef(
                target_data.values[:min_len],
                day_data.values[:min_len]
            )[0, 1]

            if not np.isnan(corr):
                similar_days.append({
                    "date": date.date().isoformat(),
                    "similarity_score": float(corr),
                    "mean_glucose": float(day_data.mean()),
                    "std_glucose": float(day_data.std())
                })

        # Sort by similarity
        similar_days.sort(key=lambda x: x['similarity_score'], reverse=True)

        return {
            "target_date": target_date.date().isoformat(),
            "similar_days_found": len(similar_days),
            "top_similar_days": similar_days[:top_k]
        }
