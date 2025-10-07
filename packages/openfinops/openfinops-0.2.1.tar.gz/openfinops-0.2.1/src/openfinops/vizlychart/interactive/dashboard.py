"""
Interactive Dashboard and Web Components
=======================================

Provides web-based interactive dashboards and chart containers.
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

import json
import warnings
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import numpy as np

try:
    import tornado.web
    import tornado.ioloop
    import tornado.websocket
    HAS_TORNADO = True
except ImportError:
    HAS_TORNADO = False

try:
    import ipywidgets as ipw
    from IPython.display import display, HTML
    HAS_IPYWIDGETS = True
except ImportError:
    HAS_IPYWIDGETS = False

from ..exceptions import VizlyError


class ChartContainer:
    """Container for managing multiple interactive charts."""

    def __init__(self, layout: str = 'grid'):
        self.charts = {}
        self.layout = layout
        self.container_id = f"vizly_container_{id(self)}"

    def add_chart(
        self,
        chart_id: str,
        chart,
        position: Optional[Dict[str, Any]] = None
    ) -> 'ChartContainer':
        """Add a chart to the container."""
        chart_config = {
            'chart': chart,
            'position': position or {},
            'visible': True,
            'interactive': True
        }

        self.charts[chart_id] = chart_config
        return self

    def set_layout(self, layout: str, **layout_kwargs) -> 'ChartContainer':
        """Set container layout: 'grid', 'tabs', 'split', 'custom'."""
        self.layout = layout
        self.layout_kwargs = layout_kwargs
        return self

    def create_html_dashboard(self) -> str:
        """Generate HTML dashboard with interactive charts."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vizly Interactive Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart-container {{
                    border: 1px solid #ddd;
                    margin: 10px;
                    padding: 10px;
                    border-radius: 5px;
                }}
                .dashboard-header {{
                    text-align: center;
                    color: #333;
                    margin-bottom: 20px;
                }}
                .grid-layout {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 20px;
                }}
                .tab-container {{
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                .tab-buttons {{
                    background-color: #f1f1f1;
                    padding: 0;
                    margin: 0;
                }}
                .tab-button {{
                    background-color: #f1f1f1;
                    border: none;
                    padding: 10px 20px;
                    cursor: pointer;
                    font-size: 16px;
                }}
                .tab-button.active {{
                    background-color: #ccc;
                }}
                .tab-content {{
                    padding: 20px;
                    display: none;
                }}
                .tab-content.active {{
                    display: block;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>🚀 Vizly Interactive Dashboard</h1>
                <p>Real-time data visualization and analytics</p>
            </div>

            {content}

            <script>
                // Interactive features
                {javascript}
            </script>
        </body>
        </html>
        """

        if self.layout == 'grid':
            content = self._create_grid_layout()
        elif self.layout == 'tabs':
            content = self._create_tab_layout()
        elif self.layout == 'split':
            content = self._create_split_layout()
        else:
            content = self._create_custom_layout()

        javascript = self._create_javascript()

        return html_template.format(content=content, javascript=javascript)

    def _create_grid_layout(self) -> str:
        """Create grid layout HTML."""
        html = '<div class="grid-layout">'

        for chart_id, chart_config in self.charts.items():
            chart_html = self._chart_to_html(chart_id, chart_config['chart'])
            html += f'''
            <div class="chart-container" id="{chart_id}">
                <h3>{chart_id.replace('_', ' ').title()}</h3>
                {chart_html}
            </div>
            '''

        html += '</div>'
        return html

    def _create_tab_layout(self) -> str:
        """Create tabbed layout HTML."""
        html = '<div class="tab-container">'

        # Tab buttons
        html += '<div class="tab-buttons">'
        for i, chart_id in enumerate(self.charts.keys()):
            active_class = 'active' if i == 0 else ''
            html += f'''
            <button class="tab-button {active_class}"
                    onclick="openTab(event, '{chart_id}')">
                {chart_id.replace('_', ' ').title()}
            </button>
            '''
        html += '</div>'

        # Tab content
        for i, (chart_id, chart_config) in enumerate(self.charts.items()):
            active_class = 'active' if i == 0 else ''
            chart_html = self._chart_to_html(chart_id, chart_config['chart'])
            html += f'''
            <div id="{chart_id}" class="tab-content {active_class}">
                {chart_html}
            </div>
            '''

        html += '</div>'
        return html

    def _create_split_layout(self) -> str:
        """Create split pane layout."""
        html = '<div style="display: flex; height: 600px;">'

        for i, (chart_id, chart_config) in enumerate(self.charts.items()):
            width = f"{100 / len(self.charts)}%"
            chart_html = self._chart_to_html(chart_id, chart_config['chart'])
            html += f'''
            <div style="width: {width}; border-right: 1px solid #ddd; padding: 10px;">
                <h3>{chart_id.replace('_', ' ').title()}</h3>
                {chart_html}
            </div>
            '''

        html += '</div>'
        return html

    def _create_custom_layout(self) -> str:
        """Create custom layout based on position specifications."""
        html = '<div style="position: relative; height: 800px;">'

        for chart_id, chart_config in self.charts.items():
            position = chart_config.get('position', {})
            style = self._position_to_css(position)
            chart_html = self._chart_to_html(chart_id, chart_config['chart'])

            html += f'''
            <div style="{style}" class="chart-container">
                <h3>{chart_id.replace('_', ' ').title()}</h3>
                {chart_html}
            </div>
            '''

        html += '</div>'
        return html

    def _chart_to_html(self, chart_id: str, chart) -> str:
        """Convert chart to HTML representation."""
        # For now, create a placeholder that would contain the chart
        # In a full implementation, this would export the chart as SVG or use Plot.ly
        return f'''
        <div id="chart_{chart_id}" style="width: 100%; height: 400px;
             border: 1px dashed #ccc; display: flex; align-items: center;
             justify-content: center; background-color: #f9f9f9;">
            <div style="text-align: center;">
                <h4>📊 {chart_id.replace('_', ' ').title()}</h4>
                <p>Interactive chart would be rendered here</p>
                <button onclick="refreshChart('{chart_id}')">🔄 Refresh</button>
            </div>
        </div>
        '''

    def _position_to_css(self, position: Dict[str, Any]) -> str:
        """Convert position dict to CSS styles."""
        styles = ["position: absolute;"]

        if 'left' in position:
            styles.append(f"left: {position['left']}px;")
        if 'top' in position:
            styles.append(f"top: {position['top']}px;")
        if 'width' in position:
            styles.append(f"width: {position['width']}px;")
        if 'height' in position:
            styles.append(f"height: {position['height']}px;")

        return " ".join(styles)

    def _create_javascript(self) -> str:
        """Create JavaScript for interactivity."""
        return """
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].classList.remove("active");
            }
            tablinks = document.getElementsByClassName("tab-button");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].classList.remove("active");
            }
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }

        function refreshChart(chartId) {
            console.log('Refreshing chart:', chartId);
            // Chart refresh logic would go here
            alert('Chart ' + chartId + ' refreshed!');
        }

        // WebSocket connection for real-time updates
        function connectWebSocket() {
            const ws = new WebSocket('ws://localhost:8888/ws');

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateChart(data.chart_id, data.data);
            };

            ws.onopen = function(event) {
                console.log('WebSocket connected');
            };

            ws.onclose = function(event) {
                console.log('WebSocket disconnected');
                // Attempt to reconnect
                setTimeout(connectWebSocket, 5000);
            };
        }

        function updateChart(chartId, data) {
            console.log('Updating chart:', chartId, data);
            // Chart update logic would go here
        }

        // Initialize WebSocket connection
        // connectWebSocket();
        """

    def save_dashboard(self, filename: str) -> None:
        """Save dashboard as HTML file."""
        html_content = self.create_html_dashboard()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def serve_dashboard(self, port: int = 8888) -> None:
        """Serve dashboard as web application."""
        if not HAS_TORNADO:
            warnings.warn("Tornado required for web dashboard serving")
            return

        dashboard_html = self.create_html_dashboard()

        class MainHandler(tornado.web.RequestHandler):
            def get(self):
                self.write(dashboard_html)

        class WebSocketHandler(tornado.websocket.WebSocketHandler):
            def open(self):
                print("WebSocket opened")

            def on_message(self, message):
                # Echo message back (placeholder)
                self.write_message(f"Echo: {message}")

            def on_close(self):
                print("WebSocket closed")

        app = tornado.web.Application([
            (r"/", MainHandler),
            (r"/ws", WebSocketHandler),
        ])

        app.listen(port)
        print(f"🌐 Dashboard server started at http://localhost:{port}")
        tornado.ioloop.IOLoop.current().start()


class InteractiveDashboard:
    """Advanced interactive dashboard with real-time capabilities."""

    def __init__(self, title: str = "Vizly Dashboard"):
        self.title = title
        self.containers = {}
        self.real_time_charts = {}
        self.data_sources = {}

    def create_container(
        self,
        container_id: str,
        layout: str = 'grid'
    ) -> ChartContainer:
        """Create a new chart container."""
        container = ChartContainer(layout)
        self.containers[container_id] = container
        return container

    def add_real_time_chart(
        self,
        chart_id: str,
        chart,
        data_source: Optional[Any] = None
    ) -> None:
        """Add real-time chart to dashboard."""
        self.real_time_charts[chart_id] = chart
        if data_source:
            self.data_sources[chart_id] = data_source

    def create_jupyter_dashboard(self) -> None:
        """Create dashboard for Jupyter environment."""
        if not HAS_IPYWIDGETS:
            warnings.warn("ipywidgets required for Jupyter dashboard")
            return

        # Create tabs for different containers
        tab_contents = []
        tab_titles = []

        for container_id, container in self.containers.items():
            # Create output widgets for charts
            chart_outputs = []
            for chart_id, chart_config in container.charts.items():
                output = ipw.Output()
                with output:
                    chart_config['chart'].show()
                chart_outputs.append(output)

            # Layout charts in container
            if container.layout == 'grid':
                # Create grid layout
                if len(chart_outputs) == 1:
                    container_widget = chart_outputs[0]
                elif len(chart_outputs) == 2:
                    container_widget = ipw.HBox(chart_outputs)
                else:
                    # Create 2x2 grid or similar
                    rows = []
                    for i in range(0, len(chart_outputs), 2):
                        row = chart_outputs[i:i+2]
                        rows.append(ipw.HBox(row))
                    container_widget = ipw.VBox(rows)
            else:
                container_widget = ipw.VBox(chart_outputs)

            tab_contents.append(container_widget)
            tab_titles.append(container_id.replace('_', ' ').title())

        # Create tabbed interface
        if tab_contents:
            tabs = ipw.Tab(children=tab_contents)
            for i, title in enumerate(tab_titles):
                tabs.set_title(i, title)

            # Add dashboard header
            header = ipw.HTML(f"""
            <div style="text-align: center; padding: 20px;">
                <h1>🚀 {self.title}</h1>
                <p>Interactive Data Visualization Dashboard</p>
            </div>
            """)

            dashboard = ipw.VBox([header, tabs])
            display(dashboard)

    def export_to_web(self, output_dir: str = "dashboard_output") -> None:
        """Export dashboard to standalone web application."""
        import os

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate main dashboard HTML
        main_container = list(self.containers.values())[0] if self.containers else ChartContainer()
        dashboard_html = main_container.create_html_dashboard()

        # Save main HTML
        with open(os.path.join(output_dir, 'index.html'), 'w') as f:
            f.write(dashboard_html)

        # Create additional assets
        css_content = """
        /* Enhanced Dashboard Styles */
        .dashboard-enhanced {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .chart-container-enhanced {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin: 15px;
            padding: 20px;
            transition: transform 0.3s ease;
        }

        .chart-container-enhanced:hover {
            transform: translateY(-5px);
        }
        """

        with open(os.path.join(output_dir, 'styles.css'), 'w') as f:
            f.write(css_content)

        # Create configuration file
        config = {
            'title': self.title,
            'containers': list(self.containers.keys()),
            'real_time_charts': list(self.real_time_charts.keys()),
            'created': datetime.now().isoformat()
        }

        with open(os.path.join(output_dir, 'config.json'), 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Dashboard exported to: {output_dir}")
        print(f"🌐 Open {output_dir}/index.html in your browser")


class DashboardBuilder:
    """Builder pattern for creating complex dashboards."""

    def __init__(self):
        self.dashboard = InteractiveDashboard()
        self.current_container = None

    def set_title(self, title: str) -> 'DashboardBuilder':
        """Set dashboard title."""
        self.dashboard.title = title
        return self

    def add_container(
        self,
        container_id: str,
        layout: str = 'grid'
    ) -> 'DashboardBuilder':
        """Add new container and make it current."""
        self.current_container = self.dashboard.create_container(container_id, layout)
        return self

    def add_chart(
        self,
        chart_id: str,
        chart,
        position: Optional[Dict[str, Any]] = None
    ) -> 'DashboardBuilder':
        """Add chart to current container."""
        if self.current_container:
            self.current_container.add_chart(chart_id, chart, position)
        return self

    def add_real_time_chart(
        self,
        chart_id: str,
        chart,
        data_source: Optional[Any] = None
    ) -> 'DashboardBuilder':
        """Add real-time chart."""
        self.dashboard.add_real_time_chart(chart_id, chart, data_source)
        return self

    def build(self) -> InteractiveDashboard:
        """Build and return the dashboard."""
        return self.dashboard

    def build_and_serve(self, port: int = 8888) -> None:
        """Build dashboard and serve it."""
        dashboard = self.build()
        if dashboard.containers:
            main_container = list(dashboard.containers.values())[0]
            main_container.serve_dashboard(port)

    def build_and_export(self, output_dir: str = "dashboard_output") -> None:
        """Build dashboard and export to files."""
        dashboard = self.build()
        dashboard.export_to_web(output_dir)