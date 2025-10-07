"""
Specialized Scientific Plots
============================

Domain-specific visualization tools for advanced analysis.
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

from ..charts.professional_charts import ProfessionalChart
from ..rendering.vizlyengine import ColorHDR, Font


def parallel_coordinates(data: np.ndarray, labels: Optional[List[str]] = None,
                        class_column: Optional[np.ndarray] = None,
                        title: str = "Parallel Coordinates Plot", **kwargs) -> ProfessionalChart:
    """Create parallel coordinates plot for multivariate data analysis."""
    from ..charts.professional_charts import ProfessionalLineChart as LineChart

    chart = LineChart(**kwargs)

    n_features = data.shape[1]
    n_samples = data.shape[0]

    # Normalize data to [0, 1] range for each feature
    normalized_data = np.zeros_like(data)
    for i in range(n_features):
        col_min, col_max = data[:, i].min(), data[:, i].max()
        if col_max > col_min:
            normalized_data[:, i] = (data[:, i] - col_min) / (col_max - col_min)
        else:
            normalized_data[:, i] = 0.5  # All values are the same

    # Generate colors for different classes
    if class_column is not None:
        unique_classes = np.unique(class_column)
        colors = [ColorHDR.from_hex(color) for color in
                 ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C']]
        color_map = {cls: colors[i % len(colors)] for i, cls in enumerate(unique_classes)}
    else:
        default_color = ColorHDR.from_hex('#3498DB')

    # Plot each sample as a line
    x_positions = np.arange(n_features)
    for i in range(n_samples):
        color = (color_map[class_column[i]] if class_column is not None
                else default_color)
        alpha = 0.7 if class_column is not None else 0.5

        # Create semi-transparent lines
        chart.plot(x_positions, normalized_data[i, :],
                  color=ColorHDR(color.r, color.g, color.b, alpha),
                  line_width=1)

    chart.set_title(title)
    chart.set_labels("Features", "Normalized Values")

    # Set custom x-tick labels if provided
    if labels:
        # This would require tick customization in the base chart
        pass

    return chart


def andrews_curves(data: np.ndarray, class_column: np.ndarray = None,
                   title: str = "Andrews Curves", **kwargs) -> ProfessionalChart:
    """Create Andrews curves for multivariate data visualization."""
    from ..charts.professional_charts import ProfessionalLineChart as LineChart

    chart = LineChart(**kwargs)

    n_features = data.shape[1]
    n_samples = data.shape[0]

    # Create parameter range
    t = np.linspace(-np.pi, np.pi, 200)

    # Generate colors for different classes
    if class_column is not None:
        unique_classes = np.unique(class_column)
        colors = [ColorHDR.from_hex(color) for color in
                 ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C']]
        color_map = {cls: colors[i % len(colors)] for i, cls in enumerate(unique_classes)}
    else:
        default_color = ColorHDR.from_hex('#3498DB')

    # Plot Andrews curves for each sample
    for i in range(min(n_samples, 100)):  # Limit for performance
        # Calculate Andrews curve
        curve = data[i, 0] / np.sqrt(2) * np.ones_like(t)

        for j in range(1, n_features):
            if j % 2 == 1:  # Odd indices use sin
                k = (j + 1) // 2
                curve += data[i, j] * np.sin(k * t)
            else:  # Even indices use cos
                k = j // 2
                curve += data[i, j] * np.cos(k * t)

        color = (color_map[class_column[i]] if class_column is not None
                else default_color)
        alpha = 0.7 if class_column is not None else 0.5

        chart.plot(t, curve,
                  color=ColorHDR(color.r, color.g, color.b, alpha),
                  line_width=1)

    chart.set_title(title)
    chart.set_labels("t", "f(t)")
    return chart


def radar_chart(data: np.ndarray, categories: List[str],
                labels: Optional[List[str]] = None,
                title: str = "Radar Chart", **kwargs) -> ProfessionalChart:
    """Create radar/spider chart for multivariate comparison."""
    from ..charts.professional_charts import ProfessionalLineChart as LineChart

    chart = LineChart(**kwargs)

    n_vars = len(categories)
    n_samples = data.shape[0] if data.ndim > 1 else 1

    # Calculate angles for each variable
    angles = np.linspace(0, 2 * np.pi, n_vars, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    # Colors for different samples
    colors = [ColorHDR.from_hex(color) for color in
             ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C']]

    # Plot each sample
    if data.ndim == 1:
        data = data.reshape(1, -1)

    for i, sample in enumerate(data):
        values = sample.tolist()
        values += values[:1]  # Complete the circle

        color = colors[i % len(colors)]
        label = labels[i] if labels and i < len(labels) else f'Sample {i+1}'

        # Plot the radar lines (simplified - would need proper polar coordinate transformation)
        x_coords = [val * np.cos(angle) for val, angle in zip(values, angles)]
        y_coords = [val * np.sin(angle) for val, angle in zip(values, angles)]

        chart.plot(x_coords, y_coords, color=color, line_width=2, label=label)

        # Fill area (simplified)
        chart.plot(x_coords, y_coords, color=ColorHDR(color.r, color.g, color.b, 0.25),
                  line_width=0)

    chart.set_title(title)
    return chart


def sankey_diagram(flows: List[Tuple[str, str, float]], title: str = "Sankey Diagram", **kwargs) -> ProfessionalChart:
    """Create simplified Sankey diagram for flow visualization."""
    from ..charts.professional_charts import ProfessionalBarChart as BarChart

    # This is a simplified representation - full Sankey requires complex path calculations
    chart = BarChart(**kwargs)

    # Extract source and target totals
    sources = {}
    targets = {}

    for source, target, value in flows:
        sources[source] = sources.get(source, 0) + value
        targets[target] = targets.get(target, 0) + value

    # Create stacked bar representation
    all_nodes = list(set(sources.keys()) | set(targets.keys()))
    values = [sources.get(node, 0) + targets.get(node, 0) for node in all_nodes]

    colors = [ColorHDR.from_hex(color) for color in
             ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C']]

    for i, (node, value) in enumerate(zip(all_nodes, values)):
        chart.bar([node], [value], color=colors[i % len(colors)])

    chart.set_title(title + " (Simplified)")
    chart.set_labels("Nodes", "Total Flow")
    return chart


def treemap_chart(values: List[float], labels: List[str],
                 title: str = "Treemap Chart", **kwargs) -> ProfessionalChart:
    """Create simplified treemap visualization."""
    from ..charts.professional_charts import ProfessionalBarChart as BarChart

    # Simplified treemap as horizontal bar chart
    chart = BarChart(**kwargs)

    # Sort by value for better visualization
    sorted_items = sorted(zip(values, labels), reverse=True)
    sorted_values, sorted_labels = zip(*sorted_items)

    colors = [ColorHDR.from_hex(color) for color in
             ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C']]

    for i, (value, label) in enumerate(zip(sorted_values, sorted_labels)):
        chart.bar([label], [value], color=colors[i % len(colors)])

    chart.set_title(title + " (Bar Representation)")
    chart.set_labels("Categories", "Values")
    return chart