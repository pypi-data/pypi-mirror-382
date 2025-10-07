"""
Smart Chart Type Selection
=========================

Intelligent algorithms for automatically selecting the best chart type
based on data characteristics and analysis goals.
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

import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class DataType(Enum):
    """Data type classifications."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    BOOLEAN = "boolean"


class DataDistribution(Enum):
    """Data distribution patterns."""
    NORMAL = "normal"
    SKEWED = "skewed"
    BIMODAL = "bimodal"
    UNIFORM = "uniform"
    SPARSE = "sparse"


class AnalysisIntent(Enum):
    """Types of analysis the user might want."""
    COMPARISON = "comparison"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    TREND = "trend"
    COMPOSITION = "composition"
    RELATIONSHIP = "relationship"
    HIERARCHY = "hierarchy"


@dataclass
class DataProfile:
    """Profile of a dataset or column."""
    data_type: DataType
    size: int
    unique_values: int
    null_percentage: float
    distribution: Optional[DataDistribution] = None
    temporal_pattern: bool = False
    categorical_cardinality: Optional[str] = None  # low, medium, high
    numeric_range: Optional[Tuple[float, float]] = None
    sample_values: List[Any] = None

    def __post_init__(self):
        if self.sample_values is None:
            self.sample_values = []


@dataclass
class ChartRecommendation:
    """Recommendation for a chart type with confidence score."""
    chart_type: str
    confidence: float
    reasons: List[str]
    alternative_types: List[str] = None
    configuration_hints: Dict[str, Any] = None

    def __post_init__(self):
        if self.alternative_types is None:
            self.alternative_types = []
        if self.configuration_hints is None:
            self.configuration_hints = {}


