"""
Enhanced OpenFinOps API
======================

Seamless integration of professional rendering engine with matplotlib-like API.
This provides the best of both worlds: matplotlib compatibility and superior quality.
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
import warnings

import numpy as np

from .professional_charts import (
    ProfessionalLineChart, ProfessionalScatterChart, ProfessionalBarChart,
    ProfessionalChart
)
from ..rendering.vizlyengine import (
    ColorHDR, Font, RenderQuality, LineStyle, MarkerStyle
)


class EnhancedLineChart:
    """Enhanced Line Chart with professional rendering and matplotlib-like API."""

    def __init__(self, width: int = 800, height: int = 600, dpi: float = 96.0,
                 quality: str = "high", style: str = "professional"):
        """
        Create enhanced line chart.

        Parameters:
        -----------
        width : int
            Chart width in pixels
        height : int
            Chart height in pixels
        dpi : float
            Dots per inch for high-resolution output
        quality : str
            Rendering quality: 'fast', 'balanced', 'high', 'ultra'
        style : str
            Chart style: 'professional', 'dark', 'minimal'
        """
        # Map string quality to enum
        quality_map = {
            'fast': RenderQuality.FAST,
            'balanced': RenderQuality.BALANCED,
            'high': RenderQuality.HIGH,
            'ultra': RenderQuality.ULTRA
        }

        self._chart = ProfessionalLineChart(
            width=width, height=height, dpi=dpi,
            quality=quality_map.get(quality, RenderQuality.HIGH)
        )
        self._chart.set_style(style)

        # Store parameters
        self.width = width
        self.height = height
        self.dpi = dpi

    def plot(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list],
             color: Union[str, tuple] = None, linewidth: float = 2.0,
             linestyle: str = 'solid', marker: str = None,
             markersize: float = 6.0, alpha: float = 1.0,
             label: str = "", smooth: bool = False) -> 'EnhancedLineChart':
        """
        Plot line with matplotlib-compatible API.

        Parameters:
        -----------
        x, y : array-like
            Data coordinates
        color : str or tuple
            Line color (supports hex, named colors, RGB tuples)
        linewidth : float
            Line width
        linestyle : str
            Line style: 'solid', 'dashed', 'dotted', 'dashdot'
        marker : str
            Marker style: 'o', 's', '^', 'D', '*', '+', 'x'
        markersize : float
            Marker size
        alpha : float
            Transparency (0-1)
        label : str
            Legend label
        smooth : bool
            Enable smooth curve interpolation
        """
        # Convert color formats
        if color is None:
            chart_color = None  # Auto-select
        elif isinstance(color, str):
            if color.startswith('#'):
                chart_color = ColorHDR.from_hex(color)
            else:
                chart_color = self._named_color_to_hdr(color)
        elif isinstance(color, (tuple, list)):
            if len(color) == 3:
                chart_color = ColorHDR(color[0], color[1], color[2], 1.0)
            elif len(color) == 4:
                chart_color = ColorHDR(color[0], color[1], color[2], color[3])
            else:
                raise ValueError("Color tuple must have 3 or 4 elements")
        else:
            chart_color = None

        # Convert line style
        style_map = {
            'solid': LineStyle.SOLID,
            '-': LineStyle.SOLID,
            'dashed': LineStyle.DASHED,
            '--': LineStyle.DASHED,
            'dotted': LineStyle.DOTTED,
            ':': LineStyle.DOTTED,
            'dashdot': LineStyle.DASHDOT,
            '-.': LineStyle.DASHDOT
        }
        chart_style = style_map.get(linestyle, LineStyle.SOLID)

        # Convert marker style
        marker_map = {
            'o': MarkerStyle.CIRCLE,
            's': MarkerStyle.SQUARE,
            '^': MarkerStyle.TRIANGLE,
            'D': MarkerStyle.DIAMOND,
            '*': MarkerStyle.STAR,
            '+': MarkerStyle.PLUS,
            'x': MarkerStyle.CROSS
        }
        chart_marker = marker_map.get(marker) if marker else None

        # Plot using professional engine
        self._chart.plot(
            x=x, y=y, color=chart_color, line_width=linewidth,
            line_style=chart_style, marker=chart_marker,
            marker_size=markersize, alpha=alpha, label=label, smooth=smooth
        )

        return self

    def _named_color_to_hdr(self, color_name: str) -> ColorHDR:
        """Convert named color to HDR color."""
        color_map = {
            'red': ColorHDR(1.0, 0.0, 0.0, 1.0),
            'blue': ColorHDR(0.0, 0.0, 1.0, 1.0),
            'green': ColorHDR(0.0, 1.0, 0.0, 1.0),
            'black': ColorHDR(0.0, 0.0, 0.0, 1.0),
            'white': ColorHDR(1.0, 1.0, 1.0, 1.0),
            'orange': ColorHDR(1.0, 0.5, 0.0, 1.0),
            'purple': ColorHDR(0.5, 0.0, 0.5, 1.0),
            'yellow': ColorHDR(1.0, 1.0, 0.0, 1.0),
            'cyan': ColorHDR(0.0, 1.0, 1.0, 1.0),
            'magenta': ColorHDR(1.0, 0.0, 1.0, 1.0),
            'gray': ColorHDR(0.5, 0.5, 0.5, 1.0),
            'grey': ColorHDR(0.5, 0.5, 0.5, 1.0),
        }
        return color_map.get(color_name.lower(), ColorHDR(0.0, 0.0, 0.0, 1.0))

    def set_title(self, title: str, fontsize: float = 16) -> 'EnhancedLineChart':
        """Set chart title (matplotlib-compatible)."""
        self._chart.set_title(title, font_size=fontsize)
        return self

    def set_xlabel(self, xlabel: str, fontsize: float = 12) -> 'EnhancedLineChart':
        """Set X-axis label (matplotlib-compatible)."""
        current_ylabel = self._chart.ylabel
        self._chart.set_labels(xlabel=xlabel, ylabel=current_ylabel, font_size=fontsize)
        return self

    def set_ylabel(self, ylabel: str, fontsize: float = 12) -> 'EnhancedLineChart':
        """Set Y-axis label (matplotlib-compatible)."""
        current_xlabel = self._chart.xlabel
        self._chart.set_labels(xlabel=current_xlabel, ylabel=ylabel, font_size=fontsize)
        return self

    def grid(self, visible: bool = True, alpha: float = 0.3) -> 'EnhancedLineChart':
        """Enable/disable grid (matplotlib-compatible)."""
        # Grid is handled automatically in professional charts
        return self

    def legend(self, loc: str = 'upper_right') -> 'EnhancedLineChart':
        """Add legend (matplotlib-compatible)."""
        # Legend is handled automatically when labels are provided
        return self

    def annotate(self, text: str, xy: tuple, fontsize: float = 10,
                 arrow: bool = True) -> 'EnhancedLineChart':
        """Add annotation (matplotlib-compatible)."""
        self._chart.add_annotation(xy[0], xy[1], text, arrow=arrow, font_size=fontsize)
        return self

    def set_style(self, style: str) -> 'EnhancedLineChart':
        """Set chart style theme."""
        self._chart.set_style(style)
        return self

    def savefig(self, filename: str, dpi: float = None, format: str = None,
                bbox_inches: str = 'tight') -> None:
        """Save figure (matplotlib-compatible)."""
        # Determine format from filename if not specified
        if format is None:
            if filename.endswith('.png'):
                format = 'png'
            elif filename.endswith('.svg'):
                format = 'svg'
            else:
                format = 'png'  # Default

        # Use specified DPI or chart DPI
        save_dpi = dpi if dpi else self.dpi

        self._chart.save(filename, format=format, dpi=save_dpi)

    def show(self) -> None:
        """Display chart (matplotlib-compatible)."""
        self._chart.show()

    def render(self) -> str:
        """Manually trigger rendering and return SVG."""
        return self._chart.render()

    @property
    def figure(self):
        """Access underlying professional chart object."""
        return self._chart


class EnhancedScatterChart:
    """Enhanced Scatter Chart with professional rendering."""

    def __init__(self, width: int = 800, height: int = 600, dpi: float = 96.0,
                 quality: str = "high", style: str = "professional"):
        quality_map = {
            'fast': RenderQuality.FAST,
            'balanced': RenderQuality.BALANCED,
            'high': RenderQuality.HIGH,
            'ultra': RenderQuality.ULTRA
        }

        self._chart = ProfessionalScatterChart(
            width=width, height=height, dpi=dpi,
            quality=quality_map.get(quality, RenderQuality.HIGH)
        )
        self._chart.set_style(style)

        self.width = width
        self.height = height
        self.dpi = dpi

    def scatter(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list],
                s: Union[float, np.ndarray, list] = 20.0,
                c: Union[str, tuple, np.ndarray, list] = None,
                marker: str = 'o', alpha: float = 1.0,
                label: str = "") -> 'EnhancedScatterChart':
        """Create scatter plot (matplotlib-compatible)."""
        # Convert color
        if c is None:
            chart_colors = None
        elif isinstance(c, str):
            if c.startswith('#'):
                chart_colors = ColorHDR.from_hex(c)
            else:
                chart_colors = self._named_color_to_hdr(c)
        else:
            chart_colors = c  # Pass through for array colors

        # Convert marker
        marker_map = {'o': MarkerStyle.CIRCLE, 's': MarkerStyle.SQUARE}
        chart_marker = marker_map.get(marker, MarkerStyle.CIRCLE)

        self._chart.scatter(
            x=x, y=y, s=s, c=chart_colors,
            marker=chart_marker, alpha=alpha, label=label
        )
        return self

    def plot(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list],
             s: Union[float, np.ndarray, list] = 20.0,
             c: Union[str, tuple, np.ndarray, list] = None,
             marker: str = 'o', alpha: float = 1.0,
             label: str = "") -> 'EnhancedScatterChart':
        """Alias for scatter method - create scatter plot (matplotlib-compatible)."""
        return self.scatter(x, y, s, c, marker, alpha, label)

    def render(self) -> str:
        """Manually trigger rendering and return SVG."""
        return self._chart.render()

    def _named_color_to_hdr(self, color_name: str) -> ColorHDR:
        """Convert named color to HDR color."""
        color_map = {
            'red': ColorHDR(1.0, 0.0, 0.0, 1.0),
            'blue': ColorHDR(0.0, 0.0, 1.0, 1.0),
            'green': ColorHDR(0.0, 1.0, 0.0, 1.0),
        }
        return color_map.get(color_name.lower(), ColorHDR(0.0, 0.0, 0.0, 1.0))

    # Common methods
    def set_title(self, title: str, fontsize: float = 16):
        self._chart.set_title(title, font_size=fontsize); return self
    def set_xlabel(self, xlabel: str, fontsize: float = 12):
        self._chart.set_labels(xlabel=xlabel, ylabel=self._chart.ylabel, font_size=fontsize); return self
    def set_ylabel(self, ylabel: str, fontsize: float = 12):
        self._chart.set_labels(xlabel=self._chart.xlabel, ylabel=ylabel, font_size=fontsize); return self
    def savefig(self, filename: str, dpi: float = None, format: str = None):
        fmt = format or ('png' if filename.endswith('.png') else 'svg')
        self._chart.save(filename, format=fmt, dpi=dpi or self.dpi)
    def show(self): self._chart.show()
    def set_style(self, style: str): self._chart.set_style(style); return self

    @property
    def figure(self): return self._chart


class EnhancedBarChart:
    """Enhanced Bar Chart with professional rendering."""

    def __init__(self, width: int = 800, height: int = 600, dpi: float = 96.0,
                 quality: str = "high", style: str = "professional"):
        quality_map = {
            'fast': RenderQuality.FAST,
            'balanced': RenderQuality.BALANCED,
            'high': RenderQuality.HIGH,
            'ultra': RenderQuality.ULTRA
        }

        self._chart = ProfessionalBarChart(
            width=width, height=height, dpi=dpi,
            quality=quality_map.get(quality, RenderQuality.HIGH)
        )
        self._chart.set_style(style)

        self.width = width
        self.height = height
        self.dpi = dpi

    def bar(self, x: Union[np.ndarray, list], height: Union[np.ndarray, list],
            width: float = 0.8, color: Union[str, tuple] = None,
            alpha: float = 1.0, label: str = "") -> 'EnhancedBarChart':
        """Create bar chart (matplotlib-compatible)."""
        # Convert color
        if color is None:
            chart_color = None
        elif isinstance(color, str):
            if color.startswith('#'):
                chart_color = ColorHDR.from_hex(color)
            else:
                chart_color = self._named_color_to_hdr(color)
        else:
            chart_color = ColorHDR(color[0], color[1], color[2],
                                  color[3] if len(color) > 3 else 1.0)

        self._chart.bar(
            x=x, height=height, width=width, color=chart_color,
            alpha=alpha, label=label
        )
        return self

    def plot(self, height: Union[np.ndarray, list], x: Union[np.ndarray, list] = None,
             width: float = 0.8, color: Union[str, tuple] = None,
             alpha: float = 1.0, label: str = "") -> 'EnhancedBarChart':
        """Alias for bar method - create bar chart (matplotlib-compatible)."""
        if x is None:
            x = range(len(height))
        return self.bar(x, height, width, color, alpha, label)

    def render(self) -> str:
        """Manually trigger rendering and return SVG."""
        return self._chart.render()

    def _named_color_to_hdr(self, color_name: str) -> ColorHDR:
        """Convert named color to HDR color."""
        color_map = {
            'red': ColorHDR(1.0, 0.0, 0.0, 1.0),
            'blue': ColorHDR(0.0, 0.0, 1.0, 1.0),
            'green': ColorHDR(0.0, 1.0, 0.0, 1.0),
            'orange': ColorHDR(1.0, 0.5, 0.0, 1.0),
        }
        return color_map.get(color_name.lower(), ColorHDR(0.0, 0.0, 0.0, 1.0))

    # Common methods
    def set_title(self, title: str, fontsize: float = 16):
        self._chart.set_title(title, font_size=fontsize); return self
    def set_xlabel(self, xlabel: str, fontsize: float = 12):
        self._chart.set_labels(xlabel=xlabel, ylabel=self._chart.ylabel, font_size=fontsize); return self
    def set_ylabel(self, ylabel: str, fontsize: float = 12):
        self._chart.set_labels(xlabel=self._chart.xlabel, ylabel=ylabel, font_size=fontsize); return self
    def savefig(self, filename: str, dpi: float = None, format: str = None):
        fmt = format or ('png' if filename.endswith('.png') else 'svg')
        self._chart.save(filename, format=fmt, dpi=dpi or self.dpi)
    def show(self): self._chart.show()
    def set_style(self, style: str): self._chart.set_style(style); return self

    @property
    def figure(self): return self._chart


# Convenience functions for matplotlib-style usage
def linechart(width: int = 800, height: int = 600, **kwargs) -> EnhancedLineChart:
    """Create enhanced line chart with matplotlib-style API."""
    return EnhancedLineChart(width=width, height=height, **kwargs)

def scatterchart(width: int = 800, height: int = 600, **kwargs) -> EnhancedScatterChart:
    """Create enhanced scatter chart with matplotlib-style API."""
    return EnhancedScatterChart(width=width, height=height, **kwargs)

def barchart(width: int = 800, height: int = 600, **kwargs) -> EnhancedBarChart:
    """Create enhanced bar chart with matplotlib-style API."""
    return EnhancedBarChart(width=width, height=height, **kwargs)