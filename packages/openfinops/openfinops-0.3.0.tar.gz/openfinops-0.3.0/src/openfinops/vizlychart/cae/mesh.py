"""Advanced mesh visualization for finite element analysis."""

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
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import warnings

import numpy as np

from ..core.renderer import RenderEngine
from ..figure import VizlyFigure

try:
    import vtk

    HAS_VTK = True
except ImportError:
    HAS_VTK = False
    warnings.warn("VTK not available. Advanced mesh features will be limited.")

try:
    import trimesh

    HAS_TRIMESH = True
except ImportError:
    HAS_TRIMESH = False


logger = logging.getLogger(__name__)


class ElementType(Enum):
    """Finite element types."""

    TRI3 = "tri3"  # 3-node triangle
    TRI6 = "tri6"  # 6-node triangle
    QUAD4 = "quad4"  # 4-node quadrilateral
    QUAD8 = "quad8"  # 8-node quadrilateral
    TET4 = "tet4"  # 4-node tetrahedron
    TET10 = "tet10"  # 10-node tetrahedron
    HEX8 = "hex8"  # 8-node hexahedron
    HEX20 = "hex20"  # 20-node hexahedron
    BEAM2 = "beam2"  # 2-node beam
    BEAM3 = "beam3"  # 3-node beam


class MeshQuality(Enum):
    """Mesh quality metrics."""

    ASPECT_RATIO = "aspect_ratio"
    SKEWNESS = "skewness"
    JACOBIAN = "jacobian"
    WARPAGE = "warpage"
    ORTHOGONALITY = "orthogonality"


@dataclass
class Element:
    """Finite element definition."""

    id: int
    type: ElementType
    node_ids: List[int]
    material_id: Optional[int] = None
    properties: Dict[str, float] = field(default_factory=dict)


@dataclass
class Node:
    """Finite element node definition."""

    id: int
    coordinates: Tuple[float, float, float]
    dof_ids: Optional[List[int]] = None
    constraints: Dict[str, bool] = field(default_factory=dict)


