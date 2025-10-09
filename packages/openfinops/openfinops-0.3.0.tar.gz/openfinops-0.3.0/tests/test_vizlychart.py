"""
Unit tests for VizlyChart visualization library.
"""

import pytest
import numpy as np
from openfinops.vizlychart import LineChart, ScatterChart, BarChart, HistogramChart
from openfinops.vizlychart.charts.chart_3d import Surface3D, Scatter3D


@pytest.mark.unit
@pytest.mark.visualization
class TestVizlyChart:
    """Test suite for VizlyChart library."""

    def test_line_chart_initialization(self):
        """Test LineChart initialization."""
        chart = LineChart()
        assert chart is not None
        assert hasattr(chart, 'plot')

    def test_line_chart_plot(self):
        """Test LineChart plotting."""
        chart = LineChart()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        chart.plot(x, y, label='sin(x)')

        # Verify chart has data series
        assert hasattr(chart, 'line_series')
        assert chart.line_series is not None

    def test_scatter_chart_initialization(self):
        """Test ScatterChart initialization."""
        chart = ScatterChart()
        assert chart is not None
        assert hasattr(chart, 'scatter')

    def test_scatter_chart_plot(self):
        """Test ScatterChart plotting."""
        chart = ScatterChart()
        x = np.random.randn(100)
        y = np.random.randn(100)

        chart.scatter(x, y)

        # Verify chart has data series
        assert hasattr(chart, 'data_series')
        assert chart.data_series is not None

    def test_bar_chart_initialization(self):
        """Test BarChart initialization."""
        chart = BarChart()
        assert chart is not None
        assert hasattr(chart, 'bar')

    def test_bar_chart_plot(self):
        """Test BarChart plotting."""
        chart = BarChart()
        categories = ['A', 'B', 'C', 'D']
        values = [10, 25, 15, 30]

        chart.bar(categories, values)

        # Verify chart has data series
        assert hasattr(chart, 'data_series')
        assert chart.data_series is not None

    def test_histogram_chart(self):
        """Test HistogramChart."""
        chart = HistogramChart()
        data = np.random.normal(0, 1, 1000)

        chart.hist(data, bins=50)

        # Verify chart has data series
        assert hasattr(chart, 'data_series')
        assert chart.data_series is not None

    @pytest.mark.parametrize("chart_type,data_generator", [
        (LineChart, lambda: (np.linspace(0, 10, 50), np.cos(np.linspace(0, 10, 50)))),
        (ScatterChart, lambda: (np.random.randn(50), np.random.randn(50))),
        (BarChart, lambda: (['X', 'Y', 'Z'], [5, 10, 15])),
    ])
    def test_multiple_chart_types(self, chart_type, data_generator):
        """Test multiple chart types with different data."""
        chart = chart_type()
        data = data_generator()

        if chart_type == LineChart:
            chart.plot(data[0], data[1])
        elif chart_type == ScatterChart:
            chart.scatter(data[0], data[1])
        elif chart_type == BarChart:
            chart.bar(data[0], data[1])

        # Verify chart has data series
        assert hasattr(chart, 'data_series')
        assert chart.data_series is not None


@pytest.mark.unit
@pytest.mark.visualization
class TestVizlyChart3D:
    """Test suite for 3D visualizations."""

    def test_surface_3d_initialization(self):
        """Test Surface3D initialization."""
        chart = Surface3D()
        assert chart is not None
        assert hasattr(chart, 'plot_surface')

    def test_surface_3d_plot(self):
        """Test Surface3D plotting."""
        chart = Surface3D()

        x = np.linspace(-5, 5, 30)
        y = np.linspace(-5, 5, 30)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))

        chart.plot_surface(X, Y, Z)

        # Verify chart has data series
        assert hasattr(chart, 'data_series')
        assert chart.data_series is not None

    def test_scatter_3d_initialization(self):
        """Test Scatter3D initialization."""
        chart = Scatter3D()
        assert chart is not None
        assert hasattr(chart, 'scatter')

    def test_scatter_3d_plot(self):
        """Test Scatter3D plotting."""
        chart = Scatter3D()

        x = np.random.randn(100)
        y = np.random.randn(100)
        z = np.random.randn(100)

        chart.scatter(x, y, z)

        # Verify chart has data series
        assert hasattr(chart, 'data_series')
        assert chart.data_series is not None

    def test_surface_3d_mathematical_function(self):
        """Test Surface3D with various mathematical functions."""
        chart = Surface3D()

        x = np.linspace(-2, 2, 25)
        y = np.linspace(-2, 2, 25)
        X, Y = np.meshgrid(x, y)

        # Test with Gaussian function
        Z = np.exp(-(X**2 + Y**2))
        chart.plot_surface(X, Y, Z)

        # Verify chart has data series
        assert hasattr(chart, 'data_series')
        assert chart.data_series is not None

    def test_scatter_3d_with_colors(self):
        """Test Scatter3D with color mapping."""
        chart = Scatter3D()

        n = 200
        x = np.random.randn(n)
        y = np.random.randn(n)
        z = np.random.randn(n)
        colors = np.sqrt(x**2 + y**2 + z**2)  # Color by distance from origin

        chart.scatter(x, y, z, c=colors)

        # Verify chart has data series
        assert hasattr(chart, 'data_series')
        assert chart.data_series is not None


@pytest.mark.unit
@pytest.mark.visualization
class TestChartStyling:
    """Test suite for chart styling and customization."""

    def test_line_chart_styling(self):
        """Test LineChart styling options."""
        chart = LineChart()
        chart.set_title("Test Chart")
        chart.set_labels("X Axis", "Y Axis")

        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        chart.plot(x, y)

        # Verify styling attributes exist
        assert chart.title == "Test Chart"
        assert chart.xlabel == "X Axis"
        assert chart.ylabel == "Y Axis"

    def test_chart_legend(self):
        """Test chart legend functionality."""
        chart = LineChart()
        x = np.linspace(0, 10, 50)

        chart.plot(x, np.sin(x), label='sin')
        chart.plot(x, np.cos(x), label='cos')

        # Verify legend entries added
        assert len(chart.legend_entries) == 2
        legend_labels = [entry['label'] for entry in chart.legend_entries]
        assert 'sin' in legend_labels
        assert 'cos' in legend_labels

    def test_chart_customization(self):
        """Test chart customization options."""
        chart = LineChart()
        chart.set_title("Custom Chart")
        chart.set_style("professional")

        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        chart.plot(x, y)

        # Verify chart is customizable
        assert chart.title == "Custom Chart"
        assert hasattr(chart, 'set_style')
