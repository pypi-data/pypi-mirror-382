"""
Tests for Reporting System
===========================

Test report generation, export, and BI integrations.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from openfinops.reporting import (
    ReportEngine,
    ReportBuilder,
    ReportType,
    ExportManager,
    ExportFormat,
    ExportOptions,
    ScheduledReportManager,
    ScheduleFrequency,
    BIConnector,
    TableauConnector,
    PowerBIConnector,
    ConnectionConfig,
)
from openfinops.reporting.report_builder import ChartType


@pytest.fixture
def report_engine():
    """Create report engine."""
    return ReportEngine()


@pytest.fixture
def sample_cost_data():
    """Create sample cost data."""
    return [
        {"service": "ec2", "cost": 1500.00, "region": "us-east-1"},
        {"service": "s3", "cost": 500.00, "region": "us-east-1"},
        {"service": "rds", "cost": 800.00, "region": "us-west-2"},
    ]


class TestReportEngine:
    """Test ReportEngine class."""

    def test_initialization(self, report_engine):
        """Test engine initialization."""
        assert report_engine is not None
        assert len(report_engine._templates) > 0

    def test_create_report(self, report_engine):
        """Test creating a report."""
        report = report_engine.create_report(
            name="Test Report",
            report_type=ReportType.COST_SUMMARY,
            description="Test description",
        )

        assert report.id is not None
        assert report.name == "Test Report"
        assert report.report_type == ReportType.COST_SUMMARY

    def test_generate_report(self, report_engine, sample_cost_data):
        """Test generating a report."""
        report = report_engine.create_report(
            name="Cost Report",
            report_type=ReportType.COST_SUMMARY,
        )

        generated = report_engine.generate_report(
            report.id,
            data_sources={"summary": sample_cost_data},
        )

        assert generated.status.value == "completed"

    def test_list_templates(self, report_engine):
        """Test listing templates."""
        templates = report_engine.list_templates()

        assert len(templates) > 0
        assert "cost_summary" in templates


class TestReportBuilder:
    """Test ReportBuilder class."""

    def test_builder_initialization(self):
        """Test builder initialization."""
        builder = ReportBuilder("My Report")

        assert builder.report_name == "My Report"
        assert builder.get_section_count() == 0

    def test_add_summary_section(self):
        """Test adding summary section."""
        builder = ReportBuilder("Report")
        builder.add_summary("Overview", {"total_cost": 1000})

        assert builder.get_section_count() == 1

    def test_add_table_section(self):
        """Test adding table section."""
        builder = ReportBuilder("Report")
        data = [{"service": "ec2", "cost": 100}]
        builder.add_table("Cost Table", data)

        assert builder.get_section_count() == 1

    def test_add_chart_section(self):
        """Test adding chart section."""
        builder = ReportBuilder("Report")
        builder.add_chart(
            "Cost Trend",
            ChartType.LINE,
            [{"date": "2025-01", "cost": 100}],
        )

        assert builder.get_section_count() == 1

    def test_build_report(self):
        """Test building report configuration."""
        builder = ReportBuilder("Test Report")
        builder.add_summary("Summary", {"total": 1000})
        builder.add_table("Details", [{"item": "test"}])

        report_config = builder.build()

        assert report_config["name"] == "Test Report"
        assert len(report_config["sections"]) == 2
        assert report_config["total_sections"] == 2

    def test_fluent_api(self):
        """Test fluent API chaining."""
        builder = ReportBuilder("Report")

        result = (
            builder
            .add_summary("Summary", {})
            .add_table("Table", [])
            .add_chart("Chart", ChartType.BAR, [])
        )

        assert result == builder
        assert builder.get_section_count() == 3


class TestExportManager:
    """Test ExportManager class."""

    def test_export_json(self):
        """Test JSON export."""
        manager = ExportManager()

        report_data = {
            "name": "Test Report",
            "sections": [{"type": "summary", "content": {"total": 100}}],
        }

        options = ExportOptions(format=ExportFormat.JSON)
        result = manager.export(report_data, options)

        assert isinstance(result, str)
        assert "Test Report" in result

    def test_export_csv(self):
        """Test CSV export."""
        manager = ExportManager()

        report_data = {
            "name": "Test Report",
            "sections": [
                {
                    "type": "table",
                    "title": "Cost Data",
                    "content": [
                        {"service": "ec2", "cost": 100},
                        {"service": "s3", "cost": 50},
                    ],
                }
            ],
        }

        options = ExportOptions(format=ExportFormat.CSV)
        result = manager.export(report_data, options)

        assert isinstance(result, str)
        assert "ec2" in result

    def test_export_html(self):
        """Test HTML export."""
        manager = ExportManager()

        report_data = {
            "name": "Test Report",
            "description": "Test description",
            "sections": [],
        }

        options = ExportOptions(format=ExportFormat.HTML)
        result = manager.export(report_data, options)

        assert isinstance(result, str)
        assert "<!DOCTYPE html>" in result
        assert "Test Report" in result

    def test_export_markdown(self):
        """Test Markdown export."""
        manager = ExportManager()

        report_data = {
            "name": "Test Report",
            "description": "Description",
            "sections": [],
        }

        options = ExportOptions(format=ExportFormat.MARKDOWN)
        result = manager.export(report_data, options)

        assert isinstance(result, str)
        assert "# Test Report" in result

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        manager = ExportManager()

        formats = manager.get_supported_formats()

        assert ExportFormat.JSON in formats
        assert ExportFormat.CSV in formats
        assert ExportFormat.HTML in formats


class TestScheduledReports:
    """Test ScheduledReportManager class."""

    def test_create_schedule(self):
        """Test creating a report schedule."""
        manager = ScheduledReportManager()

        schedule = manager.create_schedule(
            name="Daily Report",
            report_config={"type": "cost_summary"},
            frequency=ScheduleFrequency.DAILY,
            recipients=["user@example.com"],
        )

        assert schedule.id is not None
        assert schedule.name == "Daily Report"
        assert schedule.frequency == ScheduleFrequency.DAILY

    def test_list_schedules(self):
        """Test listing schedules."""
        manager = ScheduledReportManager()

        manager.create_schedule(
            "Schedule 1", {}, ScheduleFrequency.DAILY, []
        )
        manager.create_schedule(
            "Schedule 2", {}, ScheduleFrequency.WEEKLY, []
        )

        schedules = manager.list_schedules()

        assert len(schedules) == 2

    def test_enable_disable_schedule(self):
        """Test enabling/disabling schedules."""
        manager = ScheduledReportManager()

        schedule = manager.create_schedule(
            "Test Schedule", {}, ScheduleFrequency.DAILY, []
        )

        manager.disable_schedule(schedule.id)
        updated = manager.get_schedule(schedule.id)
        assert updated.enabled is False

        manager.enable_schedule(schedule.id)
        updated = manager.get_schedule(schedule.id)
        assert updated.enabled is True

    def test_get_due_schedules(self):
        """Test getting due schedules."""
        import time

        manager = ScheduledReportManager()

        current_time = time.time()
        past_time = current_time - 3600  # 1 hour ago

        # Create schedule with past next_run time
        schedule = manager.create_schedule(
            "Due Schedule", {}, ScheduleFrequency.DAILY, []
        )

        # Update the schedule's next_run to a past time
        manager.update_schedule(schedule.id, next_run=past_time)

        # Get due schedules with current time
        due = manager.get_due_schedules(current_time=current_time)

        assert len(due) == 1
        assert due[0].id == schedule.id


class TestBIConnectors:
    """Test BI connector classes."""

    def test_tableau_connector(self):
        """Test Tableau connector."""
        config = ConnectionConfig(
            host="https://tableau.example.com",
            username="user",
            api_key="key",
        )

        connector = TableauConnector(config)
        assert connector is not None
        assert not connector.is_connected()

        # Connect
        result = connector.connect()
        assert result is True
        assert connector.is_connected()

    def test_powerbi_connector(self):
        """Test Power BI connector."""
        config = ConnectionConfig(
            host="https://app.powerbi.com",
            username="user",
            api_key="key",
        )

        connector = PowerBIConnector(config)
        assert connector is not None

        # Connect
        result = connector.connect()
        assert result is True

    def test_publish_dataset(self):
        """Test publishing dataset to BI tool."""
        config = ConnectionConfig(
            host="https://tableau.example.com",
            api_key="key",
        )

        connector = TableauConnector(config)
        connector.connect()

        data = [
            {"service": "ec2", "cost": 100},
            {"service": "s3", "cost": 50},
        ]

        dataset_id = connector.publish_dataset("cost_data", data)

        assert dataset_id is not None
        assert isinstance(dataset_id, str)

    def test_create_dashboard(self):
        """Test creating dashboard in BI tool."""
        config = ConnectionConfig(
            host="https://powerbi.com",
            api_key="key",
        )

        connector = PowerBIConnector(config)
        connector.connect()

        dashboard_id = connector.create_dashboard(
            "Cost Dashboard",
            "dataset-123",
            {"layout": "grid"},
        )

        assert dashboard_id is not None


class TestIntegration:
    """Integration tests for reporting system."""

    def test_complete_report_workflow(self, report_engine, sample_cost_data):
        """Test complete report generation workflow."""
        # Build report
        builder = ReportBuilder("Monthly Cost Report")
        builder.add_summary("Overview", {"total_cost": 2800})
        builder.add_table("Cost Breakdown", sample_cost_data)
        builder.add_chart("Cost by Service", ChartType.PIE, sample_cost_data)

        report_config = builder.build()

        # Create report
        report = report_engine.create_report(
            name=report_config["name"],
            report_type=ReportType.CUSTOM,
        )

        report.sections = report_config["sections"]

        # Generate report
        generated = report_engine.generate_report(report.id, {})

        assert generated.status.value == "completed"

        # Export report
        manager = ExportManager()

        export_data = {
            "name": generated.name,
            "sections": generated.sections,
        }

        html_output = manager.export(
            export_data,
            ExportOptions(format=ExportFormat.HTML),
        )

        assert "Monthly Cost Report" in html_output


# Run quick test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
