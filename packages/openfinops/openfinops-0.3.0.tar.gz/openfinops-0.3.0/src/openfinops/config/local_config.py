"""
OpenFinOps Local Configuration
============================

Central configuration for localhost-only deployment.
All external endpoints replaced with local equivalents.
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
from pathlib import Path


class LocalConfig:
    """Local configuration for OpenFinOps"""

    # Base server configuration
    BASE_URL = "http://localhost:8080"
    HOST = "127.0.0.1"
    PORT = 8080

    # Database configuration - Multi-RDBMS support
    DATABASE_CONFIG = {
        "type": "sqlite",  # sqlite, postgresql, mysql, mariadb, oracle, mssql
        "path": "openfinops_local.db",  # For SQLite
        "host": "localhost",
        "port": None,  # Will use defaults based on type
        "database": "openfinops",
        "username": "openfinops",
        "password": "",
        "charset": "utf8mb4",  # For MySQL/MariaDB
        "service_name": "XE",  # For Oracle
        "driver": "ODBC Driver 17 for SQL Server",  # For SQL Server
        "connection_string": None,  # Custom connection string
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "connect_timeout": 30,
        "echo": False,  # SQL query logging
        "ssl_mode": "prefer",  # For PostgreSQL
        "ssl_cert": None,
        "ssl_key": None,
        "ssl_ca": None
    }

    # Legacy compatibility
    DATABASE_URL = "sqlite:///openfinops_local.db"
    DATABASE_PATH = Path.cwd() / "openfinops_local.db"

    # API endpoints (all local)
    API_ENDPOINTS = {
        "telemetry_ingest": f"{BASE_URL}/api/v1/telemetry/ingest",
        "agent_registration": f"{BASE_URL}/api/v1/agents/register",
        "cost_management": f"{BASE_URL}/api/v1/cost-management",
        "erp_system": f"{BASE_URL}/api/v1/erp",
        "treasury_system": f"{BASE_URL}/api/v1/treasury",
        "financial_data": f"{BASE_URL}/api/v1/financial",
        "infrastructure_metrics": f"{BASE_URL}/api/v1/infrastructure",
        "operations_data": f"{BASE_URL}/api/v1/operations"
    }

    # Dashboard URLs
    DASHBOARD_URLS = {
        "cfo": f"{BASE_URL}/dashboard/cfo",
        "finance_analyst": f"{BASE_URL}/dashboard/finance_analyst",
        "infrastructure_leader": f"{BASE_URL}/dashboard/infrastructure_leader",
        "coo": f"{BASE_URL}/dashboard/coo",
        "home": f"{BASE_URL}/dashboard",
        "login": f"{BASE_URL}/auth/login"
    }

    # Telemetry configuration
    TELEMETRY_CONFIG = {
        "endpoint": f"{BASE_URL}/api/v1/telemetry/ingest",
        "registration_endpoint": f"{BASE_URL}/api/v1/agents/register",
        "health_check_endpoint": f"{BASE_URL}/health",
        "timeout": 30,
        "retry_attempts": 3,
        "heartbeat_interval": 300,
        "metrics_interval": 60,
        "buffer_size": 1000
    }

    # Local AI/ML configuration
    AI_CONFIG = {
        "local_models": True,
        "model_storage": Path.cwd() / "models",
        "inference_endpoint": f"{BASE_URL}/api/v1/inference",
        "training_endpoint": f"{BASE_URL}/api/v1/training",
        "model_registry": f"{BASE_URL}/api/v1/models"
    }

    # Security configuration
    SECURITY_CONFIG = {
        "api_key": "local-development-key",
        "jwt_secret": "local-jwt-secret-key",
        "session_timeout": 3600,
        "enable_authentication": True,
        "enable_audit_log": True
    }

    # Cloud provider local configuration
    CLOUD_CONFIG = {
        "aws": {
            "endpoint": f"{BASE_URL}/api/v1/cloud/aws",
            "credentials_file": "~/.aws/credentials",
            "cost_api": f"{BASE_URL}/api/v1/cloud/aws/costs"
        },
        "gcp": {
            "endpoint": f"{BASE_URL}/api/v1/cloud/gcp",
            "credentials_file": "~/.gcp/credentials.json",
            "cost_api": f"{BASE_URL}/api/v1/cloud/gcp/costs"
        },
        "azure": {
            "endpoint": f"{BASE_URL}/api/v1/cloud/azure",
            "credentials_file": "~/.azure/credentials",
            "cost_api": f"{BASE_URL}/api/v1/cloud/azure/costs"
        }
    }

    # Monitoring configuration
    MONITORING_CONFIG = {
        "control_tower_endpoint": f"{BASE_URL}/api/v1/control-tower",
        "health_checks": [
            f"{BASE_URL}/health",
            f"{BASE_URL}/api/v1/agents",
            f"{BASE_URL}/api/v1/metrics/summary"
        ],
        "alert_endpoint": f"{BASE_URL}/api/v1/alerts",
        "incident_endpoint": f"{BASE_URL}/api/v1/incidents"
    }

    # Static assets (embedded)
    STATIC_CONFIG = {
        "css_endpoint": f"{BASE_URL}/static/style.css",
        "js_endpoint": f"{BASE_URL}/static/app.js",
        "favicon": f"{BASE_URL}/static/favicon.ico",
        "logo": f"{BASE_URL}/static/logo.png"
    }

    @classmethod
    def get_telemetry_config(cls, agent_id: str = None) -> dict:
        """Get telemetry configuration for agents"""
        config = cls.TELEMETRY_CONFIG.copy()
        if agent_id:
            config["agent_id"] = agent_id
        return config

    @classmethod
    def get_dashboard_config(cls, role: str) -> dict:
        """Get dashboard configuration for specific role"""
        role_key = role.lower()
        if role_key in cls.DASHBOARD_URLS:
            return {
                "dashboard_url": cls.DASHBOARD_URLS[role_key],
                "api_endpoint": f"{cls.BASE_URL}/api/v1/dashboard/{role_key}/data",
                "refresh_interval": 120000,  # 2 minutes
                "auto_refresh": True
            }
        return cls.get_default_dashboard_config()

    @classmethod
    def get_default_dashboard_config(cls) -> dict:
        """Get default dashboard configuration"""
        return {
            "dashboard_url": cls.DASHBOARD_URLS["home"],
            "api_endpoint": f"{cls.BASE_URL}/api/v1/dashboard/status",
            "refresh_interval": 60000,  # 1 minute
            "auto_refresh": True
        }

    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration"""
        return cls.DATABASE_CONFIG.copy()

    @classmethod
    def update_database_config(cls, **kwargs):
        """Update database configuration"""
        for key, value in kwargs.items():
            if key in cls.DATABASE_CONFIG:
                cls.DATABASE_CONFIG[key] = value

    @classmethod
    def validate_config(cls) -> bool:
        """Validate local configuration"""
        try:
            # For SQLite, check if database path is writable
            if cls.DATABASE_CONFIG["type"] == "sqlite":
                db_path = Path(cls.DATABASE_CONFIG["path"])
                db_path.parent.mkdir(exist_ok=True)

            # Check if model storage exists
            if cls.AI_CONFIG["local_models"]:
                cls.AI_CONFIG["model_storage"].mkdir(exist_ok=True)

            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False

    @classmethod
    def get_environment_info(cls) -> dict:
        """Get environment information"""
        return {
            "deployment_type": "localhost",
            "external_dependencies": False,
            "internet_required": False,
            "database_type": cls.DATABASE_CONFIG["type"],
            "database_config": cls.get_database_config(),
            "base_url": cls.BASE_URL,
            "config_valid": cls.validate_config()
        }


