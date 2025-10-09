"""
Tests for Virtual Tagger
=========================

Test virtual tag inference without physical tags.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.tagging import VirtualTagger, VirtualTag


@pytest.fixture
def tagger():
    """Create VirtualTagger instance."""
    return VirtualTagger()


@pytest.fixture
def resources_with_parent():
    """Create resources with parent relationships."""
    return [
        {
            "id": "vpc-123",
            "type": "vpc",
            "name": "production-vpc",
            "tags": {"team": "platform", "cost_center": "eng-001"},
        },
        {
            "id": "i-456",
            "type": "ec2",
            "name": "web-server-1",
            "parent_id": "vpc-123",
            "tags": {},
        },
        {
            "id": "i-789",
            "type": "ec2",
            "name": "api-server-1",
            "parent_id": "vpc-123",
            "tags": {},
        },
    ]


class TestVirtualTagger:
    """Test VirtualTagger class."""

    def test_initialization(self, tagger):
        """Test tagger initialization."""
        assert tagger is not None
        assert len(tagger._inference_rules) > 0  # Has default rules

    def test_infer_environment_from_name(self, tagger):
        """Test inferring environment tag from resource name."""
        resource = {"id": "i-123", "name": "prod-web-server-1", "type": "ec2"}

        virtual_tags = tagger.infer_tags(resource)

        assert len(virtual_tags) > 0
        env_tags = [vt for vt in virtual_tags if vt.key == "environment"]
        assert len(env_tags) > 0
        assert env_tags[0].value == "production"
        assert env_tags[0].confidence >= 0.8

    def test_infer_staging_environment(self, tagger):
        """Test inferring staging environment."""
        resource = {"id": "i-456", "name": "staging-api-service"}

        virtual_tags = tagger.infer_tags(resource)

        env_tags = [vt for vt in virtual_tags if vt.key == "environment"]
        assert len(env_tags) > 0
        assert env_tags[0].value == "staging"

    def test_infer_dev_environment(self, tagger):
        """Test inferring development environment."""
        resource = {"id": "i-789", "name": "dev-database"}

        virtual_tags = tagger.infer_tags(resource)

        env_tags = [vt for vt in virtual_tags if vt.key == "environment"]
        assert len(env_tags) > 0
        assert env_tags[0].value == "development"

    def test_regex_inference_method(self, tagger):
        """Test that regex inference sets correct method."""
        resource = {"id": "i-123", "name": "prod-server"}

        virtual_tags = tagger.infer_tags(resource)

        for vtag in virtual_tags:
            assert vtag.inference_method == "regex_pattern"
            assert "pattern" in vtag.metadata
            assert "matched_text" in vtag.metadata

    def test_confidence_scores_valid(self, tagger):
        """Test that confidence scores are valid."""
        resource = {"id": "i-123", "name": "prod-web-server"}

        virtual_tags = tagger.infer_tags(resource)

        for vtag in virtual_tags:
            assert 0.0 <= vtag.confidence <= 1.0
            assert vtag.resource_id == "i-123"

    def test_add_custom_inference_rule(self, tagger):
        """Test adding a custom inference rule."""
        initial_count = len(tagger._inference_rules)

        tagger.add_inference_rule(
            {
                "name": "application_inference",
                "method": "regex",
                "patterns": {
                    "application": [
                        (r"myapp", "my-application"),
                    ]
                },
                "confidence": 0.95,
            }
        )

        assert len(tagger._inference_rules) == initial_count + 1

        # Test that new rule works
        resource = {"id": "i-123", "name": "prod-myapp-server"}
        virtual_tags = tagger.infer_tags(resource)

        app_tags = [vt for vt in virtual_tags if vt.key == "application"]
        assert len(app_tags) > 0
        assert app_tags[0].value == "my-application"
        assert app_tags[0].confidence == 0.95

    def test_infer_from_relationship(self, tagger):
        """Test tag inference from parent resource."""
        parent = {
            "id": "vpc-123",
            "tags": {"team": "platform", "cost_center": "eng-001"},
        }

        child = {"id": "i-456", "name": "web-server", "parent_id": "vpc-123", "tags": {}}

        context = {"parent_id": "vpc-123", "parent_tags": parent["tags"]}

        virtual_tags = tagger.infer_tags(child, context=context)

        # Should have inherited tags
        team_tags = [vt for vt in virtual_tags if vt.key == "team"]
        cost_center_tags = [vt for vt in virtual_tags if vt.key == "cost_center"]

        assert len(team_tags) > 0
        assert team_tags[0].value == "platform"
        assert team_tags[0].inference_method == "relationship"

        assert len(cost_center_tags) > 0
        assert cost_center_tags[0].value == "eng-001"

    def test_relationship_metadata(self, tagger):
        """Test that relationship inference includes proper metadata."""
        context = {
            "parent_id": "vpc-123",
            "parent_tags": {"team": "platform"},
        }

        child = {"id": "i-456", "parent_id": "vpc-123"}

        virtual_tags = tagger.infer_tags(child, context=context)

        team_tags = [vt for vt in virtual_tags if vt.key == "team"]
        if team_tags:
            tag = team_tags[0]
            assert "parent_id" in tag.metadata
            assert tag.metadata["parent_id"] == "vpc-123"
            assert "inherited_from" in tag.metadata

    def test_get_virtual_tags(self, tagger):
        """Test getting virtual tags as dict."""
        resource = {"id": "i-123", "name": "prod-web-server"}
        tagger.infer_tags(resource)

        virtual_tags_dict = tagger.get_virtual_tags("i-123")

        assert isinstance(virtual_tags_dict, dict)
        assert "environment" in virtual_tags_dict
        assert virtual_tags_dict["environment"] == "production"

    def test_get_virtual_tags_with_min_confidence(self, tagger):
        """Test filtering virtual tags by confidence."""
        resource = {"id": "i-123", "name": "prod-server"}
        tagger.infer_tags(resource)

        # High confidence threshold - should return tags
        high_conf_tags = tagger.get_virtual_tags("i-123", min_confidence=0.5)
        assert len(high_conf_tags) > 0

        # Very high threshold - may filter some out
        very_high_conf_tags = tagger.get_virtual_tags("i-123", min_confidence=0.99)
        assert len(very_high_conf_tags) <= len(high_conf_tags)

    def test_bulk_infer(self, tagger, resources_with_parent):
        """Test bulk inference across multiple resources."""
        results = tagger.bulk_infer(resources_with_parent, build_relationships=True)

        # Should have results for all resources
        assert len(results) == 3

        # VPC should have tags from name
        assert "vpc-123" in results

        # EC2 instances should have inherited tags
        assert "i-456" in results
        instance_tags = results["i-456"]

        # Check for inherited tags
        team_tags = [vt for vt in instance_tags if vt.key == "team"]
        if team_tags:
            assert team_tags[0].value == "platform"

    def test_bulk_infer_builds_relationships(self, tagger):
        """Test that bulk_infer builds relationship graph."""
        resources = [
            {"id": "parent-1", "tags": {"environment": "production"}},
            {"id": "child-1", "parent_id": "parent-1", "tags": {}},
            {"id": "child-2", "parent_id": "parent-1", "tags": {}},
        ]

        tagger.bulk_infer(resources, build_relationships=True)

        # Check relationship graph was built
        assert "parent-1" in tagger._resource_relationships
        assert "child-1" in tagger._resource_relationships["parent-1"]
        assert "child-2" in tagger._resource_relationships["parent-1"]

    def test_get_tagging_suggestions(self, tagger):
        """Test getting suggestions for physical tagging."""
        resource = {"id": "i-123", "name": "prod-web-server"}
        tagger.infer_tags(resource)

        existing_tags = {"owner": "alice"}
        suggestions = tagger.get_tagging_suggestions("i-123", existing_tags)

        # Should suggest environment (not in existing tags)
        assert len(suggestions) > 0
        assert any(s["key"] == "environment" for s in suggestions)

        # Suggestions should have confidence and reason
        for suggestion in suggestions:
            assert "key" in suggestion
            assert "value" in suggestion
            assert "confidence" in suggestion
            assert "reason" in suggestion

    def test_suggestions_skip_existing_tags(self, tagger):
        """Test that suggestions skip already-tagged keys."""
        resource = {"id": "i-123", "name": "prod-server"}
        tagger.infer_tags(resource)

        existing_tags = {"environment": "staging"}  # Already tagged
        suggestions = tagger.get_tagging_suggestions("i-123", existing_tags)

        # Should not suggest environment since it exists
        assert not any(s["key"] == "environment" for s in suggestions)

    def test_suggestions_sorted_by_confidence(self, tagger):
        """Test that suggestions are sorted by confidence."""
        # Add multiple rules with different confidence
        tagger.add_inference_rule(
            {
                "name": "low_confidence",
                "method": "regex",
                "patterns": {"tag1": [(r"server", "value1")]},
                "confidence": 0.5,
            }
        )

        tagger.add_inference_rule(
            {
                "name": "high_confidence",
                "method": "regex",
                "patterns": {"tag2": [(r"server", "value2")]},
                "confidence": 0.95,
            }
        )

        resource = {"id": "i-123", "name": "my-server"}
        tagger.infer_tags(resource)

        suggestions = tagger.get_tagging_suggestions("i-123", {})

        # Should be sorted by confidence descending
        if len(suggestions) >= 2:
            assert suggestions[0]["confidence"] >= suggestions[1]["confidence"]

    def test_get_inference_coverage(self, tagger):
        """Test calculating inference coverage metrics."""
        resources = [
            {"id": "i-1", "name": "prod-web-server"},
            {"id": "i-2", "name": "staging-api-service"},
            {"id": "i-3", "name": "unknown-resource"},
        ]

        # Infer for all resources
        for resource in resources:
            tagger.infer_tags(resource)

        coverage = tagger.get_inference_coverage(
            resources, required_tags=["environment", "team"]
        )

        assert "total_resources" in coverage
        assert coverage["total_resources"] == 3

        assert "overall_coverage" in coverage
        assert "by_tag" in coverage
        assert "tag_counts" in coverage

        # Should have coverage for environment (prod, staging detected)
        assert "environment" in coverage["by_tag"]
        assert coverage["by_tag"]["environment"] >= 0

    def test_coverage_with_no_resources(self, tagger):
        """Test coverage calculation with empty resource list."""
        coverage = tagger.get_inference_coverage([], required_tags=["environment"])

        assert coverage["coverage"] == 0

    def test_clear_virtual_tags(self, tagger):
        """Test clearing all virtual tags."""
        resource = {"id": "i-123", "name": "prod-server"}
        tagger.infer_tags(resource)

        assert len(tagger._virtual_tags) > 0

        tagger.clear()

        assert len(tagger._virtual_tags) == 0
        assert len(tagger._resource_relationships) == 0

    def test_case_insensitive_matching(self, tagger):
        """Test that pattern matching is case-insensitive."""
        resources = [
            {"id": "1", "name": "PROD-server"},
            {"id": "2", "name": "Prod-server"},
            {"id": "3", "name": "prod-server"},
        ]

        for resource in resources:
            virtual_tags = tagger.infer_tags(resource)
            env_tags = [vt for vt in virtual_tags if vt.key == "environment"]
            assert len(env_tags) > 0
            assert env_tags[0].value == "production"

    def test_multiple_patterns_same_resource(self, tagger):
        """Test that multiple patterns can match the same resource."""
        # Resource name could match multiple patterns
        resource = {"id": "i-123", "name": "prod-api-server"}

        virtual_tags = tagger.infer_tags(resource)

        # Should have environment from prod
        env_tags = [vt for vt in virtual_tags if vt.key == "environment"]
        assert len(env_tags) > 0

    def test_deduplicate_same_tag_key(self, tagger):
        """Test that get_virtual_tags deduplicates same keys by confidence."""
        # Add two rules that both infer same tag with different confidence
        tagger.add_inference_rule(
            {
                "name": "rule1",
                "method": "regex",
                "patterns": {"team": [(r"web", "frontend")]},
                "confidence": 0.7,
            }
        )

        tagger.add_inference_rule(
            {
                "name": "rule2",
                "method": "regex",
                "patterns": {"team": [(r"web", "backend")]},
                "confidence": 0.9,
            }
        )

        resource = {"id": "i-123", "name": "web-server"}
        tagger.infer_tags(resource)

        virtual_tags_dict = tagger.get_virtual_tags("i-123")

        # Should only have one "team" tag (highest confidence)
        assert "team" in virtual_tags_dict
        # Should use the higher confidence value
        assert virtual_tags_dict["team"] == "backend"


class TestVirtualTag:
    """Test VirtualTag dataclass."""

    def test_virtual_tag_creation(self):
        """Test creating a virtual tag."""
        tag = VirtualTag(
            key="environment",
            value="production",
            resource_id="i-123",
            confidence=0.90,
            inference_method="regex_pattern",
            metadata={"pattern": r"^prod-"},
        )

        assert tag.key == "environment"
        assert tag.value == "production"
        assert tag.resource_id == "i-123"
        assert tag.confidence == 0.90
        assert tag.inference_method == "regex_pattern"
        assert "pattern" in tag.metadata

    def test_virtual_tag_default_metadata(self):
        """Test that metadata defaults to empty dict."""
        tag = VirtualTag(
            key="team",
            value="platform",
            resource_id="i-456",
            confidence=0.85,
            inference_method="relationship",
        )

        assert tag.metadata == {}


class TestInferenceRules:
    """Test inference rule system."""

    def test_default_rules_exist(self, tagger):
        """Test that default inference rules are loaded."""
        assert len(tagger._inference_rules) > 0

        # Should have environment inference rule
        env_rule = next(
            (r for r in tagger._inference_rules if r.get("name") == "environment_from_name"),
            None,
        )
        assert env_rule is not None
        assert env_rule["method"] == "regex"

    def test_regex_rule_structure(self, tagger):
        """Test that regex rules have proper structure."""
        tagger.add_inference_rule(
            {
                "name": "test_rule",
                "method": "regex",
                "patterns": {
                    "test_tag": [
                        (r"test", "test_value"),
                    ]
                },
                "confidence": 0.85,
            }
        )

        resource = {"id": "i-123", "name": "test-resource"}
        virtual_tags = tagger.infer_tags(resource)

        test_tags = [vt for vt in virtual_tags if vt.key == "test_tag"]
        assert len(test_tags) > 0

    def test_relationship_rule_structure(self, tagger):
        """Test relationship-based inference rule."""
        # Default relationship rule should exist
        rel_rule = next(
            (r for r in tagger._inference_rules if r.get("method") == "relationship"),
            None,
        )

        assert rel_rule is not None
        assert "inherit_tags" in rel_rule

    def test_rule_without_method(self, tagger):
        """Test that rules without method don't crash."""
        tagger.add_inference_rule(
            {
                "name": "invalid_rule",
                # No method specified
                "confidence": 0.5,
            }
        )

        resource = {"id": "i-123", "name": "test"}
        # Should not raise exception
        virtual_tags = tagger.infer_tags(resource)
        assert isinstance(virtual_tags, list)


