"""
Statistical Visualization Tools
===============================

Advanced statistical plots and analysis visualizations.
"""

# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from __future__ import annotations

from typing import List, Optional, Union, Tuple, Dict, Any
import math

import numpy as np

try:
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    stats = None

from ..charts.professional_charts import ProfessionalChart
from ..charts.advanced_charts import HeatmapChart
from ..rendering.vizlyengine import ColorHDR, Font, MarkerStyle


class StatisticalPlots(ProfessionalChart):
    """Collection of statistical visualization methods."""

    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)


def qqplot(data: np.ndarray, distribution: str = "normal",
           title: str = "Q-Q Plot", **kwargs) -> ProfessionalChart:
    """Create a quantile-quantile plot."""
    from ..charts.professional_charts import ProfessionalLineChart as LineChart

    chart = LineChart(**kwargs)
    data_sorted = np.sort(data)
    n = len(data)

    # Calculate theoretical quantiles
    if distribution == "normal":
        if SCIPY_AVAILABLE:
            theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, n))
        else:
            # Simple normal approximation
            p_values = np.linspace(0.01, 0.99, n)
            theoretical_quantiles = np.sqrt(2) * np.array([
                math.erf(p - 0.5) * 2.5 for p in p_values
            ])
    elif distribution == "uniform":
        theoretical_quantiles = np.linspace(data_sorted.min(), data_sorted.max(), n)
    else:
        raise ValueError(f"Unsupported distribution: {distribution}")

    # Plot Q-Q line
    chart.plot(theoretical_quantiles, data_sorted, color=ColorHDR.from_hex('#2E86C1'),
               marker='o', line_width=0, label='Data points')

    # Add reference line
    min_val = min(theoretical_quantiles.min(), data_sorted.min())
    max_val = max(theoretical_quantiles.max(), data_sorted.max())
    chart.plot([min_val, max_val], [min_val, max_val],
               color=ColorHDR.from_hex('#E74C3C'), line_width=2, label='Perfect fit')

    chart.set_title(title)
    chart.set_labels(f"Theoretical {distribution.title()} Quantiles", "Sample Quantiles")
    return chart


def residual_plot(y_true: np.ndarray, y_pred: np.ndarray,
                  title: str = "Residual Plot", **kwargs) -> ProfessionalChart:
    """Create a residual plot for regression analysis."""
    from ..charts.professional_charts import ProfessionalLineChart as LineChart

    chart = LineChart(**kwargs)
    residuals = y_true - y_pred

    # Plot residuals as scatter points using plot with no line
    chart.plot(y_pred, residuals, color=ColorHDR.from_hex('#3498DB'), line_width=0,
               marker=MarkerStyle.CIRCLE, marker_size=6.0, alpha=0.7)

    # Add horizontal line at y=0
    x_min, x_max = y_pred.min(), y_pred.max()
    chart.plot([x_min, x_max], [0, 0], color=ColorHDR.from_hex('#E74C3C'), line_width=2)

    chart.set_title(title)
    chart.set_labels("Predicted Values", "Residuals")
    return chart


def correlation_matrix(data: np.ndarray, labels: Optional[List[str]] = None,
                       title: str = "Correlation Matrix", **kwargs) -> HeatmapChart:
    """Create correlation matrix heatmap with enhanced visualization."""
    from ..charts.advanced_charts import HeatmapChart

    # Calculate correlation matrix
    corr_matrix = np.corrcoef(data.T)

    # Create chart with proper dimensions for correlation visualization
    chart_kwargs = {'width': 800, 'height': 600}
    chart_kwargs.update(kwargs)

    chart = HeatmapChart(**chart_kwargs)

    # Use coolwarm colormap which is perfect for correlations (-1 to 1)
    chart.heatmap(corr_matrix, x_labels=labels, y_labels=labels,
                  colormap="coolwarm", show_values=True)

    chart.set_title(title)
    chart.colorbar = True  # Enable colorbar for correlation scale

    return chart


def pca_plot(data: np.ndarray, n_components: int = 2, labels: Optional[np.ndarray] = None,
             title: str = "PCA Plot", **kwargs) -> ProfessionalChart:
    """Create PCA visualization."""
    # Simple PCA implementation (or use scipy if available)
    if SCIPY_AVAILABLE:
        from scipy.linalg import eigh

        # Center the data
        data_centered = data - np.mean(data, axis=0)

        # Calculate covariance matrix
        cov_matrix = np.cov(data_centered.T)

        # Get eigenvalues and eigenvectors
        eigenvalues, eigenvectors = eigh(cov_matrix)

        # Sort by eigenvalues (descending)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Transform data
        pca_data = data_centered @ eigenvectors[:, :n_components]
    else:
        # Fallback: simple projection (not true PCA)
        pca_data = data[:, :n_components]

    if n_components == 2:
        from ..charts.professional_charts import ProfessionalScatterChart as ScatterChart
        chart = ScatterChart(**kwargs)

        if labels is not None:
            unique_labels = np.unique(labels)
            colors = chart.default_colors

            for i, label in enumerate(unique_labels):
                mask = labels == label
                chart.scatter(pca_data[mask, 0], pca_data[mask, 1],
                             c=colors[i % len(colors)], label=str(label))
        else:
            chart.scatter(pca_data[:, 0], pca_data[:, 1], c=chart.default_colors[0])

        chart.set_title(title)
        chart.set_labels("First Principal Component", "Second Principal Component")
        return chart
    else:
        raise ValueError("Only 2D PCA plots are currently supported")


def dendrogram(linkage_matrix: np.ndarray, labels: Optional[List[str]] = None,
               title: str = "Dendrogram", **kwargs) -> ProfessionalChart:
    """Create dendrogram for hierarchical clustering."""
    from ..charts.professional_charts import ProfessionalLineChart as LineChart

    chart = LineChart(**kwargs)

    # Simplified dendrogram drawing
    # This is a basic implementation - full dendrogram requires complex tree traversal
    n_samples = linkage_matrix.shape[0] + 1

    # Draw simplified tree structure
    for i, (cluster1, cluster2, distance, size) in enumerate(linkage_matrix):
        x1 = cluster1 if cluster1 < n_samples else cluster1 - n_samples + len(linkage_matrix)
        x2 = cluster2 if cluster2 < n_samples else cluster2 - n_samples + len(linkage_matrix)

        # Draw connecting lines
        chart.plot([x1, x1], [0, distance], color=ColorHDR.from_hex('#2C3E50'), line_width=1)
        chart.plot([x2, x2], [0, distance], color=ColorHDR.from_hex('#2C3E50'), line_width=1)
        chart.plot([x1, x2], [distance, distance], color=ColorHDR.from_hex('#2C3E50'), line_width=1)

    chart.set_title(title)
    chart.set_labels("Samples", "Distance")
    return chart