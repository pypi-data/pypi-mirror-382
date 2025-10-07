"""
Enterprise Performance Dashboard Web Server

Real-time web-based dashboard for monitoring Vizly Enterprise performance,
system health, and operational metrics with live updates and interactive charts.

Features:
- Real-time dashboard with WebSocket updates
- Interactive charts and metrics visualization
- Role-based dashboard access and customization
- Alert management and notification interface
- Performance analytics and trend analysis
- Export capabilities for reports and data

Enterprise Requirements:
- Secure authentication and authorization
- Scalable real-time updates for multiple concurrent users
- Integration with existing enterprise monitoring infrastructure
- Customizable dashboards for different user roles
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



import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import base64
import io

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from .monitoring import PerformanceMonitor, get_performance_monitor
from .dashboard import PerformanceDashboard, create_system_admin_dashboard, create_executive_dashboard, create_api_dashboard
from .security import EnterpriseSecurityManager


class DashboardWebSocketManager:
    """Manage WebSocket connections for real-time dashboard updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}
        self.dashboard_subscriptions: Dict[str, List[str]] = {}  # user_id -> dashboard_ids

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection and register user"""
        await websocket.accept()
        self.active_connections.append(websocket)

        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)

        logging.info(f"User {user_id} connected to dashboard WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logging.info(f"User {user_id} disconnected from dashboard WebSocket")

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections for a specific user"""
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logging.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected users"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logging.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

    def subscribe_to_dashboard(self, user_id: str, dashboard_id: str):
        """Subscribe user to dashboard updates"""
        if user_id not in self.dashboard_subscriptions:
            self.dashboard_subscriptions[user_id] = []
        if dashboard_id not in self.dashboard_subscriptions[user_id]:
            self.dashboard_subscriptions[user_id].append(dashboard_id)

    def unsubscribe_from_dashboard(self, user_id: str, dashboard_id: str):
        """Unsubscribe user from dashboard updates"""
        if user_id in self.dashboard_subscriptions:
            if dashboard_id in self.dashboard_subscriptions[user_id]:
                self.dashboard_subscriptions[user_id].remove(dashboard_id)


