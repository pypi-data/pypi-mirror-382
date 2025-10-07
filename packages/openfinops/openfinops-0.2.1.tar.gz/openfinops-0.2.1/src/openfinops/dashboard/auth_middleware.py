"""
Role-based authentication middleware for executive dashboard system.
Integrates with IAM system to provide secure access control.
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



from functools import wraps
from typing import Dict, Any, Optional, Callable
from flask import Flask, request, jsonify, session, redirect, url_for
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets
from dataclasses import dataclass
from enum import Enum
import logging

from .iam_system import IAMManager, DashboardType, UserRole


class AuthenticationError(Exception):
    """Custom exception for authentication failures"""
    pass


class AuthorizationError(Exception):
    """Custom exception for authorization failures"""
    pass


@dataclass
class AuthenticationRequest:
    """Data structure for authentication requests"""
    username: str
    password: str
    mfa_token: Optional[str] = None
    remember_me: bool = False


@dataclass
class AuthenticationResponse:
    """Data structure for authentication responses"""
    success: bool
    token: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[UserRole] = None
    dashboard_access: Optional[Dict[str, bool]] = None
    expires_at: Optional[datetime] = None
    message: str = ""


class SessionManager:
    """Manages user sessions and authentication state"""

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=8)
        self.max_sessions_per_user = 3

    def create_session(self, user_id: str, token: str, role: UserRole) -> str:
        """Create a new user session"""
        session_id = secrets.token_urlsafe(32)

        # Clean up old sessions for this user
        self._cleanup_user_sessions(user_id)

        session_data = {
            'user_id': user_id,
            'token': token,
            'role': role.value,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None
        }

        self.active_sessions[session_id] = session_data
        return session_id

    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate and refresh a user session"""
        if session_id not in self.active_sessions:
            return None

        session_data = self.active_sessions[session_id]

        # Check if session has expired
        if datetime.utcnow() - session_data['last_activity'] > self.session_timeout:
            self.destroy_session(session_id)
            return None

        # Update last activity
        session_data['last_activity'] = datetime.utcnow()
        return session_data

    def destroy_session(self, session_id: str) -> bool:
        """Destroy a user session"""
        return self.active_sessions.pop(session_id, None) is not None

    def _cleanup_user_sessions(self, user_id: str):
        """Clean up old sessions for a user"""
        user_sessions = [
            (sid, data) for sid, data in self.active_sessions.items()
            if data['user_id'] == user_id
        ]

        # Sort by last activity and keep only the most recent sessions
        user_sessions.sort(key=lambda x: x[1]['last_activity'], reverse=True)

        if len(user_sessions) >= self.max_sessions_per_user:
            for session_id, _ in user_sessions[self.max_sessions_per_user-1:]:
                self.destroy_session(session_id)


