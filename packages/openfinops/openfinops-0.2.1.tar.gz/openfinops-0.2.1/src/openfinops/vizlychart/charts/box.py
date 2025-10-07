"""Box plot chart helpers."""

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
from typing import List, Sequence

from .base import BaseChart


@dataclass
class BoxChart(BaseChart):
    """Convenience wrapper for box plots."""

    def boxplot(
        self,
        data: List[Sequence[float]],
        labels: List[str] | None = None,
        patch_artist: bool = True,
    ) -> None:
        """Create a box plot."""

        box_plot = self.axes.boxplot(data, labels=labels, patch_artist=patch_artist)

        # Color the boxes
        if patch_artist:
            colors = [
                "lightblue",
                "lightgreen",
                "lightcoral",
                "lightyellow",
                "lightgray",
            ]
            for patch, color in zip(box_plot["boxes"], colors * len(box_plot["boxes"])):
                patch.set_facecolor(color)