class DashboardServer:
    """Enterprise dashboard web server with real-time updates"""

    def __init__(self, performance_monitor: Optional[PerformanceMonitor] = None,
                 security_manager: Optional[EnterpriseSecurityManager] = None,
                 config: Optional[Dict] = None):
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for dashboard server. Install with: pip install fastapi uvicorn")

        self.performance_monitor = performance_monitor or get_performance_monitor()
        self.security_manager = security_manager
        self.config = config or {}

        # Initialize FastAPI app
        self.app = FastAPI(
            title="Vizly Enterprise Dashboard",
            description="Real-time performance monitoring dashboard",
            version="1.0.0"
        )

        # WebSocket manager
        self.websocket_manager = DashboardWebSocketManager()

        # Dashboard instances
        self.dashboards = {
            'system_admin': create_system_admin_dashboard(),
            'executive': create_executive_dashboard(),
            'api_performance': create_api_dashboard()
        }

        # Security
        self.security = HTTPBearer(auto_error=False) if security_manager else None

        # Setup routes
        self._setup_routes()

        # Background tasks
        self.update_task = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _setup_routes(self):
        """Setup FastAPI routes for dashboard"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Serve main dashboard page"""
            return self._get_dashboard_html()

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "dashboard_types": list(self.dashboards.keys())
            }

        @self.app.get("/api/dashboard/{dashboard_type}")
        async def get_dashboard_data(dashboard_type: str, user: Optional[str] = Depends(self._get_current_user)):
            """Get dashboard data for specific dashboard type"""
            if dashboard_type not in self.dashboards:
                raise HTTPException(status_code=404, detail="Dashboard not found")

            dashboard = self.dashboards[dashboard_type]
            return dashboard.get_dashboard_config()

        @self.app.get("/api/metrics/live")
        async def get_live_metrics(user: Optional[str] = Depends(self._get_current_user)):
            """Get current live metrics"""
            return self.performance_monitor.get_dashboard_data()

        @self.app.get("/api/charts/{chart_type}")
        async def get_dashboard_chart(chart_type: str, user: Optional[str] = Depends(self._get_current_user)):
            """Generate and return dashboard chart as base64 encoded image"""
            dashboard = self.dashboards.get('system_admin')

            try:
                if chart_type == 'system_health':
                    fig = dashboard.generate_system_health_chart()
                elif chart_type == 'resource_usage':
                    fig = dashboard.generate_resource_usage_chart()
                elif chart_type == 'api_performance':
                    fig = dashboard.generate_api_performance_chart()
                else:
                    raise HTTPException(status_code=404, detail="Chart type not found")

                # Convert figure to base64
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

                return {
                    "chart_type": chart_type,
                    "image": f"data:image/png;base64,{img_base64}",
                    "generated_at": datetime.now().isoformat()
                }

            except Exception as e:
                self.logger.error(f"Error generating chart {chart_type}: {e}")
                raise HTTPException(status_code=500, detail="Chart generation failed")

        @self.app.get("/api/alerts")
        async def get_alerts(user: Optional[str] = Depends(self._get_current_user)):
            """Get current alerts"""
            dashboard = self.dashboards.get('system_admin')
            return dashboard.generate_alerts_overview()

        @self.app.get("/api/executive/summary")
        async def get_executive_summary(user: Optional[str] = Depends(self._get_current_user)):
            """Get executive summary"""
            dashboard = self.dashboards.get('executive')
            return dashboard.generate_executive_summary()

        @self.app.post("/api/dashboard/{dashboard_type}/export")
        async def export_dashboard_report(dashboard_type: str, format: str = "json",
                                        user: Optional[str] = Depends(self._get_current_user)):
            """Export dashboard report"""
            if dashboard_type not in self.dashboards:
                raise HTTPException(status_code=404, detail="Dashboard not found")

            dashboard = self.dashboards[dashboard_type]
            report_path = dashboard.export_dashboard_report(format=format)

            return {
                "export_format": format,
                "file_path": report_path,
                "generated_at": datetime.now().isoformat()
            }

        @self.app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket endpoint for real-time updates"""
            await self.websocket_manager.connect(websocket, user_id)
            try:
                while True:
                    # Keep connection alive and handle client messages
                    message = await websocket.receive_text()
                    data = json.loads(message)

                    if data.get('type') == 'subscribe':
                        dashboard_id = data.get('dashboard_id')
                        if dashboard_id:
                            self.websocket_manager.subscribe_to_dashboard(user_id, dashboard_id)

                    elif data.get('type') == 'unsubscribe':
                        dashboard_id = data.get('dashboard_id')
                        if dashboard_id:
                            self.websocket_manager.unsubscribe_from_dashboard(user_id, dashboard_id)

            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket, user_id)

    async def _get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
        """Get current authenticated user"""
        if not self.security_manager or not credentials:
            return "anonymous"  # Allow anonymous access for demo

        try:
            # Validate JWT token
            payload = self.security_manager.decode_jwt_token(credentials.credentials)
            return payload.get('user_id', 'unknown')
        except Exception as e:
            self.logger.warning(f"Authentication failed: {e}")
            return "anonymous"

    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML page"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vizly Enterprise Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            overflow-x: hidden;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .header h1 {
            color: #2c3e50;
            font-size: 1.8rem;
            font-weight: 700;
        }

        .header .subtitle {
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-top: 0.2rem;
        }

        .dashboard-container {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }

        .metric-card h3 {
            color: #2c3e50;
            margin-bottom: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .metric-label {
            color: #7f8c8d;
            font-size: 0.9rem;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-healthy { background-color: #27ae60; }
        .status-warning { background-color: #f39c12; }
        .status-critical { background-color: #e74c3c; }

        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 2rem;
        }

        .chart-container h3 {
            color: #2c3e50;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            font-weight: 600;
        }

        .chart-image {
            width: 100%;
            border-radius: 8px;
        }

        .alerts-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .alert-item {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            border-left: 4px solid;
        }

        .alert-warning {
            background-color: #fff3cd;
            border-left-color: #f39c12;
        }

        .alert-critical {
            background-color: #f8d7da;
            border-left-color: #e74c3c;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: #7f8c8d;
        }

        .refresh-button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s ease;
        }

        .refresh-button:hover {
            transform: scale(1.05);
        }

        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }

            .dashboard-container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Vizly Enterprise Dashboard</h1>
        <div class="subtitle">Real-time Performance Monitoring & Analytics</div>
    </div>

    <div class="dashboard-container">
        <div class="dashboard-grid">
            <div class="metric-card">
                <h3>System Health</h3>
                <div class="metric-value" id="health-score">--</div>
                <div class="metric-label">
                    <span class="status-indicator" id="health-indicator"></span>
                    <span id="health-status">Loading...</span>
                </div>
            </div>

            <div class="metric-card">
                <h3>CPU Usage</h3>
                <div class="metric-value" id="cpu-usage">--</div>
                <div class="metric-label">Percentage</div>
            </div>

            <div class="metric-card">
                <h3>Memory Usage</h3>
                <div class="metric-value" id="memory-usage">--</div>
                <div class="metric-label">Percentage</div>
            </div>

            <div class="metric-card">
                <h3>Active Alerts</h3>
                <div class="metric-value" id="active-alerts">--</div>
                <div class="metric-label">Current Issues</div>
            </div>
        </div>

        <div class="chart-container">
            <h3>📊 System Resource Usage</h3>
            <img id="resource-chart" class="chart-image" alt="Loading chart..." />
        </div>

        <div class="chart-container">
            <h3>⚡ API Performance Analytics</h3>
            <img id="api-chart" class="chart-image" alt="Loading chart..." />
        </div>

        <div class="alerts-container">
            <h3>🚨 Active Alerts</h3>
            <div id="alerts-list">
                <div class="loading">Loading alerts...</div>
            </div>
        </div>

        <div style="text-align: center; margin-top: 2rem;">
            <button class="refresh-button" onclick="refreshDashboard()">
                🔄 Refresh Dashboard
            </button>
        </div>
    </div>

    <script>
        let websocket = null;

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            initWebSocket();

            // Auto-refresh every 30 seconds
            setInterval(loadDashboard, 30000);
        });

        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/dashboard_user`;

            websocket = new WebSocket(wsUrl);

            websocket.onopen = function(event) {
                console.log('WebSocket connected');
                // Subscribe to dashboard updates
                websocket.send(JSON.stringify({
                    type: 'subscribe',
                    dashboard_id: 'system_admin'
                }));
            };

            websocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'metrics_update') {
                    updateMetrics(data.metrics);
                }
            };

            websocket.onclose = function(event) {
                console.log('WebSocket disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(initWebSocket, 5000);
            };
        }

        async function loadDashboard() {
            try {
                // Load live metrics
                const metricsResponse = await fetch('/api/metrics/live');
                const metricsData = await metricsResponse.json();
                updateMetrics(metricsData);

                // Load charts
                await loadCharts();

                // Load alerts
                await loadAlerts();

            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }

        function updateMetrics(data) {
            const systemHealth = data.system_health || {};

            // Update health score
            const healthScore = systemHealth.health_score || 0;
            document.getElementById('health-score').textContent = Math.round(healthScore);

            const healthStatus = systemHealth.status || 'unknown';
            document.getElementById('health-status').textContent = healthStatus.charAt(0).toUpperCase() + healthStatus.slice(1);

            const healthIndicator = document.getElementById('health-indicator');
            healthIndicator.className = 'status-indicator';
            if (healthScore > 80) {
                healthIndicator.classList.add('status-healthy');
            } else if (healthScore > 60) {
                healthIndicator.classList.add('status-warning');
            } else {
                healthIndicator.classList.add('status-critical');
            }

            // Update CPU usage
            const cpuMetrics = data.metrics?.cpu || [];
            if (cpuMetrics.length > 0) {
                const latestCpu = cpuMetrics[cpuMetrics.length - 1].value;
                document.getElementById('cpu-usage').textContent = Math.round(latestCpu) + '%';
            }

            // Update memory usage
            const memoryMetrics = data.metrics?.memory || [];
            if (memoryMetrics.length > 0) {
                const latestMemory = memoryMetrics[memoryMetrics.length - 1].value;
                document.getElementById('memory-usage').textContent = Math.round(latestMemory) + '%';
            }

            // Update active alerts count
            const alertsCount = data.active_alerts?.length || 0;
            document.getElementById('active-alerts').textContent = alertsCount;
        }

        async function loadCharts() {
            try {
                // Load resource usage chart
                const resourceResponse = await fetch('/api/charts/resource_usage');
                const resourceData = await resourceResponse.json();
                document.getElementById('resource-chart').src = resourceData.image;

                // Load API performance chart
                const apiResponse = await fetch('/api/charts/api_performance');
                const apiData = await apiResponse.json();
                document.getElementById('api-chart').src = apiData.image;

            } catch (error) {
                console.error('Error loading charts:', error);
            }
        }

        async function loadAlerts() {
            try {
                const response = await fetch('/api/alerts');
                const data = await response.json();

                const alertsList = document.getElementById('alerts-list');

                if (data.recent_alerts && data.recent_alerts.length > 0) {
                    alertsList.innerHTML = data.recent_alerts.map(alert => `
                        <div class="alert-item alert-${alert.severity}">
                            <strong>${alert.metric_name}</strong>: ${alert.message}
                            <br><small>Triggered: ${new Date(alert.timestamp).toLocaleString()}</small>
                        </div>
                    `).join('');
                } else {
                    alertsList.innerHTML = '<div style="text-align: center; color: #27ae60; padding: 1rem;">✅ No active alerts</div>';
                }

            } catch (error) {
                console.error('Error loading alerts:', error);
                document.getElementById('alerts-list').innerHTML = '<div class="loading">Error loading alerts</div>';
            }
        }

        function refreshDashboard() {
            loadDashboard();
        }
    </script>
</body>
</html>
        """

    async def start_background_updates(self):
        """Start background task for real-time updates"""
        async def update_loop():
            while True:
                try:
                    # Get latest dashboard data
                    dashboard_data = self.performance_monitor.get_dashboard_data()

                    # Broadcast to all connected users
                    await self.websocket_manager.broadcast_to_all({
                        'type': 'metrics_update',
                        'metrics': dashboard_data,
                        'timestamp': datetime.now().isoformat()
                    })

                    await asyncio.sleep(10)  # Update every 10 seconds

                except Exception as e:
                    self.logger.error(f"Error in background update loop: {e}")
                    await asyncio.sleep(10)

        self.update_task = asyncio.create_task(update_loop())

    async def stop_background_updates(self):
        """Stop background updates"""
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass

    def run(self, host: str = "0.0.0.0", port: int = 8889, reload: bool = False):
        """Run the dashboard server"""
        self.logger.info(f"Starting Vizly Enterprise Dashboard on http://{host}:{port}")

        # Start background updates
        asyncio.create_task(self.start_background_updates())

        # Run server
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )


# Convenience functions
def create_dashboard_server(performance_monitor: Optional[PerformanceMonitor] = None,
                          config: Optional[Dict] = None) -> DashboardServer:
    """Create a new dashboard server instance"""
    return DashboardServer(performance_monitor=performance_monitor, config=config)


def run_dashboard_server(host: str = "0.0.0.0", port: int = 8889,
                        performance_monitor: Optional[PerformanceMonitor] = None):
    """Quick way to run dashboard server"""
    server = create_dashboard_server(performance_monitor)
    server.run(host=host, port=port)


if __name__ == "__main__":
    # Run dashboard server if executed directly
    run_dashboard_server()