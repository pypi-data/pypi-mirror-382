"""
OpenFinOps - Professional Data Visualization Library
===================================================

A high-performance charting library powered by VizlyEngine for professional-quality visualization.

Key Features:
- VizlyEngine: Professional HDR rendering with anti-aliasing
- Multiple chart types: line, scatter, bar, surface, heatmap
- SVG and PNG export with high DPI support
- Jupyter notebook integration
- Engineering-grade precision and quality
- matplotlib-compatible API

Basic Usage:
    >>> import openfinops as vc
    >>> import numpy as np
    >>>
    >>> # Create data
    >>> x = np.linspace(0, 10, 100)
    >>> y = np.sin(x)
    >>>
    >>> # Professional chart with VizlyEngine
    >>> chart = vc.LineChart()
    >>> chart.plot(x, y, color=vc.ColorHDR.from_hex('#3498db'), smooth=True)
    >>> chart.set_title("VizlyEngine Professional Chart")
    >>> chart.show()

Enhanced matplotlib-like API:
    >>> # matplotlib-compatible interface
    >>> chart = vc.linechart()
    >>> chart.plot(x, y, color='blue', linewidth=2, label='Data')
    >>> chart.set_title("matplotlib-style API")
    >>> chart.grid(True)
    >>> chart.legend()
    >>> chart.show()

Quick Plotting:
    >>> # One-line plotting
    >>> chart = vc.quick_plot(x, y, 'line', title='Quick Plot')
    >>> chart.show()
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



__version__ = "2.4.4"
__author__ = "OpenFinOps Development Team"
__license__ = "MIT"
__description__ = "Professional data visualization library powered by VizlyEngine"

# Try to import the available modules, with fallbacks for missing ones
try:
    from .exceptions import ChartValidationError, VizlyError, ThemeNotFoundError
except ImportError:
    # Define minimal exceptions if module is missing
    class VizlyError(Exception):
        """Base exception for Vizly-related errors."""
        pass

    class ThemeNotFoundError(VizlyError):
        """Raised when a requested theme key is not registered."""
        pass

    class ChartValidationError(VizlyError):
        """Raised when chart inputs fail validation."""
        pass

# VIZLYENGINE - Professional rendering system
try:
    from .charts.professional_charts import (
        ProfessionalLineChart as LineChart,
        ProfessionalScatterChart as ScatterChart,
        ProfessionalBarChart as BarChart
    )
    from .charts.enhanced_api import (
        EnhancedLineChart, EnhancedScatterChart, EnhancedBarChart,
        linechart, scatterchart, barchart
    )
    from .rendering.vizlyengine import RenderQuality, ColorHDR, Font

    VIZLYENGINE_AVAILABLE = True

except ImportError as e:
    # Fallback implementations if VizlyEngine unavailable
    LineChart = None
    ScatterChart = None
    BarChart = None
    EnhancedLineChart = None
    EnhancedScatterChart = None
    EnhancedBarChart = None
    RenderQuality = None
    ColorHDR = None
    Font = None
    VIZLYENGINE_AVAILABLE = False
    import warnings
    warnings.warn(f"VizlyEngine unavailable: {e}")

    def linechart(*args, **kwargs):
        raise ImportError("VizlyEngine not available")
    def scatterchart(*args, **kwargs):
        raise ImportError("VizlyEngine not available")
    def barchart(*args, **kwargs):
        raise ImportError("VizlyEngine not available")


try:
    from .figure import VizlyFigure
except ImportError:
    VizlyFigure = None

try:
    from .theme import THEMES, apply_theme, get_theme
except ImportError:
    THEMES = {}

    def apply_theme(theme):
        pass

    def get_theme():
        return "default"


# Legacy chart types (may be supported by other modules)
try:
    from .charts.surface import SurfaceChart, InteractiveSurfaceChart
    from .charts.advanced_charts import HeatmapChart
except ImportError:
    # Provide placeholder classes if legacy charts are missing
    class SurfaceChart:
        def __init__(self, width=800, height=600):
            pass
        def plot_surface(self, *args, **kwargs):
            return self
        def save(self, *args, **kwargs):
            pass
        def show(self):
            print("SurfaceChart not available")

    class InteractiveSurfaceChart:
        def __init__(self, width=800, height=600):
            pass
        def plot(self, *args, **kwargs):
            return self
        def export_mesh(self, *args, **kwargs):
            return {"rows": 0, "cols": 0, "x": [], "zmin": 0, "zmax": 0}
        def save(self, *args, **kwargs):
            pass
        def show(self):
            print("InteractiveSurfaceChart not available")

    class HeatmapChart:
        def __init__(self, width=800, height=600):
            pass
        def heatmap(self, *args, **kwargs):
            return self
        def save(self, *args, **kwargs):
            pass
        def show(self):
            print("HeatmapChart not available")


# Additional chart types
try:
    from .charts.histogram import HistogramChart
    from .charts.box import BoxChart
    from .charts.engineering import BodePlot, StressStrainChart
except ImportError:

    class HistogramChart:
        def __init__(self):
            pass

        def hist(self, *args, **kwargs):
            pass

        def plot(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

        def show(self):
            pass

    class BoxChart:
        def __init__(self):
            pass

        def boxplot(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

        def show(self):
            pass

    class BodePlot:
        def __init__(self):
            pass

        def plot(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

        def show(self):
            pass

    class StressStrainChart:
        def __init__(self):
            pass

        def plot(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

        def show(self):
            pass


# Create Figure class alias
try:
    from .figure import VizlyFigure as Figure
except ImportError:

    class Figure:
        def __init__(self, *args, **kwargs):
            pass

        def add_subplot(self, *args, **kwargs):
            pass

        def savefig(self, *args, **kwargs):
            pass

        def show(self):
            pass


# Advanced chart types (optional)
try:
    from .charts.advanced_charts import (
        HeatmapChart,
    )
    from .charts.advanced import (
        RadarChart,
    )
except ImportError:

    class HeatmapChart:
        def __init__(self):
            pass

        def heatmap(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

    class RadarChart:
        def __init__(self):
            pass

        def plot(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass


# Data Science chart types (advanced analytics)
try:
    from .charts.datascience import (
        TimeSeriesChart,
        DistributionChart,
        CorrelationChart,
        FinancialIndicatorChart,
    )
except ImportError:

    class TimeSeriesChart:
        def __init__(self):
            pass

        def plot_timeseries(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

    class DistributionChart:
        def __init__(self):
            pass

        def plot_distribution(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

    class CorrelationChart:
        def __init__(self):
            pass

        def plot_correlation_matrix(self, *args, **kwargs):
            pass

        def plot_scatter_matrix(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

    class FinancialIndicatorChart:
        def __init__(self):
            pass

        def plot_bollinger_bands(self, *args, **kwargs):
            pass

        def plot_rsi(self, *args, **kwargs):
            pass

        def plot_macd(self, *args, **kwargs):
            pass

        def plot_volume_profile(self, *args, **kwargs):
            pass

        def plot_candlestick_with_indicators(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass


# Interactive chart types (advanced interactivity)
try:
    from .interactive import (
        InteractiveChart,
        InteractiveScatterChart,
        InteractiveLineChart,
        RealTimeChart,
        FinancialStreamChart,
        InteractiveDashboard,
        DashboardBuilder,
    )
except ImportError:

    class InteractiveChart:
        def __init__(self):
            pass

        def enable_tooltips(self, *args, **kwargs):
            return self

        def enable_zoom_pan(self, *args, **kwargs):
            return self

        def enable_selection(self, *args, **kwargs):
            return self

        def show_interactive(self, *args, **kwargs):
            pass

    class InteractiveScatterChart:
        def __init__(self):
            pass

        def plot(self, *args, **kwargs):
            return self

    class InteractiveLineChart:
        def __init__(self):
            pass

        def plot(self, *args, **kwargs):
            return self

    class RealTimeChart:
        def __init__(self):
            pass

        def add_stream(self, *args, **kwargs):
            return self

        def start_streaming(self):
            pass

    class FinancialStreamChart:
        def __init__(self):
            pass

        def add_price_stream(self, *args, **kwargs):
            return self

    class InteractiveDashboard:
        def __init__(self):
            pass

        def create_container(self, *args, **kwargs):
            return None

    class DashboardBuilder:
        def __init__(self):
            pass

        def set_title(self, *args, **kwargs):
            return self

        def build(self):
            return InteractiveDashboard()


# Financial chart types (optional - legacy)
try:
    from .charts.financial import (
        CandlestickChart,
        RSIChart,
        MACDChart,
    )
except ImportError:

    class CandlestickChart:
        def __init__(self):
            pass

        def plot(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

    class RSIChart:
        def __init__(self):
            pass

        def plot(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass

    class MACDChart:
        def __init__(self):
            pass

        def plot(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            pass


# Core rendering (VizlyEngine implementation)
try:
    from .rendering.vizlyengine import AdvancedRenderer, AdvancedCanvas
    ImageRenderer = AdvancedRenderer
    Figure = AdvancedRenderer
    Canvas = AdvancedCanvas

    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

    class Rectangle:
        def __init__(self, x, y, w, h):
            self.x, self.y, self.w, self.h = x, y, w, h

except ImportError:
    # Provide minimal implementations if VizlyEngine unavailable
    class AdvancedRenderer:
        def __init__(self, *args, **kwargs):
            pass
        def save(self, *args, **kwargs):
            pass

    ImageRenderer = AdvancedRenderer
    Figure = AdvancedRenderer
    Canvas = AdvancedRenderer

    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

    class Rectangle:
        def __init__(self, x, y, w, h):
            self.x, self.y, self.w, self.h = x, y, w, h


# 3D Interaction (with safe imports)
try:
    from . import interaction3d
except ImportError:
    interaction3d = None

# AI-powered features
try:
    from . import ai
    from .ai import create as ai_create, recommend_chart, style_chart
except ImportError:
    ai = None
    ai_create = None
    recommend_chart = None
    style_chart = None

# Backend management
try:
    from . import backends
    from .backends import set_backend, list_backends
except ImportError:
    backends = None
    set_backend = None
    list_backends = None

# ML/Causal charts
try:
    from .charts.ml_causal import (
        CausalDAGChart, FeatureImportanceChart,
        SHAPWaterfallChart, ModelPerformanceChart
    )
except ImportError:
    CausalDAGChart = None
    FeatureImportanceChart = None
    SHAPWaterfallChart = None
    ModelPerformanceChart = None

# Advanced Features - NEW CAPABILITIES
try:
    # Advanced Chart Types
    from .charts.advanced_charts import ContourChart, BoxPlot, ViolinPlot
    from .charts.chart_3d import Chart3D, Surface3D, Scatter3D, Line3D

    # Pandas Integration
    from .integrations.pandas_integration import DataFramePlotter, VizlyAccessor

    # Animation System
    from .animation.animation_core import Animation, AnimationFrame, animate_chart, create_gif_animation

    # Scientific Visualization
    from .scientific.statistics import qqplot, residual_plot, correlation_matrix, pca_plot, dendrogram
    from .scientific.signal_processing import spectrogram, phase_plot, bode_plot, nyquist_plot, waterfall_plot
    from .scientific.specialized_plots import parallel_coordinates

    # Fine-Grained Control API
    from .control import (
        Axes, StyleManager, LayoutManager, SubplotGrid, FigureManager,
        ColorPalette, LinearLocator, LogFormatter, create_subplot_grid,
        create_figure, tight_layout
    )

    # AI Training Visualization System - NEW ENTERPRISE FEATURE
    from .ai_training import (
        TrainingMonitor, RealTimeTrainingDashboard, EarlyStoppingAnalyzer,
        DistributedTrainingMonitor, HyperparameterOptimizer3D
    )

    ADVANCED_FEATURES_AVAILABLE = True
    AI_TRAINING_AVAILABLE = True
except ImportError as e:
    # Fallbacks for missing advanced features
    ContourChart = None
    BoxPlot = None
    ViolinPlot = None
    Chart3D = None
    Surface3D = None
    Scatter3D = None
    Line3D = None
    DataFramePlotter = None
    VizlyAccessor = None
    Animation = None
    AnimationFrame = None
    animate_chart = None
    create_gif_animation = None
    qqplot = None
    residual_plot = None
    correlation_matrix = None
    pca_plot = None
    dendrogram = None
    spectrogram = None
    phase_plot = None
    bode_plot = None
    nyquist_plot = None
    waterfall_plot = None
    parallel_coordinates = None
    Axes = None
    StyleManager = None
    LayoutManager = None
    SubplotGrid = None
    FigureManager = None
    ColorPalette = None
    LinearLocator = None
    LogFormatter = None
    create_subplot_grid = None
    create_figure = None
    tight_layout = None

    ADVANCED_FEATURES_AVAILABLE = False
    AI_TRAINING_AVAILABLE = False
    import warnings
    warnings.warn(f"Advanced features unavailable: {e}")

    # AI Training fallbacks
    TrainingMonitor = None
    RealTimeTrainingDashboard = None
    EarlyStoppingAnalyzer = None
    DistributedTrainingMonitor = None
    HyperparameterOptimizer3D = None


# Version information
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    "__description__",

    # Core charts
    "LineChart",
    "ScatterChart",
    "BarChart",
    "SurfaceChart",
    "InteractiveSurfaceChart",
    "HeatmapChart",

    # PROFESSIONAL ENGINE (matplotlib-quality)
    "EnhancedLineChart",
    "EnhancedScatterChart",
    "EnhancedBarChart",

    # Advanced Chart Types - NEW
    "ContourChart",
    "BoxPlot",
    "ViolinPlot",
    "Chart3D",
    "Surface3D",
    "Scatter3D",
    "Line3D",

    # Pandas Integration - NEW
    "DataFramePlotter",
    "VizlyAccessor",

    # Animation System - NEW
    "Animation",
    "AnimationFrame",
    "animate_chart",
    "create_gif_animation",

    # Scientific Visualization - NEW
    "qqplot",
    "residual_plot",
    "correlation_matrix",
    "pca_plot",
    "dendrogram",
    "spectrogram",
    "phase_plot",
    "bode_plot",
    "nyquist_plot",
    "waterfall_plot",
    "parallel_coordinates",

    # Fine-Grained Control API - NEW
    "Axes",
    "StyleManager",
    "LayoutManager",
    "SubplotGrid",
    "FigureManager",
    "ColorPalette",
    "LinearLocator",
    "LogFormatter",
    "create_subplot_grid",
    "create_figure",
    "tight_layout",

    # Convenience functions
    "linechart",
    "scatterchart",
    "barchart",

    # Advanced rendering
    "RenderQuality",
    "ColorHDR",
    "Font",

    # Additional charts
    "HistogramChart",
    "BoxChart",
    "BodePlot",
    "StressStrainChart",

    # Financial charts (legacy)
    "CandlestickChart",
    "RSIChart",
    "MACDChart",

    # Data Science charts
    "TimeSeriesChart",
    "DistributionChart",
    "CorrelationChart",
    "FinancialIndicatorChart",

    # Interactive charts
    "InteractiveChart",
    "InteractiveScatterChart",
    "InteractiveLineChart",
    "RealTimeChart",
    "FinancialStreamChart",
    "InteractiveDashboard",
    "DashboardBuilder",

    # Core rendering
    "ImageRenderer",
    "Figure",
    "Canvas",
    "Point",
    "Rectangle",

    # AI Features
    "ai",
    "ai_create",
    "recommend_chart",
    "style_chart",

    # Backend Management
    "backends",
    "set_backend",
    "list_backends",

    # ML/Causal Charts
    "CausalDAGChart",
    "FeatureImportanceChart",
    "SHAPWaterfallChart",
    "ModelPerformanceChart",

    # Exceptions
    "VizlyError",
    "ThemeNotFoundError",
    "ChartValidationError",

    # Unified API functions
    "create_line_chart",
    "create_scatter_chart",
    "create_bar_chart",
    "create_surface_chart",
    "create_heatmap_chart",
    "quick_plot",

    # Package info functions
    "get_info",
    "print_info",
    "version_info",
    "check_dependencies",

    # AI Training Visualization System - ENTERPRISE FEATURE
    "TrainingMonitor",
    "RealTimeTrainingDashboard",
    "EarlyStoppingAnalyzer",
    "DistributedTrainingMonitor",
    "HyperparameterOptimizer3D",

    # Capability flags
    "VIZLYENGINE_AVAILABLE",
    "ADVANCED_FEATURES_AVAILABLE",
    "AI_TRAINING_AVAILABLE",

    # Jupyter/Colab display support
    "SVG",
    "HTML",
    "display",
    "JUPYTER_AVAILABLE",
]

# Unified API functions
def create_line_chart(style='professional', **kwargs):
    """Create a line chart using VizlyEngine.

    Args:
        style: 'professional' (default) or 'enhanced' (matplotlib-like)
        **kwargs: Chart creation arguments

    Returns:
        LineChart instance using VizlyEngine
    """
    if not VIZLYENGINE_AVAILABLE:
        raise ImportError("VizlyEngine not available")

    if style == 'enhanced':
        return EnhancedLineChart(**kwargs)
    else:  # professional
        return LineChart(**kwargs)

def create_scatter_chart(style='professional', **kwargs):
    """Create a scatter chart using VizlyEngine."""
    if not VIZLYENGINE_AVAILABLE:
        raise ImportError("VizlyEngine not available")

    if style == 'enhanced':
        return EnhancedScatterChart(**kwargs)
    else:  # professional
        return ScatterChart(**kwargs)

def create_bar_chart(style='professional', **kwargs):
    """Create a bar chart using VizlyEngine."""
    if not VIZLYENGINE_AVAILABLE:
        raise ImportError("VizlyEngine not available")

    if style == 'enhanced':
        return EnhancedBarChart(**kwargs)
    else:  # professional
        return BarChart(**kwargs)

def create_surface_chart(**kwargs):
    """Create a surface chart (legacy support)."""
    return SurfaceChart(**kwargs)

def create_heatmap_chart(**kwargs):
    """Create a heatmap chart (legacy support)."""
    return HeatmapChart(**kwargs)

# Convenience functions
def quick_plot(x, y, chart_type='line', title="", **kwargs):
    """Quickly create and display a chart.

    Args:
        x, y: Data arrays
        chart_type: 'line', 'scatter', or 'bar'
        title: Chart title
        **kwargs: Additional chart arguments

    Returns:
        Chart instance
    """
    if chart_type == 'line':
        chart = create_line_chart()
        chart.plot(x, y, **kwargs)
    elif chart_type == 'scatter':
        chart = create_scatter_chart()
        if hasattr(chart, 'scatter'):
            chart.scatter(x, y, **kwargs)
        else:
            chart.plot(x, y, **kwargs)
    elif chart_type == 'bar':
        chart = create_bar_chart()
        chart.bar(x, y, **kwargs)
    else:
        raise ValueError(f"Unknown chart type: {chart_type}")

    if title:
        if hasattr(chart, 'set_title'):
            chart.set_title(title)

    # Handle grid and legend for different API styles
    if hasattr(chart, 'grid'):
        # Enhanced API
        chart.grid(True)
    elif hasattr(chart, 'add_axes'):
        # Professional API (though this is now removed)
        pass

    return chart

# Package metadata
def get_info():
    """Get package information."""
    info = {
        'version': __version__,
        'vizlyengine': VIZLYENGINE_AVAILABLE,
        'enhanced_api': VIZLYENGINE_AVAILABLE,  # Enhanced API is part of VizlyEngine
    }
    return info

def print_info():
    """Print package capabilities."""
    info = get_info()
    print(f"OpenFinOps v{info['version']}")
    print("=" * 30)
    print(f"{'✅' if info['vizlyengine'] else '❌'} VizlyEngine: {info['vizlyengine']}")
    print(f"{'✅' if info['enhanced_api'] else '❌'} Enhanced API: {info['enhanced_api']}")

    if info['vizlyengine']:
        print("\n🚀 Professional quality rendering with VizlyEngine!")
    else:
        print("\n⚠️  VizlyEngine not available - limited functionality")

# Library metadata for introspection
__package_info__ = {
    "name": "openfinops",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "license": __license__,
    "python_requires": ">=3.7",
    "dependencies": ["numpy>=1.19.0"],
    "features": [
        "VizlyEngine Professional Rendering",
        "HDR Quality Output with Anti-aliasing",
        "SVG and PNG Export",
        "Jupyter Integration",
        "matplotlib-compatible Enhanced API",
        "Engineering Precision",
    ],
    "chart_types": [
        "Line", "Scatter", "Bar", "Surface", "Heatmap"
    ],
}


def version_info():
    """Get version information as tuple."""
    return tuple(map(int, __version__.split(".")))


def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import numpy

        numpy_version = numpy.__version__
        print(f"✓ NumPy {numpy_version} - OK")
        return True
    except ImportError:
        print("❌ NumPy not found - please install: pip install numpy")
        return False


def demo():
    """Run a quick demonstration of Vizly capabilities."""
    print("🚀 Vizly Demo")
    print("=" * 30)

    # Check dependencies
    if not check_dependencies():
        return

    import numpy as np

    print("Creating sample visualization...")

    try:
        # Create sample data
        x = np.linspace(0, 2 * np.pi, 50)
        y = np.sin(x)

        # Create chart
        chart = LineChart()
        chart.plot(x, y, color="blue", linewidth=2, label="sin(x)")
        chart.set_title("Vizly Demo - Sine Wave")
        chart.set_labels("X", "Y")
        chart.add_legend()
        chart.add_grid(alpha=0.3)

        # Save demo
        chart.save("vizly_demo.png", dpi=300)
        print("✓ Demo chart saved as 'vizly_demo.png'")
        print("🎉 Vizly is working correctly!")
    except Exception as e:
        print(f"⚠️ Demo completed with limited functionality: {e}")
        print("🎯 Basic Vizly structure is available!")


# Initialize default configuration
_config = {"theme": "default", "backend": "auto", "performance": "balanced"}


def configure(theme="default", backend="auto", performance="balanced"):
    """Configure Vizly global settings."""
    global _config
    _config = {"theme": theme, "backend": backend, "performance": performance}
    print(
        f"Vizly configured: theme={theme}, backend={backend}, performance={performance}"
    )


# Jupyter/Colab display support
try:
    from IPython.display import SVG, HTML, display
    JUPYTER_AVAILABLE = True
except ImportError:
    # Fallback for non-Jupyter environments
    class SVG:
        def __init__(self, data=None, filename=None, **kwargs):
            pass

    class HTML:
        def __init__(self, data=None, **kwargs):
            pass

    def display(*args, **kwargs):
        pass

    JUPYTER_AVAILABLE = False

# Welcome message for interactive sessions
def _interactive_welcome():
    """Show welcome message in interactive environments."""
    try:
        # Only show in interactive sessions
        if hasattr(__builtins__, "__IPYTHON__") or hasattr(__builtins__, "get_ipython"):
            print("📊 Vizly loaded - High-performance visualization ready!")
            print("   Try: vizly.demo() for a quick demonstration")
    except Exception:
        pass  # Silently ignore any issues


# Import isolation protection (optional, can be disabled if needed)
try:
    import os
    if os.environ.get("VIZLY_DISABLE_ISOLATION", "").lower() not in ("1", "true", "yes"):
        from .vizly_isolation_config import enable_vizly_isolation
        enable_vizly_isolation()
except ImportError:
    pass  # Isolation config not available

# Show welcome message
_interactive_welcome()
