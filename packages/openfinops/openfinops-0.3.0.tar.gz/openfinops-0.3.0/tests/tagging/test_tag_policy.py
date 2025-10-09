"""
Tests for Tag Policy Engine
============================

Test tag policy enforcement.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.tagging import TagPolicy, TagPolicyViolation, PolicySeverity, PolicyEnforcer


@pytest.fixture
def basic_policy():
    """Create basic tag policy."""
    return TagPolicy(
        name="basic_required_tags",
        description="Basic required tags for all resources",
        required_tags=["environment", "team", "owner"],
        severity=PolicySeverity.ERROR,
    )


@pytest.fixture
def production_policy():
    """Create production-specific policy."""
    return TagPolicy(
        name="production_policy",
        description="Strict tags for production",
        required_tags=["environment", "team", "cost_center", "compliance"],
        tag_patterns={
            "environment": r"^(production|prod)$",
        },
        allowed_values={
            "compliance": ["pci", "hipaa", "sox", "none"],
        },
        severity=PolicySeverity.CRITICAL,
        applies_to={"environments": ["production", "prod"]},
    )


class TestTagPolicy:
    """Test TagPolicy class."""

    def test_initialization(self, basic_policy):
        """Test policy initialization."""
        assert basic_policy.name == "basic_required_tags"
        assert len(basic_policy.required_tags) == 3

    def test_validate_compliant_tags(self, basic_policy):
        """Test validation with compliant tags."""
        resource = {"id": "i-123", "type": "ec2"}
        tags = {"environment": "production", "team": "platform", "owner": "alice"}

        violations = basic_policy.validate(tags, resource)

        assert len(violations) == 0

    def test_validate_missing_required_tags(self, basic_policy):
        """Test detection of missing required tags."""
        resource = {"id": "i-123", "type": "ec2"}
        tags = {"environment": "production"}  # Missing team and owner

        violations = basic_policy.validate(tags, resource)

        assert len(violations) == 1
        violation = violations[0]
        assert violation.violation_type == "missing_required_tags"
        assert "team" in violation.missing_tags
        assert "owner" in violation.missing_tags

    def test_validate_invalid_pattern(self, production_policy):
        """Test validation of tag patterns."""
        resource = {"id": "i-123", "environment": "production"}
        tags = {
            "environment": "dev",  # Invalid for production policy pattern
            "team": "platform",
            "cost_center": "eng-001",
            "compliance": "none",
        }

        violations = production_policy.validate(tags, resource)

        # Should have violation for invalid environment pattern
        assert any(v.violation_type == "invalid_tag_value" for v in violations)

    def test_validate_disallowed_value(self, production_policy):
        """Test validation of allowed values."""
        resource = {"id": "i-123", "environment": "production"}
        tags = {
            "environment": "production",
            "team": "platform",
            "cost_center": "eng-001",
            "compliance": "invalid_value",  # Not in allowed list
        }

        violations = production_policy.validate(tags, resource)

        assert any(v.violation_type == "value_not_allowed" for v in violations)

    def test_policy_applies_to_resource_type(self):
        """Test policy application based on resource type."""
        policy = TagPolicy(
            name="ec2_policy",
            required_tags=["instance_type"],
            applies_to={"resource_types": ["ec2"]},
        )

        # Should apply to EC2
        ec2_resource = {"id": "i-123", "type": "ec2"}
        assert policy._applies_to_resource(ec2_resource)

        # Should not apply to RDS
        rds_resource = {"id": "db-456", "type": "rds"}
        assert not policy._applies_to_resource(rds_resource)

    def test_policy_applies_to_environment(self, production_policy):
        """Test policy application based on environment."""
        # Should apply to production
        prod_resource = {"id": "i-123", "environment": "production"}
        assert production_policy._applies_to_resource(prod_resource)

        # Should not apply to dev
        dev_resource = {"id": "i-456", "environment": "development"}
        assert not production_policy._applies_to_resource(dev_resource)

    def test_violation_has_remediation(self, basic_policy):
        """Test that violations include remediation advice."""
        resource = {"id": "i-123"}
        tags = {}

        violations = basic_policy.validate(tags, resource)

        assert len(violations) > 0
        assert violations[0].remediation is not None

    def test_severity_levels(self):
        """Test different severity levels."""
        severities = [
            PolicySeverity.INFO,
            PolicySeverity.WARNING,
            PolicySeverity.ERROR,
            PolicySeverity.CRITICAL,
        ]

        for severity in severities:
            policy = TagPolicy(
                name=f"test_{severity.value}",
                required_tags=["test"],
                severity=severity,
            )

            resource = {"id": "test"}
            violations = policy.validate({}, resource)

            assert len(violations) > 0
            assert violations[0].severity == severity


class TestPolicyEnforcer:
    """Test PolicyEnforcer class."""

    def test_add_policy(self, basic_policy):
        """Test adding a policy."""
        enforcer = PolicyEnforcer()
        enforcer.add_policy(basic_policy)

        assert basic_policy.name in enforcer._policies

    def test_enforce_all_compliant(self, basic_policy):
        """Test enforcement with all compliant resources."""
        enforcer = PolicyEnforcer()
        enforcer.add_policy(basic_policy)

        resources = [
            {
                "id": "i-123",
                "tags": {"environment": "prod", "team": "platform", "owner": "alice"},
            },
            {
                "id": "i-456",
                "tags": {"environment": "dev", "team": "data", "owner": "bob"},
            },
        ]

        result = enforcer.enforce(resources)

        assert result["status"] == "passed"
        assert result["total_violations"] == 0
        assert result["compliant_resources"] == 2
        assert result["compliance_rate"] == 100.0

    def test_enforce_with_violations(self, basic_policy):
        """Test enforcement with violations."""
        enforcer = PolicyEnforcer()
        enforcer.add_policy(basic_policy)

        resources = [
            {
                "id": "i-123",
                "tags": {"environment": "prod", "team": "platform", "owner": "alice"},
            },
            {"id": "i-456", "tags": {"environment": "dev"}},  # Missing tags
        ]

        result = enforcer.enforce(resources)

        assert result["status"] == "failed"
        assert result["total_violations"] > 0
        assert result["compliant_resources"] == 1
        assert result["non_compliant_resources"] == 1
        assert result["compliance_rate"] == 50.0

    def test_enforce_stop_on_critical(self, production_policy):
        """Test stopping enforcement on critical violation."""
        enforcer = PolicyEnforcer()
        enforcer.add_policy(production_policy)

        resources = [
            {"id": "i-123", "environment": "production", "tags": {}},  # Critical violation
            {"id": "i-456", "tags": {}},
        ]

        result = enforcer.enforce(resources, stop_on_critical=True)

        assert result.get("stopped_on_critical") is True

    def test_remove_policy(self, basic_policy):
        """Test removing a policy."""
        enforcer = PolicyEnforcer()
        enforcer.add_policy(basic_policy)
        enforcer.remove_policy(basic_policy.name)

        assert basic_policy.name not in enforcer._policies

    def test_get_policy_summary(self, basic_policy):
        """Test getting policy summary."""
        enforcer = PolicyEnforcer()
        enforcer.add_policy(basic_policy)

        summary = enforcer.get_policy_summary()

        assert summary["total_policies"] == 1
        assert len(summary["policies"]) == 1
        assert summary["policies"][0]["name"] == basic_policy.name

    def test_violations_grouped_by_severity(self, basic_policy):
        """Test that violations are grouped by severity."""
        enforcer = PolicyEnforcer()
        enforcer.add_policy(basic_policy)

        resources = [
            {"id": "i-123", "tags": {}},
            {"id": "i-456", "tags": {}},
        ]

        result = enforcer.enforce(resources)

        assert "violations_by_severity" in result
        assert "error" in result["violations_by_severity"]


class TestViolationDataclass:
    """Test TagPolicyViolation dataclass."""

    def test_violation_creation(self):
        """Test creating a policy violation."""
        violation = TagPolicyViolation(
            resource_id="i-123",
            policy_name="test_policy",
            severity=PolicySeverity.ERROR,
            violation_type="missing_required_tags",
            message="Missing tags",
            missing_tags=["environment", "team"],
        )

        assert violation.resource_id == "i-123"
        assert violation.severity == PolicySeverity.ERROR
        assert len(violation.missing_tags) == 2


class TestIntegration:
    """Integration tests."""

    def test_multi_policy_enforcement(self, basic_policy, production_policy):
        """Test enforcing multiple policies."""
        enforcer = PolicyEnforcer()
        enforcer.add_policy(basic_policy)
        enforcer.add_policy(production_policy)

        resources = [
            {
                "id": "i-123",
                "environment": "production",
                "tags": {"environment": "production"},  # Missing many tags
            }
        ]

        result = enforcer.enforce(resources)

        # Should have violations from both policies
        assert result["total_violations"] >= 2
