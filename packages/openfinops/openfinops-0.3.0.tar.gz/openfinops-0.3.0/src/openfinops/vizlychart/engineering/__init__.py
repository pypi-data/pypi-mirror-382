"""
Vizly Engineering Module
=======================

Advanced engineering analysis and visualization capabilities including:
- Finite Element Analysis (FEA)
- Computational Fluid Dynamics (CFD)
- Modal Analysis and Vibration
- Thermal Analysis
- CAD Model Import and Rendering

This module provides GPU-accelerated solvers and specialized chart types
for engineering applications.
"""

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



from .bode import BodePlot
from .stress import StressStrainChart
from .fem import FEMSolver, FEMChart
from .cfd import CFDSolver, CFDChart
from .modal import ModalSolver, ModalChart
from .thermal import ThermalSolver, ThermalChart
from .cad_import import IGESImporter, STEPImporter, STLImporter, CADViewer

__all__ = [
    "BodePlot",
    "StressStrainChart",
    'FEMSolver', 'FEMChart',
    'CFDSolver', 'CFDChart',
    'ModalSolver', 'ModalChart',
    'ThermalSolver', 'ThermalChart',
    'IGESImporter', 'STEPImporter', 'STLImporter', 'CADViewer'
]
