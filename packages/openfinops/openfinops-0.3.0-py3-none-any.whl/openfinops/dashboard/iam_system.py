"""
Executive Dashboard IAM System
=============================

Role-based access control system for executive and operational dashboards
with fine-grained permissions for different organizational roles.
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



from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import json
import logging
from datetime import datetime, timedelta
import jwt
import bcrypt

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Access levels for data and functionality."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    EXECUTIVE = "executive"


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DashboardType(Enum):
    """Types of dashboards available."""
    CFO_EXECUTIVE = "cfo_executive"
    FINANCE_ANALYST = "finance_analyst"
    INFRASTRUCTURE_LEADER = "infrastructure_leader"
    COO_OPERATIONAL = "coo_operational"
    CTO_TECHNICAL = "cto_technical"
    CEO_STRATEGIC = "ceo_strategic"
    SECURITY_LEADER = "security_leader"
    DATA_SCIENTIST = "data_scientist"
    OPERATIONS_MANAGER = "operations_manager"


@dataclass
class Permission:
    """Individual permission definition."""
    name: str
    resource_type: str
    access_level: AccessLevel
    data_classification: DataClassification
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Role:
    """Role definition with permissions and constraints."""
    name: str
    display_name: str
    description: str
    permissions: List[Permission]
    allowed_dashboards: List[DashboardType]
    data_access_level: DataClassification
    session_timeout: int = 28800  # 8 hours default
    require_mfa: bool = False
    ip_restrictions: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class User:
    """User definition with role assignments."""
    user_id: str
    username: str
    email: str
    full_name: str
    department: str
    roles: List[str]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None


class IAMManager:
    """Identity and Access Management system for executive dashboards."""

    def __init__(self):
        self.roles = self._initialize_roles()
        self.users = {}
        self.active_sessions = {}
        self.audit_log = []

    def _initialize_roles(self) -> Dict[str, Role]:
        """Initialize predefined organizational roles."""

        roles = {}

        # CFO Role - Chief Financial Officer
        roles["cfo"] = Role(
            name="cfo",
            display_name="Chief Financial Officer",
            description="Executive financial oversight and strategic financial decision making",
            permissions=[
                Permission("view_financial_dashboards", "dashboard", AccessLevel.EXECUTIVE, DataClassification.RESTRICTED),
                Permission("view_all_costs", "financial_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_budgets", "budget_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("approve_budgets", "budget_data", AccessLevel.WRITE, DataClassification.RESTRICTED),
                Permission("view_financial_forecasts", "forecast_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("export_financial_reports", "reports", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_audit_trails", "audit_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_compliance_reports", "compliance_data", AccessLevel.READ, DataClassification.RESTRICTED),
            ],
            allowed_dashboards=[DashboardType.CFO_EXECUTIVE, DashboardType.CEO_STRATEGIC],
            data_access_level=DataClassification.RESTRICTED,
            require_mfa=True,
            session_timeout=14400  # 4 hours for security
        )

        # Finance Analyst Role
        roles["finance_analyst"] = Role(
            name="finance_analyst",
            display_name="Finance Analyst",
            description="Detailed financial analysis and reporting",
            permissions=[
                Permission("view_financial_dashboards", "dashboard", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_cost_analytics", "financial_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("create_financial_reports", "reports", AccessLevel.WRITE, DataClassification.CONFIDENTIAL),
                Permission("view_budget_details", "budget_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("analyze_cost_trends", "analytics", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("export_financial_data", "data_export", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_vendor_costs", "vendor_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
            ],
            allowed_dashboards=[DashboardType.FINANCE_ANALYST],
            data_access_level=DataClassification.CONFIDENTIAL
        )

        # Infrastructure Leader Role
        roles["infrastructure_leader"] = Role(
            name="infrastructure_leader",
            display_name="Infrastructure Leader",
            description="Technical infrastructure management and optimization",
            permissions=[
                Permission("view_infrastructure_dashboards", "dashboard", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_system_metrics", "system_data", AccessLevel.READ, DataClassification.INTERNAL),
                Permission("view_performance_data", "performance_data", AccessLevel.READ, DataClassification.INTERNAL),
                Permission("manage_infrastructure_alerts", "alerts", AccessLevel.WRITE, DataClassification.INTERNAL),
                Permission("view_resource_utilization", "resource_data", AccessLevel.READ, DataClassification.INTERNAL),
                Permission("view_infrastructure_costs", "cost_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("optimize_resources", "optimization", AccessLevel.WRITE, DataClassification.INTERNAL),
                Permission("view_security_metrics", "security_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
            ],
            allowed_dashboards=[DashboardType.INFRASTRUCTURE_LEADER],
            data_access_level=DataClassification.CONFIDENTIAL
        )

        # COO Role - Chief Operating Officer
        roles["coo"] = Role(
            name="coo",
            display_name="Chief Operating Officer",
            description="Operational excellence and business process optimization",
            permissions=[
                Permission("view_operational_dashboards", "dashboard", AccessLevel.EXECUTIVE, DataClassification.RESTRICTED),
                Permission("view_operational_metrics", "operational_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_efficiency_metrics", "efficiency_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_process_analytics", "process_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_team_performance", "team_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("approve_operational_changes", "operations", AccessLevel.WRITE, DataClassification.RESTRICTED),
                Permission("view_risk_assessments", "risk_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_compliance_status", "compliance_data", AccessLevel.READ, DataClassification.RESTRICTED),
            ],
            allowed_dashboards=[DashboardType.COO_OPERATIONAL, DashboardType.CEO_STRATEGIC],
            data_access_level=DataClassification.RESTRICTED,
            require_mfa=True
        )

        # CTO Role - Chief Technology Officer
        roles["cto"] = Role(
            name="cto",
            display_name="Chief Technology Officer",
            description="Technology strategy and technical leadership",
            permissions=[
                Permission("view_technical_dashboards", "dashboard", AccessLevel.EXECUTIVE, DataClassification.RESTRICTED),
                Permission("view_ai_ml_metrics", "ai_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_development_metrics", "dev_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_technology_costs", "tech_costs", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("approve_technical_initiatives", "tech_initiatives", AccessLevel.WRITE, DataClassification.RESTRICTED),
                Permission("view_innovation_metrics", "innovation_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_technical_risk", "tech_risk", AccessLevel.READ, DataClassification.RESTRICTED),
            ],
            allowed_dashboards=[DashboardType.CTO_TECHNICAL, DashboardType.CEO_STRATEGIC],
            data_access_level=DataClassification.RESTRICTED,
            require_mfa=True
        )

        # CEO Role - Chief Executive Officer
        roles["ceo"] = Role(
            name="ceo",
            display_name="Chief Executive Officer",
            description="Strategic oversight and executive decision making",
            permissions=[
                Permission("view_all_dashboards", "dashboard", AccessLevel.EXECUTIVE, DataClassification.RESTRICTED),
                Permission("view_strategic_metrics", "strategic_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_company_performance", "performance_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_financial_summary", "financial_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_operational_summary", "operational_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_board_reports", "board_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("approve_strategic_initiatives", "strategy", AccessLevel.WRITE, DataClassification.RESTRICTED),
            ],
            allowed_dashboards=[dash for dash in DashboardType],  # Access to all dashboards
            data_access_level=DataClassification.RESTRICTED,
            require_mfa=True,
            session_timeout=14400  # 4 hours
        )

        # Security Leader Role
        roles["security_leader"] = Role(
            name="security_leader",
            display_name="Security Leader",
            description="Security oversight and compliance management",
            permissions=[
                Permission("view_security_dashboards", "dashboard", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_security_metrics", "security_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_compliance_data", "compliance_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("manage_security_alerts", "security_alerts", AccessLevel.WRITE, DataClassification.RESTRICTED),
                Permission("view_audit_logs", "audit_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("view_risk_assessments", "risk_data", AccessLevel.READ, DataClassification.RESTRICTED),
                Permission("manage_access_controls", "iam", AccessLevel.ADMIN, DataClassification.RESTRICTED),
            ],
            allowed_dashboards=[DashboardType.SECURITY_LEADER],
            data_access_level=DataClassification.RESTRICTED,
            require_mfa=True
        )

        # Data Scientist Role
        roles["data_scientist"] = Role(
            name="data_scientist",
            display_name="Data Scientist",
            description="AI/ML model development and analysis",
            permissions=[
                Permission("view_data_science_dashboards", "dashboard", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_ml_metrics", "ml_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_model_performance", "model_data", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("create_ml_experiments", "experiments", AccessLevel.WRITE, DataClassification.CONFIDENTIAL),
                Permission("export_model_data", "data_export", AccessLevel.READ, DataClassification.CONFIDENTIAL),
                Permission("view_training_costs", "training_costs", AccessLevel.READ, DataClassification.INTERNAL),
            ],
            allowed_dashboards=[DashboardType.DATA_SCIENTIST],
            data_access_level=DataClassification.CONFIDENTIAL
        )

        # Operations Manager Role
        roles["operations_manager"] = Role(
            name="operations_manager",
            display_name="Operations Manager",
            description="Day-to-day operational management",
            permissions=[
                Permission("view_operations_dashboards", "dashboard", AccessLevel.READ, DataClassification.INTERNAL),
                Permission("view_operational_metrics", "ops_data", AccessLevel.READ, DataClassification.INTERNAL),
                Permission("manage_operational_alerts", "ops_alerts", AccessLevel.WRITE, DataClassification.INTERNAL),
                Permission("view_team_metrics", "team_data", AccessLevel.READ, DataClassification.INTERNAL),
                Permission("view_process_efficiency", "process_data", AccessLevel.READ, DataClassification.INTERNAL),
                Permission("create_operational_reports", "reports", AccessLevel.WRITE, DataClassification.INTERNAL),
            ],
            allowed_dashboards=[DashboardType.OPERATIONS_MANAGER],
            data_access_level=DataClassification.INTERNAL
        )

        return roles

    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user with role assignments."""
        user = User(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            department=user_data["department"],
            roles=user_data["roles"]
        )

        # Hash password if provided
        if "password" in user_data:
            user.password_hash = bcrypt.hashpw(
                user_data["password"].encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

        self.users[user.user_id] = user

        # Log user creation
        self._log_audit_event("user_created", user.user_id, {
            "username": user.username,
            "roles": user.roles,
            "department": user.department
        })

        return user

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token."""
        user = self.get_user_by_username(username)
        if not user or not user.is_active:
            self._log_audit_event("authentication_failed", username, {"reason": "user_not_found"})
            return None

        # Verify password
        if not user.password_hash or not bcrypt.checkpw(
            password.encode('utf-8'),
            user.password_hash.encode('utf-8')
        ):
            self._log_audit_event("authentication_failed", user.user_id, {"reason": "invalid_password"})
            return None

        # Update last login
        user.last_login = datetime.utcnow()

        # Generate JWT token
        token = self._generate_jwt_token(user)

        # Create session
        session_id = self._create_session(user, token)

        self._log_audit_event("authentication_success", user.user_id, {"session_id": session_id})

        return token

    def check_permission(self, user_id: str, permission_name: str, resource_type: str = None) -> bool:
        """Check if user has specific permission."""
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False

        # Get all permissions for user's roles
        user_permissions = self._get_user_permissions(user)

        # Check if permission exists
        for permission in user_permissions:
            if permission.name == permission_name:
                if resource_type is None or permission.resource_type == resource_type:
                    return True

        return False

    def can_access_dashboard(self, user_id: str, dashboard_type: DashboardType) -> bool:
        """Check if user can access specific dashboard type."""
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False

        # Get allowed dashboards for user's roles
        allowed_dashboards = set()
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                allowed_dashboards.update(role.allowed_dashboards)

        return dashboard_type in allowed_dashboards

    def get_user_data_access_level(self, user_id: str) -> DataClassification:
        """Get the highest data classification level user can access."""
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return DataClassification.PUBLIC

        highest_level = DataClassification.PUBLIC

        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                if role.data_access_level == DataClassification.RESTRICTED:
                    return DataClassification.RESTRICTED
                elif role.data_access_level == DataClassification.CONFIDENTIAL and highest_level != DataClassification.RESTRICTED:
                    highest_level = DataClassification.CONFIDENTIAL
                elif role.data_access_level == DataClassification.INTERNAL and highest_level == DataClassification.PUBLIC:
                    highest_level = DataClassification.INTERNAL

        return highest_level

    def _get_user_permissions(self, user: User) -> List[Permission]:
        """Get all permissions for a user based on their roles."""
        permissions = []

        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                permissions.extend(role.permissions)

        return permissions

    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for authenticated user."""

        # Get role information
        role_info = []
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                role_info.append({
                    "name": role.name,
                    "display_name": role.display_name,
                    "data_access_level": role.data_access_level.value
                })

        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "department": user.department,
            "roles": user.roles,
            "role_info": role_info,
            "data_access_level": self.get_user_data_access_level(user.user_id).value,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=28800)  # 8 hours default
        }

        # Use a secret key from environment or config
        secret_key = "your-secret-key"  # In production, use environment variable

        return jwt.encode(payload, secret_key, algorithm='HS256')

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            secret_key = "your-secret-key"  # Same key used for encoding
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])

            # Verify user still exists and is active
            user = self.users.get(payload["user_id"])
            if not user or not user.is_active:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None

    def _create_session(self, user: User, token: str) -> str:
        """Create user session."""
        import uuid
        session_id = str(uuid.uuid4())

        self.active_sessions[session_id] = {
            "user_id": user.user_id,
            "token": token,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "ip_address": None,  # Set by web framework
            "user_agent": None   # Set by web framework
        }

        return session_id

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def _log_audit_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Log audit event."""
        audit_entry = {
            "timestamp": datetime.utcnow(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }

        self.audit_log.append(audit_entry)
        logger.info(f"Audit event: {event_type} for user {user_id}")

    def get_role_hierarchy(self) -> Dict[str, List[str]]:
        """Get role hierarchy for permission inheritance."""
        return {
            "ceo": ["cfo", "coo", "cto", "security_leader"],
            "cfo": ["finance_analyst"],
            "coo": ["operations_manager"],
            "cto": ["infrastructure_leader", "data_scientist"],
            "security_leader": [],
            "finance_analyst": [],
            "infrastructure_leader": [],
            "data_scientist": [],
            "operations_manager": []
        }

    def export_iam_configuration(self) -> Dict[str, Any]:
        """Export IAM configuration for backup or migration."""
        return {
            "roles": {name: {
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "permissions": [
                    {
                        "name": p.name,
                        "resource_type": p.resource_type,
                        "access_level": p.access_level.value,
                        "data_classification": p.data_classification.value,
                        "conditions": p.conditions
                    } for p in role.permissions
                ],
                "allowed_dashboards": [d.value for d in role.allowed_dashboards],
                "data_access_level": role.data_access_level.value,
                "session_timeout": role.session_timeout,
                "require_mfa": role.require_mfa
            } for name, role in self.roles.items()},
            "users": {user_id: {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "department": user.department,
                "roles": user.roles,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "mfa_enabled": user.mfa_enabled
            } for user_id, user in self.users.items()}
        }


# Global IAM instance
iam_manager = IAMManager()


def get_iam_manager() -> IAMManager:
    """Get global IAM manager instance."""
    return iam_manager