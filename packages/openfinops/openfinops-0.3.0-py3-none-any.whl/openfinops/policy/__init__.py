"""
Policy Engine & Governance
===========================

Comprehensive policy engine for FinOps governance, compliance, and cost control.

This module provides:
- Policy definition and management
- Budget policy enforcement
- Compliance and security policies
- Resource lifecycle policies
- Policy violation tracking and remediation
- Policy as code (YAML/JSON)

Example:
    >>> from openfinops.policy import PolicyEngine, BudgetPolicy
    >>>
    >>> engine = PolicyEngine()
    >>>
    >>> # Define budget policy
    >>> policy = BudgetPolicy(
    ...     name="monthly_budget",
    ...     limit=10000,
    ...     scope={"team": "platform"},
    ...     actions=["alert", "block"]
    ... )
    >>> engine.add_policy(policy)
    >>>
    >>> # Evaluate spending
    >>> violations = engine.evaluate_spending(current_spend=12000, scope={"team": "platform"})
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .policy_engine import PolicyEngine, Policy, PolicyType, PolicySeverity, PolicyStatus
from .budget_policy import BudgetPolicy, BudgetViolation, BudgetThreshold
from .compliance_policy import CompliancePolicy, ComplianceRule, ComplianceViolation
from .lifecycle_policy import LifecyclePolicy, LifecycleAction, ResourceState
from .violation_tracker import ViolationTracker, Violation, ViolationStatus, Remediation

__all__ = [
    # Core engine
    "PolicyEngine",
    "Policy",
    "PolicyType",
    "PolicySeverity",
    "PolicyStatus",
    # Budget policies
    "BudgetPolicy",
    "BudgetViolation",
    "BudgetThreshold",
    # Compliance policies
    "CompliancePolicy",
    "ComplianceRule",
    "ComplianceViolation",
    # Lifecycle policies
    "LifecyclePolicy",
    "LifecycleAction",
    "ResourceState",
    # Violation tracking
    "ViolationTracker",
    "Violation",
    "ViolationStatus",
    "Remediation",
]
