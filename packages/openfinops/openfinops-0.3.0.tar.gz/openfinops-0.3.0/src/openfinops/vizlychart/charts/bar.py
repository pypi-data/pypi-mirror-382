"""Bar chart helpers."""

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
class BarChart(BaseChart):
    """Produce grouped or stacked bar charts."""

    def plot(
        self,
        categories: Sequence[str],
        values: Sequence[float] | Iterable[float],
        *,
        label: str | None = None,
        color: str | None = None,
        width: float = 0.6,
        xlabel: str | None = None,
        ylabel: str | None = None,
    ) -> None:
        x = np.arange(len(categories))
        y = self._validate_xy(range(len(categories)), values)[1]
        self.axes.bar(x, y, color=color, width=width, label=label or self.label)
        self.axes.set_xticks(x)
        self.axes.set_xticklabels(categories, rotation=0)
        if label or self.label:
            self.axes.legend()
        self._maybe_set_labels(xlabel, ylabel)

    def plot_grouped(
        self,
        categories: Sequence[str],
        value_map: dict[str, Sequence[float] | Iterable[float]],
        *,
        width: float = 0.2,
        xlabel: str | None = None,
        ylabel: str | None = None,
    ) -> None:
        x = np.arange(len(categories))
        offsets = np.linspace(
            -width * (len(value_map) - 1) / 2,
            width * (len(value_map) - 1) / 2,
            len(value_map),
        )
        for offset, (label, values) in zip(offsets, value_map.items()):
            y = self._validate_xy(range(len(categories)), values)[1]
            self.axes.bar(x + offset, y, width=width, label=label)
        self.axes.set_xticks(x)
        self.axes.set_xticklabels(categories)
        self.axes.legend()
        self._maybe_set_labels(xlabel, ylabel)

    def bar(
        self,
        categories: Sequence[str],
        values: Sequence[float] | Iterable[float],
        *,
        color: str = "steelblue",
        alpha: float = 1.0,
        width: float = 0.6,
        label: str | None = None,
    ) -> None:
        """Create a simple bar chart (alias for plot method)."""
        self.plot(categories, values, label=label, color=color, width=width)

    def grouped_bar(
        self,
        categories: Sequence[str],
        value_map: dict[str, Sequence[float] | Iterable[float]],
        *,
        width: float = 0.2,
        xlabel: str | None = None,
        ylabel: str | None = None,
    ) -> None:
        """Create a grouped bar chart (alias for plot_grouped method)."""
        self.plot_grouped(
            categories, value_map, width=width, xlabel=xlabel, ylabel=ylabel
        )
