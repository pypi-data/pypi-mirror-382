"""
Tagging Engine
==============

Core engine for automated resource tagging.

Provides:
- Pattern-based tagging from resource names
- ML-based tag suggestions
- Tag normalization and validation
- Integration with tag policies
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class TagSuggestion:
    """
    Represents a suggested tag for a resource.

    Attributes:
        key: Tag key
        value: Suggested value
        confidence: Confidence score (0.0-1.0)
        reason: Why this tag was suggested
        source: Source of suggestion (pattern, ml, policy)
    """

    key: str
    value: str
    confidence: float
    reason: str
    source: str


class TaggingEngine:
    """
    Automated resource tagging engine.

    Features:
    - Pattern-based tagging from resource names
    - Tag inference from related resources
    - Tag normalization and standardization
    - Integration with tag policies
    """

    def __init__(self):
        """Initialize tagging engine."""
        self._tag_patterns: Dict[str, List[re.Pattern]] = {}
        self._tag_defaults: Dict[str, str] = {}
        self._tag_aliases: Dict[str, str] = {}  # Normalize variations
        self._policies: List[Any] = []  # TagPolicy objects

        # Initialize common patterns
        self._init_default_patterns()

    def _init_default_patterns(self):
        """Initialize default tagging patterns."""
        # Environment detection from name
        self.add_tag_pattern(
            "environment",
            [
                (r"prod[-_]", "production"),
                (r"[-_]prod[-_]", "production"),
                (r"production", "production"),
                (r"stag(e|ing)", "staging"),
                (r"dev[-_]", "development"),
                (r"[-_]dev[-_]", "development"),
                (r"test[-_]", "test"),
                (r"[-_]test[-_]", "test"),
            ],
        )

        # Service/Application detection
        self.add_tag_pattern(
            "service",
            [
                (r"web[-_]", "web"),
                (r"api[-_]", "api"),
                (r"db[-_]|database", "database"),
                (r"cache[-_]|redis", "cache"),
                (r"queue[-_]|kafka|rabbitmq", "queue"),
                (r"worker[-_]", "worker"),
                (r"batch[-_]", "batch"),
            ],
        )

        # Team/Owner detection
        self.add_tag_pattern(
            "team",
            [
                (r"[-_]platform[-_]", "platform"),
                (r"[-_]data[-_]", "data"),
                (r"[-_]ml[-_]|[-_]ai[-_]", "ml"),
                (r"[-_]infra[-_]", "infrastructure"),
                (r"[-_]security[-_]", "security"),
            ],
        )

        # Common aliases
        self._tag_aliases = {
            "env": "environment",
            "app": "application",
            "svc": "service",
            "owner": "team",
        }

    def add_tag_pattern(
        self, tag_key: str, patterns: List[tuple[str, str]]
    ):
        """
        Add tagging patterns for a key.

        Args:
            tag_key: Tag key to extract
            patterns: List of (regex_pattern, value) tuples
        """
        if tag_key not in self._tag_patterns:
            self._tag_patterns[tag_key] = []

        for pattern_str, value in patterns:
            compiled = re.compile(pattern_str, re.IGNORECASE)
            self._tag_patterns[tag_key].append((compiled, value))

    def auto_tag(
        self,
        resource: Dict[str, Any],
        existing_tags: Optional[Dict[str, str]] = None,
        suggest_only: bool = False,
    ) -> Dict[str, str]:
        """
        Automatically tag a resource.

        Args:
            resource: Resource dictionary with 'name', 'id', etc.
            existing_tags: Existing tags on the resource
            suggest_only: If True, return suggestions without applying

        Returns:
            Dictionary of tags (or suggestions)
        """
        existing_tags = existing_tags or {}
        suggestions = {}

        # Extract from resource name
        resource_name = resource.get("name", resource.get("id", ""))
        suggestions.update(self._extract_from_name(resource_name))

        # Extract from resource type
        resource_type = resource.get("type", "")
        if resource_type:
            suggestions.update(self._extract_from_type(resource_type))

        # Apply defaults for missing tags
        for key, default_value in self._tag_defaults.items():
            if key not in suggestions and key not in existing_tags:
                suggestions[key] = default_value

        # Normalize tag keys
        suggestions = self._normalize_tags(suggestions)

        # Merge with existing, preferring existing
        result = {**suggestions, **existing_tags}

        return result

    def suggest_tags(
        self, resource: Dict[str, Any], existing_tags: Optional[Dict[str, str]] = None
    ) -> List[TagSuggestion]:
        """
        Generate tag suggestions for a resource.

        Args:
            resource: Resource dictionary
            existing_tags: Existing tags on the resource

        Returns:
            List of TagSuggestion objects
        """
        existing_tags = existing_tags or {}
        suggestions = []

        resource_name = resource.get("name", resource.get("id", ""))

        # Pattern-based suggestions
        for tag_key, patterns in self._tag_patterns.items():
            if tag_key in existing_tags:
                continue  # Skip if already tagged

            for pattern, value in patterns:
                if pattern.search(resource_name):
                    suggestions.append(
                        TagSuggestion(
                            key=tag_key,
                            value=value,
                            confidence=0.85,
                            reason=f"Matched pattern in resource name: '{resource_name}'",
                            source="pattern",
                        )
                    )
                    break  # Use first match

        # Policy-based suggestions (required tags without values)
        for policy in self._policies:
            for required_tag in policy.required_tags:
                if required_tag not in existing_tags and required_tag not in [
                    s.key for s in suggestions
                ]:
                    suggestions.append(
                        TagSuggestion(
                            key=required_tag,
                            value="",  # No suggested value
                            confidence=1.0,
                            reason=f"Required by policy: {policy.name}",
                            source="policy",
                        )
                    )

        return suggestions

    def _extract_from_name(self, name: str) -> Dict[str, str]:
        """Extract tags from resource name using patterns."""
        tags = {}

        for tag_key, patterns in self._tag_patterns.items():
            for pattern, value in patterns:
                if pattern.search(name):
                    tags[tag_key] = value
                    break  # Use first match

        return tags

    def _extract_from_type(self, resource_type: str) -> Dict[str, str]:
        """Extract tags from resource type."""
        tags = {}

        # Map common resource types to tags
        type_mappings = {
            "ec2": {"resource_type": "compute"},
            "rds": {"resource_type": "database"},
            "s3": {"resource_type": "storage"},
            "lambda": {"resource_type": "serverless"},
            "eks": {"resource_type": "kubernetes"},
            "vm": {"resource_type": "compute"},
            "database": {"resource_type": "database"},
        }

        resource_type_lower = resource_type.lower()
        for type_key, type_tags in type_mappings.items():
            if type_key in resource_type_lower:
                tags.update(type_tags)
                break

        return tags

    def _normalize_tags(self, tags: Dict[str, str]) -> Dict[str, str]:
        """Normalize tag keys using aliases."""
        normalized = {}

        for key, value in tags.items():
            # Convert aliases to standard keys
            normalized_key = self._tag_aliases.get(key, key)
            normalized[normalized_key] = value

        return normalized

    def add_policy(self, policy: Any):
        """
        Add a tag policy to the engine.

        Args:
            policy: TagPolicy instance
        """
        self._policies.append(policy)
        logger.info(f"Added tag policy: {policy.name}")

    def validate_tags(
        self, tags: Dict[str, str], resource: Dict[str, Any]
    ) -> List[Any]:  # Returns TagPolicyViolation objects
        """
        Validate tags against all policies.

        Args:
            tags: Tags to validate
            resource: Resource being tagged

        Returns:
            List of policy violations
        """
        violations = []

        for policy in self._policies:
            policy_violations = policy.validate(tags, resource)
            violations.extend(policy_violations)

        return violations

    def set_default_tags(self, defaults: Dict[str, str]):
        """
        Set default tags to apply when not detected.

        Args:
            defaults: Dictionary of default tag key-value pairs
        """
        self._tag_defaults.update(defaults)

    def get_tag_coverage(
        self, resources: List[Dict[str, Any]], required_tags: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate tag coverage across resources.

        Args:
            resources: List of resources with 'tags' field
            required_tags: List of tag keys to check

        Returns:
            Dictionary with coverage statistics
        """
        total_resources = len(resources)
        if total_resources == 0:
            return {"coverage": 0, "by_tag": {}}

        tag_counts = {tag: 0 for tag in required_tags}

        for resource in resources:
            resource_tags = resource.get("tags", {})
            for tag in required_tags:
                if tag in resource_tags and resource_tags[tag]:
                    tag_counts[tag] += 1

        # Calculate percentages
        by_tag = {
            tag: {
                "count": count,
                "percentage": (count / total_resources) * 100,
                "missing": total_resources - count,
            }
            for tag, count in tag_counts.items()
        }

        # Overall coverage (resources with ALL required tags)
        fully_tagged = sum(
            1
            for resource in resources
            if all(
                tag in resource.get("tags", {}) and resource.get("tags", {})[tag]
                for tag in required_tags
            )
        )

        coverage = (fully_tagged / total_resources) * 100

        return {
            "total_resources": total_resources,
            "fully_tagged": fully_tagged,
            "coverage": coverage,
            "by_tag": by_tag,
        }
