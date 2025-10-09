"""
Axes and Layout Control
======================

Fine-grained control over chart axes, ticks, grids, and layout elements.
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
from dataclasses import dataclass
import math

import numpy as np

from ..rendering.vizlyengine import ColorHDR, Font, LineStyle


@dataclass
class TickProperties:
    """Properties for axis ticks."""
    major_length: float = 5.0
    minor_length: float = 3.0
    major_width: float = 1.0
    minor_width: float = 0.5
    major_color: ColorHDR = None
    minor_color: ColorHDR = None
    direction: str = "out"  # "in", "out", "inout"
    labelsize: float = 10.0
    labelcolor: ColorHDR = None
    labelfont: Font = None
    labelrotation: float = 0.0
    labelpad: float = 4.0

    def __post_init__(self):
        if self.major_color is None:
            self.major_color = ColorHDR(0, 0, 0, 1)
        if self.minor_color is None:
            self.minor_color = ColorHDR(0.5, 0.5, 0.5, 1)
        if self.labelcolor is None:
            self.labelcolor = ColorHDR(0, 0, 0, 1)
        if self.labelfont is None:
            self.labelfont = Font(size=10)


@dataclass
class SpineProperties:
    """Properties for axis spines."""
    visible: bool = True
    color: ColorHDR = None
    linewidth: float = 1.0
    linestyle: LineStyle = None
    position: str = "data"  # "data", "axes", "outward"
    position_offset: float = 0.0

    def __post_init__(self):
        if self.color is None:
            self.color = ColorHDR(0, 0, 0, 1)
        if self.linestyle is None:
            self.linestyle = LineStyle.SOLID


@dataclass
class GridProperties:
    """Properties for grid lines."""
    visible: bool = True
    color: ColorHDR = None
    linewidth: float = 0.8
    linestyle: LineStyle = None
    alpha: float = 0.5
    which: str = "major"  # "major", "minor", "both"

    def __post_init__(self):
        if self.color is None:
            self.color = ColorHDR(0.8, 0.8, 0.8, 0.5)
        if self.linestyle is None:
            self.linestyle = LineStyle.SOLID


class AxisControl:
    """Fine-grained control over individual axis properties."""

    def __init__(self, chart, axis: str = "x"):
        self.chart = chart
        self.axis = axis  # "x" or "y"

        # Axis properties
        self.label = ""
        self.label_font = Font(size=12, weight="bold")
        self.label_color = ColorHDR(0, 0, 0, 1)
        self.label_pad = 10.0

        # Tick properties
        self.ticks = TickProperties()
        self.tick_positions = None  # Auto-calculated if None
        self.tick_labels = None     # Auto-generated if None

        # Spine properties
        self.spines = {
            "top": SpineProperties(visible=True),
            "bottom": SpineProperties(visible=True),
            "left": SpineProperties(visible=True),
            "right": SpineProperties(visible=True)
        }

        # Limits
        self.xlim = None
        self.ylim = None

        # Scale
        self.scale = "linear"  # "linear", "log", "symlog"

    def set_label(self, label: str, fontsize: float = None, color: ColorHDR = None,
                  fontweight: str = None, fontfamily: str = None) -> 'AxisControl':
        """Set axis label with detailed formatting."""
        self.label = label
        if fontsize is not None:
            self.label_font.size = fontsize
        if color is not None:
            self.label_color = color
        if fontweight is not None:
            self.label_font.weight = fontweight
        if fontfamily is not None:
            self.label_font.family = fontfamily
        return self

    def set_ticks(self, positions: List[float] = None, labels: List[str] = None,
                  minor: bool = False, **tick_params) -> 'AxisControl':
        """Set tick positions and labels with detailed formatting."""
        if positions is not None:
            self.tick_positions = np.array(positions)
        if labels is not None:
            self.tick_labels = labels

        # Update tick properties
        for param, value in tick_params.items():
            if hasattr(self.ticks, param):
                setattr(self.ticks, param, value)

        return self

    def set_ticklabels(self, labels: List[str], rotation: float = 0,
                       ha: str = "center", va: str = "center",
                       fontsize: float = None, color: ColorHDR = None) -> 'AxisControl':
        """Set tick label formatting."""
        self.tick_labels = labels
        self.ticks.labelrotation = rotation
        if fontsize is not None:
            self.ticks.labelsize = fontsize
            self.ticks.labelfont.size = fontsize
        if color is not None:
            self.ticks.labelcolor = color
        return self

    def set_major_locator(self, locator: 'TickLocator') -> 'AxisControl':
        """Set major tick locator."""
        self.major_locator = locator
        return self

    def set_minor_locator(self, locator: 'TickLocator') -> 'AxisControl':
        """Set minor tick locator."""
        self.minor_locator = locator
        return self

    def set_major_formatter(self, formatter: 'TickFormatter') -> 'AxisControl':
        """Set major tick formatter."""
        self.major_formatter = formatter
        return self

    def set_scale(self, scale: str, **kwargs) -> 'AxisControl':
        """Set axis scale."""
        self.scale = scale
        # Handle scale-specific parameters
        if scale == "log":
            self.log_base = kwargs.get("base", 10)
        elif scale == "symlog":
            self.symlog_threshold = kwargs.get("linthresh", 1.0)
        return self

    def set_lim(self, left: float = None, right: float = None) -> 'AxisControl':
        """Set axis limits."""
        if self.axis == "x":
            self.xlim = (left, right)
        else:
            self.ylim = (left, right)
        return self

    def invert_axis(self) -> 'AxisControl':
        """Invert the axis direction."""
        self.inverted = True
        return self

    def grid(self, visible: bool = True, which: str = "major",
             color: ColorHDR = None, linestyle: LineStyle = None,
             linewidth: float = None, alpha: float = None) -> 'AxisControl':
        """Control grid appearance."""
        self.grid_props = GridProperties(
            visible=visible,
            which=which,
            color=color or ColorHDR(0.8, 0.8, 0.8, 0.5),
            linestyle=linestyle or LineStyle.SOLID,
            linewidth=linewidth or 0.8,
            alpha=alpha or 0.5
        )
        return self

    def spine_set_visible(self, spine: str, visible: bool) -> 'AxisControl':
        """Set spine visibility."""
        if spine in self.spines:
            self.spines[spine].visible = visible
        return self

    def spine_set_position(self, spine: str, position: Union[str, Tuple[str, float]]) -> 'AxisControl':
        """Set spine position."""
        if spine in self.spines:
            if isinstance(position, tuple):
                self.spines[spine].position = position[0]
                self.spines[spine].position_offset = position[1]
            else:
                self.spines[spine].position = position
        return self

    def spine_set_color(self, spine: str, color: ColorHDR) -> 'AxisControl':
        """Set spine color."""
        if spine in self.spines:
            self.spines[spine].color = color
        return self

    def spine_set_linewidth(self, spine: str, linewidth: float) -> 'AxisControl':
        """Set spine line width."""
        if spine in self.spines:
            self.spines[spine].linewidth = linewidth
        return self


class GridControl:
    """Fine-grained control over grid appearance."""

    def __init__(self, chart):
        self.chart = chart
        self.major_grid = GridProperties()
        self.minor_grid = GridProperties(visible=False)

    def grid(self, visible: bool = True, which: str = "major",
             axis: str = "both", **kwargs) -> 'GridControl':
        """Control grid visibility and appearance."""
        grid_props = self.major_grid if which in ["major", "both"] else self.minor_grid

        grid_props.visible = visible

        for prop, value in kwargs.items():
            if hasattr(grid_props, prop):
                setattr(grid_props, prop, value)

        return self

    def set_major_grid(self, **kwargs) -> 'GridControl':
        """Set major grid properties."""
        return self.grid(which="major", **kwargs)

    def set_minor_grid(self, **kwargs) -> 'GridControl':
        """Set minor grid properties."""
        return self.grid(which="minor", **kwargs)


class TickLocator:
    """Base class for tick locators."""

    def __init__(self):
        pass

    def tick_values(self, vmin: float, vmax: float) -> np.ndarray:
        """Return tick positions for given data range."""
        return np.array([])


class LinearLocator(TickLocator):
    """Linear tick locator with specified number of ticks."""

    def __init__(self, numticks: int = 5):
        self.numticks = numticks

    def tick_values(self, vmin: float, vmax: float) -> np.ndarray:
        return np.linspace(vmin, vmax, self.numticks)


class MultipleLocator(TickLocator):
    """Tick locator with fixed spacing."""

    def __init__(self, base: float):
        self.base = base

    def tick_values(self, vmin: float, vmax: float) -> np.ndarray:
        start = math.ceil(vmin / self.base) * self.base
        end = math.floor(vmax / self.base) * self.base
        return np.arange(start, end + self.base/2, self.base)


class LogLocator(TickLocator):
    """Logarithmic tick locator."""

    def __init__(self, base: float = 10.0, subs: List[float] = None):
        self.base = base
        self.subs = subs or [1.0]

    def tick_values(self, vmin: float, vmax: float) -> np.ndarray:
        if vmin <= 0 or vmax <= 0:
            return np.array([])

        log_min = math.log(vmin, self.base)
        log_max = math.log(vmax, self.base)

        decades = range(int(math.floor(log_min)), int(math.ceil(log_max)) + 1)
        ticks = []

        for decade in decades:
            for sub in self.subs:
                tick = self.base ** decade * sub
                if vmin <= tick <= vmax:
                    ticks.append(tick)

        return np.array(ticks)


class TickFormatter:
    """Base class for tick formatters."""

    def __call__(self, x: float, pos: int) -> str:
        """Format tick value."""
        return str(x)


class ScalarFormatter(TickFormatter):
    """Standard scalar formatter."""

    def __init__(self, useOffset: bool = True, useMathText: bool = False):
        self.useOffset = useOffset
        self.useMathText = useMathText

    def __call__(self, x: float, pos: int) -> str:
        if abs(x) < 1e-10:
            return "0"
        elif abs(x) >= 1e6 or abs(x) <= 1e-4:
            return f"{x:.2e}"
        else:
            return f"{x:.3g}"


class LogFormatter(TickFormatter):
    """Logarithmic formatter."""

    def __init__(self, base: float = 10.0, labelOnlyBase: bool = True):
        self.base = base
        self.labelOnlyBase = labelOnlyBase

    def __call__(self, x: float, pos: int) -> str:
        if x <= 0:
            return ""

        log_x = math.log(x, self.base)
        if abs(log_x - round(log_x)) < 1e-10:  # Close to integer power
            power = int(round(log_x))
            if self.base == 10:
                return f"$10^{{{power}}}$" if power != 0 else "1"
            else:
                return f"${self.base}^{{{power}}}$" if power != 0 else "1"
        elif not self.labelOnlyBase:
            return f"{x:.2g}"
        else:
            return ""


class Axes:
    """Fine-grained control interface for chart axes."""

    def __init__(self, chart):
        self.chart = chart
        self.xaxis = AxisControl(chart, "x")
        self.yaxis = AxisControl(chart, "y")
        self.grid_control = GridControl(chart)

        # Axes-level properties
        self.facecolor = ColorHDR(1, 1, 1, 1)  # Background color
        self.edgecolor = ColorHDR(0, 0, 0, 1)  # Edge color
        self.linewidth = 1.0
        self.frame_on = True

    def set_xlabel(self, xlabel: str, **kwargs) -> 'Axes':
        """Set x-axis label."""
        self.xaxis.set_label(xlabel, **kwargs)
        return self

    def set_ylabel(self, ylabel: str, **kwargs) -> 'Axes':
        """Set y-axis label."""
        self.yaxis.set_label(ylabel, **kwargs)
        return self

    def set_xlim(self, left: float = None, right: float = None) -> 'Axes':
        """Set x-axis limits."""
        self.xaxis.set_lim(left, right)
        return self

    def set_ylim(self, bottom: float = None, top: float = None) -> 'Axes':
        """Set y-axis limits."""
        self.yaxis.set_lim(bottom, top)
        return self

    def set_xscale(self, scale: str, **kwargs) -> 'Axes':
        """Set x-axis scale."""
        self.xaxis.set_scale(scale, **kwargs)
        return self

    def set_yscale(self, scale: str, **kwargs) -> 'Axes':
        """Set y-axis scale."""
        self.yaxis.set_scale(scale, **kwargs)
        return self

    def grid(self, visible: bool = True, **kwargs) -> 'Axes':
        """Enable/disable and configure grid."""
        self.grid_control.grid(visible, **kwargs)
        return self

    def set_facecolor(self, color: Union[str, ColorHDR]) -> 'Axes':
        """Set axes background color."""
        if isinstance(color, str):
            self.facecolor = ColorHDR.from_hex(color)
        else:
            self.facecolor = color
        return self

    def set_aspect(self, aspect: Union[str, float]) -> 'Axes':
        """Set aspect ratio of the axes."""
        self.aspect = aspect
        return self

    def invert_xaxis(self) -> 'Axes':
        """Invert the x-axis."""
        self.xaxis.invert_axis()
        return self

    def invert_yaxis(self) -> 'Axes':
        """Invert the y-axis."""
        self.yaxis.invert_axis()
        return self

    def tick_params(self, axis: str = "both", **kwargs) -> 'Axes':
        """Control tick parameters."""
        if axis in ["both", "x"]:
            self.xaxis.set_ticks(**kwargs)
        if axis in ["both", "y"]:
            self.yaxis.set_ticks(**kwargs)
        return self