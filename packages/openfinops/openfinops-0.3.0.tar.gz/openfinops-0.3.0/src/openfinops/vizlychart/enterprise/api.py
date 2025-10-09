"""
Enterprise API Framework
========================

Comprehensive API framework for enterprise integration including
SDKs, client libraries, and developer tools.
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
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    warnings.warn("requests library not available. Install with: pip install requests")

from .charts import ChartMetadata, EnterpriseChartFactory
from .security import SecurityLevel
from .licensing import LicenseFeature


@dataclass
class APIResponse:
    """Standardized API response wrapper."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIEndpoint:
    """API endpoint definition."""
    path: str
    method: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    requires_auth: bool = True
    required_permissions: List[str] = field(default_factory=list)
    required_license: Optional[LicenseFeature] = None


class VizlyEnterpriseClient:
    """
    Python SDK for Vizly Enterprise API.

    Provides a high-level interface for creating charts, managing users,
    and accessing enterprise features programmatically.
    """

    def __init__(self, base_url: str = "http://localhost:8888",
                 api_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for API client. Install with: pip install requests")

        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.token: Optional[str] = None

        # Set up authentication
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        elif username and password:
            self.authenticate(username, password)

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with username and password."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    return True

            return False
        except Exception:
            return False

    def health_check(self) -> APIResponse:
        """Check server health status."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return APIResponse(
                success=response.status_code == 200,
                data=response.json() if response.status_code == 200 else None,
                status_code=response.status_code
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500)

    def get_metrics(self) -> APIResponse:
        """Get system metrics."""
        try:
            response = self.session.get(f"{self.base_url}/metrics")
            return APIResponse(
                success=response.status_code == 200,
                data=response.json() if response.status_code == 200 else None,
                status_code=response.status_code
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500)

    def create_chart(self, chart_type: str, title: str,
                    data: Optional[Dict[str, Any]] = None,
                    security_level: str = "internal",
                    compliance_tags: Optional[List[str]] = None) -> APIResponse:
        """
        Create enterprise chart via API.

        Args:
            chart_type: Type of chart ('executive_dashboard', 'financial_analytics', etc.)
            title: Chart title
            data: Chart-specific data (KPIs, metrics, etc.)
            security_level: Security classification
            compliance_tags: Compliance tags for governance
        """
        try:
            payload = {
                "type": chart_type,
                "title": title,
                "security_level": security_level,
                "compliance_tags": compliance_tags or []
            }

            if data:
                payload.update(data)

            response = self.session.post(
                f"{self.base_url}/api/charts",
                json=payload
            )

            return APIResponse(
                success=response.status_code == 200,
                data=response.json() if response.status_code == 200 else None,
                error=response.json().get("error") if response.status_code != 200 else None,
                status_code=response.status_code
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500)

    def get_chart(self, chart_id: str) -> APIResponse:
        """Get chart details by ID."""
        try:
            response = self.session.get(f"{self.base_url}/api/charts/{chart_id}")
            return APIResponse(
                success=response.status_code == 200,
                data=response.json() if response.status_code == 200 else None,
                error=response.json().get("error") if response.status_code != 200 else None,
                status_code=response.status_code
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500)

    def list_charts(self) -> APIResponse:
        """List all charts."""
        try:
            response = self.session.get(f"{self.base_url}/api/charts")
            return APIResponse(
                success=response.status_code == 200,
                data=response.json() if response.status_code == 200 else None,
                status_code=response.status_code
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500)

    def list_users(self) -> APIResponse:
        """List users (admin only)."""
        try:
            response = self.session.get(f"{self.base_url}/api/users")
            return APIResponse(
                success=response.status_code == 200,
                data=response.json() if response.status_code == 200 else None,
                error=response.json().get("error") if response.status_code != 200 else None,
                status_code=response.status_code
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500)

    def create_user(self, username: str, role: str = "viewer") -> APIResponse:
        """Create new user (admin only)."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/users",
                json={"username": username, "role": role}
            )
            return APIResponse(
                success=response.status_code == 200,
                data=response.json() if response.status_code == 200 else None,
                error=response.json().get("error") if response.status_code != 200 else None,
                status_code=response.status_code
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e), status_code=500)


