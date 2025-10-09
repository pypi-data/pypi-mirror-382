"""
Local Telemetry Collection Server
================================

Self-hosted telemetry collection server that replaces the need for external endpoints.
Provides a complete telemetry collection infrastructure that can be deployed anywhere.
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
import sqlite3
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, render_template_string
from collections import defaultdict, deque
import logging


@dataclass
class TelemetryData:
    """Telemetry data structure"""
    timestamp: float
    agent_id: str
    hostname: str
    cloud_provider: str
    region: str
    metrics: Dict[str, Any]
    events: List[Dict[str, Any]]
    traces: List[Dict[str, Any]]


class TelemetryDatabase:
    """SQLite database for telemetry storage"""

    def __init__(self, db_path: str = "telemetry.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize telemetry database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                agent_id TEXT,
                hostname TEXT,
                cloud_provider TEXT,
                region TEXT,
                metrics TEXT,
                events TEXT,
                traces TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_registry (
                agent_id TEXT PRIMARY KEY,
                hostname TEXT,
                cloud_provider TEXT,
                region TEXT,
                last_heartbeat REAL,
                status TEXT,
                config TEXT,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                agent_id TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_timestamp ON telemetry_data(agent_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON telemetry_data(timestamp)')

        conn.commit()
        conn.close()

    def store_telemetry(self, data: TelemetryData):
        """Store telemetry data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO telemetry_data
            (timestamp, agent_id, hostname, cloud_provider, region, metrics, events, traces)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.timestamp,
            data.agent_id,
            data.hostname,
            data.cloud_provider,
            data.region,
            json.dumps(data.metrics),
            json.dumps(data.events),
            json.dumps(data.traces)
        ))

        conn.commit()
        conn.close()

    def register_agent(self, agent_id: str, hostname: str, cloud_provider: str,
                      region: str, config: Dict[str, Any]):
        """Register a new agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO agent_registry
            (agent_id, hostname, cloud_provider, region, last_heartbeat, status, config)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent_id, hostname, cloud_provider, region,
            time.time(), 'active', json.dumps(config)
        ))

        conn.commit()
        conn.close()

    def update_agent_heartbeat(self, agent_id: str):
        """Update agent heartbeat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE agent_registry
            SET last_heartbeat = ?, status = 'active'
            WHERE agent_id = ?
        ''', (time.time(), agent_id))

        conn.commit()
        conn.close()

    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM agent_registry ORDER BY last_heartbeat DESC')
        columns = [desc[0] for desc in cursor.description]

        agents = []
        for row in cursor.fetchall():
            agent = dict(zip(columns, row))
            agent['config'] = json.loads(agent['config']) if agent['config'] else {}
            agents.append(agent)

        conn.close()
        return agents

    def get_recent_telemetry(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent telemetry data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = time.time() - (hours * 3600)
        cursor.execute('''
            SELECT * FROM telemetry_data
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', (cutoff_time,))

        columns = [desc[0] for desc in cursor.description]
        telemetry = []

        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            data['metrics'] = json.loads(data['metrics']) if data['metrics'] else {}
            data['events'] = json.loads(data['events']) if data['events'] else []
            data['traces'] = json.loads(data['traces']) if data['traces'] else []
            telemetry.append(data)

        conn.close()
        return telemetry