class TestIntegration:
    """Integration tests for virtual tagging."""

    def test_complete_workflow(self, tagger):
        """Test complete virtual tagging workflow."""
        # Setup: Add custom rule
        tagger.add_inference_rule(
            {
                "name": "service_inference",
                "method": "regex",
                "patterns": {
                    "service": [
                        (r"web", "web-service"),
                        (r"api", "api-service"),
                    ]
                },
                "confidence": 0.85,
            }
        )

        # Infer tags
        resource = {"id": "i-123", "name": "prod-web-server-1"}
        virtual_tags = tagger.infer_tags(resource)

        # Should have environment and service
        keys = {vt.key for vt in virtual_tags}
        assert "environment" in keys
        assert "service" in keys

        # Get as dict
        tags_dict = tagger.get_virtual_tags("i-123")
        assert tags_dict["environment"] == "production"
        assert tags_dict["service"] == "web-service"

        # Get suggestions
        suggestions = tagger.get_tagging_suggestions("i-123", {})
        assert len(suggestions) >= 2

    def test_hierarchy_with_bulk_infer(self, tagger):
        """Test inferring tags across resource hierarchy."""
        resources = [
            {
                "id": "vpc-1",
                "name": "prod-vpc",
                "tags": {"cost_center": "eng-001", "project": "platform"},
            },
            {"id": "i-1", "name": "web-1", "parent_id": "vpc-1", "tags": {}},
            {"id": "i-2", "name": "api-1", "parent_id": "vpc-1", "tags": {}},
        ]

        results = tagger.bulk_infer(resources, build_relationships=True)

        # VPC should have environment from name
        vpc_tags = [vt for vt in results["vpc-1"] if vt.key == "environment"]
        assert len(vpc_tags) > 0

        # Instances should have inherited tags
        i1_tags = results["i-1"]
        i1_keys = {vt.key for vt in i1_tags}

        # Should have cost_center and project from parent
        assert "cost_center" in i1_keys or "project" in i1_keys

    def test_coverage_improves_with_inference(self, tagger):
        """Test that virtual tagging improves tag coverage."""
        resources = [
            {"id": "i-1", "name": "prod-server", "tags": {}},  # Untagged
            {"id": "i-2", "name": "staging-server", "tags": {}},  # Untagged
            {"id": "i-3", "name": "dev-server", "tags": {}},  # Untagged
        ]

        # Without inference, coverage would be 0%
        # With inference, coverage should improve

        # Infer tags
        for resource in resources:
            tagger.infer_tags(resource)

        coverage = tagger.get_inference_coverage(
            resources, required_tags=["environment"]
        )

        # Should have some coverage from name-based inference
        assert coverage["by_tag"]["environment"] > 0
        assert coverage["tag_counts"]["environment"] >= 2  # At least 2/3
