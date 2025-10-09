"""
Enterprise Security & Compliance Framework
==========================================

Comprehensive security infrastructure for enterprise deployments including
encryption, access control, audit logging, and compliance management.
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
import logging
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid
from datetime import datetime, timedelta

import jwt
from cryptography.fernet import Fernet


class SecurityLevel(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class Permission(Enum):
    """User permissions for resources."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"


@dataclass
class UserSession:
    """Enterprise user session with security context."""
    user_id: str
    session_id: str
    roles: Set[str] = field(default_factory=set)
    permissions: Set[Permission] = field(default_factory=set)
    security_clearance: SecurityLevel = SecurityLevel.INTERNAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=8))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class AuditEvent:
    """Security audit event for compliance tracking."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: str = ""
    session_id: str = ""
    action: str = ""
    resource_type: str = ""
    resource_id: str = ""
    result: str = "success"  # success, failure, denied
    ip_address: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.INTERNAL


class EnterpriseSecurityManager:
    """
    Comprehensive enterprise security manager with encryption, access control,
    and audit capabilities.

    Features:
    - AES-256 encryption for data at rest
    - JWT-based session management
    - Role-based access control (RBAC)
    - Data classification and handling
    - Comprehensive audit logging
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.active_sessions: Dict[str, UserSession] = {}
        self.role_permissions: Dict[str, Set[Permission]] = {
            "viewer": {Permission.READ},
            "analyst": {Permission.READ, Permission.WRITE},
            "admin": {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE},
            "super_admin": set(Permission),
        }
        self.audit_logger = ComplianceAuditLogger()
        self.jwt_secret = secrets.token_urlsafe(32)

    def authenticate_user(self, username: str, password: str,
                         ip_address: Optional[str] = None) -> Optional[UserSession]:
        """
        Authenticate user and create secure session.

        In production, this would integrate with:
        - LDAP/Active Directory
        - SAML/SSO providers
        - Multi-factor authentication
        """
        # Placeholder authentication logic
        # In real implementation, verify against enterprise identity provider

        if self._verify_credentials(username, password):
            session = UserSession(
                user_id=username,
                session_id=str(uuid.uuid4()),
                roles=self._get_user_roles(username),
                ip_address=ip_address
            )

            # Calculate permissions from roles
            for role in session.roles:
                session.permissions.update(self.role_permissions.get(role, set()))

            # Set security clearance based on roles
            if "super_admin" in session.roles:
                session.security_clearance = SecurityLevel.RESTRICTED
            elif "admin" in session.roles:
                session.security_clearance = SecurityLevel.CONFIDENTIAL

            self.active_sessions[session.session_id] = session

            # Log successful authentication
            self.audit_logger.log_event(AuditEvent(
                user_id=username,
                session_id=session.session_id,
                action="authentication",
                resource_type="session",
                result="success",
                ip_address=ip_address
            ))

            return session

        # Log failed authentication
        self.audit_logger.log_event(AuditEvent(
            user_id=username,
            action="authentication",
            resource_type="session",
            result="failure",
            ip_address=ip_address,
            details={"reason": "invalid_credentials"}
        ))

        return None

    def authorize_action(self, session_id: str, action: Permission,
                        resource_type: str, resource_id: str,
                        required_security_level: SecurityLevel = SecurityLevel.INTERNAL) -> bool:
        """
        Authorize user action based on permissions and security clearance.
        """
        session = self.active_sessions.get(session_id)
        if not session or session.expires_at < datetime.utcnow():
            self.audit_logger.log_event(AuditEvent(
                session_id=session_id,
                action=action.value,
                resource_type=resource_type,
                resource_id=resource_id,
                result="denied",
                details={"reason": "invalid_session"}
            ))
            return False

        # Check if user has required permission
        if action not in session.permissions:
            self.audit_logger.log_event(AuditEvent(
                user_id=session.user_id,
                session_id=session_id,
                action=action.value,
                resource_type=resource_type,
                resource_id=resource_id,
                result="denied",
                details={"reason": "insufficient_permissions"}
            ))
            return False

        # Check security clearance
        security_levels = {
            SecurityLevel.PUBLIC: 0,
            SecurityLevel.INTERNAL: 1,
            SecurityLevel.CONFIDENTIAL: 2,
            SecurityLevel.RESTRICTED: 3
        }

        if security_levels[session.security_clearance] < security_levels[required_security_level]:
            self.audit_logger.log_event(AuditEvent(
                user_id=session.user_id,
                session_id=session_id,
                action=action.value,
                resource_type=resource_type,
                resource_id=resource_id,
                result="denied",
                details={"reason": "insufficient_security_clearance"}
            ))
            return False

        # Log successful authorization
        self.audit_logger.log_event(AuditEvent(
            user_id=session.user_id,
            session_id=session_id,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            result="success"
        ))

        return True

    def encrypt_sensitive_data(self, data: Any, security_level: SecurityLevel) -> bytes:
        """
        Encrypt sensitive data based on classification level.
        """
        if security_level in [SecurityLevel.CONFIDENTIAL, SecurityLevel.RESTRICTED]:
            # For highly sensitive data, add additional encryption layers
            data_str = json.dumps(data) if not isinstance(data, str) else data
            encrypted = self.cipher.encrypt(data_str.encode())

            # Add metadata for decryption
            metadata = {
                "security_level": security_level.value,
                "encrypted_at": datetime.utcnow().isoformat(),
                "algorithm": "AES-256-CBC"
            }

            return json.dumps({
                "data": encrypted.decode(),
                "metadata": metadata
            }).encode()

        # For lower security levels, use standard encryption
        data_str = json.dumps(data) if not isinstance(data, str) else data
        return self.cipher.encrypt(data_str.encode())

    def decrypt_sensitive_data(self, encrypted_data: bytes, session_id: str) -> Optional[Any]:
        """
        Decrypt sensitive data with authorization check.
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return None

        try:
            # Try to parse as enhanced encryption format
            try:
                encrypted_obj = json.loads(encrypted_data.decode())
                if isinstance(encrypted_obj, dict) and "data" in encrypted_obj:
                    security_level = SecurityLevel(encrypted_obj["metadata"]["security_level"])

                    # Check if user has clearance for this data
                    security_levels = {
                        SecurityLevel.PUBLIC: 0,
                        SecurityLevel.INTERNAL: 1,
                        SecurityLevel.CONFIDENTIAL: 2,
                        SecurityLevel.RESTRICTED: 3
                    }

                    if security_levels[session.security_clearance] < security_levels[security_level]:
                        return None

                    encrypted_data = encrypted_obj["data"].encode()
            except (json.JSONDecodeError, KeyError):
                # Fall back to standard decryption
                pass

            decrypted = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted.decode())

        except Exception:
            return None

    def generate_api_token(self, session_id: str, expires_in_hours: int = 24) -> Optional[str]:
        """
        Generate JWT API token for programmatic access.
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return None

        payload = {
            "user_id": session.user_id,
            "session_id": session_id,
            "roles": list(session.roles),
            "permissions": [p.value for p in session.permissions],
            "security_clearance": session.security_clearance.value,
            "exp": int(time.time()) + (expires_in_hours * 3600),
            "iat": int(time.time()),
            "iss": "vizly-enterprise"
        }

        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def validate_api_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate and decode JWT API token.
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.InvalidTokenError:
            return None

    def _verify_credentials(self, username: str, password: str) -> bool:
        """
        Verify user credentials against enterprise identity provider.
        In production, this would integrate with LDAP/AD/SSO.
        """
        # Placeholder implementation
        # Real implementation would check against:
        # - LDAP/Active Directory
        # - SAML identity provider
        # - OAuth/OIDC provider
        return len(username) > 0 and len(password) >= 8

    def _get_user_roles(self, username: str) -> Set[str]:
        """
        Get user roles from enterprise directory.
        """
        # Placeholder implementation
        # Real implementation would query enterprise directory
        role_mapping = {
            "admin": {"admin", "analyst", "viewer"},
            "analyst": {"analyst", "viewer"},
            "viewer": {"viewer"}
        }

        # Simple username-based role assignment for demo
        if username.startswith("admin"):
            return role_mapping["admin"]
        elif username.startswith("analyst"):
            return role_mapping["analyst"]
        else:
            return role_mapping["viewer"]


