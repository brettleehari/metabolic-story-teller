"""
PCMCI Causal Discovery Service

Uses the Tigramite library for causal discovery in time-series data.
Discovers causal relationships like "sleep yesterday -> glucose today".
"""
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime

try:
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests.parcorr import ParCorr
    TIGRAMITE_AVAILABLE = True
except ImportError:
    TIGRAMITE_AVAILABLE = False
    print("⚠️  Tigramite not available. PCMCI analysis will use fallback correlation.")


class PCMCIAnalyzer:
    """
    PCMCI (Peter-Clark Momentary Conditional Independence) analyzer.

    Discovers time-lagged causal relationships in health data.
    """

    def __init__(self, tau_max: int = 7, alpha_level: float = 0.05):
        """
        Initialize PCMCI analyzer.

        Args:
            tau_max: Maximum time lag to consider (in days)
            alpha_level: Significance level for independence tests
        """
        self.tau_max = tau_max
        self.alpha_level = alpha_level
        self.use_fallback = not TIGRAMITE_AVAILABLE

    def analyze_causality(
        self,
        data: pd.DataFrame,
        variables: List[str],
        min_data_points: int = 30
    ) -> Dict[str, any]:
        """
        Perform PCMCI causal discovery analysis.

        Args:
            data: DataFrame with time-series data (index should be date)
            variables: List of variable names to analyze
            min_data_points: Minimum data points required

        Returns:
            Dictionary with causal relationships and statistics
        """
        if len(data) < min_data_points:
            return {
                "error": "Insufficient data points",
                "data_points": len(data),
                "required": min_data_points
            }

        # Ensure data is sorted by date
        data = data.sort_index()

        # Select and prepare variables
        var_data = data[variables].copy()

        # Remove NaN values
        var_data = var_data.dropna()

        if len(var_data) < min_data_points:
            return {
                "error": "Insufficient clean data points after removing NaN",
                "data_points": len(var_data),
                "required": min_data_points
            }

        if self.use_fallback or not TIGRAMITE_AVAILABLE:
            return self._fallback_correlation_analysis(var_data, variables)

        try:
            # Prepare data for PCMCI
            dataframe = pp.DataFrame(
                var_data.values,
                datatime=np.arange(len(var_data)),
                var_names=variables
            )

            # Initialize PCMCI with ParCorr independence test
            parcorr = ParCorr(significance='analytic')
            pcmci = PCMCI(
                dataframe=dataframe,
                cond_ind_test=parcorr,
                verbosity=0
            )

            # Run PCMCI algorithm
            results = pcmci.run_pcmci(tau_max=self.tau_max, pc_alpha=self.alpha_level)

            # Extract causal links
            causal_links = self._extract_causal_links(results, variables)

            # Calculate strengths
            val_matrix = results['val_matrix']
            p_matrix = results['p_matrix']

            return {
                "method": "PCMCI",
                "causal_links": causal_links,
                "value_matrix": val_matrix.tolist(),
                "p_matrix": p_matrix.tolist(),
                "variables": variables,
                "tau_max": self.tau_max,
                "alpha_level": self.alpha_level,
                "sample_size": len(var_data)
            }

        except Exception as e:
            print(f"⚠️  PCMCI analysis failed: {str(e)}. Using fallback.")
            return self._fallback_correlation_analysis(var_data, variables)

    def _fallback_correlation_analysis(
        self,
        data: pd.DataFrame,
        variables: List[str]
    ) -> Dict[str, any]:
        """
        Fallback method using simple correlation with time lags.

        Args:
            data: DataFrame with variables
            variables: List of variable names

        Returns:
            Correlation analysis results
        """
        causal_links = []

        # Test each pair of variables with different lags
        for i, var_x in enumerate(variables):
            for j, var_y in enumerate(variables):
                if i == j:
                    continue

                # Test lags 0 to tau_max
                for lag in range(self.tau_max + 1):
                    if lag == 0 and i >= j:
                        # Avoid duplicate contemporaneous links
                        continue

                    # Shift var_x by lag
                    if lag > 0:
                        x_shifted = data[var_x].shift(lag)
                    else:
                        x_shifted = data[var_x]

                    # Calculate correlation
                    valid_mask = ~(x_shifted.isna() | data[var_y].isna())
                    if valid_mask.sum() < 10:
                        continue

                    corr = x_shifted[valid_mask].corr(data[var_y][valid_mask])

                    # Statistical significance (simple t-test)
                    n = valid_mask.sum()
                    if abs(corr) > 0.3 and n > 10:  # Threshold
                        t_stat = corr * np.sqrt(n - 2) / np.sqrt(1 - corr**2)
                        from scipy import stats
                        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))

                        if p_value < self.alpha_level:
                            causal_links.append({
                                "from": var_x,
                                "to": var_y,
                                "lag": lag,
                                "strength": float(corr),
                                "p_value": float(p_value),
                                "confidence": "high" if p_value < 0.01 else "medium",
                                "sample_size": int(n)
                            })

        return {
            "method": "Fallback Correlation",
            "causal_links": causal_links,
            "variables": variables,
            "tau_max": self.tau_max,
            "alpha_level": self.alpha_level,
            "sample_size": len(data)
        }

    def _extract_causal_links(
        self,
        results: Dict,
        variables: List[str]
    ) -> List[Dict]:
        """
        Extract causal links from PCMCI results.

        Args:
            results: PCMCI results dictionary
            variables: Variable names

        Returns:
            List of causal link dictionaries
        """
        causal_links = []
        val_matrix = results['val_matrix']
        p_matrix = results['p_matrix']

        # val_matrix shape: (N_vars, N_vars, tau_max+1)
        for j in range(len(variables)):  # Target variable
            for i in range(len(variables)):  # Source variable
                for tau in range(self.tau_max + 1):
                    val = val_matrix[i, j, tau]
                    p_val = p_matrix[i, j, tau]

                    # Only include significant links
                    if p_val < self.alpha_level and abs(val) > 0.1:
                        causal_links.append({
                            "from": variables[i],
                            "to": variables[j],
                            "lag": tau,
                            "strength": float(val),
                            "p_value": float(p_val),
                            "confidence": "high" if p_val < 0.01 else "medium",
                        })

        # Sort by absolute strength
        causal_links.sort(key=lambda x: abs(x['strength']), reverse=True)

        return causal_links

    def format_causal_graph(self, causal_links: List[Dict]) -> Dict:
        """
        Format causal links as a graph structure for visualization.

        Args:
            causal_links: List of causal link dictionaries

        Returns:
            Graph structure with nodes and edges
        """
        nodes = set()
        edges = []

        for link in causal_links:
            nodes.add(link['from'])
            nodes.add(link['to'])

            edge_label = f"lag={link['lag']}d" if link['lag'] > 0 else "same day"
            edges.append({
                "source": link['from'],
                "target": link['to'],
                "label": edge_label,
                "strength": link['strength'],
                "p_value": link['p_value'],
                "confidence": link['confidence']
            })

        return {
            "nodes": [{"id": node, "label": node} for node in nodes],
            "edges": edges
        }

    def get_top_causes(
        self,
        causal_links: List[Dict],
        target_variable: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Get top causes for a specific target variable.

        Args:
            causal_links: List of all causal links
            target_variable: Target variable name
            top_k: Number of top causes to return

        Returns:
            Top causal relationships affecting the target
        """
        target_links = [
            link for link in causal_links
            if link['to'] == target_variable
        ]

        # Sort by absolute strength
        target_links.sort(key=lambda x: abs(x['strength']), reverse=True)

        return target_links[:top_k]
