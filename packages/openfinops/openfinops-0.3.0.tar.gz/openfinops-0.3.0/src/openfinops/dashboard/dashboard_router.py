"""
Dashboard routing and access control system.
Manages navigation and access to role-specific dashboards.
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



from flask import Flask, Blueprint, request, jsonify, render_template, redirect, url_for
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from .iam_system import IAMManager, DashboardType, UserRole
from .auth_middleware import AuthenticationMiddleware, auth_required, role_required
from .cfo_dashboard import CFODashboard
from .finance_analyst_dashboard import FinanceAnalystDashboard
from .infrastructure_leader_dashboard import InfrastructureLeaderDashboard
from .coo_dashboard import COODashboard


class NavigationError(Exception):
    """Custom exception for navigation errors"""
    pass


@dataclass
class DashboardRoute:
    """Configuration for a dashboard route"""
    path: str
    dashboard_type: DashboardType
    required_roles: List[UserRole]
    title: str
    description: str
    icon: str


@dataclass
class NavigationItem:
    """Navigation menu item"""
    name: str
    path: str
    icon: str
    badge: Optional[str] = None
    children: Optional[List['NavigationItem']] = None


class DashboardRouter:
    """Main dashboard routing and access control class"""

    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.auth_middleware = AuthenticationMiddleware()
        self.iam_manager = IAMManager()
        self.logger = logging.getLogger(__name__)

        # Initialize dashboard instances
        self.cfo_dashboard = CFODashboard(self.iam_manager)
        self.finance_analyst_dashboard = FinanceAnalystDashboard(self.iam_manager)
        self.infrastructure_dashboard = InfrastructureLeaderDashboard(self.iam_manager)
        self.coo_dashboard = COODashboard(self.iam_manager)

        # Define dashboard routes
        self.routes = self._initialize_routes()

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize router with Flask app"""
        self.app = app
        self.auth_middleware.init_app(app)

        # Create and register blueprints
        self._register_blueprints()

    def _initialize_routes(self) -> Dict[str, DashboardRoute]:
        """Initialize dashboard route configurations"""
        return {
            'cfo': DashboardRoute(
                path='/dashboard/cfo',
                dashboard_type=DashboardType.CFO_EXECUTIVE,
                required_roles=[UserRole.CFO, UserRole.CEO],
                title='CFO Executive Dashboard',
                description='Strategic financial oversight and executive reporting',
                icon='chart-line'
            ),
            'finance_analyst': DashboardRoute(
                path='/dashboard/finance-analyst',
                dashboard_type=DashboardType.FINANCE_ANALYST,
                required_roles=[UserRole.FINANCE_ANALYST, UserRole.CFO, UserRole.CEO],
                title='Finance Analyst Dashboard',
                description='Detailed financial analysis and cost optimization',
                icon='chart-bar'
            ),
            'infrastructure': DashboardRoute(
                path='/dashboard/infrastructure',
                dashboard_type=DashboardType.INFRASTRUCTURE_LEADER,
                required_roles=[UserRole.INFRASTRUCTURE_LEADER, UserRole.CTO, UserRole.CEO],
                title='Infrastructure Dashboard',
                description='Technical infrastructure monitoring and capacity planning',
                icon='server'
            ),
            'coo': DashboardRoute(
                path='/dashboard/coo',
                dashboard_type=DashboardType.COO_OPERATIONAL,
                required_roles=[UserRole.COO, UserRole.CEO],
                title='COO Operational Dashboard',
                description='Operational excellence and business process analytics',
                icon='cogs'
            )
        }

    def _register_blueprints(self):
        """Register dashboard blueprints with the Flask app"""
        # Main dashboard blueprint
        main_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

        # Register main routes
        main_bp.add_url_rule('/', 'index', self.dashboard_index, methods=['GET'])
        main_bp.add_url_rule('/home', 'home', self.dashboard_home, methods=['GET'])
        main_bp.add_url_rule('/navigation', 'navigation', self.get_navigation, methods=['GET'])

        # Register dashboard-specific routes
        for route_name, route_config in self.routes.items():
            endpoint = f'{route_name}_dashboard'
            main_bp.add_url_rule(
                route_config.path.replace('/dashboard', ''),
                endpoint,
                self._create_dashboard_handler(route_name),
                methods=['GET', 'POST']
            )

        # API routes for dashboard data
        api_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')

        api_bp.add_url_rule('/cfo/data', 'cfo_data', self.get_cfo_data, methods=['GET'])
        api_bp.add_url_rule('/finance-analyst/data', 'finance_analyst_data', self.get_finance_analyst_data, methods=['GET'])
        api_bp.add_url_rule('/infrastructure/data', 'infrastructure_data', self.get_infrastructure_data, methods=['GET'])
        api_bp.add_url_rule('/coo/data', 'coo_data', self.get_coo_data, methods=['GET'])

        # Register blueprints
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(api_bp)

    def _create_dashboard_handler(self, route_name: str):
        """Create a handler function for a specific dashboard route"""
        route_config = self.routes[route_name]

        @auth_required(route_config.dashboard_type)
        @role_required(route_config.required_roles)
        def dashboard_handler():
            try:
                # Get user context
                user = self.iam_manager.get_user_by_id(request.user_id)
                if not user:
                    return redirect(url_for('auth.login'))

                # Generate navigation
                navigation = self._generate_navigation(user.role)

                # Render dashboard template
                return render_template(
                    f'dashboards/{route_name}.html',
                    title=route_config.title,
                    description=route_config.description,
                    user=user,
                    navigation=navigation,
                    dashboard_type=route_config.dashboard_type.value
                )

            except Exception as e:
                self.logger.error(f"Error loading {route_name} dashboard: {str(e)}")
                return jsonify({'error': 'Dashboard loading failed'}), 500

        return dashboard_handler

    @auth_required()
    def dashboard_index(self):
        """Main dashboard index - redirect to appropriate dashboard"""
        user = self.iam_manager.get_user_by_id(request.user_id)
        if not user:
            return redirect(url_for('auth.login'))

        # Determine default dashboard based on user role
        default_dashboard = self._get_default_dashboard(user.role)
        if default_dashboard:
            return redirect(url_for(f'dashboard.{default_dashboard}_dashboard'))
        else:
            return render_template('dashboards/no_access.html', user=user)

    @auth_required()
    def dashboard_home(self):
        """Dashboard home page with overview"""
        user = self.iam_manager.get_user_by_id(request.user_id)
        if not user:
            return redirect(url_for('auth.login'))

        # Get accessible dashboards
        accessible_dashboards = self._get_accessible_dashboards(user.role)
        navigation = self._generate_navigation(user.role)

        return render_template(
            'dashboards/home.html',
            user=user,
            accessible_dashboards=accessible_dashboards,
            navigation=navigation
        )

    @auth_required()
    def get_navigation(self):
        """API endpoint to get navigation structure"""
        user = self.iam_manager.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        navigation = self._generate_navigation(user.role)
        return jsonify({'navigation': [item.__dict__ for item in navigation]})

    # Dashboard data API endpoints
    @auth_required(DashboardType.CFO_EXECUTIVE)
    @role_required([UserRole.CFO, UserRole.CEO])
    def get_cfo_data(self):
        """Get CFO dashboard data"""
        try:
            time_period = request.args.get('period', 'current_month')
            data = self.cfo_dashboard.generate_dashboard(request.user_id, time_period)
            return jsonify(data)
        except Exception as e:
            self.logger.error(f"Error generating CFO data: {str(e)}")
            return jsonify({'error': 'Failed to load dashboard data'}), 500

    @auth_required(DashboardType.FINANCE_ANALYST)
    @role_required([UserRole.FINANCE_ANALYST, UserRole.CFO, UserRole.CEO])
    def get_finance_analyst_data(self):
        """Get Finance Analyst dashboard data"""
        try:
            time_period = request.args.get('period', 'current_month')
            data = self.finance_analyst_dashboard.generate_dashboard(request.user_id, time_period)
            return jsonify(data)
        except Exception as e:
            self.logger.error(f"Error generating Finance Analyst data: {str(e)}")
            return jsonify({'error': 'Failed to load dashboard data'}), 500

    @auth_required(DashboardType.INFRASTRUCTURE_LEADER)
    @role_required([UserRole.INFRASTRUCTURE_LEADER, UserRole.CTO, UserRole.CEO])
    def get_infrastructure_data(self):
        """Get Infrastructure dashboard data"""
        try:
            time_period = request.args.get('period', 'current_month')
            data = self.infrastructure_dashboard.generate_dashboard(request.user_id, time_period)
            return jsonify(data)
        except Exception as e:
            self.logger.error(f"Error generating Infrastructure data: {str(e)}")
            return jsonify({'error': 'Failed to load dashboard data'}), 500

    @auth_required(DashboardType.COO_OPERATIONAL)
    @role_required([UserRole.COO, UserRole.CEO])
    def get_coo_data(self):
        """Get COO dashboard data"""
        try:
            time_period = request.args.get('period', 'current_month')
            data = self.coo_dashboard.generate_dashboard(request.user_id, time_period)
            return jsonify(data)
        except Exception as e:
            self.logger.error(f"Error generating COO data: {str(e)}")
            return jsonify({'error': 'Failed to load dashboard data'}), 500

    def _get_default_dashboard(self, role: UserRole) -> Optional[str]:
        """Get the default dashboard for a user role"""
        role_dashboard_map = {
            UserRole.CFO: 'cfo',
            UserRole.FINANCE_ANALYST: 'finance_analyst',
            UserRole.INFRASTRUCTURE_LEADER: 'infrastructure',
            UserRole.COO: 'coo',
            UserRole.CEO: 'cfo',  # CEO defaults to CFO dashboard
            UserRole.CTO: 'infrastructure',  # CTO defaults to infrastructure
        }
        return role_dashboard_map.get(role)

    def _get_accessible_dashboards(self, role: UserRole) -> List[Dict[str, Any]]:
        """Get list of dashboards accessible to a user role"""
        accessible = []

        for route_name, route_config in self.routes.items():
            if role in route_config.required_roles:
                accessible.append({
                    'name': route_name,
                    'title': route_config.title,
                    'description': route_config.description,
                    'path': route_config.path,
                    'icon': route_config.icon
                })

        return accessible

    def _generate_navigation(self, role: UserRole) -> List[NavigationItem]:
        """Generate navigation menu based on user role"""
        navigation = []

        # Dashboard home
        navigation.append(NavigationItem(
            name='Dashboard Home',
            path='/dashboard/home',
            icon='home'
        ))

        # Role-specific dashboards
        accessible_dashboards = self._get_accessible_dashboards(role)
        for dashboard in accessible_dashboards:
            navigation.append(NavigationItem(
                name=dashboard['title'],
                path=dashboard['path'],
                icon=dashboard['icon']
            ))

        # Admin section for elevated roles
        if role in [UserRole.CEO, UserRole.CFO, UserRole.CTO]:
            admin_items = []

            if role == UserRole.CEO:
                admin_items.extend([
                    NavigationItem('User Management', '/admin/users', 'users'),
                    NavigationItem('System Settings', '/admin/settings', 'cog'),
                    NavigationItem('Audit Logs', '/admin/audit', 'file-text')
                ])

            if admin_items:
                navigation.append(NavigationItem(
                    name='Administration',
                    path='/admin',
                    icon='shield',
                    children=admin_items
                ))

        # User profile and settings
        navigation.append(NavigationItem(
            name='Profile',
            path='/profile',
            icon='user'
        ))

        return navigation


