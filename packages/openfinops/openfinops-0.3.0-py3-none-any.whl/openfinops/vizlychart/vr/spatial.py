"""Spatial rendering and canvas systems for VR/AR visualization."""

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
from dataclasses import dataclass, field
import logging

from ..rendering.pure_engine import PureCanvas, Color

logger = logging.getLogger(__name__)


@dataclass
class SpatialTransform:
    """3D spatial transformation for VR/AR objects."""
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 1.0]))  # quaternion
    scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))

    @property
    def matrix(self) -> np.ndarray:
        """Get 4x4 transformation matrix."""
        # Convert quaternion to rotation matrix
        x, y, z, w = self.rotation

        # Rotation matrix from quaternion
        R = np.array([
            [1 - 2*(y*y + z*z), 2*(x*y - z*w), 2*(x*z + y*w)],
            [2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w)],
            [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)]
        ])

        # 4x4 transformation matrix
        T = np.eye(4)
        T[:3, :3] = R * self.scale
        T[:3, 3] = self.position

        return T


@dataclass
class SpatialViewport:
    """Spatial viewport for immersive rendering."""
    eye_position: np.ndarray
    target_position: np.ndarray
    up_vector: np.ndarray = field(default_factory=lambda: np.array([0.0, 1.0, 0.0]))
    fov: float = 90.0  # Field of view in degrees
    near_plane: float = 0.1
    far_plane: float = 1000.0

    @property
    def view_matrix(self) -> np.ndarray:
        """Get view matrix for this viewport."""
        forward = self.target_position - self.eye_position
        forward = forward / np.linalg.norm(forward)

        right = np.cross(forward, self.up_vector)
        right = right / np.linalg.norm(right)

        up = np.cross(right, forward)

        view_matrix = np.eye(4)
        view_matrix[:3, 0] = right
        view_matrix[:3, 1] = up
        view_matrix[:3, 2] = -forward
        view_matrix[:3, 3] = self.eye_position

        return np.linalg.inv(view_matrix)

    @property
    def projection_matrix(self) -> np.ndarray:
        """Get perspective projection matrix."""
        aspect = 1.0  # Assume square for VR/AR
        fov_rad = np.radians(self.fov)

        f = 1.0 / np.tan(fov_rad / 2.0)

        proj = np.zeros((4, 4))
        proj[0, 0] = f / aspect
        proj[1, 1] = f
        proj[2, 2] = (self.far_plane + self.near_plane) / (self.near_plane - self.far_plane)
        proj[2, 3] = (2 * self.far_plane * self.near_plane) / (self.near_plane - self.far_plane)
        proj[3, 2] = -1.0

        return proj


