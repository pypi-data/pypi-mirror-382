"""Histogram chart helpers."""

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
class HistogramChart(BaseChart):
    """Convenience wrapper for histogram plots."""

    def __post_init__(self):
        """Initialize data series storage."""
        super().__post_init__()
        self.data_series = []

    def hist(
        self,
        data: Sequence[float] | Iterable[float],
        bins: int = 30,
        alpha: float = 0.7,
        color: str = "blue",
        density: bool = False,
        label: str | None = None,
    ) -> None:
        """Create a histogram."""
        data_array = np.asarray(list(data), dtype=float)

        self.axes.hist(
            data_array,
            bins=bins,
            alpha=alpha,
            color=color,
            density=density,
            label=label,
        )

        # Store data series for test compatibility
        self.data_series.append({
            'data': data_array,
            'bins': bins,
            'alpha': alpha,
            'color': color,
            'density': density,
            'label': label
        })

        if label:
            self.axes.legend()

    def plot(
        self, x, y, color: str = "red", linewidth: float = 2, label: str | None = None
    ) -> None:
        """Add a line plot (for overlaying curves on histograms)."""
        self.axes.plot(x, y, color=color, linewidth=linewidth, label=label)
        if label:
            self.axes.legend()
