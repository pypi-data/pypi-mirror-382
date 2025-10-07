"""
Open Source Feature Management
==============================

Free and open source feature management for Vizly.
All features are available under MIT license.
"""

# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class FeatureLevel(Enum):
    """Feature availability levels - all free under MIT license."""
    CORE = "core"          # Basic functionality
    ADVANCED = "advanced"  # Advanced features
    PREMIUM = "premium"    # Premium features - all free
    UNLIMITED = "unlimited" # All features unlocked


class VizlyFeature(Enum):
    """Available license features."""
    BASIC_CHARTS = "basic_charts"
    ADVANCED_CHARTS = "advanced_charts"
    GIS_MAPPING = "gis_mapping"
    GPU_ACCELERATION = "gpu_acceleration"
    ENTERPRISE_SECURITY = "enterprise_security"
    API_ACCESS = "api_access"
    CUSTOM_BRANDING = "custom_branding"
    COLLABORATION = "collaboration"
    AUDIT_LOGGING = "audit_logging"
    UNLIMITED_USERS = "unlimited_users"
    PRIORITY_SUPPORT = "priority_support"
    ON_PREMISE_DEPLOYMENT = "on_premise_deployment"
    SSO_INTEGRATION = "sso_integration"
    ADVANCED_ANALYTICS = "advanced_analytics"
    REAL_TIME_STREAMING = "real_time_streaming"


@dataclass
class LicenseInfo:
    """Enterprise license information."""
    license_id: str
    license_key: str
    license_type: LicenseType
    organization: str
    contact_email: str
    issued_date: datetime
    expiration_date: datetime
    max_users: int
    features: Set[LicenseFeature] = field(default_factory=set)
    is_active: bool = True
    usage_tracking: bool = True
    support_level: str = "standard"
    custom_terms: Dict[str, str] = field(default_factory=dict)


