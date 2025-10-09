"""
Tests for FinOps-as-Code System
=================================

Test infrastructure as code provider, resources, and Terraform generation.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.iac import (
    create_provider,
    ProviderConfig,
    budget,
    policy,
    alert,
    dashboard,
    BudgetResource,
    PolicyResource,
    AlertResource,
    DashboardResource,
    ResourceState,
    generate_terraform,
    TerraformGenerator,
    OpenFinOpsClient,
)


@pytest.fixture
def provider_config():
    """Create provider configuration."""
    return ProviderConfig(
        endpoint="https://api.openfinops.io",
        api_key="test-api-key",
        org_id="test-org",
    )


@pytest.fixture
def provider(provider_config):
    """Create OpenFinOps provider."""
    return create_provider(
        endpoint=provider_config.endpoint,
        api_key=provider_config.api_key,
        org_id=provider_config.org_id,
    )


class TestProviderConfig:
    """Test ProviderConfig class."""

    def test_config_initialization(self, provider_config):
        """Test provider config initialization."""
        assert provider_config.endpoint == "https://api.openfinops.io"
        assert provider_config.api_key == "test-api-key"
        assert provider_config.org_id == "test-org"

    def test_config_to_terraform(self, provider_config):
        """Test converting config to Terraform format."""
        tf_config = provider_config.to_terraform()

        assert tf_config["endpoint"] == provider_config.endpoint
        assert tf_config["api_key"] == provider_config.api_key
        assert tf_config["org_id"] == provider_config.org_id


class TestOpenFinOpsProvider:
    """Test OpenFinOpsProvider class."""

    def test_provider_initialization(self, provider):
        """Test provider initialization."""
        assert provider is not None
        assert provider.is_initialized()

    def test_register_resource(self, provider):
        """Test registering a resource."""
        resource = budget("test_budget", amount=1000, provider=provider)

        registered = provider.get_resource("budget", "test_budget")
        assert registered is resource

    def test_list_resources(self, provider):
        """Test listing resources."""
        budget("budget1", amount=1000, provider=provider)
        budget("budget2", amount=2000, provider=provider)
        policy("policy1", policy_type="budget", rules=[], provider=provider)

        all_resources = provider.list_resources()
        assert len(all_resources) == 3

        budgets = provider.list_resources("budget")
        assert len(budgets) == 2

    def test_validate(self, provider):
        """Test provider validation."""
        budget("valid_budget", amount=1000, provider=provider)

        result = provider.validate()

        assert result["valid"] is True
        assert result["resource_count"] == 1

    def test_plan(self, provider):
        """Test plan generation."""
        budget("budget1", amount=1000, provider=provider)
        policy("policy1", policy_type="budget", rules=[], provider=provider)

        plan = provider.plan()

        assert len(plan["create"]) == 2
        assert len(plan["update"]) == 0
        assert len(plan["delete"]) == 0

    def test_apply(self, provider):
        """Test applying changes."""
        budget("budget1", amount=1000, provider=provider)
        policy("policy1", policy_type="budget", rules=[{}], provider=provider)

        result = provider.apply(auto_approve=True)

        assert len(result["created"]) == 2
        assert len(result["failed"]) == 0


class TestBudgetResource:
    """Test BudgetResource class."""

    def test_budget_creation(self):
        """Test creating a budget resource."""
        resource = budget(name="test_budget", amount=5000, period="monthly")

        assert resource.name == "test_budget"
        assert resource.amount == 5000
        assert resource.period == "monthly"
        assert resource.state == ResourceState.PENDING

    def test_budget_validation(self):
        """Test budget validation."""
        valid_budget = budget(name="valid", amount=1000)
        result = valid_budget.validate()
        assert result["valid"] is True

        invalid_budget = budget(name="invalid", amount=-100)
        result = invalid_budget.validate()
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_budget_create(self):
        """Test budget create operation."""
        resource = budget(name="test", amount=1000)
        resource_id = resource.create()

        assert resource_id is not None
        assert resource.resource_id == resource_id
        assert resource.state == ResourceState.ACTIVE

    def test_budget_read(self):
        """Test budget read operation."""
        resource = budget(name="test", amount=1000, period="monthly")
        data = resource.read()

        assert data["name"] == "test"
        assert data["amount"] == 1000
        assert data["period"] == "monthly"

    def test_budget_update(self):
        """Test budget update operation."""
        resource = budget(name="test", amount=1000)
        resource.create()

        success = resource.update(amount=2000)

        assert success is True
        assert resource.amount == 2000
        assert resource.state == ResourceState.ACTIVE

    def test_budget_delete(self):
        """Test budget delete operation."""
        resource = budget(name="test", amount=1000)
        resource.create()

        success = resource.delete()

        assert success is True
        assert resource.state == ResourceState.DELETED

    def test_budget_to_terraform(self):
        """Test converting budget to Terraform format."""
        resource = budget(
            name="terraform_budget",
            amount=5000,
            period="monthly",
            filters={"team": "engineering"},
        )

        tf_config = resource.to_terraform()

        assert "resource" in tf_config
        assert "openfinops_budget" in tf_config["resource"]
        assert "terraform_budget" in tf_config["resource"]["openfinops_budget"]
        assert tf_config["resource"]["openfinops_budget"]["terraform_budget"]["amount"] == 5000


class TestPolicyResource:
    """Test PolicyResource class."""

    def test_policy_creation(self):
        """Test creating a policy resource."""
        resource = policy(
            name="test_policy",
            policy_type="compliance",
            rules=[{"check": "encryption_enabled"}],
        )

        assert resource.name == "test_policy"
        assert resource.policy_type == "compliance"
        assert len(resource.rules) == 1
        assert resource.state == ResourceState.PENDING

    def test_policy_validation(self):
        """Test policy validation."""
        valid_policy = policy(
            name="valid", policy_type="budget", rules=[{"threshold": 100}]
        )
        result = valid_policy.validate()
        assert result["valid"] is True

        invalid_policy = policy(name="invalid", policy_type="invalid_type", rules=[])
        result = invalid_policy.validate()
        assert result["valid"] is False

    def test_policy_crud_operations(self):
        """Test policy CRUD operations."""
        resource = policy(name="test", policy_type="budget", rules=[{}])

        # Create
        resource_id = resource.create()
        assert resource_id is not None
        assert resource.state == ResourceState.ACTIVE

        # Read
        data = resource.read()
        assert data["name"] == "test"
        assert data["policy_type"] == "budget"

        # Update
        success = resource.update(severity="critical")
        assert success is True
        assert resource.severity == "critical"

        # Delete
        success = resource.delete()
        assert success is True
        assert resource.state == ResourceState.DELETED


class TestAlertResource:
    """Test AlertResource class."""

    def test_alert_creation(self):
        """Test creating an alert resource."""
        resource = alert(
            name="test_alert",
            condition={"metric": "cost"},
            threshold=1000,
            notification_channels=["email"],
        )

        assert resource.name == "test_alert"
        assert resource.threshold == 1000
        assert "email" in resource.notification_channels

    def test_alert_validation(self):
        """Test alert validation."""
        valid_alert = alert(
            name="valid",
            condition={"metric": "cost"},
            threshold=100,
            notification_channels=["email"],
        )
        result = valid_alert.validate()
        assert result["valid"] is True

        invalid_alert = alert(
            name="invalid",
            condition={},
            threshold=100,
            notification_channels=[],
        )
        result = invalid_alert.validate()
        assert result["valid"] is False

    def test_alert_crud_operations(self):
        """Test alert CRUD operations."""
        resource = alert(
            name="test",
            condition={"metric": "cost"},
            threshold=500,
            notification_channels=["email"],
        )

        # Create
        resource_id = resource.create()
        assert resource_id is not None

        # Read
        data = resource.read()
        assert data["threshold"] == 500

        # Update
        success = resource.update(threshold=1000)
        assert success is True
        assert resource.threshold == 1000

        # Delete
        success = resource.delete()
        assert success is True


class TestDashboardResource:
    """Test DashboardResource class."""

    def test_dashboard_creation(self):
        """Test creating a dashboard resource."""
        widgets = [{"type": "chart", "title": "Cost Trend"}]
        resource = dashboard(name="test_dashboard", widgets=widgets)

        assert resource.name == "test_dashboard"
        assert len(resource.widgets) == 1

    def test_dashboard_validation(self):
        """Test dashboard validation."""
        valid_dashboard = dashboard(name="valid", widgets=[{"type": "chart"}])
        result = valid_dashboard.validate()
        assert result["valid"] is True

        invalid_dashboard = dashboard(name="invalid", widgets=[])
        result = invalid_dashboard.validate()
        assert result["valid"] is False

    def test_dashboard_crud_operations(self):
        """Test dashboard CRUD operations."""
        resource = dashboard(name="test", widgets=[{"type": "chart"}])

        # Create
        resource_id = resource.create()
        assert resource_id is not None

        # Read
        data = resource.read()
        assert data["name"] == "test"

        # Update
        new_widgets = [{"type": "table"}]
        success = resource.update(widgets=new_widgets)
        assert success is True
        assert len(resource.widgets) == 1

        # Delete
        success = resource.delete()
        assert success is True


class TestTerraformGenerator:
    """Test TerraformGenerator class."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = TerraformGenerator(provider_config={"endpoint": "test"})

        assert generator.provider_config["endpoint"] == "test"
        assert len(generator.resources) == 0

    def test_add_resource(self):
        """Test adding resources."""
        generator = TerraformGenerator()
        resource = budget(name="test", amount=1000)

        generator.add_resource(resource)

        assert len(generator.resources) == 1

    def test_generate_provider_block(self):
        """Test generating provider block."""
        generator = TerraformGenerator(
            provider_config={
                "endpoint": "https://api.openfinops.io",
                "api_key": "test-key",
                "timeout": 30,
            }
        )

        hcl = generator.generate_provider_block()

        assert 'provider "openfinops"' in hcl
        assert "endpoint" in hcl
        assert "api_key" in hcl
        assert "timeout" in hcl

    def test_generate_complete_config(self):
        """Test generating complete Terraform configuration."""
        generator = TerraformGenerator(provider_config={"endpoint": "test"})

        budget_resource = budget(name="test_budget", amount=5000)
        generator.add_resource(budget_resource)

        hcl = generator.generate()

        assert "terraform {" in hcl
        assert "required_providers {" in hcl
        assert 'provider "openfinops"' in hcl
        assert "resource" in hcl

    def test_generate_terraform_function(self):
        """Test generate_terraform helper function."""
        provider_config = {"endpoint": "test", "api_key": "key"}
        resources = [
            budget(name="budget1", amount=1000),
            policy(name="policy1", policy_type="budget", rules=[{}]),
        ]

        hcl = generate_terraform(provider_config, resources)

        assert "terraform {" in hcl
        assert "openfinops_budget" in hcl
        assert "openfinops_policy" in hcl


