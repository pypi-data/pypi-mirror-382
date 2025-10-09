"""
Report Builder
==============

Fluent API for building custom reports.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SectionType(Enum):
    """Report section types."""

    SUMMARY = "summary"
    TABLE = "table"
    CHART = "chart"
    TEXT = "text"
    METRIC = "metric"
    BREAKDOWN = "breakdown"
    COMPARISON = "comparison"
    FORECAST = "forecast"


class ChartType(Enum):
    """Chart types for reports."""

    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    WATERFALL = "waterfall"


@dataclass
class ChartConfig:
    """
    Chart configuration.

    Attributes:
        chart_type: Type of chart
        title: Chart title
        x_axis: X-axis label
        y_axis: Y-axis label
        data_key: Key for data
        options: Additional chart options
    """

    chart_type: ChartType
    title: str
    x_axis: str = ""
    y_axis: str = ""
    data_key: str = "data"
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportSection:
    """
    Report section.

    Attributes:
        section_type: Type of section
        title: Section title
        content: Section content/data
        config: Section configuration
        order: Display order
    """

    section_type: SectionType
    title: str
    content: Any = None
    config: Dict[str, Any] = field(default_factory=dict)
    order: int = 0


class ReportBuilder:
    """
    Fluent API for building custom reports.

    Example:
        >>> builder = ReportBuilder("Monthly Report")
        >>> builder.add_summary("Overview", summary_data)
        >>> builder.add_chart("Cost Trend", ChartType.LINE, trend_data)
        >>> report = builder.build()
    """

    def __init__(self, report_name: str, description: str = ""):
        """
        Initialize report builder.

        Args:
            report_name: Name of the report
            description: Report description
        """
        self.report_name = report_name
        self.description = description
        self._sections: List[ReportSection] = []
        self._metadata: Dict[str, Any] = {}
        self._section_counter = 0

    def add_summary(
        self,
        title: str,
        data: Dict[str, Any],
        key_metrics: Optional[List[str]] = None,
    ) -> "ReportBuilder":
        """
        Add a summary section.

        Args:
            title: Section title
            data: Summary data
            key_metrics: Key metrics to highlight

        Returns:
            Self for chaining
        """
        section = ReportSection(
            section_type=SectionType.SUMMARY,
            title=title,
            content=data,
            config={"key_metrics": key_metrics or []},
            order=self._section_counter,
        )

        self._sections.append(section)
        self._section_counter += 1
        return self

    def add_table(
        self,
        title: str,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None,
        sortable: bool = True,
    ) -> "ReportBuilder":
        """
        Add a table section.

        Args:
            title: Section title
            data: Table data (list of dicts)
            columns: Column names to display
            sortable: Whether table is sortable

        Returns:
            Self for chaining
        """
        section = ReportSection(
            section_type=SectionType.TABLE,
            title=title,
            content=data,
            config={"columns": columns, "sortable": sortable},
            order=self._section_counter,
        )

        self._sections.append(section)
        self._section_counter += 1
        return self

    def add_chart(
        self,
        title: str,
        chart_type: ChartType,
        data: Any,
        x_axis: str = "",
        y_axis: str = "",
        **options,
    ) -> "ReportBuilder":
        """
        Add a chart section.

        Args:
            title: Chart title
            chart_type: Type of chart
            data: Chart data
            x_axis: X-axis label
            y_axis: Y-axis label
            **options: Additional chart options

        Returns:
            Self for chaining
        """
        chart_config = ChartConfig(
            chart_type=chart_type,
            title=title,
            x_axis=x_axis,
            y_axis=y_axis,
            options=options,
        )

        section = ReportSection(
            section_type=SectionType.CHART,
            title=title,
            content=data,
            config={"chart": chart_config},
            order=self._section_counter,
        )

        self._sections.append(section)
        self._section_counter += 1
        return self

    def add_text(self, title: str, text: str, format: str = "markdown") -> "ReportBuilder":
        """
        Add a text section.

        Args:
            title: Section title
            text: Text content
            format: Text format (markdown, html, plain)

        Returns:
            Self for chaining
        """
        section = ReportSection(
            section_type=SectionType.TEXT,
            title=title,
            content=text,
            config={"format": format},
            order=self._section_counter,
        )

        self._sections.append(section)
        self._section_counter += 1
        return self

    def add_metrics(
        self,
        title: str,
        metrics: Dict[str, Any],
        layout: str = "grid",
    ) -> "ReportBuilder":
        """
        Add a metrics section (key-value pairs).

        Args:
            title: Section title
            metrics: Dictionary of metric name: value
            layout: Layout style (grid, list)

        Returns:
            Self for chaining
        """
        section = ReportSection(
            section_type=SectionType.METRIC,
            title=title,
            content=metrics,
            config={"layout": layout},
            order=self._section_counter,
        )

        self._sections.append(section)
        self._section_counter += 1
        return self

    def add_breakdown(
        self,
        title: str,
        data: Dict[str, Any],
        breakdown_by: str,
        show_percentage: bool = True,
    ) -> "ReportBuilder":
        """
        Add a breakdown section.

        Args:
            title: Section title
            data: Data to break down
            breakdown_by: Field to break down by
            show_percentage: Show percentages

        Returns:
            Self for chaining
        """
        section = ReportSection(
            section_type=SectionType.BREAKDOWN,
            title=title,
            content=data,
            config={"breakdown_by": breakdown_by, "show_percentage": show_percentage},
            order=self._section_counter,
        )

        self._sections.append(section)
        self._section_counter += 1
        return self

    def add_comparison(
        self,
        title: str,
        current: Dict[str, Any],
        previous: Dict[str, Any],
        labels: Optional[Dict[str, str]] = None,
    ) -> "ReportBuilder":
        """
        Add a comparison section.

        Args:
            title: Section title
            current: Current period data
            previous: Previous period data
            labels: Custom labels for periods

        Returns:
            Self for chaining
        """
        section = ReportSection(
            section_type=SectionType.COMPARISON,
            title=title,
            content={"current": current, "previous": previous},
            config={"labels": labels or {"current": "Current", "previous": "Previous"}},
            order=self._section_counter,
        )

        self._sections.append(section)
        self._section_counter += 1
        return self

    def add_forecast(
        self,
        title: str,
        historical: List[Dict[str, Any]],
        forecast: List[Dict[str, Any]],
        confidence_interval: Optional[Dict[str, Any]] = None,
    ) -> "ReportBuilder":
        """
        Add a forecast section.

        Args:
            title: Section title
            historical: Historical data
            forecast: Forecast data
            confidence_interval: Confidence intervals

        Returns:
            Self for chaining
        """
        section = ReportSection(
            section_type=SectionType.FORECAST,
            title=title,
            content={
                "historical": historical,
                "forecast": forecast,
                "confidence_interval": confidence_interval,
            },
            order=self._section_counter,
        )

        self._sections.append(section)
        self._section_counter += 1
        return self

    def set_metadata(self, key: str, value: Any) -> "ReportBuilder":
        """
        Set report metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Self for chaining
        """
        self._metadata[key] = value
        return self

    def reorder_section(self, section_index: int, new_order: int) -> "ReportBuilder":
        """
        Reorder a section.

        Args:
            section_index: Current section index
            new_order: New order position

        Returns:
            Self for chaining
        """
        if 0 <= section_index < len(self._sections):
            self._sections[section_index].order = new_order
            # Re-sort sections
            self._sections.sort(key=lambda s: s.order)

        return self

    def remove_section(self, section_index: int) -> "ReportBuilder":
        """
        Remove a section.

        Args:
            section_index: Section index to remove

        Returns:
            Self for chaining
        """
        if 0 <= section_index < len(self._sections):
            self._sections.pop(section_index)

        return self

    def build(self) -> Dict[str, Any]:
        """
        Build the report definition.

        Returns:
            Report configuration dictionary
        """
        return {
            "name": self.report_name,
            "description": self.description,
            "sections": [
                {
                    "type": section.section_type.value,
                    "title": section.title,
                    "content": section.content,
                    "config": section.config,
                    "order": section.order,
                }
                for section in sorted(self._sections, key=lambda s: s.order)
            ],
            "metadata": self._metadata,
            "total_sections": len(self._sections),
        }

    def get_section_count(self) -> int:
        """Get total number of sections."""
        return len(self._sections)

    def get_sections_by_type(self, section_type: SectionType) -> List[ReportSection]:
        """Get all sections of a specific type."""
        return [s for s in self._sections if s.section_type == section_type]

    def clear(self) -> "ReportBuilder":
        """
        Clear all sections.

        Returns:
            Self for chaining
        """
        self._sections.clear()
        self._section_counter = 0
        return self


# Helper functions for common report patterns
def create_executive_summary_report(
    cost_data: Dict[str, Any],
    budget_data: Dict[str, Any],
    trends: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Create an executive summary report.

    Args:
        cost_data: Cost summary data
        budget_data: Budget comparison data
        trends: Trend data

    Returns:
        Report configuration
    """
    builder = ReportBuilder("Executive Summary", "High-level cost and budget overview")

    # Key metrics
    builder.add_metrics(
        "Key Metrics",
        {
            "Total Cost": f"${cost_data.get('total', 0):,.2f}",
            "Budget Utilization": f"{budget_data.get('utilization_pct', 0):.1f}%",
            "Month-over-Month": f"{cost_data.get('mom_change_pct', 0):+.1f}%",
        },
    )

    # Cost trend
    builder.add_chart(
        "Cost Trend",
        ChartType.LINE,
        trends,
        x_axis="Date",
        y_axis="Cost ($)",
    )

    # Budget vs Actual
    builder.add_comparison(
        "Budget Performance",
        current=budget_data.get("actual", {}),
        previous=budget_data.get("budget", {}),
        labels={"current": "Actual", "previous": "Budget"},
    )

    return builder.build()


