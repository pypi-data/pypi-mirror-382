"""
Unit tests for Dashboard components.
"""

import pytest
from openfinops.dashboard.cfo_dashboard import CFODashboard
from openfinops.dashboard.coo_dashboard import COODashboard
from openfinops.dashboard.infrastructure_leader_dashboard import InfrastructureLeaderDashboard
from openfinops.dashboard.finance_analyst_dashboard import FinanceAnalystDashboard


@pytest.mark.unit
class TestCFODashboard:
    """Test suite for CFO Dashboard."""

    def test_initialization(self):
        """Test CFODashboard initialization."""
        dashboard = CFODashboard()
        assert dashboard is not None
        assert hasattr(dashboard, 'generate_dashboard')

    def test_generate_dashboard(self):
        """Test dashboard generation."""
        dashboard = CFODashboard()
        result = dashboard.generate_dashboard(
            user_id="test-cfo-001",
            time_period="current_month"
        )

        assert result is not None
        assert isinstance(result, dict)
        # CFO dashboard includes comprehensive financial sections
        assert len(result) > 0  # Has content
        assert any(key in result for key in ['metadata', 'budget_performance', 'ai_cost_analytics'])

    def test_dashboard_with_different_periods(self):
        """Test dashboard with different time periods."""
        dashboard = CFODashboard()

        periods = ["current_month", "current_quarter", "current_year"]
        for period in periods:
            result = dashboard.generate_dashboard(
                user_id="test-cfo-001",
                time_period=period
            )
            assert result is not None
            assert isinstance(result, dict)

    def test_dashboard_data_structure(self):
        """Test dashboard output data structure."""
        dashboard = CFODashboard()
        result = dashboard.generate_dashboard(
            user_id="test-cfo-001",
            time_period="current_month"
        )

        # Verify dashboard returns comprehensive financial data
        assert isinstance(result, dict)
        assert len(result) > 0
        # CFO dashboard has specific financial sections
        expected_sections = ['budget_performance', 'ai_cost_analytics', 'compliance_status', 'board_highlights']
        assert any(section in result for section in expected_sections)


@pytest.mark.unit
class TestCOODashboard:
    """Test suite for COO Dashboard."""

    def test_initialization(self):
        """Test COODashboard initialization."""
        dashboard = COODashboard()
        assert dashboard is not None
        assert hasattr(dashboard, 'generate_dashboard')

    def test_generate_dashboard(self):
        """Test COO dashboard generation."""
        dashboard = COODashboard()
        result = dashboard.generate_dashboard(
            user_id="test-coo-001",
            time_period="current_month",
            focus_area="operations"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert len(result) > 0  # Has content
        # COO dashboard includes operational sections
        assert any(key in result for key in ['metadata', 'operational_metrics', 'efficiency_analysis'])

    def test_dashboard_focus_areas(self):
        """Test dashboard with different focus areas."""
        dashboard = COODashboard()

        focus_areas = ["operations", "efficiency", "quality"]
        for area in focus_areas:
            result = dashboard.generate_dashboard(
                user_id="test-coo-001",
                time_period="current_month",
                focus_area=area
            )
            assert result is not None
            assert isinstance(result, dict)


@pytest.mark.unit
class TestInfrastructureLeaderDashboard:
    """Test suite for Infrastructure Leader Dashboard."""

    def test_initialization(self):
        """Test InfrastructureLeaderDashboard initialization."""
        dashboard = InfrastructureLeaderDashboard()
        assert dashboard is not None
        assert hasattr(dashboard, 'generate_dashboard')

    def test_generate_dashboard(self):
        """Test infrastructure dashboard generation."""
        dashboard = InfrastructureLeaderDashboard()
        result = dashboard.generate_dashboard(
            user_id="test-infra-001",
            time_period="current_hour",
            focus_area="overview"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert len(result) > 0  # Has content
        # Infrastructure dashboard includes system sections
        assert any(key in result for key in ['metadata', 'system_health', 'infrastructure_overview'])

    def test_dashboard_cluster_filters(self):
        """Test dashboard with different focus areas."""
        dashboard = InfrastructureLeaderDashboard()

        focus_areas = ["overview", "compute", "storage"]
        for focus_area in focus_areas:
            result = dashboard.generate_dashboard(
                user_id="test-infra-001",
                time_period="current_hour",
                focus_area=focus_area
            )
            assert result is not None
            assert isinstance(result, dict)


@pytest.mark.unit
class TestFinanceAnalystDashboard:
    """Test suite for Finance Analyst Dashboard."""

    def test_initialization(self):
        """Test FinanceAnalystDashboard initialization."""
        dashboard = FinanceAnalystDashboard()
        assert dashboard is not None
        assert hasattr(dashboard, 'generate_dashboard')

    def test_generate_dashboard(self):
        """Test finance analyst dashboard generation."""
        dashboard = FinanceAnalystDashboard()
        result = dashboard.generate_dashboard(
            user_id="test-analyst-001",
            time_period="current_month",
            analysis_type="cost_analysis"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert len(result) > 0  # Has content
        # Finance analyst dashboard includes analytical sections
        assert any(key in result for key in ['metadata', 'cost_analysis', 'financial_metrics'])

    def test_dashboard_analysis_types(self):
        """Test dashboard with different analysis types."""
        dashboard = FinanceAnalystDashboard()

        types = ["cost_analysis", "budget_analysis", "forecast_analysis"]
        for analysis_type in types:
            result = dashboard.generate_dashboard(
                user_id="test-analyst-001",
                time_period="current_month",
                analysis_type=analysis_type
            )
            assert result is not None
            assert isinstance(result, dict)


@pytest.mark.unit
class TestDashboardIntegration:
    """Integration tests for dashboards."""

    def test_all_dashboards_initialize(self):
        """Test that all dashboards can be initialized together."""
        cfo = CFODashboard()
        coo = COODashboard()
        infra = InfrastructureLeaderDashboard()
        finance = FinanceAnalystDashboard()

        assert cfo is not None
        assert coo is not None
        assert infra is not None
        assert finance is not None

    def test_dashboard_data_generation(self):
        """Test dashboard data generation across all types."""
        time_period = "current_month"

        # Test CFO dashboard with CFO user
        cfo = CFODashboard()
        cfo_data = cfo.generate_dashboard("test-cfo-001", time_period)
        assert cfo_data is not None
        assert len(cfo_data) > 0  # Has content

        # Test Finance dashboard with analyst user
        finance = FinanceAnalystDashboard()
        finance_data = finance.generate_dashboard(
            "test-analyst-001", time_period, "cost_analysis"
        )
        assert finance_data is not None
        assert len(finance_data) > 0  # Has content

    @pytest.mark.parametrize("dashboard_class", [
        CFODashboard,
        COODashboard,
        InfrastructureLeaderDashboard,
        FinanceAnalystDashboard,
    ])
    def test_dashboard_types(self, dashboard_class):
        """Test different dashboard types."""
        dashboard = dashboard_class()
        assert dashboard is not None
        assert hasattr(dashboard, 'generate_dashboard')