class DataAnalyzer:
    """Analyze data characteristics to inform chart selection."""

    def __init__(self):
        self.type_detectors = {
            DataType.DATETIME: self._is_datetime,
            DataType.NUMERIC: self._is_numeric,
            DataType.BOOLEAN: self._is_boolean,
            DataType.CATEGORICAL: self._is_categorical,
            DataType.TEXT: self._is_text,
        }

    def analyze_column(self, data: Union[np.ndarray, List, 'pd.Series']) -> DataProfile:
        """Analyze a single column of data."""
        if HAS_PANDAS and isinstance(data, pd.Series):
            return self._analyze_pandas_series(data)
        elif isinstance(data, (list, np.ndarray)):
            return self._analyze_array(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    def _analyze_pandas_series(self, series: 'pd.Series') -> DataProfile:
        """Analyze pandas Series."""
        # Basic stats
        size = len(series)
        unique_count = series.nunique()
        null_pct = series.isnull().sum() / size * 100

        # Detect data type
        data_type = self._detect_pandas_type(series)

        # Distribution analysis for numeric data
        distribution = None
        numeric_range = None
        if data_type == DataType.NUMERIC:
            distribution = self._analyze_distribution(series.dropna().values)
            numeric_range = (float(series.min()), float(series.max()))

        # Categorical cardinality
        categorical_cardinality = None
        if data_type == DataType.CATEGORICAL:
            if unique_count <= 5:
                categorical_cardinality = "low"
            elif unique_count <= 20:
                categorical_cardinality = "medium"
            else:
                categorical_cardinality = "high"

        # Temporal patterns
        temporal_pattern = False
        if data_type == DataType.DATETIME:
            temporal_pattern = True
        elif data_type == DataType.NUMERIC:
            # Check if numeric data has temporal characteristics
            temporal_pattern = self._has_temporal_pattern(series)

        # Sample values
        sample_values = series.dropna().head(10).tolist()

        return DataProfile(
            data_type=data_type,
            size=size,
            unique_values=unique_count,
            null_percentage=null_pct,
            distribution=distribution,
            temporal_pattern=temporal_pattern,
            categorical_cardinality=categorical_cardinality,
            numeric_range=numeric_range,
            sample_values=sample_values
        )

    def _analyze_array(self, data: Union[List, np.ndarray]) -> DataProfile:
        """Analyze list or numpy array."""
        if isinstance(data, list):
            data = np.array(data)

        size = len(data)
        unique_values = len(np.unique(data))

        # Count nulls/nans
        null_count = 0
        if data.dtype.kind in 'fc':  # float or complex
            null_count = np.isnan(data).sum()
        elif data.dtype.kind == 'O':  # object
            null_count = sum(1 for x in data if x is None or (isinstance(x, str) and x.strip() == ''))

        null_pct = null_count / size * 100

        # Detect data type
        data_type = self._detect_array_type(data)

        # Distribution analysis
        distribution = None
        numeric_range = None
        if data_type == DataType.NUMERIC:
            clean_data = data[~np.isnan(data)] if data.dtype.kind in 'fc' else data
            if len(clean_data) > 0:
                distribution = self._analyze_distribution(clean_data)
                numeric_range = (float(np.min(clean_data)), float(np.max(clean_data)))

        # Sample values
        sample_values = data[:min(10, len(data))].tolist()

        return DataProfile(
            data_type=data_type,
            size=size,
            unique_values=unique_values,
            null_percentage=null_pct,
            distribution=distribution,
            temporal_pattern=False,
            categorical_cardinality=None,
            numeric_range=numeric_range,
            sample_values=sample_values
        )

    def _detect_pandas_type(self, series: 'pd.Series') -> DataType:
        """Detect data type for pandas Series."""
        if pd.api.types.is_datetime64_any_dtype(series):
            return DataType.DATETIME
        elif pd.api.types.is_numeric_dtype(series):
            return DataType.NUMERIC
        elif pd.api.types.is_bool_dtype(series):
            return DataType.BOOLEAN
        elif pd.api.types.is_categorical_dtype(series) or series.dtype == 'object':
            # Check if it's actually categorical
            if series.nunique() / len(series) < 0.5:  # Less than 50% unique values
                return DataType.CATEGORICAL
            else:
                return DataType.TEXT
        else:
            return DataType.TEXT

    def _detect_array_type(self, data: np.ndarray) -> DataType:
        """Detect data type for numpy array."""
        if data.dtype.kind in 'fc':  # float or complex
            return DataType.NUMERIC
        elif data.dtype.kind in 'iu':  # integer or unsigned
            return DataType.NUMERIC
        elif data.dtype.kind == 'b':  # boolean
            return DataType.BOOLEAN
        elif data.dtype.kind in 'U':  # unicode string
            # Check if categorical
            unique_ratio = len(np.unique(data)) / len(data)
            return DataType.CATEGORICAL if unique_ratio < 0.5 else DataType.TEXT
        else:
            return DataType.TEXT

    def _analyze_distribution(self, data: np.ndarray) -> DataDistribution:
        """Analyze numeric data distribution."""
        if len(data) < 10:
            return DataDistribution.SPARSE

        try:
            from scipy import stats

            # Test for normality
            _, p_normal = stats.normaltest(data)

            # Calculate skewness
            skewness = stats.skew(data)

            # Test for bimodality (simple approach)
            hist, _ = np.histogram(data, bins=20)
            peaks = self._count_peaks(hist)

            if p_normal > 0.05:  # Normal distribution
                return DataDistribution.NORMAL
            elif peaks > 1:
                return DataDistribution.BIMODAL
            elif abs(skewness) > 1:
                return DataDistribution.SKEWED
            else:
                return DataDistribution.UNIFORM

        except ImportError:
            # Fallback without scipy
            std_dev = np.std(data)
            mean_val = np.mean(data)

            if std_dev / mean_val < 0.1:  # Low coefficient of variation
                return DataDistribution.UNIFORM
            else:
                return DataDistribution.NORMAL

    def _count_peaks(self, histogram: np.ndarray) -> int:
        """Count peaks in histogram."""
        peaks = 0
        for i in range(1, len(histogram) - 1):
            if histogram[i] > histogram[i-1] and histogram[i] > histogram[i+1]:
                peaks += 1
        return peaks

    def _has_temporal_pattern(self, series: 'pd.Series') -> bool:
        """Check if numeric data has temporal characteristics."""
        if not HAS_PANDAS:
            return False

        # Check if values are monotonically increasing (like timestamps)
        diff = series.diff().dropna()
        if len(diff) > 0:
            positive_ratio = (diff > 0).sum() / len(diff)
            return positive_ratio > 0.8  # 80% increasing

        return False

    def _is_datetime(self, data) -> bool:
        """Check if data is datetime."""
        if HAS_PANDAS and isinstance(data, pd.Series):
            return pd.api.types.is_datetime64_any_dtype(data)
        return False

    def _is_numeric(self, data) -> bool:
        """Check if data is numeric."""
        if HAS_PANDAS and isinstance(data, pd.Series):
            return pd.api.types.is_numeric_dtype(data)
        elif isinstance(data, np.ndarray):
            return data.dtype.kind in 'biufc'
        return False

    def _is_boolean(self, data) -> bool:
        """Check if data is boolean."""
        if HAS_PANDAS and isinstance(data, pd.Series):
            return pd.api.types.is_bool_dtype(data)
        elif isinstance(data, np.ndarray):
            return data.dtype.kind == 'b'
        return False

    def _is_categorical(self, data) -> bool:
        """Check if data is categorical."""
        if HAS_PANDAS and isinstance(data, pd.Series):
            return pd.api.types.is_categorical_dtype(data) or (
                data.dtype == 'object' and data.nunique() / len(data) < 0.5
            )
        return False

    def _is_text(self, data) -> bool:
        """Check if data is text."""
        return not any(detector(data) for detector in [
            self._is_datetime, self._is_numeric, self._is_boolean, self._is_categorical
        ])


class SmartChartSelector:
    """Intelligently recommend chart types based on data characteristics."""

    def __init__(self):
        self.analyzer = DataAnalyzer()
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize chart selection rules."""
        return {
            # Single variable visualizations
            'histogram': {
                'conditions': [
                    lambda profiles: len(profiles) == 1 and profiles[0].data_type == DataType.NUMERIC,
                    lambda profiles: profiles[0].distribution in [DataDistribution.NORMAL, DataDistribution.SKEWED]
                ],
                'confidence': 0.9,
                'reasons': ['Single numeric variable', 'Shows distribution pattern']
            },

            'box_plot': {
                'conditions': [
                    lambda profiles: len(profiles) == 1 and profiles[0].data_type == DataType.NUMERIC,
                    lambda profiles: profiles[0].size > 20
                ],
                'confidence': 0.7,
                'reasons': ['Numeric data with outliers', 'Shows quartiles and outliers']
            },

            # Two variable visualizations
            'scatter': {
                'conditions': [
                    lambda profiles: len(profiles) == 2,
                    lambda profiles: all(p.data_type == DataType.NUMERIC for p in profiles),
                    lambda profiles: all(p.size > 10 for p in profiles)
                ],
                'confidence': 0.9,
                'reasons': ['Two numeric variables', 'Best for correlation analysis']
            },

            'line': {
                'conditions': [
                    lambda profiles: len(profiles) == 2,
                    lambda profiles: any(p.temporal_pattern or p.data_type == DataType.DATETIME for p in profiles),
                    lambda profiles: any(p.data_type == DataType.NUMERIC for p in profiles)
                ],
                'confidence': 0.95,
                'reasons': ['Temporal data detected', 'Shows trends over time']
            },

            'bar': {
                'conditions': [
                    lambda profiles: len(profiles) == 2,
                    lambda profiles: any(p.data_type == DataType.CATEGORICAL for p in profiles),
                    lambda profiles: any(p.data_type == DataType.NUMERIC for p in profiles),
                    lambda profiles: all(p.categorical_cardinality in ['low', 'medium']
                                       for p in profiles if p.data_type == DataType.CATEGORICAL)
                ],
                'confidence': 0.85,
                'reasons': ['Categorical vs numeric comparison', 'Good for comparing groups']
            },

            'heatmap': {
                'conditions': [
                    lambda profiles: len(profiles) >= 3,
                    lambda profiles: sum(1 for p in profiles if p.data_type == DataType.NUMERIC) >= 2,
                    lambda profiles: all(p.size < 1000 for p in profiles)  # Not too large
                ],
                'confidence': 0.7,
                'reasons': ['Multiple numeric variables', 'Shows correlation patterns']
            },

            # Specialized visualizations
            'surface': {
                'conditions': [
                    lambda profiles: len(profiles) == 3,
                    lambda profiles: all(p.data_type == DataType.NUMERIC for p in profiles),
                    lambda profiles: all(p.size > 20 for p in profiles)
                ],
                'confidence': 0.8,
                'reasons': ['Three numeric variables', 'Good for 3D relationships']
            }
        }

    def recommend(self, data: Union[Dict[str, Any], List[Any], np.ndarray, 'pd.DataFrame'],
                  intent: Optional[AnalysisIntent] = None) -> ChartRecommendation:
        """
        Recommend the best chart type for the given data.

        Args:
            data: Input data in various formats
            intent: Optional analysis intent to guide selection

        Returns:
            ChartRecommendation with type, confidence, and reasoning
        """
        # Analyze data profiles
        profiles = self._extract_profiles(data)

        # Score all chart types
        scores = {}
        for chart_type, rule in self.rules.items():
            score = self._evaluate_rule(rule, profiles)
            if score > 0:
                scores[chart_type] = score

        # Apply intent-based adjustments
        if intent:
            scores = self._apply_intent_bias(scores, intent, profiles)

        # Select best recommendation
        if not scores:
            return self._fallback_recommendation(profiles)

        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]

        # Get reasons
        reasons = self.rules[best_type]['reasons'].copy()

        # Alternative types
        alternatives = [t for t, s in sorted(scores.items(), key=lambda x: x[1], reverse=True)
                       if t != best_type and s > 0.5][:3]

        # Configuration hints
        config_hints = self._generate_config_hints(best_type, profiles)

        return ChartRecommendation(
            chart_type=best_type,
            confidence=confidence,
            reasons=reasons,
            alternative_types=alternatives,
            configuration_hints=config_hints
        )

    def _extract_profiles(self, data: Union[Dict[str, Any], List[Any], np.ndarray, 'pd.DataFrame']) -> List[DataProfile]:
        """Extract data profiles from input data."""
        profiles = []

        if HAS_PANDAS and isinstance(data, pd.DataFrame):
            for column in data.columns:
                profiles.append(self.analyzer.analyze_column(data[column]))
        elif isinstance(data, dict):
            for key, values in data.items():
                profiles.append(self.analyzer.analyze_column(values))
        elif isinstance(data, (list, np.ndarray)):
            profiles.append(self.analyzer.analyze_column(data))
        else:
            raise ValueError(f"Unsupported data format: {type(data)}")

        return profiles

    def _evaluate_rule(self, rule: Dict[str, Any], profiles: List[DataProfile]) -> float:
        """Evaluate a chart selection rule against data profiles."""
        try:
            # Check all conditions
            for condition in rule['conditions']:
                if not condition(profiles):
                    return 0.0

            return rule['confidence']
        except Exception:
            return 0.0

    def _apply_intent_bias(self, scores: Dict[str, float], intent: AnalysisIntent,
                          profiles: List[DataProfile]) -> Dict[str, float]:
        """Apply intent-based bias to chart scores."""
        intent_preferences = {
            AnalysisIntent.CORRELATION: ['scatter', 'heatmap'],
            AnalysisIntent.DISTRIBUTION: ['histogram', 'box_plot'],
            AnalysisIntent.TREND: ['line'],
            AnalysisIntent.COMPARISON: ['bar', 'box_plot'],
            AnalysisIntent.COMPOSITION: ['bar', 'pie'],
            AnalysisIntent.RELATIONSHIP: ['scatter', 'surface']
        }

        preferred_types = intent_preferences.get(intent, [])

        # Boost preferred types
        for chart_type in preferred_types:
            if chart_type in scores:
                scores[chart_type] *= 1.2

        return scores

    def _fallback_recommendation(self, profiles: List[DataProfile]) -> ChartRecommendation:
        """Provide fallback recommendation when no rules match."""
        if len(profiles) == 1:
            return ChartRecommendation(
                chart_type='histogram',
                confidence=0.3,
                reasons=['Fallback for single variable'],
                alternative_types=['box_plot']
            )
        elif len(profiles) == 2:
            return ChartRecommendation(
                chart_type='scatter',
                confidence=0.3,
                reasons=['Fallback for two variables'],
                alternative_types=['line', 'bar']
            )
        else:
            return ChartRecommendation(
                chart_type='heatmap',
                confidence=0.3,
                reasons=['Fallback for multiple variables'],
                alternative_types=['scatter']
            )

    def _generate_config_hints(self, chart_type: str, profiles: List[DataProfile]) -> Dict[str, Any]:
        """Generate configuration hints for the recommended chart type."""
        hints = {}

        if chart_type == 'scatter':
            # Suggest point size based on data size
            total_points = sum(p.size for p in profiles)
            if total_points > 1000:
                hints['point_size'] = 'small'
                hints['alpha'] = 0.6
            elif total_points < 100:
                hints['point_size'] = 'large'

        elif chart_type == 'bar':
            # Suggest orientation based on category names
            cat_profile = next((p for p in profiles if p.data_type == DataType.CATEGORICAL), None)
            if cat_profile and cat_profile.sample_values:
                avg_length = np.mean([len(str(val)) for val in cat_profile.sample_values[:5]])
                if avg_length > 10:
                    hints['orientation'] = 'horizontal'

        elif chart_type == 'line':
            # Suggest time formatting
            datetime_profile = next((p for p in profiles
                                   if p.data_type == DataType.DATETIME or p.temporal_pattern), None)
            if datetime_profile:
                hints['x_axis_format'] = 'datetime'

        elif chart_type == 'histogram':
            # Suggest number of bins
            profile = profiles[0]
            if profile.size < 50:
                hints['bins'] = 10
            elif profile.size < 500:
                hints['bins'] = 20
            else:
                hints['bins'] = 50

        return hints

    def explain_recommendation(self, recommendation: ChartRecommendation) -> str:
        """Generate human-readable explanation for the recommendation."""
        explanation = f"Recommended: {recommendation.chart_type.title()} Chart (confidence: {recommendation.confidence:.1%})\n\n"

        explanation += "Reasons:\n"
        for reason in recommendation.reasons:
            explanation += f"• {reason}\n"

        if recommendation.alternative_types:
            explanation += f"\nAlternatives to consider: {', '.join(recommendation.alternative_types)}\n"

        if recommendation.configuration_hints:
            explanation += "\nSuggested configurations:\n"
            for key, value in recommendation.configuration_hints.items():
                explanation += f"• {key}: {value}\n"

        return explanation


# Convenient function for quick recommendations
def recommend_chart(data, intent: Optional[str] = None) -> ChartRecommendation:
    """
    Quick function to get chart recommendations.

    Args:
        data: Input data (DataFrame, dict, array, etc.)
        intent: Optional analysis intent ('correlation', 'distribution', etc.)

    Returns:
        ChartRecommendation
    """
    selector = SmartChartSelector()

    # Convert string intent to enum
    intent_enum = None
    if intent:
        try:
            intent_enum = AnalysisIntent(intent.lower())
        except ValueError:
            warnings.warn(f"Unknown intent '{intent}', proceeding without intent bias")

    return selector.recommend(data, intent_enum)