class FEAMesh:
    """Finite Element Analysis mesh representation."""

    def __init__(self) -> None:
        self.nodes: Dict[int, Node] = {}
        self.elements: Dict[int, Element] = {}
        self.node_sets: Dict[str, List[int]] = {}
        self.element_sets: Dict[str, List[int]] = {}
        self.materials: Dict[int, Dict[str, float]] = {}
        self._connectivity_cache: Optional[np.ndarray] = None
        self._vertices_cache: Optional[np.ndarray] = None

    def add_node(self, node: Node) -> None:
        """Add a node to the mesh."""
        self.nodes[node.id] = node
        self._invalidate_cache()

    def add_element(self, element: Element) -> None:
        """Add an element to the mesh."""
        self.elements[element.id] = element
        self._invalidate_cache()

    def add_nodes_bulk(self, node_ids: List[int], coordinates: np.ndarray) -> None:
        """Add multiple nodes efficiently."""
        if len(node_ids) != len(coordinates):
            raise ValueError("Number of node IDs must match coordinates array")

        for i, node_id in enumerate(node_ids):
            coord = tuple(coordinates[i].tolist())
            self.nodes[node_id] = Node(node_id, coord)

        self._invalidate_cache()

    def add_elements_bulk(
        self,
        element_ids: List[int],
        element_type: ElementType,
        connectivity: np.ndarray,
    ) -> None:
        """Add multiple elements efficiently."""
        if len(element_ids) != len(connectivity):
            raise ValueError("Number of element IDs must match connectivity array")

        for i, elem_id in enumerate(element_ids):
            node_ids = connectivity[i].tolist()
            self.elements[elem_id] = Element(elem_id, element_type, node_ids)

        self._invalidate_cache()

    def get_vertices(self) -> np.ndarray:
        """Get vertex coordinates as numpy array."""
        if self._vertices_cache is None:
            vertices = []
            sorted_nodes = sorted(self.nodes.items())
            for node_id, node in sorted_nodes:
                vertices.append(list(node.coordinates))
            self._vertices_cache = np.array(vertices, dtype=float)
        return self._vertices_cache

    def get_connectivity(self) -> np.ndarray:
        """Get element connectivity as numpy array."""
        if self._connectivity_cache is None:
            connectivity = []
            sorted_elements = sorted(self.elements.items())
            for elem_id, element in sorted_elements:
                # Map node IDs to indices
                node_indices = []
                sorted_nodes = sorted(self.nodes.keys())
                for node_id in element.node_ids:
                    try:
                        idx = sorted_nodes.index(node_id)
                        node_indices.append(idx)
                    except ValueError:
                        raise ValueError(f"Node {node_id} not found in mesh")
                connectivity.append(node_indices)
            self._connectivity_cache = np.array(connectivity, dtype=int)
        return self._connectivity_cache

    def get_surface_mesh(self) -> Tuple[np.ndarray, np.ndarray]:
        """Extract surface mesh for visualization."""
        vertices = self.get_vertices()

        # Extract surface elements based on element types
        surface_faces = []

        for element in self.elements.values():
            if element.type in [ElementType.TRI3, ElementType.TRI6]:
                # Triangular elements - use first 3 nodes
                face = element.node_ids[:3]
                sorted_nodes = sorted(self.nodes.keys())
                face_indices = [sorted_nodes.index(nid) for nid in face]
                surface_faces.append(face_indices)

            elif element.type in [ElementType.QUAD4, ElementType.QUAD8]:
                # Quadrilateral elements - split into triangles
                face = element.node_ids[:4]
                sorted_nodes = sorted(self.nodes.keys())
                face_indices = [sorted_nodes.index(nid) for nid in face]
                # Split quad into two triangles
                surface_faces.append(
                    [face_indices[0], face_indices[1], face_indices[2]]
                )
                surface_faces.append(
                    [face_indices[0], face_indices[2], face_indices[3]]
                )

            elif element.type in [ElementType.TET4, ElementType.TET10]:
                # Tetrahedral elements - extract all faces
                nodes = element.node_ids[:4]
                sorted_nodes = sorted(self.nodes.keys())
                node_indices = [sorted_nodes.index(nid) for nid in nodes]

                # Tet faces
                faces = [
                    [node_indices[0], node_indices[1], node_indices[2]],
                    [node_indices[0], node_indices[1], node_indices[3]],
                    [node_indices[0], node_indices[2], node_indices[3]],
                    [node_indices[1], node_indices[2], node_indices[3]],
                ]
                surface_faces.extend(faces)

        if not surface_faces:
            # No surface elements found, return empty arrays
            return vertices, np.array([], dtype=int).reshape(0, 3)

        faces = np.array(surface_faces, dtype=int)
        return vertices, faces

    def calculate_quality_metrics(self, metric: MeshQuality) -> Dict[int, float]:
        """Calculate mesh quality metrics."""
        metrics = {}

        for elem_id, element in self.elements.items():
            if metric == MeshQuality.ASPECT_RATIO:
                metrics[elem_id] = self._calculate_aspect_ratio(element)
            elif metric == MeshQuality.SKEWNESS:
                metrics[elem_id] = self._calculate_skewness(element)
            elif metric == MeshQuality.JACOBIAN:
                metrics[elem_id] = self._calculate_jacobian(element)
            # Add more metrics as needed

        return metrics

    def _calculate_aspect_ratio(self, element: Element) -> float:
        """Calculate element aspect ratio."""
        # Simple implementation for triangular elements
        if element.type in [ElementType.TRI3, ElementType.TRI6]:
            coords = []
            for node_id in element.node_ids[:3]:
                coords.append(self.nodes[node_id].coordinates)

            # Calculate edge lengths
            p1, p2, p3 = coords
            edge1 = np.linalg.norm(np.array(p2) - np.array(p1))
            edge2 = np.linalg.norm(np.array(p3) - np.array(p2))
            edge3 = np.linalg.norm(np.array(p1) - np.array(p3))

            max_edge = max(edge1, edge2, edge3)
            min_edge = min(edge1, edge2, edge3)

            return max_edge / min_edge if min_edge > 0 else float("inf")

        return 1.0  # Default for unsupported element types

    def _calculate_skewness(self, element: Element) -> float:
        """Calculate element skewness."""
        # Placeholder implementation
        return 0.0

    def _calculate_jacobian(self, element: Element) -> float:
        """Calculate element Jacobian determinant."""
        # Placeholder implementation
        return 1.0

    def _invalidate_cache(self) -> None:
        """Invalidate cached arrays."""
        self._connectivity_cache = None
        self._vertices_cache = None

    def create_node_set(self, name: str, node_ids: List[int]) -> None:
        """Create a named set of nodes."""
        self.node_sets[name] = node_ids

    def create_element_set(self, name: str, element_ids: List[int]) -> None:
        """Create a named set of elements."""
        self.element_sets[name] = element_ids

    def get_bounding_box(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get mesh bounding box."""
        vertices = self.get_vertices()
        if len(vertices) == 0:
            return np.zeros(3), np.zeros(3)

        min_coords = np.min(vertices, axis=0)
        max_coords = np.max(vertices, axis=0)
        return min_coords, max_coords


class StructuralMesh(FEAMesh):
    """Specialized mesh for structural analysis."""

    def __init__(self) -> None:
        super().__init__()
        self.boundary_conditions: Dict[str, Dict[str, float]] = {}
        self.loads: Dict[str, Dict[str, float]] = {}

    def add_boundary_condition(self, node_set: str, dof: str, value: float) -> None:
        """Add boundary condition to a node set."""
        if node_set not in self.boundary_conditions:
            self.boundary_conditions[node_set] = {}
        self.boundary_conditions[node_set][dof] = value

    def add_load(self, node_set: str, direction: str, magnitude: float) -> None:
        """Add load to a node set."""
        if node_set not in self.loads:
            self.loads[node_set] = {}
        self.loads[node_set][direction] = magnitude


class MeshRenderer:
    """High-performance mesh rendering."""

    def __init__(
        self,
        figure: Optional[VizlyFigure] = None,
        render_engine: Optional[RenderEngine] = None,
    ) -> None:
        self.figure = figure or VizlyFigure()
        self.render_engine = render_engine
        self._mesh_cache: Dict[str, Any] = {}

    def render_mesh(
        self,
        mesh: FEAMesh,
        mode: str = "surface",
        scalar_field: Optional[np.ndarray] = None,
        vector_field: Optional[np.ndarray] = None,
        colormap: str = "viridis",
        show_edges: bool = False,
        edge_color: str = "black",
        alpha: float = 1.0,
    ) -> None:
        """Render finite element mesh."""

        if mode == "surface":
            self._render_surface_mesh(
                mesh, scalar_field, colormap, show_edges, edge_color, alpha
            )
        elif mode == "wireframe":
            self._render_wireframe_mesh(mesh, edge_color)
        elif mode == "nodes":
            self._render_node_mesh(mesh)
        elif mode == "volume" and HAS_VTK:
            self._render_volume_mesh(mesh, scalar_field, colormap, alpha)

        if vector_field is not None:
            self._render_vector_field(mesh, vector_field)

    def _render_surface_mesh(
        self,
        mesh: FEAMesh,
        scalar_field: Optional[np.ndarray],
        colormap: str,
        show_edges: bool,
        edge_color: str,
        alpha: float,
    ) -> None:
        """Render surface mesh."""
        vertices, faces = mesh.get_surface_mesh()

        if len(faces) == 0:
            logger.warning("No surface elements found in mesh")
            return

        # Ensure 3D axes
        if not hasattr(self.figure.axes, "plot_trisurf"):
            axes = self.figure.figure.add_subplot(111, projection="3d")
            self.figure.bind_axes(axes)

        if scalar_field is not None and len(scalar_field) == len(vertices):
            # Color by scalar field
            x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]

            # Use plot_trisurf for colored surface
            self.figure.axes.plot_trisurf(
                x,
                y,
                z,
                triangles=faces,
                facecolors=scalar_field,
                cmap=colormap,
                alpha=alpha,
            )
        else:
            # Simple surface without coloring
            x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
            self.figure.axes.plot_trisurf(
                x, y, z, triangles=faces, alpha=alpha, color="lightblue"
            )

        if show_edges:
            self._render_mesh_edges(vertices, faces, edge_color)

    def _render_wireframe_mesh(self, mesh: FEAMesh, edge_color: str) -> None:
        """Render wireframe mesh."""
        vertices, faces = mesh.get_surface_mesh()
        self._render_mesh_edges(vertices, faces, edge_color)

    def _render_mesh_edges(
        self, vertices: np.ndarray, faces: np.ndarray, edge_color: str
    ) -> None:
        """Render mesh edges."""
        if not hasattr(self.figure.axes, "plot3D"):
            axes = self.figure.figure.add_subplot(111, projection="3d")
            self.figure.bind_axes(axes)

        # Draw all edges
        for face in faces:
            for i in range(len(face)):
                p1 = vertices[face[i]]
                p2 = vertices[face[(i + 1) % len(face)]]
                self.figure.axes.plot3D(
                    [p1[0], p2[0]],
                    [p1[1], p2[1]],
                    [p1[2], p2[2]],
                    color=edge_color,
                    linewidth=0.5,
                )

    def _render_node_mesh(self, mesh: FEAMesh) -> None:
        """Render mesh nodes."""
        vertices = mesh.get_vertices()

        if not hasattr(self.figure.axes, "scatter3D"):
            axes = self.figure.figure.add_subplot(111, projection="3d")
            self.figure.bind_axes(axes)

        self.figure.axes.scatter3D(
            vertices[:, 0], vertices[:, 1], vertices[:, 2], s=20, c="red", marker="o"
        )

    def _render_volume_mesh(
        self,
        mesh: FEAMesh,
        scalar_field: Optional[np.ndarray],
        colormap: str,
        alpha: float,
    ) -> None:
        """Render volume mesh using VTK."""
        if not HAS_VTK:
            logger.warning("VTK not available for volume rendering")
            return

        # This would require more complex VTK integration
        # For now, fall back to surface rendering
        self._render_surface_mesh(mesh, scalar_field, colormap, False, "black", alpha)

    def _render_vector_field(self, mesh: FEAMesh, vector_field: np.ndarray) -> None:
        """Render vector field on mesh."""
        vertices = mesh.get_vertices()

        if len(vector_field) != len(vertices):
            logger.error("Vector field size must match number of vertices")
            return

        if not hasattr(self.figure.axes, "quiver3D"):
            axes = self.figure.figure.add_subplot(111, projection="3d")
            self.figure.bind_axes(axes)

        x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
        u, v, w = vector_field[:, 0], vector_field[:, 1], vector_field[:, 2]

        self.figure.axes.quiver3D(x, y, z, u, v, w, length=0.1, normalize=True)

    def render_quality_metrics(
        self, mesh: FEAMesh, metric: MeshQuality, colormap: str = "RdYlBu_r"
    ) -> None:
        """Render mesh colored by quality metrics."""
        quality_values = mesh.calculate_quality_metrics(metric)

        # Convert to array aligned with elements
        vertices = mesh.get_vertices()
        scalar_field = np.zeros(len(vertices))

        # For simplicity, assign element quality to all nodes of that element
        for elem_id, quality in quality_values.items():
            element = mesh.elements[elem_id]
            sorted_nodes = sorted(mesh.nodes.keys())
            for node_id in element.node_ids:
                try:
                    vertex_idx = sorted_nodes.index(node_id)
                    scalar_field[vertex_idx] = quality
                except ValueError:
                    continue

        self._render_surface_mesh(mesh, scalar_field, colormap, True, "gray", 0.8)

    def animate_deformation(
        self,
        mesh: FEAMesh,
        displacement_history: List[np.ndarray],
        scale_factor: float = 1.0,
        fps: int = 30,
    ) -> None:
        """Animate mesh deformation over time."""
        # This would require animation framework
        # For now, just render the final deformed state
        if displacement_history:
            final_displacement = displacement_history[-1]
            deformed_mesh = self._apply_displacement(
                mesh, final_displacement, scale_factor
            )
            self.render_mesh(deformed_mesh)

    def _apply_displacement(
        self, mesh: FEAMesh, displacement: np.ndarray, scale_factor: float
    ) -> FEAMesh:
        """Apply displacement to mesh nodes."""
        deformed_mesh = FEAMesh()

        # Copy elements
        deformed_mesh.elements = mesh.elements.copy()
        deformed_mesh.materials = mesh.materials.copy()
        deformed_mesh.node_sets = mesh.node_sets.copy()
        deformed_mesh.element_sets = mesh.element_sets.copy()

        # Apply displacement to nodes
        sorted_nodes = sorted(mesh.nodes.items())
        for i, (node_id, node) in enumerate(sorted_nodes):
            if i < len(displacement):
                disp = displacement[i] * scale_factor
                new_coords = (
                    node.coordinates[0] + disp[0],
                    node.coordinates[1] + disp[1],
                    (
                        node.coordinates[2] + disp[2]
                        if len(disp) > 2
                        else node.coordinates[2]
                    ),
                )
                deformed_mesh.nodes[node_id] = Node(
                    node_id, new_coords, node.dof_ids, node.constraints
                )
            else:
                deformed_mesh.nodes[node_id] = node

        return deformed_mesh
