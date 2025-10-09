"""
Tests for InsightEngine
========================

Test the core insight generation engine.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.insights.insight_engine import (
    InsightEngine,
    Insight,
    InsightPriority,
    InsightCategory,
    InsightGenerator,
)


class MockInsightGenerator(InsightGenerator):
    """Mock generator for testing."""

    def generate(self, hub, cost_obs, time_range="30d"):
        return [
            Insight(
                title="Mock Insight 1",
                description="Test insight",
                priority=InsightPriority.HIGH,
                category=InsightCategory.COST_OPTIMIZATION,
                impact="Test impact",
                recommendation="Test recommendation",
                confidence=0.9,
            ),
            Insight(
                title="Mock Insight 2",
                description="Test insight 2",
                priority=InsightPriority.LOW,
                category=InsightCategory.EFFICIENCY,
                impact="Test impact 2",
                recommendation="Test recommendation 2",
                confidence=0.85,
            ),
        ]


@pytest.fixture
def insight_engine():
    """Create InsightEngine instance."""
    engine = InsightEngine()
    # Register mock generator
    engine.register_generator("test_persona", MockInsightGenerator())
    return engine


def test_insight_creation():
    """Test creating an Insight."""
    insight = Insight(
        title="Test Insight",
        description="Test description",
        priority=InsightPriority.MEDIUM,
        category=InsightCategory.BUDGET,
        impact="Medium impact",
        recommendation="Test recommendation",
        metadata={"key": "value"},
        confidence=0.95,
    )

    assert insight.title == "Test Insight"
    assert insight.priority == InsightPriority.MEDIUM
    assert insight.category == InsightCategory.BUDGET
    assert insight.confidence == 0.95
    assert insight.metadata["key"] == "value"


def test_register_generator(insight_engine):
    """Test registering a persona generator."""
    generator = MockInsightGenerator()
    insight_engine.register_generator("new_persona", generator)

    assert "new_persona" in insight_engine._generators
    assert insight_engine._generators["new_persona"] == generator


def test_generate_insights_success(insight_engine):
    """Test generating insights for a persona."""
    insights = insight_engine.generate_insights("test_persona")

    assert len(insights) == 2
    assert insights[0].title == "Mock Insight 1"
    assert insights[0].priority == InsightPriority.HIGH
    assert insights[1].title == "Mock Insight 2"
    assert insights[1].priority == InsightPriority.LOW


def test_generate_insights_unknown_persona(insight_engine):
    """Test generating insights for unknown persona."""
    insights = insight_engine.generate_insights("unknown_persona")

    assert len(insights) == 0


def test_filter_by_priority(insight_engine):
    """Test filtering insights by minimum priority."""
    insights = insight_engine.generate_insights(
        "test_persona", min_priority=InsightPriority.HIGH
    )

    assert len(insights) == 1
    assert insights[0].priority == InsightPriority.HIGH


def test_filter_by_category(insight_engine):
    """Test filtering insights by category."""
    insights = insight_engine.generate_insights(
        "test_persona", categories=[InsightCategory.EFFICIENCY]
    )

    assert len(insights) == 1
    assert insights[0].category == InsightCategory.EFFICIENCY


def test_filter_by_priority_and_category(insight_engine):
    """Test filtering by both priority and category."""
    insights = insight_engine.generate_insights(
        "test_persona",
        min_priority=InsightPriority.MEDIUM,
        categories=[InsightCategory.COST_OPTIMIZATION],
    )

    assert len(insights) == 1
    assert insights[0].priority == InsightPriority.HIGH
    assert insights[0].category == InsightCategory.COST_OPTIMIZATION


def test_insight_priority_enum():
    """Test InsightPriority enum values."""
    assert InsightPriority.LOW.value == "low"
    assert InsightPriority.MEDIUM.value == "medium"
    assert InsightPriority.HIGH.value == "high"
    assert InsightPriority.CRITICAL.value == "critical"


def test_insight_category_enum():
    """Test InsightCategory enum values."""
    assert InsightCategory.COST_OPTIMIZATION.value == "cost_optimization"
    assert InsightCategory.EFFICIENCY.value == "efficiency"
    assert InsightCategory.BUDGET.value == "budget"
    assert InsightCategory.ANOMALY.value == "anomaly"
    assert InsightCategory.FORECAST.value == "forecast"


def test_empty_metadata():
    """Test insight with empty metadata."""
    insight = Insight(
        title="Test",
        description="Test",
        priority=InsightPriority.LOW,
        category=InsightCategory.EFFICIENCY,
        impact="Test",
        recommendation="Test",
    )

    assert insight.metadata == {}


def test_default_confidence():
    """Test default confidence value."""
    insight = Insight(
        title="Test",
        description="Test",
        priority=InsightPriority.LOW,
        category=InsightCategory.EFFICIENCY,
        impact="Test",
        recommendation="Test",
    )

    assert insight.confidence == 1.0


def test_generate_with_custom_time_range(insight_engine):
    """Test generating insights with custom time range."""
    insights = insight_engine.generate_insights("test_persona", time_range="7d")

    assert len(insights) == 2  # Should still work with different time range


def test_multiple_personas(insight_engine):
    """Test registering and using multiple personas."""
    engine = InsightEngine()

    gen1 = MockInsightGenerator()
    gen2 = MockInsightGenerator()

    engine.register_generator("persona1", gen1)
    engine.register_generator("persona2", gen2)

    insights1 = engine.generate_insights("persona1")
    insights2 = engine.generate_insights("persona2")

    assert len(insights1) == 2
    assert len(insights2) == 2