# Export configuration instance
config = LocalConfig()


def get_config():
    """Get the local configuration instance"""
    return config


def update_base_url(new_host: str, new_port: int):
    """Update base URL for different host/port"""
    LocalConfig.BASE_URL = f"http://{new_host}:{new_port}"
    LocalConfig.HOST = new_host
    LocalConfig.PORT = new_port

    # Update all endpoint URLs
    base_url = LocalConfig.BASE_URL

    LocalConfig.API_ENDPOINTS.update({
        "telemetry_ingest": f"{base_url}/api/v1/telemetry/ingest",
        "agent_registration": f"{base_url}/api/v1/agents/register",
        "cost_management": f"{base_url}/api/v1/cost-management",
        "erp_system": f"{base_url}/api/v1/erp",
        "treasury_system": f"{base_url}/api/v1/treasury",
        "financial_data": f"{base_url}/api/v1/financial",
        "infrastructure_metrics": f"{base_url}/api/v1/infrastructure",
        "operations_data": f"{base_url}/api/v1/operations"
    })

    LocalConfig.DASHBOARD_URLS.update({
        "cfo": f"{base_url}/dashboard/cfo",
        "finance_analyst": f"{base_url}/dashboard/finance_analyst",
        "infrastructure_leader": f"{base_url}/dashboard/infrastructure_leader",
        "coo": f"{base_url}/dashboard/coo",
        "home": f"{base_url}/dashboard",
        "login": f"{base_url}/auth/login"
    })

    LocalConfig.TELEMETRY_CONFIG.update({
        "endpoint": f"{base_url}/api/v1/telemetry/ingest",
        "registration_endpoint": f"{base_url}/api/v1/agents/register",
        "health_check_endpoint": f"{base_url}/health"
    })


# Utility functions for backward compatibility
def get_api_endpoint(service: str) -> str:
    """Get API endpoint for a service"""
    return LocalConfig.API_ENDPOINTS.get(service, LocalConfig.BASE_URL)


def get_dashboard_url(role: str) -> str:
    """Get dashboard URL for a role"""
    return LocalConfig.DASHBOARD_URLS.get(role.lower(), LocalConfig.DASHBOARD_URLS["home"])


def get_telemetry_endpoint() -> str:
    """Get telemetry ingestion endpoint"""
    return LocalConfig.TELEMETRY_CONFIG["endpoint"]


if __name__ == "__main__":
    # Print configuration summary
    print("🏗️ OpenFinOps Local Configuration")
    print("=" * 40)
    print(f"Base URL: {LocalConfig.BASE_URL}")
    print(f"Database: {LocalConfig.DATABASE_URL}")
    print(f"Host: {LocalConfig.HOST}:{LocalConfig.PORT}")
    print()
    print("📡 API Endpoints:")
    for name, url in LocalConfig.API_ENDPOINTS.items():
        print(f"  {name}: {url}")
    print()
    print("📊 Dashboard URLs:")
    for name, url in LocalConfig.DASHBOARD_URLS.items():
        print(f"  {name}: {url}")
    print()
    print("✅ Configuration validated:", LocalConfig.validate_config())