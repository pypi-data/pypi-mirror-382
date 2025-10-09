"""
Core Policy Engine
==================

Central policy engine for defining, evaluating, and enforcing FinOps policies.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of policies."""

    BUDGET = "budget"
    COMPLIANCE = "compliance"
    LIFECYCLE = "lifecycle"
    SECURITY = "security"
    TAGGING = "tagging"
    CUSTOM = "custom"


class PolicySeverity(Enum):
    """Policy violation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class PolicyStatus(Enum):
    """Policy status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    ARCHIVED = "archived"


@dataclass
class PolicyEvaluation:
    """
    Result of policy evaluation.

    Attributes:
        policy_name: Name of evaluated policy
        passed: Whether evaluation passed
        violations: List of violations found
        timestamp: Evaluation timestamp
        metadata: Additional context
    """

    policy_name: str
    passed: bool
    violations: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Policy:
    """
    Base policy definition.

    Attributes:
        name: Policy name (unique identifier)
        description: Policy description
        policy_type: Type of policy
        severity: Violation severity
        status: Policy status
        scope: Scope criteria (e.g., {"team": "platform"})
        conditions: Policy conditions to evaluate
        actions: Actions to take on violation
        metadata: Additional policy metadata
    """

    name: str
    description: str
    policy_type: PolicyType
    severity: PolicySeverity = PolicySeverity.WARNING
    status: PolicyStatus = PolicyStatus.ACTIVE
    scope: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, context: Dict[str, Any]) -> PolicyEvaluation:
        """
        Evaluate policy against context.

        Args:
            context: Evaluation context (resources, costs, etc.)

        Returns:
            Policy evaluation result
        """
        # Check if policy applies to this context
        if not self._applies_to_context(context):
            return PolicyEvaluation(
                policy_name=self.name,
                passed=True,
                metadata={"reason": "policy_scope_not_applicable"},
            )

        # Evaluate conditions
        violations = self._evaluate_conditions(context)

        return PolicyEvaluation(
            policy_name=self.name,
            passed=len(violations) == 0,
            violations=violations,
            metadata={"severity": self.severity.value, "actions": self.actions},
        )

    def _applies_to_context(self, context: Dict[str, Any]) -> bool:
        """Check if policy applies to this context."""
        if not self.scope:
            return True  # No scope restrictions

        # Check scope criteria
        for key, value in self.scope.items():
            context_value = context.get(key)
            if isinstance(value, list):
                if context_value not in value:
                    return False
            elif context_value != value:
                return False

        return True

    def _evaluate_conditions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate policy conditions.

        Override in subclasses for specific policy logic.
        """
        return []


class PolicyEngine:
    """
    Central policy engine for managing and evaluating policies.
    """

    def __init__(self):
        """Initialize policy engine."""
        self._policies: Dict[str, Policy] = {}
        self._policy_groups: Dict[str, Set[str]] = {}
        self._evaluation_history: List[PolicyEvaluation] = []

    def add_policy(self, policy: Policy):
        """
        Add a policy to the engine.

        Args:
            policy: Policy to add
        """
        if policy.name in self._policies:
            logger.warning(f"Policy '{policy.name}' already exists, overwriting")

        self._policies[policy.name] = policy
        logger.info(f"Added policy: {policy.name} ({policy.policy_type.value})")

    def remove_policy(self, policy_name: str):
        """Remove a policy."""
        if policy_name in self._policies:
            del self._policies[policy_name]
            logger.info(f"Removed policy: {policy_name}")

    def get_policy(self, policy_name: str) -> Optional[Policy]:
        """Get a policy by name."""
        return self._policies.get(policy_name)

    def list_policies(
        self, policy_type: Optional[PolicyType] = None, status: Optional[PolicyStatus] = None
    ) -> List[Policy]:
        """
        List policies with optional filters.

        Args:
            policy_type: Filter by policy type
            status: Filter by status

        Returns:
            List of matching policies
        """
        policies = list(self._policies.values())

        if policy_type:
            policies = [p for p in policies if p.policy_type == policy_type]

        if status:
            policies = [p for p in policies if p.status == status]

        return policies

    def create_policy_group(self, group_name: str, policy_names: List[str]):
        """
        Create a named group of policies.

        Args:
            group_name: Group name
            policy_names: List of policy names
        """
        self._policy_groups[group_name] = set(policy_names)
        logger.info(f"Created policy group '{group_name}' with {len(policy_names)} policies")

    def evaluate_policy(self, policy_name: str, context: Dict[str, Any]) -> PolicyEvaluation:
        """
        Evaluate a single policy.

        Args:
            policy_name: Policy name
            context: Evaluation context

        Returns:
            Policy evaluation result
        """
        policy = self.get_policy(policy_name)
        if not policy:
            raise ValueError(f"Policy not found: {policy_name}")

        if policy.status != PolicyStatus.ACTIVE:
            logger.info(f"Skipping inactive policy: {policy_name}")
            return PolicyEvaluation(
                policy_name=policy_name,
                passed=True,
                metadata={"reason": "policy_inactive"},
            )

        evaluation = policy.evaluate(context)
        self._evaluation_history.append(evaluation)

        return evaluation

    def evaluate_all(
        self, context: Dict[str, Any], policy_type: Optional[PolicyType] = None
    ) -> List[PolicyEvaluation]:
        """
        Evaluate all active policies.

        Args:
            context: Evaluation context
            policy_type: Optional filter by policy type

        Returns:
            List of evaluation results
        """
        policies = self.list_policies(policy_type=policy_type, status=PolicyStatus.ACTIVE)

        evaluations = []
        for policy in policies:
            evaluation = self.evaluate_policy(policy.name, context)
            evaluations.append(evaluation)

        return evaluations

    def evaluate_group(self, group_name: str, context: Dict[str, Any]) -> List[PolicyEvaluation]:
        """
        Evaluate a policy group.

        Args:
            group_name: Policy group name
            context: Evaluation context

        Returns:
            List of evaluation results
        """
        if group_name not in self._policy_groups:
            raise ValueError(f"Policy group not found: {group_name}")

        policy_names = self._policy_groups[group_name]
        evaluations = []

        for policy_name in policy_names:
            try:
                evaluation = self.evaluate_policy(policy_name, context)
                evaluations.append(evaluation)
            except ValueError:
                logger.warning(f"Policy not found in group: {policy_name}")

        return evaluations

    def get_violations(
        self,
        severity: Optional[PolicySeverity] = None,
        since: Optional[float] = None,
    ) -> List[PolicyEvaluation]:
        """
        Get policy violations from evaluation history.

        Args:
            severity: Filter by severity
            since: Filter by timestamp (unix timestamp)

        Returns:
            List of evaluations with violations
        """
        violations = [e for e in self._evaluation_history if not e.passed]

        if severity:
            violations = [
                v for v in violations if v.metadata.get("severity") == severity.value
            ]

        if since:
            violations = [v for v in violations if v.timestamp >= since]

        return violations

    def get_compliance_report(self) -> Dict[str, Any]:
        """
        Generate compliance report.

        Returns:
            Compliance summary
        """
        total_policies = len(self._policies)
        active_policies = len(self.list_policies(status=PolicyStatus.ACTIVE))

        total_evaluations = len(self._evaluation_history)
        passed = len([e for e in self._evaluation_history if e.passed])
        failed = total_evaluations - passed

        # Group by severity
        violations_by_severity = {}
        for evaluation in self._evaluation_history:
            if not evaluation.passed:
                severity = evaluation.metadata.get("severity", "unknown")
                violations_by_severity[severity] = violations_by_severity.get(severity, 0) + 1

        return {
            "total_policies": total_policies,
            "active_policies": active_policies,
            "total_evaluations": total_evaluations,
            "passed_evaluations": passed,
            "failed_evaluations": failed,
            "compliance_rate": (passed / total_evaluations * 100) if total_evaluations > 0 else 0,
            "violations_by_severity": violations_by_severity,
            "policy_groups": len(self._policy_groups),
        }

    def execute_policy_actions(self, evaluation: PolicyEvaluation) -> List[Dict[str, Any]]:
        """
        Execute actions for a policy violation.

        Args:
            evaluation: Policy evaluation with violations

        Returns:
            List of executed actions
        """
        if evaluation.passed:
            return []

        policy = self.get_policy(evaluation.policy_name)
        if not policy:
            return []

        executed_actions = []

        for action in policy.actions:
            try:
                result = self._execute_action(action, policy, evaluation)
                executed_actions.append(
                    {
                        "action": action,
                        "status": "success",
                        "result": result,
                        "timestamp": datetime.now().timestamp(),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to execute action '{action}': {e}")
                executed_actions.append(
                    {
                        "action": action,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now().timestamp(),
                    }
                )

        return executed_actions

    def _execute_action(
        self, action: str, policy: Policy, evaluation: PolicyEvaluation
    ) -> Dict[str, Any]:
        """Execute a single policy action."""
        # Action execution is delegated to specific implementations
        # This is a placeholder for the base implementation
        logger.info(f"Executing action '{action}' for policy '{policy.name}'")

        if action == "alert":
            return {"type": "alert", "message": f"Policy violation: {policy.name}"}
        elif action == "block":
            return {"type": "block", "message": "Resource creation/modification blocked"}
        elif action == "notify":
            return {"type": "notify", "message": "Notification sent"}

        return {"type": "unknown", "action": action}

    def clear_history(self):
        """Clear evaluation history."""
        self._evaluation_history.clear()

    def export_policies(self) -> List[Dict[str, Any]]:
        """
        Export all policies as dictionaries.

        Returns:
            List of policy configurations
        """
        return [
            {
                "name": p.name,
                "description": p.description,
                "type": p.policy_type.value,
                "severity": p.severity.value,
                "status": p.status.value,
                "scope": p.scope,
                "conditions": p.conditions,
                "actions": p.actions,
                "metadata": p.metadata,
            }
            for p in self._policies.values()
        ]

    def import_policies(self, policies_config: List[Dict[str, Any]]):
        """
        Import policies from configuration.

        Args:
            policies_config: List of policy configurations
        """
        for config in policies_config:
            try:
                policy = Policy(
                    name=config["name"],
                    description=config.get("description", ""),
                    policy_type=PolicyType(config["type"]),
                    severity=PolicySeverity(config.get("severity", "warning")),
                    status=PolicyStatus(config.get("status", "active")),
                    scope=config.get("scope", {}),
                    conditions=config.get("conditions", {}),
                    actions=config.get("actions", []),
                    metadata=config.get("metadata", {}),
                )
                self.add_policy(policy)
            except Exception as e:
                logger.error(f"Failed to import policy '{config.get('name')}': {e}")
