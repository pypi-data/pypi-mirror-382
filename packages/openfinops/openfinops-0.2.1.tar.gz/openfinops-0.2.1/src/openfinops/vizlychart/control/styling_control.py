"""
Styling Control API
===================

Fine-grained control over colors, fonts, line styles, markers, and visual appearance.
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

from ..rendering.vizlyengine import ColorHDR, Font, LineStyle


@dataclass
class ColorPalette:
    """Predefined color palette for consistent styling."""
    name: str
    colors: List[ColorHDR]

    @classmethod
    def default(cls) -> 'ColorPalette':
        """Default OpenFinOps color palette."""
        return cls("default", [
            ColorHDR.from_hex('#1f77b4'),  # Blue
            ColorHDR.from_hex('#ff7f0e'),  # Orange
            ColorHDR.from_hex('#2ca02c'),  # Green
            ColorHDR.from_hex('#d62728'),  # Red
            ColorHDR.from_hex('#9467bd'),  # Purple
            ColorHDR.from_hex('#8c564b'),  # Brown
            ColorHDR.from_hex('#e377c2'),  # Pink
            ColorHDR.from_hex('#7f7f7f'),  # Gray
            ColorHDR.from_hex('#bcbd22'),  # Olive
            ColorHDR.from_hex('#17becf'),  # Cyan
        ])

    @classmethod
    def scientific(cls) -> 'ColorPalette':
        """Scientific publication friendly palette."""
        return cls("scientific", [
            ColorHDR.from_hex('#0173B2'),  # Blue
            ColorHDR.from_hex('#DE8F05'),  # Orange
            ColorHDR.from_hex('#029E73'),  # Green
            ColorHDR.from_hex('#CC78BC'),  # Pink
            ColorHDR.from_hex('#CA9161'),  # Brown
            ColorHDR.from_hex('#FBAFE4'),  # Light Pink
            ColorHDR.from_hex('#949494'),  # Gray
            ColorHDR.from_hex('#ECE133'),  # Yellow
        ])

    @classmethod
    def colorblind_friendly(cls) -> 'ColorPalette':
        """Colorblind-friendly palette."""
        return cls("colorblind_friendly", [
            ColorHDR.from_hex('#1170aa'),  # Blue
            ColorHDR.from_hex('#fc7d0b'),  # Orange
            ColorHDR.from_hex('#a3acb9'),  # Gray
            ColorHDR.from_hex('#57606c'),  # Dark Gray
            ColorHDR.from_hex('#5fa2ce'),  # Light Blue
            ColorHDR.from_hex('#c85200'),  # Dark Orange
            ColorHDR.from_hex('#7b848f'),  # Medium Gray
            ColorHDR.from_hex('#a3cce9'),  # Very Light Blue
        ])


@dataclass
class MarkerStyle:
    """Marker appearance properties."""
    shape: str = "circle"  # circle, square, diamond, triangle, cross, plus, star
    size: float = 6.0
    edge_width: float = 1.0
    edge_color: ColorHDR = None
    face_color: ColorHDR = None
    alpha: float = 1.0

    def __post_init__(self):
        if self.edge_color is None:
            self.edge_color = ColorHDR(0, 0, 0, 1)
        if self.face_color is None:
            self.face_color = ColorHDR(0.3, 0.6, 0.9, 1)


@dataclass
class TextStyle:
    """Text appearance properties."""
    font: Font = None
    color: ColorHDR = None
    alpha: float = 1.0
    rotation: float = 0.0
    horizontal_alignment: str = "center"  # left, center, right
    vertical_alignment: str = "center"    # top, center, bottom, baseline
    bbox: Optional[Dict[str, Any]] = None  # Background box properties

    def __post_init__(self):
        if self.font is None:
            self.font = Font(family="Arial", size=12, weight="normal", style="normal")
        if self.color is None:
            self.color = ColorHDR(0, 0, 0, 1)


class LegendControl:
    """Fine-grained control over legend appearance."""

    def __init__(self, chart):
        self.chart = chart
        self.visible = True
        self.location = "best"  # best, upper right, upper left, lower left, etc.
        self.bbox_to_anchor = None
        self.ncol = 1
        self.fontsize = 10
        self.title = None
        self.title_fontsize = 12
        self.frameon = True
        self.fancybox = True
        self.shadow = False
        self.framealpha = 0.8
        self.facecolor = ColorHDR(1, 1, 1, 1)
        self.edgecolor = ColorHDR(0, 0, 0, 1)
        self.mode = None
        self.bbox_transform = None
        self.columnspacing = 2.0
        self.handlelength = 2.0
        self.handletextpad = 0.8
        self.borderpad = 0.4
        self.markerscale = 1.0

    def set_location(self, location: Union[str, Tuple[float, float]]) -> 'LegendControl':
        """Set legend location."""
        self.location = location
        return self

    def set_bbox_to_anchor(self, bbox: Tuple[float, float, float, float]) -> 'LegendControl':
        """Set bounding box for legend positioning."""
        self.bbox_to_anchor = bbox
        return self

    def set_columns(self, ncol: int) -> 'LegendControl':
        """Set number of columns in legend."""
        self.ncol = ncol
        return self

    def set_fontsize(self, size: float) -> 'LegendControl':
        """Set legend font size."""
        self.fontsize = size
        return self

    def set_title(self, title: str, fontsize: float = None) -> 'LegendControl':
        """Set legend title."""
        self.title = title
        if fontsize is not None:
            self.title_fontsize = fontsize
        return self

    def set_frame(self, visible: bool, alpha: float = None,
                  facecolor: ColorHDR = None, edgecolor: ColorHDR = None) -> 'LegendControl':
        """Control legend frame appearance."""
        self.frameon = visible
        if alpha is not None:
            self.framealpha = alpha
        if facecolor is not None:
            self.facecolor = facecolor
        if edgecolor is not None:
            self.edgecolor = edgecolor
        return self


class TextControl:
    """Fine-grained control over text elements."""

    def __init__(self, chart):
        self.chart = chart
        self.title_style = TextStyle(font=Font(size=16, weight="bold"))
        self.subtitle_style = TextStyle(font=Font(size=14, weight="normal"))
        self.axis_label_style = TextStyle(font=Font(size=12, weight="bold"))
        self.tick_label_style = TextStyle(font=Font(size=10, weight="normal"))
        self.annotation_style = TextStyle(font=Font(size=9, weight="normal"))

    def set_title_style(self, **kwargs) -> 'TextControl':
        """Set title text style."""
        self._update_text_style(self.title_style, **kwargs)
        return self

    def set_axis_label_style(self, **kwargs) -> 'TextControl':
        """Set axis label text style."""
        self._update_text_style(self.axis_label_style, **kwargs)
        return self

    def set_tick_label_style(self, **kwargs) -> 'TextControl':
        """Set tick label text style."""
        self._update_text_style(self.tick_label_style, **kwargs)
        return self

    def _update_text_style(self, style: TextStyle, **kwargs):
        """Update text style with provided parameters."""
        for key, value in kwargs.items():
            if key == 'fontsize':
                style.font.size = value
            elif key == 'fontweight':
                style.font.weight = value
            elif key == 'fontfamily':
                style.font.family = value
            elif key == 'color':
                style.color = value if isinstance(value, ColorHDR) else ColorHDR.from_hex(value)
            elif key == 'rotation':
                style.rotation = value
            elif key == 'ha' or key == 'horizontalalignment':
                style.horizontal_alignment = value
            elif key == 'va' or key == 'verticalalignment':
                style.vertical_alignment = value
            elif key == 'alpha':
                style.alpha = value


class ColorControl:
    """Fine-grained control over color schemes and palettes."""

    def __init__(self, chart):
        self.chart = chart
        self.current_palette = ColorPalette.default()
        self.color_cycle = []
        self.colormap = "viridis"

    def set_palette(self, palette: Union[str, ColorPalette, List[ColorHDR]]) -> 'ColorControl':
        """Set color palette."""
        if isinstance(palette, str):
            if palette == "default":
                self.current_palette = ColorPalette.default()
            elif palette == "scientific":
                self.current_palette = ColorPalette.scientific()
            elif palette == "colorblind_friendly":
                self.current_palette = ColorPalette.colorblind_friendly()
            else:
                raise ValueError(f"Unknown palette: {palette}")
        elif isinstance(palette, ColorPalette):
            self.current_palette = palette
        elif isinstance(palette, list):
            self.current_palette = ColorPalette("custom", palette)

        self.color_cycle = list(self.current_palette.colors)
        return self

    def set_colormap(self, colormap: str) -> 'ColorControl':
        """Set colormap for continuous color mapping."""
        self.colormap = colormap
        return self

    def get_next_color(self) -> ColorHDR:
        """Get next color from the current cycle."""
        if not self.color_cycle:
            self.color_cycle = list(self.current_palette.colors)

        return self.color_cycle.pop(0)

    def add_custom_color(self, color: Union[str, ColorHDR]) -> 'ColorControl':
        """Add custom color to current palette."""
        if isinstance(color, str):
            color = ColorHDR.from_hex(color)

        self.current_palette.colors.append(color)
        self.color_cycle.append(color)
        return self

    def interpolate_colors(self, color1: ColorHDR, color2: ColorHDR,
                          steps: int) -> List[ColorHDR]:
        """Create color gradient between two colors."""
        colors = []
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            r = color1.r + (color2.r - color1.r) * t
            g = color1.g + (color2.g - color1.g) * t
            b = color1.b + (color2.b - color1.b) * t
            a = color1.a + (color2.a - color1.a) * t
            colors.append(ColorHDR(r, g, b, a))
        return colors


class LineStyleControl:
    """Fine-grained control over line styles."""

    def __init__(self, chart):
        self.chart = chart
        self.default_width = 2.0
        self.default_style = LineStyle.SOLID
        self.default_alpha = 1.0
        self.default_cap_style = "round"  # butt, round, projecting
        self.default_join_style = "round"  # miter, round, bevel

    def create_style(self, width: float = None, style: LineStyle = None,
                    alpha: float = None, color: ColorHDR = None,
                    cap_style: str = None, join_style: str = None) -> Dict[str, Any]:
        """Create line style dictionary."""
        return {
            'width': width or self.default_width,
            'style': style or self.default_style,
            'alpha': alpha or self.default_alpha,
            'color': color,
            'cap_style': cap_style or self.default_cap_style,
            'join_style': join_style or self.default_join_style
        }

    def set_defaults(self, width: float = None, style: LineStyle = None,
                    alpha: float = None) -> 'LineStyleControl':
        """Set default line style parameters."""
        if width is not None:
            self.default_width = width
        if style is not None:
            self.default_style = style
        if alpha is not None:
            self.default_alpha = alpha
        return self


class MarkerControl:
    """Fine-grained control over marker styles."""

    def __init__(self, chart):
        self.chart = chart
        self.default_style = MarkerStyle()
        self.marker_cycle = ['circle', 'square', 'triangle', 'diamond', 'cross', 'plus', 'star']

    def create_marker(self, shape: str = None, size: float = None,
                     edge_color: ColorHDR = None, face_color: ColorHDR = None,
                     edge_width: float = None, alpha: float = None) -> MarkerStyle:
        """Create marker style."""
        return MarkerStyle(
            shape=shape or self.default_style.shape,
            size=size or self.default_style.size,
            edge_color=edge_color or self.default_style.edge_color,
            face_color=face_color or self.default_style.face_color,
            edge_width=edge_width or self.default_style.edge_width,
            alpha=alpha or self.default_style.alpha
        )

    def set_defaults(self, **kwargs) -> 'MarkerControl':
        """Set default marker parameters."""
        for key, value in kwargs.items():
            if hasattr(self.default_style, key):
                setattr(self.default_style, key, value)
        return self

    def get_next_marker_shape(self) -> str:
        """Get next marker shape from cycle."""
        shape = self.marker_cycle[0]
        self.marker_cycle = self.marker_cycle[1:] + [self.marker_cycle[0]]
        return shape


class StyleManager:
    """Central style management for charts."""

    def __init__(self, chart):
        self.chart = chart
        self.legend = LegendControl(chart)
        self.text = TextControl(chart)
        self.color = ColorControl(chart)
        self.line_style = LineStyleControl(chart)
        self.marker = MarkerControl(chart)

        # Global style properties
        self.background_color = ColorHDR(1, 1, 1, 1)
        self.figure_facecolor = ColorHDR(1, 1, 1, 1)
        self.axes_facecolor = ColorHDR(1, 1, 1, 1)

    def set_theme(self, theme: str) -> 'StyleManager':
        """Apply predefined theme."""
        if theme == "default":
            self._apply_default_theme()
        elif theme == "dark":
            self._apply_dark_theme()
        elif theme == "scientific":
            self._apply_scientific_theme()
        elif theme == "minimal":
            self._apply_minimal_theme()
        else:
            raise ValueError(f"Unknown theme: {theme}")

        return self

    def _apply_default_theme(self):
        """Apply default OpenFinOps theme."""
        self.background_color = ColorHDR(1, 1, 1, 1)
        self.figure_facecolor = ColorHDR(1, 1, 1, 1)
        self.axes_facecolor = ColorHDR(1, 1, 1, 1)
        self.color.set_palette("default")

    def _apply_dark_theme(self):
        """Apply dark theme."""
        self.background_color = ColorHDR(0.1, 0.1, 0.1, 1)
        self.figure_facecolor = ColorHDR(0.1, 0.1, 0.1, 1)
        self.axes_facecolor = ColorHDR(0.15, 0.15, 0.15, 1)

        # Update text colors for dark theme
        self.text.title_style.color = ColorHDR(0.9, 0.9, 0.9, 1)
        self.text.axis_label_style.color = ColorHDR(0.9, 0.9, 0.9, 1)
        self.text.tick_label_style.color = ColorHDR(0.8, 0.8, 0.8, 1)

    def _apply_scientific_theme(self):
        """Apply scientific publication theme."""
        self.background_color = ColorHDR(1, 1, 1, 1)
        self.figure_facecolor = ColorHDR(1, 1, 1, 1)
        self.axes_facecolor = ColorHDR(1, 1, 1, 1)
        self.color.set_palette("scientific")

        # Scientific typography
        self.text.title_style.font.family = "Times New Roman"
        self.text.axis_label_style.font.family = "Times New Roman"
        self.text.tick_label_style.font.family = "Times New Roman"

    def _apply_minimal_theme(self):
        """Apply minimal theme."""
        self.background_color = ColorHDR(1, 1, 1, 1)
        self.figure_facecolor = ColorHDR(1, 1, 1, 1)
        self.axes_facecolor = ColorHDR(1, 1, 1, 1)

        # Minimal styling
        self.line_style.default_width = 1.0
        self.legend.frameon = False

    def set_background_color(self, color: Union[str, ColorHDR]) -> 'StyleManager':
        """Set background color."""
        if isinstance(color, str):
            color = ColorHDR.from_hex(color)
        self.background_color = color
        self.figure_facecolor = color
        return self

    def set_axes_facecolor(self, color: Union[str, ColorHDR]) -> 'StyleManager':
        """Set axes background color."""
        if isinstance(color, str):
            color = ColorHDR.from_hex(color)
        self.axes_facecolor = color
        return self