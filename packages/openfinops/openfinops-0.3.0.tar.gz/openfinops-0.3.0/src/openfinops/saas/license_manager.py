"""
License Management
==================

Manage software licenses and optimize utilization.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """License types."""

    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    CONCURRENT = "concurrent"
    NAMED_USER = "named_user"


class LicenseStatus(Enum):
    """License status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"


@dataclass
class License:
    """
    Software license.

    Attributes:
        license_id: License identifier
        app_id: Application ID
        license_type: Type of license
        quantity: Number of licenses
        assigned: Number of assigned licenses
        active: Number of actively used licenses
        cost_per_license: Monthly cost per license
        purchase_date: Purchase date
        expiration_date: Expiration date
        renewal_date: Renewal date
        vendor: Vendor name
        contract_terms: Contract terms
    """

    license_id: str
    app_id: str
    license_type: LicenseType
    quantity: int
    assigned: int = 0
    active: int = 0
    cost_per_license: float = 0.0
    purchase_date: Optional[float] = None
    expiration_date: Optional[float] = None
    renewal_date: Optional[float] = None
    vendor: str = ""
    contract_terms: Dict[str, Any] = field(default_factory=dict)

    def get_utilization_rate(self) -> float:
        """Calculate utilization rate."""
        if self.quantity == 0:
            return 0.0
        return min(self.active / self.quantity, 1.0)

    def get_assignment_rate(self) -> float:
        """Calculate assignment rate."""
        if self.quantity == 0:
            return 0.0
        return min(self.assigned / self.quantity, 1.0)

    def get_total_cost(self) -> float:
        """Calculate total monthly cost."""
        return self.quantity * self.cost_per_license

    def get_wasted_cost(self) -> float:
        """Calculate wasted cost on unused licenses."""
        unused = max(0, self.quantity - self.active)
        return unused * self.cost_per_license

    def get_status(self) -> LicenseStatus:
        """
        Get license status.

        Returns:
            License status
        """
        if self.expiration_date:
            current_time = datetime.now().timestamp()

            if current_time > self.expiration_date:
                return LicenseStatus.EXPIRED

            # Expiring within 30 days
            if current_time > (self.expiration_date - 30 * 24 * 3600):
                return LicenseStatus.EXPIRING_SOON

        if self.active > 0:
            return LicenseStatus.ACTIVE
        else:
            return LicenseStatus.INACTIVE

    def days_until_expiration(self) -> Optional[int]:
        """
        Calculate days until license expiration.

        Returns:
            Days until expiration or None
        """
        if not self.expiration_date:
            return None

        current_time = datetime.now().timestamp()
        delta = self.expiration_date - current_time

        return int(delta / (24 * 3600))


