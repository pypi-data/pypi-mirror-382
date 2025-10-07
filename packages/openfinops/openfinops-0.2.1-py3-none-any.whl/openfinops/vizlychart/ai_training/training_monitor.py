"""
Real-time Training Monitor and Dashboard
=======================================

Interactive, real-time visualization system for AI/ML model training monitoring.
Provides live updates of training metrics, early stopping analysis, and resource utilization.
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



import time
import json
import threading
from typing import Dict, List, Optional, Union, Any, Callable
from collections import defaultdict, deque
import numpy as np

try:
    import websockets
    import asyncio
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

from ..rendering.vizlyengine import ColorHDR
from ..charts.professional_charts import ProfessionalLineChart


class TrainingMetrics:
    """Container for training metrics with efficient storage and retrieval."""

    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.timestamps = deque(maxlen=max_history)
        self.epochs = deque(maxlen=max_history)
        self.metadata = {}

    def log(self, epoch: int, **metrics: float):
        """Log training metrics for an epoch."""
        timestamp = time.time()

        self.epochs.append(epoch)
        self.timestamps.append(timestamp)

        for metric_name, value in metrics.items():
            self.metrics[metric_name].append(float(value))

    def get_metric(self, name: str) -> List[float]:
        """Get all values for a specific metric."""
        return list(self.metrics[name])

    def get_latest(self, name: str) -> Optional[float]:
        """Get the latest value for a metric."""
        if name in self.metrics and len(self.metrics[name]) > 0:
            return self.metrics[name][-1]
        return None

    def get_epochs(self) -> List[int]:
        """Get all epoch numbers."""
        return list(self.epochs)

    def get_metric_names(self) -> List[str]:
        """Get all available metric names."""
        return list(self.metrics.keys())


class TrainingMonitor:
    """
    Comprehensive training monitor with real-time visualization capabilities.
    """

    def __init__(self, update_interval: float = 1.0):
        self.metrics = TrainingMetrics()
        self.update_interval = update_interval
        self.is_monitoring = False
        self.callbacks = []
        self.thresholds = {}

        # Visual customization
        self.color_scheme = {
            'loss': ColorHDR.from_hex('#e74c3c'),
            'accuracy': ColorHDR.from_hex('#27ae60'),
            'val_loss': ColorHDR.from_hex('#c0392b'),
            'val_accuracy': ColorHDR.from_hex('#229954'),
            'learning_rate': ColorHDR.from_hex('#f39c12'),
            'gpu_utilization': ColorHDR.from_hex('#9b59b6'),
            'memory_usage': ColorHDR.from_hex('#34495e')
        }

    def log_metrics(self, epoch: int, **metrics: float):
        """Log training metrics for visualization."""
        self.metrics.log(epoch, **metrics)

        # Check thresholds and trigger callbacks
        self._check_thresholds(epoch, metrics)

        # Trigger update callbacks
        for callback in self.callbacks:
            callback(epoch, metrics)

    def add_threshold(self, metric_name: str, threshold: float,
                     condition: str = 'below', callback: Optional[Callable] = None):
        """Add threshold monitoring for early stopping or alerts."""
        self.thresholds[metric_name] = {
            'threshold': threshold,
            'condition': condition,
            'callback': callback,
            'triggered': False
        }

    def _check_thresholds(self, epoch: int, metrics: Dict[str, float]):
        """Check if any thresholds are triggered."""
        for metric_name, metric_value in metrics.items():
            if metric_name in self.thresholds:
                threshold_config = self.thresholds[metric_name]
                threshold = threshold_config['threshold']
                condition = threshold_config['condition']

                triggered = False
                if condition == 'below' and metric_value < threshold:
                    triggered = True
                elif condition == 'above' and metric_value > threshold:
                    triggered = True

                if triggered and not threshold_config['triggered']:
                    threshold_config['triggered'] = True
                    if threshold_config['callback']:
                        threshold_config['callback'](epoch, metric_name, metric_value)

    def add_callback(self, callback: Callable):
        """Add callback function to be called on metric updates."""
        self.callbacks.append(callback)

    def get_training_summary(self) -> Dict[str, Any]:
        """Get comprehensive training summary."""
        if not self.metrics.epochs:
            return {'status': 'no_data'}

        summary = {
            'total_epochs': len(self.metrics.epochs),
            'current_epoch': self.metrics.epochs[-1] if self.metrics.epochs else 0,
            'metrics': {},
            'training_time': 0,
            'status': 'active' if self.is_monitoring else 'stopped'
        }

        if self.metrics.timestamps:
            summary['training_time'] = self.metrics.timestamps[-1] - self.metrics.timestamps[0]

        # Calculate metric statistics
        for metric_name in self.metrics.get_metric_names():
            values = self.metrics.get_metric(metric_name)
            if values:
                summary['metrics'][metric_name] = {
                    'current': values[-1],
                    'best': min(values) if 'loss' in metric_name else max(values),
                    'worst': max(values) if 'loss' in metric_name else min(values),
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'trend': 'improving' if self._is_improving(values) else 'degrading'
                }

        return summary

    def _is_improving(self, values: List[float], window: int = 10) -> bool:
        """Determine if a metric is improving based on recent trend."""
        if len(values) < window:
            return True

        recent = values[-window:]
        early = values[-2*window:-window] if len(values) >= 2*window else values[:-window]

        if not early:
            return True

        return np.mean(recent) < np.mean(early)  # Assumes lower is better


class RealTimeTrainingDashboard:
    """
    Interactive real-time training dashboard with live updates.
    """

    def __init__(self, monitor: TrainingMonitor, width: int = 1200, height: int = 800):
        self.monitor = monitor
        self.width = width
        self.height = height
        self.charts = {}
        self.is_running = False
        self.server_thread = None

    def create_training_charts(self) -> str:
        """Create comprehensive training visualization charts."""
        epochs = self.monitor.metrics.get_epochs()
        if not epochs:
            return self._create_empty_dashboard()

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Training Monitor - Real-time Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            min-height: 100vh;
        }}

        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}

        .metric-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }}

        .metric-trend {{
            text-align: center;
            font-size: 0.9em;
            opacity: 0.8;
        }}

        .charts-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .chart-panel {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .chart-title {{
            text-align: center;
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 15px;
        }}

        .controls {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }}

        .control-btn {{
            padding: 10px 20px;
            background: rgba(52, 152, 219, 0.8);
            border: none;
            border-radius: 25px;
            color: white;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }}

        .control-btn:hover {{
            background: rgba(52, 152, 219, 1);
            transform: translateY(-2px);
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }}

        .status-active {{
            background: #27ae60;
        }}

        .status-stopped {{
            background: #e74c3c;
        }}

        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}

        #liveCharts {{
            min-height: 400px;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🤖 AI Training Monitor - Real-time Dashboard</h1>
            <p>
                <span class="status-indicator status-active"></span>
                Live Training Monitoring | Last Update: <span id="lastUpdate">{time.strftime('%H:%M:%S')}</span>
            </p>
        </div>

        <div class="controls">
            <button class="control-btn" onclick="toggleMonitoring()" id="monitorBtn">⏸️ Pause Monitoring</button>
            <button class="control-btn" onclick="resetCharts()">🔄 Reset</button>
            <button class="control-btn" onclick="exportData()">💾 Export Data</button>
            <button class="control-btn" onclick="showAnalysis()">📊 Analysis</button>
        </div>

        <div class="metrics-grid" id="metricsGrid">
            <!-- Real-time metrics will be populated here -->
        </div>

        <div class="charts-container">
            <div class="chart-panel">
                <div class="chart-title">📈 Training Loss & Validation Loss</div>
                <div id="lossChart"></div>
            </div>
            <div class="chart-panel">
                <div class="chart-title">🎯 Accuracy Metrics</div>
                <div id="accuracyChart"></div>
            </div>
        </div>

        <div class="chart-panel">
            <div class="chart-title">⚡ Learning Rate & Resource Utilization</div>
            <div id="resourceChart"></div>
        </div>

        <div id="liveCharts">
            <!-- Additional charts will be generated here -->
        </div>
    </div>

    <script>
        let isMonitoring = true;
        let chartData = {self._get_chart_data_json()};
        let updateInterval;

        function updateDashboard() {{
            if (!isMonitoring) return;

            // Update metrics cards
            updateMetricsGrid();

            // Update charts
            updateTrainingCharts();

            // Update timestamp
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
        }}

        function updateMetricsGrid() {{
            const grid = document.getElementById('metricsGrid');
            const summary = {json.dumps(self.monitor.get_training_summary())};

            let html = '';
            if (summary.metrics) {{
                for (const [metricName, metricData] of Object.entries(summary.metrics)) {{
                    const trendIcon = metricData.trend === 'improving' ? '📈' : '📉';
                    const trendColor = metricData.trend === 'improving' ? '#27ae60' : '#e74c3c';

                    html += `
                        <div class="metric-card">
                            <div class="metric-title">${{metricName.replace('_', ' ').toUpperCase()}}</div>
                            <div class="metric-value" style="color: #3498db">
                                ${{metricData.current.toFixed(4)}}
                            </div>
                            <div class="metric-trend" style="color: ${{trendColor}}">
                                ${{trendIcon}} ${{metricData.trend}} | Best: ${{metricData.best.toFixed(4)}}
                            </div>
                        </div>
                    `;
                }}
            }}

            grid.innerHTML = html;
        }}

        function updateTrainingCharts() {{
            // Generate SVG charts using OpenFinOps-style rendering
            updateLossChart();
            updateAccuracyChart();
            updateResourceChart();
        }}

        function updateLossChart() {{
            const epochs = {epochs};
            const lossData = {self.monitor.metrics.get_metric('loss') if 'loss' in self.monitor.metrics.metrics else []};
            const valLossData = {self.monitor.metrics.get_metric('val_loss') if 'val_loss' in self.monitor.metrics.metrics else []};

            const svg = generateLossChartSVG(epochs, lossData, valLossData);
            document.getElementById('lossChart').innerHTML = svg;
        }}

        function updateAccuracyChart() {{
            const epochs = {epochs};
            const accData = {self.monitor.metrics.get_metric('accuracy') if 'accuracy' in self.monitor.metrics.metrics else []};
            const valAccData = {self.monitor.metrics.get_metric('val_accuracy') if 'val_accuracy' in self.monitor.metrics.metrics else []};

            const svg = generateAccuracyChartSVG(epochs, accData, valAccData);
            document.getElementById('accuracyChart').innerHTML = svg;
        }}

        function updateResourceChart() {{
            const epochs = {epochs};
            const lrData = {self.monitor.metrics.get_metric('learning_rate') if 'learning_rate' in self.monitor.metrics.metrics else []};
            const gpuData = {self.monitor.metrics.get_metric('gpu_utilization') if 'gpu_utilization' in self.monitor.metrics.metrics else []};

            const svg = generateResourceChartSVG(epochs, lrData, gpuData);
            document.getElementById('resourceChart').innerHTML = svg;
        }}

        function generateLossChartSVG(epochs, lossData, valLossData) {{
            const width = 400, height = 250;
            const margin = 40;

            let svg = `<svg width="${{width}}" height="${{height}}" xmlns="http://www.w3.org/2000/svg">
                <rect width="${{width}}" height="${{height}}" fill="rgba(255,255,255,0.1)"/>`;

            if (epochs.length === 0 || lossData.length === 0) {{
                svg += `<text x="${{width/2}}" y="${{height/2}}" text-anchor="middle" fill="white" font-size="14">No training data available</text>`;
                svg += '</svg>';
                return svg;
            }}

            const xMin = Math.min(...epochs);
            const xMax = Math.max(...epochs);
            const yMin = Math.min(...lossData, ...(valLossData.length ? valLossData : [Infinity]));
            const yMax = Math.max(...lossData, ...(valLossData.length ? valLossData : [-Infinity]));

            const xScale = (width - 2*margin) / (xMax - xMin || 1);
            const yScale = (height - 2*margin) / (yMax - yMin || 1);

            // Draw training loss
            if (lossData.length > 1) {{
                let path = `<path d="M${{margin + (epochs[0] - xMin) * xScale}},${{height - margin - (lossData[0] - yMin) * yScale}}`;
                for (let i = 1; i < lossData.length; i++) {{
                    path += ` L${{margin + (epochs[i] - xMin) * xScale}},${{height - margin - (lossData[i] - yMin) * yScale}}`;
                }}
                path += `" stroke="#e74c3c" stroke-width="2" fill="none" opacity="0.8"/>`;
                svg += path;
            }}

            // Draw validation loss
            if (valLossData.length > 1) {{
                let path = `<path d="M${{margin + (epochs[0] - xMin) * xScale}},${{height - margin - (valLossData[0] - yMin) * yScale}}`;
                for (let i = 1; i < valLossData.length; i++) {{
                    path += ` L${{margin + (epochs[i] - xMin) * xScale}},${{height - margin - (valLossData[i] - yMin) * yScale}}`;
                }}
                path += `" stroke="#c0392b" stroke-width="2" fill="none" opacity="0.8" stroke-dasharray="5,5"/>`;
                svg += path;
            }}

            // Add axes
            svg += `<line x1="${{margin}}" y1="${{height-margin}}" x2="${{width-margin}}" y2="${{height-margin}}" stroke="white" stroke-width="1" opacity="0.5"/>`;
            svg += `<line x1="${{margin}}" y1="${{margin}}" x2="${{margin}}" y2="${{height-margin}}" stroke="white" stroke-width="1" opacity="0.5"/>`;

            // Add labels
            svg += `<text x="${{width/2}}" y="${{height-10}}" text-anchor="middle" fill="white" font-size="12">Epochs</text>`;
            svg += `<text x="15" y="${{height/2}}" text-anchor="middle" fill="white" font-size="12" transform="rotate(-90, 15, ${{height/2}})">Loss</text>`;

            svg += '</svg>';
            return svg;
        }}

        function generateAccuracyChartSVG(epochs, accData, valAccData) {{
            // Similar structure to loss chart but for accuracy
            const width = 400, height = 250;
            const margin = 40;

            let svg = `<svg width="${{width}}" height="${{height}}" xmlns="http://www.w3.org/2000/svg">
                <rect width="${{width}}" height="${{height}}" fill="rgba(255,255,255,0.1)"/>`;

            if (epochs.length === 0 || accData.length === 0) {{
                svg += `<text x="${{width/2}}" y="${{height/2}}" text-anchor="middle" fill="white" font-size="14">No accuracy data available</text>`;
                svg += '</svg>';
                return svg;
            }}

            const xMin = Math.min(...epochs);
            const xMax = Math.max(...epochs);
            const yMin = Math.min(...accData, ...(valAccData.length ? valAccData : [Infinity]));
            const yMax = Math.max(...accData, ...(valAccData.length ? valAccData : [-Infinity]));

            const xScale = (width - 2*margin) / (xMax - xMin || 1);
            const yScale = (height - 2*margin) / (yMax - yMin || 1);

            // Draw accuracy lines similar to loss chart
            if (accData.length > 1) {{
                let path = `<path d="M${{margin + (epochs[0] - xMin) * xScale}},${{height - margin - (accData[0] - yMin) * yScale}}`;
                for (let i = 1; i < accData.length; i++) {{
                    path += ` L${{margin + (epochs[i] - xMin) * xScale}},${{height - margin - (accData[i] - yMin) * yScale}}`;
                }}
                path += `" stroke="#27ae60" stroke-width="2" fill="none" opacity="0.8"/>`;
                svg += path;
            }}

            // Add axes and labels
            svg += `<line x1="${{margin}}" y1="${{height-margin}}" x2="${{width-margin}}" y2="${{height-margin}}" stroke="white" stroke-width="1" opacity="0.5"/>`;
            svg += `<line x1="${{margin}}" y1="${{margin}}" x2="${{margin}}" y2="${{height-margin}}" stroke="white" stroke-width="1" opacity="0.5"/>`;
            svg += `<text x="${{width/2}}" y="${{height-10}}" text-anchor="middle" fill="white" font-size="12">Epochs</text>`;
            svg += `<text x="15" y="${{height/2}}" text-anchor="middle" fill="white" font-size="12" transform="rotate(-90, 15, ${{height/2}})">Accuracy</text>`;

            svg += '</svg>';
            return svg;
        }}

        function generateResourceChartSVG(epochs, lrData, gpuData) {{
            // Similar structure for resource monitoring
            const width = 800, height = 250;
            const margin = 40;

            let svg = `<svg width="${{width}}" height="${{height}}" xmlns="http://www.w3.org/2000/svg">
                <rect width="${{width}}" height="${{height}}" fill="rgba(255,255,255,0.1)"/>`;

            if (epochs.length === 0) {{
                svg += `<text x="${{width/2}}" y="${{height/2}}" text-anchor="middle" fill="white" font-size="14">No resource data available</text>`;
                svg += '</svg>';
                return svg;
            }}

            // Add resource monitoring visualization here
            svg += `<text x="${{width/2}}" y="${{height/2}}" text-anchor="middle" fill="white" font-size="14">Resource monitoring active</text>`;

            svg += '</svg>';
            return svg;
        }}

        function toggleMonitoring() {{
            isMonitoring = !isMonitoring;
            const btn = document.getElementById('monitorBtn');
            btn.textContent = isMonitoring ? '⏸️ Pause Monitoring' : '▶️ Resume Monitoring';

            const indicator = document.querySelector('.status-indicator');
            indicator.className = `status-indicator ${{isMonitoring ? 'status-active' : 'status-stopped'}}`;
        }}

        function resetCharts() {{
            if (confirm('Are you sure you want to reset all training data?')) {{
                // Reset functionality
                location.reload();
            }}
        }}

        function exportData() {{
            const data = {json.dumps(self.monitor.get_training_summary())};
            const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'training_data.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}

        function showAnalysis() {{
            alert('Advanced training analysis coming soon!');
        }}

        // Initialize dashboard
        updateInterval = setInterval(updateDashboard, 2000);
        updateDashboard();

        console.log('🤖 AI Training Dashboard loaded successfully!');
    </script>
</body>
</html>
        """

        return html_content

    def _create_empty_dashboard(self) -> str:
        """Create empty dashboard when no training data is available."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>AI Training Monitor - Waiting for Data</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .waiting { font-size: 24px; color: #666; }
    </style>
</head>
<body>
    <div class="waiting">
        🤖 AI Training Monitor<br><br>
        Waiting for training data...<br>
        <small>Start logging metrics with monitor.log_metrics()</small>
    </div>
</body>
</html>
        """

    def _get_chart_data_json(self) -> str:
        """Get chart data as JSON string."""
        return json.dumps({
            'epochs': self.monitor.metrics.get_epochs(),
            'metrics': {name: self.monitor.metrics.get_metric(name)
                       for name in self.monitor.metrics.get_metric_names()}
        })

    def _get_metric_color(self, metric_name: str) -> str:
        """Get color for a specific metric."""
        color_map = {
            'loss': '#e74c3c',
            'accuracy': '#27ae60',
            'val_loss': '#c0392b',
            'val_accuracy': '#229954',
            'learning_rate': '#f39c12',
            'gpu_utilization': '#9b59b6'
        }
        return color_map.get(metric_name.lower(), '#3498db')

    def save_dashboard(self, filename: str = 'training_dashboard.html'):
        """Save the dashboard as an HTML file."""
        html_content = self.create_training_charts()
        with open(filename, 'w') as f:
            f.write(html_content)
        return filename

    def show(self, auto_refresh: bool = True):
        """Display the training dashboard."""
        filename = self.save_dashboard()
        print(f"🤖 Training Dashboard saved as: {filename}")
        print("🌐 Open the file in your browser for real-time monitoring")

        if auto_refresh:
            print("🔄 Auto-refresh enabled - dashboard will update every 2 seconds")

        return filename