class TestOpenFinOpsClient:
    """Test OpenFinOpsClient class."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = OpenFinOpsClient(
            endpoint="https://api.openfinops.io",
            api_key="test-key",
        )

        assert client.endpoint == "https://api.openfinops.io"
        assert client.api_key == "test-key"

    def test_create_budget(self):
        """Test creating budget via API."""
        client = OpenFinOpsClient(endpoint="https://api.test.io")

        result = client.create_budget({"name": "test", "amount": 1000})

        assert result["success"] is True

    def test_get_budget(self):
        """Test getting budget via API."""
        client = OpenFinOpsClient(endpoint="https://api.test.io")

        result = client.get_budget("budget-123")

        assert result is not None

    def test_list_budgets(self):
        """Test listing budgets via API."""
        client = OpenFinOpsClient(endpoint="https://api.test.io")

        budgets = client.list_budgets()

        assert isinstance(budgets, list)

    def test_policy_operations(self):
        """Test policy API operations."""
        client = OpenFinOpsClient(endpoint="https://api.test.io")

        # Create
        result = client.create_policy({"name": "test", "rules": []})
        assert result["success"] is True

        # Get
        result = client.get_policy("policy-123")
        assert result is not None

        # Update
        result = client.update_policy("policy-123", {"enabled": False})
        assert result is not None

        # Delete
        result = client.delete_policy("policy-123")
        assert result is not None

    def test_generic_resource_operations(self):
        """Test generic resource operations."""
        client = OpenFinOpsClient(endpoint="https://api.test.io")

        # Get resource
        result = client.get_resource("budget", "budget-123")
        assert result is not None

        # List resources
        resources = client.list_resources("policy")
        assert isinstance(resources, list)


class TestIntegration:
    """Integration tests for IaC system."""

    def test_complete_workflow(self, provider):
        """Test complete IaC workflow."""
        # Define resources
        budget_resource = budget(
            name="prod_budget",
            amount=10000,
            period="monthly",
            filters={"environment": "production"},
            provider=provider,
        )

        policy_resource = policy(
            name="tag_policy",
            policy_type="tagging",
            rules=[{"tag": "owner", "required": True}],
            provider=provider,
        )

        alert_resource = alert(
            name="cost_alert",
            condition={"metric": "daily_cost"},
            threshold=500,
            notification_channels=["email"],
            provider=provider,
        )

        # Validate
        validation = provider.validate()
        assert validation["valid"] is True

        # Plan
        plan = provider.plan()
        assert len(plan["create"]) == 3

        # Apply
        result = provider.apply(auto_approve=True)
        assert len(result["created"]) == 3
        assert len(result["failed"]) == 0

        # Verify state
        assert budget_resource.state == ResourceState.ACTIVE
        assert policy_resource.state == ResourceState.ACTIVE
        assert alert_resource.state == ResourceState.ACTIVE

    def test_terraform_generation_workflow(self):
        """Test Terraform generation workflow."""
        # Create resources
        resources = [
            budget(name="budget1", amount=5000, period="monthly"),
            policy(name="policy1", policy_type="budget", rules=[{}]),
            alert(
                name="alert1",
                condition={"metric": "cost"},
                threshold=1000,
                notification_channels=["email"],
            ),
        ]

        # Generate Terraform
        provider_config = {"endpoint": "https://api.openfinops.io"}
        hcl = generate_terraform(provider_config, resources)

        # Verify HCL contains all resources
        assert "openfinops_budget" in hcl
        assert "openfinops_policy" in hcl
        assert "openfinops_alert" in hcl
        assert "budget1" in hcl
        assert "policy1" in hcl
        assert "alert1" in hcl


# Run quick test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
