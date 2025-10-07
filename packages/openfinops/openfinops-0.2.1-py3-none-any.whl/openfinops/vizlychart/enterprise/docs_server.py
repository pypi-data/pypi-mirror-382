"""
API Documentation Server
========================

Interactive API documentation server with Swagger UI and examples.
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
from pathlib import Path
from typing import Dict, Any

try:
    from aiohttp import web
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    warnings.warn("aiohttp not available for documentation server")

from .api import APIDocumentationGenerator


class DocumentationServer:
    """
    Interactive API documentation server with Swagger UI.
    """

    def __init__(self, port: int = 8889):
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp required for documentation server")

        self.port = port
        self.doc_generator = APIDocumentationGenerator()
        self.app: web.Application = None

    def create_app(self) -> web.Application:
        """Create documentation web application."""
        self.app = web.Application()

        # Add routes
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/openapi.json', self.openapi_spec_handler)
        self.app.router.add_get('/docs', self.swagger_ui_handler)
        self.app.router.add_get('/redoc', self.redoc_handler)
        self.app.router.add_get('/examples', self.examples_handler)

        return self.app

    async def index_handler(self, request: web.Request) -> web.Response:
        """Main documentation index."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vizly Enterprise API Documentation</title>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                    min-height: 100vh;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                .header {
                    color: #2c5aa0;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .subtitle {
                    text-align: center;
                    color: #666;
                    font-size: 1.2em;
                    margin-bottom: 40px;
                }
                .nav-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                .nav-card {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    text-decoration: none;
                    color: #333;
                    border: 2px solid transparent;
                    transition: all 0.3s ease;
                }
                .nav-card:hover {
                    border-color: #2c5aa0;
                    background: #e3f2fd;
                    transform: translateY(-2px);
                }
                .nav-card h3 {
                    margin: 0 0 10px 0;
                    color: #2c5aa0;
                }
                .features {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 30px;
                }
                .feature-list {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 15px;
                    margin-top: 15px;
                }
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">📚 Vizly Enterprise API Documentation</h1>
                <p class="subtitle">Interactive documentation and examples for enterprise visualization</p>

                <div class="nav-grid">
                    <a href="/docs" class="nav-card">
                        <h3>🔧 Swagger UI</h3>
                        <p>Interactive API explorer with live testing</p>
                    </a>

                    <a href="/redoc" class="nav-card">
                        <h3>📖 ReDoc</h3>
                        <p>Beautiful API documentation</p>
                    </a>

                    <a href="/openapi.json" class="nav-card">
                        <h3>📄 OpenAPI Spec</h3>
                        <p>Machine-readable API specification</p>
                    </a>

                    <a href="/examples" class="nav-card">
                        <h3>💡 Code Examples</h3>
                        <p>SDK examples and integration guides</p>
                    </a>
                </div>

                <div class="features">
                    <h3>🚀 Enterprise Features</h3>
                    <div class="feature-list">
                        <div>• JWT-based authentication</div>
                        <div>• Role-based access control</div>
                        <div>• Executive dashboards</div>
                        <div>• Financial analytics</div>
                        <div>• Compliance monitoring</div>
                        <div>• Risk analysis</div>
                        <div>• Security classification</div>
                        <div>• Audit logging</div>
                        <div>• Multi-format exports</div>
                        <div>• Enterprise themes</div>
                        <div>• Performance optimization</div>
                        <div>• Comprehensive SDKs</div>
                    </div>
                </div>

                <div class="footer">
                    <p>Vizly Enterprise API Documentation • Version 1.0.0</p>
                    <p>Contact: <a href="mailto:enterprise@vizly.com">enterprise@vizly.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')

    async def openapi_spec_handler(self, request: web.Request) -> web.Response:
        """Serve OpenAPI specification."""
        spec = self.doc_generator.generate_openapi_spec()
        return web.json_response(spec)

    async def swagger_ui_handler(self, request: web.Request) -> web.Response:
        """Serve Swagger UI for interactive API exploration."""
        swagger_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vizly Enterprise API - Swagger UI</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
            <style>
                html {
                    box-sizing: border-box;
                    overflow: -moz-scrollbars-vertical;
                    overflow-y: scroll;
                }
                *, *:before, *:after {
                    box-sizing: inherit;
                }
                body {
                    margin: 0;
                    background: #fafafa;
                }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {
                    const ui = SwaggerUIBundle({
                        url: '/openapi.json',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout"
                    });
                };
            </script>
        </body>
        </html>
        """
        return web.Response(text=swagger_html, content_type='text/html')

    async def redoc_handler(self, request: web.Request) -> web.Response:
        """Serve ReDoc for beautiful API documentation."""
        redoc_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vizly Enterprise API - ReDoc</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                }
            </style>
        </head>
        <body>
            <redoc spec-url='/openapi.json'></redoc>
            <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
        </body>
        </html>
        """
        return web.Response(text=redoc_html, content_type='text/html')

    async def examples_handler(self, request: web.Request) -> web.Response:
        """Serve code examples and integration guides."""
        examples_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vizly Enterprise API Examples</title>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .header {
                    color: #2c5aa0;
                    border-bottom: 3px solid #2c5aa0;
                    padding-bottom: 10px;
                }
                .section {
                    margin: 30px 0;
                }
                .code-block {
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 15px 0;
                    overflow-x: auto;
                }
                .language-tabs {
                    display: flex;
                    border-bottom: 1px solid #ddd;
                    margin-bottom: 20px;
                }
                .tab {
                    padding: 10px 20px;
                    background: #f8f9fa;
                    border: 1px solid #ddd;
                    border-bottom: none;
                    cursor: pointer;
                    margin-right: 5px;
                }
                .tab.active {
                    background: white;
                    border-bottom: 1px solid white;
                    margin-bottom: -1px;
                }
                .tab-content {
                    display: none;
                }
                .tab-content.active {
                    display: block;
                }
                pre {
                    margin: 0;
                    white-space: pre-wrap;
                }
                .endpoint {
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 4px;
                    margin: 10px 0;
                }
                .method {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                    margin-right: 10px;
                }
                .get { background: #61affe; }
                .post { background: #49cc90; }
                .put { background: #fca130; }
                .delete { background: #f93e3e; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">💡 Vizly Enterprise API Examples</h1>

                <div class="section">
                    <h2>🔐 Authentication</h2>
                    <p>All API requests require JWT authentication. First, obtain a token:</p>

                    <div class="language-tabs">
                        <div class="tab active" onclick="showTab('auth', 'curl')">cURL</div>
                        <div class="tab" onclick="showTab('auth', 'python')">Python</div>
                        <div class="tab" onclick="showTab('auth', 'javascript')">JavaScript</div>
                    </div>

                    <div id="auth-curl" class="tab-content active">
                        <div class="code-block">
                            <pre>curl -X POST http://localhost:8888/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "admin@company.com",
    "password": "your-password"
  }'</pre>
                        </div>
                    </div>

                    <div id="auth-python" class="tab-content">
                        <div class="code-block">
                            <pre>from vizly.enterprise.api import VizlyEnterpriseClient

client = VizlyEnterpriseClient(
    base_url="http://localhost:8888",
    username="admin@company.com",
    password="your-password"
)

# Client automatically handles authentication
health = client.health_check()
print(f"Server status: {health.data['status']}")</pre>
                        </div>
                    </div>

                    <div id="auth-javascript" class="tab-content">
                        <div class="code-block">
                            <pre>const client = new VizlyEnterpriseClient('http://localhost:8888');

// Authenticate
const auth = await client.authenticate('admin@company.com', 'your-password');
if (auth.success) {
    console.log('Authentication successful');
    console.log('Token:', auth.data.token);
}</pre>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📊 Creating Charts</h2>

                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <code>/api/charts</code> - Create enterprise chart
                    </div>

                    <h3>Executive Dashboard Example</h3>

                    <div class="language-tabs">
                        <div class="tab active" onclick="showTab('chart', 'python')">Python</div>
                        <div class="tab" onclick="showTab('chart', 'javascript')">JavaScript</div>
                        <div class="tab" onclick="showTab('chart', 'curl')">cURL</div>
                    </div>

                    <div id="chart-python" class="tab-content active">
                        <div class="code-block">
                            <pre>response = client.create_chart(
    "executive_dashboard",
    "Q4 Performance Dashboard",
    data={
        "kpis": {
            "Revenue": {"value": 1200000, "target": 1000000, "status": "good"},
            "Profit": {"value": 180000, "target": 150000, "status": "good"},
            "Customer Satisfaction": {"value": 87, "target": 90, "status": "warning"}
        }
    },
    security_level="confidential",
    compliance_tags=["Executive Reporting", "Board Review"]
)

if response.success:
    print(f"Chart created: {response.data['id']}")
    print(f"Security level: {response.data['security_level']}")
else:
    print(f"Error: {response.error}")</pre>
                        </div>
                    </div>

                    <div id="chart-javascript" class="tab-content">
                        <div class="code-block">
                            <pre>const chartConfig = {
    type: 'executive_dashboard',
    title: 'Q4 Performance Dashboard',
    security_level: 'confidential',
    compliance_tags: ['Executive Reporting', 'Board Review'],
    kpis: {
        'Revenue': {value: 1200000, target: 1000000, status: 'good'},
        'Profit': {value: 180000, target: 150000, status: 'good'},
        'Customer Satisfaction': {value: 87, target: 90, status: 'warning'}
    }
};

const result = await client.createChart(chartConfig);
if (result.success) {
    console.log('Chart created:', result.data.id);
    console.log('Security level:', result.data.security_level);
}</pre>
                        </div>
                    </div>

                    <div id="chart-curl" class="tab-content">
                        <div class="code-block">
                            <pre>curl -X POST http://localhost:8888/api/charts \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "type": "executive_dashboard",
    "title": "Q4 Performance Dashboard",
    "security_level": "confidential",
    "compliance_tags": ["Executive Reporting", "Board Review"],
    "kpis": {
        "Revenue": {"value": 1200000, "target": 1000000, "status": "good"},
        "Profit": {"value": 180000, "target": 150000, "status": "good"}
    }
  }'</pre>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📈 Chart Types</h2>

                    <h3>1. Executive Dashboard</h3>
                    <p>KPI tracking with status indicators and progress bars.</p>
                    <ul>
                        <li><strong>Type:</strong> <code>executive_dashboard</code></li>
                        <li><strong>Data:</strong> KPIs with values, targets, and status</li>
                        <li><strong>Use cases:</strong> C-level reporting, board presentations</li>
                    </ul>

                    <h3>2. Financial Analytics</h3>
                    <p>Waterfall charts and variance analysis for financial reporting.</p>
                    <ul>
                        <li><strong>Type:</strong> <code>financial_analytics</code></li>
                        <li><strong>Data:</strong> Categories and values for waterfall analysis</li>
                        <li><strong>Use cases:</strong> Revenue analysis, budget variance</li>
                    </ul>

                    <h3>3. Compliance Scorecard</h3>
                    <p>Traffic light scorecards for compliance monitoring.</p>
                    <ul>
                        <li><strong>Type:</strong> <code>compliance</code></li>
                        <li><strong>Data:</strong> Metrics with scores and thresholds</li>
                        <li><strong>Use cases:</strong> GDPR, SOX, HIPAA compliance tracking</li>
                    </ul>

                    <h3>4. Risk Analysis</h3>
                    <p>Risk matrices and probability analysis.</p>
                    <ul>
                        <li><strong>Type:</strong> <code>risk_analysis</code></li>
                        <li><strong>Data:</strong> Risk factors with probability and impact</li>
                        <li><strong>Use cases:</strong> Enterprise risk management</li>
                    </ul>
                </div>

                <div class="section">
                    <h2>🔒 Security Features</h2>

                    <h3>Security Levels</h3>
                    <ul>
                        <li><code>public</code> - No restrictions</li>
                        <li><code>internal</code> - Company internal only</li>
                        <li><code>confidential</code> - Sensitive business data</li>
                        <li><code>restricted</code> - Highest security level</li>
                    </ul>

                    <h3>Compliance Tags</h3>
                    <p>Tag charts for regulatory compliance:</p>
                    <ul>
                        <li><code>SOX</code> - Sarbanes-Oxley compliance</li>
                        <li><code>GDPR</code> - Data protection compliance</li>
                        <li><code>HIPAA</code> - Healthcare data compliance</li>
                        <li><code>Executive Reporting</code> - Executive visibility</li>
                    </ul>
                </div>
            </div>

            <script>
                function showTab(section, language) {
                    // Hide all tabs in section
                    const contents = document.querySelectorAll(`[id^="${section}-"]`);
                    contents.forEach(content => {
                        content.classList.remove('active');
                    });

                    const tabs = document.querySelectorAll(`[onclick*="${section}"]`);
                    tabs.forEach(tab => {
                        tab.classList.remove('active');
                    });

                    // Show selected tab
                    document.getElementById(`${section}-${language}`).classList.add('active');
                    event.target.classList.add('active');
                }
            </script>
        </body>
        </html>
        """
        return web.Response(text=examples_html, content_type='text/html')

    def start(self) -> None:
        """Start the documentation server."""
        if not self.app:
            self.create_app()

        print(f"📚 Starting Vizly Enterprise API Documentation Server...")
        print(f"   URL: http://localhost:{self.port}")
        print(f"   Swagger UI: http://localhost:{self.port}/docs")
        print(f"   ReDoc: http://localhost:{self.port}/redoc")
        print(f"   Examples: http://localhost:{self.port}/examples")

        try:
            web.run_app(self.app, host='0.0.0.0', port=self.port)
        except KeyboardInterrupt:
            print("\n📚 Documentation server stopped")


def start_documentation_server(port: int = 8889) -> None:
    """Start interactive API documentation server."""
    server = DocumentationServer(port)
    server.start()