"""
OpenFinOps Web UI Server
=========================

Flask-based web server with WebSocket support for real-time dashboard updates.
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



import os
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time

# Import OpenFinOps components
try:
    from openfinops import ObservabilityHub
    from openfinops.dashboard import CFODashboard, COODashboard, InfrastructureLeaderDashboard
    from openfinops.observability import CostObservatory
    OPENFINOPS_AVAILABLE = True
except ImportError:
    OPENFINOPS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

app.config['SECRET_KEY'] = 'openfinops-secret-key-change-in-production'
CORS(app)

# Initialize SocketIO for real-time updates
# Use eventlet for better WebSocket support, fallback to threading
try:
    import eventlet
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
except ImportError:
    # Fallback to threading mode (WebSocket may not work in dev mode)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading',
                       engineio_logger=False, logger=False)

# Global state
dashboard_data = {
    'cfo': {},
    'coo': {},
    'infrastructure': {},
    'metrics': {
        'total_cost': 0,
        'ai_ml_cost': 0,
        'cloud_cost': 0,
        'cost_trend': []
    }
}

update_thread = None
update_thread_running = False


def generate_mock_data():
    """Generate mock data for demonstration."""
    import random
    return {
        'timestamp': datetime.now().isoformat(),
        'total_cost': round(random.uniform(50000, 150000), 2),
        'ai_ml_cost': round(random.uniform(20000, 60000), 2),
        'cloud_cost': round(random.uniform(30000, 90000), 2),
        'cost_by_service': {
            'EC2': round(random.uniform(10000, 30000), 2),
            'S3': round(random.uniform(5000, 15000), 2),
            'SageMaker': round(random.uniform(15000, 45000), 2),
            'Lambda': round(random.uniform(2000, 8000), 2),
        },
        'cost_trend': [
            {'date': f'Day {i}', 'cost': round(random.uniform(40000, 160000), 2)}
            for i in range(1, 8)
        ],
        'top_resources': [
            {'name': f'Resource {i}', 'cost': round(random.uniform(5000, 25000), 2)}
            for i in range(1, 6)
        ]
    }


def background_updater():
    """Background thread to push real-time updates to clients."""
    global update_thread_running
    logger.info("Starting background updater thread")

    while update_thread_running:
        try:
            # Generate new data
            new_data = generate_mock_data()
            dashboard_data['metrics'] = new_data

            # Emit update to all connected clients
            socketio.emit('dashboard_update', new_data, namespace='/live')

            # Sleep for 5 seconds before next update
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error in background updater: {e}")
            time.sleep(5)


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/dashboard/cfo')
def cfo_dashboard():
    """CFO Executive Dashboard."""
    return render_template('cfo_dashboard.html')


@app.route('/dashboard/coo')
def coo_dashboard():
    """COO Operational Dashboard."""
    return render_template('coo_dashboard.html')


@app.route('/dashboard/infrastructure')
def infrastructure_dashboard():
    """Infrastructure Leader Dashboard."""
    return render_template('infrastructure_dashboard.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'openfinops_available': OPENFINOPS_AVAILABLE
    })


@app.route('/api/metrics')
def get_metrics():
    """Get current metrics."""
    return jsonify(dashboard_data['metrics'])


@app.route('/api/dashboard/cfo')
def get_cfo_data():
    """Get CFO dashboard data."""
    if OPENFINOPS_AVAILABLE:
        try:
            dashboard = CFODashboard()
            # For now, return mock data - will integrate real dashboard later
            data = generate_mock_data()
            data['dashboard_type'] = 'CFO Executive'
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error generating CFO dashboard: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify(generate_mock_data())


@app.route('/api/dashboard/coo')
def get_coo_data():
    """Get COO dashboard data."""
    data = generate_mock_data()
    data['dashboard_type'] = 'COO Operational'
    data['operational_efficiency'] = 87.5
    data['sla_compliance'] = 99.2
    return jsonify(data)


@app.route('/api/dashboard/infrastructure')
def get_infrastructure_data():
    """Get Infrastructure dashboard data."""
    import random
    data = generate_mock_data()
    data['dashboard_type'] = 'Infrastructure Leader'
    data['system_health'] = {
        'cpu_usage': round(random.uniform(40, 80), 1),
        'memory_usage': round(random.uniform(50, 85), 1),
        'disk_usage': round(random.uniform(30, 70), 1),
        'network_throughput': round(random.uniform(100, 500), 1)
    }
    return jsonify(data)


# WebSocket event handlers
@socketio.on('connect', namespace='/live')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected")
    emit('connected', {'message': 'Connected to OpenFinOps live updates'})

    # Send initial data
    emit('dashboard_update', dashboard_data['metrics'])


@socketio.on('disconnect', namespace='/live')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected")


@socketio.on('request_update', namespace='/live')
def handle_update_request():
    """Handle manual update request from client."""
    logger.info("Update requested by client")
    new_data = generate_mock_data()
    emit('dashboard_update', new_data)


def start_server(host='0.0.0.0', port=8080, debug=False):
    """Start the OpenFinOps web server.

    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8080)
        debug: Enable debug mode (default: False)
    """
    global update_thread, update_thread_running

    # Create templates and static directories if they don't exist
    template_dir = Path(__file__).parent / 'templates'
    static_dir = Path(__file__).parent / 'static'
    template_dir.mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)

    logger.info(f"Starting OpenFinOps Web UI on {host}:{port}")
    logger.info(f"Dashboard URL: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")

    # Start background update thread
    update_thread_running = True
    update_thread = threading.Thread(target=background_updater, daemon=True)
    update_thread.start()

    try:
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        update_thread_running = False
        if update_thread:
            update_thread.join(timeout=2)


if __name__ == '__main__':
    start_server(debug=True)
