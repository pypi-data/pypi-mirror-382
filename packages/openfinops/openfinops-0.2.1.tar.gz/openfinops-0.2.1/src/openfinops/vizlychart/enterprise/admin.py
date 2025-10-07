"""
Enterprise User Management & Administration
==========================================

Administrative interfaces for enterprise user management, role assignment,
and organizational structure management.
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

import hashlib
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from .security import EnterpriseSecurityManager, SecurityLevel, Permission


@dataclass
class EnterpriseUser:
    """Enterprise user with extended attributes."""
    user_id: str
    username: str
    email: str
    roles: Set[str] = field(default_factory=set)
    security_clearance: SecurityLevel = SecurityLevel.INTERNAL
    department: Optional[str] = None
    manager_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    failed_login_attempts: int = 0
    password_hash: Optional[str] = None
    must_change_password: bool = False
    mfa_enabled: bool = False
    api_access_enabled: bool = False


@dataclass
class Organization:
    """Enterprise organization structure."""
    org_id: str
    name: str
    parent_id: Optional[str] = None
    users: Set[str] = field(default_factory=set)
    admin_users: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)


class UserManager:
    """
    Enterprise user management with LDAP/AD integration capabilities.

    Features:
    - User lifecycle management
    - Role-based permissions
    - Organization hierarchy
    - Password policy enforcement
    - Account security monitoring
    """

    def __init__(self, security_manager: Optional[EnterpriseSecurityManager] = None):
        self.security_manager = security_manager or EnterpriseSecurityManager()
        self.users: Dict[str, EnterpriseUser] = {}
        self.organizations: Dict[str, Organization] = {}
        self._load_demo_users()

    def create_user(self, username: str, role: str, email: Optional[str] = None,
                   department: Optional[str] = None) -> bool:
        """
        Create new enterprise user with role assignment.
        """
        try:
            if username in self.users:
                return False

            user = EnterpriseUser(
                user_id=str(uuid.uuid4()),
                username=username,
                email=email or f"{username}@company.com",
                roles={role},
                department=department,
                must_change_password=True  # Force password change on first login
            )

            # Set security clearance based on role
            if role == "super_admin":
                user.security_clearance = SecurityLevel.RESTRICTED
            elif role == "admin":
                user.security_clearance = SecurityLevel.CONFIDENTIAL
            elif role == "analyst":
                user.security_clearance = SecurityLevel.INTERNAL
            else:
                user.security_clearance = SecurityLevel.INTERNAL

            self.users[username] = user
            return True

        except Exception:
            return False

    def update_user_roles(self, username: str, roles: Set[str]) -> bool:
        """Update user role assignments."""
        if username not in self.users:
            return False

        self.users[username].roles = roles

        # Update security clearance based on highest role
        if "super_admin" in roles:
            self.users[username].security_clearance = SecurityLevel.RESTRICTED
        elif "admin" in roles:
            self.users[username].security_clearance = SecurityLevel.CONFIDENTIAL
        else:
            self.users[username].security_clearance = SecurityLevel.INTERNAL

        return True

    def deactivate_user(self, username: str) -> bool:
        """Deactivate user account."""
        if username not in self.users:
            return False

        self.users[username].is_active = False
        return True

    def list_users(self) -> List[Dict[str, str]]:
        """List all users with basic information."""
        return [
            {
                "username": user.username,
                "email": user.email,
                "role": ", ".join(user.roles),
                "department": user.department or "N/A",
                "last_login": user.last_login.isoformat() if user.last_login else "Never",
                "is_active": "Active" if user.is_active else "Inactive"
            }
            for user in self.users.values()
        ]

    def get_user_by_username(self, username: str) -> Optional[EnterpriseUser]:
        """Get user by username."""
        return self.users.get(username)

    def validate_password_policy(self, password: str) -> bool:
        """
        Validate password against enterprise policy.

        Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(password) < 12:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return has_upper and has_lower and has_digit and has_special

    def set_user_password(self, username: str, password: str) -> bool:
        """Set user password with policy validation."""
        if username not in self.users:
            return False

        if not self.validate_password_policy(password):
            return False

        # Hash password with salt
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)

        self.users[username].password_hash = f"{salt}:{password_hash.hex()}"
        self.users[username].must_change_password = False

        return True

    def record_login_attempt(self, username: str, success: bool) -> None:
        """Record login attempt for security monitoring."""
        if username in self.users:
            user = self.users[username]

            if success:
                user.last_login = datetime.utcnow()
                user.failed_login_attempts = 0
            else:
                user.failed_login_attempts += 1

                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.is_active = False

    def create_organization(self, name: str, parent_id: Optional[str] = None) -> str:
        """Create new organization unit."""
        org_id = str(uuid.uuid4())
        org = Organization(
            org_id=org_id,
            name=name,
            parent_id=parent_id
        )
        self.organizations[org_id] = org
        return org_id

    def add_user_to_organization(self, username: str, org_id: str) -> bool:
        """Add user to organization."""
        if username not in self.users or org_id not in self.organizations:
            return False

        self.organizations[org_id].users.add(username)
        return True

    def get_organization_users(self, org_id: str) -> List[EnterpriseUser]:
        """Get all users in organization."""
        if org_id not in self.organizations:
            return []

        org = self.organizations[org_id]
        return [self.users[username] for username in org.users if username in self.users]

    def _load_demo_users(self) -> None:
        """Load demonstration users for testing."""
        demo_users = [
            ("admin@company.com", "super_admin", "IT"),
            ("analyst@company.com", "analyst", "Analytics"),
            ("viewer@company.com", "viewer", "Sales"),
            ("manager@company.com", "admin", "Management")
        ]

        for username, role, dept in demo_users:
            self.create_user(username, role, username, dept)