def create_detailed_cost_report(
    cost_data: List[Dict[str, Any]],
    breakdown_by: str = "service",
) -> Dict[str, Any]:
    """
    Create a detailed cost report.

    Args:
        cost_data: Detailed cost data
        breakdown_by: Field to break down by

    Returns:
        Report configuration
    """
    builder = ReportBuilder("Detailed Cost Report", "Comprehensive cost breakdown and analysis")

    # Summary
    total_cost = sum(item.get("cost", 0) for item in cost_data)
    builder.add_summary(
        "Overview",
        {"total_cost": total_cost, "resource_count": len(cost_data)},
    )

    # Top cost drivers table
    sorted_data = sorted(cost_data, key=lambda x: x.get("cost", 0), reverse=True)[:20]
    builder.add_table("Top Cost Drivers", sorted_data, sortable=True)

    # Breakdown by service/team/etc
    breakdown_data = {}
    for item in cost_data:
        key = item.get(breakdown_by, "unknown")
        breakdown_data[key] = breakdown_data.get(key, 0) + item.get("cost", 0)

    builder.add_breakdown(f"Cost by {breakdown_by.title()}", breakdown_data, breakdown_by)

    # Pie chart
    builder.add_chart(
        f"Cost Distribution by {breakdown_by.title()}",
        ChartType.PIE,
        breakdown_data,
    )

    return builder.build()
