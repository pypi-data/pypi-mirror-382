"""
Enterprise Chart Types & Enhancements
=====================================

Business-focused chart types and enhancements for enterprise visualization
including executive dashboards, financial analytics, and compliance features.
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

import numpy as np
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle, Circle
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("Matplotlib not available for enterprise charts")

from ..charts.base import BaseChart
from ..figure import VizlyFigure
from .security import SecurityLevel, DataClassifier
from .licensing import LicenseManager, LicenseFeature, LicenseEnforcer


@dataclass
class ChartMetadata:
    """Enterprise chart metadata for governance and compliance."""
    chart_id: str
    title: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    data_sources: List[str] = field(default_factory=list)
    compliance_tags: List[str] = field(default_factory=list)
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None


class EnterpriseBaseChart(BaseChart):
    """
    Enhanced base chart with enterprise features like data governance,
    security classification, and audit trails.
    """

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)
        self.metadata = ChartMetadata(
            chart_id=f"chart_{id(self)}",
            title="Enterprise Chart",
            created_by="system"
        )
        self.data_classifier = DataClassifier()
        self.license_enforcer = LicenseEnforcer(LicenseManager())
        self._audit_trail: List[Dict[str, Any]] = []

    def _log_chart_event(self, event_type: str, details: Dict[str, Any] = None) -> None:
        """Log chart events for audit trail."""
        self._audit_trail.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "chart_id": self.metadata.chart_id,
            "user": self.metadata.created_by,
            "details": details or {}
        })

    def set_security_classification(self, level: SecurityLevel) -> None:
        """Set security classification for the chart."""
        self.metadata.security_level = level
        self._log_chart_event("security_classification_changed", {
            "new_level": level.value
        })

    def add_data_source(self, source: str) -> None:
        """Register data source for governance tracking."""
        if source not in self.metadata.data_sources:
            self.metadata.data_sources.append(source)
            self._log_chart_event("data_source_added", {"source": source})

    def add_compliance_tag(self, tag: str) -> None:
        """Add compliance tag (e.g., 'SOX', 'HIPAA', 'GDPR')."""
        if tag not in self.metadata.compliance_tags:
            self.metadata.compliance_tags.append(tag)
            self._log_chart_event("compliance_tag_added", {"tag": tag})

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get complete audit trail for the chart."""
        return self._audit_trail.copy()