class SpatialRenderer:
    """Advanced spatial renderer for VR/AR environments."""

    def __init__(self, width: int = 2048, height: int = 2048):
        self.width = width
        self.height = height

        # Stereo rendering
        self.left_viewport: Optional[SpatialViewport] = None
        self.right_viewport: Optional[SpatialViewport] = None
        self.ipd = 0.064  # Interpupillary distance in meters

        # Render targets
        self.left_canvas = PureCanvas(width, height)
        self.right_canvas = PureCanvas(width, height)

        # Scene objects
        self.spatial_objects: List[SpatialObject] = []

        # Performance tracking
        self.render_time = 0.0
        self.triangles_rendered = 0

    def setup_stereo_cameras(self, head_position: np.ndarray, head_rotation: np.ndarray,
                           target_position: Optional[np.ndarray] = None):
        """Setup stereo camera configuration."""
        if target_position is None:
            # Look forward by default
            forward = np.array([0, 0, -1])
            forward = head_rotation @ forward
            target_position = head_position + forward

        # Calculate eye positions
        right_vector = np.array([1, 0, 0])
        right_vector = head_rotation @ right_vector

        left_eye = head_position - right_vector * (self.ipd / 2)
        right_eye = head_position + right_vector * (self.ipd / 2)

        self.left_viewport = SpatialViewport(left_eye, target_position)
        self.right_viewport = SpatialViewport(right_eye, target_position)

    def add_spatial_object(self, obj: 'SpatialObject'):
        """Add a spatial object to the scene."""
        self.spatial_objects.append(obj)

    def remove_spatial_object(self, obj: 'SpatialObject'):
        """Remove a spatial object from the scene."""
        if obj in self.spatial_objects:
            self.spatial_objects.remove(obj)

    def render_stereo_frame(self) -> Tuple[PureCanvas, PureCanvas]:
        """Render a stereo frame for VR."""
        start_time = time.time()

        if not self.left_viewport or not self.right_viewport:
            raise RuntimeError("Stereo cameras not configured")

        # Clear canvases
        self.left_canvas.clear()
        self.right_canvas.clear()

        # Render left eye
        self._render_eye(self.left_canvas, self.left_viewport)

        # Render right eye
        self._render_eye(self.right_canvas, self.right_viewport)

        self.render_time = time.time() - start_time

        return self.left_canvas, self.right_canvas

    def render_mono_frame(self, viewport: SpatialViewport) -> PureCanvas:
        """Render a mono frame for AR or desktop preview."""
        start_time = time.time()

        canvas = PureCanvas(self.width, self.height)
        canvas.clear()

        self._render_eye(canvas, viewport)

        self.render_time = time.time() - start_time

        return canvas

    def _render_eye(self, canvas: PureCanvas, viewport: SpatialViewport):
        """Render scene for one eye/viewport."""
        view_matrix = viewport.view_matrix
        proj_matrix = viewport.projection_matrix
        mvp_matrix = proj_matrix @ view_matrix

        self.triangles_rendered = 0

        # Render all spatial objects
        for obj in self.spatial_objects:
            if obj.visible:
                obj_mvp = mvp_matrix @ obj.transform.matrix
                self._render_spatial_object(canvas, obj, obj_mvp)

    def _render_spatial_object(self, canvas: PureCanvas, obj: 'SpatialObject', mvp_matrix: np.ndarray):
        """Render a single spatial object."""
        if obj.geometry is None:
            return

        # Transform vertices
        vertices = obj.geometry.vertices
        if len(vertices) == 0:
            return

        # Add homogeneous coordinate
        homogeneous_verts = np.column_stack([vertices, np.ones(len(vertices))])

        # Transform to clip space
        transformed = (mvp_matrix @ homogeneous_verts.T).T

        # Perspective divide and convert to screen space
        screen_coords = transformed[:, :3] / transformed[:, 3:4]

        # Convert to canvas coordinates
        canvas_x = (screen_coords[:, 0] + 1) * canvas.width / 2
        canvas_y = (1 - screen_coords[:, 1]) * canvas.height / 2

        # Render geometry
        if obj.geometry.faces is not None:
            # Render faces
            for face in obj.geometry.faces:
                if len(face) >= 3:
                    face_coords = [(canvas_x[i], canvas_y[i]) for i in face[:3]]

                    # Simple back-face culling
                    v1, v2, v3 = face_coords
                    cross = (v2[0] - v1[0]) * (v3[1] - v1[1]) - (v2[1] - v1[1]) * (v3[0] - v1[0])
                    if cross > 0:  # Front-facing
                        canvas.set_fill_color(obj.material.color)
                        self._draw_triangle(canvas, face_coords)
                        self.triangles_rendered += 1
        else:
            # Render as point cloud
            canvas.set_fill_color(obj.material.color)
            for i in range(len(canvas_x)):
                if 0 <= canvas_x[i] < canvas.width and 0 <= canvas_y[i] < canvas.height:
                    canvas.draw_circle(canvas_x[i], canvas_y[i], 2, fill=True)

    def _draw_triangle(self, canvas: PureCanvas, coords: List[Tuple[float, float]]):
        """Draw a filled triangle."""
        if len(coords) < 3:
            return

        # Simple triangle rasterization (could be optimized)
        points = [coords[0], coords[1], coords[2], coords[0]]  # Close the triangle
        canvas.draw_polyline(points)


