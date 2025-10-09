"""
3D Object Manipulation System
Provides transformation tools, gizmos, and object manipulation interfaces.
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



import numpy as np
import math
import time
from typing import List, Tuple, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class TransformMode(Enum):
    """Transform manipulation modes."""

    TRANSLATE = "translate"
    ROTATE = "rotate"
    SCALE = "scale"
    COMBINED = "combined"


class AxisConstraint(Enum):
    """Axis constraint for transformations."""

    NONE = "none"
    X_AXIS = "x"
    Y_AXIS = "y"
    Z_AXIS = "z"
    XY_PLANE = "xy"
    XZ_PLANE = "xz"
    YZ_PLANE = "yz"
    SCREEN_SPACE = "screen"


@dataclass
class Transform3D:
    """3D transformation matrix with position, rotation, and scale."""

    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    rotation: np.ndarray = field(
        default_factory=lambda: np.array([0.0, 0.0, 0.0])
    )  # Euler angles
    scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))

    def __post_init__(self):
        """Ensure arrays are numpy arrays."""
        self.position = np.array(self.position, dtype=float)
        self.rotation = np.array(self.rotation, dtype=float)
        self.scale = np.array(self.scale, dtype=float)

    @property
    def matrix(self) -> np.ndarray:
        """Get the 4x4 transformation matrix."""
        # Create translation matrix
        translation = np.eye(4)
        translation[:3, 3] = self.position

        # Create rotation matrices
        rx = self._rotation_matrix_x(self.rotation[0])
        ry = self._rotation_matrix_y(self.rotation[1])
        rz = self._rotation_matrix_z(self.rotation[2])
        rotation = rz @ ry @ rx

        # Create scale matrix
        scale_matrix = np.eye(4)
        scale_matrix[0, 0] = self.scale[0]
        scale_matrix[1, 1] = self.scale[1]
        scale_matrix[2, 2] = self.scale[2]

        return translation @ rotation @ scale_matrix

    @property
    def inverse_matrix(self) -> np.ndarray:
        """Get the inverse transformation matrix."""
        return np.linalg.inv(self.matrix)

    def translate(self, offset: np.ndarray):
        """Apply translation offset."""
        self.position += offset

    def rotate(self, angles: np.ndarray):
        """Apply rotation (Euler angles in radians)."""
        self.rotation += angles

    def scale_by(self, factors: np.ndarray):
        """Apply scaling factors."""
        self.scale *= factors

    def set_position(self, position: np.ndarray):
        """Set absolute position."""
        self.position = np.array(position, dtype=float)

    def set_rotation(self, rotation: np.ndarray):
        """Set absolute rotation (Euler angles in radians)."""
        self.rotation = np.array(rotation, dtype=float)

    def set_scale(self, scale: np.ndarray):
        """Set absolute scale."""
        self.scale = np.array(scale, dtype=float)

    def transform_point(self, point: np.ndarray) -> np.ndarray:
        """Transform a 3D point."""
        homogeneous_point = np.append(point, 1.0)
        transformed = self.matrix @ homogeneous_point
        return transformed[:3]

    def transform_vector(self, vector: np.ndarray) -> np.ndarray:
        """Transform a 3D vector (no translation)."""
        rotation_scale = self.matrix[:3, :3]
        return rotation_scale @ vector

    def transform_normal(self, normal: np.ndarray) -> np.ndarray:
        """Transform a normal vector (inverse transpose)."""
        inv_transpose = np.linalg.inv(self.matrix[:3, :3]).T
        transformed = inv_transpose @ normal
        return transformed / np.linalg.norm(transformed)

    @classmethod
    def from_matrix(cls, matrix: np.ndarray) -> "Transform3D":
        """Create transform from 4x4 matrix."""
        # Extract translation
        position = matrix[:3, 3]

        # Extract scale
        scale = np.array(
            [
                np.linalg.norm(matrix[:3, 0]),
                np.linalg.norm(matrix[:3, 1]),
                np.linalg.norm(matrix[:3, 2]),
            ]
        )

        # Extract rotation (remove scale first)
        rotation_matrix = matrix[:3, :3] / scale
        rotation = cls._matrix_to_euler(rotation_matrix)

        return cls(position, rotation, scale)

    @staticmethod
    def _rotation_matrix_x(angle: float) -> np.ndarray:
        """Create rotation matrix around X axis."""
        c, s = math.cos(angle), math.sin(angle)
        return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])

    @staticmethod
    def _rotation_matrix_y(angle: float) -> np.ndarray:
        """Create rotation matrix around Y axis."""
        c, s = math.cos(angle), math.sin(angle)
        return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])

    @staticmethod
    def _rotation_matrix_z(angle: float) -> np.ndarray:
        """Create rotation matrix around Z axis."""
        c, s = math.cos(angle), math.sin(angle)
        return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    @staticmethod
    def _matrix_to_euler(rotation_matrix: np.ndarray) -> np.ndarray:
        """Convert rotation matrix to Euler angles (XYZ order)."""
        r11, r12, r13 = rotation_matrix[0, :]
        r21, r22, r23 = rotation_matrix[1, :]
        r31, r32, r33 = rotation_matrix[2, :]

        # Extract Euler angles
        sy = math.sqrt(r11 * r11 + r21 * r21)

        singular = sy < 1e-6

        if not singular:
            x = math.atan2(r32, r33)
            y = math.atan2(-r31, sy)
            z = math.atan2(r21, r11)
        else:
            x = math.atan2(-r23, r22)
            y = math.atan2(-r31, sy)
            z = 0

        return np.array([x, y, z])

    def copy(self) -> "Transform3D":
        """Create a copy of this transform."""
        return Transform3D(
            self.position.copy(), self.rotation.copy(), self.scale.copy()
        )

    def lerp(self, other: "Transform3D", t: float) -> "Transform3D":
        """Linear interpolation between transforms."""
        return Transform3D(
            self.position + (other.position - self.position) * t,
            self.rotation + (other.rotation - self.rotation) * t,
            self.scale + (other.scale - self.scale) * t,
        )


class ManipulatorGizmo:
    """3D manipulation gizmo for interactive object transformation."""

    def __init__(self, transform: Transform3D):
        self.transform = transform
        self.mode = TransformMode.TRANSLATE
        self.constraint = AxisConstraint.NONE

        # Gizmo properties
        self.size = 1.0
        self.axis_length = 2.0
        self.handle_size = 0.2
        self.line_width = 3.0

        # Colors
        self.x_color = np.array([1.0, 0.0, 0.0])  # Red
        self.y_color = np.array([0.0, 1.0, 0.0])  # Green
        self.z_color = np.array([0.0, 0.0, 1.0])  # Blue
        self.center_color = np.array([1.0, 1.0, 0.0])  # Yellow
        self.highlight_color = np.array([1.0, 1.0, 1.0])  # White

        # Interaction state
        self.is_active = False
        self.active_axis = AxisConstraint.NONE
        self.interaction_start_pos = None
        self.initial_transform = None

        # Event callbacks
        self.on_transform_start: Optional[Callable] = None
        self.on_transform_update: Optional[Callable] = None
        self.on_transform_end: Optional[Callable] = None

    def set_mode(self, mode: TransformMode):
        """Set the manipulation mode."""
        self.mode = mode

    def set_constraint(self, constraint: AxisConstraint):
        """Set the axis constraint."""
        self.constraint = constraint

    def start_interaction(
        self,
        screen_pos: Tuple[float, float],
        ray_origin: np.ndarray,
        ray_direction: np.ndarray,
    ) -> bool:
        """Start manipulation interaction. Returns True if gizmo was hit."""
        hit_axis = self._hit_test(ray_origin, ray_direction)

        if hit_axis != AxisConstraint.NONE:
            self.is_active = True
            self.active_axis = hit_axis
            self.interaction_start_pos = screen_pos
            self.initial_transform = self.transform.copy()

            if self.on_transform_start:
                self.on_transform_start(self.transform)

            return True

        return False

    def update_interaction(
        self,
        screen_pos: Tuple[float, float],
        ray_origin: np.ndarray,
        ray_direction: np.ndarray,
    ):
        """Update manipulation based on mouse movement."""
        if not self.is_active or not self.interaction_start_pos:
            return

        # Calculate movement delta
        dx = screen_pos[0] - self.interaction_start_pos[0]
        dy = screen_pos[1] - self.interaction_start_pos[1]

        # Apply transformation based on mode and constraint
        if self.mode == TransformMode.TRANSLATE:
            self._apply_translation(dx, dy, ray_origin, ray_direction)
        elif self.mode == TransformMode.ROTATE:
            self._apply_rotation(dx, dy)
        elif self.mode == TransformMode.SCALE:
            self._apply_scaling(dx, dy)

        if self.on_transform_update:
            self.on_transform_update(self.transform)

    def end_interaction(self):
        """End manipulation interaction."""
        if self.is_active:
            self.is_active = False
            self.active_axis = AxisConstraint.NONE
            self.interaction_start_pos = None

            if self.on_transform_end:
                self.on_transform_end(self.transform)

    def get_gizmo_geometry(self) -> Dict[str, Any]:
        """Get geometry data for rendering the gizmo."""
        geometry = {"axes": [], "handles": [], "planes": []}

        center = self.transform.position
        scale = self.size

        if self.mode == TransformMode.TRANSLATE:
            # Translation arrows
            geometry["axes"] = [
                {
                    "start": center,
                    "end": center + np.array([self.axis_length * scale, 0, 0]),
                    "color": self.x_color,
                    "highlight": self.active_axis == AxisConstraint.X_AXIS,
                },
                {
                    "start": center,
                    "end": center + np.array([0, self.axis_length * scale, 0]),
                    "color": self.y_color,
                    "highlight": self.active_axis == AxisConstraint.Y_AXIS,
                },
                {
                    "start": center,
                    "end": center + np.array([0, 0, self.axis_length * scale]),
                    "color": self.z_color,
                    "highlight": self.active_axis == AxisConstraint.Z_AXIS,
                },
            ]

            # Plane handles
            plane_size = self.handle_size * scale
            geometry["planes"] = [
                {  # XY plane
                    "center": center + np.array([plane_size, plane_size, 0]),
                    "normal": np.array([0, 0, 1]),
                    "size": plane_size,
                    "color": self.z_color * 0.5,
                    "highlight": self.active_axis == AxisConstraint.XY_PLANE,
                },
                {  # XZ plane
                    "center": center + np.array([plane_size, 0, plane_size]),
                    "normal": np.array([0, 1, 0]),
                    "size": plane_size,
                    "color": self.y_color * 0.5,
                    "highlight": self.active_axis == AxisConstraint.XZ_PLANE,
                },
                {  # YZ plane
                    "center": center + np.array([0, plane_size, plane_size]),
                    "normal": np.array([1, 0, 0]),
                    "size": plane_size,
                    "color": self.x_color * 0.5,
                    "highlight": self.active_axis == AxisConstraint.YZ_PLANE,
                },
            ]

        elif self.mode == TransformMode.ROTATE:
            # Rotation rings
            geometry["axes"] = [
                {
                    "type": "circle",
                    "center": center,
                    "radius": self.axis_length * scale * 0.8,
                    "normal": np.array([1, 0, 0]),
                    "color": self.x_color,
                    "highlight": self.active_axis == AxisConstraint.X_AXIS,
                },
                {
                    "type": "circle",
                    "center": center,
                    "radius": self.axis_length * scale * 0.8,
                    "normal": np.array([0, 1, 0]),
                    "color": self.y_color,
                    "highlight": self.active_axis == AxisConstraint.Y_AXIS,
                },
                {
                    "type": "circle",
                    "center": center,
                    "radius": self.axis_length * scale * 0.8,
                    "normal": np.array([0, 0, 1]),
                    "color": self.z_color,
                    "highlight": self.active_axis == AxisConstraint.Z_AXIS,
                },
            ]

        elif self.mode == TransformMode.SCALE:
            # Scale handles
            handle_offset = self.axis_length * scale * 0.8
            geometry["handles"] = [
                {
                    "position": center + np.array([handle_offset, 0, 0]),
                    "size": self.handle_size * scale,
                    "color": self.x_color,
                    "highlight": self.active_axis == AxisConstraint.X_AXIS,
                },
                {
                    "position": center + np.array([0, handle_offset, 0]),
                    "size": self.handle_size * scale,
                    "color": self.y_color,
                    "highlight": self.active_axis == AxisConstraint.Y_AXIS,
                },
                {
                    "position": center + np.array([0, 0, handle_offset]),
                    "size": self.handle_size * scale,
                    "color": self.z_color,
                    "highlight": self.active_axis == AxisConstraint.Z_AXIS,
                },
                {
                    "position": center,
                    "size": self.handle_size * scale * 1.5,
                    "color": self.center_color,
                    "highlight": self.active_axis == AxisConstraint.NONE,
                },
            ]

        return geometry

    def _hit_test(
        self, ray_origin: np.ndarray, ray_direction: np.ndarray
    ) -> AxisConstraint:
        """Test which part of the gizmo was hit by the ray."""
        center = self.transform.position
        min_distance = float("inf")
        hit_axis = AxisConstraint.NONE

        # Test axis handles
        if self.mode == TransformMode.TRANSLATE:
            axes = [
                (AxisConstraint.X_AXIS, np.array([1, 0, 0])),
                (AxisConstraint.Y_AXIS, np.array([0, 1, 0])),
                (AxisConstraint.Z_AXIS, np.array([0, 0, 1])),
            ]

            for axis_type, axis_dir in axes:
                axis_end = center + axis_dir * self.axis_length * self.size
                distance = self._ray_to_line_distance(
                    ray_origin, ray_direction, center, axis_end
                )

                if distance < self.handle_size * self.size and distance < min_distance:
                    min_distance = distance
                    hit_axis = axis_type

            # Test plane handles
            plane_tests = [
                (AxisConstraint.XY_PLANE, np.array([0, 0, 1])),
                (AxisConstraint.XZ_PLANE, np.array([0, 1, 0])),
                (AxisConstraint.YZ_PLANE, np.array([1, 0, 0])),
            ]

            for plane_type, plane_normal in plane_tests:
                plane_center = center + (axis_dir * self.handle_size * self.size)
                distance = self._ray_to_plane_distance(
                    ray_origin, ray_direction, plane_center, plane_normal
                )

                if distance < self.handle_size * self.size and distance < min_distance:
                    min_distance = distance
                    hit_axis = plane_type

        return hit_axis

    def _ray_to_line_distance(
        self,
        ray_origin: np.ndarray,
        ray_direction: np.ndarray,
        line_start: np.ndarray,
        line_end: np.ndarray,
    ) -> float:
        """Calculate distance from ray to line segment."""
        line_dir = line_end - line_start
        line_length = np.linalg.norm(line_dir)

        if line_length < 1e-6:
            return np.linalg.norm(ray_origin - line_start)

        line_dir = line_dir / line_length

        # Vector from line start to ray origin
        w = ray_origin - line_start

        # Parameters for closest approach
        a = np.dot(ray_direction, ray_direction)
        b = np.dot(ray_direction, line_dir)
        c = np.dot(line_dir, line_dir)
        d = np.dot(ray_direction, w)
        e = np.dot(line_dir, w)

        denom = a * c - b * b

        if abs(denom) < 1e-6:  # Lines are parallel
            return np.linalg.norm(w - np.dot(w, line_dir) * line_dir)

        t_ray = (b * e - c * d) / denom
        t_line = (a * e - b * d) / denom

        # Clamp line parameter to segment
        t_line = max(0, min(line_length, t_line))

        # Calculate closest points
        ray_point = ray_origin + t_ray * ray_direction
        line_point = line_start + (t_line / line_length) * (line_end - line_start)

        return np.linalg.norm(ray_point - line_point)

    def _ray_to_plane_distance(
        self,
        ray_origin: np.ndarray,
        ray_direction: np.ndarray,
        plane_point: np.ndarray,
        plane_normal: np.ndarray,
    ) -> float:
        """Calculate distance from ray intersection to plane."""
        denom = np.dot(plane_normal, ray_direction)

        if abs(denom) < 1e-6:  # Ray parallel to plane
            return float("inf")

        t = np.dot(plane_point - ray_origin, plane_normal) / denom

        if t < 0:  # Intersection behind ray
            return float("inf")

        intersection = ray_origin + t * ray_direction
        return np.linalg.norm(intersection - plane_point)

    def _apply_translation(
        self, dx: float, dy: float, ray_origin: np.ndarray, ray_direction: np.ndarray
    ):
        """Apply translation transformation."""
        sensitivity = 0.01

        if self.active_axis == AxisConstraint.X_AXIS:
            self.transform.translate(np.array([dx * sensitivity, 0, 0]))
        elif self.active_axis == AxisConstraint.Y_AXIS:
            self.transform.translate(np.array([0, -dy * sensitivity, 0]))
        elif self.active_axis == AxisConstraint.Z_AXIS:
            self.transform.translate(np.array([0, 0, dx * sensitivity]))
        elif self.active_axis == AxisConstraint.XY_PLANE:
            self.transform.translate(np.array([dx * sensitivity, -dy * sensitivity, 0]))
        elif self.active_axis == AxisConstraint.XZ_PLANE:
            self.transform.translate(np.array([dx * sensitivity, 0, dy * sensitivity]))
        elif self.active_axis == AxisConstraint.YZ_PLANE:
            self.transform.translate(np.array([0, -dy * sensitivity, dx * sensitivity]))

    def _apply_rotation(self, dx: float, dy: float):
        """Apply rotation transformation."""
        sensitivity = 0.01

        if self.active_axis == AxisConstraint.X_AXIS:
            self.transform.rotate(np.array([dy * sensitivity, 0, 0]))
        elif self.active_axis == AxisConstraint.Y_AXIS:
            self.transform.rotate(np.array([0, dx * sensitivity, 0]))
        elif self.active_axis == AxisConstraint.Z_AXIS:
            self.transform.rotate(np.array([0, 0, dx * sensitivity]))

    def _apply_scaling(self, dx: float, dy: float):
        """Apply scaling transformation."""
        sensitivity = 0.01
        scale_factor = 1.0 + (dx + dy) * sensitivity

        if self.active_axis == AxisConstraint.X_AXIS:
            self.transform.scale_by(np.array([scale_factor, 1, 1]))
        elif self.active_axis == AxisConstraint.Y_AXIS:
            self.transform.scale_by(np.array([1, scale_factor, 1]))
        elif self.active_axis == AxisConstraint.Z_AXIS:
            self.transform.scale_by(np.array([1, 1, scale_factor]))
        elif self.active_axis == AxisConstraint.NONE:  # Uniform scaling
            self.transform.scale_by(
                np.array([scale_factor, scale_factor, scale_factor])
            )


class ObjectManipulator:
    """High-level object manipulation coordinator."""

    def __init__(self):
        self.manipulated_objects: Dict[str, Transform3D] = {}
        self.active_gizmos: Dict[str, ManipulatorGizmo] = {}
        self.manipulation_history: List[Dict[str, Any]] = []
        self.max_history = 50

        # Settings
        self.snap_enabled = False
        self.snap_grid_size = 1.0
        self.snap_angle = math.radians(15)  # 15 degrees

    def add_object(self, object_id: str, transform: Transform3D):
        """Add object for manipulation."""
        self.manipulated_objects[object_id] = transform
        self.active_gizmos[object_id] = ManipulatorGizmo(transform)

    def remove_object(self, object_id: str):
        """Remove object from manipulation."""
        self.manipulated_objects.pop(object_id, None)
        self.active_gizmos.pop(object_id, None)

    def get_gizmo(self, object_id: str) -> Optional[ManipulatorGizmo]:
        """Get gizmo for object."""
        return self.active_gizmos.get(object_id)

    def set_manipulation_mode(self, mode: TransformMode):
        """Set manipulation mode for all gizmos."""
        for gizmo in self.active_gizmos.values():
            gizmo.set_mode(mode)

    def enable_snap(self, grid_size: float = 1.0, angle: float = None):
        """Enable snap-to-grid."""
        self.snap_enabled = True
        self.snap_grid_size = grid_size
        if angle is not None:
            self.snap_angle = angle

    def disable_snap(self):
        """Disable snap-to-grid."""
        self.snap_enabled = False

    def start_manipulation(
        self,
        object_id: str,
        screen_pos: Tuple[float, float],
        ray_origin: np.ndarray,
        ray_direction: np.ndarray,
    ) -> bool:
        """Start manipulation for object."""
        gizmo = self.active_gizmos.get(object_id)
        if gizmo:
            success = gizmo.start_interaction(screen_pos, ray_origin, ray_direction)
            if success:
                self._save_state(object_id)
            return success
        return False

    def update_manipulation(
        self,
        object_id: str,
        screen_pos: Tuple[float, float],
        ray_origin: np.ndarray,
        ray_direction: np.ndarray,
    ):
        """Update manipulation for object."""
        gizmo = self.active_gizmos.get(object_id)
        if gizmo and gizmo.is_active:
            gizmo.update_interaction(screen_pos, ray_origin, ray_direction)

            if self.snap_enabled:
                self._apply_snapping(object_id)

    def end_manipulation(self, object_id: str):
        """End manipulation for object."""
        gizmo = self.active_gizmos.get(object_id)
        if gizmo:
            gizmo.end_interaction()

    def undo_last_operation(self) -> bool:
        """Undo the last manipulation operation."""
        if self.manipulation_history:
            last_state = self.manipulation_history.pop()
            object_id = last_state["object_id"]

            if object_id in self.manipulated_objects:
                self.manipulated_objects[object_id] = last_state["transform"].copy()
                return True

        return False

    def duplicate_object(
        self, object_id: str, offset: np.ndarray = None
    ) -> Optional[str]:
        """Duplicate an object with optional offset."""
        if object_id in self.manipulated_objects:
            new_id = f"{object_id}_copy_{len(self.manipulated_objects)}"
            original_transform = self.manipulated_objects[object_id]

            # Create copy with offset
            new_transform = original_transform.copy()
            if offset is not None:
                new_transform.translate(offset)
            else:
                new_transform.translate(np.array([1.0, 0.0, 0.0]))  # Default offset

            self.add_object(new_id, new_transform)
            return new_id

        return None

    def align_objects(self, object_ids: List[str], alignment_axis: AxisConstraint):
        """Align multiple objects along specified axis."""
        if len(object_ids) < 2:
            return

        # Get reference position (first object)
        ref_transform = self.manipulated_objects.get(object_ids[0])
        if not ref_transform:
            return

        ref_pos = ref_transform.position

        # Align other objects
        for obj_id in object_ids[1:]:
            transform = self.manipulated_objects.get(obj_id)
            if transform:
                self._save_state(obj_id)

                if alignment_axis == AxisConstraint.X_AXIS:
                    transform.position[0] = ref_pos[0]
                elif alignment_axis == AxisConstraint.Y_AXIS:
                    transform.position[1] = ref_pos[1]
                elif alignment_axis == AxisConstraint.Z_AXIS:
                    transform.position[2] = ref_pos[2]

    def distribute_objects(
        self, object_ids: List[str], distribution_axis: AxisConstraint
    ):
        """Distribute objects evenly along axis."""
        if len(object_ids) < 3:
            return

        # Sort objects by position along axis
        transforms = [
            (obj_id, self.manipulated_objects[obj_id])
            for obj_id in object_ids
            if obj_id in self.manipulated_objects
        ]

        axis_index = 0
        if distribution_axis == AxisConstraint.Y_AXIS:
            axis_index = 1
        elif distribution_axis == AxisConstraint.Z_AXIS:
            axis_index = 2

        transforms.sort(key=lambda x: x[1].position[axis_index])

        # Calculate distribution
        start_pos = transforms[0][1].position[axis_index]
        end_pos = transforms[-1][1].position[axis_index]
        step = (end_pos - start_pos) / (len(transforms) - 1)

        # Apply distribution
        for i, (obj_id, transform) in enumerate(transforms[1:-1], 1):
            self._save_state(obj_id)
            new_pos = start_pos + i * step
            transform.position[axis_index] = new_pos

    def _apply_snapping(self, object_id: str):
        """Apply snapping to object position/rotation."""
        transform = self.manipulated_objects.get(object_id)
        if not transform:
            return

        # Snap position to grid
        snapped_pos = (
            np.round(transform.position / self.snap_grid_size) * self.snap_grid_size
        )
        transform.set_position(snapped_pos)

        # Snap rotation to angle increments
        snapped_rot = np.round(transform.rotation / self.snap_angle) * self.snap_angle
        transform.set_rotation(snapped_rot)

    def _save_state(self, object_id: str):
        """Save current state for undo."""
        transform = self.manipulated_objects.get(object_id)
        if transform:
            state = {
                "object_id": object_id,
                "transform": transform.copy(),
                "timestamp": time.time(),
            }

            self.manipulation_history.append(state)

            # Limit history size
            if len(self.manipulation_history) > self.max_history:
                self.manipulation_history = self.manipulation_history[
                    -self.max_history // 2 :
                ]


# Additional utilities for object manipulation
def create_transform_from_points(
    origin: np.ndarray, x_axis: np.ndarray, y_axis: np.ndarray
) -> Transform3D:
    """Create transform from origin and axis vectors."""
    # Normalize axes
    x_axis = x_axis / np.linalg.norm(x_axis)
    y_axis = y_axis / np.linalg.norm(y_axis)
    z_axis = np.cross(x_axis, y_axis)
    z_axis = z_axis / np.linalg.norm(z_axis)

    # Create rotation matrix
    rotation_matrix = np.column_stack([x_axis, y_axis, z_axis])

    # Convert to transform
    transform = Transform3D()
    transform.set_position(origin)

    # Convert rotation matrix to Euler angles
    transform.rotation = Transform3D._matrix_to_euler(rotation_matrix)

    return transform


def interpolate_transforms(
    transform1: Transform3D, transform2: Transform3D, t: float
) -> Transform3D:
    """Interpolate between two transforms."""
    return transform1.lerp(transform2, t)