class ExecutiveDashboardChart(EnterpriseBaseChart):
    """
    Executive dashboard chart with KPI tracking, trends, and alerts.
    """

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)
        self.metadata.title = "Executive Dashboard"

    @LicenseEnforcer(LicenseManager()).require_feature(LicenseFeature.ADVANCED_CHARTS)
    def create_kpi_dashboard(self, kpis: Dict[str, Dict[str, Union[float, str]]],
                           layout: str = "grid") -> None:
        """
        Create executive KPI dashboard.

        Args:
            kpis: Dictionary of KPI data with metrics like value, target, status
            layout: Layout type ("grid", "flow", "focus")
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib required for dashboard charts")

        self._log_chart_event("kpi_dashboard_created", {
            "kpi_count": len(kpis),
            "layout": layout
        })

        # Clear existing content
        self.figure.figure.clear()

        # Calculate grid layout
        n_kpis = len(kpis)
        if layout == "grid":
            cols = min(3, n_kpis)
            rows = (n_kpis + cols - 1) // cols
        else:
            cols, rows = n_kpis, 1

        # Create subplots for each KPI
        for i, (kpi_name, kpi_data) in enumerate(kpis.items()):
            ax = self.figure.figure.add_subplot(rows, cols, i + 1)

            value = kpi_data.get('value', 0)
            target = kpi_data.get('target')
            status = kpi_data.get('status', 'neutral')

            # Color mapping for status
            colors = {
                'good': '#28a745',
                'warning': '#ffc107',
                'critical': '#dc3545',
                'neutral': '#6c757d'
            }
            color = colors.get(status, colors['neutral'])

            # Create KPI visualization
            if target:
                # Progress bar style
                progress = min(value / target, 1.0) if target > 0 else 0
                ax.barh([0], [progress], color=color, alpha=0.7)
                ax.barh([0], [1-progress], left=[progress], color='lightgray', alpha=0.3)
                ax.set_xlim(0, 1)
                ax.set_ylim(-0.5, 0.5)
                ax.set_title(f"{kpi_name}\n{value:,.0f} / {target:,.0f}")
            else:
                # Simple value display
                ax.text(0.5, 0.5, f"{value:,.0f}", ha='center', va='center',
                       fontsize=24, color=color, fontweight='bold',
                       transform=ax.transAxes)
                ax.set_title(kpi_name)

            # Remove axes for cleaner look
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

        self.figure.figure.suptitle("Executive Dashboard", fontsize=16, fontweight='bold')
        self.figure.figure.tight_layout()

    def add_trend_indicators(self, trends: Dict[str, float]) -> None:
        """Add trend indicators to KPIs."""
        self._log_chart_event("trend_indicators_added", {
            "trend_count": len(trends)
        })
        # Implementation for trend arrows/indicators


class FinancialAnalyticsChart(EnterpriseBaseChart):
    """
    Financial analytics charts for enterprise financial reporting.
    """

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)
        self.metadata.title = "Financial Analytics"
        self.add_compliance_tag("SOX")

    @LicenseEnforcer(LicenseManager()).require_feature(LicenseFeature.ADVANCED_ANALYTICS)
    def create_waterfall_chart(self, categories: List[str], values: List[float],
                              title: str = "Waterfall Analysis") -> None:
        """
        Create waterfall chart for financial analysis.
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib required for financial charts")

        self._log_chart_event("waterfall_chart_created", {
            "categories": len(categories),
            "title": title
        })

        ax = self.axes
        cumulative = np.cumsum([0] + values[:-1])

        # Colors for positive/negative values
        colors = ['green' if v >= 0 else 'red' for v in values]

        # Create bars
        bars = ax.bar(range(len(values)), values, bottom=cumulative, color=colors, alpha=0.7)

        # Add connecting lines
        for i in range(len(values) - 1):
            start_y = cumulative[i] + values[i]
            end_y = cumulative[i + 1]
            ax.plot([i + 0.4, i + 1.4], [start_y, end_y], 'k--', alpha=0.5)

        # Formatting
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            y_pos = cumulative[i] + height/2
            ax.text(bar.get_x() + bar.get_width()/2., y_pos, f'{value:,.0f}',
                   ha='center', va='center', fontweight='bold', color='white')

    def create_variance_analysis(self, actual: List[float], budget: List[float],
                               periods: List[str]) -> None:
        """Create budget vs actual variance analysis."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib required for variance analysis")

        self._log_chart_event("variance_analysis_created", {
            "periods": len(periods)
        })

        ax = self.axes
        x = np.arange(len(periods))
        width = 0.35

        # Create grouped bars
        bars1 = ax.bar(x - width/2, actual, width, label='Actual', color='steelblue')
        bars2 = ax.bar(x + width/2, budget, width, label='Budget', color='lightcoral')

        # Calculate and display variance percentages
        variances = [(a - b) / b * 100 if b != 0 else 0 for a, b in zip(actual, budget)]

        for i, var in enumerate(variances):
            color = 'green' if var >= 0 else 'red'
            ax.text(i, max(actual[i], budget[i]) + max(actual + budget) * 0.05,
                   f'{var:+.1f}%', ha='center', va='bottom',
                   color=color, fontweight='bold')

        ax.set_xlabel('Periods')
        ax.set_ylabel('Amount')
        ax.set_title('Budget vs Actual Variance Analysis')
        ax.set_xticks(x)
        ax.set_xticklabels(periods)
        ax.legend()
        ax.grid(True, alpha=0.3)


class ComplianceChart(EnterpriseBaseChart):
    """
    Compliance-focused charts for regulatory reporting and auditing.
    """

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)
        self.metadata.title = "Compliance Chart"

    def create_audit_trail_chart(self, events: List[Dict[str, Any]]) -> None:
        """Create visual audit trail for compliance reporting."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib required for audit trail charts")

        self._log_chart_event("audit_trail_created", {
            "event_count": len(events)
        })

        ax = self.axes

        # Process events by date
        dates = [datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                for event in events]
        event_types = [event.get('event_type', 'unknown') for event in events]

        # Create timeline
        unique_types = list(set(event_types))
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_types)))
        type_colors = dict(zip(unique_types, colors))

        for i, (date, event_type) in enumerate(zip(dates, event_types)):
            y_pos = unique_types.index(event_type)
            ax.scatter(date, y_pos, c=[type_colors[event_type]], s=50, alpha=0.7)

        ax.set_yticks(range(len(unique_types)))
        ax.set_yticklabels(unique_types)
        ax.set_xlabel('Date')
        ax.set_title('Audit Trail Timeline')

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        ax.grid(True, alpha=0.3)

    def create_compliance_scorecard(self, metrics: Dict[str, Dict[str, float]]) -> None:
        """Create compliance scorecard with traffic light indicators."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib required for compliance scorecards")

        self._log_chart_event("compliance_scorecard_created", {
            "metric_count": len(metrics)
        })

        ax = self.axes

        categories = list(metrics.keys())
        y_pos = np.arange(len(categories))

        for i, (category, data) in enumerate(metrics.items()):
            score = data.get('score', 0)
            threshold_good = data.get('threshold_good', 90)
            threshold_warning = data.get('threshold_warning', 70)

            # Determine color based on score
            if score >= threshold_good:
                color = 'green'
                status = '✓'
            elif score >= threshold_warning:
                color = 'orange'
                status = '⚠'
            else:
                color = 'red'
                status = '✗'

            # Create horizontal bar
            ax.barh(i, score, color=color, alpha=0.7)

            # Add status symbol and score
            ax.text(score/2, i, f"{status} {score:.1f}%",
                   ha='center', va='center', fontweight='bold', color='white')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories)
        ax.set_xlabel('Compliance Score (%)')
        ax.set_title('Compliance Scorecard')
        ax.set_xlim(0, 100)
        ax.grid(True, alpha=0.3, axis='x')


class RiskAnalysisChart(EnterpriseBaseChart):
    """
    Risk analysis and management charts for enterprise risk assessment.
    """

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)
        self.metadata.title = "Risk Analysis"
        self.add_compliance_tag("Risk Management")

    @LicenseEnforcer(LicenseManager()).require_feature(LicenseFeature.ADVANCED_ANALYTICS)
    def create_risk_matrix(self, risks: List[Dict[str, Any]]) -> None:
        """
        Create risk probability vs impact matrix.

        Args:
            risks: List of risk dictionaries with 'name', 'probability', 'impact', 'category'
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib required for risk matrix")

        self._log_chart_event("risk_matrix_created", {
            "risk_count": len(risks)
        })

        ax = self.axes

        # Extract data
        probabilities = [risk.get('probability', 0) for risk in risks]
        impacts = [risk.get('impact', 0) for risk in risks]
        names = [risk.get('name', f'Risk {i}') for i, risk in enumerate(risks)]
        categories = [risk.get('category', 'General') for risk in risks]

        # Color by category
        unique_categories = list(set(categories))
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_categories)))
        category_colors = dict(zip(unique_categories, colors))
        risk_colors = [category_colors[cat] for cat in categories]

        # Create scatter plot
        scatter = ax.scatter(probabilities, impacts, c=risk_colors, s=100, alpha=0.7)

        # Add risk zones (background)
        ax.axhspan(0, 33, 0, 33, alpha=0.1, color='green', label='Low Risk')
        ax.axhspan(33, 67, 33, 67, alpha=0.1, color='yellow', label='Medium Risk')
        ax.axhspan(67, 100, 67, 100, alpha=0.1, color='red', label='High Risk')

        # Add labels for each risk
        for i, name in enumerate(names):
            ax.annotate(name, (probabilities[i], impacts[i]),
                       xytext=(5, 5), textcoords='offset points', fontsize=8)

        ax.set_xlabel('Probability (%)')
        ax.set_ylabel('Impact (%)')
        ax.set_title('Risk Probability vs Impact Matrix')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)

        # Add legend for categories
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                    markerfacecolor=category_colors[cat],
                                    markersize=8, label=cat)
                         for cat in unique_categories]
        ax.legend(handles=legend_elements, loc='upper left')

    def create_monte_carlo_simulation(self, n_simulations: int = 1000,
                                    risk_factors: Dict[str, Tuple[float, float]] = None) -> None:
        """Create Monte Carlo risk simulation visualization."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib required for Monte Carlo simulation")

        self._log_chart_event("monte_carlo_created", {
            "simulations": n_simulations,
            "factors": len(risk_factors) if risk_factors else 0
        })

        # Default risk factors if none provided
        if risk_factors is None:
            risk_factors = {
                'Market Risk': (0.05, 0.15),  # (mean, std)
                'Credit Risk': (0.02, 0.08),
                'Operational Risk': (0.01, 0.05)
            }

        # Run simulations
        total_risk = np.zeros(n_simulations)
        for factor_name, (mean, std) in risk_factors.items():
            factor_risk = np.random.normal(mean, std, n_simulations)
            total_risk += factor_risk

        # Create histogram
        ax = self.axes
        n, bins, patches = ax.hist(total_risk, bins=50, density=True, alpha=0.7,
                                  color='steelblue', edgecolor='black')

        # Add percentile lines
        percentiles = [5, 50, 95]
        percentile_values = np.percentile(total_risk, percentiles)
        colors = ['red', 'orange', 'red']

        for p, val, color in zip(percentiles, percentile_values, colors):
            ax.axvline(val, color=color, linestyle='--', alpha=0.8, linewidth=2)
            ax.text(val, ax.get_ylim()[1] * 0.9, f'{p}th: {val:.3f}',
                   rotation=90, ha='right', va='top', fontweight='bold')

        ax.set_xlabel('Total Risk')
        ax.set_ylabel('Probability Density')
        ax.set_title(f'Monte Carlo Risk Simulation ({n_simulations:,} iterations)')
        ax.grid(True, alpha=0.3)

        # Add summary statistics
        mean_risk = np.mean(total_risk)
        std_risk = np.std(total_risk)
        ax.text(0.02, 0.98, f'Mean: {mean_risk:.4f}\nStd: {std_risk:.4f}',
               transform=ax.transAxes, va='top', bbox=dict(boxstyle='round',
               facecolor='white', alpha=0.8))


# Enterprise Chart Factory
class EnterpriseChartFactory:
    """Factory for creating enterprise chart types."""

    @staticmethod
    def create_chart(chart_type: str, figure: Optional[VizlyFigure] = None) -> EnterpriseBaseChart:
        """Create enterprise chart by type."""
        chart_types = {
            'executive_dashboard': ExecutiveDashboardChart,
            'financial_analytics': FinancialAnalyticsChart,
            'compliance': ComplianceChart,
            'risk_analysis': RiskAnalysisChart
        }

        chart_class = chart_types.get(chart_type)
        if not chart_class:
            raise ValueError(f"Unknown chart type: {chart_type}")

        return chart_class(figure)

    @staticmethod
    def get_available_charts() -> List[str]:
        """Get list of available enterprise chart types."""
        return ['executive_dashboard', 'financial_analytics', 'compliance', 'risk_analysis']