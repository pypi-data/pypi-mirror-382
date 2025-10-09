"""OpenFinOps Charts Module - Professional chart implementations using VizlyEngine."""

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



# Main chart classes using VizlyEngine
from .professional_charts import (
    ProfessionalLineChart as LineChart,
    ProfessionalScatterChart as ScatterChart,
    ProfessionalBarChart as BarChart
)

# Enhanced matplotlib-like API
from .enhanced_api import (
    EnhancedLineChart,
    EnhancedScatterChart,
    EnhancedBarChart,
    linechart,
    scatterchart,
    barchart
)
from .histogram import HistogramChart
from .box import BoxChart

# Advanced chart types
from .advanced import (
    HeatmapChart,
    ViolinChart,
    RadarChart,
    TreemapChart,
    SankeyChart,
    SpectrogramChart,
    ClusterChart,
    ParallelCoordinatesChart,
    ConvexHullChart,
)

# Financial chart types
from .financial import (
    CandlestickChart,
    OHLCChart,
    VolumeProfileChart,
    RSIChart,
    MACDChart,
    PointAndFigureChart,
)

# Engineering chart types
from .engineering import (
    BodePlot,
    StressStrainChart,
    PhaseDiagram,
    ContourChart,
)

# Data science chart types
from .datascience import (
    DistributionChart,
    CorrelationChart,
    RegressionChart,
)

__all__ = [
    # Main VizlyEngine charts
    "LineChart",
    "ScatterChart",
    "BarChart",

    # Enhanced matplotlib-like API
    "EnhancedLineChart",
    "EnhancedScatterChart",
    "EnhancedBarChart",
    "linechart",
    "scatterchart",
    "barchart",

    # Legacy chart types (may use different engines)
    "SurfaceChart",
    "InteractiveSurfaceChart",
    "HistogramChart",
    "BoxChart",
    "HeatmapChart",
    "ViolinChart",
    "RadarChart",
    "TreemapChart",
    "SankeyChart",
    "SpectrogramChart",
    "ClusterChart",
    "ParallelCoordinatesChart",
    "ConvexHullChart",
    "CandlestickChart",
    "OHLCChart",
    "VolumeProfileChart",
    "RSIChart",
    "MACDChart",
    "PointAndFigureChart",
    "BodePlot",
    "StressStrainChart",
    "PhaseDiagram",
    "ContourChart",
    "DistributionChart",
    "CorrelationChart",
    "RegressionChart",
]
