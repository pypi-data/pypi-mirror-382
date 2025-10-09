"""
FinOps-as-Code Resources
=========================

Resource definitions for managing OpenFinOps infrastructure as code.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ResourceState(Enum):
    """Resource lifecycle states."""

    PENDING = "pending"
    CREATING = "creating"
    ACTIVE = "active"
    UPDATING = "updating"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILED = "failed"


class Resource(ABC):
    """
    Base class for OpenFinOps resources.
    """

    def __init__(self, name: str, provider: Any):
        """
        Initialize resource.

        Args:
            name: Resource name
            provider: OpenFinOps provider instance
        """
        self.name = name
        self.provider = provider
        self.state = ResourceState.PENDING
        self.resource_id: Optional[str] = None

    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        """
        Validate resource configuration.

        Returns:
            Validation results
        """
        pass

    @abstractmethod
    def create(self) -> str:
        """
        Create resource.

        Returns:
            Resource ID
        """
        pass

    @abstractmethod
    def read(self) -> Dict[str, Any]:
        """
        Read resource state.

        Returns:
            Resource data
        """
        pass

    @abstractmethod
    def update(self, **changes) -> bool:
        """
        Update resource.

        Args:
            **changes: Fields to update

        Returns:
            Success status
        """
        pass

    @abstractmethod
    def delete(self) -> bool:
        """
        Delete resource.

        Returns:
            Success status
        """
        pass

    def get_plan_action(self) -> str:
        """
        Determine plan action for resource.

        Returns:
            Action: create, update, delete, no_change
        """
        if self.state == ResourceState.PENDING:
            return "create"
        elif self.state == ResourceState.DELETED:
            return "delete"
        elif hasattr(self, "_has_changes") and self._has_changes():
            return "update"
        else:
            return "no_change"

    def to_terraform(self) -> Dict[str, Any]:
        """
        Convert resource to Terraform HCL format.

        Returns:
            Terraform resource configuration
        """
        return {
            "name": self.name,
            "id": self.resource_id,
            "state": self.state.value,
        }


class BudgetResource(Resource):
    """
    Budget resource.

    Manages cost budgets and thresholds.
    """

    def __init__(
        self,
        name: str,
        provider: Any,
        amount: float = 0.0,
        period: str = "monthly",
        currency: str = "USD",
        filters: Optional[Dict[str, Any]] = None,
        alerts: Optional[List[Dict[str, Any]]] = None,
        actions: Optional[List[str]] = None,
    ):
        """Initialize budget resource."""
        super().__init__(name, provider)
        self.amount = amount
        self.period = period
        self.currency = currency
        self.filters = filters or {}
        self.alerts = alerts or []
        self.actions = actions or []

    def validate(self) -> Dict[str, Any]:
        """Validate budget configuration."""
        errors = []

        if self.amount <= 0:
            errors.append("Budget amount must be positive")

        if self.period not in ["hourly", "daily", "weekly", "monthly", "quarterly", "yearly"]:
            errors.append(f"Invalid period: {self.period}")

        return {"valid": len(errors) == 0, "errors": errors}

    def create(self) -> str:
        """Create budget."""
        self.state = ResourceState.CREATING
        logger.info(f"Creating budget: {self.name}")

        # In production, call API to create budget
        self.resource_id = f"budget-{hash(self.name)}"
        self.state = ResourceState.ACTIVE

        logger.info(f"Created budget: {self.resource_id}")
        return self.resource_id

    def read(self) -> Dict[str, Any]:
        """Read budget state."""
        return {
            "name": self.name,
            "amount": self.amount,
            "period": self.period,
            "currency": self.currency,
            "filters": self.filters,
            "alerts": self.alerts,
            "state": self.state.value,
        }

    def update(self, **changes) -> bool:
        """Update budget."""
        self.state = ResourceState.UPDATING
        logger.info(f"Updating budget: {self.name}")

        for key, value in changes.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.state = ResourceState.ACTIVE
        logger.info(f"Updated budget: {self.resource_id}")
        return True

    def delete(self) -> bool:
        """Delete budget."""
        self.state = ResourceState.DELETING
        logger.info(f"Deleting budget: {self.name}")

        # In production, call API to delete budget
        self.state = ResourceState.DELETED

        logger.info(f"Deleted budget: {self.resource_id}")
        return True

    def to_terraform(self) -> Dict[str, Any]:
        """Convert to Terraform format."""
        return {
            "resource": {
                "openfinops_budget": {
                    self.name: {
                        "amount": self.amount,
                        "period": self.period,
                        "currency": self.currency,
                        "filters": self.filters,
                        "alerts": self.alerts,
                        "actions": self.actions,
                    }
                }
            }
        }


class PolicyResource(Resource):
    """
    Policy resource.

    Manages governance policies.
    """

    def __init__(
        self,
        name: str,
        provider: Any,
        policy_type: str = "budget",
        rules: Optional[List[Dict[str, Any]]] = None,
        enabled: bool = True,
        severity: str = "warning",
        actions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        """Initialize policy resource."""
        super().__init__(name, provider)
        self.policy_type = policy_type
        self.rules = rules or []
        self.enabled = enabled
        self.severity = severity
        self.actions = actions or []
        self.tags = tags or {}

    def validate(self) -> Dict[str, Any]:
        """Validate policy configuration."""
        errors = []

        if self.policy_type not in ["budget", "compliance", "lifecycle", "security", "tagging"]:
            errors.append(f"Invalid policy type: {self.policy_type}")

        if not self.rules:
            errors.append("Policy must have at least one rule")

        return {"valid": len(errors) == 0, "errors": errors}

    def create(self) -> str:
        """Create policy."""
        self.state = ResourceState.CREATING
        logger.info(f"Creating policy: {self.name}")

        self.resource_id = f"policy-{hash(self.name)}"
        self.state = ResourceState.ACTIVE

        logger.info(f"Created policy: {self.resource_id}")
        return self.resource_id

    def read(self) -> Dict[str, Any]:
        """Read policy state."""
        return {
            "name": self.name,
            "policy_type": self.policy_type,
            "rules": self.rules,
            "enabled": self.enabled,
            "severity": self.severity,
            "state": self.state.value,
        }

    def update(self, **changes) -> bool:
        """Update policy."""
        self.state = ResourceState.UPDATING
        logger.info(f"Updating policy: {self.name}")

        for key, value in changes.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.state = ResourceState.ACTIVE
        logger.info(f"Updated policy: {self.resource_id}")
        return True

    def delete(self) -> bool:
        """Delete policy."""
        self.state = ResourceState.DELETING
        logger.info(f"Deleting policy: {self.name}")

        self.state = ResourceState.DELETED

        logger.info(f"Deleted policy: {self.resource_id}")
        return True

    def to_terraform(self) -> Dict[str, Any]:
        """Convert to Terraform format."""
        return {
            "resource": {
                "openfinops_policy": {
                    self.name: {
                        "policy_type": self.policy_type,
                        "rules": self.rules,
                        "enabled": self.enabled,
                        "severity": self.severity,
                        "actions": self.actions,
                        "tags": self.tags,
                    }
                }
            }
        }


class AlertResource(Resource):
    """
    Alert resource.

    Manages cost and compliance alerts.
    """

    def __init__(
        self,
        name: str,
        provider: Any,
        condition: Optional[Dict[str, Any]] = None,
        threshold: float = 0.0,
        comparison: str = "greater_than",
        notification_channels: Optional[List[str]] = None,
        enabled: bool = True,
        severity: str = "warning",
    ):
        """Initialize alert resource."""
        super().__init__(name, provider)
        self.condition = condition or {}
        self.threshold = threshold
        self.comparison = comparison
        self.notification_channels = notification_channels or []
        self.enabled = enabled
        self.severity = severity

    def validate(self) -> Dict[str, Any]:
        """Validate alert configuration."""
        errors = []

        if not self.condition:
            errors.append("Alert condition is required")

        if self.comparison not in ["greater_than", "less_than", "equal_to", "not_equal_to"]:
            errors.append(f"Invalid comparison: {self.comparison}")

        if not self.notification_channels:
            errors.append("At least one notification channel is required")

        return {"valid": len(errors) == 0, "errors": errors}

    def create(self) -> str:
        """Create alert."""
        self.state = ResourceState.CREATING
        logger.info(f"Creating alert: {self.name}")

        self.resource_id = f"alert-{hash(self.name)}"
        self.state = ResourceState.ACTIVE

        logger.info(f"Created alert: {self.resource_id}")
        return self.resource_id

    def read(self) -> Dict[str, Any]:
        """Read alert state."""
        return {
            "name": self.name,
            "condition": self.condition,
            "threshold": self.threshold,
            "comparison": self.comparison,
            "channels": self.notification_channels,
            "enabled": self.enabled,
            "state": self.state.value,
        }

    def update(self, **changes) -> bool:
        """Update alert."""
        self.state = ResourceState.UPDATING
        logger.info(f"Updating alert: {self.name}")

        for key, value in changes.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.state = ResourceState.ACTIVE
        logger.info(f"Updated alert: {self.resource_id}")
        return True

    def delete(self) -> bool:
        """Delete alert."""
        self.state = ResourceState.DELETING
        logger.info(f"Deleting alert: {self.name}")

        self.state = ResourceState.DELETED

        logger.info(f"Deleted alert: {self.resource_id}")
        return True

    def to_terraform(self) -> Dict[str, Any]:
        """Convert to Terraform format."""
        return {
            "resource": {
                "openfinops_alert": {
                    self.name: {
                        "condition": self.condition,
                        "threshold": self.threshold,
                        "comparison": self.comparison,
                        "notification_channels": self.notification_channels,
                        "enabled": self.enabled,
                        "severity": self.severity,
                    }
                }
            }
        }


class DashboardResource(Resource):
    """
    Dashboard resource.

    Manages custom dashboards.
    """

    def __init__(
        self,
        name: str,
        provider: Any,
        description: str = "",
        widgets: Optional[List[Dict[str, Any]]] = None,
        layout: str = "grid",
        refresh_interval: int = 300,
        visibility: str = "private",
        tags: Optional[Dict[str, str]] = None,
    ):
        """Initialize dashboard resource."""
        super().__init__(name, provider)
        self.description = description
        self.widgets = widgets or []
        self.layout = layout
        self.refresh_interval = refresh_interval
        self.visibility = visibility
        self.tags = tags or {}

    def validate(self) -> Dict[str, Any]:
        """Validate dashboard configuration."""
        errors = []

        if not self.widgets:
            errors.append("Dashboard must have at least one widget")

        if self.layout not in ["grid", "flex", "rows", "columns"]:
            errors.append(f"Invalid layout: {self.layout}")

        return {"valid": len(errors) == 0, "errors": errors}

    def create(self) -> str:
        """Create dashboard."""
        self.state = ResourceState.CREATING
        logger.info(f"Creating dashboard: {self.name}")

        self.resource_id = f"dashboard-{hash(self.name)}"
        self.state = ResourceState.ACTIVE

        logger.info(f"Created dashboard: {self.resource_id}")
        return self.resource_id

    def read(self) -> Dict[str, Any]:
        """Read dashboard state."""
        return {
            "name": self.name,
            "description": self.description,
            "widgets": self.widgets,
            "layout": self.layout,
            "refresh_interval": self.refresh_interval,
            "state": self.state.value,
        }

    def update(self, **changes) -> bool:
        """Update dashboard."""
        self.state = ResourceState.UPDATING
        logger.info(f"Updating dashboard: {self.name}")

        for key, value in changes.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.state = ResourceState.ACTIVE
        logger.info(f"Updated dashboard: {self.resource_id}")
        return True

    def delete(self) -> bool:
        """Delete dashboard."""
        self.state = ResourceState.DELETING
        logger.info(f"Deleting dashboard: {self.name}")

        self.state = ResourceState.DELETED

        logger.info(f"Deleted dashboard: {self.resource_id}")
        return True

    def to_terraform(self) -> Dict[str, Any]:
        """Convert to Terraform format."""
        return {
            "resource": {
                "openfinops_dashboard": {
                    self.name: {
                        "description": self.description,
                        "widgets": self.widgets,
                        "layout": self.layout,
                        "refresh_interval": self.refresh_interval,
                        "visibility": self.visibility,
                        "tags": self.tags,
                    }
                }
            }
        }


# Helper functions for resource creation
def budget(
    name: str,
    amount: float,
    period: str = "monthly",
    provider: Any = None,
    **kwargs,
) -> BudgetResource:
    """
    Create a budget resource.

    Args:
        name: Budget name
        amount: Budget amount
        period: Budget period
        provider: OpenFinOps provider
        **kwargs: Additional budget options

    Returns:
        Budget resource instance
    """
    resource = BudgetResource(
        name=name,
        provider=provider,
        amount=amount,
        period=period,
        **kwargs,
    )

    if provider:
        provider.register_resource("budget", name, resource)

    return resource


def policy(
    name: str,
    policy_type: str,
    rules: List[Dict[str, Any]],
    provider: Any = None,
    **kwargs,
) -> PolicyResource:
    """
    Create a policy resource.

    Args:
        name: Policy name
        policy_type: Type of policy
        rules: Policy rules
        provider: OpenFinOps provider
        **kwargs: Additional policy options

    Returns:
        Policy resource instance
    """
    resource = PolicyResource(
        name=name,
        provider=provider,
        policy_type=policy_type,
        rules=rules,
        **kwargs,
    )

    if provider:
        provider.register_resource("policy", name, resource)

    return resource


def alert(
    name: str,
    condition: Dict[str, Any],
    threshold: float,
    notification_channels: List[str],
    provider: Any = None,
    **kwargs,
) -> AlertResource:
    """
    Create an alert resource.

    Args:
        name: Alert name
        condition: Alert condition
        threshold: Alert threshold
        notification_channels: Notification channels
        provider: OpenFinOps provider
        **kwargs: Additional alert options

    Returns:
        Alert resource instance
    """
    resource = AlertResource(
        name=name,
        provider=provider,
        condition=condition,
        threshold=threshold,
        notification_channels=notification_channels,
        **kwargs,
    )

    if provider:
        provider.register_resource("alert", name, resource)

    return resource


def dashboard(
    name: str,
    widgets: List[Dict[str, Any]],
    provider: Any = None,
    **kwargs,
) -> DashboardResource:
    """
    Create a dashboard resource.

    Args:
        name: Dashboard name
        widgets: Dashboard widgets
        provider: OpenFinOps provider
        **kwargs: Additional dashboard options

    Returns:
        Dashboard resource instance
    """
    resource = DashboardResource(
        name=name,
        provider=provider,
        widgets=widgets,
        **kwargs,
    )

    if provider:
        provider.register_resource("dashboard", name, resource)

    return resource