class LicenseManager:
    """
    Manages software licenses and optimization.
    """

    def __init__(self):
        """Initialize license manager."""
        self._licenses: Dict[str, License] = {}
        self._user_assignments: Dict[str, List[str]] = {}  # user_id -> [license_ids]

    def add_license(self, license: License):
        """
        Add a license.

        Args:
            license: License to add
        """
        self._licenses[license.license_id] = license
        logger.info(f"Added license: {license.license_id} ({license.quantity} seats)")

    def get_license(self, license_id: str) -> Optional[License]:
        """
        Get license by ID.

        Args:
            license_id: License ID

        Returns:
            License or None
        """
        return self._licenses.get(license_id)

    def list_licenses(
        self,
        app_id: Optional[str] = None,
        license_type: Optional[LicenseType] = None,
        status: Optional[LicenseStatus] = None,
    ) -> List[License]:
        """
        List licenses with filters.

        Args:
            app_id: Filter by application ID
            license_type: Filter by license type
            status: Filter by status

        Returns:
            List of licenses
        """
        licenses = list(self._licenses.values())

        if app_id:
            licenses = [l for l in licenses if l.app_id == app_id]

        if license_type:
            licenses = [l for l in licenses if l.license_type == license_type]

        if status:
            licenses = [l for l in licenses if l.get_status() == status]

        return licenses

    def assign_license(self, license_id: str, user_id: str) -> bool:
        """
        Assign license to user.

        Args:
            license_id: License ID
            user_id: User ID

        Returns:
            Success status
        """
        license = self.get_license(license_id)
        if not license:
            logger.error(f"License not found: {license_id}")
            return False

        if license.assigned >= license.quantity:
            logger.warning(f"No available licenses: {license_id}")
            return False

        if user_id not in self._user_assignments:
            self._user_assignments[user_id] = []

        if license_id not in self._user_assignments[user_id]:
            self._user_assignments[user_id].append(license_id)
            license.assigned += 1
            logger.info(f"Assigned license {license_id} to user {user_id}")
            return True

        return False

    def unassign_license(self, license_id: str, user_id: str) -> bool:
        """
        Unassign license from user.

        Args:
            license_id: License ID
            user_id: User ID

        Returns:
            Success status
        """
        if user_id not in self._user_assignments:
            return False

        if license_id in self._user_assignments[user_id]:
            self._user_assignments[user_id].remove(license_id)
            license = self.get_license(license_id)
            if license:
                license.assigned = max(0, license.assigned - 1)
            logger.info(f"Unassigned license {license_id} from user {user_id}")
            return True

        return False

    def get_user_licenses(self, user_id: str) -> List[License]:
        """
        Get all licenses assigned to a user.

        Args:
            user_id: User ID

        Returns:
            List of licenses
        """
        license_ids = self._user_assignments.get(user_id, [])
        return [self.get_license(lid) for lid in license_ids if self.get_license(lid)]

    def get_expiring_licenses(self, days: int = 30) -> List[License]:
        """
        Get licenses expiring within specified days.

        Args:
            days: Number of days

        Returns:
            List of expiring licenses
        """
        expiring = []
        current_time = datetime.now().timestamp()
        threshold = current_time + (days * 24 * 3600)

        for license in self._licenses.values():
            if license.expiration_date:
                if current_time < license.expiration_date <= threshold:
                    expiring.append(license)

        return sorted(expiring, key=lambda x: x.expiration_date or 0)

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get license optimization recommendations.

        Returns:
            List of recommendations
        """
        recommendations = []

        for license in self._licenses.values():
            utilization = license.get_utilization_rate()

            # Low utilization
            if utilization < 0.5 and license.quantity > 0:
                recommended_quantity = max(license.active + 2, int(license.active * 1.2))
                potential_savings = (license.quantity - recommended_quantity) * license.cost_per_license

                recommendations.append({
                    "type": "reduce_licenses",
                    "license_id": license.license_id,
                    "app_id": license.app_id,
                    "current_quantity": license.quantity,
                    "active_users": license.active,
                    "recommended_quantity": recommended_quantity,
                    "utilization": utilization,
                    "potential_savings": potential_savings,
                    "priority": "high" if potential_savings > 500 else "medium",
                })

            # Over-allocated (more assigned than quantity)
            if license.assigned > license.quantity:
                recommendations.append({
                    "type": "increase_licenses",
                    "license_id": license.license_id,
                    "app_id": license.app_id,
                    "current_quantity": license.quantity,
                    "assigned": license.assigned,
                    "shortage": license.assigned - license.quantity,
                    "priority": "high",
                })

            # Inactive licenses
            if license.active == 0 and license.quantity > 0:
                recommendations.append({
                    "type": "unused_license",
                    "license_id": license.license_id,
                    "app_id": license.app_id,
                    "quantity": license.quantity,
                    "monthly_waste": license.get_total_cost(),
                    "recommendation": "Consider canceling subscription",
                    "priority": "high",
                })

        return sorted(recommendations, key=lambda x: x.get("potential_savings", 0), reverse=True)

    def get_renewal_calendar(self, months: int = 3) -> List[Dict[str, Any]]:
        """
        Get upcoming license renewals.

        Args:
            months: Number of months to look ahead

        Returns:
            List of renewal events
        """
        renewals = []
        current_time = datetime.now().timestamp()
        threshold = current_time + (months * 30 * 24 * 3600)

        for license in self._licenses.values():
            renewal_date = license.renewal_date or license.expiration_date

            if renewal_date and current_time < renewal_date <= threshold:
                renewals.append({
                    "license_id": license.license_id,
                    "app_id": license.app_id,
                    "vendor": license.vendor,
                    "renewal_date": renewal_date,
                    "days_until_renewal": int((renewal_date - current_time) / (24 * 3600)),
                    "annual_cost": license.get_total_cost() * 12,
                    "current_utilization": license.get_utilization_rate(),
                })

        return sorted(renewals, key=lambda x: x["renewal_date"])

    def get_license_metrics(self) -> Dict[str, Any]:
        """
        Get license portfolio metrics.

        Returns:
            License metrics
        """
        licenses = list(self._licenses.values())

        total_quantity = sum(l.quantity for l in licenses)
        total_assigned = sum(l.assigned for l in licenses)
        total_active = sum(l.active for l in licenses)
        total_cost = sum(l.get_total_cost() for l in licenses)
        total_waste = sum(l.get_wasted_cost() for l in licenses)

        expiring_30 = len(self.get_expiring_licenses(30))
        expiring_90 = len(self.get_expiring_licenses(90))

        return {
            "total_licenses": len(licenses),
            "total_seats": total_quantity,
            "assigned_seats": total_assigned,
            "active_seats": total_active,
            "total_monthly_cost": total_cost,
            "wasted_monthly_cost": total_waste,
            "average_utilization": total_active / total_quantity if total_quantity > 0 else 0,
            "expiring_30_days": expiring_30,
            "expiring_90_days": expiring_90,
        }

    def optimize_allocation(self, app_id: str) -> Dict[str, Any]:
        """
        Optimize license allocation for an application.

        Args:
            app_id: Application ID

        Returns:
            Optimization plan
        """
        app_licenses = self.list_licenses(app_id=app_id)

        if not app_licenses:
            return {"status": "no_licenses_found"}

        total_quantity = sum(l.quantity for l in app_licenses)
        total_active = sum(l.active for l in app_licenses)
        total_cost = sum(l.get_total_cost() for l in app_licenses)

        # Recommend quantity with 20% buffer
        recommended_quantity = max(total_active + 2, int(total_active * 1.2))
        potential_savings = (total_quantity - recommended_quantity) * (
            total_cost / total_quantity if total_quantity > 0 else 0
        )

        return {
            "app_id": app_id,
            "current_licenses": total_quantity,
            "active_users": total_active,
            "recommended_licenses": recommended_quantity,
            "reduction": total_quantity - recommended_quantity,
            "current_monthly_cost": total_cost,
            "potential_monthly_savings": potential_savings,
            "potential_annual_savings": potential_savings * 12,
            "action": "reduce" if recommended_quantity < total_quantity else "maintain",
        }
