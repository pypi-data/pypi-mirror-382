"""
Policy Violation Tracking
==========================

Track, manage, and remediate policy violations.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ViolationStatus(Enum):
    """Violation status."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    IGNORED = "ignored"
    EXPIRED = "expired"


class RemediationStatus(Enum):
    """Remediation status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Remediation:
    """
    Remediation action for a violation.

    Attributes:
        action: Remediation action to take
        description: Description of remediation
        status: Current status
        assignee: Who is responsible
        due_date: When remediation is due
        completed_at: When remediation was completed
        metadata: Additional context
    """

    action: str
    description: str
    status: RemediationStatus = RemediationStatus.PENDING
    assignee: Optional[str] = None
    due_date: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Violation:
    """
    Policy violation record.

    Attributes:
        id: Unique violation ID
        policy_name: Name of violated policy
        resource_id: Affected resource
        violation_type: Type of violation
        severity: Violation severity
        description: Violation description
        status: Current status
        created_at: When violation was detected
        updated_at: Last update timestamp
        resolved_at: When violation was resolved
        remediation: Remediation actions
        metadata: Additional violation details
    """

    id: str
    policy_name: str
    resource_id: str
    violation_type: str
    severity: str
    description: str
    status: ViolationStatus = ViolationStatus.OPEN
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    resolved_at: Optional[float] = None
    remediation: Optional[Remediation] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_status(self, new_status: ViolationStatus, note: str = ""):
        """Update violation status."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now().timestamp()

        if new_status == ViolationStatus.RESOLVED:
            self.resolved_at = self.updated_at

        logger.info(
            f"Violation {self.id} status changed: {old_status.value} -> {new_status.value}. {note}"
        )

    def assign_remediation(self, remediation: Remediation):
        """Assign remediation action."""
        self.remediation = remediation
        self.updated_at = datetime.now().timestamp()
        logger.info(f"Remediation assigned to violation {self.id}: {remediation.action}")

    def get_age_hours(self) -> float:
        """Get violation age in hours."""
        current_time = datetime.now().timestamp()
        age_seconds = current_time - self.created_at
        return age_seconds / 3600

    def is_overdue(self) -> bool:
        """Check if remediation is overdue."""
        if not self.remediation or not self.remediation.due_date:
            return False

        if self.status in [ViolationStatus.RESOLVED, ViolationStatus.IGNORED]:
            return False

        current_time = datetime.now().timestamp()
        return current_time > self.remediation.due_date


