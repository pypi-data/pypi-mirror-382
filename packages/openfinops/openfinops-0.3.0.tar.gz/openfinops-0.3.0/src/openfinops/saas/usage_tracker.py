"""
Usage Tracking
===============

Track SaaS application usage and identify optimization opportunities.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ActivityLevel(Enum):
    """User activity levels."""

    ACTIVE = "active"  # Used in last 7 days
    OCCASIONAL = "occasional"  # Used in last 30 days
    INACTIVE = "inactive"  # Not used in 30+ days
    NEVER_USED = "never_used"  # Never logged in


@dataclass
class UserActivity:
    """
    User activity record.

    Attributes:
        user_id: User identifier
        app_id: Application ID
        last_login: Last login timestamp
        login_count: Total login count
        sessions_30d: Sessions in last 30 days
        active_days_30d: Active days in last 30 days
        features_used: Features accessed
    """

    user_id: str
    app_id: str
    last_login: Optional[float] = None
    login_count: int = 0
    sessions_30d: int = 0
    active_days_30d: int = 0
    features_used: List[str] = field(default_factory=list)

    def get_activity_level(self) -> ActivityLevel:
        """
        Determine activity level.

        Returns:
            Activity level
        """
        if self.login_count == 0:
            return ActivityLevel.NEVER_USED

        if not self.last_login:
            return ActivityLevel.INACTIVE

        current_time = datetime.now().timestamp()
        days_since_login = (current_time - self.last_login) / (24 * 3600)

        if days_since_login <= 7:
            return ActivityLevel.ACTIVE
        elif days_since_login <= 30:
            return ActivityLevel.OCCASIONAL
        else:
            return ActivityLevel.INACTIVE

    def days_since_last_login(self) -> Optional[int]:
        """
        Calculate days since last login.

        Returns:
            Days since last login or None
        """
        if not self.last_login:
            return None

        current_time = datetime.now().timestamp()
        return int((current_time - self.last_login) / (24 * 3600))


class UsageTracker:
    """
    Tracks SaaS application usage patterns.
    """

    def __init__(self):
        """Initialize usage tracker."""
        self._activity: Dict[str, UserActivity] = {}  # key: user_id:app_id

    def _get_key(self, user_id: str, app_id: str) -> str:
        """Generate composite key."""
        return f"{user_id}:{app_id}"

    def record_login(self, user_id: str, app_id: str, timestamp: Optional[float] = None):
        """
        Record user login.

        Args:
            user_id: User ID
            app_id: Application ID
            timestamp: Login timestamp (defaults to now)
        """
        key = self._get_key(user_id, app_id)

        if key not in self._activity:
            self._activity[key] = UserActivity(user_id=user_id, app_id=app_id)

        activity = self._activity[key]
        activity.login_count += 1
        activity.last_login = timestamp or datetime.now().timestamp()

        logger.debug(f"Recorded login: {user_id} -> {app_id}")

    def record_session(
        self,
        user_id: str,
        app_id: str,
        features: Optional[List[str]] = None,
        timestamp: Optional[float] = None,
    ):
        """
        Record user session.

        Args:
            user_id: User ID
            app_id: Application ID
            features: Features accessed during session
            timestamp: Session timestamp
        """
        key = self._get_key(user_id, app_id)

        if key not in self._activity:
            self._activity[key] = UserActivity(user_id=user_id, app_id=app_id)

        activity = self._activity[key]
        activity.sessions_30d += 1

        if features:
            for feature in features:
                if feature not in activity.features_used:
                    activity.features_used.append(feature)

    def get_user_activity(self, user_id: str, app_id: str) -> Optional[UserActivity]:
        """
        Get user activity for an application.

        Args:
            user_id: User ID
            app_id: Application ID

        Returns:
            User activity or None
        """
        key = self._get_key(user_id, app_id)
        return self._activity.get(key)

    def get_app_users(self, app_id: str) -> List[UserActivity]:
        """
        Get all users for an application.

        Args:
            app_id: Application ID

        Returns:
            List of user activities
        """
        return [a for a in self._activity.values() if a.app_id == app_id]

    def get_inactive_users(self, app_id: str, days: int = 30) -> List[UserActivity]:
        """
        Get inactive users for an application.

        Args:
            app_id: Application ID
            days: Inactivity threshold in days

        Returns:
            List of inactive user activities
        """
        inactive = []

        for activity in self.get_app_users(app_id):
            days_since = activity.days_since_last_login()

            if days_since is None or days_since >= days:
                inactive.append(activity)

        return inactive

    def get_never_used_licenses(self, app_id: str) -> List[UserActivity]:
        """
        Get users who never used the application.

        Args:
            app_id: Application ID

        Returns:
            List of never-used activities
        """
        return [
            a for a in self.get_app_users(app_id)
            if a.get_activity_level() == ActivityLevel.NEVER_USED
        ]

    def get_usage_summary(self, app_id: str) -> Dict[str, Any]:
        """
        Get usage summary for an application.

        Args:
            app_id: Application ID

        Returns:
            Usage summary
        """
        users = self.get_app_users(app_id)

        if not users:
            return {
                "app_id": app_id,
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "never_used": 0,
            }

        active = sum(1 for u in users if u.get_activity_level() == ActivityLevel.ACTIVE)
        occasional = sum(1 for u in users if u.get_activity_level() == ActivityLevel.OCCASIONAL)
        inactive = sum(1 for u in users if u.get_activity_level() == ActivityLevel.INACTIVE)
        never_used = sum(1 for u in users if u.get_activity_level() == ActivityLevel.NEVER_USED)

        total_logins = sum(u.login_count for u in users)

        return {
            "app_id": app_id,
            "total_users": len(users),
            "active_users": active,
            "occasional_users": occasional,
            "inactive_users": inactive,
            "never_used": never_used,
            "total_logins": total_logins,
            "average_logins_per_user": total_logins / len(users) if users else 0,
            "activity_breakdown": {
                "active": active,
                "occasional": occasional,
                "inactive": inactive,
                "never_used": never_used,
            },
        }

    def get_reclamation_candidates(
        self, app_id: str, inactivity_days: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Get license reclamation candidates.

        Args:
            app_id: Application ID
            inactivity_days: Inactivity threshold

        Returns:
            List of reclamation candidates
        """
        candidates = []
        inactive_users = self.get_inactive_users(app_id, inactivity_days)

        for activity in inactive_users:
            days_since = activity.days_since_last_login()

            candidates.append({
                "user_id": activity.user_id,
                "app_id": activity.app_id,
                "last_login": activity.last_login,
                "days_inactive": days_since,
                "total_logins": activity.login_count,
                "activity_level": activity.get_activity_level().value,
                "recommendation": "Reclaim license",
            })

        return sorted(candidates, key=lambda x: x.get("days_inactive", 0), reverse=True)

    def get_feature_adoption(self, app_id: str) -> Dict[str, int]:
        """
        Get feature adoption metrics.

        Args:
            app_id: Application ID

        Returns:
            Feature usage counts
        """
        feature_usage = {}
        users = self.get_app_users(app_id)

        for activity in users:
            for feature in activity.features_used:
                feature_usage[feature] = feature_usage.get(feature, 0) + 1

        return dict(sorted(feature_usage.items(), key=lambda x: x[1], reverse=True))

    def get_engagement_trends(self, app_id: str) -> Dict[str, Any]:
        """
        Get user engagement trends.

        Args:
            app_id: Application ID

        Returns:
            Engagement metrics
        """
        users = self.get_app_users(app_id)

        if not users:
            return {"app_id": app_id, "engagement_score": 0}

        # Calculate engagement score (0-100)
        active_ratio = sum(
            1 for u in users if u.get_activity_level() == ActivityLevel.ACTIVE
        ) / len(users)

        avg_sessions = sum(u.sessions_30d for u in users) / len(users)
        avg_active_days = sum(u.active_days_30d for u in users) / len(users)

        # Engagement score based on activity level and frequency
        engagement_score = min(100, int(
            (active_ratio * 40) +  # 40% weight on active users
            (min(avg_sessions / 20, 1) * 30) +  # 30% weight on session frequency
            (min(avg_active_days / 20, 1) * 30)  # 30% weight on active days
        ))

        return {
            "app_id": app_id,
            "engagement_score": engagement_score,
            "active_user_ratio": active_ratio,
            "average_sessions_30d": avg_sessions,
            "average_active_days_30d": avg_active_days,
            "health": "high" if engagement_score >= 70 else "medium" if engagement_score >= 40 else "low",
        }


