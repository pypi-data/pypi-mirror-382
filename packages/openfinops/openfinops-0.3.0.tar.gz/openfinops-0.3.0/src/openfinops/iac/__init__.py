"""
FinOps-as-Code (Infrastructure as Code)
=========================================

Manage OpenFinOps resources as code with Terraform integration.

This module provides:
- Provider configuration
- Resource definitions (budgets, policies, alerts, dashboards)
- Terraform HCL generation
- API client for resource management
- Infrastructure validation and planning

Example:
    >>> from openfinops.iac import create_provider, budget, policy, generate_terraform
    >>>
    >>> # Create provider
    >>> provider = create_provider(
    ...     endpoint="https://api.openfinops.io",
    ...     api_key="your-api-key"
    ... )
    >>>
    >>> # Define resources
    >>> budget("prod_budget", amount=10000, period="monthly", provider=provider)
    >>> policy("tag_policy", policy_type="tagging", rules=[...], provider=provider)
    >>>
    >>> # Apply changes
    >>> result = provider.apply()
    >>>
    >>> # Or generate Terraform
    >>> hcl = generate_terraform(
    ...     provider.config.to_terraform(),
    ...     provider.list_resources().values()
    ... )
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .provider import OpenFinOpsProvider, ProviderConfig, create_provider
from .resources import (
    Resource,
    ResourceState,
    BudgetResource,
    PolicyResource,
    AlertResource,
    DashboardResource,
    budget,
    policy,
    alert,
    dashboard,
)
from .terraform_generator import (
    TerraformGenerator,
    generate_terraform,
    generate_module,
    save_module,
)
from .client import OpenFinOpsClient, create_client

__all__ = [
    # Provider
    "OpenFinOpsProvider",
    "ProviderConfig",
    "create_provider",
    # Resources
    "Resource",
    "ResourceState",
    "BudgetResource",
    "PolicyResource",
    "AlertResource",
    "DashboardResource",
    "budget",
    "policy",
    "alert",
    "dashboard",
    # Terraform
    "TerraformGenerator",
    "generate_terraform",
    "generate_module",
    "save_module",
    # Client
    "OpenFinOpsClient",
    "create_client",
]
