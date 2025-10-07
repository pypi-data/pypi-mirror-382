"""Scatter plot helpers."""

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

import numpy as np

from .base import BaseChart


@dataclass
class ScatterChart(BaseChart):
    """Create high-density scatter plots with sensible defaults."""

    def plot(
        self,
        x_values: Sequence[float] | Iterable[float],
        y_values: Sequence[float] | Iterable[float],
        *,
        label: str | None = None,
        color: str | None = None,
        c: Sequence[float] | Iterable[float] | None = None,
        size: int = 40,
        s: int | None = None,
        alpha: float = 0.9,
        style: str = "o",
        cmap: str = "viridis",
        xlabel: str | None = None,
        ylabel: str | None = None,
        grid: bool = True,
        edgecolors: str | None = None,
        linewidths: float = 0.5,
        vmin: float | None = None,
        vmax: float | None = None,
        density_alpha: bool = False,
    ) -> None:
        """Enhanced scatter plotting with additional styling and performance features."""
        x, y = self._validate_xy(x_values, y_values)

        # Apply data sampling if enabled
        x, y = self._sample_data(x, y)

        # Store plot data for export functionality
        color_data = c
        if c is not None:
            c = (
                self._sanitize_data(c)
                if hasattr(self, "_sanitize_data")
                else np.asarray(c)
            )
            # Apply sampling to color data as well
            if hasattr(self, "_sampling_enabled") and getattr(
                self, "_sampling_enabled", False
            ):
                if len(c) == len(self._plot_data["x"]):  # Original length
                    # Need to resample color data to match sampled x, y
                    original_x = self._plot_data["x"]
                    sampled_indices = np.searchsorted(original_x, x)
                    c = (
                        c[sampled_indices]
                        if len(c) > max(sampled_indices)
                        else c[: len(x)]
                    )

        self._plot_data = {"x": x, "y": y, "c": color_data}

        # Handle size parameter (s takes precedence over size)
        point_size = s if s is not None else size

        # Density-based alpha adjustment
        plot_alpha = alpha
        if density_alpha and len(x) > 100:
            # Reduce alpha for high-density plots
            density_factor = min(1.0, 1000.0 / len(x))
            plot_alpha = alpha * density_factor

        # Prepare scatter arguments
        scatter_kwargs = {
            "label": label or self.label,
            "s": point_size,
            "alpha": plot_alpha,
            "marker": style,
            "cmap": cmap,
            "edgecolors": edgecolors,
            "linewidths": linewidths,
        }

        # Handle color specification
        if color is not None:
            scatter_kwargs["color"] = color
        elif c is not None:
            scatter_kwargs["c"] = c
            if vmin is not None:
                scatter_kwargs["vmin"] = vmin
            if vmax is not None:
                scatter_kwargs["vmax"] = vmax

        # Apply fast rendering config if enabled
        if getattr(self, "_fast_rendering", False):
            render_config = getattr(self, "_render_config", {})
            scatter_kwargs.update(render_config)

        scatter = self.axes.scatter(x, y, **scatter_kwargs)

        # Configure grid
        if grid:
            grid_alpha = 0.3 if not getattr(self, "_fast_rendering", False) else 0.1
            self.axes.grid(True, linestyle=":", alpha=grid_alpha, linewidth=0.5)

        # Add legend if needed
        if label or self.label:
            self.axes.legend(frameon=True, fancybox=True, shadow=True, framealpha=0.9)

        self._maybe_set_labels(xlabel, ylabel)

        # Store scatter object for colorbar
        self._scatter = scatter

    def add_colorbar(self, label: str | None = None) -> None:
        """Add a colorbar to the scatter plot."""
        if hasattr(self, "_scatter") and self.figure:
            # Access the matplotlib figure from VizlyFigure
            if hasattr(self.figure, "fig"):
                cbar = self.figure.fig.colorbar(self._scatter, ax=self.axes)
            elif hasattr(self.figure, "colorbar"):
                cbar = self.figure.colorbar(self._scatter, ax=self.axes)
            else:
                # Fallback to matplotlib
                import matplotlib.pyplot as plt

                cbar = plt.colorbar(self._scatter, ax=self.axes)

            if label:
                cbar.set_label(label)