def analyze_usage_patterns(
    tracker: UsageTracker, app_id: str
) -> Dict[str, Any]:
    """
    Comprehensive usage pattern analysis.

    Args:
        tracker: Usage tracker instance
        app_id: Application ID

    Returns:
        Usage analysis
    """
    summary = tracker.get_usage_summary(app_id)
    inactive = tracker.get_inactive_users(app_id, days=30)
    never_used = tracker.get_never_used_licenses(app_id)
    reclamation = tracker.get_reclamation_candidates(app_id, inactivity_days=60)
    engagement = tracker.get_engagement_trends(app_id)

    return {
        "summary": summary,
        "inactive_count": len(inactive),
        "never_used_count": len(never_used),
        "reclamation_candidates": len(reclamation),
        "engagement": engagement,
        "recommendations": _generate_usage_recommendations(
            summary, len(inactive), len(never_used), engagement
        ),
    }


def _generate_usage_recommendations(
    summary: Dict[str, Any],
    inactive_count: int,
    never_used_count: int,
    engagement: Dict[str, Any],
) -> List[str]:
    """Generate usage-based recommendations."""
    recommendations = []

    total_users = summary.get("total_users", 0)

    if never_used_count > 0:
        recommendations.append(
            f"Reclaim {never_used_count} never-used licenses"
        )

    if inactive_count > total_users * 0.2:  # More than 20% inactive
        recommendations.append(
            f"Review {inactive_count} inactive users for license reclamation"
        )

    engagement_score = engagement.get("engagement_score", 0)

    if engagement_score < 40:
        recommendations.append(
            "Low engagement detected - consider user training or alternative tools"
        )
    elif engagement_score < 70:
        recommendations.append(
            "Medium engagement - identify and address adoption barriers"
        )

    if not recommendations:
        recommendations.append("Usage patterns are healthy - no immediate actions needed")

    return recommendations
