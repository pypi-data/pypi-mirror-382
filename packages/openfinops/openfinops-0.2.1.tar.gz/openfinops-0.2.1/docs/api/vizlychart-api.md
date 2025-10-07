# VizlyChart API Reference

Complete API reference for the VizlyChart visualization library included in OpenFinOps.

## Table of Contents

- [Basic Charts](#basic-charts)
  - [LineChart](#linechart)
  - [ScatterChart](#scatterchart)
  - [BarChart](#barchart)
  - [HistogramChart](#histogramchart)
- [3D Visualization](#3d-visualization)
  - [Surface3D](#surface3d)
  - [Scatter3D](#scatter3d)
- [Financial Charts](#financial-charts)
  - [CandlestickChart](#candlestickchart)
  - [OHLCChart](#ohlcchart)
- [Advanced Features](#advanced-features)
  - [Real-time Streaming](#real-time-streaming)
  - [Interactive Controls](#interactive-controls)
  - [Themes and Styling](#themes-and-styling)
- [Export and Rendering](#export-and-rendering)

---

## Basic Charts

### LineChart

Create professional line charts for time series and continuous data.

**Location**: `openfinops.vizlychart.charts.LineChart`

```python
from openfinops.vizlychart.charts import LineChart
import numpy as np

# Create chart
chart = LineChart(
    width=800,
    height=600,
    title="Training Loss Over Time"
)

# Plot data
x = np.linspace(0, 100, 1000)
y = np.exp(-x/20) + np.random.randn(1000) * 0.1

chart.plot(
    x, y,
    color='blue',
    linewidth=2,
    label='Training Loss',
    linestyle='-'
)

# Customize
chart.set_title("Model Training Progress")
chart.set_xlabel("Epoch")
chart.set_ylabel("Loss")
chart.add_legend(location='upper right')
chart.add_grid(alpha=0.3)

# Save
chart.save("training_loss.png", dpi=300)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | int | 800 | Chart width in pixels |
| `height` | int | 600 | Chart height in pixels |
| `title` | str | None | Chart title |
| `figsize` | tuple | None | Figure size (width, height) in inches |

#### Methods

##### `plot(x, y, **kwargs)`

Add a line to the chart.

**Parameters:**
- `x` (array-like): X-axis data
- `y` (array-like): Y-axis data
- `color` (str): Line color (name, hex, or RGB)
- `linewidth` (float): Line width in points
- `linestyle` (str): Line style ('-', '--', '-.', ':')
- `label` (str): Label for legend
- `alpha` (float): Transparency (0-1)
- `marker` (str): Marker style ('o', 's', '^', etc.)
- `markersize` (float): Marker size

**Example:**
```python
chart.plot(x, y1, color='#FF5733', linewidth=2.5, label='Series 1')
chart.plot(x, y2, color='blue', linestyle='--', label='Series 2')
```

##### `set_title(title, fontsize=14, fontweight='bold')`

Set the chart title.

##### `set_xlabel(label, fontsize=12)` / `set_ylabel(label, fontsize=12)`

Set axis labels.

##### `set_xlim(xmin, xmax)` / `set_ylim(ymin, ymax)`

Set axis limits.

##### `add_legend(location='best', fontsize=10)`

Add a legend to the chart.

**Location options:** 'best', 'upper right', 'upper left', 'lower right', 'lower left', 'center'

##### `add_grid(alpha=0.3, linestyle='--', color='gray')`

Add gridlines.

##### `save(filename, dpi=300, format=None)`

Save chart to file.

**Supported formats:** PNG, SVG, PDF, JPG

---

### ScatterChart

Create scatter plots for correlation and distribution analysis.

**Location**: `openfinops.vizlychart.charts.ScatterChart`

```python
from openfinops.vizlychart.charts import ScatterChart
import numpy as np

chart = ScatterChart(width=800, height=600)

# Generate data
x = np.random.randn(500)
y = 2 * x + np.random.randn(500) * 0.5
colors = x + y  # Color by value

chart.scatter(
    x, y,
    c=colors,
    s=50,  # Size
    alpha=0.6,
    cmap='viridis',
    edgecolors='black',
    linewidths=0.5
)

chart.set_title("GPU Utilization vs. Cost")
chart.set_xlabel("GPU Usage (%)")
chart.set_ylabel("Cost ($/hour)")
chart.add_colorbar(label="Combined Metric")

chart.save("utilization_vs_cost.png")
```

#### Methods

##### `scatter(x, y, **kwargs)`

Create a scatter plot.

**Parameters:**
- `x`, `y` (array-like): Data coordinates
- `s` (float or array): Marker size(s)
- `c` (color or array): Marker color(s)
- `marker` (str): Marker style
- `alpha` (float): Transparency
- `cmap` (str): Colormap name
- `edgecolors` (color): Edge color
- `linewidths` (float): Edge width

##### `add_colorbar(label=None, orientation='vertical')`

Add a colorbar for color-mapped data.

##### `add_trendline(degree=1, color='red', linestyle='--')`

Add a polynomial trendline.

```python
chart.add_trendline(degree=2, color='red', label='Quadratic Fit')
```

---

### BarChart

Create bar charts for categorical data comparison.

**Location**: `openfinops.vizlychart.charts.BarChart`

```python
from openfinops.vizlychart.charts import BarChart

chart = BarChart()

# Data
providers = ['AWS', 'Azure', 'GCP', 'OpenAI']
costs = [1250, 980, 1100, 450]
colors = ['#FF9900', '#008AD7', '#4285F4', '#10A37F']

chart.bar(
    providers,
    costs,
    color=colors,
    width=0.6,
    edgecolor='black',
    linewidth=1
)

chart.set_title("Monthly Cloud Costs by Provider")
chart.set_ylabel("Cost ($)")
chart.set_xlabel("Provider")

# Add value labels on bars
chart.add_value_labels(format='${:.0f}')

chart.save("cloud_costs.png")
```

#### Methods

##### `bar(x, height, **kwargs)`

Create vertical bars.

**Parameters:**
- `x` (array-like): Bar positions or labels
- `height` (array-like): Bar heights
- `width` (float): Bar width
- `color` (color or list): Bar color(s)
- `edgecolor` (color): Edge color
- `linewidth` (float): Edge width
- `align` (str): Alignment ('center' or 'edge')

##### `barh(y, width, **kwargs)`

Create horizontal bars (same parameters, swapped x/y).

##### `add_value_labels(format='{:.1f}', fontsize=10)`

Add value labels on top of bars.

##### `group_bars(data_dict, group_names)`

Create grouped bar charts.

```python
data = {
    'Compute': [500, 400, 450],
    'Storage': [200, 150, 180],
    'Network': [100, 80, 90]
}

chart.group_bars(data, group_names=['AWS', 'Azure', 'GCP'])
```

---

### HistogramChart

Create histograms for distribution analysis.

**Location**: `openfinops.vizlychart.charts.HistogramChart`

```python
from openfinops.vizlychart.charts import HistogramChart
import numpy as np

chart = HistogramChart()

# Data
latencies = np.random.gamma(2, 50, 10000)

chart.hist(
    latencies,
    bins=50,
    color='skyblue',
    edgecolor='black',
    alpha=0.7,
    density=True  # Normalize to probability density
)

# Add distribution curve
chart.add_kde_curve(color='red', linewidth=2)

chart.set_title("API Response Latency Distribution")
chart.set_xlabel("Latency (ms)")
chart.set_ylabel("Probability Density")

chart.save("latency_distribution.png")
```

#### Methods

##### `hist(data, bins=10, **kwargs)`

Create a histogram.

**Parameters:**
- `data` (array-like): Input data
- `bins` (int or array): Number of bins or bin edges
- `range` (tuple): Data range (min, max)
- `density` (bool): Normalize to probability density
- `cumulative` (bool): Show cumulative distribution
- `histtype` (str): 'bar', 'barstacked', 'step', 'stepfilled'

##### `add_kde_curve(bandwidth='auto', **kwargs)`

Add a kernel density estimate curve.

##### `add_statistics_box(stats=['mean', 'median', 'std'])`

Add a text box with statistics.

```python
chart.add_statistics_box(
    stats=['mean', 'median', 'std', 'min', 'max'],
    location='upper right'
)
```

---

## 3D Visualization

### Surface3D

Create 3D surface plots.

**Location**: `openfinops.vizlychart.charts.Surface3D`

```python
from openfinops.vizlychart.charts import Surface3D
import numpy as np

chart = Surface3D(width=1000, height=800)

# Create mesh
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

chart.plot_surface(
    X, Y, Z,
    cmap='viridis',
    alpha=0.8,
    edgecolor='none'
)

chart.set_title("Cost Landscape Analysis")
chart.set_labels("Parameter 1", "Parameter 2", "Cost")

# Set viewing angle
chart.set_view(elev=30, azim=45)

chart.save("cost_landscape_3d.png")
```

#### Methods

##### `plot_surface(X, Y, Z, **kwargs)`

Create a 3D surface.

**Parameters:**
- `X`, `Y`, `Z` (2D arrays): Mesh coordinates and values
- `cmap` (str): Colormap
- `alpha` (float): Transparency
- `rstride`, `cstride` (int): Row/column stride for mesh
- `edgecolor` (color): Edge color

##### `set_view(elev=30, azim=45)`

Set the viewing angle.

- `elev` (float): Elevation angle (degrees)
- `azim` (float): Azimuthal angle (degrees)

##### `add_contours(Z, levels=10, **kwargs)`

Add contour lines.

---

### Scatter3D

Create 3D scatter plots.

**Location**: `openfinops.vizlychart.charts.Scatter3D`

```python
from openfinops.vizlychart.charts import Scatter3D
import numpy as np

chart = Scatter3D()

# Generate 3D data
n = 500
x = np.random.randn(n)
y = np.random.randn(n)
z = x**2 + y**2 + np.random.randn(n) * 0.1

chart.scatter(
    x, y, z,
    c=z,  # Color by z value
    s=50,
    alpha=0.6,
    cmap='plasma'
)

chart.set_title("Resource Utilization Cluster")
chart.set_labels("CPU", "Memory", "Cost")
chart.add_colorbar(label="Cost Metric")

chart.save("cluster_3d.png")
```

#### Methods

##### `scatter(x, y, z, **kwargs)`

Create 3D scatter plot.

**Parameters:** Similar to 2D scatter with added `z` dimension.

---

## Financial Charts

### CandlestickChart

Create candlestick charts for financial data.

**Location**: `openfinops.vizlychart.charts.CandlestickChart`

```python
from openfinops.vizlychart.charts import CandlestickChart
import pandas as pd

chart = CandlestickChart()

# Load OHLC data
data = pd.DataFrame({
    'date': pd.date_range('2025-01-01', periods=100),
    'open': np.random.randn(100).cumsum() + 100,
    'high': np.random.randn(100).cumsum() + 102,
    'low': np.random.randn(100).cumsum() + 98,
    'close': np.random.randn(100).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, 100)
})

chart.plot_candlestick(
    data,
    up_color='green',
    down_color='red',
    width=0.6
)

# Add volume bars
chart.add_volume(data, alpha=0.3)

# Add moving averages
chart.add_moving_average(data['close'], window=20, color='blue', label='MA20')
chart.add_moving_average(data['close'], window=50, color='orange', label='MA50')

chart.set_title("Cloud Cost Trends")
chart.add_legend()

chart.save("cost_candlestick.png")
```

#### Methods

##### `plot_candlestick(data, **kwargs)`

Plot candlestick chart.

**Parameters:**
- `data` (DataFrame): Must have 'open', 'high', 'low', 'close' columns
- `up_color` (color): Color for up candles
- `down_color` (color): Color for down candles
- `width` (float): Candle width

##### `add_volume(data, alpha=0.3)`

Add volume bars below chart.

##### `add_moving_average(data, window, **kwargs)`

Add moving average line.

##### `add_bollinger_bands(data, window=20, num_std=2)`

Add Bollinger Bands.

---

## Advanced Features

### Real-time Streaming

Stream data to charts in real-time.

```python
from openfinops.vizlychart.streaming import StreamingLineChart
import time

chart = StreamingLineChart(
    max_points=100,  # Keep last 100 points
    update_interval=1000  # Update every 1 second
)

# Start streaming
chart.start()

# Add data points
for i in range(1000):
    timestamp = time.time()
    value = np.sin(i / 10) + np.random.randn() * 0.1

    chart.add_point(timestamp, value)
    time.sleep(0.1)

chart.stop()
```

#### StreamingLineChart Methods

##### `start()`
Start the streaming visualization.

##### `add_point(x, y)`
Add a new data point.

##### `stop()`
Stop streaming and finalize chart.

##### `set_buffer_size(size)`
Set the number of points to keep in buffer.

---

### Interactive Controls

Add interactive controls to charts.

```python
from openfinops.vizlychart.interactive import InteractiveChart

chart = InteractiveChart()

# Add data
chart.plot(x, y)

# Add zoom control
chart.add_zoom_control()

# Add pan control
chart.add_pan_control()

# Add data cursor (crosshairs)
chart.add_cursor(hover=True)

# Add range slider
chart.add_range_slider(axis='x')

# Add click callback
def on_click(event):
    print(f"Clicked at ({event.xdata}, {event.ydata})")

chart.add_click_callback(on_click)

# Display interactive chart
chart.show()
```

---

### Themes and Styling

Apply professional themes.

```python
from openfinops.vizlychart import LineChart
from openfinops.vizlychart.theme import Theme

# Create custom theme
theme = Theme(
    background_color='#FFFFFF',
    text_color='#333333',
    grid_color='#CCCCCC',
    color_palette=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
    font_family='Arial',
    title_fontsize=16,
    label_fontsize=12
)

# Apply theme
chart = LineChart(theme=theme)

# Or use built-in themes
chart.set_theme('dark')  # 'light', 'dark', 'minimal', 'professional'
```

#### Built-in Themes

- **light**: Clean light theme
- **dark**: Dark background theme
- **minimal**: Minimalist design
- **professional**: Corporate style
- **scientific**: Publication-ready
- **vibrant**: Bold colors

---

## Export and Rendering

### Rendering Backends

VizlyChart supports multiple rendering backends:

```python
from openfinops.vizlychart import LineChart

chart = LineChart(backend='svg')  # 'png', 'svg', 'canvas', 'webgl'
```

**Backends:**
- **png**: Raster images (default)
- **svg**: Vector graphics
- **canvas**: HTML5 canvas
- **webgl**: Hardware-accelerated 3D

### Export Methods

##### `save(filename, dpi=300, format=None, transparent=False)`

Save chart to file.

```python
# PNG with high resolution
chart.save("chart.png", dpi=300)

# SVG for scalability
chart.save("chart.svg")

# PDF for printing
chart.save("chart.pdf")

# Transparent background
chart.save("chart.png", transparent=True)
```

##### `to_base64(format='png', dpi=150)`

Export to base64 string for web embedding.

```python
base64_str = chart.to_base64(format='png')
html = f'<img src="data:image/png;base64,{base64_str}" />'
```

##### `to_html(interactive=True)`

Export to standalone HTML.

```python
html = chart.to_html(interactive=True)
with open("chart.html", "w") as f:
    f.write(html)
```

##### `to_json()`

Export chart configuration and data as JSON.

```python
json_data = chart.to_json()
```

---

## Complete Examples

### Cost Dashboard Chart

```python
from openfinops.vizlychart.charts import LineChart, BarChart
from openfinops.vizlychart.rendering import SubplotGrid
import numpy as np
import pandas as pd

# Create subplot grid
grid = SubplotGrid(rows=2, cols=2, figsize=(16, 12))

# 1. Cost Trend (Line Chart)
trend_chart = grid.add_subplot(0, 0)
dates = pd.date_range('2025-01-01', periods=90)
costs = np.cumsum(np.random.randn(90) * 10 + 100)
trend_chart.plot(dates, costs, color='blue', linewidth=2)
trend_chart.set_title("Daily Cost Trend")
trend_chart.set_ylabel("Cost ($)")

# 2. Cost by Provider (Bar Chart)
provider_chart = grid.add_subplot(0, 1)
providers = ['AWS', 'Azure', 'GCP', 'OpenAI']
costs = [2500, 1800, 2100, 600]
provider_chart.bar(providers, costs, color=['#FF9900', '#008AD7', '#4285F4', '#10A37F'])
provider_chart.set_title("Cost by Provider")

# 3. GPU Utilization (Scatter)
util_chart = grid.add_subplot(1, 0)
hours = np.arange(24)
utilization = np.random.rand(24) * 100
util_chart.scatter(hours, utilization, s=100, c=utilization, cmap='RdYlGn')
util_chart.set_title("GPU Utilization by Hour")
util_chart.set_xlabel("Hour of Day")
util_chart.set_ylabel("Utilization (%)")

# 4. Cost Distribution (Histogram)
dist_chart = grid.add_subplot(1, 1)
daily_costs = np.random.gamma(2, 50, 1000)
dist_chart.hist(daily_costs, bins=30, color='skyblue', edgecolor='black')
dist_chart.set_title("Daily Cost Distribution")
dist_chart.set_xlabel("Cost ($)")

# Save dashboard
grid.save("cost_dashboard.png", dpi=300)
```

### Real-time Training Monitor

```python
from openfinops.vizlychart.streaming import StreamingLineChart
from openfinops import LLMObservabilityHub
import time

# Initialize
llm_hub = LLMObservabilityHub()
chart = StreamingLineChart(
    max_points=100,
    title="Real-time Training Loss",
    xlabel="Step",
    ylabel="Loss"
)

chart.start()

# Training loop
for step in range(1000):
    # Simulate training
    loss = 1.0 / (step + 1) + np.random.randn() * 0.01

    # Track with OpenFinOps
    llm_hub.track_training_metrics(
        model_id="llm-v1",
        epoch=1,
        step=step,
        loss=loss
    )

    # Update chart
    chart.add_point(step, loss)

    time.sleep(0.1)

chart.save("training_monitor.mp4", format='video', fps=30)
```

## See Also

- [Observability API](observability-api.md) - Data collection APIs
- [Dashboard API](dashboard-api.md) - Dashboard integration
- [Tutorials](../tutorials/basic-usage.md) - Step-by-step guides
- [Examples](../../examples/README.md) - Code examples
