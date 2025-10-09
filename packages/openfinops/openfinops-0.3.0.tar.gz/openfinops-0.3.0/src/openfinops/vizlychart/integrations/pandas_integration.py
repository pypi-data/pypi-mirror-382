"""
Pandas Integration for OpenFinOps
==================================

Seamless integration with pandas DataFrames and Series, providing
df.plot() functionality and automatic data handling.
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



from typing import Optional, Union, List, Dict, Any, Tuple
import numpy as np

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from ..charts.professional_charts import ProfessionalLineChart as LineChart, ProfessionalScatterChart as ScatterChart, ProfessionalBarChart as BarChart
from ..charts.advanced_charts import ContourChart, HeatmapChart, BoxPlot, ViolinPlot
from ..rendering.vizlyengine import ColorHDR


# Define VizlyAccessor class for import compatibility
class VizlyAccessor:
    """Pandas accessor for OpenFinOps plotting (stub for import compatibility)."""

    def __init__(self, pandas_obj=None):
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas is required for DataFrame plotting. Install with: pip install pandas")
        self._obj = pandas_obj
        self._plotter = DataFramePlotter(pandas_obj) if pandas_obj is not None else None

    def line(self, **kwargs):
        if self._plotter is None:
            raise RuntimeError("No DataFrame attached to accessor")
        return self._plotter.line(**kwargs)

    def scatter(self, **kwargs):
        if self._plotter is None:
            raise RuntimeError("No DataFrame attached to accessor")
        return self._plotter.scatter(**kwargs)

    def bar(self, **kwargs):
        if self._plotter is None:
            raise RuntimeError("No DataFrame attached to accessor")
        return self._plotter.bar(**kwargs)


class DataFramePlotter:
    """High-level plotting interface for pandas DataFrames."""

    def __init__(self, data: 'pd.DataFrame'):
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas is required for DataFrame plotting. Install with: pip install pandas")

        self.data = data

    def line(self, x: Optional[str] = None, y: Optional[Union[str, List[str]]] = None,
             title: str = "", **kwargs) -> LineChart:
        """Create line plot from DataFrame columns."""
        chart = LineChart(**kwargs)

        if x is None:
            x_data = self.data.index
            x_label = self.data.index.name or "Index"
        else:
            x_data = self.data[x].values
            x_label = x

        if y is None:
            # Plot all numeric columns
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            y_cols = [col for col in numeric_cols if col != x]
        elif isinstance(y, str):
            y_cols = [y]
        else:
            y_cols = y

        colors = chart.default_colors
        for i, col in enumerate(y_cols):
            y_data = self.data[col].values
            color = colors[i % len(colors)]
            chart.plot(x_data, y_data, color=color, label=col)

        chart.set_title(title or f"Line Plot of {', '.join(y_cols)}")
        chart.set_labels(x_label, "Value")
        return chart

    def scatter(self, x: str, y: str, c: Optional[str] = None,
                size: Optional[str] = None, title: str = "", **kwargs) -> ScatterChart:
        """Create scatter plot from DataFrame columns."""
        chart = ScatterChart(**kwargs)

        x_data = self.data[x].values
        y_data = self.data[y].values

        # Color mapping
        if c is not None:
            if self.data[c].dtype in ['object', 'category']:
                # Categorical coloring
                categories = self.data[c].unique()
                colors = chart.default_colors
                for i, cat in enumerate(categories):
                    mask = self.data[c] == cat
                    chart.scatter(x_data[mask], y_data[mask],
                                c=colors[i % len(colors)], label=str(cat))
            else:
                # Continuous coloring (simplified)
                chart.scatter(x_data, y_data, c=chart.default_colors[0])
        else:
            chart.scatter(x_data, y_data, c=chart.default_colors[0])

        chart.set_title(title or f"{y} vs {x}")
        chart.set_labels(x, y)
        return chart

    def bar(self, x: Optional[str] = None, y: Optional[str] = None,
            title: str = "", **kwargs) -> BarChart:
        """Create bar plot from DataFrame."""
        chart = BarChart(**kwargs)

        if x is None and y is None:
            # Use index and first numeric column
            x_data = self.data.index.astype(str)
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            y_data = self.data[numeric_cols[0]].values
            y_label = numeric_cols[0]
        elif x is not None and y is not None:
            x_data = self.data[x].astype(str).values
            y_data = self.data[y].values
            y_label = y
        else:
            raise ValueError("Both x and y must be specified for bar plots")

        chart.bar(x_data, y_data, color=chart.default_colors[0])
        chart.set_title(title or f"Bar Plot of {y_label}")
        chart.set_labels(x or "Categories", y_label)
        return chart

    def hist(self, column: Optional[str] = None, bins: int = 30,
             title: str = "", **kwargs) -> BarChart:
        """Create histogram from DataFrame column."""
        chart = BarChart(**kwargs)

        if column is None:
            # Use first numeric column
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise ValueError("No numeric columns found for histogram")
            column = numeric_cols[0]

        data = self.data[column].dropna().values
        counts, bin_edges = np.histogram(data, bins=bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        chart.bar([f"{edge:.2f}" for edge in bin_centers], counts,
                 color=chart.default_colors[0])
        chart.set_title(title or f"Histogram of {column}")
        chart.set_labels(column, "Frequency")
        return chart

    def box(self, columns: Optional[List[str]] = None, title: str = "", **kwargs) -> BoxPlot:
        """Create box plot from DataFrame columns."""
        chart = BoxPlot(**kwargs)

        if columns is None:
            columns = self.data.select_dtypes(include=[np.number]).columns.tolist()

        data_lists = [self.data[col].dropna().values for col in columns]
        chart.box(data_lists, labels=columns)

        chart.set_title(title or f"Box Plot of {', '.join(columns)}")
        return chart


def register_pandas_accessor():
    """Register the .vizly accessor for pandas DataFrames."""
    if not PANDAS_AVAILABLE:
        return

    @pd.api.extensions.register_dataframe_accessor("vizly")
    class VizlyAccessor:
        """Pandas accessor for OpenFinOps plotting."""

        def __init__(self, pandas_obj):
            self._obj = pandas_obj
            self._plotter = DataFramePlotter(pandas_obj)

        def line(self, **kwargs):
            """Create line plot."""
            return self._plotter.line(**kwargs)

        def scatter(self, **kwargs):
            """Create scatter plot."""
            return self._plotter.scatter(**kwargs)

        def bar(self, **kwargs):
            """Create bar plot."""
            return self._plotter.bar(**kwargs)

        def hist(self, **kwargs):
            """Create histogram."""
            return self._plotter.hist(**kwargs)

        def box(self, **kwargs):
            """Create box plot."""
            return self._plotter.box(**kwargs)


def plot_dataframe(df: 'pd.DataFrame', kind: str = 'line', **kwargs):
    """Plot DataFrame with specified chart type."""
    if not PANDAS_AVAILABLE:
        raise ImportError("Pandas is required. Install with: pip install pandas")

    plotter = DataFramePlotter(df)

    if kind == 'line':
        return plotter.line(**kwargs)
    elif kind == 'scatter':
        return plotter.scatter(**kwargs)
    elif kind == 'bar':
        return plotter.bar(**kwargs)
    elif kind == 'hist':
        return plotter.hist(**kwargs)
    elif kind == 'box':
        return plotter.box(**kwargs)
    else:
        raise ValueError(f"Unsupported plot kind: {kind}")


# Compatibility alias
DataFrame = DataFramePlotter if PANDAS_AVAILABLE else None