class ViolationTracker:
    """
    Tracks and manages policy violations.
    """

    def __init__(self):
        """Initialize violation tracker."""
        self._violations: Dict[str, Violation] = {}
        self._violation_counter = 0

    def create_violation(
        self,
        policy_name: str,
        resource_id: str,
        violation_type: str,
        severity: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Violation:
        """
        Create a new violation.

        Args:
            policy_name: Name of violated policy
            resource_id: Affected resource ID
            violation_type: Type of violation
            severity: Violation severity
            description: Description
            metadata: Additional details

        Returns:
            Created violation
        """
        self._violation_counter += 1
        violation_id = f"VIO-{self._violation_counter:06d}"

        violation = Violation(
            id=violation_id,
            policy_name=policy_name,
            resource_id=resource_id,
            violation_type=violation_type,
            severity=severity,
            description=description,
            metadata=metadata or {},
        )

        self._violations[violation_id] = violation
        logger.info(f"Created violation {violation_id} for resource {resource_id}")

        return violation

    def get_violation(self, violation_id: str) -> Optional[Violation]:
        """Get violation by ID."""
        return self._violations.get(violation_id)

    def list_violations(
        self,
        status: Optional[ViolationStatus] = None,
        severity: Optional[str] = None,
        policy_name: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> List[Violation]:
        """
        List violations with optional filters.

        Args:
            status: Filter by status
            severity: Filter by severity
            policy_name: Filter by policy
            resource_id: Filter by resource

        Returns:
            List of matching violations
        """
        violations = list(self._violations.values())

        if status:
            violations = [v for v in violations if v.status == status]

        if severity:
            violations = [v for v in violations if v.severity == severity]

        if policy_name:
            violations = [v for v in violations if v.policy_name == policy_name]

        if resource_id:
            violations = [v for v in violations if v.resource_id == resource_id]

        return violations

    def update_violation_status(
        self, violation_id: str, new_status: ViolationStatus, note: str = ""
    ):
        """Update violation status."""
        violation = self.get_violation(violation_id)
        if not violation:
            raise ValueError(f"Violation not found: {violation_id}")

        violation.update_status(new_status, note)

    def assign_remediation(
        self,
        violation_id: str,
        action: str,
        description: str,
        assignee: Optional[str] = None,
        due_in_hours: int = 24,
    ):
        """
        Assign remediation to a violation.

        Args:
            violation_id: Violation ID
            action: Remediation action
            description: Remediation description
            assignee: Person responsible
            due_in_hours: Hours until due
        """
        violation = self.get_violation(violation_id)
        if not violation:
            raise ValueError(f"Violation not found: {violation_id}")

        due_date = datetime.now() + timedelta(hours=due_in_hours)

        remediation = Remediation(
            action=action,
            description=description,
            assignee=assignee,
            due_date=due_date.timestamp(),
        )

        violation.assign_remediation(remediation)

    def bulk_create_from_evaluation(
        self, policy_name: str, evaluation: Dict[str, Any]
    ) -> List[Violation]:
        """
        Create violations from policy evaluation.

        Args:
            policy_name: Policy name
            evaluation: Policy evaluation result

        Returns:
            List of created violations
        """
        violations_data = evaluation.get("violations", [])
        created_violations = []

        for violation_data in violations_data:
            violation = self.create_violation(
                policy_name=policy_name,
                resource_id=violation_data.get("resource_id", "unknown"),
                violation_type=violation_data.get("type", "unknown"),
                severity=evaluation.get("metadata", {}).get("severity", "warning"),
                description=violation_data.get("description", ""),
                metadata=violation_data,
            )
            created_violations.append(violation)

        return created_violations

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get violation statistics.

        Returns:
            Statistics summary
        """
        total = len(self._violations)
        if total == 0:
            return {
                "total_violations": 0,
                "by_status": {},
                "by_severity": {},
                "by_policy": {},
                "overdue_count": 0,
            }

        # Count by status
        by_status = defaultdict(int)
        for v in self._violations.values():
            by_status[v.status.value] += 1

        # Count by severity
        by_severity = defaultdict(int)
        for v in self._violations.values():
            by_severity[v.severity] += 1

        # Count by policy
        by_policy = defaultdict(int)
        for v in self._violations.values():
            by_policy[v.policy_name] += 1

        # Count overdue
        overdue = sum(1 for v in self._violations.values() if v.is_overdue())

        # Average resolution time
        resolved = [v for v in self._violations.values() if v.status == ViolationStatus.RESOLVED]
        avg_resolution_hours = 0.0
        if resolved:
            resolution_times = [
                (v.resolved_at - v.created_at) / 3600 for v in resolved if v.resolved_at
            ]
            avg_resolution_hours = sum(resolution_times) / len(resolution_times)

        return {
            "total_violations": total,
            "by_status": dict(by_status),
            "by_severity": dict(by_severity),
            "by_policy": dict(by_policy),
            "overdue_count": overdue,
            "resolved_count": len(resolved),
            "average_resolution_hours": avg_resolution_hours,
        }

    def get_violations_by_resource(self) -> Dict[str, List[Violation]]:
        """
        Group violations by resource.

        Returns:
            Dictionary mapping resource_id to violations
        """
        by_resource = defaultdict(list)

        for violation in self._violations.values():
            by_resource[violation.resource_id].append(violation)

        return dict(by_resource)

    def get_overdue_violations(self) -> List[Violation]:
        """Get all overdue violations."""
        return [v for v in self._violations.values() if v.is_overdue()]

    def auto_resolve_duplicates(self, resource_id: str, violation_type: str):
        """
        Auto-resolve duplicate violations for same resource/type.

        Args:
            resource_id: Resource ID
            violation_type: Violation type
        """
        violations = [
            v
            for v in self._violations.values()
            if v.resource_id == resource_id
            and v.violation_type == violation_type
            and v.status == ViolationStatus.OPEN
        ]

        # Keep newest, resolve older ones
        if len(violations) > 1:
            violations.sort(key=lambda v: v.created_at, reverse=True)
            for old_violation in violations[1:]:
                old_violation.update_status(
                    ViolationStatus.RESOLVED,
                    "Auto-resolved as duplicate",
                )

    def cleanup_old_resolved(self, days: int = 30):
        """
        Clean up old resolved violations.

        Args:
            days: Age threshold in days
        """
        cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()

        to_remove = []
        for violation_id, violation in self._violations.items():
            if (
                violation.status == ViolationStatus.RESOLVED
                and violation.resolved_at
                and violation.resolved_at < cutoff_time
            ):
                to_remove.append(violation_id)

        for violation_id in to_remove:
            del self._violations[violation_id]

        logger.info(f"Cleaned up {len(to_remove)} old resolved violations")

    def export_violations(self, status_filter: Optional[ViolationStatus] = None) -> List[Dict[str, Any]]:
        """
        Export violations as dictionaries.

        Args:
            status_filter: Optional status filter

        Returns:
            List of violation data
        """
        violations = self.list_violations(status=status_filter)

        return [
            {
                "id": v.id,
                "policy_name": v.policy_name,
                "resource_id": v.resource_id,
                "violation_type": v.violation_type,
                "severity": v.severity,
                "description": v.description,
                "status": v.status.value,
                "created_at": v.created_at,
                "updated_at": v.updated_at,
                "resolved_at": v.resolved_at,
                "age_hours": v.get_age_hours(),
                "is_overdue": v.is_overdue(),
                "remediation": (
                    {
                        "action": v.remediation.action,
                        "description": v.remediation.description,
                        "status": v.remediation.status.value,
                        "assignee": v.remediation.assignee,
                        "due_date": v.remediation.due_date,
                    }
                    if v.remediation
                    else None
                ),
                "metadata": v.metadata,
            }
            for v in violations
        ]
