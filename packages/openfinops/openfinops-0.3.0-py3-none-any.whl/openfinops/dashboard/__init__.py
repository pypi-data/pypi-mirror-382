"""
OpenFinOps Dashboard Module
============================

Executive and role-based dashboards for FinOps visibility.

Available Dashboards:
- CFODashboard: Financial executive dashboard
- COODashboard: Operations executive dashboard
- InfrastructureLeaderDashboard: Infrastructure team dashboard
- FinanceAnalystDashboard: Finance analyst dashboard
- ModelCostDashboard: AI/ML model cost tracking
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



__all__ = [
    "CFODashboard",
    "COODashboard",
    "InfrastructureLeaderDashboard",
    "FinanceAnalystDashboard",
    "ModelCostDashboard",
    "DashboardRouter",
]

# Import dashboard classes
try:
    from .cfo_dashboard import CFODashboard
except ImportError:
    CFODashboard = None

try:
    from .coo_dashboard import COODashboard
except ImportError:
    COODashboard = None

try:
    from .infrastructure_leader_dashboard import InfrastructureLeaderDashboard
except ImportError:
    InfrastructureLeaderDashboard = None

try:
    from .finance_analyst_dashboard import FinanceAnalystDashboard
except ImportError:
    FinanceAnalystDashboard = None

try:
    from .model_cost_dashboard import ModelCostDashboard
except ImportError:
    ModelCostDashboard = None

try:
    from .dashboard_router import DashboardRouter
except ImportError:
    DashboardRouter = None
