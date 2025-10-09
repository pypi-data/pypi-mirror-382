"""
Resource Lifecycle Policies
============================

Policies for managing resource lifecycle, idle detection, and auto-shutdown.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from .policy_engine import Policy, PolicyType, PolicySeverity

logger = logging.getLogger(__name__)


class ResourceState(Enum):
    """Resource lifecycle states."""

    ACTIVE = "active"
    IDLE = "idle"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    SCHEDULED_FOR_DELETION = "scheduled_for_deletion"


class LifecycleAction(Enum):
    """Lifecycle actions."""

    STOP = "stop"
    TERMINATE = "terminate"
    SNAPSHOT = "snapshot"
    DOWNSIZE = "downsize"
    NOTIFY_OWNER = "notify_owner"
    TAG_FOR_REVIEW = "tag_for_review"
    NO_ACTION = "no_action"


@dataclass
class IdleDetectionConfig:
    """
    Configuration for idle resource detection.

    Attributes:
        cpu_threshold: CPU usage threshold (%)
        network_threshold: Network throughput threshold (bytes/sec)
        memory_threshold: Memory usage threshold (%)
        duration_minutes: Duration to be considered idle
        check_interval_minutes: How often to check
    """

    cpu_threshold: float = 5.0
    network_threshold: float = 1000.0
    memory_threshold: float = 20.0
    duration_minutes: int = 60
    check_interval_minutes: int = 15


class LifecyclePolicy(Policy):
    """
    Resource lifecycle management policy.

    Manages resource lifecycle based on usage patterns and age.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        resource_types: Optional[List[str]] = None,
        idle_config: Optional[IdleDetectionConfig] = None,
        max_age_days: Optional[int] = None,
        auto_action: LifecycleAction = LifecycleAction.NOTIFY_OWNER,
        grace_period_hours: int = 24,
        exclude_tags: Optional[Dict[str, str]] = None,
        scope: Optional[Dict[str, Any]] = None,
        severity: PolicySeverity = PolicySeverity.WARNING,
        actions: Optional[List[str]] = None,
    ):
        """
        Initialize lifecycle policy.

        Args:
            name: Policy name
            description: Policy description
            resource_types: Types of resources this applies to
            idle_config: Idle detection configuration
            max_age_days: Maximum resource age before action
            auto_action: Action to take automatically
            grace_period_hours: Grace period before taking action
            exclude_tags: Resources with these tags are excluded
            scope: Policy scope
            severity: Default severity
            actions: Actions to take
        """
        super().__init__(
            name=name,
            description=description,
            policy_type=PolicyType.LIFECYCLE,
            severity=severity,
            scope=scope or {},
            actions=actions or ["notify"],
        )

        self.resource_types = resource_types or []
        self.idle_config = idle_config or IdleDetectionConfig()
        self.max_age_days = max_age_days
        self.auto_action = auto_action
        self.grace_period_hours = grace_period_hours
        self.exclude_tags = exclude_tags or {}

    def _evaluate_conditions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate lifecycle conditions."""
        resources = context.get("resources", [])
        if not isinstance(resources, list):
            resources = [resources]

        current_time = context.get("current_time", datetime.now().timestamp())
        violations = []

        for resource in resources:
            # Skip if excluded by tags
            if self._is_excluded(resource):
                continue

            # Skip if not matching resource type
            if self.resource_types and resource.get("type") not in self.resource_types:
                continue

            # Check idle status
            if self._is_idle(resource, context):
                violations.append(
                    {
                        "type": "idle_resource",
                        "resource_id": resource.get("id"),
                        "resource_type": resource.get("type"),
                        "state": ResourceState.IDLE.value,
                        "recommended_action": self.auto_action.value,
                        "reason": "Resource is idle based on usage metrics",
                        "cost_impact": self._estimate_cost_savings(resource),
                    }
                )

            # Check age
            if self.max_age_days and self._is_too_old(resource, current_time):
                age_days = self._get_age_days(resource, current_time)
                violations.append(
                    {
                        "type": "aged_resource",
                        "resource_id": resource.get("id"),
                        "resource_type": resource.get("type"),
                        "age_days": age_days,
                        "max_age_days": self.max_age_days,
                        "recommended_action": self.auto_action.value,
                        "reason": f"Resource exceeds maximum age of {self.max_age_days} days",
                    }
                )

        return violations

    def _is_excluded(self, resource: Dict[str, Any]) -> bool:
        """Check if resource is excluded by tags."""
        tags = resource.get("tags", {})

        for key, value in self.exclude_tags.items():
            if tags.get(key) == value:
                return True

        # Check for protected tag
        if tags.get("lifecycle_policy") == "protected":
            return True

        return False

    def _is_idle(self, resource: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if resource is idle."""
        metrics = resource.get("metrics", {})

        # Get recent metrics
        cpu_usage = metrics.get("cpu_usage", 100.0)
        network_bytes = metrics.get("network_bytes_per_sec", float("inf"))
        memory_usage = metrics.get("memory_usage", 100.0)

        # Check against thresholds
        is_idle = (
            cpu_usage < self.idle_config.cpu_threshold
            and network_bytes < self.idle_config.network_threshold
            and memory_usage < self.idle_config.memory_threshold
        )

        # Check duration
        if is_idle:
            idle_since = metrics.get("idle_since")
            if idle_since:
                current_time = context.get("current_time", datetime.now().timestamp())
                idle_duration_minutes = (current_time - idle_since) / 60

                return idle_duration_minutes >= self.idle_config.duration_minutes

        return False

    def _is_too_old(self, resource: Dict[str, Any], current_time: float) -> bool:
        """Check if resource exceeds maximum age."""
        if not self.max_age_days:
            return False

        age_days = self._get_age_days(resource, current_time)
        return age_days > self.max_age_days

    def _get_age_days(self, resource: Dict[str, Any], current_time: float) -> float:
        """Get resource age in days."""
        created_at = resource.get("created_at")
        if not created_at:
            return 0.0

        age_seconds = current_time - created_at
        return age_seconds / 86400  # Convert to days

    def _estimate_cost_savings(self, resource: Dict[str, Any]) -> float:
        """Estimate cost savings from taking action."""
        # Simple estimation based on resource cost
        monthly_cost = resource.get("monthly_cost", 0.0)

        if self.auto_action == LifecycleAction.STOP:
            # Stopping saves compute but not storage
            return monthly_cost * 0.7  # Estimate 70% savings

        elif self.auto_action == LifecycleAction.TERMINATE:
            # Terminating saves everything
            return monthly_cost

        elif self.auto_action == LifecycleAction.DOWNSIZE:
            # Downsizing saves some cost
            return monthly_cost * 0.5  # Estimate 50% savings

        return 0.0

    def get_lifecycle_recommendation(
        self, resource: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get lifecycle recommendation for a resource.

        Args:
            resource: Resource to evaluate
            context: Evaluation context

        Returns:
            Recommendation details
        """
        violations = self._evaluate_conditions({"resources": [resource], **context})

        if not violations:
            return {
                "resource_id": resource.get("id"),
                "action": LifecycleAction.NO_ACTION.value,
                "reason": "Resource is actively used and within age limits",
            }

        # Take first violation (most critical)
        violation = violations[0]

        return {
            "resource_id": resource.get("id"),
            "action": violation.get("recommended_action"),
            "reason": violation.get("reason"),
            "cost_savings": violation.get("cost_impact", 0.0),
            "grace_period_hours": self.grace_period_hours,
            "violation_type": violation.get("type"),
        }


class ScheduledActionPolicy(Policy):
    """
    Policy for scheduled resource actions (stop/start).
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        schedule: Optional[Dict[str, Any]] = None,
        action: LifecycleAction = LifecycleAction.STOP,
        resource_types: Optional[List[str]] = None,
        scope: Optional[Dict[str, Any]] = None,
        severity: PolicySeverity = PolicySeverity.INFO,
    ):
        """
        Initialize scheduled action policy.

        Args:
            name: Policy name
            description: Policy description
            schedule: Schedule configuration (cron-like)
            action: Action to take on schedule
            resource_types: Types of resources
            scope: Policy scope
            severity: Severity level
        """
        super().__init__(
            name=name,
            description=description,
            policy_type=PolicyType.LIFECYCLE,
            severity=severity,
            scope=scope or {},
            actions=[action.value],
        )

        self.schedule = schedule or {}
        self.action = action
        self.resource_types = resource_types or []

    def _evaluate_conditions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate scheduled actions."""
        current_time = context.get("current_time", datetime.now())
        if isinstance(current_time, float):
            current_time = datetime.fromtimestamp(current_time)

        resources = context.get("resources", [])
        if not isinstance(resources, list):
            resources = [resources]

        violations = []

        # Check if current time matches schedule
        if self._matches_schedule(current_time):
            for resource in resources:
                if self.resource_types and resource.get("type") not in self.resource_types:
                    continue

                violations.append(
                    {
                        "type": "scheduled_action",
                        "resource_id": resource.get("id"),
                        "action": self.action.value,
                        "scheduled_time": current_time.isoformat(),
                        "reason": f"Scheduled {self.action.value} per policy",
                    }
                )

        return violations

    def _matches_schedule(self, current_time: datetime) -> bool:
        """Check if current time matches schedule."""
        # Simple schedule matching (can be extended with cron-like syntax)
        hour = self.schedule.get("hour")
        if hour is not None and current_time.hour != hour:
            return False

        day_of_week = self.schedule.get("day_of_week")
        if day_of_week is not None and current_time.weekday() != day_of_week:
            return False

        return True


def create_idle_resource_policy(
    resource_type: str = "ec2",
    auto_stop: bool = True,
) -> LifecyclePolicy:
    """
    Create policy for idle resource detection.

    Args:
        resource_type: Type of resource
        auto_stop: Whether to auto-stop idle resources

    Returns:
        Configured lifecycle policy
    """
    return LifecyclePolicy(
        name=f"idle_{resource_type}_policy",
        description=f"Detect and handle idle {resource_type} instances",
        resource_types=[resource_type],
        idle_config=IdleDetectionConfig(
            cpu_threshold=5.0,
            network_threshold=1000.0,
            memory_threshold=20.0,
            duration_minutes=120,  # 2 hours
        ),
        auto_action=LifecycleAction.STOP if auto_stop else LifecycleAction.NOTIFY_OWNER,
        grace_period_hours=24,
        exclude_tags={"environment": "production"},
        severity=PolicySeverity.WARNING,
    )


def create_weekend_shutdown_policy(resource_types: Optional[List[str]] = None) -> ScheduledActionPolicy:
    """
    Create policy for weekend shutdown.

    Args:
        resource_types: Types of resources to shutdown

    Returns:
        Scheduled action policy
    """
    return ScheduledActionPolicy(
        name="weekend_shutdown",
        description="Stop non-production resources on weekends",
        schedule={"day_of_week": 5, "hour": 18},  # Friday 6 PM
        action=LifecycleAction.STOP,
        resource_types=resource_types or ["ec2", "rds"],
        scope={"environment": ["dev", "staging"]},
        severity=PolicySeverity.INFO,
    )
