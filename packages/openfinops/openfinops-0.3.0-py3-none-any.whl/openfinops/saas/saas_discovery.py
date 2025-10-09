"""
SaaS Application Discovery
===========================

Discover and track SaaS applications across the organization.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SaaSCategory(Enum):
    """SaaS application categories."""

    PRODUCTIVITY = "productivity"
    COLLABORATION = "collaboration"
    DEVELOPMENT = "development"
    SECURITY = "security"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    SALES = "sales"
    HR = "hr"
    FINANCE = "finance"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


class ApprovalStatus(Enum):
    """Application approval status."""

    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


@dataclass
class SaaSApplication:
    """
    SaaS application definition.

    Attributes:
        app_id: Application identifier
        name: Application name
        vendor: Vendor name
        category: Application category
        monthly_cost: Monthly cost in USD
        users: Number of licensed users
        active_users: Number of active users
        approval_status: Approval status
        discovered_date: Discovery date
        integrations: Connected integrations
        owner: Business owner
        tags: Application tags
    """

    app_id: str
    name: str
    vendor: str
    category: SaaSCategory
    monthly_cost: float = 0.0
    users: int = 0
    active_users: int = 0
    approval_status: ApprovalStatus = ApprovalStatus.UNKNOWN
    discovered_date: Optional[float] = None
    integrations: List[str] = field(default_factory=list)
    owner: str = ""
    tags: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize application."""
        if self.discovered_date is None:
            self.discovered_date = datetime.now().timestamp()

    def get_utilization_rate(self) -> float:
        """
        Calculate license utilization rate.

        Returns:
            Utilization rate (0.0 to 1.0)
        """
        if self.users == 0:
            return 0.0
        return min(self.active_users / self.users, 1.0)

    def get_cost_per_user(self) -> float:
        """
        Calculate cost per user.

        Returns:
            Monthly cost per user
        """
        if self.users == 0:
            return 0.0
        return self.monthly_cost / self.users

    def get_cost_per_active_user(self) -> float:
        """
        Calculate cost per active user.

        Returns:
            Monthly cost per active user
        """
        if self.active_users == 0:
            return 0.0
        return self.monthly_cost / self.active_users

    def get_wasted_spend(self) -> float:
        """
        Calculate wasted spend on unused licenses.

        Returns:
            Monthly wasted spend
        """
        unused_licenses = max(0, self.users - self.active_users)
        if self.users == 0:
            return 0.0
        return (unused_licenses / self.users) * self.monthly_cost