class AuthenticationMiddleware:
    """Main authentication middleware class"""

    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.iam_manager = IAMManager()
        self.session_manager = SessionManager()
        self.logger = logging.getLogger(__name__)

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize the authentication middleware with Flask app"""
        self.app = app
        app.config.setdefault('SECRET_KEY', secrets.token_hex(32))
        app.config.setdefault('JWT_SECRET_KEY', secrets.token_hex(32))
        app.config.setdefault('JWT_EXPIRATION_DELTA', timedelta(hours=24))

        # Register error handlers
        app.errorhandler(AuthenticationError)(self._handle_auth_error)
        app.errorhandler(AuthorizationError)(self._handle_authz_error)

    def authenticate_user(self, auth_request: AuthenticationRequest) -> AuthenticationResponse:
        """Authenticate a user with username/password"""
        try:
            # Authenticate with IAM system
            token = self.iam_manager.authenticate_user(
                auth_request.username,
                auth_request.password
            )

            if not token:
                return AuthenticationResponse(
                    success=False,
                    message="Invalid username or password"
                )

            # Get user details
            user = self.iam_manager.get_user_by_username(auth_request.username)
            if not user:
                return AuthenticationResponse(
                    success=False,
                    message="User not found"
                )

            # Check if MFA is required
            if user.mfa_enabled and not auth_request.mfa_token:
                return AuthenticationResponse(
                    success=False,
                    message="MFA token required"
                )

            # Validate MFA if provided
            if auth_request.mfa_token and not self._validate_mfa_token(user.id, auth_request.mfa_token):
                return AuthenticationResponse(
                    success=False,
                    message="Invalid MFA token"
                )

            # Create session
            session_id = self.session_manager.create_session(user.id, token, user.role)

            # Get dashboard access permissions
            dashboard_access = self._get_dashboard_access(user.role)

            return AuthenticationResponse(
                success=True,
                token=token,
                user_id=user.id,
                role=user.role,
                dashboard_access=dashboard_access,
                expires_at=datetime.utcnow() + self.app.config['JWT_EXPIRATION_DELTA'],
                message="Authentication successful"
            )

        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return AuthenticationResponse(
                success=False,
                message="Authentication failed"
            )

    def require_auth(self, dashboard_type: Optional[DashboardType] = None):
        """Decorator to require authentication for routes"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Get session from request
                    session_id = request.headers.get('X-Session-ID') or session.get('session_id')
                    if not session_id:
                        raise AuthenticationError("No session found")

                    # Validate session
                    session_data = self.session_manager.validate_session(session_id)
                    if not session_data:
                        raise AuthenticationError("Invalid or expired session")

                    # Check dashboard access if specified
                    if dashboard_type:
                        if not self.iam_manager.can_access_dashboard(session_data['user_id'], dashboard_type):
                            raise AuthorizationError(f"Access denied to {dashboard_type.value} dashboard")

                    # Add user context to request
                    request.user_id = session_data['user_id']
                    request.user_role = UserRole(session_data['role'])

                    return f(*args, **kwargs)

                except AuthenticationError as e:
                    return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
                except AuthorizationError as e:
                    return jsonify({'error': 'Access denied', 'message': str(e)}), 403

            return decorated_function
        return decorator

    def require_role(self, required_roles: list[UserRole]):
        """Decorator to require specific roles"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(request, 'user_role') or request.user_role not in required_roles:
                    raise AuthorizationError(f"Requires one of: {[role.value for role in required_roles]}")
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def logout_user(self, session_id: str) -> bool:
        """Logout a user by destroying their session"""
        return self.session_manager.destroy_session(session_id)

    def _validate_mfa_token(self, user_id: str, token: str) -> bool:
        """Validate MFA token (placeholder implementation)"""
        # In a real implementation, this would validate TOTP/SMS tokens
        return len(token) == 6 and token.isdigit()

    def _get_dashboard_access(self, role: UserRole) -> Dict[str, bool]:
        """Get dashboard access permissions for a role"""
        access_map = {}
        for dashboard_type in DashboardType:
            access_map[dashboard_type.value] = self.iam_manager.can_access_dashboard_by_role(role, dashboard_type)
        return access_map

    def _handle_auth_error(self, error):
        """Handle authentication errors"""
        return jsonify({
            'error': 'Authentication Error',
            'message': str(error)
        }), 401

    def _handle_authz_error(self, error):
        """Handle authorization errors"""
        return jsonify({
            'error': 'Authorization Error',
            'message': str(error)
        }), 403


# Flask route decorators for convenience
def auth_required(dashboard_type: Optional[DashboardType] = None):
    """Convenience decorator for authentication requirement"""
    auth_middleware = AuthenticationMiddleware()
    return auth_middleware.require_auth(dashboard_type)


def role_required(roles: list[UserRole]):
    """Convenience decorator for role requirement"""
    auth_middleware = AuthenticationMiddleware()
    return auth_middleware.require_role(roles)


# Example usage and route definitions
def create_auth_routes(app: Flask, auth_middleware: AuthenticationMiddleware):
    """Create authentication routes"""

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login endpoint"""
        data = request.get_json()

        auth_request = AuthenticationRequest(
            username=data.get('username', ''),
            password=data.get('password', ''),
            mfa_token=data.get('mfa_token'),
            remember_me=data.get('remember_me', False)
        )

        response = auth_middleware.authenticate_user(auth_request)

        if response.success:
            session['session_id'] = auth_middleware.session_manager.create_session(
                response.user_id, response.token, response.role
            )
            return jsonify({
                'success': True,
                'user_id': response.user_id,
                'role': response.role.value,
                'dashboard_access': response.dashboard_access,
                'expires_at': response.expires_at.isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': response.message
            }), 401

    @app.route('/api/auth/logout', methods=['POST'])
    @auth_required()
    def logout():
        """Logout endpoint"""
        session_id = session.get('session_id')
        if session_id:
            auth_middleware.logout_user(session_id)
            session.clear()

        return jsonify({'success': True, 'message': 'Logged out successfully'})

    @app.route('/api/auth/profile', methods=['GET'])
    @auth_required()
    def profile():
        """Get current user profile"""
        user = auth_middleware.iam_manager.get_user_by_id(request.user_id)
        if user:
            return jsonify({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'is_active': user.is_active,
                'dashboard_access': auth_middleware._get_dashboard_access(user.role)
            })
        else:
            return jsonify({'error': 'User not found'}), 404


# Security utilities
class SecurityUtils:
    """Security utility functions"""

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash a password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )

        return password_hash.hex(), salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify a password against its hash"""
        computed_hash, _ = SecurityUtils.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, password_hash)

    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)