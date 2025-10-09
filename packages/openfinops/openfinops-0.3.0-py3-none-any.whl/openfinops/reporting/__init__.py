"""
Advanced Reporting & BI Integrations
=====================================

Comprehensive reporting engine with BI tool integrations and multi-format exports.

This module provides:
- Report generation engine
- Multi-format exports (PDF, Excel, CSV, HTML, JSON)
- Scheduled reports
- Custom report builder
- BI tool integrations (Tableau, Power BI, Looker)
- Data export utilities

Example:
    >>> from openfinops.reporting import ReportEngine, ReportBuilder, ExportFormat
    >>>
    >>> engine = ReportEngine()
    >>>
    >>> # Build custom report
    >>> builder = ReportBuilder("Monthly Cost Report")
    >>> builder.add_section("summary", cost_data)
    >>> builder.add_chart("cost_trend", trend_data)
    >>>
    >>> # Generate report
    >>> report = builder.build()
    >>> engine.generate(report, format=ExportFormat.PDF, output="report.pdf")
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .report_engine import ReportEngine, Report, ReportType, ReportStatus
from .report_builder import ReportBuilder, ReportSection, ChartConfig
from .export_manager import ExportManager, ExportFormat, ExportOptions
from .scheduled_reports import ScheduledReportManager, ReportSchedule, ScheduleFrequency
from .bi_connectors import (
    BIConnector,
    TableauConnector,
    PowerBIConnector,
    LookerConnector,
    ConnectionConfig,
)

__all__ = [
    # Core engine
    "ReportEngine",
    "Report",
    "ReportType",
    "ReportStatus",
    # Report building
    "ReportBuilder",
    "ReportSection",
    "ChartConfig",
    # Export
    "ExportManager",
    "ExportFormat",
    "ExportOptions",
    # Scheduling
    "ScheduledReportManager",
    "ReportSchedule",
    "ScheduleFrequency",
    # BI integrations
    "BIConnector",
    "TableauConnector",
    "PowerBIConnector",
    "LookerConnector",
    "ConnectionConfig",
]