class TelemetryServer:
    """Local telemetry collection server"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.db = TelemetryDatabase()
        self.logger = logging.getLogger(__name__)

        # In-memory cache for performance
        self.recent_data = deque(maxlen=1000)
        self.agent_status = {}

        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes for telemetry collection"""

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'version': '1.0.0',
                'uptime': time.time() - getattr(self, 'start_time', time.time())
            })

        @self.app.route('/api/v1/telemetry/ingest', methods=['POST'])
        def ingest_telemetry():
            """Ingest telemetry data from agents"""
            try:
                data = request.get_json()

                if not data or 'agent_id' not in data:
                    return jsonify({'error': 'Invalid telemetry data'}), 400

                # Create telemetry data object
                telemetry = TelemetryData(
                    timestamp=data.get('timestamp', time.time()),
                    agent_id=data['agent_id'],
                    hostname=data.get('hostname', 'unknown'),
                    cloud_provider=data.get('cloud_provider', 'unknown'),
                    region=data.get('region', 'unknown'),
                    metrics=data.get('metrics', {}),
                    events=data.get('events', []),
                    traces=data.get('traces', [])
                )

                # Store in database
                self.db.store_telemetry(telemetry)

                # Update agent heartbeat
                self.db.update_agent_heartbeat(data['agent_id'])

                # Cache for real-time access
                self.recent_data.append(asdict(telemetry))

                return jsonify({'status': 'success', 'message': 'Telemetry data received'})

            except Exception as e:
                self.logger.error(f"Error ingesting telemetry: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/v1/agents/register', methods=['POST'])
        def register_agent():
            """Register a new telemetry agent"""
            try:
                data = request.get_json()

                required_fields = ['agent_id', 'hostname', 'cloud_provider', 'region']
                if not all(field in data for field in required_fields):
                    return jsonify({'error': 'Missing required fields'}), 400

                self.db.register_agent(
                    agent_id=data['agent_id'],
                    hostname=data['hostname'],
                    cloud_provider=data['cloud_provider'],
                    region=data['region'],
                    config=data.get('config', {})
                )

                return jsonify({'status': 'success', 'message': 'Agent registered'})

            except Exception as e:
                self.logger.error(f"Error registering agent: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/v1/agents', methods=['GET'])
        def list_agents():
            """List all registered agents"""
            try:
                agents = self.db.get_agents()

                # Add status information
                current_time = time.time()
                for agent in agents:
                    last_heartbeat = agent.get('last_heartbeat', 0)
                    time_since_heartbeat = current_time - last_heartbeat

                    if time_since_heartbeat < 300:  # 5 minutes
                        agent['status'] = 'healthy'
                    elif time_since_heartbeat < 900:  # 15 minutes
                        agent['status'] = 'warning'
                    else:
                        agent['status'] = 'offline'

                return jsonify({'agents': agents})

            except Exception as e:
                self.logger.error(f"Error listing agents: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/v1/telemetry/recent', methods=['GET'])
        def get_recent_telemetry():
            """Get recent telemetry data"""
            try:
                hours = int(request.args.get('hours', 24))
                telemetry = self.db.get_recent_telemetry(hours)

                return jsonify({
                    'telemetry': telemetry,
                    'count': len(telemetry),
                    'hours': hours
                })

            except Exception as e:
                self.logger.error(f"Error getting recent telemetry: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/v1/metrics/summary', methods=['GET'])
        def get_metrics_summary():
            """Get telemetry metrics summary"""
            try:
                agents = self.db.get_agents()
                telemetry = self.db.get_recent_telemetry(1)  # Last 1 hour

                # Calculate summary metrics
                total_agents = len(agents)
                healthy_agents = len([a for a in agents if a.get('status') == 'healthy'])
                total_events = sum(len(t.get('events', [])) for t in telemetry)

                summary = {
                    'total_agents': total_agents,
                    'healthy_agents': healthy_agents,
                    'offline_agents': total_agents - healthy_agents,
                    'total_events_last_hour': total_events,
                    'average_events_per_agent': total_events / max(total_agents, 1),
                    'data_points': len(telemetry),
                    'timestamp': time.time()
                }

                return jsonify(summary)

            except Exception as e:
                self.logger.error(f"Error getting metrics summary: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/dashboard', methods=['GET'])
        def dashboard():
            """Telemetry dashboard"""
            return render_template_string(self._get_dashboard_template())

        @self.app.route('/', methods=['GET'])
        def index():
            """Root endpoint - redirect to dashboard"""
            return '''
            <html>
            <head><title>OpenFinOps Telemetry Server</title></head>
            <body>
                <h1>🏗️ OpenFinOps Telemetry Collection Server</h1>
                <p>Your local telemetry collection infrastructure is running!</p>
                <ul>
                    <li><a href="/dashboard">📊 Telemetry Dashboard</a></li>
                    <li><a href="/api/v1/agents">👥 Registered Agents</a></li>
                    <li><a href="/api/v1/metrics/summary">📈 Metrics Summary</a></li>
                    <li><a href="/health">❤️ Health Check</a></li>
                </ul>
                <h3>API Endpoints:</h3>
                <ul>
                    <li><code>POST /api/v1/telemetry/ingest</code> - Ingest telemetry data</li>
                    <li><code>POST /api/v1/agents/register</code> - Register new agent</li>
                    <li><code>GET /api/v1/agents</code> - List all agents</li>
                    <li><code>GET /api/v1/telemetry/recent</code> - Get recent telemetry</li>
                </ul>
            </body>
            </html>
            '''

    def _get_dashboard_template(self):
        """Get dashboard HTML template"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>OpenFinOps Telemetry Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .metric-value { font-size: 2em; font-weight: bold; color: #FFD700; }
        .metric-label { margin-top: 10px; opacity: 0.9; }
        .agents-table {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.2); }
        .status-healthy { color: #4CAF50; font-weight: bold; }
        .status-warning { color: #FF9800; font-weight: bold; }
        .status-offline { color: #F44336; font-weight: bold; }
        .refresh-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
    <script>
        let refreshInterval;

        function loadDashboard() {
            fetch('/api/v1/metrics/summary')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-agents').textContent = data.total_agents;
                    document.getElementById('healthy-agents').textContent = data.healthy_agents;
                    document.getElementById('offline-agents').textContent = data.offline_agents;
                    document.getElementById('total-events').textContent = data.total_events_last_hour;
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                });

            fetch('/api/v1/agents')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('agents-tbody');
                    tbody.innerHTML = '';

                    data.agents.forEach(agent => {
                        const row = tbody.insertRow();
                        row.innerHTML = `
                            <td>${agent.agent_id}</td>
                            <td>${agent.hostname}</td>
                            <td>${agent.cloud_provider}</td>
                            <td>${agent.region}</td>
                            <td class="status-${agent.status}">${agent.status}</td>
                            <td>${new Date(agent.last_heartbeat * 1000).toLocaleTimeString()}</td>
                        `;
                    });
                });
        }

        function startAutoRefresh() {
            if (refreshInterval) clearInterval(refreshInterval);
            refreshInterval = setInterval(loadDashboard, 30000); // Refresh every 30 seconds
            document.getElementById('auto-refresh').textContent = 'ON';
        }

        function stopAutoRefresh() {
            if (refreshInterval) clearInterval(refreshInterval);
            document.getElementById('auto-refresh').textContent = 'OFF';
        }

        window.onload = function() {
            loadDashboard();
            startAutoRefresh();
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ OpenFinOps Telemetry Dashboard</h1>
            <p>Real-time infrastructure monitoring | Last update: <span id="last-update">Loading...</span></p>
            <button class="refresh-btn" onclick="loadDashboard()">🔄 Refresh Now</button>
            <button class="refresh-btn" onclick="startAutoRefresh()">▶️ Auto-refresh</button>
            <button class="refresh-btn" onclick="stopAutoRefresh()">⏸️ Stop</button>
            <span>Auto-refresh: <span id="auto-refresh">ON</span></span>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value" id="total-agents">-</div>
                <div class="metric-label">Total Agents</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="healthy-agents">-</div>
                <div class="metric-label">Healthy Agents</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="offline-agents">-</div>
                <div class="metric-label">Offline Agents</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="total-events">-</div>
                <div class="metric-label">Events (Last Hour)</div>
            </div>
        </div>

        <div class="agents-table">
            <h2>📡 Registered Agents</h2>
            <table>
                <thead>
                    <tr>
                        <th>Agent ID</th>
                        <th>Hostname</th>
                        <th>Cloud Provider</th>
                        <th>Region</th>
                        <th>Status</th>
                        <th>Last Heartbeat</th>
                    </tr>
                </thead>
                <tbody id="agents-tbody">
                    <tr><td colspan="6">Loading agents...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        '''

    def start_server(self):
        """Start the telemetry server"""
        self.start_time = time.time()
        self.logger.info(f"Starting Telemetry Server on {self.host}:{self.port}")

        print(f"🚀 OpenFinOps Telemetry Server starting...")
        print(f"📡 Listening on: http://{self.host}:{self.port}")
        print(f"📊 Dashboard: http://{self.host}:{self.port}/dashboard")
        print(f"❤️  Health Check: http://{self.host}:{self.port}/health")
        print(f"🗃️  Database: {self.db.db_path}")

        self.app.run(host=self.host, port=self.port, debug=False)


# Telemetry agent configuration for local server
def get_local_telemetry_config(server_host: str = "localhost", server_port: int = 8080):
    """Get configuration for agents to use local telemetry server"""
    base_url = f"http://{server_host}:{server_port}"

    return {
        "telemetry": {
            "endpoint": f"{base_url}/api/v1/telemetry/ingest",
            "registration_endpoint": f"{base_url}/api/v1/agents/register",
            "health_check_endpoint": f"{base_url}/health",
            "timeout": 30,
            "retry_attempts": 3
        },
        "collection": {
            "metrics_interval": 60,
            "heartbeat_interval": 300,
            "batch_size": 100
        },
        "local_buffer": {
            "max_size": "100MB",
            "flush_interval": 30,
            "offline_retention": "24h"
        }
    }


if __name__ == "__main__":
    # Start local telemetry server
    server = TelemetryServer(host="0.0.0.0", port=8080)

    print("🏗️ Starting OpenFinOps Local Telemetry Collection Server")
    print("="*60)

    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n👋 Telemetry server stopped gracefully")
    except Exception as e:
        print(f"❌ Error starting server: {e}")