class VRCanvas(SpatialRenderer):
    """Specialized VR canvas with room-scale support."""

    def __init__(self, width: int = 2048, height: int = 2048):
        super().__init__(width, height)
        self.room_bounds: Optional[List[Tuple[float, float]]] = None
        self.guardian_system = True

    def setup_room_scale(self, bounds: List[Tuple[float, float]]):
        """Setup room-scale VR boundaries."""
        self.room_bounds = bounds
        logger.info(f"Room-scale VR configured with bounds: {bounds}")

    def render_guardian_bounds(self, canvas: PureCanvas, viewport: SpatialViewport):
        """Render guardian boundary system."""
        if not self.room_bounds or not self.guardian_system:
            return

        # Render room boundaries on the floor
        canvas.set_stroke_color("cyan")
        canvas.set_line_width(2.0)

        # Transform boundary points to screen space
        view_proj = viewport.projection_matrix @ viewport.view_matrix

        boundary_points = []
        for x, z in self.room_bounds:
            world_point = np.array([x, 0, z, 1])  # On the floor (y=0)
            screen_point = view_proj @ world_point

            if screen_point[3] > 0:  # In front of camera
                screen_x = (screen_point[0] / screen_point[3] + 1) * canvas.width / 2
                screen_y = (1 - screen_point[1] / screen_point[3]) * canvas.height / 2
                boundary_points.append((screen_x, screen_y))

        if len(boundary_points) > 2:
            boundary_points.append(boundary_points[0])  # Close the loop
            canvas.draw_polyline(boundary_points)


class ARCanvas(SpatialRenderer):
    """Specialized AR canvas with camera feed integration."""

    def __init__(self, width: int = 1920, height: int = 1080):
        super().__init__(width, height)
        self.camera_feed: Optional[np.ndarray] = None
        self.plane_anchors: List[Dict] = []
        self.light_estimation = True

    def set_camera_feed(self, camera_image: np.ndarray):
        """Set the camera feed background."""
        self.camera_feed = camera_image

    def add_plane_anchor(self, position: np.ndarray, normal: np.ndarray, size: Tuple[float, float]):
        """Add a detected plane anchor."""
        anchor = {
            'position': position,
            'normal': normal,
            'size': size,
            'timestamp': time.time()
        }
        self.plane_anchors.append(anchor)

    def render_ar_frame(self, viewport: SpatialViewport) -> PureCanvas:
        """Render AR frame with camera background."""
        canvas = self.render_mono_frame(viewport)

        # Composite camera feed if available
        if self.camera_feed is not None:
            self._composite_camera_feed(canvas)

        # Render detected planes
        self._render_plane_anchors(canvas, viewport)

        return canvas

    def _composite_camera_feed(self, canvas: PureCanvas):
        """Composite camera feed as background."""
        # In a real implementation, this would blend the camera feed
        # For now, just indicate that camera feed is active
        canvas.set_fill_color(Color(0.1, 0.1, 0.1, 0.5))
        # Would composite actual camera pixels here

    def _render_plane_anchors(self, canvas: PureCanvas, viewport: SpatialViewport):
        """Render detected plane anchors."""
        canvas.set_stroke_color("green")
        canvas.set_line_width(1.0)

        view_proj = viewport.projection_matrix @ viewport.view_matrix

        for anchor in self.plane_anchors:
            pos = anchor['position']
            size = anchor['size']

            # Create plane corners
            corners = [
                pos + np.array([-size[0]/2, 0, -size[1]/2]),
                pos + np.array([size[0]/2, 0, -size[1]/2]),
                pos + np.array([size[0]/2, 0, size[1]/2]),
                pos + np.array([-size[0]/2, 0, size[1]/2]),
            ]

            # Transform to screen space
            screen_corners = []
            for corner in corners:
                world_point = np.append(corner, 1)
                screen_point = view_proj @ world_point

                if screen_point[3] > 0:
                    screen_x = (screen_point[0] / screen_point[3] + 1) * canvas.width / 2
                    screen_y = (1 - screen_point[1] / screen_point[3]) * canvas.height / 2
                    screen_corners.append((screen_x, screen_y))

            # Draw plane outline
            if len(screen_corners) == 4:
                screen_corners.append(screen_corners[0])  # Close the loop
                canvas.draw_polyline(screen_corners)


