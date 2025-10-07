"""Line chart helpers."""

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

from dataclasses import dataclass
from typing import Iterable, Sequence

from matplotlib.lines import Line2D

from .base import BaseChart


@dataclass
class LineChart(BaseChart):
    """Convenience wrapper for standard line plots."""

    def plot(
        self,
        x_values: Sequence[float] | Iterable[float],
        y_values: Sequence[float] | Iterable[float],
        *,
        label: str | None = None,
        color: str | None = None,
        linewidth: float = 2.0,
        marker: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        grid: bool = True,
        glow: bool = False,
        linestyle: str = "-",
        alpha: float = 1.0,
        markersize: float = 6.0,
        markerfacecolor: str | None = None,
        markeredgecolor: str | None = None,
        smooth: bool = False,
        smooth_factor: float = 0.1,
        yerr: Sequence[float] | Iterable[float] | None = None,
        xerr: Sequence[float] | Iterable[float] | None = None,
        errorbar_style: str = "line",
        errorbar_capsize: float = 3.0,
        errorbar_alpha: float = 0.7,
    ) -> Line2D:
        """Enhanced line plotting with additional styling and performance options."""
        x, y = self._validate_xy(x_values, y_values)

        # Apply data sampling if enabled
        x, y = self._sample_data(x, y)

        # Store plot data for export functionality
        self._plot_data = {"x": x, "y": y}

        # Apply smoothing if requested
        if smooth and len(x) > 3:
            try:
                from scipy.interpolate import UnivariateSpline

                spline = UnivariateSpline(x, y, s=smooth_factor * len(x))
                x_smooth = np.linspace(x.min(), x.max(), len(x) * 2)
                y_smooth = spline(x_smooth)
                x, y = x_smooth, y_smooth
            except ImportError:
                import warnings

                warnings.warn(
                    "Smoothing requires scipy. Install with: pip install scipy",
                    UserWarning,
                )

        # Apply rendering optimizations
        plot_kwargs = {
            "label": label or self.label,
            "color": color,
            "linewidth": linewidth,
            "linestyle": linestyle,
            "alpha": alpha,
            "marker": marker,
            "markersize": markersize,
        }

        if markerfacecolor:
            plot_kwargs["markerfacecolor"] = markerfacecolor
        if markeredgecolor:
            plot_kwargs["markeredgecolor"] = markeredgecolor

        # Apply fast rendering config if enabled
        if getattr(self, "_fast_rendering", False):
            render_config = getattr(self, "_render_config", {})
            plot_kwargs.update(render_config)

        # Create glow effect
        if glow:
            glow_color = color if color else "blue"
            for i in range(1, 8):
                glow_kwargs = plot_kwargs.copy()
                glow_kwargs.update(
                    {
                        "linewidth": linewidth + i * 1.5,
                        "alpha": (0.15 - i * 0.02),
                        "color": glow_color,
                        "marker": None,  # No markers for glow
                        "label": None,  # No label for glow
                    }
                )
                self.axes.plot(x, y, **glow_kwargs)

        # Handle error bars if provided
        if yerr is not None or xerr is not None:
            # Convert error data to numpy arrays if provided
            y_errors = None
            x_errors = None

            if yerr is not None:
                from .base import _to_numpy
                y_errors = _to_numpy(yerr)
                if len(y_errors) != len(y):
                    raise ValueError("yerr must have same length as y data")

            if xerr is not None:
                from .base import _to_numpy
                x_errors = _to_numpy(xerr)
                if len(x_errors) != len(x):
                    raise ValueError("xerr must have same length as x data")

            # Create errorbar plot
            errorbar_kwargs = {
                "yerr": y_errors,
                "xerr": x_errors,
                "fmt": 'o' if marker else '-',
                "capsize": errorbar_capsize,
                "alpha": errorbar_alpha,
                "color": color,
                "linewidth": linewidth * 0.8,
                "markersize": markersize * 0.8 if marker else 0,
                "label": label or self.label,
            }

            # Use errorbar instead of plot when errors are present
            line = self.axes.errorbar(x, y, **errorbar_kwargs)
        else:
            # Main line plot (no errors)
            (line,) = self.axes.plot(x, y, **plot_kwargs)

        # Configure grid
        if grid:
            grid_alpha = 0.3 if not getattr(self, "_fast_rendering", False) else 0.1
            self.axes.grid(True, alpha=grid_alpha, linestyle=":", linewidth=0.5)

        # Add legend if needed
        if label or self.label:
            self.axes.legend(frameon=True, fancybox=True, shadow=True, framealpha=0.9)

        self._maybe_set_labels(xlabel, ylabel)
        return line

    def plot_multiple(
        self,
        series: dict[
            str,
            tuple[Sequence[float] | Iterable[float], Sequence[float] | Iterable[float]],
        ],
        *,
        xlabel: str | None = None,
        ylabel: str | None = None,
    ) -> None:
        for label, (xs, ys) in series.items():
            self.plot(xs, ys, label=label, grid=False)
        self.axes.grid(True)
        self._maybe_set_labels(xlabel, ylabel)
