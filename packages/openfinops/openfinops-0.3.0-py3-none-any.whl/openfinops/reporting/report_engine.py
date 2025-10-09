"""
Report Generation Engine
========================

Core engine for generating and managing reports.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports."""

    COST_SUMMARY = "cost_summary"
    BUDGET_ANALYSIS = "budget_analysis"
    COMPLIANCE = "compliance"
    USAGE_TRENDS = "usage_trends"
    ANOMALY = "anomaly"
    FORECAST = "forecast"
    RESOURCE_INVENTORY = "resource_inventory"
    CUSTOM = "custom"


class ReportStatus(Enum):
    """Report generation status."""

    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Report:
    """
    Report definition.

    Attributes:
        id: Unique report ID
        name: Report name
        report_type: Type of report
        description: Report description
        parameters: Report parameters
        sections: Report sections/content
        metadata: Additional metadata
        created_at: Creation timestamp
        status: Generation status
    """

    id: str
    name: str
    report_type: ReportType
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    sections: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    status: ReportStatus = ReportStatus.PENDING


class ReportEngine:
    """
    Central report generation engine.

    Generates reports from templates and data sources.
    """

    def __init__(self):
        """Initialize report engine."""
        self._reports: Dict[str, Report] = {}
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._data_providers: Dict[str, Callable] = {}
        self._report_counter = 0

        # Initialize default templates
        self._init_default_templates()

    def _init_default_templates(self):
        """Initialize default report templates."""
        self._templates["cost_summary"] = {
            "name": "Cost Summary Report",
            "sections": [
                {"type": "summary", "title": "Executive Summary"},
                {"type": "chart", "title": "Cost Trends", "chart_type": "line"},
                {"type": "table", "title": "Top Cost Drivers", "sort_by": "cost"},
                {"type": "breakdown", "title": "Cost by Service"},
            ],
        }

        self._templates["budget_analysis"] = {
            "name": "Budget Analysis Report",
            "sections": [
                {"type": "summary", "title": "Budget Overview"},
                {"type": "chart", "title": "Budget vs Actual", "chart_type": "bar"},
                {"type": "table", "title": "Budget Details"},
                {"type": "forecast", "title": "Forecast to End of Period"},
            ],
        }

    def register_data_provider(self, provider_name: str, provider_func: Callable):
        """
        Register a data provider function.

        Args:
            provider_name: Name of the data provider
            provider_func: Function that returns data
        """
        self._data_providers[provider_name] = provider_func
        logger.info(f"Registered data provider: {provider_name}")

    def create_report(
        self,
        name: str,
        report_type: ReportType,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None,
    ) -> Report:
        """
        Create a new report.

        Args:
            name: Report name
            report_type: Type of report
            description: Report description
            parameters: Report parameters
            template_name: Template to use

        Returns:
            Created report
        """
        self._report_counter += 1
        report_id = f"RPT-{self._report_counter:06d}"

        # Load template if specified
        sections = []
        if template_name and template_name in self._templates:
            template = self._templates[template_name]
            sections = template.get("sections", [])

        report = Report(
            id=report_id,
            name=name,
            report_type=report_type,
            description=description,
            parameters=parameters or {},
            sections=sections,
        )

        self._reports[report_id] = report
        logger.info(f"Created report {report_id}: {name}")

        return report

    def generate_report(
        self, report_id: str, data_sources: Optional[Dict[str, Any]] = None
    ) -> Report:
        """
        Generate a report.

        Args:
            report_id: Report ID
            data_sources: Optional data sources to use

        Returns:
            Generated report
        """
        report = self._reports.get(report_id)
        if not report:
            raise ValueError(f"Report not found: {report_id}")

        report.status = ReportStatus.GENERATING
        logger.info(f"Generating report {report_id}")

        try:
            # Fetch data for each section
            for section in report.sections:
                section_data = self._fetch_section_data(section, data_sources or {}, report.parameters)
                section["data"] = section_data

            report.status = ReportStatus.COMPLETED
            report.metadata["generated_at"] = datetime.now().timestamp()
            logger.info(f"Report {report_id} generated successfully")

        except Exception as e:
            report.status = ReportStatus.FAILED
            report.metadata["error"] = str(e)
            logger.error(f"Failed to generate report {report_id}: {e}")
            raise

        return report

    def _fetch_section_data(
        self,
        section: Dict[str, Any],
        data_sources: Dict[str, Any],
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Fetch data for a report section."""
        section_type = section.get("type")

        # Use data provider if available
        provider_name = section.get("data_provider")
        if provider_name and provider_name in self._data_providers:
            provider = self._data_providers[provider_name]
            return provider(parameters)

        # Use provided data sources
        if section_type in data_sources:
            return data_sources[section_type]

        # Return placeholder
        return {"message": f"No data available for section type: {section_type}"}

    def get_report(self, report_id: str) -> Optional[Report]:
        """Get a report by ID."""
        return self._reports.get(report_id)

    def list_reports(
        self,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
    ) -> List[Report]:
        """
        List reports with optional filters.

        Args:
            report_type: Filter by report type
            status: Filter by status

        Returns:
            List of reports
        """
        reports = list(self._reports.values())

        if report_type:
            reports = [r for r in reports if r.report_type == report_type]

        if status:
            reports = [r for r in reports if r.status == status]

        return reports

    def add_template(self, template_name: str, template_config: Dict[str, Any]):
        """
        Add a custom report template.

        Args:
            template_name: Template name
            template_config: Template configuration
        """
        self._templates[template_name] = template_config
        logger.info(f"Added template: {template_name}")

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name."""
        return self._templates.get(template_name)

    def list_templates(self) -> List[str]:
        """List available templates."""
        return list(self._templates.keys())

    def delete_report(self, report_id: str):
        """Delete a report."""
        if report_id in self._reports:
            del self._reports[report_id]
            logger.info(f"Deleted report {report_id}")

    def get_report_statistics(self) -> Dict[str, Any]:
        """
        Get report generation statistics.

        Returns:
            Statistics summary
        """
        total = len(self._reports)
        if total == 0:
            return {
                "total_reports": 0,
                "by_status": {},
                "by_type": {},
            }

        # Count by status
        by_status = {}
        for report in self._reports.values():
            status = report.status.value
            by_status[status] = by_status.get(status, 0) + 1

        # Count by type
        by_type = {}
        for report in self._reports.values():
            report_type = report.report_type.value
            by_type[report_type] = by_type.get(report_type, 0) + 1

        # Calculate completion rate
        completed = by_status.get(ReportStatus.COMPLETED.value, 0)
        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "total_reports": total,
            "by_status": by_status,
            "by_type": by_type,
            "completion_rate": completion_rate,
            "total_templates": len(self._templates),
            "total_data_providers": len(self._data_providers),
        }

    def clone_report(self, report_id: str, new_name: Optional[str] = None) -> Report:
        """
        Clone an existing report.

        Args:
            report_id: Report to clone
            new_name: Name for cloned report

        Returns:
            Cloned report
        """
        original = self.get_report(report_id)
        if not original:
            raise ValueError(f"Report not found: {report_id}")

        name = new_name or f"{original.name} (Copy)"

        cloned = self.create_report(
            name=name,
            report_type=original.report_type,
            description=original.description,
            parameters=original.parameters.copy(),
        )

        # Copy sections
        cloned.sections = [section.copy() for section in original.sections]

        return cloned


