"""Bode plot utilities leveraging Vizly."""

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

from ..figure import VizlyFigure


@dataclass
class BodePlot:
    """Generate magnitude/phase Bode plots for transfer functions."""

    figure: VizlyFigure | None = None

    def plot(
        self,
        numerator: Sequence[float] | Iterable[float],
        denominator: Sequence[float] | Iterable[float],
        *,
        omega: np.ndarray | None = None,
        units: str = "rad/s",
    ) -> VizlyFigure:
        fig = self.figure or VizlyFigure(height=8.0)
        fig.figure.clf()
        axes_mag, axes_phase = fig.figure.subplots(2, 1, sharex=True)

        w = omega if omega is not None else np.logspace(-2, 2, 400)
        num = np.poly1d(list(numerator))
        den = np.poly1d(list(denominator))
        jw = 1j * w
        response = num(jw) / den(jw)

        magnitude_db = 20 * np.log10(np.abs(response))
        phase_deg = np.unwrap(np.angle(response)) * 180 / np.pi

        axes_mag.semilogx(w, magnitude_db, color="#2563eb")
        axes_mag.set_ylabel("Magnitude (dB)")
        axes_mag.grid(True, which="both")

        axes_phase.semilogx(w, phase_deg, color="#7c3aed")
        axes_phase.set_ylabel("Phase (deg)")
        axes_phase.set_xlabel(f"Frequency ({units})")
        axes_phase.grid(True, which="both")

        fig.axes = axes_mag
        return fig
