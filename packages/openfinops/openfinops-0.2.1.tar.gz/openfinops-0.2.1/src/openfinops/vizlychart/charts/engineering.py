"""Engineering chart types."""

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
from typing import Iterable, Sequence, Tuple

import numpy as np
from scipy import signal

from .base import BaseChart


@dataclass
class BodePlot(BaseChart):
    """Convenience wrapper for Bode plots."""

    def plot(
        self,
        numerator: Sequence[float],
        denominator: Sequence[float],
        frequencies: Sequence[float] | None = None,
    ) -> "VizlyFigure":
        """Create a Bode plot with magnitude and phase subplots."""
        # Create transfer function
        system = signal.TransferFunction(numerator, denominator)

        # Generate frequency range if not provided
        if frequencies is None:
            w = np.logspace(-2, 3, 1000)
        else:
            w = np.asarray(frequencies)

        # Calculate frequency response
        w_rad, h = signal.freqresp(system, w)

        # Create subplots if not already created
        if len(self.figure.figure.axes) == 1:
            # Replace the single axes with two subplots
            self.figure.figure.clear()
            ax1 = self.figure.figure.add_subplot(2, 1, 1)
            ax2 = self.figure.figure.add_subplot(2, 1, 2)
            self._axes = ax1  # Update base chart's axes reference
        else:
            ax1, ax2 = self.figure.figure.axes[:2]

        # Magnitude plot (top subplot)
        mag_db = 20 * np.log10(np.abs(h))
        ax1.semilogx(w_rad, mag_db, "b-", linewidth=2)
        ax1.set_ylabel("Magnitude (dB)")
        ax1.grid(True, which="both", alpha=0.3)
        ax1.set_title("Bode Plot")

        # Phase plot (bottom subplot)
        phase_deg = np.angle(h) * 180 / np.pi
        ax2.semilogx(w_rad, phase_deg, "r-", linewidth=2)
        ax2.set_xlabel("Frequency (rad/s)")
        ax2.set_ylabel("Phase (degrees)")
        ax2.grid(True, which="both", alpha=0.3)

        self.figure.figure.tight_layout()
        return self.figure


@dataclass
class StressStrainChart(BaseChart):
    """Convenience wrapper for stress-strain curves."""

    def plot(
        self,
        strain: Sequence[float] | Iterable[float],
        stress: Sequence[float] | Iterable[float],
        yield_point: Tuple[float, float] | None = None,
        ultimate_point: Tuple[float, float] | None = None,
    ) -> None:
        """Create a stress-strain curve."""
        strain_array = np.asarray(list(strain), dtype=float)
        stress_array = np.asarray(list(stress), dtype=float)

        # Main curve
        self.axes.plot(
            strain_array, stress_array, "b-", linewidth=2, label="Stress-Strain"
        )

        # Mark special points
        if yield_point:
            self.axes.plot(
                yield_point[0], yield_point[1], "ro", markersize=8, label="Yield Point"
            )

        if ultimate_point:
            self.axes.plot(
                ultimate_point[0],
                ultimate_point[1],
                "rs",
                markersize=8,
                label="Ultimate Strength",
            )

        self.axes.set_xlabel("Strain")
        self.axes.set_ylabel("Stress (MPa)")
        self.axes.grid(True, alpha=0.3)
        self.axes.legend()


@dataclass
class PhaseDiagram(BaseChart):
    """Phase diagram visualization for materials science."""

    def plot(
        self,
        temperature: Sequence[float],
        composition: Sequence[float],
        phases: Sequence[str] | None = None,
    ) -> None:
        """Create a phase diagram."""
        temp_array = np.asarray(temperature, dtype=float)
        comp_array = np.asarray(composition, dtype=float)

        # Plot phase boundaries
        self.axes.plot(comp_array, temp_array, "b-", linewidth=2, label="Phase Boundary")

        self.axes.set_xlabel("Composition (%)")
        self.axes.set_ylabel("Temperature (°C)")
        self.axes.set_title("Phase Diagram")
        self.axes.grid(True, alpha=0.3)
        self.axes.legend()


@dataclass
class ContourChart(BaseChart):
    """Contour plot for engineering data visualization."""

    def plot(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        Z: np.ndarray,
        levels: int = 10,
    ) -> None:
        """Create a contour plot."""
        contour = self.axes.contour(X, Y, Z, levels=levels)
        self.axes.clabel(contour, inline=True, fontsize=8)

        self.axes.set_xlabel("X")
        self.axes.set_ylabel("Y")
        self.axes.set_title("Contour Plot")
        self.axes.grid(True, alpha=0.3)
