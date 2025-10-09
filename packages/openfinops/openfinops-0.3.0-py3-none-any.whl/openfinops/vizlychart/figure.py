"""Core figure management utilities for Vizly."""

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

import contextlib
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import matplotlib
import numpy as np
from matplotlib import pyplot as plt

from .exceptions import VizlyError
from .theme import VizlyTheme, apply_theme

# Default to a non-interactive backend so the library is safe in headless environments.
if matplotlib.get_backend().lower() not in {
    "agg",
    "module://matplotlib_inline.backend_inline",
}:
    with contextlib.suppress(Exception):
        matplotlib.use("Agg", force=True)


@dataclass
class VizlyFigure:
    """Wrapper around Matplotlib figures with built-in theming and helpers."""

    width: float = 10.0
    height: float = 6.0
    style: str = "light"
    tight_layout: bool = True

    def __post_init__(self) -> None:
        self.theme: VizlyTheme = apply_theme(self.style)
        self.figure, self.axes = plt.subplots(figsize=(self.width, self.height))
        if self.tight_layout:
            self.figure.tight_layout()

    def new_axes(self, projection: str | None = None) -> matplotlib.axes.Axes:
        """Create a new axes on the figure, optionally with a projection."""
        ax = self.figure.add_subplot(111, projection=projection)
        self.axes = ax
        return ax

    def add_subplot(
        self, position: int, projection: str | None = None
    ) -> matplotlib.axes.Axes:
        """Add a subplot in the provided position index (e.g., 221)."""
        ax = self.figure.add_subplot(position, projection=projection)
        self.axes = ax
        return ax

    def plot_grid(self, layout: Tuple[int, int]) -> list[matplotlib.axes.Axes]:
        """Return axes laid out as an evenly spaced grid."""
        rows, cols = layout
        axes = self.figure.subplots(rows, cols)
        flat_axes = np.atleast_1d(axes).ravel().tolist()
        self.axes = flat_axes  # type: ignore[assignment]
        return flat_axes  # type: ignore[return-value]

    def save(self, path: str | Path, dpi: int = 300) -> Path:
        """Persist the figure to disk."""
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        self.figure.savefig(output, dpi=dpi, facecolor=self.theme.background)
        return output

    def show(self) -> None:
        """Display the current figure."""
        plt.show()

    def close(self) -> None:
        """Close the Matplotlib figure to release resources."""
        plt.close(self.figure)

    def export_data(self) -> dict[str, list[float]]:
        """Extract line data from the active axes for downstream analysis."""
        axes = self.axes[0] if isinstance(self.axes, list) else self.axes
        if not hasattr(axes, "lines"):
            raise VizlyError("Active axes does not expose line data.")
        data: dict[str, list[float]] = {}
        for idx, line in enumerate(axes.lines):
            label = line.get_label() or f"series_{idx}"
            data[label] = list(line.get_ydata())
        return data
