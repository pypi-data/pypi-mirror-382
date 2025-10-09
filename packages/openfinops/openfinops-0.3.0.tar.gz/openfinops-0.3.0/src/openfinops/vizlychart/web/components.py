"""Interactive web components for browser-based visualization."""

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

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid

import numpy as np

from ..figure import VizlyFigure
from ..core.streaming import DataStream

try:
    import tornado.web
    import tornado.websocket

    HAS_TORNADO = True
except ImportError:
    HAS_TORNADO = False

try:
    import plotly.graph_objects as go
    import plotly.io as pio

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


logger = logging.getLogger(__name__)


@dataclass
class ChartConfig:
    """Configuration for interactive charts."""

    chart_type: str
    title: str = ""
    width: int = 800
    height: int = 600
    background_color: str = "#ffffff"
    show_toolbar: bool = True
    enable_zoom: bool = True
    enable_pan: bool = True
    enable_select: bool = True
    auto_scale: bool = True
    animation_duration: int = 500


@dataclass
class InteractionEvent:
    """Event data for chart interactions."""

    event_type: str  # click, hover, zoom, pan, select
    chart_id: str
    data: Dict[str, Any]
    timestamp: float


class BaseWebComponent(ABC):
    """Abstract base class for web components."""

    def __init__(self, component_id: Optional[str] = None) -> None:
        self.id = component_id or str(uuid.uuid4())
        self.event_handlers: Dict[str, List[Callable]] = {}

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """Convert component to JSON representation."""
        ...

    @abstractmethod
    def to_html(self) -> str:
        """Generate HTML for the component."""
        ...

    def on(self, event_type: str, handler: Callable[[InteractionEvent], None]) -> None:
        """Register event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def emit(self, event: InteractionEvent) -> None:
        """Emit an event to all registered handlers."""
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")


class InteractiveChart(BaseWebComponent):
    """High-performance interactive chart component."""

    def __init__(
        self, config: Optional[ChartConfig] = None, component_id: Optional[str] = None
    ) -> None:
        super().__init__(component_id)
        self.config = config or ChartConfig(chart_type="line")
        self.data_series: List[Dict[str, Any]] = []
        self.layout_options: Dict[str, Any] = {}
        self._real_time_enabled = False
        self._data_stream: Optional[DataStream] = None

    def add_line_series(
        self,
        x: np.ndarray,
        y: np.ndarray,
        name: str = "Series",
        color: Optional[str] = None,
        line_width: float = 2.0,
        line_style: str = "solid",
        marker_style: Optional[str] = None,
    ) -> str:
        """Add a line series to the chart."""
        series_id = str(uuid.uuid4())

        series_data = {
            "id": series_id,
            "type": "line",
            "name": name,
            "x": x.tolist() if isinstance(x, np.ndarray) else x,
            "y": y.tolist() if isinstance(y, np.ndarray) else y,
            "color": color,
            "line_width": line_width,
            "line_style": line_style,
            "marker_style": marker_style,
        }

        self.data_series.append(series_data)
        return series_id

    def add_scatter_series(
        self,
        x: np.ndarray,
        y: np.ndarray,
        name: str = "Scatter",
        color: Optional[str] = None,
        marker_size: float = 5.0,
        marker_style: str = "circle",
    ) -> str:
        """Add a scatter series to the chart."""
        series_id = str(uuid.uuid4())

        series_data = {
            "id": series_id,
            "type": "scatter",
            "name": name,
            "x": x.tolist() if isinstance(x, np.ndarray) else x,
            "y": y.tolist() if isinstance(y, np.ndarray) else y,
            "color": color,
            "marker_size": marker_size,
            "marker_style": marker_style,
        }

        self.data_series.append(series_data)
        return series_id

    def add_bar_series(
        self,
        x: Union[List[str], np.ndarray],
        y: np.ndarray,
        name: str = "Bars",
        color: Optional[str] = None,
        bar_width: float = 0.8,
    ) -> str:
        """Add a bar series to the chart."""
        series_id = str(uuid.uuid4())

        series_data = {
            "id": series_id,
            "type": "bar",
            "name": name,
            "x": x.tolist() if isinstance(x, np.ndarray) else x,
            "y": y.tolist() if isinstance(y, np.ndarray) else y,
            "color": color,
            "bar_width": bar_width,
        }

        self.data_series.append(series_data)
        return series_id

    def add_surface_series(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        name: str = "Surface",
        colorscale: str = "viridis",
        opacity: float = 1.0,
    ) -> str:
        """Add a 3D surface series to the chart."""
        series_id = str(uuid.uuid4())

        series_data = {
            "id": series_id,
            "type": "surface",
            "name": name,
            "x": x.tolist() if isinstance(x, np.ndarray) else x,
            "y": y.tolist() if isinstance(y, np.ndarray) else y,
            "z": z.tolist() if isinstance(z, np.ndarray) else z,
            "colorscale": colorscale,
            "opacity": opacity,
        }

        self.data_series.append(series_data)
        return series_id

    def update_series_data(
        self,
        series_id: str,
        x: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        z: Optional[np.ndarray] = None,
    ) -> None:
        """Update data for an existing series."""
        for series in self.data_series:
            if series["id"] == series_id:
                if x is not None:
                    series["x"] = x.tolist() if isinstance(x, np.ndarray) else x
                if y is not None:
                    series["y"] = y.tolist() if isinstance(y, np.ndarray) else y
                if z is not None:
                    series["z"] = z.tolist() if isinstance(z, np.ndarray) else z
                break

    def set_layout_options(self, **options) -> None:
        """Set layout options for the chart."""
        self.layout_options.update(options)

    def enable_real_time(self, data_stream: DataStream) -> None:
        """Enable real-time data updates."""
        self._real_time_enabled = True
        self._data_stream = data_stream

        # Subscribe to data stream updates
        def on_data_update(source_name: str, data: Dict[str, np.ndarray]) -> None:
            # Update chart data and emit update event
            event = InteractionEvent(
                event_type="data_update",
                chart_id=self.id,
                data={"source": source_name, "data": data},
                timestamp=time.time(),
            )
            self.emit(event)

        data_stream.subscribe(on_data_update)

    def to_json(self) -> Dict[str, Any]:
        """Convert chart to JSON representation."""
        return {
            "id": self.id,
            "type": "interactive_chart",
            "config": asdict(self.config),
            "data_series": self.data_series,
            "layout_options": self.layout_options,
            "real_time_enabled": self._real_time_enabled,
        }

    def to_html(self) -> str:
        """Generate HTML for the interactive chart."""
        if HAS_PLOTLY:
            return self._generate_plotly_html()
        else:
            return self._generate_basic_html()

    def _generate_plotly_html(self) -> str:
        """Generate HTML using Plotly.js."""
        plotly_data = []

        for series in self.data_series:
            if series["type"] == "line":
                trace = go.Scatter(
                    x=series["x"],
                    y=series["y"],
                    mode="lines",
                    name=series["name"],
                    line=dict(color=series["color"], width=series["line_width"]),
                )
            elif series["type"] == "scatter":
                trace = go.Scatter(
                    x=series["x"],
                    y=series["y"],
                    mode="markers",
                    name=series["name"],
                    marker=dict(color=series["color"], size=series["marker_size"]),
                )
            elif series["type"] == "bar":
                trace = go.Bar(
                    x=series["x"],
                    y=series["y"],
                    name=series["name"],
                    marker_color=series["color"],
                )
            elif series["type"] == "surface":
                trace = go.Surface(
                    x=series["x"],
                    y=series["y"],
                    z=series["z"],
                    name=series["name"],
                    colorscale=series["colorscale"],
                    opacity=series["opacity"],
                )
            else:
                continue

            plotly_data.append(trace)

        layout = go.Layout(
            title=self.config.title,
            width=self.config.width,
            height=self.config.height,
            plot_bgcolor=self.config.background_color,
            **self.layout_options,
        )

        fig = go.Figure(data=plotly_data, layout=layout)

        # Generate HTML
        config = {
            "displayModeBar": self.config.show_toolbar,
            "scrollZoom": self.config.enable_zoom,
            "doubleClick": "reset+autosize",
        }

        html = pio.to_html(fig, config=config, div_id=self.id, include_plotlyjs="cdn")
        return html

    def _generate_basic_html(self) -> str:
        """Generate basic HTML with D3.js fallback."""
        return f"""
        <div id="{self.id}" style="width: {self.config.width}px; height: {self.config.height}px;">
            <svg width="100%" height="100%">
                <!-- Basic SVG chart would be rendered here -->
                <text x="50%" y="50%" text-anchor="middle" dy="0.35em">
                    Chart: {self.config.title}
                </text>
            </svg>
        </div>
        <script>
            // Basic JavaScript for interactivity
            const chartData = {json.dumps(self.to_json())};
            console.log('Chart data:', chartData);
        </script>
        """


class WebGLRenderer(BaseWebComponent):
    """High-performance WebGL renderer for large datasets."""

    def __init__(self, canvas_id: Optional[str] = None) -> None:
        super().__init__(canvas_id)
        self.buffers: Dict[str, Any] = {}
        self.shaders: Dict[str, str] = {}
        self.vertex_count = 0

    def add_line_buffer(
        self, vertices: np.ndarray, colors: Optional[np.ndarray] = None
    ) -> str:
        """Add line data to WebGL buffer."""
        buffer_id = str(uuid.uuid4())

        buffer_data = {
            "id": buffer_id,
            "type": "lines",
            "vertices": vertices.astype(np.float32).tolist(),
            "colors": (
                colors.astype(np.float32).tolist() if colors is not None else None
            ),
            "count": len(vertices),
        }

        self.buffers[buffer_id] = buffer_data
        self.vertex_count += len(vertices)
        return buffer_id

    def add_point_buffer(
        self,
        vertices: np.ndarray,
        colors: Optional[np.ndarray] = None,
        sizes: Optional[np.ndarray] = None,
    ) -> str:
        """Add point data to WebGL buffer."""
        buffer_id = str(uuid.uuid4())

        buffer_data = {
            "id": buffer_id,
            "type": "points",
            "vertices": vertices.astype(np.float32).tolist(),
            "colors": (
                colors.astype(np.float32).tolist() if colors is not None else None
            ),
            "sizes": sizes.astype(np.float32).tolist() if sizes is not None else None,
            "count": len(vertices),
        }

        self.buffers[buffer_id] = buffer_data
        self.vertex_count += len(vertices)
        return buffer_id

    def to_json(self) -> Dict[str, Any]:
        """Convert renderer to JSON representation."""
        return {
            "id": self.id,
            "type": "webgl_renderer",
            "buffers": self.buffers,
            "shaders": self.shaders,
            "vertex_count": self.vertex_count,
        }

    def to_html(self) -> str:
        """Generate HTML with WebGL canvas."""
        return f"""
        <canvas id="{self.id}" style="width: 100%; height: 100%;"></canvas>
        <script>
            const rendererData = {json.dumps(self.to_json())};

            // Initialize WebGL context
            const canvas = document.getElementById('{self.id}');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

            if (!gl) {{
                console.error('WebGL not supported');
            }} else {{
                initWebGLRenderer(gl, rendererData);
            }}

            function initWebGLRenderer(gl, data) {{
                // WebGL initialization code
                console.log('Initializing WebGL renderer with', data.vertex_count, 'vertices');

                // Basic vertex shader
                const vertexShaderSource = `
                    attribute vec3 position;
                    attribute vec3 color;
                    varying vec3 vColor;
                    uniform mat4 uMVPMatrix;

                    void main() {{
                        gl_Position = uMVPMatrix * vec4(position, 1.0);
                        vColor = color;
                        gl_PointSize = 2.0;
                    }}
                `;

                // Basic fragment shader
                const fragmentShaderSource = `
                    precision mediump float;
                    varying vec3 vColor;

                    void main() {{
                        gl_FragColor = vec4(vColor, 1.0);
                    }}
                `;

                // Create and compile shaders
                const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
                const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

                // Create program
                const program = createProgram(gl, vertexShader, fragmentShader);
                gl.useProgram(program);

                // Render buffers
                for (const bufferId in data.buffers) {{
                    const buffer = data.buffers[bufferId];
                    renderBuffer(gl, program, buffer);
                }}
            }}

            function createShader(gl, type, source) {{
                const shader = gl.createShader(type);
                gl.shaderSource(shader, source);
                gl.compileShader(shader);

                if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {{
                    console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
                    gl.deleteShader(shader);
                    return null;
                }}

                return shader;
            }}

            function createProgram(gl, vertexShader, fragmentShader) {{
                const program = gl.createProgram();
                gl.attachShader(program, vertexShader);
                gl.attachShader(program, fragmentShader);
                gl.linkProgram(program);

                if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {{
                    console.error('Program linking error:', gl.getProgramInfoLog(program));
                    return null;
                }}

                return program;
            }}

            function renderBuffer(gl, program, buffer) {{
                // Create and bind vertex buffer
                const vertexBuffer = gl.createBuffer();
                gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
                gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(buffer.vertices), gl.STATIC_DRAW);

                // Set up position attribute
                const positionLocation = gl.getAttribLocation(program, 'position');
                gl.enableVertexAttribArray(positionLocation);
                gl.vertexAttribPointer(positionLocation, 3, gl.FLOAT, false, 0, 0);

                // Color buffer if available
                if (buffer.colors) {{
                    const colorBuffer = gl.createBuffer();
                    gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
                    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(buffer.colors), gl.STATIC_DRAW);

                    const colorLocation = gl.getAttribLocation(program, 'color');
                    gl.enableVertexAttribArray(colorLocation);
                    gl.vertexAttribPointer(colorLocation, 3, gl.FLOAT, false, 0, 0);
                }}

                // Set up MVP matrix (identity for now)
                const mvpLocation = gl.getUniformLocation(program, 'uMVPMatrix');
                const identityMatrix = [
                    1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1
                ];
                gl.uniformMatrix4fv(mvpLocation, false, identityMatrix);

                // Draw
                if (buffer.type === 'lines') {{
                    gl.drawArrays(gl.LINES, 0, buffer.count);
                }} else if (buffer.type === 'points') {{
                    gl.drawArrays(gl.POINTS, 0, buffer.count);
                }}
            }}
        </script>
        """


class DashboardComponent(BaseWebComponent):
    """Dashboard component that can contain multiple charts."""

    def __init__(
        self, title: str = "Dashboard", component_id: Optional[str] = None
    ) -> None:
        super().__init__(component_id)
        self.title = title
        self.charts: Dict[str, BaseWebComponent] = {}
        self.layout: Dict[str, Any] = {"type": "grid", "columns": 2}

    def add_chart(
        self, chart: BaseWebComponent, position: Optional[Tuple[int, int]] = None
    ) -> str:
        """Add a chart to the dashboard."""
        chart_id = chart.id
        self.charts[chart_id] = chart

        if position:
            chart.position = position

        return chart_id

    def remove_chart(self, chart_id: str) -> None:
        """Remove a chart from the dashboard."""
        if chart_id in self.charts:
            del self.charts[chart_id]

    def set_layout(self, layout_type: str, **options) -> None:
        """Set dashboard layout."""
        self.layout = {"type": layout_type, **options}

    def to_json(self) -> Dict[str, Any]:
        """Convert dashboard to JSON representation."""
        return {
            "id": self.id,
            "type": "dashboard",
            "title": self.title,
            "layout": self.layout,
            "charts": {
                chart_id: chart.to_json() for chart_id, chart in self.charts.items()
            },
        }

    def to_html(self) -> str:
        """Generate HTML for the dashboard."""
        chart_html = []

        for chart_id, chart in self.charts.items():
            chart_html.append(
                f'<div class="chart-container" id="container-{chart_id}">'
            )
            chart_html.append(chart.to_html())
            chart_html.append("</div>")

        charts_html = "\n".join(chart_html)

        return f"""
        <div id="{self.id}" class="vizly-dashboard">
            <h1>{self.title}</h1>
            <div class="dashboard-content" style="display: grid; grid-template-columns: repeat({self.layout.get('columns', 2)}, 1fr); gap: 20px;">
                {charts_html}
            </div>
        </div>
        <style>
            .vizly-dashboard {{
                font-family: Arial, sans-serif;
                padding: 20px;
            }}
            .chart-container {{
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
        </style>
        """


class ChartWidget(BaseWebComponent):
    """Widget wrapper for embedding charts in web applications."""

    def __init__(self, figure: VizlyFigure, component_id: Optional[str] = None) -> None:
        super().__init__(component_id)
        self.figure = figure
        self.interactive_features = {
            "zoom": True,
            "pan": True,
            "select": True,
            "export": True,
        }

    def enable_feature(self, feature: str, enabled: bool = True) -> None:
        """Enable or disable interactive features."""
        if feature in self.interactive_features:
            self.interactive_features[feature] = enabled

    def to_json(self) -> Dict[str, Any]:
        """Convert widget to JSON representation."""
        # Extract data from matplotlib figure
        chart_data = self._extract_figure_data()

        return {
            "id": self.id,
            "type": "chart_widget",
            "data": chart_data,
            "features": self.interactive_features,
        }

    def _extract_figure_data(self) -> Dict[str, Any]:
        """Extract data from matplotlib figure."""
        data = {"series": []}

        axes = self.figure.axes
        if hasattr(axes, "lines"):
            for line in axes.lines:
                series_data = {
                    "type": "line",
                    "x": line.get_xdata().tolist(),
                    "y": line.get_ydata().tolist(),
                    "label": line.get_label(),
                    "color": line.get_color(),
                    "linewidth": line.get_linewidth(),
                    "linestyle": line.get_linestyle(),
                }
                data["series"].append(series_data)

        if hasattr(axes, "collections"):
            for collection in axes.collections:
                if hasattr(collection, "get_offsets"):
                    # Scatter plot
                    offsets = collection.get_offsets()
                    if len(offsets) > 0:
                        series_data = {
                            "type": "scatter",
                            "x": offsets[:, 0].tolist(),
                            "y": offsets[:, 1].tolist(),
                            "color": collection.get_facecolors().tolist(),
                            "size": collection.get_sizes().tolist(),
                        }
                        data["series"].append(series_data)

        return data

    def to_html(self) -> str:
        """Generate HTML for the widget."""
        return f"""
        <div id="{self.id}" class="vizly-widget">
            <div class="widget-toolbar">
                <button onclick="zoomIn('{self.id}')" {'disabled' if not self.interactive_features['zoom'] else ''}>Zoom In</button>
                <button onclick="zoomOut('{self.id}')" {'disabled' if not self.interactive_features['zoom'] else ''}>Zoom Out</button>
                <button onclick="resetView('{self.id}')" {'disabled' if not self.interactive_features['pan'] else ''}>Reset</button>
                <button onclick="exportChart('{self.id}')" {'disabled' if not self.interactive_features['export'] else ''}>Export</button>
            </div>
            <div class="widget-content">
                <!-- Chart will be rendered here -->
            </div>
        </div>
        <script>
            const widgetData = {json.dumps(self.to_json())};

            function zoomIn(widgetId) {{
                console.log('Zoom in:', widgetId);
                // Implementation for zoom in
            }}

            function zoomOut(widgetId) {{
                console.log('Zoom out:', widgetId);
                // Implementation for zoom out
            }}

            function resetView(widgetId) {{
                console.log('Reset view:', widgetId);
                // Implementation for reset view
            }}

            function exportChart(widgetId) {{
                console.log('Export chart:', widgetId);
                // Implementation for chart export
            }}

            // Initialize widget
            console.log('Widget data:', widgetData);
        </script>
        <style>
            .vizly-widget {{
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }}
            .widget-toolbar {{
                padding: 10px;
                background: #f5f5f5;
                border-bottom: 1px solid #ddd;
            }}
            .widget-toolbar button {{
                margin-right: 5px;
                padding: 5px 10px;
                border: 1px solid #ddd;
                background: white;
                cursor: pointer;
            }}
            .widget-toolbar button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            .widget-content {{
                padding: 10px;
            }}
        </style>
        """
