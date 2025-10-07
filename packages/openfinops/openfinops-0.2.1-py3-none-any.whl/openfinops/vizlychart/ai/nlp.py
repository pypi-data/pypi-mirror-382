"""
AI-Driven Natural Language Visualization
=======================================

Natural language interface for creating charts from text descriptions.
Uses pattern matching and semantic analysis to interpret user intent.
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

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class ChartType(Enum):
    """Supported chart types for NLP generation."""
    LINE = "line"
    SCATTER = "scatter"
    BAR = "bar"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    SURFACE = "surface"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    TIMESERIES = "timeseries"


class AnalysisType(Enum):
    """Types of analysis that can be inferred."""
    TREND = "trend"
    COMPARISON = "comparison"
    DISTRIBUTION = "distribution"
    CORRELATION = "correlation"
    COMPOSITION = "composition"
    TEMPORAL = "temporal"


@dataclass
class ChartIntent:
    """Parsed intent from natural language."""
    chart_type: ChartType
    analysis_type: AnalysisType
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    title: Optional[str] = None
    style_hints: Dict[str, Any] = None
    aggregation: Optional[str] = None
    filters: Dict[str, Any] = None
    confidence: float = 0.0

    def __post_init__(self):
        if self.style_hints is None:
            self.style_hints = {}
        if self.filters is None:
            self.filters = {}


class NaturalLanguageProcessor:
    """Process natural language to extract visualization intent."""

    def __init__(self):
        self.patterns = self._init_patterns()
        self.column_aliases = self._init_column_aliases()

    def _init_patterns(self) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
        """Initialize regex patterns for chart type detection."""
        return {
            'chart_type': [
                # Line charts
                (r'\b(line|trend|over time|time series|temporal)\b', {'type': ChartType.LINE, 'analysis': AnalysisType.TEMPORAL}),
                (r'\b(plot.*over|show.*trend|track.*over)\b', {'type': ChartType.LINE, 'analysis': AnalysisType.TREND}),

                # Scatter plots
                (r'\b(scatter|relationship|correlation between)\b', {'type': ChartType.SCATTER, 'analysis': AnalysisType.CORRELATION}),
                (r'\b(vs|versus|against)\b', {'type': ChartType.SCATTER, 'analysis': AnalysisType.CORRELATION}),

                # Bar charts
                (r'\b(bar|compare|comparison|by category|by region)\b', {'type': ChartType.BAR, 'analysis': AnalysisType.COMPARISON}),
                (r'\b(show.*by|breakdown.*by|group.*by)\b', {'type': ChartType.BAR, 'analysis': AnalysisType.COMPOSITION}),

                # Histograms
                (r'\b(histogram|distribution|frequency)\b', {'type': ChartType.HISTOGRAM, 'analysis': AnalysisType.DISTRIBUTION}),

                # Box plots
                (r'\b(box plot|quartile|outlier)\b', {'type': ChartType.BOX, 'analysis': AnalysisType.DISTRIBUTION}),

                # Heatmaps
                (r'\b(heatmap|heat map|intensity|correlation matrix)\b', {'type': ChartType.HEATMAP, 'analysis': AnalysisType.CORRELATION}),

                # Surface plots
                (r'\b(surface|3d|three dimensional|contour)\b', {'type': ChartType.SURFACE, 'analysis': AnalysisType.TREND}),
            ],

            'style_hints': [
                # Colors
                (r'\b(red|blue|green|yellow|purple|orange|black|white)\b', 'color'),
                (r'\b(dark|light|bright|vibrant)\b', 'color_scheme'),

                # Sizes
                (r'\b(large|small|big|tiny|huge)\b', 'size'),
                (r'\b(thick|thin|bold|fine)\b', 'line_width'),

                # Themes
                (r'\b(professional|business|scientific|engineering|dark|light)\b', 'theme'),
            ],

            'aggregation': [
                (r'\b(sum|total|average|mean|median|count|max|maximum|min|minimum)\b', 'agg_func'),
                (r'\b(monthly|weekly|daily|yearly|quarterly)\b', 'time_agg'),
            ],

            'filters': [
                (r'\bwhere\s+(\w+)\s*(>|<|=|>=|<=)\s*([0-9.]+)\b', 'numeric_filter'),
                (r'\bwhere\s+(\w+)\s*=\s*["\']([^"\']+)["\']\b', 'text_filter'),
            ]
        }

    def _init_column_aliases(self) -> Dict[str, List[str]]:
        """Common aliases for column names."""
        return {
            'time': ['date', 'time', 'timestamp', 'datetime', 'year', 'month', 'day'],
            'sales': ['sales', 'revenue', 'income', 'earnings'],
            'price': ['price', 'cost', 'amount', 'value'],
            'quantity': ['quantity', 'count', 'number', 'volume'],
            'region': ['region', 'area', 'location', 'geography', 'territory'],
            'category': ['category', 'type', 'class', 'group', 'segment'],
            'performance': ['performance', 'score', 'rating', 'metric'],
        }

    def parse(self, text: str, data_columns: Optional[List[str]] = None) -> ChartIntent:
        """Parse natural language text to extract chart intent."""
        text = text.lower().strip()

        # Extract chart type and analysis type
        chart_type, analysis_type, confidence = self._extract_chart_type(text)

        # Extract column mappings
        x_col, y_col = self._extract_columns(text, data_columns)

        # Extract styling hints
        style_hints = self._extract_style_hints(text)

        # Extract title
        title = self._extract_title(text)

        # Extract aggregation
        aggregation = self._extract_aggregation(text)

        # Extract filters
        filters = self._extract_filters(text)

        return ChartIntent(
            chart_type=chart_type,
            analysis_type=analysis_type,
            x_column=x_col,
            y_column=y_col,
            title=title,
            style_hints=style_hints,
            aggregation=aggregation,
            filters=filters,
            confidence=confidence
        )

    def _extract_chart_type(self, text: str) -> Tuple[ChartType, AnalysisType, float]:
        """Extract chart type and analysis type from text."""
        best_match = None
        highest_confidence = 0.0

        for pattern, config in self.patterns['chart_type']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Simple confidence based on pattern specificity
                confidence = len(match.group(0)) / len(text) * 100
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    best_match = config

        if best_match:
            return best_match['type'], best_match['analysis'], highest_confidence

        # Default fallback
        return ChartType.SCATTER, AnalysisType.CORRELATION, 0.1

    def _extract_columns(self, text: str, data_columns: Optional[List[str]]) -> Tuple[Optional[str], Optional[str]]:
        """Extract column names from text."""
        if not data_columns:
            return None, None

        # Look for explicit column mentions
        mentioned_columns = []
        for col in data_columns:
            if col.lower() in text:
                mentioned_columns.append(col)

        # Try to match column aliases
        for alias, variants in self.column_aliases.items():
            for variant in variants:
                if variant in text:
                    # Find matching actual column
                    for col in data_columns:
                        if any(v in col.lower() for v in variants):
                            mentioned_columns.append(col)
                            break

        # Remove duplicates while preserving order
        mentioned_columns = list(dict.fromkeys(mentioned_columns))

        if len(mentioned_columns) >= 2:
            return mentioned_columns[0], mentioned_columns[1]
        elif len(mentioned_columns) == 1:
            # Try to infer the other column
            col = mentioned_columns[0]
            if any(t in col.lower() for t in ['time', 'date', 'year']):
                # Time column found, look for value column
                value_cols = [c for c in data_columns if c != col and
                             any(v in c.lower() for v in ['sales', 'revenue', 'price', 'value', 'amount'])]
                if value_cols:
                    return col, value_cols[0]
            return col, None

        return None, None

    def _extract_style_hints(self, text: str) -> Dict[str, Any]:
        """Extract styling hints from text."""
        hints = {}

        for pattern, hint_type in self.patterns['style_hints']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hints[hint_type] = match.group(0)

        return hints

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract or generate title from text."""
        # Look for explicit title patterns
        title_patterns = [
            r'title[d]?\s*["\']([^"\']+)["\']',
            r'call(?:ed)?\s*["\']([^"\']+)["\']',
            r'show\s*["\']([^"\']+)["\']'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        # Generate title from the first few words
        words = text.split()[:6]
        if len(words) > 2:
            return ' '.join(words).title()

        return None

    def _extract_aggregation(self, text: str) -> Optional[str]:
        """Extract aggregation function from text."""
        for pattern, _ in self.patterns['aggregation']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_filters(self, text: str) -> Dict[str, Any]:
        """Extract filter conditions from text."""
        filters = {}

        # Numeric filters
        numeric_pattern = r'\bwhere\s+(\w+)\s*(>|<|=|>=|<=)\s*([0-9.]+)\b'
        for match in re.finditer(numeric_pattern, text, re.IGNORECASE):
            column, operator, value = match.groups()
            filters[column] = {'op': operator, 'value': float(value)}

        # Text filters
        text_pattern = r'\bwhere\s+(\w+)\s*=\s*["\']([^"\']+)["\']\b'
        for match in re.finditer(text_pattern, text, re.IGNORECASE):
            column, value = match.groups()
            filters[column] = {'op': '=', 'value': value}

        return filters


class AIChartGenerator:
    """Generate charts from natural language descriptions."""

    def __init__(self):
        self.nlp = NaturalLanguageProcessor()

    def create(self, description: str, data: Optional[Union[np.ndarray, 'pd.DataFrame']] = None,
               data_columns: Optional[List[str]] = None) -> Any:
        """
        Create a chart from natural language description.

        Args:
            description: Natural language description of the desired chart
            data: Optional data to use for the chart
            data_columns: Column names if data is provided

        Returns:
            Configured chart object
        """
        # Parse the description
        intent = self.nlp.parse(description, data_columns)

        # Import chart classes
        from ..charts import (
            LineChart, ScatterChart, BarChart, HistogramChart,
            BoxChart, HeatmapChart, SurfaceChart
        )
        from ..charts.datascience import (
            TimeSeriesChart, DistributionChart, CorrelationChart
        )

        # Select chart class
        chart_class = self._get_chart_class(intent.chart_type)

        # Create chart with auto-detected parameters
        chart = chart_class()

        # Apply data if provided
        if data is not None:
            self._apply_data(chart, data, intent, data_columns)

        # Apply styling
        self._apply_styling(chart, intent)

        # Set title
        if intent.title:
            chart.set_title(intent.title)
        elif hasattr(chart, 'set_title'):
            chart.set_title(self._generate_title(intent))

        return chart

    def _get_chart_class(self, chart_type: ChartType):
        """Get appropriate chart class for the chart type."""
        from ..charts import (
            LineChart, ScatterChart, BarChart, HistogramChart,
            BoxChart, HeatmapChart, SurfaceChart
        )
        from ..charts.datascience import (
            TimeSeriesChart, DistributionChart, CorrelationChart
        )

        mapping = {
            ChartType.LINE: LineChart,
            ChartType.SCATTER: ScatterChart,
            ChartType.BAR: BarChart,
            ChartType.HISTOGRAM: HistogramChart,
            ChartType.BOX: BoxChart,
            ChartType.HEATMAP: HeatmapChart,
            ChartType.SURFACE: SurfaceChart,
            ChartType.TIMESERIES: TimeSeriesChart,
            ChartType.DISTRIBUTION: DistributionChart,
            ChartType.CORRELATION: CorrelationChart,
        }

        return mapping.get(chart_type, ScatterChart)

    def _apply_data(self, chart, data: Union[np.ndarray, 'pd.DataFrame'],
                   intent: ChartIntent, data_columns: Optional[List[str]]):
        """Apply data to the chart based on intent."""
        if HAS_PANDAS and isinstance(data, pd.DataFrame):
            self._apply_dataframe(chart, data, intent)
        elif isinstance(data, np.ndarray):
            self._apply_numpy_array(chart, data, intent, data_columns)

    def _apply_dataframe(self, chart, df: 'pd.DataFrame', intent: ChartIntent):
        """Apply pandas DataFrame to chart."""
        x_col = intent.x_column
        y_col = intent.y_column

        # Auto-detect columns if not specified
        if not x_col or not y_col:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

            if datetime_cols and not x_col:
                x_col = datetime_cols[0]
            elif numeric_cols and not x_col:
                x_col = numeric_cols[0]

            if numeric_cols and not y_col:
                candidates = [c for c in numeric_cols if c != x_col]
                if candidates:
                    y_col = candidates[0]

        # Apply filters
        filtered_df = df
        for col, filter_config in intent.filters.items():
            if col in df.columns:
                op = filter_config['op']
                value = filter_config['value']
                if op == '=':
                    filtered_df = filtered_df[filtered_df[col] == value]
                elif op == '>':
                    filtered_df = filtered_df[filtered_df[col] > value]
                elif op == '<':
                    filtered_df = filtered_df[filtered_df[col] < value]

        # Plot data based on chart type
        if hasattr(chart, 'plot') and x_col and y_col:
            chart.plot(filtered_df[x_col].values, filtered_df[y_col].values)
        elif hasattr(chart, 'scatter') and x_col and y_col:
            chart.scatter(filtered_df[x_col].values, filtered_df[y_col].values)
        elif hasattr(chart, 'bar') and x_col and y_col:
            chart.bar(filtered_df[x_col].values, filtered_df[y_col].values)

    def _apply_numpy_array(self, chart, data: np.ndarray, intent: ChartIntent,
                          data_columns: Optional[List[str]]):
        """Apply numpy array to chart."""
        if data.ndim == 1:
            # 1D data - create x values
            x = np.arange(len(data))
            y = data
        elif data.ndim == 2 and data.shape[1] >= 2:
            # 2D data - use first two columns
            x = data[:, 0]
            y = data[:, 1]
        else:
            return  # Can't handle this data format

        # Plot based on chart type
        if hasattr(chart, 'plot'):
            chart.plot(x, y)
        elif hasattr(chart, 'scatter'):
            chart.scatter(x, y)

    def _apply_styling(self, chart, intent: ChartIntent):
        """Apply styling based on intent."""
        style_hints = intent.style_hints

        # Apply color
        if 'color' in style_hints and hasattr(chart, 'set_color'):
            chart.set_color(style_hints['color'])

        # Apply theme
        if 'theme' in style_hints and hasattr(chart, 'set_theme'):
            chart.set_theme(style_hints['theme'])

        # Apply size hints
        if 'size' in style_hints and hasattr(chart, 'set_size'):
            size_map = {'small': 0.5, 'large': 1.5, 'huge': 2.0}
            size = size_map.get(style_hints['size'], 1.0)
            chart.set_size(size)

    def _generate_title(self, intent: ChartIntent) -> str:
        """Generate a title based on the intent."""
        chart_name = intent.chart_type.value.title()

        if intent.x_column and intent.y_column:
            return f"{chart_name}: {intent.y_column} vs {intent.x_column}"
        elif intent.y_column:
            return f"{chart_name}: {intent.y_column}"
        else:
            return f"{chart_name} Chart"


# Convenient module-level function
def create(description: str, data=None, data_columns=None):
    """
    Create a chart from natural language description.

    Examples:
        >>> import openfinops as vc
        >>> chart = vc.ai.create("scatter plot of sales vs price")
        >>> chart = vc.ai.create("line chart showing revenue over time")
        >>> chart = vc.ai.create("bar chart comparing sales by region")
    """
    generator = AIChartGenerator()
    return generator.create(description, data, data_columns)