"""Field visualization for scalar, vector, and tensor data on meshes."""

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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple
import warnings

import numpy as np
from scipy.interpolate import griddata
from scipy.spatial import cKDTree

from .mesh import FEAMesh
from ..figure import VizlyFigure

try:
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
    from matplotlib.cm import ScalarMappable
    from mpl_toolkits.axes_grid1 import make_axes_locatable
except ImportError:
    warnings.warn("Matplotlib not fully available for field visualization")


logger = logging.getLogger(__name__)


class FieldType(Enum):
    """Types of field data."""

    SCALAR = "scalar"
    VECTOR = "vector"
    TENSOR = "tensor"


class InterpolationMethod(Enum):
    """Interpolation methods for field data."""

    NEAREST = "nearest"
    LINEAR = "linear"
    CUBIC = "cubic"
    RBF = "rbf"  # Radial basis function


@dataclass
class FieldData:
    """Container for field data on a mesh."""

    values: np.ndarray
    locations: np.ndarray  # Node coordinates where values are defined
    field_type: FieldType
    name: str
    units: Optional[str] = None
    time_step: Optional[float] = None


class BaseField(ABC):
    """Abstract base class for field visualization."""

    def __init__(self, mesh: FEAMesh, figure: Optional[VizlyFigure] = None) -> None:
        self.mesh = mesh
        self.figure = figure or VizlyFigure()
        self.field_data: Dict[str, FieldData] = {}

    @abstractmethod
    def render(self, field_name: str, **kwargs) -> None:
        """Render the field."""
        ...

    def add_field_data(self, field_data: FieldData) -> None:
        """Add field data to the visualization."""
        self.field_data[field_data.name] = field_data

    def interpolate_to_grid(
        self,
        field_name: str,
        resolution: Tuple[int, int, int] = (50, 50, 50),
        method: InterpolationMethod = InterpolationMethod.LINEAR,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Interpolate field data to a regular grid."""
        if field_name not in self.field_data:
            raise ValueError(f"Field '{field_name}' not found")

        field = self.field_data[field_name]

        # Get mesh bounding box
        min_coords, max_coords = self.mesh.get_bounding_box()

        # Create regular grid
        x = np.linspace(min_coords[0], max_coords[0], resolution[0])
        y = np.linspace(min_coords[1], max_coords[1], resolution[1])
        z = np.linspace(min_coords[2], max_coords[2], resolution[2])

        grid_x, grid_y, grid_z = np.meshgrid(x, y, z, indexing="ij")
        grid_points = np.column_stack((grid_x.ravel(), grid_y.ravel(), grid_z.ravel()))

        # Interpolate field values to grid
        if method == InterpolationMethod.NEAREST:
            tree = cKDTree(field.locations)
            _, indices = tree.query(grid_points)
            interpolated_values = field.values[indices]
        else:
            # Use scipy's griddata for linear/cubic interpolation
            method_map = {
                InterpolationMethod.LINEAR: "linear",
                InterpolationMethod.CUBIC: "cubic",
            }
            scipy_method = method_map.get(method, "linear")

            if field.field_type == FieldType.SCALAR:
                interpolated_values = griddata(
                    field.locations,
                    field.values,
                    grid_points,
                    method=scipy_method,
                    fill_value=0.0,
                )
            else:
                # For vector/tensor fields, interpolate each component
                interpolated_values = np.zeros(
                    (len(grid_points), field.values.shape[1])
                )
                for i in range(field.values.shape[1]):
                    interpolated_values[:, i] = griddata(
                        field.locations,
                        field.values[:, i],
                        grid_points,
                        method=scipy_method,
                        fill_value=0.0,
                    )

        # Reshape back to grid
        if field.field_type == FieldType.SCALAR:
            interpolated_grid = interpolated_values.reshape(resolution)
        else:
            interpolated_grid = interpolated_values.reshape(
                (*resolution, field.values.shape[1])
            )

        grid_coords = (grid_x, grid_y, grid_z)
        return grid_coords, interpolated_grid


class ScalarField(BaseField):
    """Visualization for scalar fields (temperature, pressure, stress, etc.)."""

    def render(
        self,
        field_name: str,
        colormap: str = "viridis",
        show_colorbar: bool = True,
        contour_levels: Optional[int] = None,
        surface_plot: bool = True,
        clip_range: Optional[Tuple[float, float]] = None,
        alpha: float = 1.0,
    ) -> None:
        """Render scalar field on mesh."""

        if field_name not in self.field_data:
            raise ValueError(f"Scalar field '{field_name}' not found")

        field = self.field_data[field_name]
        if field.field_type != FieldType.SCALAR:
            raise ValueError(f"Field '{field_name}' is not a scalar field")

        # Get mesh surface
        vertices, faces = self.mesh.get_surface_mesh()

        # Map field values to vertices
        scalar_values = self._map_field_to_vertices(field, vertices)

        # Apply clipping if specified
        if clip_range:
            scalar_values = np.clip(scalar_values, clip_range[0], clip_range[1])

        # Ensure 3D axes
        if not hasattr(self.figure.axes, "plot_trisurf"):
            axes = self.figure.figure.add_subplot(111, projection="3d")
            self.figure.bind_axes(axes)

        if surface_plot:
            # Surface plot with colors
            x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]

            # Create triangulated surface with scalar coloring
            surf = self.figure.axes.plot_trisurf(
                x,
                y,
                z,
                triangles=faces,
                facecolors=plt.cm.get_cmap(colormap)(
                    Normalize(vmin=np.min(scalar_values), vmax=np.max(scalar_values))(
                        scalar_values
                    )
                ),
                alpha=alpha,
            )

            # Add colorbar
            if show_colorbar:
                mappable = ScalarMappable(
                    norm=Normalize(
                        vmin=np.min(scalar_values), vmax=np.max(scalar_values)
                    ),
                    cmap=colormap,
                )
                mappable.set_array(scalar_values)

                # Create colorbar
                divider = make_axes_locatable(self.figure.axes)
                cax = divider.append_axes("right", size="5%", pad=0.1)
                cbar = self.figure.figure.colorbar(mappable, cax=cax)
                cbar.set_label(f"{field.name} ({field.units or 'units'})")

        if contour_levels:
            # Add contour lines
            self._add_contour_lines(field, contour_levels, colormap)

    def render_contour_plot(
        self,
        field_name: str,
        levels: int = 10,
        colormap: str = "viridis",
        filled: bool = True,
        show_labels: bool = False,
    ) -> None:
        """Render 2D contour plot of scalar field."""

        if field_name not in self.field_data:
            raise ValueError(f"Scalar field '{field_name}' not found")

        field = self.field_data[field_name]

        # Create 2D grid for contouring
        grid_coords, interpolated_grid = self.interpolate_to_grid(
            field_name, resolution=(100, 100, 1)
        )

        # Extract 2D slice (assuming z-constant)
        x_grid, y_grid = grid_coords[0][:, :, 0], grid_coords[1][:, :, 0]
        z_values = interpolated_grid[:, :, 0]

        # Create contour plot
        if filled:
            contour = self.figure.axes.contourf(
                x_grid, y_grid, z_values, levels=levels, cmap=colormap
            )
        else:
            contour = self.figure.axes.contour(
                x_grid, y_grid, z_values, levels=levels, colors="black"
            )

        if show_labels:
            self.figure.axes.clabel(contour, inline=True, fontsize=8)

        # Add colorbar for filled contours
        if filled:
            cbar = self.figure.figure.colorbar(contour)
            cbar.set_label(f"{field.name} ({field.units or 'units'})")

    def render_isosurface(
        self,
        field_name: str,
        iso_value: float,
        colormap: str = "viridis",
        alpha: float = 0.7,
    ) -> None:
        """Render isosurface of scalar field."""

        # This would require marching cubes algorithm
        # For now, implement a simplified version
        logger.warning("Isosurface rendering not fully implemented yet")

    def _map_field_to_vertices(
        self, field: FieldData, vertices: np.ndarray
    ) -> np.ndarray:
        """Map field values from their locations to mesh vertices."""
        if len(field.values) == len(vertices):
            # Field values are already at vertices
            return field.values

        # Need to interpolate from field locations to vertices
        tree = cKDTree(field.locations)
        distances, indices = tree.query(vertices)

        # Use nearest neighbor for now
        return field.values[indices]

    def _add_contour_lines(self, field: FieldData, levels: int, colormap: str) -> None:
        """Add contour lines to 3D surface."""
        # This would require projecting contours onto the 3D surface
        # Simplified implementation for now
        pass


class VectorField(BaseField):
    """Visualization for vector fields (velocity, displacement, force, etc.)."""

    def render(
        self,
        field_name: str,
        scale_factor: float = 1.0,
        arrow_density: float = 1.0,
        colormap: str = "viridis",
        color_by_magnitude: bool = True,
        show_colorbar: bool = True,
        normalize_arrows: bool = False,
    ) -> None:
        """Render vector field as arrows on mesh."""

        if field_name not in self.field_data:
            raise ValueError(f"Vector field '{field_name}' not found")

        field = self.field_data[field_name]
        if field.field_type != FieldType.VECTOR:
            raise ValueError(f"Field '{field_name}' is not a vector field")

        # Subsample points based on arrow density
        n_points = len(field.locations)
        n_arrows = int(n_points * arrow_density)
        indices = np.random.choice(n_points, n_arrows, replace=False)

        positions = field.locations[indices]
        vectors = field.values[indices]

        # Calculate magnitudes for coloring
        magnitudes = np.linalg.norm(vectors, axis=1)

        if normalize_arrows:
            # Normalize vector lengths but keep magnitude for coloring
            non_zero_mask = magnitudes > 0
            vectors[non_zero_mask] = (
                vectors[non_zero_mask] / magnitudes[non_zero_mask][:, np.newaxis]
            )

        # Ensure 3D axes
        if not hasattr(self.figure.axes, "quiver3D"):
            axes = self.figure.figure.add_subplot(111, projection="3d")
            self.figure.bind_axes(axes)

        # Create quiver plot
        x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]
        u, v, w = (
            vectors[:, 0] * scale_factor,
            vectors[:, 1] * scale_factor,
            vectors[:, 2] * scale_factor,
        )

        if color_by_magnitude:
            # Color arrows by magnitude
            quiver = self.figure.axes.quiver3D(
                x,
                y,
                z,
                u,
                v,
                w,
                cmap=colormap,
                array=magnitudes,
                length=1.0,
                normalize=False,
            )

            if show_colorbar:
                cbar = self.figure.figure.colorbar(quiver)
                cbar.set_label(f"{field.name} magnitude ({field.units or 'units'})")
        else:
            # Single color arrows
            self.figure.axes.quiver3D(x, y, z, u, v, w, length=1.0, normalize=False)

    def render_streamlines(
        self,
        field_name: str,
        starting_points: Optional[np.ndarray] = None,
        colormap: str = "viridis",
        density: float = 1.0,
        max_length: float = 10.0,
    ) -> None:
        """Render streamlines of vector field."""

        if field_name not in self.field_data:
            raise ValueError(f"Vector field '{field_name}' not found")

        field = self.field_data[field_name]

        # Generate starting points if not provided
        if starting_points is None:
            min_coords, max_coords = self.mesh.get_bounding_box()
            n_seeds = int(20 * density)
            starting_points = np.random.uniform(min_coords, max_coords, (n_seeds, 3))

        # Integrate streamlines
        streamlines = []
        for start_point in starting_points:
            streamline = self._integrate_streamline(field, start_point, max_length)
            if len(streamline) > 1:
                streamlines.append(streamline)

        # Ensure 3D axes
        if not hasattr(self.figure.axes, "plot3D"):
            axes = self.figure.figure.add_subplot(111, projection="3d")
            self.figure.bind_axes(axes)

        # Plot streamlines
        for streamline in streamlines:
            x, y, z = streamline[:, 0], streamline[:, 1], streamline[:, 2]
            self.figure.axes.plot3D(x, y, z, alpha=0.7)

    def _integrate_streamline(
        self,
        field: FieldData,
        start_point: np.ndarray,
        max_length: float,
        step_size: float = 0.1,
    ) -> np.ndarray:
        """Integrate a streamline using simple Euler method."""

        streamline = [start_point]
        current_point = start_point.copy()
        total_length = 0.0

        tree = cKDTree(field.locations)

        while total_length < max_length:
            # Find nearest field value
            distance, index = tree.query(current_point)

            if distance > step_size * 5:  # Too far from any data point
                break

            velocity = field.values[index]
            speed = np.linalg.norm(velocity)

            if speed < 1e-6:  # Near stagnation point
                break

            # Take step
            direction = velocity / speed
            step = direction * step_size
            current_point = current_point + step
            streamline.append(current_point.copy())

            total_length += step_size

        return np.array(streamline)


class TensorField(BaseField):
    """Visualization for tensor fields (stress, strain, etc.)."""

    def render(
        self,
        field_name: str,
        component: str = "von_mises",
        colormap: str = "jet",
        show_colorbar: bool = True,
        principal_directions: bool = False,
    ) -> None:
        """Render tensor field component."""

        if field_name not in self.field_data:
            raise ValueError(f"Tensor field '{field_name}' not found")

        field = self.field_data[field_name]
        if field.field_type != FieldType.TENSOR:
            raise ValueError(f"Field '{field_name}' is not a tensor field")

        # Extract scalar component from tensor
        scalar_values = self._extract_tensor_component(field.values, component)

        # Create scalar field for rendering
        scalar_field = FieldData(
            values=scalar_values,
            locations=field.locations,
            field_type=FieldType.SCALAR,
            name=f"{field.name}_{component}",
            units=field.units,
            time_step=field.time_step,
        )

        # Add to field data temporarily
        temp_name = f"temp_{component}"
        self.field_data[temp_name] = scalar_field

        # Render as scalar field
        scalar_renderer = ScalarField(self.mesh, self.figure)
        scalar_renderer.field_data = self.field_data
        scalar_renderer.render(
            temp_name, colormap=colormap, show_colorbar=show_colorbar
        )

        # Clean up temporary field
        del self.field_data[temp_name]

        if principal_directions:
            self._render_principal_directions(field)

    def _extract_tensor_component(
        self, tensor_values: np.ndarray, component: str
    ) -> np.ndarray:
        """Extract scalar component from tensor field."""

        if component == "von_mises":
            # Calculate von Mises stress
            return self._calculate_von_mises(tensor_values)
        elif component == "hydrostatic":
            # Calculate hydrostatic pressure
            return self._calculate_hydrostatic(tensor_values)
        elif component in ["xx", "yy", "zz", "xy", "xz", "yz"]:
            # Direct tensor component
            component_map = {
                "xx": (0, 0),
                "yy": (1, 1),
                "zz": (2, 2),
                "xy": (0, 1),
                "xz": (0, 2),
                "yz": (1, 2),
            }
            i, j = component_map[component]
            return (
                tensor_values[:, i, j]
                if tensor_values.ndim == 3
                else tensor_values[:, i * 3 + j]
            )
        else:
            raise ValueError(f"Unknown tensor component: {component}")

    def _calculate_von_mises(self, stress_tensors: np.ndarray) -> np.ndarray:
        """Calculate von Mises stress from stress tensors."""

        if stress_tensors.ndim == 3:  # Full 3x3 tensors
            s11 = stress_tensors[:, 0, 0]
            s22 = stress_tensors[:, 1, 1]
            s33 = stress_tensors[:, 2, 2]
            s12 = stress_tensors[:, 0, 1]
            s13 = stress_tensors[:, 0, 2]
            s23 = stress_tensors[:, 1, 2]
        else:  # Voigt notation [s11, s22, s33, s12, s13, s23]
            s11 = stress_tensors[:, 0]
            s22 = stress_tensors[:, 1]
            s33 = stress_tensors[:, 2]
            s12 = stress_tensors[:, 3]
            s13 = stress_tensors[:, 4]
            s23 = stress_tensors[:, 5]

        # von Mises stress formula
        von_mises = np.sqrt(
            0.5
            * (
                (s11 - s22) ** 2
                + (s22 - s33) ** 2
                + (s33 - s11) ** 2
                + 6 * (s12**2 + s13**2 + s23**2)
            )
        )

        return von_mises

    def _calculate_hydrostatic(self, stress_tensors: np.ndarray) -> np.ndarray:
        """Calculate hydrostatic pressure from stress tensors."""

        if stress_tensors.ndim == 3:  # Full 3x3 tensors
            trace = np.trace(stress_tensors, axis1=1, axis2=2)
        else:  # Voigt notation
            trace = stress_tensors[:, 0] + stress_tensors[:, 1] + stress_tensors[:, 2]

        return trace / 3.0

    def _render_principal_directions(self, field: FieldData) -> None:
        """Render principal stress/strain directions."""

        # Calculate principal directions (eigenvectors)
        positions = field.locations[::10]  # Subsample for clarity
        tensors = field.values[::10]

        # Ensure 3D axes
        if not hasattr(self.figure.axes, "quiver3D"):
            axes = self.figure.figure.add_subplot(111, projection="3d")
            self.figure.bind_axes(axes)

        for i, (pos, tensor) in enumerate(zip(positions, tensors)):
            if tensor.ndim == 1:  # Convert Voigt to full tensor
                full_tensor = np.array(
                    [
                        [tensor[0], tensor[3], tensor[4]],
                        [tensor[3], tensor[1], tensor[5]],
                        [tensor[4], tensor[5], tensor[2]],
                    ]
                )
            else:
                full_tensor = tensor

            # Calculate eigenvalues and eigenvectors
            eigenvals, eigenvecs = np.linalg.eigh(full_tensor)

            # Sort by eigenvalue magnitude
            sort_indices = np.argsort(np.abs(eigenvals))[::-1]
            eigenvals = eigenvals[sort_indices]
            eigenvecs = eigenvecs[:, sort_indices]

            # Plot principal directions
            scale = 0.1
            colors = ["red", "green", "blue"]

            for j in range(3):
                direction = eigenvecs[:, j] * eigenvals[j] * scale
                self.figure.axes.quiver3D(
                    pos[0],
                    pos[1],
                    pos[2],
                    direction[0],
                    direction[1],
                    direction[2],
                    color=colors[j],
                    alpha=0.7,
                )