class RoleManager:
    """
    Enterprise role and permission management.
    """

    def __init__(self):
        self.roles: Dict[str, Set[Permission]] = {
            "viewer": {Permission.READ},
            "analyst": {Permission.READ, Permission.WRITE},
            "admin": {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE},
            "super_admin": set(Permission),
        }

        self.custom_roles: Dict[str, Set[Permission]] = {}

    def create_custom_role(self, role_name: str, permissions: Set[Permission]) -> bool:
        """Create custom role with specific permissions."""
        if role_name in self.roles:
            return False

        self.custom_roles[role_name] = permissions
        return True

    def get_role_permissions(self, role_name: str) -> Set[Permission]:
        """Get permissions for a role."""
        if role_name in self.roles:
            return self.roles[role_name]
        elif role_name in self.custom_roles:
            return self.custom_roles[role_name]
        else:
            return set()

    def list_available_roles(self) -> List[str]:
        """List all available roles."""
        return list(self.roles.keys()) + list(self.custom_roles.keys())


class AuditManager:
    """
    Enterprise audit and compliance management.
    """

    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    def generate_user_access_report(self) -> Dict[str, List[Dict[str, str]]]:
        """Generate user access report for compliance."""
        report = {
            "active_users": [],
            "inactive_users": [],
            "privileged_users": [],
            "failed_login_users": []
        }

        for user in self.user_manager.users.values():
            user_info = {
                "username": user.username,
                "roles": ", ".join(user.roles),
                "security_clearance": user.security_clearance.value,
                "last_login": user.last_login.isoformat() if user.last_login else "Never"
            }

            if not user.is_active:
                report["inactive_users"].append(user_info)
            else:
                report["active_users"].append(user_info)

            if "admin" in user.roles or "super_admin" in user.roles:
                report["privileged_users"].append(user_info)

            if user.failed_login_attempts > 0:
                user_info["failed_attempts"] = str(user.failed_login_attempts)
                report["failed_login_users"].append(user_info)

        return report

    def check_password_compliance(self) -> Dict[str, List[str]]:
        """Check password policy compliance."""
        compliance_issues = {
            "must_change_password": [],
            "no_password_set": [],
            "mfa_disabled": []
        }

        for user in self.user_manager.users.values():
            if user.must_change_password:
                compliance_issues["must_change_password"].append(user.username)

            if not user.password_hash:
                compliance_issues["no_password_set"].append(user.username)

            if not user.mfa_enabled and "admin" in user.roles:
                compliance_issues["mfa_disabled"].append(user.username)

        return compliance_issues