# Flask application factory function
def create_dashboard_app(config_name: str = 'default') -> Flask:
    """Create Flask application with dashboard routing"""
    app = Flask(__name__)

    # Basic configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key-here'

    # Initialize dashboard router
    dashboard_router = DashboardRouter(app)

    # Add basic routes
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Page not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app


# Utility functions for route management
class RouteManager:
    """Utility class for managing dashboard routes"""

    @staticmethod
    def get_routes_for_role(role: UserRole) -> Dict[str, DashboardRoute]:
        """Get available routes for a specific role"""
        router = DashboardRouter()
        available_routes = {}

        for route_name, route_config in router.routes.items():
            if role in route_config.required_roles:
                available_routes[route_name] = route_config

        return available_routes

    @staticmethod
    def validate_route_access(user_id: str, dashboard_type: DashboardType) -> bool:
        """Validate if a user can access a specific dashboard route"""
        iam_manager = IAMManager()
        return iam_manager.can_access_dashboard(user_id, dashboard_type)

    @staticmethod
    def get_breadcrumbs(current_path: str) -> List[Dict[str, str]]:
        """Generate breadcrumb navigation for current path"""
        breadcrumbs = [{'name': 'Dashboard', 'path': '/dashboard'}]

        path_parts = current_path.strip('/').split('/')
        if len(path_parts) > 1:
            # Add specific dashboard breadcrumb
            dashboard_name = path_parts[1].replace('-', ' ').title()
            breadcrumbs.append({
                'name': dashboard_name,
                'path': current_path
            })

        return breadcrumbs


if __name__ == '__main__':
    # Example usage
    app = create_dashboard_app()
    app.run(debug=True, host='0.0.0.0', port=5000)