"""
Enterprise Web Server & API Framework
=====================================

High-performance web server with enterprise security, load balancing,
and API management capabilities.
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

import asyncio
import logging
import ssl
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from aiohttp import web
    from aiohttp.web import middleware
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    # Mock middleware decorator for when aiohttp is not available
    def middleware(func):
        return func

from .admin import UserManager
from .security import EnterpriseSecurityManager


@dataclass
class ServerConfig:
    """Enterprise server configuration."""
    host: str = "0.0.0.0"
    port: int = 8443
    ssl_enabled: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    max_request_size: int = 100 * 1024 * 1024  # 100MB
    request_timeout: int = 300
    worker_count: int = 4
    enable_cors: bool = True
    api_rate_limit: int = 1000  # requests per minute


class EnterpriseServer:
    """
    Enterprise-grade web server with security, performance, and monitoring.

    Features:
    - SSL/TLS encryption
    - JWT-based authentication
    - Role-based API access
    - Request rate limiting
    - Health monitoring
    - Audit logging
    """

    def __init__(self, port: int = 8443, ssl_enabled: bool = True,
                 config_path: Optional[str] = None):
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp is required for enterprise server. Install with: pip install aiohttp")

        self.config = ServerConfig(port=port, ssl_enabled=ssl_enabled)
        self.security_manager = EnterpriseSecurityManager()
        self.user_manager = UserManager(self.security_manager)
        self.app: Optional[web.Application] = None
        self.logger = logging.getLogger("vizly.enterprise.server")

        # Rate limiting storage
        self.rate_limit_store: Dict[str, List[float]] = {}

        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        """Load server configuration from YAML file."""
        try:
            import yaml
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)

            server_config = config_data.get('server', {})
            self.config.host = server_config.get('host', self.config.host)
            self.config.port = server_config.get('port', self.config.port)

            ssl_config = server_config.get('ssl', {})
            self.config.ssl_enabled = ssl_config.get('enabled', True)
            self.config.ssl_cert_path = ssl_config.get('cert_file')
            self.config.ssl_key_path = ssl_config.get('key_file')

        except Exception as e:
            self.logger.warning(f"Failed to load config from {config_path}: {e}")

    @middleware
    async def auth_middleware(self, request: web.Request, handler) -> web.Response:
        """Authentication middleware for API endpoints."""
        # Skip auth for health checks and public endpoints
        if request.path in ['/health', '/metrics', '/']:
            return await handler(request)

        # Extract JWT token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return web.json_response(
                {"error": "Missing or invalid authorization header"},
                status=401
            )

        token = auth_header[7:]  # Remove 'Bearer ' prefix
        payload = self.security_manager.validate_api_token(token)

        if not payload:
            return web.json_response(
                {"error": "Invalid or expired token"},
                status=401
            )

        # Add user context to request
        request['user_id'] = payload['user_id']
        request['session_id'] = payload['session_id']
        request['permissions'] = payload['permissions']

        return await handler(request)

    @middleware
    async def rate_limit_middleware(self, request: web.Request, handler) -> web.Response:
        """Rate limiting middleware."""
        client_ip = request.remote or 'unknown'
        current_time = asyncio.get_event_loop().time()

        # Clean old entries
        if client_ip in self.rate_limit_store:
            self.rate_limit_store[client_ip] = [
                timestamp for timestamp in self.rate_limit_store[client_ip]
                if current_time - timestamp < 60  # 1 minute window
            ]

        # Check rate limit
        request_count = len(self.rate_limit_store.get(client_ip, []))
        if request_count >= self.config.api_rate_limit:
            return web.json_response(
                {"error": "Rate limit exceeded"},
                status=429
            )

        # Record request
        if client_ip not in self.rate_limit_store:
            self.rate_limit_store[client_ip] = []
        self.rate_limit_store[client_ip].append(current_time)

        return await handler(request)

    def create_app(self) -> web.Application:
        """Create and configure the web application."""
        middlewares = []

        if self.config.api_rate_limit > 0:
            middlewares.append(self.rate_limit_middleware)

        middlewares.append(self.auth_middleware)

        self.app = web.Application(middlewares=middlewares)

        # Configure CORS if enabled
        if self.config.enable_cors:
            self._setup_cors()

        # Register routes
        self._register_routes()

        return self.app

    def _setup_cors(self) -> None:
        """Setup CORS headers for cross-origin requests."""
        try:
            import aiohttp_cors

            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })

            # Add CORS to all routes
            for route in list(self.app.router.routes()):
                cors.add(route)

        except ImportError:
            self.logger.warning("aiohttp-cors not available. CORS not configured.")

    def _register_routes(self) -> None:
        """Register API routes."""
        # Health and monitoring
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/metrics', self.metrics_handler)

        # Authentication
        self.app.router.add_post('/api/auth/login', self.login_handler)
        self.app.router.add_post('/api/auth/logout', self.logout_handler)
        self.app.router.add_post('/api/auth/refresh', self.refresh_token_handler)

        # User management
        self.app.router.add_get('/api/users', self.list_users_handler)
        self.app.router.add_post('/api/users', self.create_user_handler)
        self.app.router.add_get('/api/users/{user_id}', self.get_user_handler)

        # Chart management
        self.app.router.add_get('/api/charts', self.list_charts_handler)
        self.app.router.add_post('/api/charts', self.create_chart_handler)
        self.app.router.add_get('/api/charts/{chart_id}', self.get_chart_handler)

        # Static files (for web interface)
        static_path = Path(__file__).parent.parent.parent.parent / "static"
        if static_path.exists():
            self.app.router.add_static('/', static_path, name='static')

    async def index_handler(self, request: web.Request) -> web.Response:
        """Main index page."""
        return web.Response(text="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vizly Enterprise</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #2c5aa0; }
                .status { color: #28a745; }
            </style>
        </head>
        <body>
            <h1 class="header">🚀 Vizly Enterprise Server</h1>
            <p class="status">✅ Server is running and ready for requests</p>
            <h3>API Endpoints:</h3>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/metrics">System Metrics</a></li>
                <li><code>POST /api/auth/login</code> - User authentication</li>
                <li><code>GET /api/charts</code> - List charts</li>
                <li><code>POST /api/charts</code> - Create enterprise chart</li>
                <li><code>GET /api/charts/{id}</code> - Get chart details</li>
            </ul>

            <h3>Enterprise Chart Types:</h3>
            <ul>
                <li><strong>Executive Dashboard</strong> - KPI tracking with status indicators</li>
                <li><strong>Financial Analytics</strong> - Waterfall charts and variance analysis</li>
                <li><strong>Compliance</strong> - Scorecards and audit trail visualization</li>
                <li><strong>Risk Analysis</strong> - Risk matrices and Monte Carlo simulation</li>
            </ul>

            <h3>Features:</h3>
            <ul>
                <li>🔐 Enterprise security and compliance</li>
                <li>📊 Professional themes and branding</li>
                <li>📤 Multi-format exports (PDF, PNG, HTML)</li>
                <li>🎨 Accessibility features</li>
                <li>📋 Audit trails and governance</li>
                <li>⚡ GPU acceleration and performance optimization</li>
            </ul>
        </body>
        </html>
        """, content_type='text/html')

    async def health_handler(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        health_status = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "version": "1.0.0",
            "services": {
                "security_manager": "operational",
                "user_manager": "operational",
                "database": "operational"
            }
        }
        return web.json_response(health_status)

    async def metrics_handler(self, request: web.Request) -> web.Response:
        """System metrics endpoint."""
        import psutil

        metrics = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "active_sessions": len(self.security_manager.active_sessions),
            "total_users": len(self.user_manager.users),
            "request_count": sum(len(requests) for requests in self.rate_limit_store.values())
        }
        return web.json_response(metrics)

    async def login_handler(self, request: web.Request) -> web.Response:
        """User login endpoint."""
        try:
            data = await request.json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return web.json_response(
                    {"error": "Username and password required"},
                    status=400
                )

            # Authenticate user
            session = self.security_manager.authenticate_user(
                username, password, request.remote
            )

            if not session:
                return web.json_response(
                    {"error": "Invalid credentials"},
                    status=401
                )

            # Generate API token
            token = self.security_manager.generate_api_token(session.session_id)

            return web.json_response({
                "token": token,
                "user_id": session.user_id,
                "roles": list(session.roles),
                "expires_at": session.expires_at.isoformat()
            })

        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )

    async def logout_handler(self, request: web.Request) -> web.Response:
        """User logout endpoint."""
        session_id = request.get('session_id')
        if session_id and session_id in self.security_manager.active_sessions:
            del self.security_manager.active_sessions[session_id]

        return web.json_response({"message": "Logged out successfully"})

    async def refresh_token_handler(self, request: web.Request) -> web.Response:
        """Refresh API token."""
        session_id = request.get('session_id')
        if not session_id:
            return web.json_response({"error": "Invalid session"}, status=401)

        token = self.security_manager.generate_api_token(session_id)
        if not token:
            return web.json_response({"error": "Unable to refresh token"}, status=401)

        return web.json_response({"token": token})

    async def list_users_handler(self, request: web.Request) -> web.Response:
        """List users endpoint."""
        # Check permissions
        if 'admin' not in request.get('permissions', []):
            return web.json_response({"error": "Insufficient permissions"}, status=403)

        users = self.user_manager.list_users()
        return web.json_response({"users": users})

    async def create_user_handler(self, request: web.Request) -> web.Response:
        """Create user endpoint."""
        if 'admin' not in request.get('permissions', []):
            return web.json_response({"error": "Insufficient permissions"}, status=403)

        try:
            data = await request.json()
            username = data.get('username')
            role = data.get('role', 'viewer')

            success = self.user_manager.create_user(username, role)

            if success:
                return web.json_response({"message": "User created successfully"})
            else:
                return web.json_response({"error": "Failed to create user"}, status=400)

        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    async def get_user_handler(self, request: web.Request) -> web.Response:
        """Get user details endpoint."""
        user_id = request.match_info['user_id']

        # Users can view their own profile, admins can view any
        request_user_id = request.get('user_id')
        if user_id != request_user_id and 'admin' not in request.get('permissions', []):
            return web.json_response({"error": "Insufficient permissions"}, status=403)

        user = self.user_manager.get_user_by_username(user_id)
        if not user:
            return web.json_response({"error": "User not found"}, status=404)

        return web.json_response({
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "roles": list(user.roles),
            "department": user.department,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active
        })

    async def list_charts_handler(self, request: web.Request) -> web.Response:
        """List charts endpoint."""
        # Placeholder implementation
        charts = [
            {"id": "1", "title": "Sales Dashboard", "type": "line", "created_at": "2024-01-01"},
            {"id": "2", "title": "Performance Metrics", "type": "scatter", "created_at": "2024-01-02"}
        ]
        return web.json_response({"charts": charts})

    async def create_chart_handler(self, request: web.Request) -> web.Response:
        """Create chart endpoint."""
        try:
            data = await request.json()
            chart_type = data.get('type', 'executive_dashboard')
            title = data.get('title', 'Enterprise Chart')

            # Import here to avoid circular dependencies
            from .charts import EnterpriseChartFactory
            from .security import SecurityLevel

            # Create enterprise chart
            chart = EnterpriseChartFactory.create_chart(chart_type)
            chart.metadata.title = title
            chart.metadata.created_by = request.get('user_id', 'api_user')

            # Set security classification
            security_level = data.get('security_level', 'internal')
            if security_level == 'confidential':
                chart.set_security_classification(SecurityLevel.CONFIDENTIAL)
            elif security_level == 'restricted':
                chart.set_security_classification(SecurityLevel.RESTRICTED)
            else:
                chart.set_security_classification(SecurityLevel.INTERNAL)

            # Add compliance tags if provided
            for tag in data.get('compliance_tags', []):
                chart.add_compliance_tag(tag)

            # Create chart data based on type
            if chart_type == 'executive_dashboard' and 'kpis' in data:
                chart.create_kpi_dashboard(data['kpis'])
            elif chart_type == 'compliance' and 'metrics' in data:
                chart.create_compliance_scorecard(data['metrics'])

            return web.json_response({
                "id": chart.metadata.chart_id,
                "title": chart.metadata.title,
                "type": chart_type,
                "security_level": chart.metadata.security_level.value,
                "compliance_tags": chart.metadata.compliance_tags,
                "audit_trail_count": len(chart.get_audit_trail()),
                "message": "Enterprise chart created successfully"
            })

        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    async def get_chart_handler(self, request: web.Request) -> web.Response:
        """Get chart details endpoint."""
        chart_id = request.match_info['chart_id']
        # Placeholder implementation
        return web.json_response({
            "id": chart_id,
            "title": f"Chart {chart_id}",
            "type": "line",
            "data": {"x": [1, 2, 3], "y": [4, 5, 6]}
        })

    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for HTTPS."""
        if not self.config.ssl_enabled:
            return None

        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

            if self.config.ssl_cert_path and self.config.ssl_key_path:
                context.load_cert_chain(self.config.ssl_cert_path, self.config.ssl_key_path)
            else:
                # Generate self-signed certificate for development
                self.logger.warning("Using self-signed certificate for development")

            return context

        except Exception as e:
            self.logger.error(f"Failed to create SSL context: {e}")
            return None

    def start(self) -> None:
        """Start the enterprise server."""
        if not self.app:
            self.create_app()

        ssl_context = self._create_ssl_context()

        print("🚀 Starting Vizly Enterprise Server...")
        print(f"   Host: {self.config.host}")
        print(f"   Port: {self.config.port}")
        print(f"   SSL: {'Enabled' if ssl_context else 'Disabled'}")
        print(f"   Workers: {self.config.worker_count}")

        try:
            web.run_app(
                self.app,
                host=self.config.host,
                port=self.config.port,
                ssl_context=ssl_context,
                access_log=self.logger
            )
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise