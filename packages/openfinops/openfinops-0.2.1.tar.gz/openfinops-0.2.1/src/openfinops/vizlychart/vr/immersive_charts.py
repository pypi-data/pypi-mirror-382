"""Immersive chart implementations for VR/AR environments."""

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

import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import logging

from .spatial import SpatialObject, SpatialGeometry, SpatialMaterial, SpatialRenderer
from ..rendering.pure_engine import Color

logger = logging.getLogger(__name__)


class ImmersiveChart:
    """Base class for immersive VR/AR charts."""

    def __init__(self, chart_id: str, chart_type: str):
        self.chart_id = chart_id
        self.chart_type = chart_type
        self.spatial_objects: List[SpatialObject] = []

        # Interaction properties
        self.interactive = True
        self.hover_enabled = True
        self.selection_enabled = True

        # Animation properties
        self.animated = False
        self.animation_duration = 1.0
        self.animation_progress = 0.0

        # Scale and positioning
        self.world_scale = 1.0
        self.base_position = np.array([0.0, 1.0, -2.0])

    def generate_spatial_objects(self) -> List[SpatialObject]:
        """Generate spatial objects for the chart."""
        return self.spatial_objects

    def update_data(self, data: Dict[str, Any]):
        """Update chart data and regenerate spatial objects."""
        self._clear_objects()
        self._generate_from_data(data)

    def set_position(self, position: np.ndarray):
        """Set the chart position in world space."""
        self.base_position = position
        self._update_object_positions()

    def set_scale(self, scale: float):
        """Set the chart scale."""
        self.world_scale = scale
        self._update_object_scales()

    def animate_in(self, duration: float = 1.0):
        """Animate chart appearance."""
        self.animated = True
        self.animation_duration = duration
        self.animation_progress = 0.0

    def _clear_objects(self):
        """Clear existing spatial objects."""
        self.spatial_objects.clear()

    def _generate_from_data(self, data: Dict[str, Any]):
        """Generate spatial objects from data (to be implemented by subclasses)."""
        pass

    def _update_object_positions(self):
        """Update positions of all spatial objects."""
        for obj in self.spatial_objects:
            obj.transform.position += self.base_position

    def _update_object_scales(self):
        """Update scales of all spatial objects."""
        for obj in self.spatial_objects:
            obj.set_scale(self.world_scale)


class VRScatterChart(ImmersiveChart):
    """3D scatter plot for VR environments."""

    def __init__(self, chart_id: str):
        super().__init__(chart_id, "vr_scatter")
        self.point_size = 0.05  # meters
        self.color_map = "viridis"

    def _generate_from_data(self, data: Dict[str, Any]):
        """Generate 3D scatter plot objects."""
        x = np.array(data.get('x', []))
        y = np.array(data.get('y', []))
        z = np.array(data.get('z', []))
        colors = data.get('colors', None)
        sizes = data.get('sizes', None)

        if len(x) == 0 or len(x) != len(y) or len(x) != len(z):
            logger.warning("Invalid scatter data provided")
            return

        # Normalize coordinates to reasonable VR space
        x_norm = self._normalize_array(x) * 2.0  # 2 meter spread
        y_norm = self._normalize_array(y) * 2.0
        z_norm = self._normalize_array(z) * 2.0

        # Generate point objects
        for i in range(len(x)):
            point_id = f"{self.chart_id}_point_{i}"

            # Create sphere for each point
            point_size = sizes[i] if sizes is not None else self.point_size
            point_obj = SpatialObject.create_sphere(point_id, point_size, subdivisions=8)

            # Set position
            position = np.array([x_norm[i], y_norm[i], z_norm[i]]) + self.base_position
            point_obj.set_position(position)

            # Set color
            if colors is not None:
                if isinstance(colors[i], str):
                    point_obj.material.color = Color.from_name(colors[i])
                elif len(colors[i]) >= 3:
                    point_obj.material.color = Color(colors[i][0], colors[i][1], colors[i][2])

            point_obj.interactive = self.interactive
            self.spatial_objects.append(point_obj)

        logger.info(f"Generated {len(self.spatial_objects)} points for VR scatter chart")

    def _normalize_array(self, arr: np.ndarray) -> np.ndarray:
        """Normalize array to [0, 1] range."""
        if len(arr) == 0:
            return arr

        min_val, max_val = np.min(arr), np.max(arr)
        if max_val == min_val:
            return np.zeros_like(arr)

        return (arr - min_val) / (max_val - min_val) - 0.5  # Center around 0


class VRSurfaceChart(ImmersiveChart):
    """3D surface plot for VR environments."""

    def __init__(self, chart_id: str):
        super().__init__(chart_id, "vr_surface")
        self.resolution = (20, 20)  # Grid resolution
        self.wireframe = False

    def _generate_from_data(self, data: Dict[str, Any]):
        """Generate 3D surface mesh objects."""
        X = np.array(data.get('X', []))
        Y = np.array(data.get('Y', []))
        Z = np.array(data.get('Z', []))

        if X.size == 0 or X.shape != Y.shape or X.shape != Z.shape:
            logger.warning("Invalid surface data provided")
            return

        # Create surface mesh
        vertices = []
        faces = []
        colors = []

        rows, cols = X.shape

        # Generate vertices
        for i in range(rows):
            for j in range(cols):
                # Normalize to VR space
                x_norm = (X[i, j] - np.min(X)) / (np.max(X) - np.min(X)) - 0.5
                y_norm = (Z[i, j] - np.min(Z)) / (np.max(Z) - np.min(Z))  # Height
                z_norm = (Y[i, j] - np.min(Y)) / (np.max(Y) - np.min(Y)) - 0.5

                vertices.append([x_norm * 2, y_norm * 2, z_norm * 2])

                # Color based on height
                height_norm = (Z[i, j] - np.min(Z)) / (np.max(Z) - np.min(Z))
                color = self._height_to_color(height_norm)
                colors.append(color)

        # Generate faces (triangles)
        for i in range(rows - 1):
            for j in range(cols - 1):
                # Current vertex indices
                v0 = i * cols + j
                v1 = i * cols + (j + 1)
                v2 = (i + 1) * cols + j
                v3 = (i + 1) * cols + (j + 1)

                # Two triangles per quad
                faces.append([v0, v1, v2])
                faces.append([v1, v3, v2])

        # Create surface object
        geometry = SpatialGeometry(
            vertices=np.array(vertices),
            faces=np.array(faces)
        )

        surface_obj = SpatialObject(f"{self.chart_id}_surface", geometry)
        surface_obj.set_position(self.base_position)
        surface_obj.interactive = self.interactive

        self.spatial_objects.append(surface_obj)

        logger.info(f"Generated surface with {len(vertices)} vertices and {len(faces)} faces")

    def _height_to_color(self, height_norm: float) -> Color:
        """Convert normalized height to color."""
        # Simple blue-to-red gradient
        if height_norm < 0.5:
            # Blue to green
            r = 0.0
            g = height_norm * 2
            b = 1.0 - height_norm * 2
        else:
            # Green to red
            r = (height_norm - 0.5) * 2
            g = 1.0 - (height_norm - 0.5) * 2
            b = 0.0

        return Color(r, g, b, 1.0)


