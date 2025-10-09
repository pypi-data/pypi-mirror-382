"""
SaaS Management & License Optimization
========================================

Comprehensive SaaS application management, license optimization, and shadow IT detection.

This module provides:
- SaaS application discovery and tracking
- License management and optimization
- Usage tracking and analytics
- Shadow IT detection and remediation
- Cost optimization recommendations

Example:
    >>> from openfinops.saas import SaaSDiscovery, LicenseManager, UsageTracker
    >>>
    >>> # Discover SaaS applications
    >>> discovery = SaaSDiscovery()
    >>> apps = discovery.discover_from_billing(billing_data)
    >>>
    >>> # Manage licenses
    >>> license_mgr = LicenseManager()
    >>> license_mgr.add_license(license)
    >>> recommendations = license_mgr.get_optimization_recommendations()
    >>>
    >>> # Track usage
    >>> tracker = UsageTracker()
    >>> tracker.record_login(user_id, app_id)
    >>> inactive = tracker.get_inactive_users(app_id)
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .saas_discovery import (
    SaaSDiscovery,
    SaaSApplication,
    SaaSCategory,
    ApprovalStatus,
    create_sample_application,
)
from .license_manager import (
    LicenseManager,
    License,
    LicenseType,
    LicenseStatus,
)
from .usage_tracker import (
    UsageTracker,
    UserActivity,
    ActivityLevel,
    analyze_usage_patterns,
)
from .shadow_it_detector import (
    ShadowITDetector,
    ShadowITApplication,
    RiskLevel,
    setup_default_shadow_it_rules,
)

__all__ = [
    # SaaS Discovery
    "SaaSDiscovery",
    "SaaSApplication",
    "SaaSCategory",
    "ApprovalStatus",
    "create_sample_application",
    # License Management
    "LicenseManager",
    "License",
    "LicenseType",
    "LicenseStatus",
    # Usage Tracking
    "UsageTracker",
    "UserActivity",
    "ActivityLevel",
    "analyze_usage_patterns",
    # Shadow IT Detection
    "ShadowITDetector",
    "ShadowITApplication",
    "RiskLevel",
    "setup_default_shadow_it_rules",
]
