"""
Tests for Core Policy Engine
=============================

Test policy definition, evaluation, and enforcement.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.policy import (
    PolicyEngine,
    Policy,
    PolicyType,
    PolicySeverity,
    PolicyStatus,
    BudgetPolicy,
    CompliancePolicy,
    LifecyclePolicy,
    ViolationTracker,
)


@pytest.fixture
def policy_engine():
    """Create policy engine."""
    return PolicyEngine()


@pytest.fixture
def basic_policy():
    """Create basic policy."""
    return Policy(
        name="test_policy",
        description="Test policy",
        policy_type=PolicyType.CUSTOM,
        severity=PolicySeverity.WARNING,
        scope={"team": "platform"},
        conditions={"max_cost": 1000},
        actions=["alert", "notify"],
    )


class TestPolicyEngine:
    """Test PolicyEngine class."""

    def test_initialization(self, policy_engine):
        """Test engine initialization."""
        assert policy_engine is not None
        assert len(policy_engine._policies) == 0

    def test_add_policy(self, policy_engine, basic_policy):
        """Test adding a policy."""
        policy_engine.add_policy(basic_policy)

        assert basic_policy.name in policy_engine._policies
        assert policy_engine.get_policy(basic_policy.name) == basic_policy

    def test_remove_policy(self, policy_engine, basic_policy):
        """Test removing a policy."""
        policy_engine.add_policy(basic_policy)
        policy_engine.remove_policy(basic_policy.name)

        assert basic_policy.name not in policy_engine._policies

    def test_list_policies(self, policy_engine):
        """Test listing policies."""
        policy1 = Policy("policy1", "Description 1", PolicyType.BUDGET)
        policy2 = Policy("policy2", "Description 2", PolicyType.COMPLIANCE)

        policy_engine.add_policy(policy1)
        policy_engine.add_policy(policy2)

        all_policies = policy_engine.list_policies()
        assert len(all_policies) == 2

        budget_policies = policy_engine.list_policies(policy_type=PolicyType.BUDGET)
        assert len(budget_policies) == 1
        assert budget_policies[0].name == "policy1"

    def test_evaluate_policy(self, policy_engine, basic_policy):
        """Test evaluating a single policy."""
        policy_engine.add_policy(basic_policy)

        context = {"team": "platform", "current_cost": 500}
        evaluation = policy_engine.evaluate_policy(basic_policy.name, context)

        assert evaluation.policy_name == basic_policy.name
        assert isinstance(evaluation.passed, bool)

    def test_export_import_policies(self, policy_engine, basic_policy):
        """Test exporting and importing policies."""
        policy_engine.add_policy(basic_policy)

        # Export
        exported = policy_engine.export_policies()
        assert len(exported) == 1
        assert exported[0]["name"] == basic_policy.name

        # Clear and reimport
        policy_engine.remove_policy(basic_policy.name)
        policy_engine.import_policies(exported)

        assert basic_policy.name in policy_engine._policies


class TestBudgetPolicy:
    """Test BudgetPolicy class."""

    def test_budget_policy_creation(self):
        """Test creating budget policy."""
        policy = BudgetPolicy(
            name="team_budget",
            description="Team monthly budget",
            limit=10000,
            scope={"team": "platform"},
        )

        assert policy.name == "team_budget"
        assert policy.limit == 10000
        assert len(policy.thresholds) == 3  # Default thresholds

    def test_budget_evaluation(self):
        """Test budget threshold evaluation."""
        policy = BudgetPolicy(
            name="test_budget",
            limit=1000,
        )

        # Under budget
        context1 = {"current_spend": 500}
        evaluation1 = policy.evaluate(context1)
        assert evaluation1.passed is True

        # Over 90% threshold
        context2 = {"current_spend": 950}
        evaluation2 = policy.evaluate(context2)
        assert evaluation2.passed is False
        assert len(evaluation2.violations) > 0

    def test_forecast_budget(self):
        """Test budget forecasting."""
        policy = BudgetPolicy(name="test", limit=3000)

        forecast = policy.get_forecast(
            current_spend=1000,
            days_elapsed=10,
            days_total=30,
        )

        assert "forecast_spend" in forecast
        assert forecast["forecast_spend"] == 3000  # 100/day * 30 days


class TestCompliancePolicy:
    """Test CompliancePolicy class."""

    def test_compliance_policy_creation(self):
        """Test creating compliance policy."""
        from openfinops.policy.compliance_policy import create_soc2_policy

        policy = create_soc2_policy()

        assert policy.name == "soc2_compliance"
        assert len(policy.rules) > 0

    def test_compliance_evaluation(self):
        """Test compliance rule evaluation."""
        from openfinops.policy.compliance_policy import CompliancePolicy, ComplianceRule, RuleType

        policy = CompliancePolicy(
            name="test_compliance",
            rules=[
                ComplianceRule(
                    rule_id="encryption_rule",
                    rule_type=RuleType.ENCRYPTION_REQUIRED,
                    description="Encryption required",
                )
            ],
        )

        # Non-compliant resource
        context1 = {"resources": [{"id": "r-1", "encrypted": False}]}
        evaluation1 = policy.evaluate(context1)
        assert not evaluation1.passed

        # Compliant resource
        context2 = {"resources": [{"id": "r-2", "encrypted": True}]}
        evaluation2 = policy.evaluate(context2)
        assert evaluation2.passed


class TestLifecyclePolicy:
    """Test LifecyclePolicy class."""

    def test_lifecycle_policy_creation(self):
        """Test creating lifecycle policy."""
        from openfinops.policy.lifecycle_policy import create_idle_resource_policy

        policy = create_idle_resource_policy(resource_type="ec2")

        assert "idle_ec2" in policy.name
        assert policy.idle_config is not None

    def test_idle_detection(self):
        """Test idle resource detection."""
        from openfinops.policy.lifecycle_policy import LifecyclePolicy, IdleDetectionConfig
        import time

        policy = LifecyclePolicy(
            name="idle_detect",
            resource_types=["ec2"],
            idle_config=IdleDetectionConfig(
                cpu_threshold=5.0,
                duration_minutes=60,
            ),
        )

        # Idle resource - idle for 2 hours
        current_time = time.time()
        idle_since = current_time - (120 * 60)  # 2 hours ago

        idle_resource = {
            "id": "i-123",
            "type": "ec2",
            "metrics": {
                "cpu_usage": 2.0,
                "network_bytes_per_sec": 100,
                "memory_usage": 10.0,
                "idle_since": idle_since,
            },
        }

        context = {"resources": [idle_resource], "current_time": current_time}
        evaluation = policy.evaluate(context)

        assert not evaluation.passed  # Should detect idle
        assert len(evaluation.violations) > 0


class TestViolationTracker:
    """Test ViolationTracker class."""

    def test_create_violation(self):
        """Test creating a violation."""
        tracker = ViolationTracker()

        violation = tracker.create_violation(
            policy_name="test_policy",
            resource_id="r-123",
            violation_type="budget_exceeded",
            severity="error",
            description="Budget exceeded",
        )

        assert violation.id is not None
        assert violation.policy_name == "test_policy"
        assert violation.resource_id == "r-123"

    def test_list_violations(self):
        """Test listing violations."""
        from openfinops.policy import ViolationStatus

        tracker = ViolationTracker()

        tracker.create_violation("p1", "r1", "type1", "error", "desc1")
        tracker.create_violation("p2", "r2", "type2", "warning", "desc2")

        all_violations = tracker.list_violations()
        assert len(all_violations) == 2

        error_violations = tracker.list_violations(severity="error")
        assert len(error_violations) == 1

    def test_get_statistics(self):
        """Test violation statistics."""
        tracker = ViolationTracker()

        tracker.create_violation("p1", "r1", "t1", "error", "d1")
        tracker.create_violation("p1", "r2", "t1", "warning", "d2")

        stats = tracker.get_statistics()

        assert stats["total_violations"] == 2
        assert "by_severity" in stats
        assert "by_policy" in stats


# Run quick test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
