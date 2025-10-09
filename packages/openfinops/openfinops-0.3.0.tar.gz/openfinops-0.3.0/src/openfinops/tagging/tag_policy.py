"""
Tag Policy Engine
=================

Define and enforce tagging policies for compliance and governance.

Provides:
- Required tag enforcement
- Tag value validation (regex patterns, allowed values)
- Custom validation rules
- Policy violation reporting
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class PolicySeverity(Enum):
    """Severity levels for policy violations."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TagPolicyViolation:
    """
    Represents a tag policy violation.

    Attributes:
        resource_id: ID of the resource with violation
        policy_name: Name of violated policy
        severity: Violation severity
        violation_type: Type of violation
        message: Human-readable description
        missing_tags: Tags that are missing
        invalid_tags: Tags with invalid values
        remediation: Suggested fix
    """

    resource_id: str
    policy_name: str
    severity: PolicySeverity
    violation_type: str
    message: str
    missing_tags: List[str] = field(default_factory=list)
    invalid_tags: Dict[str, str] = field(default_factory=dict)
    remediation: Optional[str] = None


class TagPolicy:
    """
    Tag policy definition and enforcement.

    Enforces tagging standards for compliance and governance.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        required_tags: Optional[List[str]] = None,
        tag_patterns: Optional[Dict[str, str]] = None,
        allowed_values: Optional[Dict[str, List[str]]] = None,
        severity: PolicySeverity = PolicySeverity.ERROR,
        applies_to: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize tag policy.

        Args:
            name: Policy name
            description: Policy description
            required_tags: List of required tag keys
            tag_patterns: Dict of tag_key: regex_pattern for validation
            allowed_values: Dict of tag_key: [allowed_values]
            severity: Default severity for violations
            applies_to: Criteria for which resources this policy applies to
        """
        self.name = name
        self.description = description
        self.required_tags = required_tags or []
        self.tag_patterns = {
            key: re.compile(pattern) for key, pattern in (tag_patterns or {}).items()
        }
        self.allowed_values = allowed_values or {}
        self.severity = severity
        self.applies_to = applies_to or {}
        self._custom_validators: List[Callable] = []

    def validate(
        self, tags: Dict[str, str], resource: Dict[str, Any]
    ) -> List[TagPolicyViolation]:
        """
        Validate tags against this policy.

        Args:
            tags: Resource tags to validate
            resource: Resource dictionary

        Returns:
            List of policy violations
        """
        violations = []

        # Check if policy applies to this resource
        if not self._applies_to_resource(resource):
            return violations

        # Check required tags
        missing_tags = [tag for tag in self.required_tags if tag not in tags or not tags[tag]]

        if missing_tags:
            violations.append(
                TagPolicyViolation(
                    resource_id=resource.get("id", "unknown"),
                    policy_name=self.name,
                    severity=self.severity,
                    violation_type="missing_required_tags",
                    message=f"Missing required tags: {', '.join(missing_tags)}",
                    missing_tags=missing_tags,
                    remediation=f"Add the following tags: {', '.join(missing_tags)}",
                )
            )

        # Validate tag patterns
        invalid_tags = {}
        for tag_key, pattern in self.tag_patterns.items():
            if tag_key in tags:
                if not pattern.match(tags[tag_key]):
                    invalid_tags[tag_key] = tags[tag_key]

        if invalid_tags:
            violations.append(
                TagPolicyViolation(
                    resource_id=resource.get("id", "unknown"),
                    policy_name=self.name,
                    severity=self.severity,
                    violation_type="invalid_tag_value",
                    message=f"Invalid tag values: {', '.join(invalid_tags.keys())}",
                    invalid_tags=invalid_tags,
                    remediation="Update tag values to match required patterns",
                )
            )

        # Validate allowed values
        for tag_key, allowed in self.allowed_values.items():
            if tag_key in tags:
                if tags[tag_key] not in allowed:
                    violations.append(
                        TagPolicyViolation(
                            resource_id=resource.get("id", "unknown"),
                            policy_name=self.name,
                            severity=self.severity,
                            violation_type="value_not_allowed",
                            message=(
                                f"Tag '{tag_key}' has value '{tags[tag_key]}' "
                                f"which is not in allowed list: {allowed}"
                            ),
                            invalid_tags={tag_key: tags[tag_key]},
                            remediation=f"Use one of: {', '.join(allowed)}",
                        )
                    )

        # Run custom validators
        for validator in self._custom_validators:
            custom_violations = validator(tags, resource, self)
            violations.extend(custom_violations)

        return violations

    def _applies_to_resource(self, resource: Dict[str, Any]) -> bool:
        """Check if policy applies to this resource."""
        if not self.applies_to:
            return True  # Applies to all resources

        # Check resource type
        if "resource_types" in self.applies_to:
            resource_type = resource.get("type", "")
            if resource_type not in self.applies_to["resource_types"]:
                return False

        # Check tags (policy applies only if resource has certain tags)
        if "has_tags" in self.applies_to:
            resource_tags = resource.get("tags", {})
            required_tags = self.applies_to["has_tags"]

            for key, value in required_tags.items():
                if resource_tags.get(key) != value:
                    return False

        # Check environment
        if "environments" in self.applies_to:
            resource_env = resource.get("environment") or resource.get("tags", {}).get(
                "environment"
            )
            if resource_env not in self.applies_to["environments"]:
                return False

        return True

    def add_custom_validator(
        self, validator: Callable[[Dict[str, str], Dict[str, Any], "TagPolicy"], List[TagPolicyViolation]]
    ):
        """
        Add a custom validation function.

        Args:
            validator: Function that takes (tags, resource, policy) and returns violations
        """
        self._custom_validators.append(validator)


