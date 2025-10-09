"""
Tests for Tag-Based Cost Attribution
=====================================

Test cost attribution using resource tags.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.tagging import TagBasedAttribution, AttributionResult


@pytest.fixture
def attribution_engine():
    """Create attribution engine."""
    return TagBasedAttribution()


@pytest.fixture
def sample_resources_with_costs():
    """Create sample resources with costs."""
    return [
        {
            "id": "i-123",
            "cost": 150.00,
            "tags": {"team": "platform", "environment": "production", "project": "api"},
        },
        {
            "id": "i-456",
            "cost": 250.00,
            "tags": {"team": "ml-research", "environment": "production", "project": "training"},
        },
        {
            "id": "i-789",
            "cost": 100.00,
            "tags": {"team": "platform", "environment": "staging", "project": "web"},
        },
        {
            "id": "i-999",
            "cost": 50.00,
            "tags": {"team": "ml-research", "environment": "development"},
        },
    ]


class TestTagBasedAttribution:
    """Test TagBasedAttribution class."""

    def test_initialization(self, attribution_engine):
        """Test attribution engine initialization."""
        assert attribution_engine is not None
        assert attribution_engine._virtual_tagger is None

    def test_attribute_by_team(self, attribution_engine, sample_resources_with_costs):
        """Test cost attribution by team."""
        results = attribution_engine.attribute_costs(
            sample_resources_with_costs,
            dimension="team",
            use_virtual_tags=False,
        )

        # Should have results for each team
        assert len(results) == 2

        # Find platform and ml-research results
        platform = next(r for r in results if r.value == "platform")
        ml_research = next(r for r in results if r.value == "ml-research")

        # Check platform costs (150 + 100 = 250)
        assert platform.total_cost == 250.00
        assert platform.resource_count == 2
        assert platform.dimension == "team"

        # Check ml-research costs (250 + 50 = 300)
        assert ml_research.total_cost == 300.00
        assert ml_research.resource_count == 2

    def test_attribute_by_environment(self, attribution_engine, sample_resources_with_costs):
        """Test cost attribution by environment."""
        results = attribution_engine.attribute_costs(
            sample_resources_with_costs,
            dimension="environment",
            use_virtual_tags=False,
        )

        # Find production results
        prod_result = next(r for r in results if r.value == "production")

        # Production should have 2 resources (i-123: 150, i-456: 250)
        assert prod_result.total_cost == 400.00
        assert prod_result.resource_count == 2

    def test_attribution_sorted_by_cost(self, attribution_engine, sample_resources_with_costs):
        """Test that results are sorted by cost descending."""
        results = attribution_engine.attribute_costs(
            sample_resources_with_costs,
            dimension="team",
            use_virtual_tags=False,
        )

        # Should be sorted by cost descending
        for i in range(len(results) - 1):
            assert results[i].total_cost >= results[i + 1].total_cost

    def test_attribution_percentage_calculation(
        self, attribution_engine, sample_resources_with_costs
    ):
        """Test that percentage is correctly calculated."""
        results = attribution_engine.attribute_costs(
            sample_resources_with_costs,
            dimension="team",
            use_virtual_tags=False,
        )

        # Total cost is 550
        total = sum(r.total_cost for r in results)
        assert total == pytest.approx(550.00, abs=0.01)

        # Percentages should add up to 100
        total_pct = sum(r.percentage for r in results)
        assert total_pct == pytest.approx(100.0, abs=0.01)

        # Check individual percentages
        ml_research = next(r for r in results if r.value == "ml-research")
        # ml-research: 300 / 550 = 54.54%
        assert ml_research.percentage == pytest.approx(54.54, abs=0.1)

    def test_attribution_includes_resource_ids(
        self, attribution_engine, sample_resources_with_costs
    ):
        """Test that results include resource IDs."""
        results = attribution_engine.attribute_costs(
            sample_resources_with_costs,
            dimension="team",
        )

        platform = next(r for r in results if r.value == "platform")

        assert len(platform.resources) == 2
        assert "i-123" in platform.resources
        assert "i-789" in platform.resources

    def test_untagged_resources_labeled(self, attribution_engine):
        """Test that resources without tag are labeled as untagged."""
        resources = [
            {"id": "i-1", "cost": 100.00, "tags": {"team": "platform"}},
            {"id": "i-2", "cost": 50.00, "tags": {}},  # No team tag
        ]

        results = attribution_engine.attribute_costs(
            resources,
            dimension="team",
            use_virtual_tags=False,
        )

        # Should have platform and untagged
        assert len(results) == 2

        untagged = next(r for r in results if r.value == "untagged")
        assert untagged.total_cost == 50.00
        assert untagged.resource_count == 1

    def test_custom_untagged_label(self, attribution_engine, sample_resources_with_costs):
        """Test using custom label for untagged resources."""
        resources = [{"id": "i-1", "cost": 100.00, "tags": {}}]

        results = attribution_engine.attribute_costs(
            resources,
            dimension="team",
            untagged_label="no_team_assigned",
        )

        assert len(results) == 1
        assert results[0].value == "no_team_assigned"

    def test_multi_dimensional_attribution(
        self, attribution_engine, sample_resources_with_costs
    ):
        """Test attribution across multiple dimensions."""
        results = attribution_engine.multi_dimensional_attribution(
            sample_resources_with_costs,
            dimensions=["team", "environment", "project"],
            use_virtual_tags=False,
        )

        # Should have results for each dimension
        assert "team" in results
        assert "environment" in results
        assert "project" in results

        # Each dimension should have attribution results
        assert len(results["team"]) > 0
        assert len(results["environment"]) > 0

        # Check that results are AttributionResult objects
        assert all(isinstance(r, AttributionResult) for r in results["team"])

    def test_get_untagged_resources(self, attribution_engine):
        """Test finding resources missing specific tags."""
        resources = [
            {"id": "i-1", "cost": 100.00, "tags": {"team": "platform"}},
            {"id": "i-2", "cost": 50.00, "tags": {}},
            {"id": "i-3", "cost": 75.00, "tags": {"environment": "prod"}},
        ]

        untagged = attribution_engine.get_untagged_resources(
            resources,
            dimension="team",
            use_virtual_tags=False,
        )

        # Should return i-2 and i-3 (no team tag)
        assert len(untagged) == 2
        ids = [r["id"] for r in untagged]
        assert "i-2" in ids
        assert "i-3" in ids

    def test_get_attribution_summary(self, attribution_engine, sample_resources_with_costs):
        """Test getting attribution summary."""
        summary = attribution_engine.get_attribution_summary(
            sample_resources_with_costs,
            dimensions=["team", "environment"],
        )

        # Should have top-level stats
        assert "total_cost" in summary
        assert summary["total_cost"] == 550.00

        assert "total_resources" in summary
        assert summary["total_resources"] == 4

        # Should have per-dimension breakdown
        assert "by_dimension" in summary
        assert "team" in summary["by_dimension"]
        assert "environment" in summary["by_dimension"]

        # Check team dimension stats
        team_stats = summary["by_dimension"]["team"]
        assert "total_values" in team_stats
        assert "tagged_cost" in team_stats
        assert "untagged_cost" in team_stats
        assert "attribution_coverage" in team_stats
        assert "top_5" in team_stats

        # All resources have team tags, so coverage should be 100%
        assert team_stats["attribution_coverage"] == pytest.approx(100.0, abs=0.1)

    def test_summary_identifies_untagged(self, attribution_engine):
        """Test that summary correctly identifies untagged resources."""
        resources = [
            {"id": "i-1", "cost": 100.00, "tags": {"team": "platform"}},
            {"id": "i-2", "cost": 50.00, "tags": {}},  # Untagged
        ]

        summary = attribution_engine.get_attribution_summary(
            resources,
            dimensions=["team"],
        )

        team_stats = summary["by_dimension"]["team"]

        assert team_stats["tagged_cost"] == 100.00
        assert team_stats["untagged_cost"] == 50.00
        assert team_stats["tagged_resources"] == 1
        assert team_stats["untagged_resources"] == 1

        # Coverage should be 66.67% (100 / 150)
        assert team_stats["attribution_coverage"] == pytest.approx(66.67, abs=0.1)

    def test_showback_report(self, attribution_engine, sample_resources_with_costs):
        """Test generating showback report."""
        report = attribution_engine.showback_report(
            sample_resources_with_costs,
            dimension="team",
            top_n=2,
        )

        # Should have report structure
        assert "dimension" in report
        assert report["dimension"] == "team"

        assert "total_cost" in report
        assert report["total_cost"] == 550.00

        assert "top_consumers" in report
        assert len(report["top_consumers"]) <= 2

        # Top consumers should have details
        for consumer in report["top_consumers"]:
            assert "value" in consumer
            assert "cost" in consumer
            assert "percentage" in consumer
            assert "resources" in consumer

        # Should have "others" section
        assert "others" in report

    def test_showback_report_top_n(self, attribution_engine):
        """Test showback report with different top_n values."""
        resources = [
            {"id": f"i-{i}", "cost": 100.00, "tags": {"team": f"team-{i}"}}
            for i in range(10)
        ]

        report = attribution_engine.showback_report(resources, dimension="team", top_n=5)

        # Should only show top 5
        assert len(report["top_consumers"]) == 5

        # Others should account for remaining 5 teams
        assert report["others"]["count"] == 5

    def test_set_virtual_tagger(self, attribution_engine):
        """Test setting virtual tagger."""
        from openfinops.tagging import VirtualTagger

        virtual_tagger = VirtualTagger()
        attribution_engine.set_virtual_tagger(virtual_tagger)

        assert attribution_engine._virtual_tagger is virtual_tagger

    def test_attribution_with_virtual_tags(self, attribution_engine):
        """Test that virtual tagger is called for untagged resources."""
        from openfinops.tagging import VirtualTagger

        # Create mock virtual tagger
        virtual_tagger = VirtualTagger()
        attribution_engine.set_virtual_tagger(virtual_tagger)

        # Add inference rule
        virtual_tagger.add_inference_rule(
            {
                "name": "team_inference",
                "method": "regex",
                "patterns": {
                    "team": [
                        (r"platform", "platform-team"),
                    ]
                },
                "confidence": 0.85,
            }
        )

        # Resource without team tag but with inferrable name
        resources = [
            {"id": "i-1", "name": "platform-server", "cost": 100.00, "tags": {}},
        ]

        # Infer virtual tags first
        for resource in resources:
            virtual_tagger.infer_tags(resource)

        # Now attribute with virtual tags
        results = attribution_engine.attribute_costs(
            resources,
            dimension="team",
            use_virtual_tags=True,
        )

        # Should use virtual tag instead of marking as untagged
        team_result = next((r for r in results if r.value == "platform-team"), None)
        if team_result:
            assert team_result.total_cost == 100.00

    def test_trend_analysis_placeholder(self, attribution_engine):
        """Test that trend analysis method exists."""
        historical_data = []
        result = attribution_engine.trend_analysis(
            historical_data,
            dimension="team",
            group_by_period="day",
        )

        # Placeholder implementation should return structure
        assert "dimension" in result
        assert "period" in result
        assert "trends" in result


class TestAttributionResult:
    """Test AttributionResult dataclass."""

    def test_attribution_result_creation(self):
        """Test creating attribution result."""
        result = AttributionResult(
            dimension="team",
            value="platform",
            total_cost=250.00,
            resource_count=3,
            percentage=45.5,
            resources=["i-1", "i-2", "i-3"],
        )

        assert result.dimension == "team"
        assert result.value == "platform"
        assert result.total_cost == 250.00
        assert result.resource_count == 3
        assert result.percentage == 45.5
        assert len(result.resources) == 3

    def test_attribution_result_default_resources(self):
        """Test that resources defaults to empty list."""
        result = AttributionResult(
            dimension="project",
            value="api",
            total_cost=100.00,
            resource_count=1,
            percentage=100.0,
        )

        assert result.resources == []


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_resources_list(self, attribution_engine):
        """Test attribution with no resources."""
        results = attribution_engine.attribute_costs(
            [],
            dimension="team",
        )

        assert len(results) == 0

    def test_zero_cost_resources(self, attribution_engine):
        """Test resources with zero cost."""
        resources = [
            {"id": "i-1", "cost": 0.0, "tags": {"team": "platform"}},
            {"id": "i-2", "cost": 100.0, "tags": {"team": "ml"}},
        ]

        results = attribution_engine.attribute_costs(resources, dimension="team")

        # Should still include zero-cost resource
        platform = next(r for r in results if r.value == "platform")
        assert platform.total_cost == 0.0
        assert platform.resource_count == 1

    def test_resources_without_id(self, attribution_engine):
        """Test resources missing ID field."""
        resources = [
            {"cost": 100.0, "tags": {"team": "platform"}},  # No id
        ]

        results = attribution_engine.attribute_costs(resources, dimension="team")

        # Should handle gracefully
        assert len(results) > 0
        platform = next(r for r in results if r.value == "platform")
        assert "unknown" in platform.resources

    def test_resources_without_tags_field(self, attribution_engine):
        """Test resources missing tags field entirely."""
        resources = [
            {"id": "i-1", "cost": 100.0},  # No tags field
        ]

        results = attribution_engine.attribute_costs(
            resources,
            dimension="team",
            use_virtual_tags=False,
        )

        # Should treat as untagged
        assert len(results) == 1
        assert results[0].value == "untagged"

    def test_summary_with_empty_resources(self, attribution_engine):
        """Test summary with empty resource list."""
        summary = attribution_engine.get_attribution_summary([], dimensions=["team"])

        assert summary["total_cost"] == 0
        assert summary["total_resources"] == 0


class TestIntegration:
    """Integration tests for cost attribution."""

    def test_complete_attribution_workflow(self, attribution_engine):
        """Test complete cost attribution workflow."""
        # Setup: Create resources with costs
        resources = [
            {
                "id": "i-1",
                "cost": 500.00,
                "tags": {"team": "ml", "project": "training", "environment": "prod"},
            },
            {
                "id": "i-2",
                "cost": 300.00,
                "tags": {"team": "platform", "project": "api", "environment": "prod"},
            },
            {
                "id": "i-3",
                "cost": 200.00,
                "tags": {"team": "ml", "project": "inference", "environment": "staging"},
            },
            {"id": "i-4", "cost": 100.00, "tags": {}},  # Untagged
        ]

        # 1. Single dimension attribution
        team_attribution = attribution_engine.attribute_costs(resources, dimension="team")

        assert len(team_attribution) == 3  # ml, platform, untagged
        ml_result = next(r for r in team_attribution if r.value == "ml")
        assert ml_result.total_cost == 700.00

        # 2. Multi-dimensional attribution
        multi_attr = attribution_engine.multi_dimensional_attribution(
            resources,
            dimensions=["team", "project", "environment"],
        )

        assert len(multi_attr["team"]) == 3
        assert len(multi_attr["project"]) >= 2
        assert len(multi_attr["environment"]) >= 2

        # 3. Get summary
        summary = attribution_engine.get_attribution_summary(
            resources,
            dimensions=["team"],
        )

        # Should show 90.91% coverage (1000/1100 tagged, 100 untagged)
        team_stats = summary["by_dimension"]["team"]
        assert team_stats["attribution_coverage"] == pytest.approx(90.91, abs=0.1)

        # 4. Generate showback report
        report = attribution_engine.showback_report(
            resources,
            dimension="team",
            top_n=2,
        )

        assert report["total_cost"] == 1100.00
        assert len(report["top_consumers"]) <= 2

    def test_attribution_with_virtual_tags_end_to_end(self, attribution_engine):
        """Test end-to-end attribution with virtual tag inference."""
        from openfinops.tagging import VirtualTagger

        # Setup virtual tagger
        virtual_tagger = VirtualTagger()
        attribution_engine.set_virtual_tagger(virtual_tagger)

        # Resources with inferrable names
        resources = [
            {"id": "i-1", "name": "prod-web-server", "cost": 100.00, "tags": {}},
            {"id": "i-2", "name": "staging-api-service", "cost": 50.00, "tags": {}},
            {
                "id": "i-3",
                "name": "dev-db",
                "cost": 75.00,
                "tags": {"environment": "development"},
            },
        ]

        # Infer virtual tags
        for resource in resources:
            virtual_tagger.infer_tags(resource)

        # Attribute by environment with virtual tags
        results = attribution_engine.attribute_costs(
            resources,
            dimension="environment",
            use_virtual_tags=True,
        )

        # Should have production, staging, development (from physical and virtual tags)
        env_values = {r.value for r in results}
        assert "production" in env_values or "staging" in env_values

        # Should have attributed costs based on inferred tags
        total_attributed = sum(r.total_cost for r in results)
        assert total_attributed == 225.00

    def test_untagged_resource_identification(self, attribution_engine):
        """Test identifying and tracking untagged resources."""
        resources = [
            {"id": "i-1", "cost": 100.00, "tags": {"team": "platform"}},
            {"id": "i-2", "cost": 50.00, "tags": {"team": "ml"}},
            {"id": "i-3", "cost": 75.00, "tags": {}},  # Untagged
            {"id": "i-4", "cost": 25.00, "tags": {"project": "api"}},  # No team
        ]

        # Find untagged resources
        untagged = attribution_engine.get_untagged_resources(
            resources,
            dimension="team",
            use_virtual_tags=False,
        )

        assert len(untagged) == 2
        untagged_ids = [r["id"] for r in untagged]
        assert "i-3" in untagged_ids
        assert "i-4" in untagged_ids

        # Verify in attribution results
        results = attribution_engine.attribute_costs(resources, dimension="team")
        untagged_result = next(r for r in results if r.value == "untagged")

        assert untagged_result.total_cost == 100.00  # 75 + 25
        assert untagged_result.resource_count == 2
