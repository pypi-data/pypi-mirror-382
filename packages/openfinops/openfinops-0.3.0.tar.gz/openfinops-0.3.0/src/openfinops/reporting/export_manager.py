"""
Export Manager
==============

Multi-format export system for reports.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import csv
import logging

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"
    MARKDOWN = "markdown"


@dataclass
class ExportOptions:
    """
    Export configuration options.

    Attributes:
        format: Export format
        filename: Output filename
        include_metadata: Include report metadata
        compress: Compress output
        template: Template name for HTML/PDF
        page_size: Page size for PDF
        options: Additional format-specific options
    """

    format: ExportFormat
    filename: str = ""
    include_metadata: bool = True
    compress: bool = False
    template: str = "default"
    page_size: str = "letter"
    options: Dict[str, Any] = field(default_factory=dict)


class ExportManager:
    """
    Manages multi-format report exports.
    """

    def __init__(self):
        """Initialize export manager."""
        self._exporters = {
            ExportFormat.JSON: self._export_json,
            ExportFormat.CSV: self._export_csv,
            ExportFormat.HTML: self._export_html,
            ExportFormat.MARKDOWN: self._export_markdown,
        }

    def export(
        self,
        report_data: Dict[str, Any],
        options: ExportOptions,
    ) -> str:
        """
        Export report to specified format.

        Args:
            report_data: Report data to export
            options: Export options

        Returns:
            Path to exported file or export content
        """
        export_format = options.format

        if export_format not in self._exporters:
            raise ValueError(f"Unsupported export format: {export_format}")

        exporter = self._exporters[export_format]

        try:
            result = exporter(report_data, options)
            logger.info(f"Successfully exported report to {export_format.value}")
            return result
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            raise

    def _export_json(self, report_data: Dict[str, Any], options: ExportOptions) -> str:
        """Export report as JSON."""
        output = report_data.copy()

        if not options.include_metadata:
            output.pop("metadata", None)

        json_str = json.dumps(output, indent=2, default=str)

        if options.filename:
            filepath = Path(options.filename)
            filepath.write_text(json_str)
            return str(filepath)

        return json_str

    def _export_csv(self, report_data: Dict[str, Any], options: ExportOptions) -> str:
        """Export report as CSV."""
        # Extract tabular sections
        csv_content = []

        for section in report_data.get("sections", []):
            if section.get("type") == "table":
                csv_content.extend(self._section_to_csv_rows(section))
            elif section.get("type") == "breakdown":
                csv_content.extend(self._breakdown_to_csv_rows(section))

        if not csv_content:
            # Fallback: export summary data
            csv_content = self._dict_to_csv_rows(report_data)

        # Write to file or return as string
        if options.filename:
            filepath = Path(options.filename)
            with filepath.open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(csv_content)
            return str(filepath)

        # Return as string
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_content)
        return output.getvalue()

    def _section_to_csv_rows(self, section: Dict[str, Any]) -> list:
        """Convert table section to CSV rows."""
        rows = []

        # Add section title as header
        rows.append([section.get("title", "Section")])
        rows.append([])  # Empty row

        # Get data
        data = section.get("content", [])
        if not data:
            return rows

        # Extract columns
        if isinstance(data, list) and len(data) > 0:
            columns = list(data[0].keys())
            rows.append(columns)  # Header row

            # Data rows
            for item in data:
                rows.append([item.get(col, "") for col in columns])

        rows.append([])  # Empty row after section
        return rows

    def _breakdown_to_csv_rows(self, section: Dict[str, Any]) -> list:
        """Convert breakdown section to CSV rows."""
        rows = []

        # Add section title
        rows.append([section.get("title", "Breakdown")])
        rows.append([])

        # Get breakdown data
        content = section.get("content", {})
        breakdown_by = section.get("config", {}).get("breakdown_by", "Category")

        rows.append([breakdown_by, "Value"])

        for key, value in content.items():
            rows.append([key, value])

        rows.append([])
        return rows

    def _dict_to_csv_rows(self, data: Dict[str, Any]) -> list:
        """Convert dictionary to CSV rows."""
        rows = [["Key", "Value"]]

        for key, value in data.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            rows.append([key, value])

        return rows

    def _export_html(self, report_data: Dict[str, Any], options: ExportOptions) -> str:
        """Export report as HTML."""
        html_content = self._generate_html(report_data, options.template)

        if options.filename:
            filepath = Path(options.filename)
            filepath.write_text(html_content)
            return str(filepath)

        return html_content

    def _generate_html(self, report_data: Dict[str, Any], template: str) -> str:
        """Generate HTML content."""
        report_name = report_data.get("name", "Report")
        description = report_data.get("description", "")
        sections = report_data.get("sections", [])

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        .metric {{
            display: inline-block;
            margin: 10px;
            padding: 15px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            min-width: 150px;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <h1>{report_name}</h1>
    <p>{description}</p>
"""

        # Add sections
        for section in sections:
            html += self._section_to_html(section)

        html += """
</body>
</html>
"""

        return html

    def _section_to_html(self, section: Dict[str, Any]) -> str:
        """Convert section to HTML."""
        section_type = section.get("type")
        title = section.get("title", "Section")
        content = section.get("content", {})

        html = f'<div class="section">\n    <h2>{title}</h2>\n'

        if section_type == "table":
            html += self._table_to_html(content)
        elif section_type == "metric":
            html += self._metrics_to_html(content)
        elif section_type == "summary":
            html += self._summary_to_html(content)
        elif section_type == "text":
            html += f'<p>{content}</p>'
        else:
            html += f'<pre>{json.dumps(content, indent=2)}</pre>'

        html += "</div>\n"
        return html

    def _table_to_html(self, data: list) -> str:
        """Convert table data to HTML."""
        if not data:
            return "<p>No data</p>"

        html = "<table>\n"

        # Header
        if isinstance(data, list) and len(data) > 0:
            columns = list(data[0].keys())
            html += "    <tr>\n"
            for col in columns:
                html += f"        <th>{col}</th>\n"
            html += "    </tr>\n"

            # Rows
            for row in data:
                html += "    <tr>\n"
                for col in columns:
                    value = row.get(col, "")
                    html += f"        <td>{value}</td>\n"
                html += "    </tr>\n"

        html += "</table>\n"
        return html

    def _metrics_to_html(self, metrics: dict) -> str:
        """Convert metrics to HTML."""
        html = '<div class="metrics">\n'

        for key, value in metrics.items():
            html += f'''    <div class="metric">
        <div class="metric-label">{key}</div>
        <div class="metric-value">{value}</div>
    </div>\n'''

        html += "</div>\n"
        return html

    def _summary_to_html(self, data: dict) -> str:
        """Convert summary to HTML."""
        html = "<ul>\n"

        for key, value in data.items():
            html += f"    <li><strong>{key}:</strong> {value}</li>\n"

        html += "</ul>\n"
        return html

    def _export_markdown(self, report_data: Dict[str, Any], options: ExportOptions) -> str:
        """Export report as Markdown."""
        md_content = self._generate_markdown(report_data)

        if options.filename:
            filepath = Path(options.filename)
            filepath.write_text(md_content)
            return str(filepath)

        return md_content

    def _generate_markdown(self, report_data: Dict[str, Any]) -> str:
        """Generate Markdown content."""
        report_name = report_data.get("name", "Report")
        description = report_data.get("description", "")
        sections = report_data.get("sections", [])

        md = f"# {report_name}\n\n"

        if description:
            md += f"{description}\n\n"

        # Add sections
        for section in sections:
            md += self._section_to_markdown(section)

        return md

    def _section_to_markdown(self, section: Dict[str, Any]) -> str:
        """Convert section to Markdown."""
        section_type = section.get("type")
        title = section.get("title", "Section")
        content = section.get("content", {})

        md = f"## {title}\n\n"

        if section_type == "table":
            md += self._table_to_markdown(content)
        elif section_type == "summary":
            md += self._dict_to_markdown(content)
        elif section_type == "text":
            md += f"{content}\n\n"
        else:
            md += f"```json\n{json.dumps(content, indent=2)}\n```\n\n"

        return md

    def _table_to_markdown(self, data: list) -> str:
        """Convert table data to Markdown."""
        if not data:
            return "*No data*\n\n"

        md = ""

        if isinstance(data, list) and len(data) > 0:
            columns = list(data[0].keys())

            # Header
            md += "| " + " | ".join(columns) + " |\n"
            md += "| " + " | ".join(["---"] * len(columns)) + " |\n"

            # Rows
            for row in data:
                values = [str(row.get(col, "")) for col in columns]
                md += "| " + " | ".join(values) + " |\n"

        md += "\n"
        return md

    def _dict_to_markdown(self, data: dict) -> str:
        """Convert dictionary to Markdown."""
        md = ""

        for key, value in data.items():
            md += f"- **{key}**: {value}\n"

        md += "\n"
        return md

    def register_exporter(self, format: ExportFormat, exporter_func: callable):
        """
        Register a custom exporter.

        Args:
            format: Export format
            exporter_func: Function that exports data
        """
        self._exporters[format] = exporter_func
        logger.info(f"Registered custom exporter for {format.value}")

    def get_supported_formats(self) -> list:
        """Get list of supported export formats."""
        return list(self._exporters.keys())