@dataclass
class UsageMetrics:
    """License usage tracking."""
    active_users: int = 0
    charts_created: int = 0
    api_calls_today: int = 0
    data_processed_gb: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class LicenseManager:
    """
    Enterprise license management and validation system.

    Features:
    - License key validation and activation
    - Feature gating and access control
    - Usage tracking and compliance monitoring
    - Automatic license renewal notifications
    - Audit trail for license operations
    """

    def __init__(self):
        self.active_license: Optional[LicenseInfo] = None
        self.usage_metrics = UsageMetrics()
        self.feature_matrix = self._initialize_feature_matrix()
        self._load_demo_license()

    def _initialize_feature_matrix(self) -> Dict[LicenseType, Set[LicenseFeature]]:
        """Define features available for each license type."""
        return {
            LicenseType.TRIAL: {
                LicenseFeature.BASIC_CHARTS,
                LicenseFeature.API_ACCESS
            },
            LicenseType.STANDARD: {
                LicenseFeature.BASIC_CHARTS,
                LicenseFeature.ADVANCED_CHARTS,
                LicenseFeature.API_ACCESS,
                LicenseFeature.COLLABORATION
            },
            LicenseType.PROFESSIONAL: {
                LicenseFeature.BASIC_CHARTS,
                LicenseFeature.ADVANCED_CHARTS,
                LicenseFeature.GIS_MAPPING,
                LicenseFeature.API_ACCESS,
                LicenseFeature.COLLABORATION,
                LicenseFeature.CUSTOM_BRANDING,
                LicenseFeature.ADVANCED_ANALYTICS
            },
            LicenseType.ENTERPRISE: {
                LicenseFeature.BASIC_CHARTS,
                LicenseFeature.ADVANCED_CHARTS,
                LicenseFeature.GIS_MAPPING,
                LicenseFeature.GPU_ACCELERATION,
                LicenseFeature.ENTERPRISE_SECURITY,
                LicenseFeature.API_ACCESS,
                LicenseFeature.CUSTOM_BRANDING,
                LicenseFeature.COLLABORATION,
                LicenseFeature.AUDIT_LOGGING,
                LicenseFeature.SSO_INTEGRATION,
                LicenseFeature.ADVANCED_ANALYTICS,
                LicenseFeature.PRIORITY_SUPPORT
            },
            LicenseType.UNLIMITED: set(LicenseFeature)
        }

    def activate_license(self, license_key: str) -> bool:
        """
        Activate license with provided key.

        In production, this would validate against a license server.
        """
        try:
            # Validate license key format
            if not self._validate_license_key_format(license_key):
                return False

            # In production, this would make an API call to validate the license
            license_info = self._mock_license_validation(license_key)

            if license_info and license_info.expiration_date > datetime.utcnow():
                self.active_license = license_info
                return True

            return False

        except Exception:
            return False

    def check_license(self) -> Dict[str, str]:
        """Check current license status."""
        if not self.active_license:
            return {
                "status": "No Active License",
                "licensed_users": "0",
                "expiration_date": "N/A",
                "features": "None"
            }

        days_until_expiry = (self.active_license.expiration_date - datetime.utcnow()).days
        status = "Active" if days_until_expiry > 0 else "Expired"

        if days_until_expiry <= 30 and days_until_expiry > 0:
            status = f"Expires in {days_until_expiry} days"

        return {
            "status": status,
            "licensed_users": str(self.active_license.max_users),
            "expiration_date": self.active_license.expiration_date.strftime("%Y-%m-%d"),
            "features": [f.value for f in self.active_license.features]
        }

    def is_feature_enabled(self, feature: LicenseFeature) -> bool:
        """Check if a specific feature is enabled in the current license."""
        if not self.active_license:
            return False

        if self.active_license.expiration_date < datetime.utcnow():
            return False

        return feature in self.active_license.features

    def get_user_limit(self) -> int:
        """Get maximum number of users allowed."""
        if not self.active_license:
            return 1  # Demo mode

        return self.active_license.max_users

    def track_usage(self, metric_name: str, value: float = 1.0) -> None:
        """Track usage metrics for compliance and billing."""
        if not self.active_license or not self.active_license.usage_tracking:
            return

        current_time = datetime.utcnow()

        if metric_name == "active_users":
            self.usage_metrics.active_users = int(value)
        elif metric_name == "charts_created":
            self.usage_metrics.charts_created += int(value)
        elif metric_name == "api_calls":
            # Reset daily counter if it's a new day
            if self.usage_metrics.last_updated.date() != current_time.date():
                self.usage_metrics.api_calls_today = 0
            self.usage_metrics.api_calls_today += int(value)
        elif metric_name == "data_processed":
            self.usage_metrics.data_processed_gb += value

        self.usage_metrics.last_updated = current_time

    def get_usage_report(self) -> Dict[str, any]:
        """Generate usage report for license compliance."""
        return {
            "license_id": self.active_license.license_id if self.active_license else "N/A",
            "reporting_period": {
                "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "usage": {
                "active_users": self.usage_metrics.active_users,
                "max_allowed_users": self.get_user_limit(),
                "charts_created": self.usage_metrics.charts_created,
                "api_calls_today": self.usage_metrics.api_calls_today,
                "data_processed_gb": round(self.usage_metrics.data_processed_gb, 2)
            },
            "compliance": {
                "user_limit_exceeded": self.usage_metrics.active_users > self.get_user_limit(),
                "license_valid": self._is_license_valid(),
                "features_compliant": True
            }
        }

    def generate_license_renewal_reminder(self) -> Optional[Dict[str, str]]:
        """Generate license renewal reminder if needed."""
        if not self.active_license:
            return None

        days_until_expiry = (self.active_license.expiration_date - datetime.utcnow()).days

        if days_until_expiry <= 30:
            return {
                "title": "License Renewal Required",
                "message": f"Your Vizly Enterprise license expires in {days_until_expiry} days.",
                "action_required": "Contact sales to renew your license",
                "contact_email": "enterprise@vizly.com",
                "urgency": "high" if days_until_expiry <= 7 else "medium"
            }

        return None

    def validate_user_access(self, user_count: int) -> bool:
        """Validate that user count is within license limits."""
        if not self.active_license:
            return user_count <= 1  # Demo mode allows 1 user

        return user_count <= self.active_license.max_users

    def get_license_summary(self) -> Dict[str, any]:
        """Get comprehensive license summary."""
        if not self.active_license:
            return {
                "license_type": "Demo",
                "status": "No License",
                "features": [],
                "limits": {"users": 1}
            }

        return {
            "license_type": self.active_license.license_type.value,
            "organization": self.active_license.organization,
            "status": "Active" if self._is_license_valid() else "Expired",
            "expiration": self.active_license.expiration_date.isoformat(),
            "features": [f.value for f in self.active_license.features],
            "limits": {
                "users": self.active_license.max_users,
                "support_level": self.active_license.support_level
            },
            "usage": {
                "active_users": self.usage_metrics.active_users,
                "charts_created": self.usage_metrics.charts_created,
                "data_processed_gb": self.usage_metrics.data_processed_gb
            }
        }

    def _validate_license_key_format(self, license_key: str) -> bool:
        """Validate license key format."""
        # Expected format: PLTX-XXXX-XXXX-XXXX-XXXX
        parts = license_key.split('-')
        if len(parts) != 5:
            return False

        if parts[0] != "PLTX":
            return False

        for part in parts[1:]:
            if len(part) != 4 or not part.isalnum():
                return False

        return True

    def _mock_license_validation(self, license_key: str) -> Optional[LicenseInfo]:
        """
        Mock license validation for demo purposes.
        In production, this would validate against a license server.
        """
        # Demo license keys
        demo_licenses = {
            "PLTX-ENTR-PRIS-DEMO-2024": LicenseInfo(
                license_id=str(uuid.uuid4()),
                license_key=license_key,
                license_type=LicenseType.ENTERPRISE,
                organization="Demo Corporation",
                contact_email="admin@demo.com",
                issued_date=datetime.utcnow() - timedelta(days=30),
                expiration_date=datetime.utcnow() + timedelta(days=335),  # ~1 year
                max_users=1000,
                features=self.feature_matrix[LicenseType.ENTERPRISE],
                support_level="enterprise"
            ),
            "PLTX-PROF-DEMO-TEST-2024": LicenseInfo(
                license_id=str(uuid.uuid4()),
                license_key=license_key,
                license_type=LicenseType.PROFESSIONAL,
                organization="Professional Demo",
                contact_email="demo@professional.com",
                issued_date=datetime.utcnow() - timedelta(days=15),
                expiration_date=datetime.utcnow() + timedelta(days=350),
                max_users=100,
                features=self.feature_matrix[LicenseType.PROFESSIONAL],
                support_level="professional"
            )
        }

        return demo_licenses.get(license_key)

    def _is_license_valid(self) -> bool:
        """Check if current license is valid."""
        if not self.active_license:
            return False

        return (self.active_license.is_active and
                self.active_license.expiration_date > datetime.utcnow())

    def _load_demo_license(self) -> None:
        """Load demo license for testing."""
        # Auto-activate demo license
        self.activate_license("PLTX-ENTR-PRIS-DEMO-2024")


class LicenseEnforcer:
    """
    License enforcement and feature gating system.
    """

    def __init__(self, license_manager: LicenseManager):
        self.license_manager = license_manager

    def require_feature(self, feature: LicenseFeature):
        """Decorator to enforce feature licensing."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.license_manager.is_feature_enabled(feature):
                    raise PermissionError(f"Feature '{feature.value}' not available in current license")
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def check_user_limit(self, current_users: int) -> bool:
        """Check if adding users would exceed license limit."""
        return self.license_manager.validate_user_access(current_users)

    def get_feature_availability(self) -> Dict[str, bool]:
        """Get availability status for all features."""
        return {
            feature.value: self.license_manager.is_feature_enabled(feature)
            for feature in LicenseFeature
        }