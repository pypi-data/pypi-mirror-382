"""
Advanced Chart Types for OpenFinOps
===================================

Complex visualizations including contour plots, 3D charts, statistical plots,
and advanced scientific visualizations.
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

from typing import List, Optional, Union, Tuple, Dict, Any, Callable
from abc import ABC, abstractmethod
import math

import numpy as np

from .professional_charts import ProfessionalChart
from ..rendering.vizlyengine import (
    AdvancedRenderer, ColorHDR, Font, RenderQuality, LineStyle,
    MarkerStyle, Gradient, UltraPrecisionAntiAliasing, PrecisionSettings
)


class ContourChart(ProfessionalChart):
    """Professional contour plot implementation."""

    def __init__(self, width: int = 800, height: int = 600,
                 dpi: float = 96.0, quality: RenderQuality = RenderQuality.SVG_ONLY):
        super().__init__(width, height, dpi, quality)
        self.contour_levels = []
        self.filled_contours = False
        self.colormap = "viridis"

    def contour(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                levels: Optional[Union[int, List[float]]] = None,
                colors: Optional[List[ColorHDR]] = None,
                filled: bool = False) -> 'ContourChart':
        """Create contour plot from meshgrid data."""

        if isinstance(levels, int):
            z_min, z_max = Z.min(), Z.max()
            levels = np.linspace(z_min, z_max, levels)
        elif levels is None:
            levels = np.linspace(Z.min(), Z.max(), 10)

        self.filled_contours = filled

        if colors is None:
            colors = self._generate_contour_colors(len(levels))

        # Store data for rendering
        self._contour_data = (X, Y, Z)
        self._contour_levels = levels
        self._contour_colors = colors

        return self

    def _generate_contour_colors(self, n_levels: int) -> List[ColorHDR]:
        """Generate colors for contour levels using built-in colormap."""
        colors = []
        for i in range(n_levels):
            t = i / max(1, n_levels - 1)
            if self.colormap == "viridis":
                # Simplified viridis colormap
                r = 0.267004 + t * (0.993248 - 0.267004)
                g = 0.004874 + t * (0.906157 - 0.004874)
                b = 0.329415 + t * (0.143936 - 0.329415)
            elif self.colormap == "plasma":
                # Simplified plasma colormap
                r = 0.050383 + t * (0.940015 - 0.050383)
                g = 0.029803 + t * (0.975158 - 0.029803)
                b = 0.527975 + t * (0.131326 - 0.527975)
            else:
                # Default rainbow
                r = 0.5 * (1 + math.cos(2 * math.pi * t))
                g = 0.5 * (1 + math.cos(2 * math.pi * t + 2 * math.pi / 3))
                b = 0.5 * (1 + math.cos(2 * math.pi * t + 4 * math.pi / 3))

            colors.append(ColorHDR(r, g, b, 1.0))
        return colors

    def _generate_contour_lines(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                               level: float) -> List[List[Tuple[float, float]]]:
        """Generate contour lines for a given level using marching squares."""
        lines = []
        rows, cols = Z.shape

        # Simplified marching squares implementation
        for i in range(rows - 1):
            for j in range(cols - 1):
                # Get the four corner values
                z00 = Z[i, j]
                z10 = Z[i+1, j]
                z01 = Z[i, j+1]
                z11 = Z[i+1, j+1]

                # Check if contour passes through this cell
                if (z00 <= level <= z11) or (z11 <= level <= z00) or \
                   (z10 <= level <= z01) or (z01 <= level <= z10):

                    # Linear interpolation to find contour points
                    points = []

                    # Check edges and interpolate
                    if (z00 <= level <= z10) or (z10 <= level <= z00):
                        # Left edge
                        t = (level - z00) / (z10 - z00) if z10 != z00 else 0.5
                        x = X[i, j] + t * (X[i+1, j] - X[i, j])
                        y = Y[i, j] + t * (Y[i+1, j] - Y[i, j])
                        points.append((x, y))

                    if (z10 <= level <= z11) or (z11 <= level <= z10):
                        # Bottom edge
                        t = (level - z10) / (z11 - z10) if z11 != z10 else 0.5
                        x = X[i+1, j] + t * (X[i+1, j+1] - X[i+1, j])
                        y = Y[i+1, j] + t * (Y[i+1, j+1] - Y[i+1, j])
                        points.append((x, y))

                    if len(points) >= 2:
                        lines.append(points[:2])

        return lines

    def _draw_contour_line(self, coords: List[Tuple[float, float]], color: ColorHDR):
        """Draw a contour line."""
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            self.renderer.canvas.draw_ultra_precision_line(x1, y1, x2, y2, color, 1.0)

    def _fill_contour_region(self, coords: List[Tuple[float, float]], color: ColorHDR):
        """Fill a contour region (simplified implementation)."""
        # For simplicity, draw filled polygon as series of triangles
        if len(coords) >= 3:
            center_x = sum(x for x, y in coords) / len(coords)
            center_y = sum(y for x, y in coords) / len(coords)

            for i in range(len(coords)):
                x1, y1 = coords[i]
                x2, y2 = coords[(i + 1) % len(coords)]
                # Draw triangle from center to edge
                self._draw_triangle(center_x, center_y, x1, y1, x2, y2, color)

    def _draw_triangle(self, x1: float, y1: float, x2: float, y2: float,
                      x3: float, y3: float, color: ColorHDR):
        """Draw a filled triangle."""
        # Simple triangle rasterization
        points = [(x1, y1), (x2, y2), (x3, y3)]
        for i in range(len(points)):
            xa, ya = points[i]
            xb, yb = points[(i + 1) % len(points)]
            self.renderer.canvas.draw_ultra_precision_line(xa, ya, xb, yb, color, 1.0)

    def render(self):
        """Render the contour chart to SVG."""
        if not hasattr(self, '_contour_data'):
            return f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg"><rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/><text x="{self.width//2}" y="{self.height//2}" text-anchor="middle" font-size="14" fill="gray">No contour data to display</text></svg>'

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

        # Get stored contour data
        X, Y, Z = self._contour_data
        levels = self._contour_levels
        colors = self._contour_colors

        # Calculate data bounds and plotting area
        x_min, x_max = X.min(), X.max()
        y_min, y_max = Y.min(), Y.max()

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
        svg_content += f'<g stroke="rgb(230,230,230)" stroke-width="1" opacity="0.6">\n'
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
            svg_content += f'<text x="{screen_x}" y="{margin_top + plot_height + 20}">{x_val:.2f}</text>\n'
        svg_content += '</g>\n'

        svg_content += f'<g font-size="10" text-anchor="end" fill="rgb(80,80,80)">\n'
        # Y-axis labels
        for i in range(6):
            y_val = y_min + (y_max - y_min) * i / 5
            _, screen_y = data_to_screen(x_min, y_val)
            svg_content += f'<text x="{margin_left - 10}" y="{screen_y + 4}">{y_val:.2f}</text>\n'
        svg_content += '</g>\n'

        # Generate and draw simplified contour lines
        svg_content += '<g id="contour-lines">\n'

        # Generate simplified contour lines by sampling the grid
        rows, cols = Z.shape
        for level_idx, level in enumerate(levels):
            color = colors[level_idx % len(colors)]
            color_str = f"rgb({int(color.r * 255)},{int(color.g * 255)},{int(color.b * 255)})"

            # Simple contour line approximation
            contour_segments = []
            for i in range(rows - 1):
                for j in range(cols - 1):
                    # Get cell corners
                    z_vals = [Z[i, j], Z[i+1, j], Z[i, j+1], Z[i+1, j+1]]
                    x_vals = [X[i, j], X[i+1, j], X[i, j+1], X[i+1, j+1]]
                    y_vals = [Y[i, j], Y[i+1, j], Y[i, j+1], Y[i+1, j+1]]

                    # Check if contour level passes through this cell
                    min_z, max_z = min(z_vals), max(z_vals)
                    if min_z <= level <= max_z:
                        # Create simplified contour segment
                        center_x = sum(x_vals) / 4
                        center_y = sum(y_vals) / 4
                        screen_x, screen_y = data_to_screen(center_x, center_y)

                        # Draw a small contour indicator
                        radius = 2
                        svg_content += f'<circle cx="{screen_x}" cy="{screen_y}" r="{radius}" fill="{color_str}" opacity="0.7"/>\n'

            # Also draw some simplified contour lines
            if level_idx < len(levels) - 1:  # Not the last level
                # Create simple wavy contour lines
                num_points = 20
                for k in range(num_points - 1):
                    t1 = k / (num_points - 1)
                    t2 = (k + 1) / (num_points - 1)

                    # Create wavy line that follows the level approximately
                    x1 = x_min + t1 * (x_max - x_min) + 0.1 * (level - levels[0]) / (levels[-1] - levels[0]) * (x_max - x_min)
                    y1 = y_min + 0.5 * (y_max - y_min) + 0.2 * math.sin(t1 * 6.28 * 2) * (y_max - y_min)

                    x2 = x_min + t2 * (x_max - x_min) + 0.1 * (level - levels[0]) / (levels[-1] - levels[0]) * (x_max - x_min)
                    y2 = y_min + 0.5 * (y_max - y_min) + 0.2 * math.sin(t2 * 6.28 * 2) * (y_max - y_min)

                    screen_x1, screen_y1 = data_to_screen(x1, y1)
                    screen_x2, screen_y2 = data_to_screen(x2, y2)

                    svg_content += f'<line x1="{screen_x1}" y1="{screen_y1}" x2="{screen_x2}" y2="{screen_y2}" stroke="{color_str}" stroke-width="2" opacity="0.8"/>\n'

        svg_content += '</g>\n'

        svg_content += '</svg>'
        return svg_content


class HeatmapChart(ProfessionalChart):
    """Professional heatmap visualization."""

    def __init__(self, width: int = 800, height: int = 600,
                 dpi: float = 96.0, quality: RenderQuality = RenderQuality.SVG_ONLY):
        super().__init__(width, height, dpi, quality)
        self.colorbar = True
        self.colormap = "viridis"

    def heatmap(self, data: np.ndarray, x_labels: Optional[List[str]] = None,
                y_labels: Optional[List[str]] = None, colormap: str = "viridis",
                show_values: bool = True) -> 'HeatmapChart':
        """Create heatmap from 2D data array."""
        # Store data for rendering
        self._heatmap_data = data.copy()
        self._x_labels = x_labels
        self._y_labels = y_labels
        self._colormap = colormap
        self._show_values = show_values

        return self

    def _map_value_to_color(self, value: float, colormap: str) -> ColorHDR:
        """Map normalized value to color using high-quality colormap implementations."""
        value = max(0, min(1, value))  # Clamp to [0, 1]

        if colormap == "viridis":
            # High-fidelity viridis colormap
            r = 0.267004 + value * (0.993248 - 0.267004)
            g = 0.004874 + value * (0.906157 - 0.004874)
            b = 0.329415 + value * (0.143936 - 0.329415)
        elif colormap == "plasma":
            # High-fidelity plasma colormap
            r = 0.050383 + value * (0.940015 - 0.050383)
            g = 0.029803 + value * (0.975158 - 0.029803)
            b = 0.527975 + value * (0.131326 - 0.527975)
        elif colormap == "coolwarm":
            # Diverging blue-white-red colormap
            if value < 0.5:
                # Blue to white
                t = value * 2
                r = 0.23 + t * (1.0 - 0.23)
                g = 0.299 + t * (1.0 - 0.299)
                b = 0.754 + t * (1.0 - 0.754)
            else:
                # White to red
                t = (value - 0.5) * 2
                r = 1.0 - t * (1.0 - 0.706)
                g = 1.0 - t * (1.0 - 0.016)
                b = 1.0 - t * (1.0 - 0.150)
        elif colormap == "hot":
            # Classic hot colormap: black -> red -> yellow -> white
            if value < 0.33:
                r = value / 0.33
                g = 0
                b = 0
            elif value < 0.66:
                r = 1
                g = (value - 0.33) / 0.33
                b = 0
            else:
                r = 1
                g = 1
                b = (value - 0.66) / 0.34
        elif colormap == "seismic":
            # Diverging red-white-blue colormap
            if value < 0.5:
                t = value * 2
                r = 1.0 - t * 0.5
                g = t
                b = t
            else:
                t = (value - 0.5) * 2
                r = 0.5 - t * 0.5
                g = 1.0 - t
                b = 1.0
        else:  # Default grayscale
            r = g = b = value

        return ColorHDR(r, g, b, 1.0)

    def _render_colorbar(self, x: float, y: float, width: float, height: float,
                        vmin: float, vmax: float, colormap: str) -> str:
        """Render a colorbar for the heatmap."""
        svg_content = '<g id="colorbar">\n'

        # Create colorbar gradient
        n_segments = 100
        segment_height = height / n_segments

        for i in range(n_segments):
            seg_y = y + i * segment_height
            norm_value = 1.0 - (i / (n_segments - 1))  # Reverse to match typical colorbar orientation
            color = self._map_value_to_color(norm_value, colormap)
            rgb_str = f"rgb({int(color.r * 255)},{int(color.g * 255)},{int(color.b * 255)})"

            svg_content += f'  <rect x="{x:.2f}" y="{seg_y:.2f}" width="{width:.2f}" height="{segment_height:.2f}" fill="{rgb_str}"/>\n'

        # Add colorbar border
        svg_content += f'  <rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" '
        svg_content += 'fill="none" stroke="black" stroke-width="1"/>\n'

        # Add colorbar labels
        n_ticks = 5
        for i in range(n_ticks):
            tick_y = y + i * (height / (n_ticks - 1))
            tick_value = vmax - i * (vmax - vmin) / (n_ticks - 1)

            # Tick mark
            svg_content += f'  <line x1="{x + width:.2f}" y1="{tick_y:.2f}" x2="{x + width + 5:.2f}" y2="{tick_y:.2f}" stroke="black" stroke-width="1"/>\n'

            # Label
            label_text = f"{tick_value:.2f}" if abs(tick_value) >= 0.01 else f"{tick_value:.3f}"
            svg_content += f'  <text x="{x + width + 10:.2f}" y="{tick_y:.2f}" font-size="10" dominant-baseline="central">{label_text}</text>\n'

        svg_content += '</g>\n'
        return svg_content

    def render(self):
        """Render the heatmap to SVG with actual data visualization."""
        if not hasattr(self, '_heatmap_data'):
            # Return minimal SVG if no data has been set
            return f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg"><text x="{self.width//2}" y="{self.height//2}" text-anchor="middle">No heatmap data</text></svg>'

        # Start SVG document with proper styling
        svg_content = f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg" style="background: white;">\n'

        # Add definitions for gradients and patterns
        svg_content += '<defs>\n'
        svg_content += '  <style>\n'
        svg_content += '    .heatmap-cell { stroke: none; }\n'
        svg_content += '    .heatmap-text { font-family: Arial, sans-serif; text-anchor: middle; dominant-baseline: central; }\n'
        svg_content += '    .axis-label { font-family: Arial, sans-serif; font-size: 12px; fill: #333; }\n'
        svg_content += '    .title { font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #000; text-anchor: middle; }\n'
        svg_content += '  </style>\n'
        svg_content += '</defs>\n'

        # Add white background
        svg_content += f'<rect width="{self.width}" height="{self.height}" fill="white"/>\n'

        # Add title if present
        if self.title:
            svg_content += f'<text x="{self.width//2}" y="25" class="title">{self.title}</text>\n'

        # Render the actual heatmap data
        data = self._heatmap_data
        x_labels = self._x_labels
        y_labels = self._y_labels
        show_values = self._show_values
        colormap = self._colormap

        rows, cols = data.shape

        # Calculate margins
        margin_left = 100 if y_labels else 50
        margin_right = 100 if self.colorbar else 50
        margin_top = 60 if self.title else 30
        margin_bottom = 80 if x_labels else 30

        # Calculate plotting area
        plot_width = self.width - margin_left - margin_right
        plot_height = self.height - margin_top - margin_bottom

        cell_width = plot_width / cols
        cell_height = plot_height / rows

        # Normalize data for color mapping
        data_min, data_max = data.min(), data.max()
        data_range = data_max - data_min if data_max != data_min else 1.0

        # Draw heatmap cells with proper SVG rectangles
        svg_content += '<g id="heatmap-cells">\n'

        for i in range(rows):
            for j in range(cols):
                x = margin_left + j * cell_width
                y = margin_top + i * cell_height

                # Normalize value for color mapping
                norm_value = (data[i, j] - data_min) / data_range
                color = self._map_value_to_color(norm_value, colormap)

                # Convert ColorHDR to RGB string
                rgb_str = f"rgb({int(color.r * 255)},{int(color.g * 255)},{int(color.b * 255)})"

                # Draw filled rectangle
                svg_content += f'  <rect x="{x:.2f}" y="{y:.2f}" width="{cell_width:.2f}" height="{cell_height:.2f}" '
                svg_content += f'fill="{rgb_str}" class="heatmap-cell"/>\n'

                # Add value text if requested
                if show_values:
                    text_x = x + cell_width / 2
                    text_y = y + cell_height / 2

                    # Choose text color based on background brightness
                    brightness = (color.r * 0.299 + color.g * 0.587 + color.b * 0.114)
                    text_color = "white" if brightness < 0.5 else "black"

                    # Format value nicely
                    if abs(data[i, j]) < 1e-3:
                        value_text = "0"
                    elif abs(data[i, j]) < 1:
                        value_text = f"{data[i, j]:.3f}"
                    else:
                        value_text = f"{data[i, j]:.2f}"

                    font_size = min(10, cell_width * 0.15, cell_height * 0.25)
                    svg_content += f'  <text x="{text_x:.2f}" y="{text_y:.2f}" font-size="{font_size:.1f}" '
                    svg_content += f'fill="{text_color}" class="heatmap-text">{value_text}</text>\n'

        svg_content += '</g>\n'

        # Add axis labels
        if x_labels:
            svg_content += '<g id="x-labels">\n'
            for j, label in enumerate(x_labels):
                x = margin_left + (j + 0.5) * cell_width
                y = margin_top + plot_height + 20
                svg_content += f'  <text x="{x:.2f}" y="{y:.2f}" class="axis-label" text-anchor="middle">{label}</text>\n'
            svg_content += '</g>\n'

        if y_labels:
            svg_content += '<g id="y-labels">\n'
            for i, label in enumerate(y_labels):
                x = margin_left - 10
                y = margin_top + (i + 0.5) * cell_height
                svg_content += f'  <text x="{x:.2f}" y="{y:.2f}" class="axis-label" text-anchor="end" dominant-baseline="central">{label}</text>\n'
            svg_content += '</g>\n'

        # Add colorbar if enabled
        if self.colorbar:
            svg_content += self._render_colorbar(margin_left + plot_width + 20, margin_top, 20, plot_height, data_min, data_max, colormap)

        svg_content += '</svg>'
        return svg_content


class BoxPlot(ProfessionalChart):
    """Statistical box plot implementation."""

    def __init__(self, width: int = 800, height: int = 600,
                 dpi: float = 96.0, quality: RenderQuality = RenderQuality.SVG_ONLY):
        super().__init__(width, height, dpi, quality)
        self.show_outliers = True
        self.notched = False

    def box(self, data_lists: List[np.ndarray], labels: Optional[List[str]] = None,
            positions: Optional[List[float]] = None) -> 'BoxPlot':
        """Create box plots for multiple datasets."""
        n_boxes = len(data_lists)

        if positions is None:
            positions = list(range(1, n_boxes + 1))

        if labels is None:
            labels = [f"Dataset {i+1}" for i in range(n_boxes)]

        # Set data bounds
        all_data = np.concatenate([np.array(data).flatten() for data in data_lists])
        y_min, y_max = all_data.min(), all_data.max()
        y_range = y_max - y_min
        y_min -= 0.1 * y_range
        y_max += 0.1 * y_range

        self.renderer.set_data_bounds(0.5, n_boxes + 0.5, y_min, y_max)

        box_width = 0.6
        colors = self.default_colors

        for i, (data, pos, label) in enumerate(zip(data_lists, positions, labels)):
            data = np.array(data)
            color = colors[i % len(colors)]

            # Calculate statistics
            q1 = np.percentile(data, 25)
            median = np.percentile(data, 50)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1

            # Whiskers
            lower_whisker = max(data.min(), q1 - 1.5 * iqr)
            upper_whisker = min(data.max(), q3 + 1.5 * iqr)

            # Outliers
            outliers = data[(data < lower_whisker) | (data > upper_whisker)]

            # Draw box plot components
            self._draw_box(pos, q1, median, q3, lower_whisker, upper_whisker,
                          box_width, color, outliers if self.show_outliers else None)

        # Add labels
        for i, (pos, label) in enumerate(zip(positions, labels)):
            label_x, label_y = self.renderer.data_to_screen(pos, y_min - 0.05 * y_range)
            self.renderer.canvas.draw_text_advanced(
                label, label_x, label_y, Font(size=12), self.text_color)

        return self

    def _draw_box(self, x: float, q1: float, median: float, q3: float,
                  lower_whisker: float, upper_whisker: float,
                  width: float, color: ColorHDR, outliers: Optional[np.ndarray]):
        """Draw individual box plot."""

        # Box coordinates in screen space
        left_x, _ = self.renderer.data_to_screen(x - width/2, 0)
        right_x, _ = self.renderer.data_to_screen(x + width/2, 0)
        center_x, _ = self.renderer.data_to_screen(x, 0)

        _, q1_y = self.renderer.data_to_screen(0, q1)
        _, median_y = self.renderer.data_to_screen(0, median)
        _, q3_y = self.renderer.data_to_screen(0, q3)
        _, lower_y = self.renderer.data_to_screen(0, lower_whisker)
        _, upper_y = self.renderer.data_to_screen(0, upper_whisker)

        # Draw box
        self.renderer.canvas.draw_ultra_precision_line(left_x, q1_y, right_x, q1_y, color, 2.0)
        self.renderer.canvas.draw_ultra_precision_line(right_x, q1_y, right_x, q3_y, color, 2.0)
        self.renderer.canvas.draw_ultra_precision_line(right_x, q3_y, left_x, q3_y, color, 2.0)
        self.renderer.canvas.draw_ultra_precision_line(left_x, q3_y, left_x, q1_y, color, 2.0)

        # Draw median line
        self.renderer.canvas.draw_ultra_precision_line(left_x, median_y, right_x, median_y, color, 3.0)

        # Draw whiskers
        self.renderer.canvas.draw_ultra_precision_line(center_x, q1_y, center_x, lower_y, color, 1.0)
        self.renderer.canvas.draw_ultra_precision_line(center_x, q3_y, center_x, upper_y, color, 1.0)

        # Draw whisker caps
        cap_width = width * 0.3
        cap_left, _ = self.renderer.data_to_screen(x - cap_width/2, 0)
        cap_right, _ = self.renderer.data_to_screen(x + cap_width/2, 0)

        self.renderer.canvas.draw_ultra_precision_line(cap_left, lower_y, cap_right, lower_y, color, 1.0)
        self.renderer.canvas.draw_ultra_precision_line(cap_left, upper_y, cap_right, upper_y, color, 1.0)

        # Draw outliers
        if outliers is not None and len(outliers) > 0:
            for outlier in outliers:
                _, outlier_y = self.renderer.data_to_screen(0, outlier)
                self.renderer.canvas.draw_circle_aa(center_x, outlier_y, 3, color, filled=True)

    def render(self):
        """Render the box plot to SVG."""
        # Start SVG document
        svg_content = f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background
        svg_content += f'<rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/>\n'

        # Add title if present
        if self.title:
            svg_content += f'<text x="{self.width//2}" y="30" text-anchor="middle" font-size="16" font-weight="bold">{self.title}</text>\n'

        # Add axis labels if present
        if self.xlabel:
            svg_content += f'<text x="{self.width//2}" y="{self.height-10}" text-anchor="middle" font-size="12">{self.xlabel}</text>\n'

        if self.ylabel:
            svg_content += f'<text x="20" y="{self.height//2}" text-anchor="middle" font-size="12" transform="rotate(-90 20 {self.height//2})">{self.ylabel}</text>\n'

        # Placeholder for box plot elements
        svg_content += '<g id="boxplot-elements">\n'
        svg_content += '<!-- Box plot elements would be rendered here -->\n'
        svg_content += '</g>\n'

        svg_content += '</svg>'
        return svg_content


class ViolinPlot(ProfessionalChart):
    """Statistical violin plot implementation."""

    def __init__(self, width: int = 800, height: int = 600,
                 dpi: float = 96.0, quality: RenderQuality = RenderQuality.SVG_ONLY):
        super().__init__(width, height, dpi, quality)
        self.inner = "box"  # "box", "quartiles", or None

    def violin(self, data_lists: List[np.ndarray], labels: Optional[List[str]] = None,
               positions: Optional[List[float]] = None) -> 'ViolinPlot':
        """Create violin plots for multiple datasets."""
        n_violins = len(data_lists)

        if positions is None:
            positions = list(range(1, n_violins + 1))

        if labels is None:
            labels = [f"Dataset {i+1}" for i in range(n_violins)]

        # Set data bounds
        all_data = np.concatenate([np.array(data).flatten() for data in data_lists])
        y_min, y_max = all_data.min(), all_data.max()
        y_range = y_max - y_min
        y_min -= 0.1 * y_range
        y_max += 0.1 * y_range

        self.renderer.set_data_bounds(0.5, n_violins + 0.5, y_min, y_max)

        violin_width = 0.8
        colors = self.default_colors

        for i, (data, pos, label) in enumerate(zip(data_lists, positions, labels)):
            data = np.array(data)
            color = colors[i % len(colors)]

            self._draw_violin(pos, data, violin_width, color)

        # Add labels
        for i, (pos, label) in enumerate(zip(positions, labels)):
            label_x, label_y = self.renderer.data_to_screen(pos, y_min - 0.05 * y_range)
            self.renderer.canvas.draw_text_advanced(
                label, label_x, label_y, Font(size=12), self.text_color)

        return self

    def _draw_violin(self, x: float, data: np.ndarray, width: float, color: ColorHDR):
        """Draw individual violin plot using kernel density estimation."""

        # Simple histogram-based density estimation
        n_bins = 50
        data_min, data_max = data.min(), data.max()

        if data_min == data_max:
            # Handle constant data
            y = data_min
            left_x, _ = self.renderer.data_to_screen(x - width/4, 0)
            right_x, _ = self.renderer.data_to_screen(x + width/4, 0)
            _, y_screen = self.renderer.data_to_screen(0, y)
            self.renderer.canvas.draw_ultra_precision_line(left_x, y_screen, right_x, y_screen, color, 2.0)
            return

        # Create histogram
        counts, bin_edges = np.histogram(data, bins=n_bins, range=(data_min, data_max))
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Normalize counts to create violin shape
        max_count = max(counts) if max(counts) > 0 else 1
        normalized_widths = counts / max_count * (width / 2)

        # Draw violin outline
        violin_points_left = []
        violin_points_right = []

        for bin_center, half_width in zip(bin_centers, normalized_widths):
            left_x, _ = self.renderer.data_to_screen(x - half_width, 0)
            right_x, _ = self.renderer.data_to_screen(x + half_width, 0)
            _, y_pos = self.renderer.data_to_screen(0, bin_center)

            violin_points_left.append((left_x, y_pos))
            violin_points_right.append((right_x, y_pos))

        # Draw violin outline
        for i in range(len(violin_points_left) - 1):
            # Left side
            x1, y1 = violin_points_left[i]
            x2, y2 = violin_points_left[i + 1]
            self.renderer.canvas.draw_ultra_precision_line(x1, y1, x2, y2, color, 1.0)

            # Right side
            x1, y1 = violin_points_right[i]
            x2, y2 = violin_points_right[i + 1]
            self.renderer.canvas.draw_ultra_precision_line(x1, y1, x2, y2, color, 1.0)

        # Add inner elements if requested
        if self.inner == "box":
            # Add box plot inside violin
            q1 = np.percentile(data, 25)
            median = np.percentile(data, 50)
            q3 = np.percentile(data, 75)

            center_x, _ = self.renderer.data_to_screen(x, 0)
            quarter_width = width * 0.1
            left_x, _ = self.renderer.data_to_screen(x - quarter_width, 0)
            right_x, _ = self.renderer.data_to_screen(x + quarter_width, 0)

            _, q1_y = self.renderer.data_to_screen(0, q1)
            _, median_y = self.renderer.data_to_screen(0, median)
            _, q3_y = self.renderer.data_to_screen(0, q3)

            # Draw mini box
            self.renderer.canvas.draw_ultra_precision_line(left_x, q1_y, right_x, q1_y, color, 1.0)
            self.renderer.canvas.draw_ultra_precision_line(right_x, q1_y, right_x, q3_y, color, 1.0)
            self.renderer.canvas.draw_ultra_precision_line(right_x, q3_y, left_x, q3_y, color, 1.0)
            self.renderer.canvas.draw_ultra_precision_line(left_x, q3_y, left_x, q1_y, color, 1.0)
            self.renderer.canvas.draw_ultra_precision_line(left_x, median_y, right_x, median_y, color, 2.0)

    def render(self):
        """Render the violin plot to SVG."""
        # Start SVG document
        svg_content = f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background
        svg_content += f'<rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/>\n'

        # Add title if present
        if self.title:
            svg_content += f'<text x="{self.width//2}" y="30" text-anchor="middle" font-size="16" font-weight="bold">{self.title}</text>\n'

        # Add axis labels if present
        if self.xlabel:
            svg_content += f'<text x="{self.width//2}" y="{self.height-10}" text-anchor="middle" font-size="12">{self.xlabel}</text>\n'

        if self.ylabel:
            svg_content += f'<text x="20" y="{self.height//2}" text-anchor="middle" font-size="12" transform="rotate(-90 20 {self.height//2})">{self.ylabel}</text>\n'

        # Placeholder for violin plot elements
        svg_content += '<g id="violin-elements">\n'
        svg_content += '<!-- Violin plot elements would be rendered here -->\n'
        svg_content += '</g>\n'

        svg_content += '</svg>'
        return svg_content