class PolicyEnforcer:
    """
    Enforces multiple tag policies across resources.
    """

    def __init__(self):
        """Initialize policy enforcer."""
        self._policies: Dict[str, TagPolicy] = {}

    def add_policy(self, policy: TagPolicy):
        """
        Add a policy to enforce.

        Args:
            policy: TagPolicy instance
        """
        self._policies[policy.name] = policy
        logger.info(f"Added policy: {policy.name}")

    def remove_policy(self, policy_name: str):
        """Remove a policy."""
        if policy_name in self._policies:
            del self._policies[policy_name]

    def enforce(
        self, resources: List[Dict[str, Any]], stop_on_critical: bool = False
    ) -> Dict[str, Any]:
        """
        Enforce all policies on resources.

        Args:
            resources: List of resources to check
            stop_on_critical: Stop enforcement on first critical violation

        Returns:
            Dictionary with enforcement results
        """
        all_violations = []

        for resource in resources:
            resource_id = resource.get("id", "unknown")
            tags = resource.get("tags", {})

            for policy in self._policies.values():
                violations = policy.validate(tags, resource)

                for violation in violations:
                    all_violations.append(violation)

                    if stop_on_critical and violation.severity == PolicySeverity.CRITICAL:
                        return {
                            "status": "failed",
                            "violations": all_violations,
                            "compliant_resources": 0,
                            "non_compliant_resources": len(resources),
                            "stopped_on_critical": True,
                        }

        # Calculate compliance
        resources_with_violations = len(
            set(v.resource_id for v in all_violations)
        )
        compliant = len(resources) - resources_with_violations

        # Group violations by severity
        by_severity = {}
        for violation in all_violations:
            severity = violation.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "status": "passed" if not all_violations else "failed",
            "total_resources": len(resources),
            "compliant_resources": compliant,
            "non_compliant_resources": resources_with_violations,
            "compliance_rate": (compliant / len(resources)) * 100 if resources else 0,
            "total_violations": len(all_violations),
            "violations_by_severity": by_severity,
            "violations": all_violations,
        }

    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of all policies."""
        return {
            "total_policies": len(self._policies),
            "policies": [
                {
                    "name": policy.name,
                    "description": policy.description,
                    "required_tags": policy.required_tags,
                    "severity": policy.severity.value,
                }
                for policy in self._policies.values()
            ],
        }


# Pre-defined common policies
COMMON_POLICIES = {
    "production_required_tags": TagPolicy(
        name="production_required_tags",
        description="Required tags for production resources",
        required_tags=["environment", "team", "cost_center", "owner"],
        tag_patterns={
            "environment": r"^(production|prod)$",
        },
        severity=PolicySeverity.ERROR,
        applies_to={"environments": ["production", "prod"]},
    ),
    "cost_allocation_tags": TagPolicy(
        name="cost_allocation_tags",
        description="Tags required for cost allocation",
        required_tags=["cost_center", "project", "team"],
        severity=PolicySeverity.ERROR,
    ),
    "security_tags": TagPolicy(
        name="security_tags",
        description="Security-related tagging requirements",
        required_tags=["data_classification", "compliance"],
        allowed_values={
            "data_classification": ["public", "internal", "confidential", "restricted"],
            "compliance": ["pci", "hipaa", "sox", "none"],
        },
        severity=PolicySeverity.CRITICAL,
    ),
}
