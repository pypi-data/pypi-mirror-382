"""
Tests for Persona-Specific Insight Generators
==============================================

Test CFO, Engineer, Finance, and Business Lead insight generators.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.insights.insight_engine import InsightPriority, InsightCategory
from openfinops.insights.personas.cfo import CFOInsightGenerator
from openfinops.insights.personas.engineer import EngineerInsightGenerator
from openfinops.insights.personas.finance import FinanceInsightGenerator
from openfinops.insights.personas.business_lead import BusinessLeadInsightGenerator


@pytest.fixture
def mock_hub():
    """Mock ObservabilityHub."""
    return None  # Generators currently don't use hub data


@pytest.fixture
def mock_cost_obs():
    """Mock CostObservatory."""
    return {}  # Generators currently use mock data


class TestCFOInsightGenerator:
    """Test CFO-specific insights."""

    def test_generate_insights(self, mock_hub, mock_cost_obs):
        """Test generating CFO insights."""
        generator = CFOInsightGenerator()
        insights = generator.generate(mock_hub, mock_cost_obs)

        assert len(insights) > 0
        # CFO should get cost trends, budget, unit economics, and ROI insights
        assert len(insights) == 4

    def test_cost_trends_insight(self, mock_hub, mock_cost_obs):
        """Test cost trends analysis."""
        generator = CFOInsightGenerator()
        insights = generator._analyze_cost_trends(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Cloud Spend" in insight.title
        assert insight.priority == InsightPriority.MEDIUM
        assert insight.category == InsightCategory.COST_OPTIMIZATION
        assert "cost_change_pct" in insight.metadata
        assert insight.confidence > 0

    def test_budget_variance_insight(self, mock_hub, mock_cost_obs):
        """Test budget variance analysis."""
        generator = CFOInsightGenerator()
        insights = generator._analyze_budget_variance(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Budget" in insight.title
        assert insight.category == InsightCategory.BUDGET
        assert "budget" in insight.metadata
        assert "actual" in insight.metadata
        assert "variance_pct" in insight.metadata

    def test_unit_economics_insight(self, mock_hub, mock_cost_obs):
        """Test unit economics analysis."""
        generator = CFOInsightGenerator()
        insights = generator._analyze_unit_economics(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Unit Economics" in insight.title
        assert insight.category == InsightCategory.EFFICIENCY
        assert "cost_per_user_previous" in insight.metadata
        assert "cost_per_user_current" in insight.metadata

    def test_roi_insight(self, mock_hub, mock_cost_obs):
        """Test ROI analysis."""
        generator = CFOInsightGenerator()
        insights = generator._analyze_roi(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "ROI" in insight.title
        assert insight.priority == InsightPriority.HIGH
        assert "monthly_cost" in insight.metadata
        assert "monthly_revenue" in insight.metadata
        assert "roi_pct" in insight.metadata


class TestEngineerInsightGenerator:
    """Test Engineer-specific insights."""

    def test_generate_insights(self, mock_hub, mock_cost_obs):
        """Test generating Engineer insights."""
        generator = EngineerInsightGenerator()
        # Engineer needs hub for resource analysis
        insights = generator.generate({}, mock_cost_obs)

        # Should have insights from all analysis methods
        assert len(insights) == 4

    def test_idle_resources_insight(self, mock_hub, mock_cost_obs):
        """Test idle resource detection."""
        generator = EngineerInsightGenerator()
        insights = generator._analyze_idle_resources({}, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Idle" in insight.title
        assert insight.priority == InsightPriority.HIGH
        assert insight.category == InsightCategory.COST_OPTIMIZATION
        assert "cluster" in insight.metadata
        assert "idle_pods" in insight.metadata
        assert "daily_cost" in insight.metadata

    def test_resource_utilization_insight(self, mock_hub, mock_cost_obs):
        """Test resource utilization analysis."""
        generator = EngineerInsightGenerator()
        insights = generator._analyze_resource_utilization({}, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Database" in insight.title or "Oversized" in insight.title
        assert insight.category == InsightCategory.COST_OPTIMIZATION
        assert "current_type" in insight.metadata
        assert "recommended_type" in insight.metadata

    def test_optimization_opportunities(self, mock_hub, mock_cost_obs):
        """Test optimization opportunity detection."""
        generator = EngineerInsightGenerator()
        insights = generator._analyze_optimization_opportunities({}, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert insight.priority == InsightPriority.MEDIUM
        assert insight.category == InsightCategory.RECOMMENDATION
        assert "savings_pct" in insight.metadata or "monthly_savings" in insight.metadata

    def test_cost_spikes_insight(self, mock_hub, mock_cost_obs):
        """Test cost spike detection."""
        generator = EngineerInsightGenerator()
        insights = generator._analyze_cost_spikes(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Spike" in insight.title
        assert insight.priority == InsightPriority.CRITICAL
        assert insight.category == InsightCategory.ANOMALY
        assert "cost_increase_pct" in insight.metadata


class TestFinanceInsightGenerator:
    """Test Finance Analyst-specific insights."""

    def test_generate_insights(self, mock_hub, mock_cost_obs):
        """Test generating Finance insights."""
        generator = FinanceInsightGenerator()
        insights = generator.generate(mock_hub, mock_cost_obs)

        # Finance gets variance, forecasts, breakdown, and trends
        assert len(insights) == 4

    def test_variance_analysis(self, mock_hub, mock_cost_obs):
        """Test variance analysis."""
        generator = FinanceInsightGenerator()
        insights = generator._analyze_variance(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Variance" in insight.title
        assert insight.priority == InsightPriority.HIGH
        assert insight.category == InsightCategory.FORECAST
        assert "forecast" in insight.metadata
        assert "trending" in insight.metadata
        assert "variance_pct" in insight.metadata

    def test_forecasts(self, mock_hub, mock_cost_obs):
        """Test forecast generation."""
        generator = FinanceInsightGenerator()
        insights = generator._analyze_forecasts(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Forecast" in insight.title
        assert insight.category == InsightCategory.FORECAST
        assert "budget_monthly" in insight.metadata
        assert "forecast_eom" in insight.metadata

    def test_cost_breakdown(self, mock_hub, mock_cost_obs):
        """Test cost distribution analysis."""
        generator = FinanceInsightGenerator()
        insights = generator._analyze_cost_breakdown(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Distribution" in insight.title
        assert insight.category == InsightCategory.COST_OPTIMIZATION
        assert "aws" in insight.metadata or "azure" in insight.metadata

    def test_trends(self, mock_hub, mock_cost_obs):
        """Test trend analysis."""
        generator = FinanceInsightGenerator()
        insights = generator._analyze_trends(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Trend" in insight.title
        assert insight.category == InsightCategory.EFFICIENCY
        assert "cost_growth_qoq_pct" in insight.metadata


class TestBusinessLeadInsightGenerator:
    """Test Business Lead-specific insights."""

    def test_generate_insights(self, mock_hub, mock_cost_obs):
        """Test generating Business Lead insights."""
        generator = BusinessLeadInsightGenerator()
        insights = generator.generate(mock_hub, mock_cost_obs)

        # Business Lead gets strategic metrics, growth, and impact insights
        assert len(insights) == 3

    def test_strategic_metrics(self, mock_hub, mock_cost_obs):
        """Test strategic KPI analysis."""
        generator = BusinessLeadInsightGenerator()
        insights = generator._analyze_strategic_metrics(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Infrastructure" in insight.title or "Efficiency" in insight.title
        assert insight.priority == InsightPriority.MEDIUM
        assert insight.category == InsightCategory.EFFICIENCY
        assert "user_growth_pct" in insight.metadata
        assert "cost_growth_pct" in insight.metadata

    def test_growth_efficiency(self, mock_hub, mock_cost_obs):
        """Test growth vs scaling analysis."""
        generator = BusinessLeadInsightGenerator()
        insights = generator._analyze_growth_efficiency(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "Growth" in insight.title
        assert insight.priority == InsightPriority.HIGH
        assert "capacity_headroom_pct" in insight.metadata

    def test_business_impact(self, mock_hub, mock_cost_obs):
        """Test business impact analysis."""
        generator = BusinessLeadInsightGenerator()
        insights = generator._analyze_business_impact(mock_cost_obs, "30d")

        assert len(insights) == 1
        insight = insights[0]

        assert "ROI" in insight.title or "Infrastructure" in insight.title
        assert "annual_cost" in insight.metadata or "annual_revenue" in insight.metadata


class TestPersonaIntegration:
    """Test integration between personas."""

    def test_all_personas_produce_insights(self, mock_hub, mock_cost_obs):
        """Test that all personas generate insights."""
        personas = [
            CFOInsightGenerator(),
            EngineerInsightGenerator(),
            FinanceInsightGenerator(),
            BusinessLeadInsightGenerator(),
        ]

        for generator in personas:
            insights = generator.generate(mock_hub, mock_cost_obs)
            assert len(insights) > 0, f"{generator.__class__.__name__} produced no insights"

    def test_different_personas_different_priorities(self, mock_hub, mock_cost_obs):
        """Test that different personas prioritize differently."""
        cfo_gen = CFOInsightGenerator()
        eng_gen = EngineerInsightGenerator()

        cfo_insights = cfo_gen.generate(mock_hub, mock_cost_obs)
        eng_insights = eng_gen.generate(mock_hub, mock_cost_obs)

        # Extract priorities
        cfo_priorities = [i.priority for i in cfo_insights]
        eng_priorities = [i.priority for i in eng_insights]

        # Engineers should have at least one CRITICAL (cost spike)
        assert InsightPriority.CRITICAL in eng_priorities

        # CFO should have HIGH priority ROI insight
        assert InsightPriority.HIGH in cfo_priorities

    def test_personas_use_different_categories(self, mock_hub, mock_cost_obs):
        """Test that personas use appropriate categories."""
        cfo_gen = CFOInsightGenerator()
        eng_gen = EngineerInsightGenerator()
        fin_gen = FinanceInsightGenerator()

        cfo_insights = cfo_gen.generate(mock_hub, mock_cost_obs)
        eng_insights = eng_gen.generate(mock_hub, mock_cost_obs)
        fin_insights = fin_gen.generate(mock_hub, mock_cost_obs)

        # CFO uses BUDGET category
        cfo_categories = [i.category for i in cfo_insights]
        assert InsightCategory.BUDGET in cfo_categories

        # Engineer uses ANOMALY category
        eng_categories = [i.category for i in eng_insights]
        assert InsightCategory.ANOMALY in eng_categories

        # Finance uses FORECAST category
        fin_categories = [i.category for i in fin_insights]
        assert InsightCategory.FORECAST in fin_categories
