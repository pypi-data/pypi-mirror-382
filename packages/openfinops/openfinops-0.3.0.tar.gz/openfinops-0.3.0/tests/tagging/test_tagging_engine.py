"""
Tests for TaggingEngine
========================

Test automated resource tagging.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.tagging import TaggingEngine, TagSuggestion


@pytest.fixture
def engine():
    """Create TaggingEngine instance."""
    return TaggingEngine()


@pytest.fixture
def prod_resources():
    """Create production resources for testing."""
    return [
        {"id": "i-123", "name": "prod-web-server-1", "type": "ec2"},
        {"id": "i-456", "name": "prod-api-service", "type": "ec2"},
        {"id": "db-789", "name": "staging-database", "type": "rds"},
    ]


class TestTaggingEngine:
    """Test TaggingEngine class."""

    def test_initialization(self, engine):
        """Test engine initialization."""
        assert engine is not None
        assert len(engine._tag_patterns) > 0  # Default patterns loaded

    def test_auto_tag_environment_from_name(self, engine):
        """Test auto-tagging environment from resource name."""
        resource = {"id": "i-123", "name": "prod-web-server-1"}
        tags = engine.auto_tag(resource)

        assert "environment" in tags
        assert tags["environment"] == "production"

    def test_auto_tag_service_from_name(self, engine):
        """Test auto-tagging service from resource name."""
        resource = {"id": "i-456", "name": "api-gateway-prod"}
        tags = engine.auto_tag(resource)

        assert "service" in tags
        assert tags["service"] == "api"

    def test_auto_tag_multiple_tags(self, engine):
        """Test extracting multiple tags at once."""
        resource = {"id": "i-789", "name": "prod-web-platform-server"}
        tags = engine.auto_tag(resource)

        assert "environment" in tags
        assert "service" in tags
        assert tags["environment"] == "production"
        assert tags["service"] == "web"

    def test_auto_tag_from_resource_type(self, engine):
        """Test tagging from resource type."""
        resource = {"id": "db-123", "name": "my-database", "type": "rds"}
        tags = engine.auto_tag(resource)

        assert "resource_type" in tags
        assert tags["resource_type"] == "database"

    def test_existing_tags_preserved(self, engine):
        """Test that existing tags are not overwritten."""
        resource = {"id": "i-123", "name": "prod-server"}
        existing = {"environment": "staging", "owner": "alice"}

        tags = engine.auto_tag(resource, existing_tags=existing)

        assert tags["environment"] == "staging"  # Existing preserved
        assert tags["owner"] == "alice"

    def test_suggest_tags(self, engine):
        """Test tag suggestions."""
        resource = {"id": "i-123", "name": "prod-web-server"}

        suggestions = engine.suggest_tags(resource)

        assert len(suggestions) > 0
        assert all(isinstance(s, TagSuggestion) for s in suggestions)

        # Should suggest environment and service
        keys = [s.key for s in suggestions]
        assert "environment" in keys
        assert "service" in keys

    def test_suggest_tags_skips_existing(self, engine):
        """Test that suggestions skip already-tagged keys."""
        resource = {"id": "i-123", "name": "prod-server"}
        existing = {"environment": "production"}

        suggestions = engine.suggest_tags(resource, existing_tags=existing)

        # Should not suggest environment since it's already tagged
        keys = [s.key for s in suggestions]
        assert "environment" not in keys

    def test_add_custom_pattern(self, engine):
        """Test adding custom tagging patterns."""
        engine.add_tag_pattern(
            "application",
            [
                (r"myapp", "my-application"),
            ],
        )

        resource = {"id": "i-123", "name": "prod-myapp-server"}
        tags = engine.auto_tag(resource)

        assert "application" in tags
        assert tags["application"] == "my-application"

    def test_set_default_tags(self, engine):
        """Test setting default tags."""
        engine.set_default_tags({"cost_center": "eng-001", "managed_by": "terraform"})

        resource = {"id": "i-123", "name": "server"}
        tags = engine.auto_tag(resource)

        assert tags["cost_center"] == "eng-001"
        assert tags["managed_by"] == "terraform"

    def test_tag_normalization(self, engine):
        """Test tag key normalization."""
        # Add tags with aliases
        tags = {"env": "production", "svc": "web"}
        normalized = engine._normalize_tags(tags)

        assert "environment" in normalized
        assert "service" in normalized
        assert normalized["environment"] == "production"

    def test_get_tag_coverage(self, engine, prod_resources):
        """Test calculating tag coverage."""
        # Add tags to resources
        prod_resources[0]["tags"] = {"environment": "production", "team": "platform"}
        prod_resources[1]["tags"] = {"environment": "production"}
        prod_resources[2]["tags"] = {}

        coverage = engine.get_tag_coverage(
            prod_resources, required_tags=["environment", "team"]
        )

        assert coverage["total_resources"] == 3
        assert coverage["fully_tagged"] == 1  # Only first resource has all tags
        assert coverage["coverage"] == pytest.approx(33.33, rel=0.1)

        # Check per-tag coverage
        assert coverage["by_tag"]["environment"]["count"] == 2
        assert coverage["by_tag"]["team"]["count"] == 1

    def test_tag_coverage_empty_resources(self, engine):
        """Test coverage with no resources."""
        coverage = engine.get_tag_coverage([], required_tags=["environment"])

        assert coverage["coverage"] == 0

    def test_confidence_scores(self, engine):
        """Test that suggestions have confidence scores."""
        resource = {"id": "i-123", "name": "prod-web-server"}
        suggestions = engine.suggest_tags(resource)

        for suggestion in suggestions:
            assert 0.0 <= suggestion.confidence <= 1.0
            assert suggestion.reason  # Has a reason
            assert suggestion.source  # Has a source

    def test_case_insensitive_patterns(self, engine):
        """Test that patterns are case-insensitive."""
        resources = [
            {"id": "1", "name": "PROD-server"},
            {"id": "2", "name": "Prod-server"},
            {"id": "3", "name": "prod-server"},
        ]

        for resource in resources:
            tags = engine.auto_tag(resource)
            assert tags.get("environment") == "production"


class TestTagSuggestion:
    """Test TagSuggestion dataclass."""

    def test_suggestion_creation(self):
        """Test creating a tag suggestion."""
        suggestion = TagSuggestion(
            key="environment",
            value="production",
            confidence=0.90,
            reason="Matched 'prod' in name",
            source="pattern",
        )

        assert suggestion.key == "environment"
        assert suggestion.value == "production"
        assert suggestion.confidence == 0.90
        assert suggestion.source == "pattern"


class TestIntegration:
    """Integration tests."""

    def test_full_tagging_workflow(self, engine):
        """Test complete tagging workflow."""
        # Setup defaults
        engine.set_default_tags({"managed_by": "openfinops"})

        # Tag a resource
        resource = {"id": "i-123", "name": "prod-web-platform-server", "type": "ec2"}
        tags = engine.auto_tag(resource)

        # Should have multiple tags
        assert "environment" in tags
        assert "service" in tags
        assert "resource_type" in tags
        assert "managed_by" in tags

        # Get suggestions for untagged dimensions
        suggestions = engine.suggest_tags(resource, existing_tags=tags)

        # Suggestions should be for missing tags only
        existing_keys = set(tags.keys())
        suggested_keys = {s.key for s in suggestions}
        assert not (existing_keys & suggested_keys)  # No overlap