@dataclass
class SpatialGeometry:
    """Geometry data for spatial objects."""
    vertices: np.ndarray
    faces: Optional[np.ndarray] = None
    normals: Optional[np.ndarray] = None
    uvs: Optional[np.ndarray] = None


@dataclass
class SpatialMaterial:
    """Material properties for spatial objects."""
    color: Color = field(default_factory=lambda: Color.from_name("white"))
    opacity: float = 1.0
    metallic: float = 0.0
    roughness: float = 0.5
    emissive: Color = field(default_factory=lambda: Color(0, 0, 0, 0))


class SpatialObject:
    """3D object in spatial coordinate system."""

    def __init__(self, object_id: str, geometry: Optional[SpatialGeometry] = None):
        self.object_id = object_id
        self.transform = SpatialTransform()
        self.geometry = geometry
        self.material = SpatialMaterial()
        self.visible = True
        self.interactive = False

    def set_position(self, position: np.ndarray):
        """Set object position."""
        self.transform.position = position

    def set_rotation(self, rotation: np.ndarray):
        """Set object rotation (quaternion)."""
        self.transform.rotation = rotation

    def set_scale(self, scale: Union[float, np.ndarray]):
        """Set object scale."""
        if isinstance(scale, float):
            self.transform.scale = np.array([scale, scale, scale])
        else:
            self.transform.scale = scale

    @classmethod
    def create_cube(cls, object_id: str, size: float = 1.0) -> 'SpatialObject':
        """Create a cube spatial object."""
        s = size / 2
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],  # Back face
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]       # Front face
        ])

        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # Back
            [4, 7, 6], [4, 6, 5],  # Front
            [0, 4, 5], [0, 5, 1],  # Bottom
            [2, 6, 7], [2, 7, 3],  # Top
            [0, 3, 7], [0, 7, 4],  # Left
            [1, 5, 6], [1, 6, 2]   # Right
        ])

        geometry = SpatialGeometry(vertices, faces)
        return cls(object_id, geometry)

    @classmethod
    def create_sphere(cls, object_id: str, radius: float = 1.0, subdivisions: int = 16) -> 'SpatialObject':
        """Create a sphere spatial object."""
        vertices = []
        faces = []

        # Generate vertices
        for i in range(subdivisions + 1):
            phi = np.pi * i / subdivisions  # 0 to pi
            for j in range(subdivisions * 2 + 1):
                theta = 2 * np.pi * j / (subdivisions * 2)  # 0 to 2pi

                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.cos(phi)
                z = radius * np.sin(phi) * np.sin(theta)

                vertices.append([x, y, z])

        # Generate faces
        for i in range(subdivisions):
            for j in range(subdivisions * 2):
                # Current row
                curr = i * (subdivisions * 2 + 1) + j
                next_j = i * (subdivisions * 2 + 1) + (j + 1) % (subdivisions * 2 + 1)

                # Next row
                next_i = (i + 1) * (subdivisions * 2 + 1) + j
                next_i_next_j = (i + 1) * (subdivisions * 2 + 1) + (j + 1) % (subdivisions * 2 + 1)

                # Two triangles per quad
                if i < subdivisions:
                    faces.append([curr, next_j, next_i_next_j])
                    faces.append([curr, next_i_next_j, next_i])

        geometry = SpatialGeometry(np.array(vertices), np.array(faces))
        return cls(object_id, geometry)