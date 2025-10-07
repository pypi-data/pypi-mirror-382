"""
Professional Chart Classes
==========================

Production-grade chart implementations using the advanced rendering engine.
These charts match or exceed matplotlib's quality and capabilities.
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

from typing import List, Optional, Union, Tuple, Dict, Any
from abc import ABC, abstractmethod

import numpy as np

from ..rendering.vizlyengine import (
    AdvancedRenderer, ColorHDR, Font, RenderQuality, LineStyle,
    MarkerStyle, Gradient, UltraPrecisionAntiAliasing, PrecisionSettings
)


class ProfessionalChart(ABC):
    """Base class for professional-grade charts."""

    def __init__(self, width: int = 800, height: int = 600,
                 dpi: float = 96.0, quality: RenderQuality = RenderQuality.SVG_ONLY):
        self.width = width
        self.height = height
        self.dpi = dpi
        self.quality = quality

        # Initialize advanced renderer
        self.renderer = AdvancedRenderer(width, height, dpi, quality)

        # Chart metadata
        self.title = ""
        self.title_font = Font(size=16, weight="bold")
        self.xlabel = ""
        self.ylabel = ""
        self.label_font = Font(size=12)

        # Professional styling
        self.background_color = ColorHDR(1, 1, 1, 1)  # White
        self.grid_color = ColorHDR(0.9, 0.9, 0.9, 0.8)
        self.axis_color = ColorHDR(0.3, 0.3, 0.3, 1.0)
        self.text_color = ColorHDR(0.1, 0.1, 0.1, 1.0)

        # Chart state
        self.legend_entries = []
        self.data_series = []
        self.annotations = []

        # Professional color palette
        self.default_colors = [
            ColorHDR(0.12, 0.47, 0.71, 1.0),  # Professional blue
            ColorHDR(1.00, 0.50, 0.05, 1.0),  # Professional orange
            ColorHDR(0.17, 0.63, 0.17, 1.0),  # Professional green
            ColorHDR(0.84, 0.15, 0.16, 1.0),  # Professional red
            ColorHDR(0.58, 0.40, 0.74, 1.0),  # Professional purple
            ColorHDR(0.55, 0.34, 0.29, 1.0),  # Professional brown
            ColorHDR(0.89, 0.47, 0.76, 1.0),  # Professional pink
            ColorHDR(0.50, 0.50, 0.50, 1.0),  # Professional gray
            ColorHDR(0.74, 0.74, 0.13, 1.0),  # Professional yellow
            ColorHDR(0.09, 0.75, 0.81, 1.0),  # Professional cyan
        ]

        # Clear canvas
        self.renderer.canvas.clear(self.background_color)

    def set_title(self, title: str, font_size: float = 22,
                  color: Optional[ColorHDR] = None) -> 'ProfessionalChart':
        """Set chart title with professional typography."""
        self.title = title
        self.title_font.size = font_size
        self.title_font.weight = "bold"
        if color:
            self.text_color = color
        return self

    def set_labels(self, xlabel: str = "", ylabel: str = "",
                   font_size: float = 16) -> 'ProfessionalChart':
        """Set axis labels."""
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.label_font.size = font_size
        self.label_font.weight = "bold"
        return self

    def set_style(self, style: str = "professional") -> 'ProfessionalChart':
        """Set chart style theme."""
        if style == "professional":
            self.background_color = ColorHDR(1, 1, 1, 1)
            self.grid_color = ColorHDR(0.9, 0.9, 0.9, 0.8)
            self.axis_color = ColorHDR(0.3, 0.3, 0.3, 1.0)
            self.text_color = ColorHDR(0.1, 0.1, 0.1, 1.0)
        elif style == "dark":
            self.background_color = ColorHDR(0.1, 0.1, 0.1, 1)
            self.grid_color = ColorHDR(0.3, 0.3, 0.3, 0.8)
            self.axis_color = ColorHDR(0.7, 0.7, 0.7, 1.0)
            self.text_color = ColorHDR(0.9, 0.9, 0.9, 1.0)
        elif style == "minimal":
            self.background_color = ColorHDR(0.98, 0.98, 0.98, 1)
            self.grid_color = ColorHDR(0.95, 0.95, 0.95, 0.5)
            self.axis_color = ColorHDR(0.4, 0.4, 0.4, 1.0)
            self.text_color = ColorHDR(0.2, 0.2, 0.2, 1.0)

        self.renderer.canvas.clear(self.background_color)
        return self

    def _get_color(self, index: int) -> ColorHDR:
        """Get color from professional palette."""
        return self.default_colors[index % len(self.default_colors)]

    def add_annotation(self, x: float, y: float, text: str,
                      arrow: bool = False, font_size: float = 10):
        """Add text annotation to chart."""
        self.annotations.append({
            'x': x, 'y': y, 'text': text,
            'arrow': arrow, 'font_size': font_size
        })

    def _draw_title_and_labels(self):
        """Draw title and axis labels with professional typography."""
        if self.title:
            title_x = self.width / 2
            title_y = 30
            self.renderer.draw_text_professional(
                self.title, title_x, title_y, self.title_font, self.text_color, "center"
            )

        if self.xlabel:
            label_x = self.width / 2
            label_y = self.height - 20
            self.renderer.draw_text_professional(
                self.xlabel, label_x, label_y, self.label_font, self.text_color, "center"
            )

        if self.ylabel:
            # Vertical text would need rotation support
            label_x = 20
            label_y = self.height / 2
            self.renderer.draw_text_professional(
                self.ylabel, label_x, label_y, self.label_font, self.text_color, "left"
            )

    def _draw_legend(self, position: str = "upper_right"):
        """Draw professional legend with proper spacing."""
        if not self.legend_entries:
            return

        # Calculate legend dimensions
        legend_width = 150
        legend_height = len(self.legend_entries) * 25 + 20

        # Position legend
        if position == "upper_right":
            legend_x = self.width - legend_width - 20
            legend_y = 80
        elif position == "upper_left":
            legend_x = 100
            legend_y = 80
        elif position == "lower_right":
            legend_x = self.width - legend_width - 20
            legend_y = self.height - legend_height - 80
        else:
            legend_x = self.width - legend_width - 20
            legend_y = 80

        # Draw legend background with subtle border
        bg_color = ColorHDR(1, 1, 1, 0.95)
        border_color = ColorHDR(0.8, 0.8, 0.8, 1.0)

        # Legend background (simplified - would need proper rectangle rendering)
        # self._draw_legend_background(legend_x, legend_y, legend_width, legend_height)

        # Draw legend entries
        entry_font = Font(family="Arial", size=14, weight="normal")
        for i, entry in enumerate(self.legend_entries):
            entry_y = legend_y + 20 + i * 25

            # Draw color indicator
            indicator_x = legend_x + 10
            self.renderer.canvas.draw_circle_aa(
                indicator_x, entry_y, 4, entry['color'], filled=True
            )

            # Draw label
            text_x = legend_x + 25
            self.renderer.draw_text_professional(
                entry['label'], text_x, entry_y, entry_font, self.text_color
            )

    def _draw_annotations(self):
        """Draw all annotations."""
        for annotation in self.annotations:
            # Convert data coordinates to screen coordinates
            screen_x, screen_y = self.renderer.data_to_screen(
                annotation['x'], annotation['y']
            )

            # Draw annotation text
            ann_font = Font(size=annotation['font_size'])
            self.renderer.draw_text_professional(
                annotation['text'], screen_x, screen_y, ann_font, self.text_color
            )

            # Draw arrow if requested
            if annotation['arrow']:
                # Simple arrow implementation
                arrow_color = ColorHDR(0.5, 0.5, 0.5, 0.8)
                self.renderer.canvas.draw_line_aa(
                    screen_x - 10, screen_y + 5, screen_x, screen_y, arrow_color, 1.0
                )

    @abstractmethod
    def render(self):
        """Render the chart (implemented by subclasses)."""
        pass

    def save(self, filename: str, format: str = "png", dpi: float = None):
        """Save chart to file with specified format and quality."""
        if dpi:
            self.dpi = dpi

        self.render()  # Make sure chart is rendered

        if format.lower() == "png":
            self.renderer.save_png_hdr(filename)
        elif format.lower() == "svg":
            self.renderer.save_svg_professional(filename)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def show(self):
        """Display chart (for Jupyter/interactive environments)."""
        self.render()

        # Get SVG representation for display
        svg_content = self.renderer.canvas.to_svg_advanced()

        # For Jupyter display
        try:
            from IPython.display import display, SVG
            display(SVG(svg_content))
        except ImportError:
            # Not in Jupyter environment
            print("Chart rendered. Use save() to export to file.")

    def to_svg(self) -> str:
        """Return the chart as SVG string."""
        return self.render()

    def save_svg(self, filename: str):
        """Save chart as SVG file."""
        svg_content = self.to_svg()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)


class ProfessionalLineChart(ProfessionalChart):
    """Professional line chart with smooth curves and advanced styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_series = []

    def plot(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list],
             label: str = "", color: Optional[ColorHDR] = None,
             line_width: float = 2.0, line_style: LineStyle = LineStyle.SOLID,
             marker: Optional[MarkerStyle] = None, marker_size: float = 6.0,
             alpha: float = 1.0, smooth: bool = False) -> 'ProfessionalLineChart':
        """Plot line series with professional styling options."""

        # Convert to numpy arrays
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

        # Auto-select color if not provided
        if color is None:
            color = self._get_color(len(self.line_series))

        # Store series data
        series_data = {
            'x': x, 'y': y, 'label': label, 'color': color,
            'line_width': line_width, 'line_style': line_style,
            'marker': marker, 'marker_size': marker_size,
            'alpha': alpha, 'smooth': smooth
        }
        self.line_series.append(series_data)

        # Add to legend if label provided
        if label:
            self.legend_entries.append({'label': label, 'color': color})

        return self

    def line(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list],
             label: str = "", color: Optional[ColorHDR] = None,
             line_width: float = 2.0, line_style: LineStyle = LineStyle.SOLID,
             marker: Optional[MarkerStyle] = None, marker_size: float = 6.0,
             alpha: float = 1.0, smooth: bool = False) -> 'ProfessionalLineChart':
        """Alias for plot method - plot line series with professional styling."""
        return self.plot(x, y, label, color, line_width, line_style, marker, marker_size, alpha, smooth)

    def render(self):
        """Render the professional line chart."""
        # Start SVG document
        svg_content = f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background
        svg_content += f'<rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/>\n'

        # Add title if present
        if self.title:
            svg_content += f'<text x="{self.width//2}" y="30" text-anchor="middle" font-size="{self.title_font.size}" font-weight="bold" fill="rgb(25,25,25)">{self.title}</text>\n'

        # Add axis labels if present
        if self.xlabel:
            svg_content += f'<text x="{self.width//2}" y="{self.height-20}" text-anchor="middle" font-size="{self.label_font.size}" fill="rgb(50,50,50)">{self.xlabel}</text>\n'
        if self.ylabel:
            svg_content += f'<text x="30" y="{self.height//2}" text-anchor="middle" font-size="{self.label_font.size}" fill="rgb(50,50,50)" transform="rotate(-90 30 {self.height//2})">{self.ylabel}</text>\n'

        if not self.line_series:
            svg_content += '<text x="400" y="300" text-anchor="middle" font-size="14" fill="gray">No data to display</text>\n'
            svg_content += '</svg>'
            return svg_content

        # Calculate data bounds and plotting area
        all_x = np.concatenate([series['x'] for series in self.line_series])
        all_y = np.concatenate([series['y'] for series in self.line_series])
        x_min, x_max = np.min(all_x), np.max(all_x)
        y_min, y_max = np.min(all_y), np.max(all_y)

        # Add padding
        x_padding = (x_max - x_min) * 0.05 if x_max != x_min else 1.0
        y_padding = (y_max - y_min) * 0.05 if y_max != y_min else 1.0
        x_min -= x_padding
        x_max += x_padding
        y_min -= y_padding
        y_max += y_padding

        # Define plotting area (margins for axes and labels)
        margin_left = 80
        margin_right = 50
        margin_top = 60
        margin_bottom = 80
        plot_width = self.width - margin_left - margin_right
        plot_height = self.height - margin_top - margin_bottom

        # Helper function to convert data coordinates to screen coordinates
        def data_to_screen(x_data, y_data):
            screen_x = margin_left + (x_data - x_min) / (x_max - x_min) * plot_width
            screen_y = margin_top + (1 - (y_data - y_min) / (y_max - y_min)) * plot_height
            return screen_x, screen_y

        # Draw grid lines
        svg_content += f'<g stroke="rgb(230,230,230)" stroke-width="1" opacity="0.8">\n'
        # Vertical grid lines
        for i in range(6):
            x_val = x_min + (x_max - x_min) * i / 5
            screen_x, _ = data_to_screen(x_val, y_min)
            svg_content += f'<line x1="{screen_x}" y1="{margin_top}" x2="{screen_x}" y2="{margin_top + plot_height}"/>\n'
        # Horizontal grid lines
        for i in range(6):
            y_val = y_min + (y_max - y_min) * i / 5
            _, screen_y = data_to_screen(x_min, y_val)
            svg_content += f'<line x1="{margin_left}" y1="{screen_y}" x2="{margin_left + plot_width}" y2="{screen_y}"/>\n'
        svg_content += '</g>\n'

        # Draw axes
        svg_content += f'<g stroke="rgb(80,80,80)" stroke-width="2" fill="none">\n'
        svg_content += f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}"/>\n'  # Y-axis
        svg_content += f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}"/>\n'  # X-axis
        svg_content += '</g>\n'

        # Draw axis labels/ticks
        svg_content += f'<g font-size="10" text-anchor="middle" fill="rgb(80,80,80)">\n'
        # X-axis labels
        for i in range(6):
            x_val = x_min + (x_max - x_min) * i / 5
            screen_x, _ = data_to_screen(x_val, y_min)
            # Handle both numeric and string x values
            if isinstance(x_val, (int, float)):
                x_label = f'{x_val:.2f}'
            else:
                x_label = str(x_val)
            svg_content += f'<text x="{screen_x}" y="{margin_top + plot_height + 20}">{x_label}</text>\n'
        svg_content += '</g>\n'

        svg_content += f'<g font-size="10" text-anchor="end" fill="rgb(80,80,80)">\n'
        # Y-axis labels
        for i in range(6):
            y_val = y_min + (y_max - y_min) * i / 5
            _, screen_y = data_to_screen(x_min, y_val)
            # Handle both numeric and string y values
            if isinstance(y_val, (int, float)):
                y_label = f'{y_val:.2f}'
            else:
                y_label = str(y_val)
            svg_content += f'<text x="{margin_left - 10}" y="{screen_y + 4}">{y_label}</text>\n'
        svg_content += '</g>\n'

        # Plot each line series
        for series in self.line_series:
            # Convert color to RGB string
            color_str = f"rgb({int(series['color'].r * 255)},{int(series['color'].g * 255)},{int(series['color'].b * 255)})"

            # Build path data for the line
            path_data = ""
            for i, (x_val, y_val) in enumerate(zip(series['x'], series['y'])):
                screen_x, screen_y = data_to_screen(x_val, y_val)
                if i == 0:
                    path_data += f"M {screen_x} {screen_y} "
                else:
                    path_data += f"L {screen_x} {screen_y} "

            # Draw the line
            svg_content += f'<path d="{path_data}" stroke="{color_str}" stroke-width="{series["line_width"]}" fill="none" opacity="{series["alpha"]}"/>\n'

            # Draw markers if specified
            if series['marker']:
                for x_val, y_val in zip(series['x'], series['y']):
                    screen_x, screen_y = data_to_screen(x_val, y_val)
                    svg_content += f'<circle cx="{screen_x}" cy="{screen_y}" r="{series["marker_size"]/2}" fill="{color_str}" opacity="{series["alpha"]}"/>\n'

        # Draw legend if there are labeled series
        if self.legend_entries:
            legend_x = self.width - 150
            legend_y = 60
            svg_content += f'<g font-size="12" font-family="Arial">\n'
            for i, entry in enumerate(self.legend_entries):
                y_pos = legend_y + i * 20
                color_str = f"rgb({int(entry['color'].r * 255)},{int(entry['color'].g * 255)},{int(entry['color'].b * 255)})"
                svg_content += f'<line x1="{legend_x}" y1="{y_pos}" x2="{legend_x + 20}" y2="{y_pos}" stroke="{color_str}" stroke-width="3"/>\n'
                svg_content += f'<text x="{legend_x + 25}" y="{y_pos + 4}" fill="rgb(50,50,50)">{entry["label"]}</text>\n'
            svg_content += '</g>\n'

        # Close SVG document
        svg_content += '</svg>'
        return svg_content