class VRLineChart(ImmersiveChart):
    """3D line chart for VR environments."""

    def __init__(self, chart_id: str):
        super().__init__(chart_id, "vr_line")
        self.line_width = 0.02  # meters
        self.tube_resolution = 8

    def _generate_from_data(self, data: Dict[str, Any]):
        """Generate 3D line objects as tubes."""
        lines = data.get('lines', [])

        for line_idx, line_data in enumerate(lines):
            x = np.array(line_data.get('x', []))
            y = np.array(line_data.get('y', []))
            z = np.array(line_data.get('z', x * 0))  # Default z=0 if not provided

            if len(x) < 2:
                continue

            # Normalize coordinates
            x_norm = self._normalize_array(x) * 2.0
            y_norm = self._normalize_array(y) * 2.0
            z_norm = self._normalize_array(z) * 2.0

            # Create tube geometry for line
            vertices, faces = self._create_tube_geometry(x_norm, y_norm, z_norm)

            geometry = SpatialGeometry(
                vertices=np.array(vertices),
                faces=np.array(faces)
            )

            line_obj = SpatialObject(f"{self.chart_id}_line_{line_idx}", geometry)
            line_obj.set_position(self.base_position)

            # Set line color
            color = line_data.get('color', 'blue')
            if isinstance(color, str):
                line_obj.material.color = Color.from_name(color)

            self.spatial_objects.append(line_obj)

    def _create_tube_geometry(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> Tuple[List, List]:
        """Create tube geometry for a 3D line."""
        vertices = []
        faces = []

        points = np.column_stack([x, y, z])

        for i in range(len(points) - 1):
            # Current and next points
            p1, p2 = points[i], points[i + 1]

            # Direction vector
            direction = p2 - p1
            length = np.linalg.norm(direction)

            if length < 1e-6:
                continue

            direction = direction / length

            # Create perpendicular vectors
            if abs(direction[1]) < 0.9:
                up = np.array([0, 1, 0])
            else:
                up = np.array([1, 0, 0])

            right = np.cross(direction, up)
            right = right / np.linalg.norm(right)
            up = np.cross(right, direction)

            # Create ring vertices
            base_idx = len(vertices)

            for j in range(self.tube_resolution):
                angle = 2 * np.pi * j / self.tube_resolution

                offset = (np.cos(angle) * right + np.sin(angle) * up) * self.line_width

                # Add vertices for both ends of segment
                vertices.append(p1 + offset)
                vertices.append(p2 + offset)

                # Create faces connecting rings
                if j < self.tube_resolution - 1:
                    # Two triangles per segment
                    v0 = base_idx + j * 2
                    v1 = base_idx + j * 2 + 1
                    v2 = base_idx + (j + 1) * 2
                    v3 = base_idx + (j + 1) * 2 + 1

                    faces.append([v0, v1, v2])
                    faces.append([v1, v3, v2])
                else:
                    # Connect to first vertices
                    v0 = base_idx + j * 2
                    v1 = base_idx + j * 2 + 1
                    v2 = base_idx
                    v3 = base_idx + 1

                    faces.append([v0, v1, v2])
                    faces.append([v1, v3, v2])

        return vertices, faces


class AROverlayChart(ImmersiveChart):
    """AR overlay chart that appears over real-world surfaces."""

    def __init__(self, chart_id: str):
        super().__init__(chart_id, "ar_overlay")
        self.anchor_plane: Optional[Dict] = None
        self.opacity = 0.8

    def set_anchor_plane(self, plane_position: np.ndarray, plane_normal: np.ndarray, plane_size: Tuple[float, float]):
        """Anchor chart to a detected plane."""
        self.anchor_plane = {
            'position': plane_position,
            'normal': plane_normal,
            'size': plane_size
        }

    def _generate_from_data(self, data: Dict[str, Any]):
        """Generate AR overlay chart objects."""
        chart_type = data.get('type', 'bar')

        if chart_type == 'bar':
            self._generate_ar_bar_chart(data)
        elif chart_type == 'line':
            self._generate_ar_line_chart(data)
        else:
            logger.warning(f"Unsupported AR chart type: {chart_type}")

    def _generate_ar_bar_chart(self, data: Dict[str, Any]):
        """Generate AR bar chart on a plane."""
        values = np.array(data.get('values', []))
        labels = data.get('labels', [f"Bar {i}" for i in range(len(values))])

        if len(values) == 0:
            return

        if not self.anchor_plane:
            logger.warning("No anchor plane set for AR chart")
            return

        # Normalize values
        max_val = np.max(values)
        if max_val == 0:
            return

        normalized_values = values / max_val

        # Create bars on the plane
        plane_pos = self.anchor_plane['position']
        plane_size = self.anchor_plane['size']

        bar_width = plane_size[0] / len(values) * 0.8

        for i, (value, label) in enumerate(zip(normalized_values, labels)):
            bar_height = value * 0.5  # Max 0.5 meters high

            # Position on plane
            x_offset = (i - len(values) / 2) * bar_width * 1.2
            bar_position = plane_pos + np.array([x_offset, bar_height / 2, 0])

            # Create bar
            bar_obj = SpatialObject.create_cube(f"{self.chart_id}_bar_{i}", bar_width)
            bar_obj.set_position(bar_position)
            bar_obj.set_scale(np.array([1.0, bar_height / bar_width, 1.0]))

            # Set color based on value
            color_intensity = 0.2 + 0.8 * value  # Darker for smaller values
            bar_obj.material.color = Color(0.2, 0.6 * color_intensity, 1.0, self.opacity)
            bar_obj.material.opacity = self.opacity

            self.spatial_objects.append(bar_obj)

    def _generate_ar_line_chart(self, data: Dict[str, Any]):
        """Generate AR line chart on a plane."""
        x = np.array(data.get('x', []))
        y = np.array(data.get('y', []))

        if len(x) < 2 or len(x) != len(y):
            return

        if not self.anchor_plane:
            logger.warning("No anchor plane set for AR chart")
            return

        # Normalize coordinates to plane
        x_norm = (x - np.min(x)) / (np.max(x) - np.min(x)) - 0.5
        y_norm = (y - np.min(y)) / (np.max(y) - np.min(y)) - 0.5

        plane_pos = self.anchor_plane['position']
        plane_size = self.anchor_plane['size']

        # Create line segments
        for i in range(len(x) - 1):
            start_pos = plane_pos + np.array([
                x_norm[i] * plane_size[0],
                0.01,  # Slightly above plane
                y_norm[i] * plane_size[1]
            ])

            end_pos = plane_pos + np.array([
                x_norm[i + 1] * plane_size[0],
                0.01,
                y_norm[i + 1] * plane_size[1]
            ])

            # Create line segment as thin cylinder
            direction = end_pos - start_pos
            length = np.linalg.norm(direction)

            if length < 1e-6:
                continue

            segment_obj = SpatialObject.create_cube(f"{self.chart_id}_segment_{i}", 0.005)

            # Position and orient the segment
            mid_pos = (start_pos + end_pos) / 2
            segment_obj.set_position(mid_pos)
            segment_obj.set_scale(np.array([0.005, 0.005, length]))

            # Set line color
            segment_obj.material.color = Color(1.0, 0.2, 0.2, self.opacity)
            segment_obj.material.opacity = self.opacity

            self.spatial_objects.append(segment_obj)


class ImmersiveChartRenderer:
    """Renderer for immersive charts in VR/AR environments."""

    def __init__(self, spatial_renderer: SpatialRenderer):
        self.spatial_renderer = spatial_renderer
        self.charts: Dict[str, ImmersiveChart] = {}

    def add_chart(self, chart: ImmersiveChart):
        """Add an immersive chart to the renderer."""
        self.charts[chart.chart_id] = chart

        # Add chart's spatial objects to renderer
        for obj in chart.spatial_objects:
            self.spatial_renderer.add_spatial_object(obj)

    def remove_chart(self, chart_id: str):
        """Remove a chart from the renderer."""
        if chart_id in self.charts:
            chart = self.charts[chart_id]

            # Remove spatial objects
            for obj in chart.spatial_objects:
                self.spatial_renderer.remove_spatial_object(obj)

            del self.charts[chart_id]

    def update_chart(self, chart_id: str, data: Dict[str, Any]):
        """Update chart data and re-render."""
        if chart_id in self.charts:
            chart = self.charts[chart_id]

            # Remove old objects
            for obj in chart.spatial_objects:
                self.spatial_renderer.remove_spatial_object(obj)

            # Update chart
            chart.update_data(data)

            # Add new objects
            for obj in chart.spatial_objects:
                self.spatial_renderer.add_spatial_object(obj)

    def get_chart_stats(self) -> Dict[str, Any]:
        """Get statistics about rendered charts."""
        total_objects = sum(len(chart.spatial_objects) for chart in self.charts.values())

        return {
            'chart_count': len(self.charts),
            'total_spatial_objects': total_objects,
            'chart_types': [chart.chart_type for chart in self.charts.values()],
            'charts': {
                chart_id: {
                    'type': chart.chart_type,
                    'objects': len(chart.spatial_objects),
                    'interactive': chart.interactive,
                    'animated': chart.animated
                }
                for chart_id, chart in self.charts.items()
            }
        }