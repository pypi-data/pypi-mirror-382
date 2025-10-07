"""Computer-Aided Engineering (CAE) visualization tools for Vizly."""

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



from .mesh import MeshRenderer, FEAMesh, StructuralMesh
from .fields import ScalarField, VectorField, TensorField
from .analysis import StressAnalysis, ThermalAnalysis, ModalAnalysis
from .geometry import CADGeometry, GeometryLoader
from .animation import TimeSeriesAnimation, DeformationAnimation

__all__ = [
    "MeshRenderer",
    "FEAMesh",
    "StructuralMesh",
    "ScalarField",
    "VectorField",
    "TensorField",
    "StressAnalysis",
    "ThermalAnalysis",
    "ModalAnalysis",
    "CADGeometry",
    "GeometryLoader",
    "TimeSeriesAnimation",
    "DeformationAnimation",
]