class ProfessionalScatterChart(ProfessionalChart):
    """Professional scatter plot with advanced styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatter_series = []

    def scatter(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list],
                s: Union[float, np.ndarray, list] = 20.0,
                c: Union[ColorHDR, np.ndarray, list] = None,
                marker: MarkerStyle = MarkerStyle.CIRCLE,
                alpha: float = 1.0, label: str = "") -> 'ProfessionalScatterChart':
        """Create professional scatter plot."""

        # Convert to numpy arrays
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

        # Handle size parameter
        if not isinstance(s, np.ndarray):
            s = np.full(len(x), s)

        # Handle color parameter
        if c is None:
            c = self._get_color(len(self.scatter_series))

        if isinstance(c, ColorHDR):
            colors = np.full(len(x), c)
        elif isinstance(c, (list, np.ndarray)):
            colors = np.array(c)
        else:
            colors = np.full(len(x), c)

        # Store series data
        series_data = {
            'x': x, 'y': y, 'sizes': s, 'colors': colors,
            'marker': marker, 'alpha': alpha, 'label': label
        }
        self.scatter_series.append(series_data)

        # Add to legend if label provided
        if label and isinstance(c, ColorHDR):
            self.legend_entries.append({'label': label, 'color': c})

        return self

    def render(self):
        """Render professional scatter chart."""
        if not self.scatter_series:
            return f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg"><rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/><text x="{self.width//2}" y="{self.height//2}" text-anchor="middle" font-size="14" fill="gray">No data to display</text></svg>'

        # Start SVG document
        svg_content = f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background
        svg_content += f'<rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/>\n'

        # Add title if present
        if self.title:
            svg_content += f'<text x="{self.width//2}" y="30" text-anchor="middle" font-size="{self.title_font.size}" font-weight="bold" fill="rgb(25,25,25)">{self.title}</text>\n'

        # Add axis labels if present
        if self.xlabel:
            svg_content += f'<text x="{self.width//2}" y="{self.height-20}" text-anchor="middle" font-size="{self.label_font.size}" fill="rgb(50,50,50)">{self.xlabel}</text>\n'
        if self.ylabel:
            svg_content += f'<text x="30" y="{self.height//2}" text-anchor="middle" font-size="{self.label_font.size}" fill="rgb(50,50,50)" transform="rotate(-90 30 {self.height//2})">{self.ylabel}</text>\n'

        # Calculate data bounds
        all_x = np.concatenate([series['x'] for series in self.scatter_series])
        all_y = np.concatenate([series['y'] for series in self.scatter_series])

        x_min, x_max = np.min(all_x), np.max(all_x)
        y_min, y_max = np.min(all_y), np.max(all_y)

        # Add padding
        x_padding = (x_max - x_min) * 0.05 if x_max != x_min else 1.0
        y_padding = (y_max - y_min) * 0.05 if y_max != y_min else 1.0
        x_min -= x_padding
        x_max += x_padding
        y_min -= y_padding
        y_max += y_padding

        # Define plotting area (margins for axes and labels)
        margin_left = 80
        margin_right = 50
        margin_top = 60
        margin_bottom = 80
        plot_width = self.width - margin_left - margin_right
        plot_height = self.height - margin_top - margin_bottom

        # Helper function to convert data coordinates to screen coordinates
        def data_to_screen(x_data, y_data):
            screen_x = margin_left + (x_data - x_min) / (x_max - x_min) * plot_width
            screen_y = margin_top + (1 - (y_data - y_min) / (y_max - y_min)) * plot_height
            return screen_x, screen_y

        # Draw grid lines
        svg_content += f'<g stroke="rgb(230,230,230)" stroke-width="1" opacity="0.8">\n'
        # Vertical grid lines
        for i in range(6):
            x_val = x_min + (x_max - x_min) * i / 5
            screen_x, _ = data_to_screen(x_val, y_min)
            svg_content += f'<line x1="{screen_x}" y1="{margin_top}" x2="{screen_x}" y2="{margin_top + plot_height}"/>\n'
        # Horizontal grid lines
        for i in range(6):
            y_val = y_min + (y_max - y_min) * i / 5
            _, screen_y = data_to_screen(x_min, y_val)
            svg_content += f'<line x1="{margin_left}" y1="{screen_y}" x2="{margin_left + plot_width}" y2="{screen_y}"/>\n'
        svg_content += '</g>\n'

        # Draw axes
        svg_content += f'<g stroke="rgb(80,80,80)" stroke-width="2" fill="none">\n'
        svg_content += f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}"/>\n'  # Y-axis
        svg_content += f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}"/>\n'  # X-axis
        svg_content += '</g>\n'

        # Draw axis labels/ticks
        svg_content += f'<g font-size="10" text-anchor="middle" fill="rgb(80,80,80)">\n'
        # X-axis labels
        for i in range(6):
            x_val = x_min + (x_max - x_min) * i / 5
            screen_x, _ = data_to_screen(x_val, y_min)
            x_label = f'{x_val:.2f}' if isinstance(x_val, (int, float)) else str(x_val)
            svg_content += f'<text x="{screen_x}" y="{margin_top + plot_height + 20}">{x_label}</text>\n'
        svg_content += '</g>\n'

        svg_content += f'<g font-size="10" text-anchor="end" fill="rgb(80,80,80)">\n'
        # Y-axis labels
        for i in range(6):
            y_val = y_min + (y_max - y_min) * i / 5
            _, screen_y = data_to_screen(x_min, y_val)
            y_label = f'{y_val:.2f}' if isinstance(y_val, (int, float)) else str(y_val)
            svg_content += f'<text x="{margin_left - 10}" y="{screen_y + 4}">{y_label}</text>\n'
        svg_content += '</g>\n'

        # Plot each scatter series
        for series in self.scatter_series:
            for i in range(len(series['x'])):
                screen_x, screen_y = data_to_screen(series['x'][i], series['y'][i])

                # Get color for this point
                if isinstance(series['colors'], np.ndarray) and len(series['colors']) > i:
                    color = series['colors'][i]
                elif isinstance(series['colors'], ColorHDR):
                    color = series['colors']
                else:
                    color = self._get_color(0)

                # Get size for this point
                size = series['sizes'][i] if len(series['sizes']) > i else 20.0
                radius = size / 2

                # Convert color to RGB string
                color_str = f"rgb({int(color.r * 255)},{int(color.g * 255)},{int(color.b * 255)})"

                # Draw scatter point as circle
                svg_content += f'<circle cx="{screen_x}" cy="{screen_y}" r="{radius}" fill="{color_str}" opacity="{series["alpha"]}"/>\n'

        # Draw legend if there are labeled series
        if self.legend_entries:
            legend_x = self.width - 150
            legend_y = 60
            svg_content += f'<g font-size="12" font-family="Arial">\n'
            for i, entry in enumerate(self.legend_entries):
                y_pos = legend_y + i * 20
                color_str = f"rgb({int(entry['color'].r * 255)},{int(entry['color'].g * 255)},{int(entry['color'].b * 255)})"
                svg_content += f'<circle cx="{legend_x + 10}" cy="{y_pos}" r="5" fill="{color_str}"/>\n'
                svg_content += f'<text x="{legend_x + 25}" y="{y_pos + 4}" fill="rgb(50,50,50)">{entry["label"]}</text>\n'
            svg_content += '</g>\n'

        # Close SVG document
        svg_content += '</svg>'
        return svg_content


class ProfessionalBarChart(ProfessionalChart):
    """Professional bar chart with advanced styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bar_series = []

    def bar(self, x: Union[np.ndarray, list], height: Union[np.ndarray, list],
            width: float = 0.8, color: Optional[ColorHDR] = None,
            alpha: float = 1.0, label: str = "",
            gradient: Optional[Gradient] = None) -> 'ProfessionalBarChart':
        """Create professional bar chart."""

        # Convert to numpy arrays
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(height, np.ndarray):
            height = np.array(height)

        # Handle categorical x data
        if x.dtype.kind in ['U', 'S', 'O']:  # String types
            x_labels = x.copy()
            x = np.arange(len(x))
        else:
            x_labels = None

        # Auto-select color if not provided
        if color is None:
            color = self._get_color(len(self.bar_series))

        # Store series data
        series_data = {
            'x': x, 'height': height, 'x_labels': x_labels,
            'width': width, 'color': color, 'alpha': alpha,
            'label': label, 'gradient': gradient
        }
        self.bar_series.append(series_data)

        # Add to legend if label provided
        if label:
            self.legend_entries.append({'label': label, 'color': color})

        return self

    def render(self):
        """Render professional bar chart."""
        if not self.bar_series:
            return f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg"><rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/><text x="{self.width//2}" y="{self.height//2}" text-anchor="middle" font-size="14" fill="gray">No data to display</text></svg>'

        # Start SVG document
        svg_content = f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background
        svg_content += f'<rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/>\n'

        # Add title if present
        if self.title:
            svg_content += f'<text x="{self.width//2}" y="30" text-anchor="middle" font-size="{self.title_font.size}" font-weight="bold" fill="rgb(25,25,25)">{self.title}</text>\n'

        # Add axis labels if present
        if self.xlabel:
            svg_content += f'<text x="{self.width//2}" y="{self.height-20}" text-anchor="middle" font-size="{self.label_font.size}" fill="rgb(50,50,50)">{self.xlabel}</text>\n'
        if self.ylabel:
            svg_content += f'<text x="30" y="{self.height//2}" text-anchor="middle" font-size="{self.label_font.size}" fill="rgb(50,50,50)" transform="rotate(-90 30 {self.height//2})">{self.ylabel}</text>\n'

        # Calculate data bounds
        all_x = np.concatenate([series['x'] for series in self.bar_series])
        all_heights = np.concatenate([series['height'] for series in self.bar_series])

        x_min, x_max = np.min(all_x) - 0.5, np.max(all_x) + 0.5
        y_min, y_max = 0, np.max(all_heights) * 1.1

        # Define plotting area (margins for axes and labels)
        margin_left = 80
        margin_right = 50
        margin_top = 60
        margin_bottom = 80
        plot_width = self.width - margin_left - margin_right
        plot_height = self.height - margin_top - margin_bottom

        # Helper function to convert data coordinates to screen coordinates
        def data_to_screen(x_data, y_data):
            screen_x = margin_left + (x_data - x_min) / (x_max - x_min) * plot_width
            screen_y = margin_top + (1 - (y_data - y_min) / (y_max - y_min)) * plot_height
            return screen_x, screen_y

        # Draw grid lines
        svg_content += f'<g stroke="rgb(230,230,230)" stroke-width="1" opacity="0.8">\n'
        # Vertical grid lines
        for i in range(6):
            x_val = x_min + (x_max - x_min) * i / 5
            screen_x, _ = data_to_screen(x_val, y_min)
            svg_content += f'<line x1="{screen_x}" y1="{margin_top}" x2="{screen_x}" y2="{margin_top + plot_height}"/>\n'
        # Horizontal grid lines
        for i in range(6):
            y_val = y_min + (y_max - y_min) * i / 5
            _, screen_y = data_to_screen(x_min, y_val)
            svg_content += f'<line x1="{margin_left}" y1="{screen_y}" x2="{margin_left + plot_width}" y2="{screen_y}"/>\n'
        svg_content += '</g>\n'

        # Draw axes
        svg_content += f'<g stroke="rgb(80,80,80)" stroke-width="2" fill="none">\n'
        svg_content += f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}"/>\n'  # Y-axis
        svg_content += f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}"/>\n'  # X-axis
        svg_content += '</g>\n'

        # Draw axis labels/ticks
        svg_content += f'<g font-size="10" text-anchor="middle" fill="rgb(80,80,80)">\n'
        # X-axis labels (handle categorical data)
        for series in self.bar_series:
            if series.get('x_labels') is not None:
                # Use categorical labels
                for i, (x_pos, x_label) in enumerate(zip(series['x'], series['x_labels'])):
                    screen_x, _ = data_to_screen(x_pos, y_min)
                    svg_content += f'<text x="{screen_x}" y="{margin_top + plot_height + 20}">{x_label}</text>\n'
                break
        else:
            # Use numeric labels
            for i in range(6):
                x_val = x_min + (x_max - x_min) * i / 5
                screen_x, _ = data_to_screen(x_val, y_min)
                x_label = f'{x_val:.2f}' if isinstance(x_val, (int, float)) else str(x_val)
                svg_content += f'<text x="{screen_x}" y="{margin_top + plot_height + 20}">{x_label}</text>\n'
        svg_content += '</g>\n'

        svg_content += f'<g font-size="10" text-anchor="end" fill="rgb(80,80,80)">\n'
        # Y-axis labels
        for i in range(6):
            y_val = y_min + (y_max - y_min) * i / 5
            _, screen_y = data_to_screen(x_min, y_val)
            y_label = f'{y_val:.2f}' if isinstance(y_val, (int, float)) else str(y_val)
            svg_content += f'<text x="{margin_left - 10}" y="{screen_y + 4}">{y_label}</text>\n'
        svg_content += '</g>\n'

        # Draw bars
        for series in self.bar_series:
            color_str = f"rgb({int(series['color'].r * 255)},{int(series['color'].g * 255)},{int(series['color'].b * 255)})"

            for i in range(len(series['x'])):
                x_pos = series['x'][i]
                bar_height = series['height'][i]
                bar_width = series['width']

                # Calculate screen coordinates for bar corners
                x1 = x_pos - bar_width/2
                x2 = x_pos + bar_width/2
                y1 = 0
                y2 = bar_height

                # Convert to screen coordinates
                sx1, sy1 = data_to_screen(x1, y1)
                sx2, sy2 = data_to_screen(x2, y2)

                # Draw filled rectangle for bar
                rect_width = sx2 - sx1
                rect_height = sy1 - sy2  # sy1 > sy2 because y-axis is flipped
                svg_content += f'<rect x="{sx1}" y="{sy2}" width="{rect_width}" height="{rect_height}" fill="{color_str}" opacity="{series["alpha"]}" stroke="rgb(60,60,60)" stroke-width="1"/>\n'

        # Draw legend if there are labeled series
        if self.legend_entries:
            legend_x = self.width - 150
            legend_y = 60
            svg_content += f'<g font-size="12" font-family="Arial">\n'
            for i, entry in enumerate(self.legend_entries):
                y_pos = legend_y + i * 20
                color_str = f"rgb({int(entry['color'].r * 255)},{int(entry['color'].g * 255)},{int(entry['color'].b * 255)})"
                svg_content += f'<rect x="{legend_x}" y="{y_pos - 6}" width="20" height="12" fill="{color_str}"/>\n'
                svg_content += f'<text x="{legend_x + 25}" y="{y_pos + 4}" fill="rgb(50,50,50)">{entry["label"]}</text>\n'
            svg_content += '</g>\n'

        # Close SVG document
        svg_content += '</svg>'
        return svg_content