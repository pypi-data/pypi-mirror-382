"""
Tests for SaaS Management System
==================================

Test SaaS discovery, license management, usage tracking, and shadow IT detection.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
import time
from openfinops.saas import (
    # SaaS Discovery
    SaaSDiscovery,
    SaaSApplication,
    SaaSCategory,
    ApprovalStatus,
    create_sample_application,
    # License Management
    LicenseManager,
    License,
    LicenseType,
    LicenseStatus,
    # Usage Tracking
    UsageTracker,
    UserActivity,
    ActivityLevel,
    analyze_usage_patterns,
    # Shadow IT
    ShadowITDetector,
    ShadowITApplication,
    RiskLevel,
    setup_default_shadow_it_rules,
)


class TestSaaSDiscovery:
    """Test SaaSDiscovery class."""

    def test_initialization(self):
        """Test discovery initialization."""
        discovery = SaaSDiscovery()

        assert discovery is not None
        assert discovery.get_total_spend() == 0

    def test_register_application(self):
        """Test registering an application."""
        discovery = SaaSDiscovery()

        app = create_sample_application(
            name="Slack",
            vendor="Slack Technologies",
            category=SaaSCategory.COLLABORATION,
            monthly_cost=1500,
            users=50,
            active_users=45,
        )

        discovery.register_application(app)

        retrieved = discovery.get_application(app.app_id)
        assert retrieved == app

    def test_list_applications(self):
        """Test listing applications with filters."""
        discovery = SaaSDiscovery()

        app1 = create_sample_application(
            "Slack", "Slack", SaaSCategory.COLLABORATION, 1500, 50, 45
        )
        app2 = create_sample_application(
            "GitHub", "GitHub", SaaSCategory.DEVELOPMENT, 2000, 30, 28
        )
        app3 = create_sample_application(
            "Zoom", "Zoom", SaaSCategory.COLLABORATION, 500, 100, 80
        )

        discovery.register_application(app1)
        discovery.register_application(app2)
        discovery.register_application(app3)

        # All apps
        all_apps = discovery.list_applications()
        assert len(all_apps) == 3

        # Filter by category
        collab_apps = discovery.list_applications(category=SaaSCategory.COLLABORATION)
        assert len(collab_apps) == 2

        # Filter by min cost
        expensive_apps = discovery.list_applications(min_cost=1000)
        assert len(expensive_apps) == 2

    def test_discover_from_billing(self):
        """Test discovering apps from billing data."""
        discovery = SaaSDiscovery()

        billing_data = [
            {"vendor": "Slack Technologies", "amount": 1500, "description": "Monthly subscription"},
            {"vendor": "GitHub", "amount": 2000, "description": "Team plan"},
            {"vendor": "AWS", "amount": 5000, "description": "Cloud services"},
        ]

        discovered = discovery.discover_from_billing(billing_data)

        # Should discover Slack and GitHub (known SaaS vendors)
        assert len(discovered) >= 1

    def test_get_total_spend(self):
        """Test calculating total spend."""
        discovery = SaaSDiscovery()

        app1 = create_sample_application("App1", "Vendor1", SaaSCategory.OTHER, 1000, 10, 8)
        app2 = create_sample_application("App2", "Vendor2", SaaSCategory.OTHER, 2000, 20, 15)

        discovery.register_application(app1)
        discovery.register_application(app2)

        total = discovery.get_total_spend()
        assert total == 3000

    def test_get_total_wasted_spend(self):
        """Test calculating wasted spend."""
        discovery = SaaSDiscovery()

        # App with 50% utilization - 5 unused licenses
        app = create_sample_application("App", "Vendor", SaaSCategory.OTHER, 1000, 10, 5)
        discovery.register_application(app)

        wasted = discovery.get_total_wasted_spend()
        assert wasted == 500  # 50% of $1000

    def test_get_category_breakdown(self):
        """Test category breakdown."""
        discovery = SaaSDiscovery()

        app1 = create_sample_application(
            "Slack", "Slack", SaaSCategory.COLLABORATION, 1500, 50, 45
        )
        app2 = create_sample_application(
            "Zoom", "Zoom", SaaSCategory.COLLABORATION, 500, 100, 80
        )

        discovery.register_application(app1)
        discovery.register_application(app2)

        breakdown = discovery.get_category_breakdown()

        assert "collaboration" in breakdown
        assert breakdown["collaboration"]["spend"] == 2000
        assert breakdown["collaboration"]["app_count"] == 2

    def test_get_optimization_opportunities(self):
        """Test optimization opportunities."""
        discovery = SaaSDiscovery()

        # Low utilization app
        low_util_app = create_sample_application(
            "LowUtil", "Vendor", SaaSCategory.OTHER, 1000, 10, 3
        )

        # Unapproved expensive app
        unapproved_app = create_sample_application(
            "Unapproved", "Vendor", SaaSCategory.OTHER, 200, 5, 4
        )
        unapproved_app.approval_status = ApprovalStatus.UNKNOWN

        discovery.register_application(low_util_app)
        discovery.register_application(unapproved_app)

        opportunities = discovery.get_optimization_opportunities()

        assert len(opportunities) > 0
        assert any(o["type"] == "low_utilization" for o in opportunities)


class TestSaaSApplication:
    """Test SaaSApplication class."""

    def test_application_creation(self):
        """Test creating an application."""
        app = create_sample_application(
            "Slack", "Slack", SaaSCategory.COLLABORATION, 1500, 50, 45
        )

        assert app.name == "Slack"
        assert app.monthly_cost == 1500
        assert app.users == 50

    def test_get_utilization_rate(self):
        """Test utilization rate calculation."""
        app = create_sample_application(
            "App", "Vendor", SaaSCategory.OTHER, 1000, 10, 8
        )

        utilization = app.get_utilization_rate()
        assert utilization == 0.8  # 80%

    def test_get_cost_per_user(self):
        """Test cost per user calculation."""
        app = create_sample_application(
            "App", "Vendor", SaaSCategory.OTHER, 1000, 10, 8
        )

        cost_per_user = app.get_cost_per_user()
        assert cost_per_user == 100  # $1000 / 10 users

    def test_get_wasted_spend(self):
        """Test wasted spend calculation."""
        app = create_sample_application(
            "App", "Vendor", SaaSCategory.OTHER, 1000, 10, 6
        )

        wasted = app.get_wasted_spend()
        assert wasted == 400  # 40% of $1000 (4 unused licenses)


class TestLicenseManager:
    """Test LicenseManager class."""

    def test_initialization(self):
        """Test license manager initialization."""
        manager = LicenseManager()

        assert manager is not None
        metrics = manager.get_license_metrics()
        assert metrics["total_licenses"] == 0

    def test_add_license(self):
        """Test adding a license."""
        manager = LicenseManager()

        license = License(
            license_id="lic-001",
            app_id="app-slack",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=50,
            cost_per_license=30.0,
        )

        manager.add_license(license)

        retrieved = manager.get_license("lic-001")
        assert retrieved == license

    def test_assign_license(self):
        """Test assigning license to user."""
        manager = LicenseManager()

        license = License(
            license_id="lic-001",
            app_id="app-slack",
            license_type=LicenseType.NAMED_USER,
            quantity=10,
            cost_per_license=30.0,
        )

        manager.add_license(license)

        success = manager.assign_license("lic-001", "user-001")

        assert success is True
        assert license.assigned == 1

    def test_unassign_license(self):
        """Test unassigning license from user."""
        manager = LicenseManager()

        license = License(
            license_id="lic-001",
            app_id="app-slack",
            license_type=LicenseType.NAMED_USER,
            quantity=10,
            cost_per_license=30.0,
        )

        manager.add_license(license)
        manager.assign_license("lic-001", "user-001")

        success = manager.unassign_license("lic-001", "user-001")

        assert success is True
        assert license.assigned == 0

    def test_get_expiring_licenses(self):
        """Test getting expiring licenses."""
        manager = LicenseManager()

        current_time = time.time()

        # License expiring in 15 days
        expiring_license = License(
            license_id="lic-001",
            app_id="app-001",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            cost_per_license=30.0,
            expiration_date=current_time + (15 * 24 * 3600),
        )

        # License expiring in 60 days
        future_license = License(
            license_id="lic-002",
            app_id="app-002",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            cost_per_license=30.0,
            expiration_date=current_time + (60 * 24 * 3600),
        )

        manager.add_license(expiring_license)
        manager.add_license(future_license)

        expiring = manager.get_expiring_licenses(days=30)

        assert len(expiring) == 1
        assert expiring[0].license_id == "lic-001"

    def test_get_optimization_recommendations(self):
        """Test license optimization recommendations."""
        manager = LicenseManager()

        # Low utilization license
        low_util_license = License(
            license_id="lic-001",
            app_id="app-001",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            assigned=10,
            active=3,  # Only 30% active
            cost_per_license=30.0,
        )

        manager.add_license(low_util_license)

        recommendations = manager.get_optimization_recommendations()

        assert len(recommendations) > 0
        assert any(r["type"] == "reduce_licenses" for r in recommendations)

    def test_license_metrics(self):
        """Test license metrics calculation."""
        manager = LicenseManager()

        license1 = License(
            license_id="lic-001",
            app_id="app-001",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            active=8,
            cost_per_license=30.0,
        )

        license2 = License(
            license_id="lic-002",
            app_id="app-002",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=20,
            active=15,
            cost_per_license=50.0,
        )

        manager.add_license(license1)
        manager.add_license(license2)

        metrics = manager.get_license_metrics()

        assert metrics["total_licenses"] == 2
        assert metrics["total_seats"] == 30
        assert metrics["active_seats"] == 23
        assert metrics["total_monthly_cost"] == 1300  # (10*30) + (20*50)


class TestLicense:
    """Test License class."""

    def test_license_creation(self):
        """Test creating a license."""
        license = License(
            license_id="lic-001",
            app_id="app-slack",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=50,
            cost_per_license=30.0,
        )

        assert license.license_id == "lic-001"
        assert license.quantity == 50

    def test_get_utilization_rate(self):
        """Test utilization rate calculation."""
        license = License(
            license_id="lic-001",
            app_id="app-001",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            active=8,
            cost_per_license=30.0,
        )

        utilization = license.get_utilization_rate()
        assert utilization == 0.8

    def test_get_total_cost(self):
        """Test total cost calculation."""
        license = License(
            license_id="lic-001",
            app_id="app-001",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            cost_per_license=30.0,
        )

        total_cost = license.get_total_cost()
        assert total_cost == 300

    def test_get_wasted_cost(self):
        """Test wasted cost calculation."""
        license = License(
            license_id="lic-001",
            app_id="app-001",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            active=6,
            cost_per_license=30.0,
        )

        wasted = license.get_wasted_cost()
        assert wasted == 120  # 4 unused * $30

    def test_get_status(self):
        """Test license status determination."""
        current_time = time.time()

        # Active license
        active_license = License(
            license_id="lic-001",
            app_id="app-001",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            active=5,
            cost_per_license=30.0,
        )

        assert active_license.get_status() == LicenseStatus.ACTIVE

        # Expired license
        expired_license = License(
            license_id="lic-002",
            app_id="app-002",
            license_type=LicenseType.SUBSCRIPTION,
            quantity=10,
            cost_per_license=30.0,
            expiration_date=current_time - 1000,  # Expired
        )

        assert expired_license.get_status() == LicenseStatus.EXPIRED


class TestUsageTracker:
    """Test UsageTracker class."""

    def test_initialization(self):
        """Test usage tracker initialization."""
        tracker = UsageTracker()

        assert tracker is not None

    def test_record_login(self):
        """Test recording user login."""
        tracker = UsageTracker()

        tracker.record_login("user-001", "app-slack")

        activity = tracker.get_user_activity("user-001", "app-slack")

        assert activity is not None
        assert activity.login_count == 1

    def test_record_session(self):
        """Test recording user session."""
        tracker = UsageTracker()

        tracker.record_session("user-001", "app-slack", features=["messaging", "calls"])

        activity = tracker.get_user_activity("user-001", "app-slack")

        assert activity is not None
        assert activity.sessions_30d == 1
        assert "messaging" in activity.features_used

    def test_get_app_users(self):
        """Test getting app users."""
        tracker = UsageTracker()

        tracker.record_login("user-001", "app-slack")
        tracker.record_login("user-002", "app-slack")
        tracker.record_login("user-003", "app-github")

        slack_users = tracker.get_app_users("app-slack")

        assert len(slack_users) == 2

    def test_get_inactive_users(self):
        """Test getting inactive users."""
        tracker = UsageTracker()

        current_time = time.time()

        # Active user (logged in recently)
        tracker.record_login("user-001", "app-slack", timestamp=current_time)

        # Inactive user (logged in 45 days ago)
        tracker.record_login("user-002", "app-slack", timestamp=current_time - (45 * 24 * 3600))

        inactive = tracker.get_inactive_users("app-slack", days=30)

        assert len(inactive) == 1
        assert inactive[0].user_id == "user-002"

    def test_get_usage_summary(self):
        """Test usage summary."""
        tracker = UsageTracker()

        current_time = time.time()

        # Active users
        tracker.record_login("user-001", "app-slack", timestamp=current_time)
        tracker.record_login("user-002", "app-slack", timestamp=current_time)

        # Inactive user
        tracker.record_login("user-003", "app-slack", timestamp=current_time - (40 * 24 * 3600))

        summary = tracker.get_usage_summary("app-slack")

        assert summary["total_users"] == 3
        assert summary["active_users"] == 2
        assert summary["inactive_users"] == 1

    def test_get_reclamation_candidates(self):
        """Test getting license reclamation candidates."""
        tracker = UsageTracker()

        current_time = time.time()

        # User inactive for 90 days
        tracker.record_login("user-001", "app-slack", timestamp=current_time - (90 * 24 * 3600))

        candidates = tracker.get_reclamation_candidates("app-slack", inactivity_days=60)

        assert len(candidates) == 1
        assert candidates[0]["user_id"] == "user-001"


class TestUserActivity:
    """Test UserActivity class."""

    def test_get_activity_level(self):
        """Test activity level determination."""
        current_time = time.time()

        # Active user
        active = UserActivity(
            user_id="user-001",
            app_id="app-slack",
            last_login=current_time,
            login_count=10,
        )

        assert active.get_activity_level() == ActivityLevel.ACTIVE

        # Inactive user
        inactive = UserActivity(
            user_id="user-002",
            app_id="app-slack",
            last_login=current_time - (40 * 24 * 3600),
            login_count=5,
        )

        assert inactive.get_activity_level() == ActivityLevel.INACTIVE

        # Never used
        never_used = UserActivity(
            user_id="user-003",
            app_id="app-slack",
            login_count=0,
        )

        assert never_used.get_activity_level() == ActivityLevel.NEVER_USED


class TestShadowITDetector:
    """Test ShadowITDetector class."""

    def test_initialization(self):
        """Test detector initialization."""
        detector = ShadowITDetector()

        assert detector is not None
        summary = detector.get_shadow_it_summary()
        assert summary["total_shadow_apps"] == 0

    def test_add_approved_vendor(self):
        """Test adding approved vendor."""
        detector = ShadowITDetector()

        detector.add_approved_vendor("Slack")

        assert detector.is_approved("Slack")
        assert detector.is_approved("slack")  # Case insensitive

    def test_detect_from_expenses(self):
        """Test detecting shadow IT from expenses."""
        detector = ShadowITDetector()

        detector.add_approved_vendor("Slack")

        expense_data = [
            {"vendor": "Slack", "amount": 1500, "category": "Software"},
            {"vendor": "Unknown Tool", "amount": 500, "category": "SaaS Subscription"},
        ]

        detected = detector.detect_from_expenses(expense_data)

        # Should detect "Unknown Tool" as shadow IT (Slack is approved)
        assert len(detected) >= 1

    def test_list_shadow_apps(self):
        """Test listing shadow apps."""
        detector = ShadowITDetector()

        app1 = ShadowITApplication(
            app_id="shadow-001",
            name="Unknown App",
            discovered_via="billing",
            risk_level=RiskLevel.HIGH,
        )

        app2 = ShadowITApplication(
            app_id="shadow-002",
            name="Another App",
            discovered_via="network",
            risk_level=RiskLevel.LOW,
        )

        detector._shadow_apps["shadow-001"] = app1
        detector._shadow_apps["shadow-002"] = app2

        # All apps
        all_apps = detector.list_shadow_apps()
        assert len(all_apps) == 2

        # Filter by risk
        high_risk = detector.list_shadow_apps(risk_level=RiskLevel.HIGH)
        assert len(high_risk) == 1

    def test_get_shadow_it_summary(self):
        """Test shadow IT summary."""
        detector = ShadowITDetector()

        app1 = ShadowITApplication(
            app_id="shadow-001",
            name="App 1",
            discovered_via="billing",
            monthly_cost=500,
            users=10,
            risk_level=RiskLevel.CRITICAL,
        )

        app2 = ShadowITApplication(
            app_id="shadow-002",
            name="App 2",
            discovered_via="network",
            monthly_cost=200,
            users=5,
            risk_level=RiskLevel.HIGH,
        )

        detector._shadow_apps["shadow-001"] = app1
        detector._shadow_apps["shadow-002"] = app2

        summary = detector.get_shadow_it_summary()

        assert summary["total_shadow_apps"] == 2
        assert summary["total_monthly_cost"] == 700
        assert summary["critical_apps"] == 1
        assert summary["high_risk_apps"] == 1

    def test_get_remediation_plan(self):
        """Test remediation plan generation."""
        detector = ShadowITDetector()

        app = ShadowITApplication(
            app_id="shadow-001",
            name="Unknown App",
            discovered_via="billing",
            monthly_cost=1000,
            risk_level=RiskLevel.CRITICAL,
        )

        detector._shadow_apps["shadow-001"] = app

        plan = detector.get_remediation_plan()

        assert len(plan) == 1
        assert plan[0]["priority"] == "immediate"
        assert len(plan[0]["actions"]) > 0


class TestIntegration:
    """Integration tests for SaaS management."""

    def test_complete_saas_workflow(self):
        """Test complete SaaS management workflow."""
        # Discovery
        discovery = SaaSDiscovery()

        app = create_sample_application(
            "Slack", "Slack Technologies", SaaSCategory.COLLABORATION, 1500, 50, 40
        )
        discovery.register_application(app)

        # License management
        license_mgr = LicenseManager()

        license = License(
            license_id="lic-slack-001",
            app_id=app.app_id,
            license_type=LicenseType.SUBSCRIPTION,
            quantity=50,
            cost_per_license=30.0,
        )

        license_mgr.add_license(license)
        license_mgr.assign_license("lic-slack-001", "user-001")

        # Usage tracking
        tracker = UsageTracker()
        tracker.record_login("user-001", app.app_id)

        # Verify workflow
        assert discovery.get_total_spend() == 1500
        assert license.assigned == 1

        activity = tracker.get_user_activity("user-001", app.app_id)
        assert activity.login_count == 1

    def test_optimization_workflow(self):
        """Test optimization recommendations workflow."""
        discovery = SaaSDiscovery()

        # Low utilization app
        app = create_sample_application(
            "UnderUsed App", "Vendor", SaaSCategory.OTHER, 2000, 100, 30
        )
        discovery.register_application(app)

        # Get opportunities
        opportunities = discovery.get_optimization_opportunities()

        assert len(opportunities) > 0
        assert any(o["type"] == "low_utilization" for o in opportunities)

        # Verify potential savings
        low_util_opp = next(o for o in opportunities if o["type"] == "low_utilization")
        assert low_util_opp["potential_savings"] > 0


# Run quick test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
