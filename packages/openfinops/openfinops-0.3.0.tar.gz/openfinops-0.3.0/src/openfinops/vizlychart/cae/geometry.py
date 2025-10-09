"""Geometry utilities for CAE visualization."""

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
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class GeometryData:
    """Container for geometry data."""

    vertices: np.ndarray
    faces: np.ndarray
    name: str
    properties: dict


class CADGeometry:
    """CAD geometry representation."""

    def __init__(self, name: str = "Geometry") -> None:
        self.name = name
        self.geometries: List[GeometryData] = []

    def add_geometry(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        name: Optional[str] = None,
        **properties,
    ) -> None:
        """Add geometry data."""
        geom_name = name or f"Geometry_{len(self.geometries)}"
        geometry = GeometryData(
            vertices=vertices, faces=faces, name=geom_name, properties=properties
        )
        self.geometries.append(geometry)


class GeometryLoader:
    """Geometry file loader."""

    @staticmethod
    def load_stl(file_path: str) -> CADGeometry:
        """Load STL file."""
        logger.info(f"Loading STL file: {file_path}")
        # Placeholder implementation
        geometry = CADGeometry("STL_Geometry")
        return geometry

    @staticmethod
    def load_obj(file_path: str) -> CADGeometry:
        """Load OBJ file."""
        logger.info(f"Loading OBJ file: {file_path}")
        # Placeholder implementation
        geometry = CADGeometry("OBJ_Geometry")
        return geometry
