"""
Compliance Policy System
========================

Compliance policies for regulatory requirements and security standards.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import logging

from .policy_engine import Policy, PolicyType, PolicySeverity

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Standard compliance frameworks."""

    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST = "nist"
    CIS = "cis"
    CUSTOM = "custom"


class RuleType(Enum):
    """Types of compliance rules."""

    TAG_REQUIRED = "tag_required"
    ENCRYPTION_REQUIRED = "encryption_required"
    REGION_RESTRICTION = "region_restriction"
    RETENTION_POLICY = "retention_policy"
    ACCESS_CONTROL = "access_control"
    AUDIT_LOGGING = "audit_logging"
    BACKUP_REQUIRED = "backup_required"
    NETWORK_SECURITY = "network_security"
    CUSTOM = "custom"


@dataclass
class ComplianceRule:
    """
    Individual compliance rule.

    Attributes:
        rule_id: Unique rule identifier
        rule_type: Type of rule
        description: Rule description
        required: Whether rule is required
        checker: Function to check compliance
        remediation: Remediation guidance
    """

    rule_id: str
    rule_type: RuleType
    description: str
    required: bool = True
    checker: Optional[callable] = None
    remediation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def check(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check rule compliance.

        Args:
            resource: Resource to check

        Returns:
            Check result with compliant status and details
        """
        if self.checker:
            try:
                result = self.checker(resource, self.metadata)
                return {
                    "rule_id": self.rule_id,
                    "compliant": result.get("compliant", False),
                    "details": result.get("details", ""),
                    "remediation": self.remediation,
                }
            except Exception as e:
                logger.error(f"Rule check failed for {self.rule_id}: {e}")
                return {
                    "rule_id": self.rule_id,
                    "compliant": False,
                    "details": f"Check failed: {str(e)}",
                    "remediation": self.remediation,
                }

        # Default checks based on rule type
        return self._default_check(resource)

    def _default_check(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Default compliance checks."""
        if self.rule_type == RuleType.TAG_REQUIRED:
            required_tags = self.metadata.get("required_tags", [])
            tags = resource.get("tags", {})
            missing = [tag for tag in required_tags if tag not in tags]

            return {
                "rule_id": self.rule_id,
                "compliant": len(missing) == 0,
                "details": f"Missing tags: {missing}" if missing else "All tags present",
                "remediation": self.remediation or f"Add missing tags: {', '.join(missing)}",
            }

        elif self.rule_type == RuleType.ENCRYPTION_REQUIRED:
            encrypted = resource.get("encrypted", False)
            return {
                "rule_id": self.rule_id,
                "compliant": encrypted,
                "details": "Encryption enabled" if encrypted else "Encryption not enabled",
                "remediation": self.remediation or "Enable encryption at rest",
            }

        elif self.rule_type == RuleType.REGION_RESTRICTION:
            allowed_regions = self.metadata.get("allowed_regions", [])
            resource_region = resource.get("region", "")

            compliant = resource_region in allowed_regions if allowed_regions else True

            return {
                "rule_id": self.rule_id,
                "compliant": compliant,
                "details": (
                    f"Resource in {'allowed' if compliant else 'restricted'} region: {resource_region}"
                ),
                "remediation": (
                    self.remediation or f"Move to allowed regions: {', '.join(allowed_regions)}"
                ),
            }

        # Default: compliant if no specific check
        return {
            "rule_id": self.rule_id,
            "compliant": True,
            "details": "No specific check implemented",
            "remediation": self.remediation,
        }


@dataclass
class ComplianceViolation:
    """
    Compliance violation details.

    Attributes:
        resource_id: Resource with violation
        rule_id: Rule that was violated
        framework: Compliance framework
        description: Violation description
        severity: Violation severity
        remediation: Remediation steps
        timestamp: Violation timestamp
    """

    resource_id: str
    rule_id: str
    framework: str
    description: str
    severity: PolicySeverity
    remediation: str
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


class CompliancePolicy(Policy):
    """
    Compliance policy for regulatory requirements.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        framework: ComplianceFramework = ComplianceFramework.CUSTOM,
        rules: Optional[List[ComplianceRule]] = None,
        scope: Optional[Dict[str, Any]] = None,
        severity: PolicySeverity = PolicySeverity.CRITICAL,
        actions: Optional[List[str]] = None,
    ):
        """
        Initialize compliance policy.

        Args:
            name: Policy name
            description: Policy description
            framework: Compliance framework
            rules: List of compliance rules
            scope: Policy scope
            severity: Default severity
            actions: Actions on violation
        """
        super().__init__(
            name=name,
            description=description,
            policy_type=PolicyType.COMPLIANCE,
            severity=severity,
            scope=scope or {},
            actions=actions or ["alert", "notify", "block"],
        )

        self.framework = framework
        self.rules = rules or []

    def add_rule(self, rule: ComplianceRule):
        """Add a compliance rule."""
        self.rules.append(rule)
        logger.info(f"Added rule {rule.rule_id} to policy {self.name}")

    def _evaluate_conditions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate compliance rules."""
        resources = context.get("resources", [])
        if not isinstance(resources, list):
            resources = [resources]

        violations = []

        for resource in resources:
            resource_id = resource.get("id", "unknown")

            for rule in self.rules:
                result = rule.check(resource)

                if not result["compliant"]:
                    violations.append(
                        {
                            "type": "compliance_violation",
                            "resource_id": resource_id,
                            "rule_id": rule.rule_id,
                            "rule_type": rule.rule_type.value,
                            "framework": self.framework.value,
                            "description": result["details"],
                            "remediation": result["remediation"],
                            "required": rule.required,
                        }
                    )

        return violations

    def get_compliance_score(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate compliance score.

        Args:
            resources: Resources to evaluate

        Returns:
            Compliance score and details
        """
        if not self.rules:
            return {"score": 100.0, "compliant": True}

        total_checks = 0
        passed_checks = 0

        for resource in resources:
            for rule in self.rules:
                result = rule.check(resource)
                total_checks += 1
                if result["compliant"]:
                    passed_checks += 1

        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        return {
            "score": score,
            "compliant": score == 100.0,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "framework": self.framework.value,
        }


# Pre-defined compliance policies
def create_soc2_policy() -> CompliancePolicy:
    """Create SOC2 compliance policy."""
    policy = CompliancePolicy(
        name="soc2_compliance",
        description="SOC2 compliance requirements",
        framework=ComplianceFramework.SOC2,
        severity=PolicySeverity.CRITICAL,
    )

    # Required tags for audit trail
    policy.add_rule(
        ComplianceRule(
            rule_id="soc2_required_tags",
            rule_type=RuleType.TAG_REQUIRED,
            description="Resources must have audit tags",
            required=True,
            metadata={"required_tags": ["owner", "environment", "cost_center", "data_classification"]},
            remediation="Add required tags for audit compliance",
        )
    )

    # Encryption at rest
    policy.add_rule(
        ComplianceRule(
            rule_id="soc2_encryption",
            rule_type=RuleType.ENCRYPTION_REQUIRED,
            description="Data must be encrypted at rest",
            required=True,
            remediation="Enable encryption at rest for all storage resources",
        )
    )

    # Audit logging
    policy.add_rule(
        ComplianceRule(
            rule_id="soc2_audit_logging",
            rule_type=RuleType.AUDIT_LOGGING,
            description="Audit logging must be enabled",
            required=True,
            remediation="Enable comprehensive audit logging",
        )
    )

    return policy


def create_hipaa_policy() -> CompliancePolicy:
    """Create HIPAA compliance policy."""
    policy = CompliancePolicy(
        name="hipaa_compliance",
        description="HIPAA compliance for healthcare data",
        framework=ComplianceFramework.HIPAA,
        severity=PolicySeverity.CRITICAL,
    )

    # PHI data classification
    policy.add_rule(
        ComplianceRule(
            rule_id="hipaa_phi_classification",
            rule_type=RuleType.TAG_REQUIRED,
            description="PHI resources must be classified",
            required=True,
            metadata={"required_tags": ["data_classification", "phi_indicator", "retention_period"]},
            remediation="Tag resources containing PHI with proper classification",
        )
    )

    # Encryption required
    policy.add_rule(
        ComplianceRule(
            rule_id="hipaa_encryption",
            rule_type=RuleType.ENCRYPTION_REQUIRED,
            description="PHI must be encrypted",
            required=True,
            remediation="Enable encryption for all PHI data stores",
        )
    )

    # Region restriction
    policy.add_rule(
        ComplianceRule(
            rule_id="hipaa_region",
            rule_type=RuleType.REGION_RESTRICTION,
            description="PHI must remain in approved regions",
            required=True,
            metadata={"allowed_regions": ["us-east-1", "us-west-2"]},
            remediation="Move PHI resources to approved US regions",
        )
    )

    return policy


def create_pci_dss_policy() -> CompliancePolicy:
    """Create PCI-DSS compliance policy."""
    policy = CompliancePolicy(
        name="pci_dss_compliance",
        description="PCI-DSS compliance for payment card data",
        framework=ComplianceFramework.PCI_DSS,
        severity=PolicySeverity.CRITICAL,
    )

    # Cardholder data classification
    policy.add_rule(
        ComplianceRule(
            rule_id="pci_chd_classification",
            rule_type=RuleType.TAG_REQUIRED,
            description="Cardholder data must be classified",
            required=True,
            metadata={"required_tags": ["pci_scope", "cardholder_data", "compliance_level"]},
            remediation="Tag all systems handling cardholder data",
        )
    )

    # Encryption
    policy.add_rule(
        ComplianceRule(
            rule_id="pci_encryption",
            rule_type=RuleType.ENCRYPTION_REQUIRED,
            description="Cardholder data must be encrypted",
            required=True,
            remediation="Enable strong encryption (AES-256) for cardholder data",
        )
    )

    # Network security
    policy.add_rule(
        ComplianceRule(
            rule_id="pci_network_security",
            rule_type=RuleType.NETWORK_SECURITY,
            description="Network segmentation required",
            required=True,
            remediation="Implement network segmentation for PCI environment",
        )
    )

    return policy


PREDEFINED_POLICIES = {
    "soc2": create_soc2_policy,
    "hipaa": create_hipaa_policy,
    "pci_dss": create_pci_dss_policy,
}