class SaaSDiscovery:
    """
    SaaS application discovery and tracking.
    """

    def __init__(self):
        """Initialize SaaS discovery."""
        self._applications: Dict[str, SaaSApplication] = {}
        self._discovery_sources: List[str] = []

    def register_application(self, app: SaaSApplication):
        """
        Register a SaaS application.

        Args:
            app: SaaS application
        """
        self._applications[app.app_id] = app
        logger.info(f"Registered SaaS application: {app.name} ({app.app_id})")

    def get_application(self, app_id: str) -> Optional[SaaSApplication]:
        """
        Get application by ID.

        Args:
            app_id: Application ID

        Returns:
            SaaS application or None
        """
        return self._applications.get(app_id)

    def list_applications(
        self,
        category: Optional[SaaSCategory] = None,
        approval_status: Optional[ApprovalStatus] = None,
        min_cost: Optional[float] = None,
    ) -> List[SaaSApplication]:
        """
        List SaaS applications with optional filters.

        Args:
            category: Filter by category
            approval_status: Filter by approval status
            min_cost: Minimum monthly cost

        Returns:
            List of applications
        """
        apps = list(self._applications.values())

        if category:
            apps = [a for a in apps if a.category == category]

        if approval_status:
            apps = [a for a in apps if a.approval_status == approval_status]

        if min_cost is not None:
            apps = [a for a in apps if a.monthly_cost >= min_cost]

        return apps

    def discover_from_billing(self, billing_data: List[Dict[str, Any]]) -> List[SaaSApplication]:
        """
        Discover SaaS applications from billing data.

        Args:
            billing_data: Billing transaction data

        Returns:
            Discovered applications
        """
        discovered = []

        for transaction in billing_data:
            vendor = transaction.get("vendor", "Unknown")
            description = transaction.get("description", "")
            amount = transaction.get("amount", 0.0)

            # Simple heuristic: if transaction is recurring and from known SaaS vendor
            if self._is_saas_vendor(vendor):
                app_id = f"saas-{vendor.lower().replace(' ', '-')}"

                if app_id not in self._applications:
                    app = SaaSApplication(
                        app_id=app_id,
                        name=vendor,
                        vendor=vendor,
                        category=self._categorize_vendor(vendor),
                        monthly_cost=amount,
                        approval_status=ApprovalStatus.UNKNOWN,
                    )
                    self.register_application(app)
                    discovered.append(app)

        logger.info(f"Discovered {len(discovered)} applications from billing data")
        return discovered

    def discover_from_integrations(self, sso_data: List[Dict[str, Any]]) -> List[SaaSApplication]:
        """
        Discover SaaS applications from SSO/integration data.

        Args:
            sso_data: SSO authentication data

        Returns:
            Discovered applications
        """
        discovered = []

        app_usage = {}
        for login in sso_data:
            app_name = login.get("application", "")
            user_id = login.get("user_id", "")

            if app_name not in app_usage:
                app_usage[app_name] = set()
            app_usage[app_name].add(user_id)

        for app_name, users in app_usage.items():
            app_id = f"sso-{app_name.lower().replace(' ', '-')}"

            if app_id not in self._applications:
                app = SaaSApplication(
                    app_id=app_id,
                    name=app_name,
                    vendor=app_name,
                    category=SaaSCategory.OTHER,
                    active_users=len(users),
                    approval_status=ApprovalStatus.UNKNOWN,
                )
                self.register_application(app)
                discovered.append(app)

        logger.info(f"Discovered {len(discovered)} applications from SSO data")
        return discovered

    def _is_saas_vendor(self, vendor: str) -> bool:
        """
        Check if vendor is a known SaaS provider.

        Args:
            vendor: Vendor name

        Returns:
            True if known SaaS vendor
        """
        # Simple heuristic - in production, use comprehensive vendor database
        saas_keywords = [
            "slack", "zoom", "github", "jira", "confluence", "salesforce",
            "hubspot", "datadog", "pagerduty", "notion", "figma", "miro",
            "asana", "monday", "dropbox", "box", "google workspace",
            "microsoft 365", "adobe", "atlassian", "okta", "auth0",
        ]
        vendor_lower = vendor.lower()
        return any(keyword in vendor_lower for keyword in saas_keywords)

    def _categorize_vendor(self, vendor: str) -> SaaSCategory:
        """
        Categorize vendor automatically.

        Args:
            vendor: Vendor name

        Returns:
            Application category
        """
        vendor_lower = vendor.lower()

        categories = {
            SaaSCategory.COLLABORATION: ["slack", "zoom", "teams", "meet"],
            SaaSCategory.DEVELOPMENT: ["github", "gitlab", "jira", "confluence"],
            SaaSCategory.SECURITY: ["okta", "auth0", "1password", "lastpass"],
            SaaSCategory.ANALYTICS: ["datadog", "splunk", "tableau", "looker"],
            SaaSCategory.MARKETING: ["hubspot", "mailchimp", "salesforce marketing"],
            SaaSCategory.SALES: ["salesforce", "hubspot sales"],
            SaaSCategory.PRODUCTIVITY: ["notion", "asana", "monday", "trello"],
        }

        for category, keywords in categories.items():
            if any(keyword in vendor_lower for keyword in keywords):
                return category

        return SaaSCategory.OTHER

    def get_total_spend(self) -> float:
        """
        Calculate total SaaS spend.

        Returns:
            Total monthly spend
        """
        return sum(app.monthly_cost for app in self._applications.values())

    def get_total_wasted_spend(self) -> float:
        """
        Calculate total wasted spend.

        Returns:
            Total monthly wasted spend
        """
        return sum(app.get_wasted_spend() for app in self._applications.values())

    def get_category_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """
        Get spending breakdown by category.

        Returns:
            Category breakdown with spend and app count
        """
        breakdown = {}

        for app in self._applications.values():
            category = app.category.value
            if category not in breakdown:
                breakdown[category] = {
                    "spend": 0.0,
                    "app_count": 0,
                    "users": 0,
                    "active_users": 0,
                }

            breakdown[category]["spend"] += app.monthly_cost
            breakdown[category]["app_count"] += 1
            breakdown[category]["users"] += app.users
            breakdown[category]["active_users"] += app.active_users

        return breakdown

    def get_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identify optimization opportunities.

        Returns:
            List of optimization recommendations
        """
        opportunities = []

        for app in self._applications.values():
            # Low utilization
            utilization = app.get_utilization_rate()
            if utilization < 0.5 and app.users > 0:
                opportunities.append({
                    "type": "low_utilization",
                    "app_id": app.app_id,
                    "app_name": app.name,
                    "utilization": utilization,
                    "potential_savings": app.get_wasted_spend(),
                    "recommendation": f"Reduce licenses from {app.users} to {app.active_users}",
                })

            # High cost per user
            cost_per_user = app.get_cost_per_active_user()
            if cost_per_user > 100 and app.active_users > 0:
                opportunities.append({
                    "type": "high_cost_per_user",
                    "app_id": app.app_id,
                    "app_name": app.name,
                    "cost_per_user": cost_per_user,
                    "recommendation": "Review pricing plan or consider alternatives",
                })

            # Unapproved applications
            if app.approval_status == ApprovalStatus.UNKNOWN and app.monthly_cost > 50:
                opportunities.append({
                    "type": "unapproved_app",
                    "app_id": app.app_id,
                    "app_name": app.name,
                    "monthly_cost": app.monthly_cost,
                    "recommendation": "Review and approve or decommission",
                })

        return sorted(opportunities, key=lambda x: x.get("potential_savings", 0), reverse=True)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get SaaS portfolio summary.

        Returns:
            Summary statistics
        """
        apps = list(self._applications.values())

        approved = [a for a in apps if a.approval_status == ApprovalStatus.APPROVED]
        unapproved = [a for a in apps if a.approval_status == ApprovalStatus.UNKNOWN]

        total_users = sum(a.users for a in apps)
        total_active = sum(a.active_users for a in apps)

        return {
            "total_applications": len(apps),
            "approved_applications": len(approved),
            "unapproved_applications": len(unapproved),
            "total_monthly_spend": self.get_total_spend(),
            "total_wasted_spend": self.get_total_wasted_spend(),
            "total_licenses": total_users,
            "active_users": total_active,
            "average_utilization": total_active / total_users if total_users > 0 else 0,
            "category_breakdown": self.get_category_breakdown(),
        }


def create_sample_application(
    name: str,
    vendor: str,
    category: SaaSCategory,
    monthly_cost: float,
    users: int,
    active_users: int,
) -> SaaSApplication:
    """
    Create a sample SaaS application.

    Args:
        name: Application name
        vendor: Vendor name
        category: Application category
        monthly_cost: Monthly cost
        users: Licensed users
        active_users: Active users

    Returns:
        SaaS application
    """
    app_id = f"app-{name.lower().replace(' ', '-')}"

    return SaaSApplication(
        app_id=app_id,
        name=name,
        vendor=vendor,
        category=category,
        monthly_cost=monthly_cost,
        users=users,
        active_users=active_users,
        approval_status=ApprovalStatus.APPROVED,
    )
