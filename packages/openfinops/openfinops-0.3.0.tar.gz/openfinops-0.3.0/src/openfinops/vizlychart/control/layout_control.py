"""
Layout Control API
==================

Fine-grained control over figure layout, subplots, spacing, and positioning.
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

from typing import List, Optional, Union, Tuple, Dict, Any, Sequence
from dataclasses import dataclass
import math

import numpy as np

from ..charts.professional_charts import ProfessionalChart
from ..rendering.vizlyengine import ColorHDR


@dataclass
class SubplotSpec:
    """Specification for a subplot within a grid."""
    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    projection: Optional[str] = None  # None, '3d', 'polar'


@dataclass
class LayoutGeometry:
    """Geometric layout parameters."""
    left: float = 0.125      # Left margin
    bottom: float = 0.11     # Bottom margin
    right: float = 0.9       # Right edge (1 - right_margin)
    top: float = 0.88        # Top edge (1 - top_margin)
    wspace: float = 0.2      # Width spacing between subplots
    hspace: float = 0.2      # Height spacing between subplots


class SubplotGrid:
    """Grid-based subplot management system."""

    def __init__(self, nrows: int = 1, ncols: int = 1, width: int = 1200, height: int = 800):
        self.nrows = nrows
        self.ncols = ncols
        self.width = width
        self.height = height
        self.subplots = {}
        self.geometry = LayoutGeometry()
        self.figure_title = None
        self.figure_title_fontsize = 16

    def add_subplot(self, row: int, col: int, rowspan: int = 1, colspan: int = 1,
                   projection: Optional[str] = None) -> ProfessionalChart:
        """Add a subplot at specified grid position."""
        if row >= self.nrows or col >= self.ncols:
            raise ValueError(f"Subplot position ({row}, {col}) exceeds grid size ({self.nrows}, {self.ncols})")

        # Calculate subplot dimensions
        subplot_width = int((self.width * (self.geometry.right - self.geometry.left) / self.ncols) * colspan)
        subplot_height = int((self.height * (self.geometry.top - self.geometry.bottom) / self.nrows) * rowspan)

        # Create chart based on projection
        if projection == '3d':
            from ..charts.chart_3d import Chart3D
            chart = Chart3D(subplot_width, subplot_height)
        elif projection == 'polar':
            chart = ProfessionalChart(subplot_width, subplot_height)
            chart._polar_projection = True
        else:
            chart = ProfessionalChart(subplot_width, subplot_height)

        # Store subplot specification
        spec = SubplotSpec(row, col, rowspan, colspan, projection)
        self.subplots[(row, col)] = (chart, spec)

        return chart

    def get_subplot(self, row: int, col: int) -> Optional[ProfessionalChart]:
        """Get existing subplot at specified position."""
        return self.subplots.get((row, col), (None, None))[0]

    def set_geometry(self, left: float = None, bottom: float = None,
                    right: float = None, top: float = None,
                    wspace: float = None, hspace: float = None) -> 'SubplotGrid':
        """Set subplot spacing and margins."""
        if left is not None:
            self.geometry.left = left
        if bottom is not None:
            self.geometry.bottom = bottom
        if right is not None:
            self.geometry.right = right
        if top is not None:
            self.geometry.top = top
        if wspace is not None:
            self.geometry.wspace = wspace
        if hspace is not None:
            self.geometry.hspace = hspace
        return self

    def tight_layout(self, pad: float = 1.08, h_pad: float = None,
                    w_pad: float = None) -> 'SubplotGrid':
        """Automatically adjust subplot parameters for tight layout."""
        # Calculate optimal spacing based on content
        h_pad = h_pad or pad
        w_pad = w_pad or pad

        # Estimate required spacing
        self.geometry.wspace = max(0.1, w_pad * 0.1)
        self.geometry.hspace = max(0.1, h_pad * 0.1)

        # Adjust margins
        self.geometry.left = max(0.05, self.geometry.left * 0.8)
        self.geometry.bottom = max(0.05, self.geometry.bottom * 0.8)
        self.geometry.right = min(0.98, self.geometry.right + 0.05)
        self.geometry.top = min(0.95, self.geometry.top + 0.05)

        return self

    def set_figure_title(self, title: str, fontsize: float = 16,
                        y: float = 0.98) -> 'SubplotGrid':
        """Set overall figure title."""
        self.figure_title = title
        self.figure_title_fontsize = fontsize
        self.figure_title_y = y
        return self

    def render_to_svg(self) -> str:
        """Render entire subplot grid to SVG."""
        svg_parts = []

        # SVG header
        svg_parts.append(f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">')

        # Figure title
        if self.figure_title:
            title_y = self.figure_title_y * self.height
            svg_parts.append(f'<text x="{self.width/2}" y="{title_y}" text-anchor="middle" '
                           f'font-size="{self.figure_title_fontsize}" font-weight="bold">{self.figure_title}</text>')

        # Render each subplot
        for (row, col), (chart, spec) in self.subplots.items():
            if chart is None:
                continue

            # Calculate subplot position
            subplot_x = self.geometry.left * self.width + col * (self.width * (self.geometry.right - self.geometry.left) / self.ncols)
            subplot_y = self.geometry.bottom * self.height + (self.nrows - row - spec.rowspan) * (self.height * (self.geometry.top - self.geometry.bottom) / self.nrows)

            # Get chart SVG and wrap in group with transform
            chart_svg = chart.to_svg()
            # Extract content between <svg> tags
            start_idx = chart_svg.find('>') + 1
            end_idx = chart_svg.rfind('</svg>')
            chart_content = chart_svg[start_idx:end_idx]

            svg_parts.append(f'<g transform="translate({subplot_x}, {subplot_y})">')
            svg_parts.append(chart_content)
            svg_parts.append('</g>')

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)


class LayoutManager:
    """Advanced layout management for complex visualizations."""

    def __init__(self, chart):
        self.chart = chart
        self.margins = {'left': 80, 'right': 40, 'top': 60, 'bottom': 60}
        self.padding = {'left': 10, 'right': 10, 'top': 10, 'bottom': 10}
        self.title_position = 'top'
        self.legend_position = 'right'
        self.colorbar_position = 'right'

    def set_margins(self, left: float = None, right: float = None,
                   top: float = None, bottom: float = None) -> 'LayoutManager':
        """Set plot margins."""
        if left is not None:
            self.margins['left'] = left
        if right is not None:
            self.margins['right'] = right
        if top is not None:
            self.margins['top'] = top
        if bottom is not None:
            self.margins['bottom'] = bottom
        return self

    def set_padding(self, left: float = None, right: float = None,
                   top: float = None, bottom: float = None) -> 'LayoutManager':
        """Set internal padding."""
        if left is not None:
            self.padding['left'] = left
        if right is not None:
            self.padding['right'] = right
        if top is not None:
            self.padding['top'] = top
        if bottom is not None:
            self.padding['bottom'] = bottom
        return self

    def set_title_position(self, position: Union[str, Tuple[float, float]]) -> 'LayoutManager':
        """Set title position."""
        self.title_position = position
        return self

    def set_legend_position(self, position: str) -> 'LayoutManager':
        """Set legend position."""
        self.legend_position = position
        return self

    def calculate_plot_area(self) -> Tuple[float, float, float, float]:
        """Calculate available plot area after margins and legends."""
        left = self.margins['left'] + self.padding['left']
        bottom = self.margins['bottom'] + self.padding['bottom']
        width = self.chart.width - left - self.margins['right'] - self.padding['right']
        height = self.chart.height - bottom - self.margins['top'] - self.padding['top']

        # Adjust for legend
        if self.legend_position == 'right':
            width -= 120  # Approximate legend width
        elif self.legend_position == 'bottom':
            height -= 60  # Approximate legend height

        return left, bottom, width, height

    def auto_layout(self) -> 'LayoutManager':
        """Automatically optimize layout based on content."""
        # Analyze chart content and adjust margins accordingly
        # This is a simplified implementation

        # Adjust margins based on axis labels
        if hasattr(self.chart, 'y_label') and self.chart.y_label:
            self.margins['left'] = max(80, len(self.chart.y_label) * 8)

        if hasattr(self.chart, 'x_label') and self.chart.x_label:
            self.margins['bottom'] = max(60, 80)

        if hasattr(self.chart, 'title') and self.chart.title:
            self.margins['top'] = max(60, 80)

        return self


class FigureManager:
    """High-level figure management and multi-chart layouts."""

    def __init__(self, width: int = 1200, height: int = 800):
        self.width = width
        self.height = height
        self.charts = []
        self.layout_type = "single"  # single, grid, custom
        self.background_color = ColorHDR(1, 1, 1, 1)
        self.title = None
        self.subtitle = None

    def add_chart(self, chart: ProfessionalChart, position: Optional[Tuple[float, float, float, float]] = None) -> 'FigureManager':
        """Add chart to figure."""
        self.charts.append((chart, position))
        return self

    def create_grid_layout(self, nrows: int, ncols: int) -> SubplotGrid:
        """Create grid-based layout."""
        self.layout_type = "grid"
        return SubplotGrid(nrows, ncols, self.width, self.height)

    def set_title(self, title: str, subtitle: str = None) -> 'FigureManager':
        """Set figure title and subtitle."""
        self.title = title
        self.subtitle = subtitle
        return self

    def set_background(self, color: Union[str, ColorHDR]) -> 'FigureManager':
        """Set figure background color."""
        if isinstance(color, str):
            color = ColorHDR.from_hex(color)
        self.background_color = color
        return self

    def dashboard_layout(self, charts: List[ProfessionalChart],
                        titles: List[str] = None) -> 'FigureManager':
        """Create dashboard-style layout."""
        self.layout_type = "dashboard"
        self.charts = []

        n_charts = len(charts)
        if n_charts == 1:
            self.add_chart(charts[0], (0.1, 0.1, 0.8, 0.8))
        elif n_charts == 2:
            self.add_chart(charts[0], (0.05, 0.1, 0.4, 0.8))
            self.add_chart(charts[1], (0.55, 0.1, 0.4, 0.8))
        elif n_charts == 3:
            self.add_chart(charts[0], (0.05, 0.55, 0.4, 0.4))
            self.add_chart(charts[1], (0.55, 0.55, 0.4, 0.4))
            self.add_chart(charts[2], (0.3, 0.05, 0.4, 0.4))
        elif n_charts == 4:
            self.add_chart(charts[0], (0.05, 0.55, 0.4, 0.4))
            self.add_chart(charts[1], (0.55, 0.55, 0.4, 0.4))
            self.add_chart(charts[2], (0.05, 0.05, 0.4, 0.4))
            self.add_chart(charts[3], (0.55, 0.05, 0.4, 0.4))

        return self

    def render_to_svg(self) -> str:
        """Render complete figure to SVG."""
        svg_parts = []

        # SVG header with background
        svg_parts.append(f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">')
        svg_parts.append(f'<rect width="{self.width}" height="{self.height}" '
                        f'fill="rgb({int(self.background_color.r*255)},{int(self.background_color.g*255)},{int(self.background_color.b*255)})"/>')

        # Figure title
        if self.title:
            svg_parts.append(f'<text x="{self.width/2}" y="30" text-anchor="middle" '
                           f'font-size="20" font-weight="bold">{self.title}</text>')

        if self.subtitle:
            title_y = 50 if self.title else 30
            svg_parts.append(f'<text x="{self.width/2}" y="{title_y}" text-anchor="middle" '
                           f'font-size="14">{self.subtitle}</text>')

        # Render charts
        for chart, position in self.charts:
            if position is None:
                position = (0.1, 0.1, 0.8, 0.8)

            x, y, w, h = position
            chart_x = x * self.width
            chart_y = y * self.height
            chart_w = w * self.width
            chart_h = h * self.height

            # Get chart SVG content
            chart_svg = chart.to_svg()
            start_idx = chart_svg.find('>') + 1
            end_idx = chart_svg.rfind('</svg>')
            chart_content = chart_svg[start_idx:end_idx]

            # Scale chart to fit allocated space
            scale_x = chart_w / chart.width
            scale_y = chart_h / chart.height
            scale = min(scale_x, scale_y)

            svg_parts.append(f'<g transform="translate({chart_x}, {chart_y}) scale({scale})">')
            svg_parts.append(chart_content)
            svg_parts.append('</g>')

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def save_svg(self, filename: str):
        """Save figure as SVG file."""
        svg_content = self.render_to_svg()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)

    def save_png(self, filename: str, dpi: int = 300):
        """Save figure as PNG file."""
        try:
            import cairosvg
        except ImportError:
            raise ImportError("cairosvg is required for PNG export. Install with: pip install cairosvg")

        svg_content = self.render_to_svg()
        cairosvg.svg2png(bytestring=svg_content.encode('utf-8'),
                        write_to=filename, dpi=dpi)


def create_subplot_grid(nrows: int, ncols: int, width: int = 1200,
                       height: int = 800) -> SubplotGrid:
    """Create a subplot grid for multiple charts."""
    return SubplotGrid(nrows, ncols, width, height)


def create_figure(width: int = 800, height: int = 600) -> FigureManager:
    """Create a new figure manager."""
    return FigureManager(width, height)


def tight_layout(*charts: ProfessionalChart, pad: float = 1.08) -> FigureManager:
    """Create tight layout for multiple charts."""
    figure = FigureManager()
    for chart in charts:
        figure.add_chart(chart)

    # Apply tight layout logic
    return figure