# Pre-defined report generators
def generate_cost_summary_report(
    cost_data: List[Dict[str, Any]],
    time_range: str = "last_30_days",
) -> Dict[str, Any]:
    """
    Generate cost summary report data.

    Args:
        cost_data: Cost data
        time_range: Time range

    Returns:
        Report data
    """
    if not cost_data:
        return {"error": "No cost data available"}

    total_cost = sum(item.get("cost", 0) for item in cost_data)

    # Group by service
    by_service = {}
    for item in cost_data:
        service = item.get("service", "unknown")
        by_service[service] = by_service.get(service, 0) + item.get("cost", 0)

    # Top cost drivers
    top_drivers = sorted(by_service.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_cost": total_cost,
        "time_range": time_range,
        "by_service": by_service,
        "top_drivers": top_drivers,
        "resource_count": len(cost_data),
    }


def generate_budget_analysis_report(
    budgets: List[Dict[str, Any]],
    actual_costs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate budget analysis report data.

    Args:
        budgets: Budget definitions
        actual_costs: Actual costs

    Returns:
        Report data
    """
    analysis = []

    for budget in budgets:
        budget_name = budget.get("name")
        budget_limit = budget.get("limit", 0)

        # Calculate actual for this budget
        scope = budget.get("scope", {})
        actual = sum(
            cost.get("cost", 0)
            for cost in actual_costs
            if all(cost.get(k) == v for k, v in scope.items())
        )

        variance = actual - budget_limit
        variance_pct = (variance / budget_limit * 100) if budget_limit > 0 else 0

        analysis.append(
            {
                "budget_name": budget_name,
                "budget_limit": budget_limit,
                "actual_cost": actual,
                "variance": variance,
                "variance_percentage": variance_pct,
                "status": "over" if variance > 0 else "under",
            }
        )

    return {
        "budget_analysis": analysis,
        "total_budgets": len(budgets),
        "budgets_exceeded": sum(1 for a in analysis if a["status"] == "over"),
    }
