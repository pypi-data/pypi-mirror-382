"""
Shadow IT Detection
====================

Detect and manage unapproved SaaS applications (Shadow IT).
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Shadow IT risk levels."""

    CRITICAL = "critical"  # High cost or security risk
    HIGH = "high"  # Significant risk
    MEDIUM = "medium"  # Moderate risk
    LOW = "low"  # Minimal risk


@dataclass
class ShadowITApplication:
    """
    Shadow IT application (unapproved SaaS).

    Attributes:
        app_id: Application identifier
        name: Application name
        discovered_via: Discovery method
        users: Number of users
        monthly_cost: Estimated monthly cost
        risk_level: Risk assessment
        security_concerns: Security issues
        compliance_concerns: Compliance issues
        alternative_approved: Approved alternative
        discovered_date: Discovery date
    """

    app_id: str
    name: str
    discovered_via: str
    users: int = 0
    monthly_cost: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    security_concerns: List[str] = field(default_factory=list)
    compliance_concerns: List[str] = field(default_factory=list)
    alternative_approved: str = ""
    discovered_date: Optional[float] = None

    def __post_init__(self):
        """Initialize application."""
        if self.discovered_date is None:
            self.discovered_date = datetime.now().timestamp()


class ShadowITDetector:
    """
    Detects and manages shadow IT applications.
    """

    def __init__(self):
        """Initialize shadow IT detector."""
        self._shadow_apps: Dict[str, ShadowITApplication] = {}
        self._approved_vendors: set = set()
        self._risk_rules: List[Dict[str, Any]] = []

    def add_approved_vendor(self, vendor: str):
        """
        Add approved vendor to whitelist.

        Args:
            vendor: Vendor name
        """
        self._approved_vendors.add(vendor.lower())
        logger.info(f"Added approved vendor: {vendor}")

    def is_approved(self, vendor: str) -> bool:
        """
        Check if vendor is approved.

        Args:
            vendor: Vendor name

        Returns:
            True if approved
        """
        return vendor.lower() in self._approved_vendors

    def add_risk_rule(
        self,
        rule_name: str,
        condition: callable,
        risk_level: RiskLevel,
        description: str,
    ):
        """
        Add risk assessment rule.

        Args:
            rule_name: Rule name
            condition: Condition function
            risk_level: Risk level if condition met
            description: Rule description
        """
        self._risk_rules.append({
            "name": rule_name,
            "condition": condition,
            "risk_level": risk_level,
            "description": description,
        })

    def detect_from_expenses(
        self, expense_data: List[Dict[str, Any]]
    ) -> List[ShadowITApplication]:
        """
        Detect shadow IT from expense/billing data.

        Args:
            expense_data: Expense transaction data

        Returns:
            Detected shadow IT applications
        """
        detected = []

        # Group expenses by vendor
        vendor_expenses = {}
        for expense in expense_data:
            vendor = expense.get("vendor", "Unknown")
            amount = expense.get("amount", 0.0)
            category = expense.get("category", "")

            # Look for software/subscription categories
            if self._is_software_expense(category, expense.get("description", "")):
                if vendor not in vendor_expenses:
                    vendor_expenses[vendor] = []
                vendor_expenses[vendor].append(expense)

        # Check for unapproved vendors
        for vendor, expenses in vendor_expenses.items():
            if not self.is_approved(vendor):
                total_cost = sum(e.get("amount", 0.0) for e in expenses)
                app_id = f"shadow-{vendor.lower().replace(' ', '-')}"

                if app_id not in self._shadow_apps:
                    app = ShadowITApplication(
                        app_id=app_id,
                        name=vendor,
                        discovered_via="expense_analysis",
                        monthly_cost=total_cost,
                    )

                    # Assess risk
                    app.risk_level = self._assess_risk(app)

                    self._shadow_apps[app_id] = app
                    detected.append(app)

                    logger.warning(f"Detected shadow IT: {vendor} (${total_cost}/month)")

        return detected

    def detect_from_network(
        self, network_data: List[Dict[str, Any]]
    ) -> List[ShadowITApplication]:
        """
        Detect shadow IT from network traffic analysis.

        Args:
            network_data: Network traffic data

        Returns:
            Detected shadow IT applications
        """
        detected = []

        # Analyze domains accessed
        domain_usage = {}
        for connection in network_data:
            domain = connection.get("domain", "")
            user_id = connection.get("user_id", "")

            if self._is_saas_domain(domain) and not self._is_approved_domain(domain):
                if domain not in domain_usage:
                    domain_usage[domain] = set()
                domain_usage[domain].add(user_id)

        # Create shadow IT entries
        for domain, users in domain_usage.items():
            app_id = f"shadow-network-{domain.replace('.', '-')}"

            if app_id not in self._shadow_apps:
                app = ShadowITApplication(
                    app_id=app_id,
                    name=domain,
                    discovered_via="network_analysis",
                    users=len(users),
                )

                app.security_concerns.append("Unapproved network access")
                app.risk_level = self._assess_risk(app)

                self._shadow_apps[app_id] = app
                detected.append(app)

                logger.warning(f"Detected shadow IT via network: {domain} ({len(users)} users)")

        return detected

    def _is_software_expense(self, category: str, description: str) -> bool:
        """Check if expense is software-related."""
        software_keywords = [
            "software", "subscription", "saas", "license", "cloud",
            "service", "platform", "app", "tool",
        ]
        text = f"{category} {description}".lower()
        return any(keyword in text for keyword in software_keywords)

    def _is_saas_domain(self, domain: str) -> bool:
        """Check if domain is likely a SaaS service."""
        # Simple heuristic - in production, use comprehensive domain database
        saas_tlds = [".io", ".app", ".cloud", ".dev"]
        saas_keywords = ["app", "cloud", "platform", "service", "software"]

        domain_lower = domain.lower()

        if any(domain_lower.endswith(tld) for tld in saas_tlds):
            return True

        return any(keyword in domain_lower for keyword in saas_keywords)

    def _is_approved_domain(self, domain: str) -> bool:
        """Check if domain is from approved vendor."""
        # In production, maintain mapping of vendors to domains
        for vendor in self._approved_vendors:
            if vendor in domain.lower():
                return True
        return False

    def _assess_risk(self, app: ShadowITApplication) -> RiskLevel:
        """
        Assess risk level of shadow IT application.

        Args:
            app: Shadow IT application

        Returns:
            Risk level
        """
        risk_score = 0

        # High cost = higher risk
        if app.monthly_cost > 1000:
            risk_score += 3
        elif app.monthly_cost > 500:
            risk_score += 2
        elif app.monthly_cost > 100:
            risk_score += 1

        # Many users = higher risk
        if app.users > 50:
            risk_score += 3
        elif app.users > 20:
            risk_score += 2
        elif app.users > 5:
            risk_score += 1

        # Security/compliance concerns
        risk_score += len(app.security_concerns)
        risk_score += len(app.compliance_concerns)

        # Apply custom rules
        for rule in self._risk_rules:
            if rule["condition"](app):
                if rule["risk_level"] == RiskLevel.CRITICAL:
                    risk_score += 4
                elif rule["risk_level"] == RiskLevel.HIGH:
                    risk_score += 3

        # Convert score to risk level
        if risk_score >= 8:
            return RiskLevel.CRITICAL
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def list_shadow_apps(
        self, risk_level: Optional[RiskLevel] = None
    ) -> List[ShadowITApplication]:
        """
        List shadow IT applications.

        Args:
            risk_level: Filter by risk level

        Returns:
            List of shadow IT apps
        """
        apps = list(self._shadow_apps.values())

        if risk_level:
            apps = [a for a in apps if a.risk_level == risk_level]

        return sorted(apps, key=lambda x: (x.risk_level.value, -x.monthly_cost))

    def get_shadow_it_summary(self) -> Dict[str, Any]:
        """
        Get shadow IT summary.

        Returns:
            Summary statistics
        """
        apps = list(self._shadow_apps.values())

        by_risk = {
            RiskLevel.CRITICAL: len([a for a in apps if a.risk_level == RiskLevel.CRITICAL]),
            RiskLevel.HIGH: len([a for a in apps if a.risk_level == RiskLevel.HIGH]),
            RiskLevel.MEDIUM: len([a for a in apps if a.risk_level == RiskLevel.MEDIUM]),
            RiskLevel.LOW: len([a for a in apps if a.risk_level == RiskLevel.LOW]),
        }

        total_cost = sum(a.monthly_cost for a in apps)
        total_users = sum(a.users for a in apps)

        return {
            "total_shadow_apps": len(apps),
            "by_risk_level": {level.value: count for level, count in by_risk.items()},
            "total_monthly_cost": total_cost,
            "total_users": total_users,
            "critical_apps": by_risk[RiskLevel.CRITICAL],
            "high_risk_apps": by_risk[RiskLevel.HIGH],
        }

    def get_remediation_plan(self) -> List[Dict[str, Any]]:
        """
        Generate remediation plan for shadow IT.

        Returns:
            Prioritized remediation actions
        """
        plan = []
        apps = self.list_shadow_apps()

        for app in apps:
            action = {
                "app_id": app.app_id,
                "app_name": app.name,
                "risk_level": app.risk_level.value,
                "users": app.users,
                "monthly_cost": app.monthly_cost,
                "actions": [],
            }

            # Determine actions based on risk
            if app.risk_level == RiskLevel.CRITICAL:
                action["priority"] = "immediate"
                action["actions"].append("Immediate review required")
                action["actions"].append("Block access if security risk")
                action["actions"].append("Contact users and business owner")
            elif app.risk_level == RiskLevel.HIGH:
                action["priority"] = "high"
                action["actions"].append("Review within 7 days")
                action["actions"].append("Evaluate approved alternatives")
            elif app.risk_level == RiskLevel.MEDIUM:
                action["priority"] = "medium"
                action["actions"].append("Review within 30 days")
                action["actions"].append("Begin approval process if legitimate need")
            else:
                action["priority"] = "low"
                action["actions"].append("Review within 90 days")

            # Add specific recommendations
            if app.alternative_approved:
                action["recommendation"] = f"Migrate to approved alternative: {app.alternative_approved}"
            elif app.monthly_cost > 500:
                action["recommendation"] = "High cost - priority for approval or decommission"
            elif app.users > 20:
                action["recommendation"] = "High user count - evaluate for organization-wide approval"

            plan.append(action)

        return plan


def setup_default_shadow_it_rules(detector: ShadowITDetector):
    """
    Set up default shadow IT detection rules.

    Args:
        detector: Shadow IT detector instance
    """
    # Rule: High cost applications are critical risk
    detector.add_risk_rule(
        "high_cost",
        lambda app: app.monthly_cost > 2000,
        RiskLevel.CRITICAL,
        "Application with monthly cost > $2000",
    )

    # Rule: Many users without approval is high risk
    detector.add_risk_rule(
        "high_user_count",
        lambda app: app.users > 100,
        RiskLevel.HIGH,
        "Application with > 100 users needs approval",
    )

    logger.info("Set up default shadow IT detection rules")
