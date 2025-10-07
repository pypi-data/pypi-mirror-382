"""Analysis utilities for CAE visualization."""

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

import logging
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

from .mesh import FEAMesh

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Container for analysis results."""

    name: str
    description: str
    data: Dict[str, np.ndarray]
    units: Optional[str] = None


class StressAnalysis:
    """Stress analysis visualization."""

    def __init__(self, mesh: FEAMesh) -> None:
        self.mesh = mesh
        self.results: Dict[str, AnalysisResult] = {}

    def add_stress_result(
        self, name: str, stress_data: np.ndarray, units: str = "Pa"
    ) -> None:
        """Add stress analysis results."""
        result = AnalysisResult(
            name=name,
            description=f"Stress analysis: {name}",
            data={"stress": stress_data},
            units=units,
        )
        self.results[name] = result

    def visualize_von_mises(self, deformation_scale: float = 1.0) -> None:
        """Visualize von Mises stress."""
        logger.info(
            f"Visualizing von Mises stress with deformation scale {deformation_scale}"
        )
        # Placeholder implementation
        pass


class ThermalAnalysis:
    """Thermal analysis visualization."""

    def __init__(self, mesh: FEAMesh) -> None:
        self.mesh = mesh
        self.results: Dict[str, AnalysisResult] = {}

    def add_temperature_result(
        self, name: str, temperature_data: np.ndarray, units: str = "K"
    ) -> None:
        """Add temperature analysis results."""
        result = AnalysisResult(
            name=name,
            description=f"Thermal analysis: {name}",
            data={"temperature": temperature_data},
            units=units,
        )
        self.results[name] = result


class ModalAnalysis:
    """Modal analysis visualization."""

    def __init__(self, mesh: FEAMesh) -> None:
        self.mesh = mesh
        self.results: Dict[str, AnalysisResult] = {}

    def add_mode_result(
        self,
        mode_number: int,
        frequency: float,
        displacement_data: np.ndarray,
        units: str = "Hz",
    ) -> None:
        """Add modal analysis results."""
        result = AnalysisResult(
            name=f"Mode_{mode_number}",
            description=f"Mode {mode_number} at {frequency} {units}",
            data={
                "displacement": displacement_data,
                "frequency": np.array([frequency]),
            },
            units=units,
        )
        self.results[f"mode_{mode_number}"] = result
