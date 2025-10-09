"""
Enterprise Performance Dashboard

Real-time performance monitoring dashboard with interactive visualizations
for system health, API performance, and operational metrics.

Features:
- Real-time system metrics visualization
- API performance monitoring and analytics
- Alert management interface
- Performance trend analysis
- Resource utilization forecasting
- Executive summary reports

Enterprise Requirements:
- Multi-tenant dashboard access with role-based views
- Integration with existing enterprise monitoring tools
- Customizable alerting and notification systems
- Historical data analysis and trend reporting
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



import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from ..charts.base import BaseChart
from ..figure import VizlyFigure
from ..charts.line import LineChart
from ..charts.bar import BarChart
from .monitoring import PerformanceMonitor, get_performance_monitor
from .themes import EnterpriseTheme


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    title: str
    widget_type: str  # 'metric', 'chart', 'alert', 'table'
    data_source: str
    refresh_interval: int = 30  # seconds
    size: tuple = (400, 300)  # width, height
    position: tuple = (0, 0)  # x, y
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}


class PerformanceDashboard:
    """Enterprise performance monitoring dashboard"""

    def __init__(self, monitor: Optional[PerformanceMonitor] = None):
        self.monitor = monitor or get_performance_monitor()
        self.widgets = {}
        self.layout_config = {
            'theme': 'enterprise',
            'grid_size': (12, 8),  # 12 columns, 8 rows
            'auto_refresh': True,
            'refresh_interval': 30
        }

        # Initialize default dashboard layout
        self._setup_default_dashboard()

    def _setup_default_dashboard(self):
        """Setup default enterprise dashboard layout"""

        # System Overview Widgets
        self.add_widget(DashboardWidget(
            'system_health', 'System Health Score', 'metric',
            'system_health.health_score', size=(300, 200), position=(0, 0)
        ))

        self.add_widget(DashboardWidget(
            'cpu_usage', 'CPU Usage', 'gauge',
            'system.cpu.usage_percent', size=(300, 200), position=(300, 0)
        ))

        self.add_widget(DashboardWidget(
            'memory_usage', 'Memory Usage', 'gauge',
            'system.memory.usage_percent', size=(300, 200), position=(600, 0)
        ))

        self.add_widget(DashboardWidget(
            'active_alerts', 'Active Alerts', 'alert_list',
            'alerts.active', size=(300, 200), position=(900, 0)
        ))

        # Performance Trends
        self.add_widget(DashboardWidget(
            'cpu_trend', 'CPU Usage Trend', 'line_chart',
            'system.cpu.usage_percent', size=(600, 300), position=(0, 200),
            config={'time_range': '1h', 'show_threshold': True}
        ))

        self.add_widget(DashboardWidget(
            'memory_trend', 'Memory Usage Trend', 'line_chart',
            'system.memory.usage_percent', size=(600, 300), position=(600, 200),
            config={'time_range': '1h', 'show_threshold': True}
        ))

        # API Performance
        self.add_widget(DashboardWidget(
            'api_response_time', 'API Response Time', 'line_chart',
            'api.request.duration', size=(600, 300), position=(0, 500),
            config={'time_range': '1h', 'aggregation': 'avg'}
        ))

        self.add_widget(DashboardWidget(
            'api_request_rate', 'Request Rate', 'line_chart',
            'api.request.count', size=(600, 300), position=(600, 500),
            config={'time_range': '1h', 'aggregation': 'sum'}
        ))

    def add_widget(self, widget: DashboardWidget):
        """Add a widget to the dashboard"""
        self.widgets[widget.widget_id] = widget

    def remove_widget(self, widget_id: str):
        """Remove a widget from the dashboard"""
        if widget_id in self.widgets:
            del self.widgets[widget_id]

    def generate_system_health_chart(self) -> VizlyFigure:
        """Generate system health overview chart"""
        # Get dashboard data
        dashboard_data = self.monitor.get_dashboard_data()
        system_health = dashboard_data['system_health']

        # Create figure with enterprise theme
        fig = VizlyFigure(width=12, height=8)
        theme = EnterpriseTheme()

        # Health score gauge (simulated with bar chart)
        health_score = system_health.get('health_score', 0)
        categories = ['Health Score']
        values = [health_score]
        colors = ['#00c851' if health_score > 80 else '#ffbb33' if health_score > 60 else '#ff4444']

        chart = BarChart(fig)
        chart.plot(categories, values, color=colors[0])
        chart.set_title('System Health Score', fontsize=16, fontweight='bold')
        chart.set_ylabel('Score')
        chart.set_ylim(0, 100)

        # Add health status text
        status = system_health.get('status', 'unknown')
        fig.text(0.5, 0.02, f'Status: {status.title()}',
                ha='center', fontsize=12,
                color=colors[0])

        return fig

    def generate_resource_usage_chart(self) -> VizlyFigure:
        """Generate resource usage trends chart"""
        # Get recent metrics
        dashboard_data = self.monitor.get_dashboard_data()
        metrics = dashboard_data['metrics']

        # Create figure
        fig = VizlyFigure(width=15, height=10)

        # Create subplots for different metrics
        fig.subplots(2, 2, figsize=(15, 10))

        # CPU Usage subplot
        if 'cpu' in metrics and metrics['cpu']:
            cpu_data = metrics['cpu']
            timestamps = [datetime.fromisoformat(m['timestamp']) for m in cpu_data]
            values = [m['value'] for m in cpu_data]

            fig.subplot(2, 2, 1)
            chart = LineChart(fig, bind_to_subplot=True)
            chart.plot(timestamps, values, color='#1f77b4', linewidth=2)
            chart.set_title('CPU Usage %', fontsize=14, fontweight='bold')
            chart.set_ylabel('Usage %')
            chart.set_ylim(0, 100)
            chart.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Warning')
            chart.axhline(y=95, color='red', linestyle='--', alpha=0.7, label='Critical')
            chart.legend()

        # Memory Usage subplot
        if 'memory' in metrics and metrics['memory']:
            memory_data = metrics['memory']
            timestamps = [datetime.fromisoformat(m['timestamp']) for m in memory_data]
            values = [m['value'] for m in memory_data]

            fig.subplot(2, 2, 2)
            chart = LineChart(fig, bind_to_subplot=True)
            chart.plot(timestamps, values, color='#ff7f0e', linewidth=2)
            chart.set_title('Memory Usage %', fontsize=14, fontweight='bold')
            chart.set_ylabel('Usage %')
            chart.set_ylim(0, 100)
            chart.axhline(y=85, color='orange', linestyle='--', alpha=0.7, label='Warning')
            chart.axhline(y=95, color='red', linestyle='--', alpha=0.7, label='Critical')
            chart.legend()

        # Disk Usage subplot
        if 'disk' in metrics and metrics['disk']:
            disk_data = metrics['disk']
            timestamps = [datetime.fromisoformat(m['timestamp']) for m in disk_data]
            values = [m['value'] for m in disk_data]

            fig.subplot(2, 2, 3)
            chart = LineChart(fig, bind_to_subplot=True)
            chart.plot(timestamps, values, color='#2ca02c', linewidth=2)
            chart.set_title('Disk Usage %', fontsize=14, fontweight='bold')
            chart.set_ylabel('Usage %')
            chart.set_ylim(0, 100)
            chart.axhline(y=90, color='orange', linestyle='--', alpha=0.7, label='Warning')
            chart.legend()

        # Summary subplot - Combined view
        fig.subplot(2, 2, 4)
        if all(metrics.get(key) for key in ['cpu', 'memory', 'disk']):
            cpu_latest = metrics['cpu'][-1]['value'] if metrics['cpu'] else 0
            memory_latest = metrics['memory'][-1]['value'] if metrics['memory'] else 0
            disk_latest = metrics['disk'][-1]['value'] if metrics['disk'] else 0

            resources = ['CPU', 'Memory', 'Disk']
            usage = [cpu_latest, memory_latest, disk_latest]
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

            chart = BarChart(fig, bind_to_subplot=True)
            chart.plot(resources, usage, color=colors)
            chart.set_title('Current Resource Usage', fontsize=14, fontweight='bold')
            chart.set_ylabel('Usage %')
            chart.set_ylim(0, 100)
            chart.axhline(y=80, color='orange', linestyle='--', alpha=0.7)

        fig.suptitle('System Resource Monitoring', fontsize=16, fontweight='bold')
        fig.tight_layout()

        return fig

    def generate_api_performance_chart(self) -> VizlyFigure:
        """Generate API performance analytics chart"""
        # Get API performance data
        api_performance = self.monitor.performance_analyzer.analyze_api_performance()

        # Create figure
        fig = VizlyFigure(width=15, height=10)
        fig.subplots(2, 2, figsize=(15, 10))

        # Response Time Distribution
        fig.subplot(2, 2, 1)
        response_times = ['Avg', 'P95', 'P99']
        times = [
            api_performance.get('average_response_time', 0),
            api_performance.get('p95_response_time', 0),
            api_performance.get('p99_response_time', 0)
        ]

        chart = BarChart(fig, bind_to_subplot=True)
        chart.plot(response_times, times, color='#1f77b4')
        chart.set_title('API Response Times', fontsize=14, fontweight='bold')
        chart.set_ylabel('Time (seconds)')

        # Request Rate
        fig.subplot(2, 2, 2)
        rate_data = ['Current Rate']
        rate_values = [api_performance.get('requests_per_minute', 0)]

        chart = BarChart(fig, bind_to_subplot=True)
        chart.plot(rate_data, rate_values, color='#ff7f0e')
        chart.set_title('Request Rate', fontsize=14, fontweight='bold')
        chart.set_ylabel('Requests/minute')

        # Error Rate
        fig.subplot(2, 2, 3)
        error_rate = api_performance.get('error_rate', 0) * 100
        success_rate = 100 - error_rate

        categories = ['Success', 'Error']
        rates = [success_rate, error_rate]
        colors = ['#2ca02c', '#d62728']

        chart = BarChart(fig, bind_to_subplot=True)
        chart.plot(categories, rates, color=colors)
        chart.set_title('Success vs Error Rate', fontsize=14, fontweight='bold')
        chart.set_ylabel('Rate %')
        chart.set_ylim(0, 100)

        # Slowest Endpoints
        fig.subplot(2, 2, 4)
        slowest = api_performance.get('slowest_endpoints', [])
        if slowest:
            endpoints = [ep['endpoint'].split('/')[-1] for ep in slowest[:5]]
            times = [ep['avg_time'] for ep in slowest[:5]]

            chart = BarChart(fig, bind_to_subplot=True)
            chart.plot(endpoints, times, color='#ff7f0e')
            chart.set_title('Slowest Endpoints', fontsize=14, fontweight='bold')
            chart.set_ylabel('Avg Time (s)')
            chart.tick_params(axis='x', rotation=45)

        fig.suptitle('API Performance Analytics', fontsize=16, fontweight='bold')
        fig.tight_layout()

        return fig

    def generate_alerts_overview(self) -> Dict[str, Any]:
        """Generate alerts overview data for dashboard"""
        active_alerts = self.monitor.alert_manager.get_active_alerts()
        alert_history = self.monitor.alert_manager.get_alert_history(hours=24)

        # Categorize alerts by severity
        severity_counts = {'critical': 0, 'warning': 0, 'info': 0}
        for alert in active_alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1

        # Recent alert trends
        alert_trends = []
        for i in range(24):
            hour_start = datetime.now() - timedelta(hours=i+1)
            hour_end = datetime.now() - timedelta(hours=i)
            hour_alerts = [
                alert for alert in alert_history
                if hour_start <= alert.timestamp <= hour_end
            ]
            alert_trends.append({
                'hour': hour_start.strftime('%H:%M'),
                'count': len(hour_alerts)
            })

        return {
            'active_count': len(active_alerts),
            'severity_breakdown': severity_counts,
            'recent_alerts': [alert.to_dict() for alert in active_alerts[:10]],
            'hourly_trends': list(reversed(alert_trends)),
            'total_24h': len(alert_history)
        }

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary for leadership dashboard"""
        dashboard_data = self.monitor.get_dashboard_data()
        system_health = dashboard_data['system_health']
        api_performance = dashboard_data['api_performance']
        alerts_overview = self.generate_alerts_overview()

        # Calculate overall system status
        health_score = system_health.get('health_score', 0)
        if health_score > 90:
            overall_status = 'Excellent'
            status_color = '#00c851'
        elif health_score > 80:
            overall_status = 'Good'
            status_color = '#ffbb33'
        elif health_score > 60:
            overall_status = 'Fair'
            status_color = '#ff8800'
        else:
            overall_status = 'Poor'
            status_color = '#ff4444'

        # Performance summary
        avg_response_time = api_performance.get('average_response_time', 0)
        request_rate = api_performance.get('requests_per_minute', 0)
        error_rate = api_performance.get('error_rate', 0) * 100

        return {
            'generated_at': datetime.now().isoformat(),
            'overall_status': {
                'score': health_score,
                'status': overall_status,
                'color': status_color
            },
            'key_metrics': {
                'avg_response_time': f"{avg_response_time:.3f}s",
                'request_rate': f"{request_rate:.0f}/min",
                'error_rate': f"{error_rate:.2f}%",
                'uptime': '99.9%',  # Would be calculated from actual uptime tracking
                'active_alerts': alerts_overview['active_count']
            },
            'performance_insights': [
                f"System health score: {health_score}/100",
                f"Average API response time: {avg_response_time:.3f} seconds",
                f"Current request rate: {request_rate:.0f} requests per minute",
                f"Error rate: {error_rate:.2f}%",
                f"Active alerts: {alerts_overview['active_count']}"
            ],
            'recommendations': system_health.get('recommendations', []),
            'next_review': (datetime.now() + timedelta(hours=24)).isoformat()
        }

    def export_dashboard_report(self, format: str = 'json', output_path: Optional[str] = None) -> str:
        """Export comprehensive dashboard report"""
        report_data = {
            'report_type': 'performance_dashboard',
            'generated_at': datetime.now().isoformat(),
            'system_health': self.monitor.get_dashboard_data()['system_health'],
            'api_performance': self.monitor.performance_analyzer.analyze_api_performance(),
            'alerts_overview': self.generate_alerts_overview(),
            'executive_summary': self.generate_executive_summary()
        }

        if format == 'json':
            report_content = json.dumps(report_data, indent=2, default=str)
            file_extension = '.json'
        else:
            # Default to JSON if unsupported format
            report_content = json.dumps(report_data, indent=2, default=str)
            file_extension = '.json'

        if output_path:
            output_file = Path(output_path)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Path(f'vizly_dashboard_report_{timestamp}{file_extension}')

        output_file.write_text(report_content)
        return str(output_file)

    def get_widget_data(self, widget_id: str) -> Dict[str, Any]:
        """Get data for a specific dashboard widget"""
        if widget_id not in self.widgets:
            return {'error': 'Widget not found'}

        widget = self.widgets[widget_id]

        # Route to appropriate data source
        if widget.data_source == 'system_health.health_score':
            dashboard_data = self.monitor.get_dashboard_data()
            return {
                'value': dashboard_data['system_health'].get('health_score', 0),
                'status': dashboard_data['system_health'].get('status', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
        elif widget.data_source in ['system.cpu.usage_percent', 'system.memory.usage_percent', 'system.disk.usage_percent']:
            metrics = self.monitor.metrics_collector.get_metrics(widget.data_source)
            if metrics:
                latest = metrics[-1]
                return {
                    'value': latest.value,
                    'timestamp': latest.timestamp.isoformat(),
                    'historical': [{'timestamp': m.timestamp.isoformat(), 'value': m.value} for m in metrics[-20:]]
                }
        elif widget.data_source == 'alerts.active':
            return self.generate_alerts_overview()

        return {'error': 'Data source not implemented'}

    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get complete dashboard configuration"""
        return {
            'layout': self.layout_config,
            'widgets': {wid: {
                'id': widget.widget_id,
                'title': widget.title,
                'type': widget.widget_type,
                'data_source': widget.data_source,
                'size': widget.size,
                'position': widget.position,
                'config': widget.config
            } for wid, widget in self.widgets.items()}
        }


# Dashboard factory functions
def create_system_admin_dashboard() -> PerformanceDashboard:
    """Create dashboard optimized for system administrators"""
    dashboard = PerformanceDashboard()

    # Add technical widgets
    dashboard.add_widget(DashboardWidget(
        'process_count', 'Active Processes', 'metric',
        'system.process.count', size=(200, 150), position=(0, 600)
    ))

    dashboard.add_widget(DashboardWidget(
        'network_io', 'Network I/O', 'line_chart',
        'system.network.bytes_total', size=(400, 300), position=(200, 600)
    ))

    return dashboard


def create_executive_dashboard() -> PerformanceDashboard:
    """Create dashboard optimized for executives"""
    dashboard = PerformanceDashboard()

    # Simplified executive view
    executive_widgets = ['system_health', 'active_alerts']
    for widget_id in list(dashboard.widgets.keys()):
        if widget_id not in executive_widgets:
            dashboard.remove_widget(widget_id)

    # Add executive summary widget
    dashboard.add_widget(DashboardWidget(
        'executive_summary', 'Executive Summary', 'summary',
        'executive.summary', size=(800, 400), position=(0, 200)
    ))

    return dashboard


def create_api_dashboard() -> PerformanceDashboard:
    """Create dashboard focused on API performance"""
    dashboard = PerformanceDashboard()

    # Remove system widgets, focus on API
    for widget_id in ['cpu_trend', 'memory_trend']:
        if widget_id in dashboard.widgets:
            dashboard.remove_widget(widget_id)

    # Add API-specific widgets
    dashboard.add_widget(DashboardWidget(
        'endpoint_errors', 'Endpoint Errors', 'table',
        'api.errors.by_endpoint', size=(600, 300), position=(0, 200)
    ))

    dashboard.add_widget(DashboardWidget(
        'user_sessions', 'Active User Sessions', 'metric',
        'api.sessions.active', size=(300, 200), position=(900, 200)
    ))

    return dashboard