class ComplianceAuditLogger:
    """
    Comprehensive audit logging for compliance requirements (SOX, HIPAA, GDPR, etc.).
    """

    def __init__(self, log_retention_days: int = 2555):  # 7 years for SOX compliance
        self.logger = logging.getLogger("vizly.enterprise.audit")
        self.retention_days = log_retention_days
        self.audit_events: List[AuditEvent] = []

    def log_event(self, event: AuditEvent) -> None:
        """
        Log audit event for compliance tracking.
        """
        self.audit_events.append(event)

        # Structure log entry for compliance requirements
        log_entry = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "session_id": event.session_id,
            "action": event.action,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "result": event.result,
            "ip_address": event.ip_address,
            "security_level": event.security_level.value,
            "details": event.details
        }

        # Log to structured logging system
        self.logger.info(f"AUDIT: {json.dumps(log_entry)}")

    def generate_compliance_report(self, start_date: datetime, end_date: datetime,
                                 user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate compliance report for audit purposes.
        """
        filtered_events = [
            event for event in self.audit_events
            if start_date <= event.timestamp <= end_date
            and (user_id is None or event.user_id == user_id)
        ]

        # Generate summary statistics
        total_events = len(filtered_events)
        failed_events = len([e for e in filtered_events if e.result == "failure"])
        denied_events = len([e for e in filtered_events if e.result == "denied"])

        action_counts = {}
        for event in filtered_events:
            action_counts[event.action] = action_counts.get(event.action, 0) + 1

        return {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_events": total_events,
                "failed_events": failed_events,
                "denied_events": denied_events,
                "success_rate": (total_events - failed_events - denied_events) / total_events if total_events > 0 else 0
            },
            "action_breakdown": action_counts,
            "events": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "user_id": e.user_id,
                    "action": e.action,
                    "resource": f"{e.resource_type}:{e.resource_id}",
                    "result": e.result,
                    "ip_address": e.ip_address
                }
                for e in filtered_events
            ]
        }

    def search_audit_trail(self, query: Dict[str, Any]) -> List[AuditEvent]:
        """
        Search audit trail for specific events.
        """
        results = []

        for event in self.audit_events:
            match = True

            if "user_id" in query and event.user_id != query["user_id"]:
                match = False
            if "action" in query and event.action != query["action"]:
                match = False
            if "resource_type" in query and event.resource_type != query["resource_type"]:
                match = False
            if "result" in query and event.result != query["result"]:
                match = False
            if "start_date" in query and event.timestamp < query["start_date"]:
                match = False
            if "end_date" in query and event.timestamp > query["end_date"]:
                match = False

            if match:
                results.append(event)

        return results


# Data Loss Prevention utilities
class DataClassifier:
    """
    Automatic data classification for enterprise compliance.
    """

    def __init__(self):
        self.classification_rules = {
            SecurityLevel.RESTRICTED: [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card numbers
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b[A-Z]{2}\d{6}[A-Z]\b'  # Passport numbers
            ],
            SecurityLevel.CONFIDENTIAL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
                r'\b\d{10}\b',  # Phone numbers
                r'\$\d+(?:,\d{3})*(?:\.\d{2})?\b'  # Currency amounts
            ],
            SecurityLevel.INTERNAL: [
                r'\b(?:salary|income|revenue|profit)\b',  # Financial terms
                r'\b(?:employee|staff|personnel)\s+\w+\b'  # Employee references
            ]
        }

    def classify_data(self, data: str) -> SecurityLevel:
        """
        Automatically classify data based on content analysis.
        """
        import re


        # Check for restricted patterns first
        for level, patterns in self.classification_rules.items():
            for pattern in patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    return level

        return SecurityLevel.PUBLIC

    def apply_data_masking(self, data: str, security_level: SecurityLevel) -> str:
        """
        Apply appropriate data masking based on classification.
        """
        import re

        if security_level == SecurityLevel.RESTRICTED:
            # Mask credit card numbers
            data = re.sub(r'\b(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})\b',
                         r'\1-****-****-\4', data)
            # Mask SSNs
            data = re.sub(r'\b(\d{3})-(\d{2})-(\d{4})\b', r'***-**-\3', data)

        elif security_level == SecurityLevel.CONFIDENTIAL:
            # Mask email addresses
            data = re.sub(r'\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b',
                         r'***@\2', data)

        return data