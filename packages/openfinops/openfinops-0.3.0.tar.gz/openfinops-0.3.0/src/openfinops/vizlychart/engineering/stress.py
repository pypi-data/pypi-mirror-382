"""Mechanical engineering plotting helpers."""

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

from ..charts.line import LineChart


@dataclass
class StressStrainChart(LineChart):
    """Render stress-strain curves with typical annotation defaults."""

    def plot(
        self,
        strain: Sequence[float] | Iterable[float],
        stress: Sequence[float] | Iterable[float],
        *,
        yield_point: tuple[float, float] | None = None,
        ultimate_point: tuple[float, float] | None = None,
        xlabel: str = "Strain",
        ylabel: str = "Stress (MPa)",
    ) -> None:
        super().plot(strain, stress, xlabel=xlabel, ylabel=ylabel, grid=True)
        if yield_point:
            self.axes.scatter(*yield_point, color="#dc2626", label="Yield")
        if ultimate_point:
            self.axes.scatter(*ultimate_point, color="#16a34a", label="Ultimate")
        if yield_point or ultimate_point:
            self.axes.legend()