class APIDocumentationGenerator:
    """
    Generate comprehensive API documentation with OpenAPI/Swagger support.
    """

    def __init__(self):
        self.endpoints: List[APIEndpoint] = []
        self._register_default_endpoints()

    def _register_default_endpoints(self) -> None:
        """Register all enterprise API endpoints."""

        # Health and metrics
        self.endpoints.extend([
            APIEndpoint(
                path="/health",
                method="GET",
                description="Check server health and service status",
                requires_auth=False,
                response_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "timestamp": {"type": "number"},
                        "version": {"type": "string"},
                        "services": {"type": "object"}
                    }
                }
            ),
            APIEndpoint(
                path="/metrics",
                method="GET",
                description="Get system performance metrics",
                requires_auth=False,
                response_schema={
                    "type": "object",
                    "properties": {
                        "cpu_usage": {"type": "number"},
                        "memory_usage": {"type": "number"},
                        "active_sessions": {"type": "integer"},
                        "total_users": {"type": "integer"}
                    }
                }
            )
        ])

        # Authentication
        self.endpoints.append(
            APIEndpoint(
                path="/api/auth/login",
                method="POST",
                description="Authenticate user and obtain JWT token",
                requires_auth=False,
                request_schema={
                    "type": "object",
                    "required": ["username", "password"],
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    }
                },
                response_schema={
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"},
                        "user_id": {"type": "string"},
                        "roles": {"type": "array", "items": {"type": "string"}},
                        "expires_at": {"type": "string"}
                    }
                }
            )
        )

        # Chart management
        self.endpoints.extend([
            APIEndpoint(
                path="/api/charts",
                method="GET",
                description="List all accessible charts",
                required_permissions=["read"],
                response_schema={
                    "type": "object",
                    "properties": {
                        "charts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "type": {"type": "string"},
                                    "created_at": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            ),
            APIEndpoint(
                path="/api/charts",
                method="POST",
                description="Create new enterprise chart",
                required_permissions=["write"],
                required_license=LicenseFeature.ADVANCED_CHARTS,
                request_schema={
                    "type": "object",
                    "required": ["type", "title"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["executive_dashboard", "financial_analytics", "compliance", "risk_analysis"]
                        },
                        "title": {"type": "string"},
                        "security_level": {
                            "type": "string",
                            "enum": ["public", "internal", "confidential", "restricted"],
                            "default": "internal"
                        },
                        "compliance_tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "kpis": {"type": "object"},
                        "metrics": {"type": "object"}
                    }
                },
                response_schema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "type": {"type": "string"},
                        "security_level": {"type": "string"},
                        "compliance_tags": {"type": "array"},
                        "audit_trail_count": {"type": "integer"}
                    }
                }
            ),
            APIEndpoint(
                path="/api/charts/{chart_id}",
                method="GET",
                description="Get chart details by ID",
                required_permissions=["read"],
                parameters={
                    "chart_id": {
                        "type": "string",
                        "description": "Unique chart identifier"
                    }
                }
            )
        ])

        # User management
        self.endpoints.extend([
            APIEndpoint(
                path="/api/users",
                method="GET",
                description="List all users (admin only)",
                required_permissions=["admin"],
                response_schema={
                    "type": "object",
                    "properties": {
                        "users": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "email": {"type": "string"},
                                    "role": {"type": "string"},
                                    "department": {"type": "string"},
                                    "last_login": {"type": "string"},
                                    "is_active": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            ),
            APIEndpoint(
                path="/api/users",
                method="POST",
                description="Create new user (admin only)",
                required_permissions=["admin"],
                request_schema={
                    "type": "object",
                    "required": ["username", "role"],
                    "properties": {
                        "username": {"type": "string"},
                        "role": {
                            "type": "string",
                            "enum": ["viewer", "analyst", "admin", "super_admin"]
                        }
                    }
                }
            )
        ])

    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Vizly Enterprise API",
                "description": "Enterprise visualization platform with advanced security and analytics",
                "version": "1.0.0",
                "contact": {
                    "name": "Vizly Enterprise Support",
                    "email": "enterprise@vizly.com"
                },
                "license": {
                    "name": "Enterprise License",
                    "url": "https://vizly.com/enterprise/license"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8888",
                    "description": "Development server"
                },
                {
                    "url": "https://api.vizly-enterprise.com",
                    "description": "Production server"
                }
            ],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                },
                "schemas": {}
            },
            "paths": {}
        }

        # Add paths
        for endpoint in self.endpoints:
            path_key = endpoint.path

            if path_key not in spec["paths"]:
                spec["paths"][path_key] = {}

            method_spec = {
                "summary": endpoint.description,
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema or {"type": "object"}
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }

            # Add authentication requirement
            if endpoint.requires_auth:
                method_spec["security"] = [{"bearerAuth": []}]
                method_spec["responses"]["401"] = {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"}
                                }
                            }
                        }
                    }
                }

            # Add request body for POST/PUT methods
            if endpoint.method.upper() in ["POST", "PUT"] and endpoint.request_schema:
                method_spec["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }

            # Add parameters
            if endpoint.parameters:
                method_spec["parameters"] = []
                for param_name, param_spec in endpoint.parameters.items():
                    method_spec["parameters"].append({
                        "name": param_name,
                        "in": "path",
                        "required": True,
                        "schema": {"type": param_spec.get("type", "string")},
                        "description": param_spec.get("description", "")
                    })

            spec["paths"][path_key][endpoint.method.lower()] = method_spec

        return spec

    def generate_markdown_docs(self) -> str:
        """Generate comprehensive Markdown documentation."""
        docs = """# Vizly Enterprise API Documentation

## Overview

The Vizly Enterprise API provides comprehensive access to enterprise visualization capabilities including chart creation, user management, and security features.

## Authentication

The API uses JWT-based authentication. Obtain a token by posting credentials to `/api/auth/login`:

```bash
curl -X POST http://localhost:8888/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "your-username", "password": "your-password"}'
```

Include the token in subsequent requests:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  http://localhost:8888/api/charts
```

## Quick Start

### Python SDK

```python
from vizly.enterprise.api import VizlyEnterpriseClient

# Initialize client
client = VizlyEnterpriseClient(
    base_url="http://localhost:8888",
    username="admin@company.com",
    password="your-password"
)

# Create executive dashboard
response = client.create_chart(
    chart_type="executive_dashboard",
    title="Q4 Performance Dashboard",
    data={
        "kpis": {
            "Revenue": {"value": 1200000, "target": 1000000, "status": "good"},
            "Profit": {"value": 180000, "target": 150000, "status": "good"}
        }
    },
    security_level="confidential",
    compliance_tags=["SOX", "Executive Reporting"]
)

print(f"Chart created: {response.data['id']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

class VizlyClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = { 'Authorization': `Bearer ${token}` };
    }

    async createChart(chartData) {
        const response = await axios.post(
            `${this.baseUrl}/api/charts`,
            chartData,
            { headers: this.headers }
        );
        return response.data;
    }
}

// Usage
const client = new VizlyClient('http://localhost:8888', 'your-jwt-token');
const chart = await client.createChart({
    type: 'executive_dashboard',
    title: 'Sales Dashboard',
    security_level: 'internal'
});
```

## API Endpoints

"""

        # Group endpoints by category
        categories = {
            "System": [e for e in self.endpoints if e.path.startswith(('/health', '/metrics'))],
            "Authentication": [e for e in self.endpoints if 'auth' in e.path],
            "Charts": [e for e in self.endpoints if '/api/charts' in e.path],
            "Users": [e for e in self.endpoints if '/api/users' in e.path]
        }

        for category, endpoints in categories.items():
            docs += f"\n### {category}\n\n"

            for endpoint in endpoints:
                docs += f"#### `{endpoint.method.upper()} {endpoint.path}`\n\n"
                docs += f"{endpoint.description}\n\n"

                if endpoint.required_permissions:
                    docs += f"**Required Permissions:** {', '.join(endpoint.required_permissions)}\n\n"

                if endpoint.required_license:
                    docs += f"**Required License:** {endpoint.required_license.value}\n\n"

                if endpoint.request_schema:
                    docs += "**Request Body:**\n```json\n"
                    docs += json.dumps(endpoint.request_schema, indent=2)
                    docs += "\n```\n\n"

                if endpoint.response_schema:
                    docs += "**Response:**\n```json\n"
                    docs += json.dumps(endpoint.response_schema, indent=2)
                    docs += "\n```\n\n"

                # Add curl example
                docs += "**Example:**\n```bash\n"
                if endpoint.method.upper() == "GET":
                    auth_header = " \\\n  -H \"Authorization: Bearer YOUR_JWT_TOKEN\"" if endpoint.requires_auth else ""
                    docs += f"curl{auth_header} \\\n  {endpoint.path.replace('{chart_id}', '123')}\n"
                else:
                    auth_header = " \\\n  -H \"Authorization: Bearer YOUR_JWT_TOKEN\"" if endpoint.requires_auth else ""
                    docs += f"curl -X {endpoint.method.upper()}{auth_header} \\\n"
                    docs += f"  -H \"Content-Type: application/json\" \\\n"
                    if endpoint.request_schema:
                        example_data = self._generate_example_data(endpoint.request_schema)
                        docs += f"  -d '{json.dumps(example_data)}' \\\n"
                    docs += f"  {endpoint.path}\n"
                docs += "```\n\n"

        docs += """
## Chart Types

### Executive Dashboard
Create KPI dashboards with status indicators and progress tracking.

```python
client.create_chart(
    chart_type="executive_dashboard",
    title="Executive KPI Dashboard",
    data={
        "kpis": {
            "Revenue": {"value": 1500000, "target": 1400000, "status": "good"},
            "Customer Satisfaction": {"value": 87, "target": 90, "status": "warning"},
            "Market Share": {"value": 12.5, "status": "neutral"}
        }
    }
)
```

### Financial Analytics
Waterfall charts and variance analysis for financial reporting.

```python
client.create_chart(
    chart_type="financial_analytics",
    title="Revenue Analysis",
    data={
        "categories": ["Q1", "Q2 Growth", "Q3 Decline", "Q4", "Total"],
        "values": [1000000, 250000, -180000, 320000, 1390000]
    }
)
```

### Compliance Scorecard
Traffic light scorecards for compliance monitoring.

```python
client.create_chart(
    chart_type="compliance",
    title="Compliance Dashboard",
    data={
        "metrics": {
            "Data Protection": {"score": 95, "threshold_good": 90},
            "Security": {"score": 88, "threshold_good": 90},
            "Audit Readiness": {"score": 76, "threshold_good": 90}
        }
    }
)
```

### Risk Analysis
Risk matrices and probability analysis.

```python
client.create_chart(
    chart_type="risk_analysis",
    title="Enterprise Risk Matrix",
    data={
        "risks": [
            {"name": "Cyber Security", "probability": 70, "impact": 85, "category": "Technology"},
            {"name": "Market Volatility", "probability": 60, "impact": 70, "category": "Financial"}
        ]
    }
)
```

## Error Handling

All API responses follow a consistent format:

```json
{
    "success": true,
    "data": {...},
    "error": null,
    "status_code": 200,
    "metadata": {...}
}
```

Common error codes:
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting:
- 1000 requests per minute per IP address
- Rate limit headers included in responses
- Exceeded limits return HTTP 429

## Security

- All data transmission encrypted via HTTPS in production
- JWT tokens expire after 8 hours
- Role-based access control (RBAC)
- Data classification and security watermarks
- Comprehensive audit logging

## Support

- Documentation: https://docs.vizly.com/enterprise
- Support: enterprise@vizly.com
- Status Page: https://status.vizly.com
"""

        return docs

    def _generate_example_data(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example data from JSON schema."""
        if schema.get("type") != "object":
            return {}

        example = {}
        properties = schema.get("properties", {})

        for prop, prop_schema in properties.items():
            prop_type = prop_schema.get("type", "string")

            if prop_type == "string":
                if "enum" in prop_schema:
                    example[prop] = prop_schema["enum"][0]
                else:
                    example[prop] = f"example_{prop}"
            elif prop_type == "integer":
                example[prop] = 123
            elif prop_type == "number":
                example[prop] = 123.45
            elif prop_type == "boolean":
                example[prop] = True
            elif prop_type == "array":
                example[prop] = ["example_item"]
            elif prop_type == "object":
                example[prop] = {"example_key": "example_value"}

        return example


def generate_api_documentation(output_dir: str = "docs/api") -> None:
    """Generate complete API documentation suite."""
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate documentation
    doc_generator = APIDocumentationGenerator()

    # OpenAPI spec
    openapi_spec = doc_generator.generate_openapi_spec()
    with open(output_path / "openapi.json", "w") as f:
        json.dump(openapi_spec, f, indent=2)

    # Markdown docs
    markdown_docs = doc_generator.generate_markdown_docs()
    with open(output_path / "README.md", "w") as f:
        f.write(markdown_docs)

    print(f"📚 API documentation generated in {output_path}")
    print(f"   - OpenAPI spec: {output_path}/openapi.json")
    print(f"   - Markdown docs: {output_path}/README.md")