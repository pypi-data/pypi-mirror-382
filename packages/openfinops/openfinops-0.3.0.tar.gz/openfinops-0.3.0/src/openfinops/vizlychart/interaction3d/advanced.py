"""
Advanced 3D Interaction System
==============================

Enhanced 3D interaction capabilities including gesture recognition,
physics simulation, and advanced camera controls.
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



from __future__ import annotations

import numpy as np
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Dict, Callable
import warnings

logger = logging.getLogger(__name__)


class InteractionMode(Enum):
    """3D interaction modes."""
    ORBIT = "orbit"
    FLY = "fly"
    FIRST_PERSON = "first_person"
    EXAMINE = "examine"
    WALK = "walk"


class GestureType(Enum):
    """Recognized gesture types."""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    PINCH = "pinch"
    PAN = "pan"
    ROTATE = "rotate"
    SWIPE = "swipe"
    LONG_PRESS = "long_press"


@dataclass
class Transform3D:
    """3D transformation matrix and operations."""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    rotation: np.ndarray = field(default_factory=lambda: np.eye(3))
    scale: np.ndarray = field(default_factory=lambda: np.ones(3))

    def to_matrix(self) -> np.ndarray:
        """Convert to 4x4 transformation matrix."""
        matrix = np.eye(4)

        # Apply scale
        scale_matrix = np.diag([*self.scale, 1.0])

        # Apply rotation
        rotation_matrix = np.eye(4)
        rotation_matrix[:3, :3] = self.rotation

        # Apply translation
        translation_matrix = np.eye(4)
        translation_matrix[:3, 3] = self.position

        # Combine transformations
        matrix = translation_matrix @ rotation_matrix @ scale_matrix
        return matrix

    def apply_to_point(self, point: np.ndarray) -> np.ndarray:
        """Apply transformation to a 3D point."""
        homogeneous_point = np.append(point, 1.0)
        transformed = self.to_matrix() @ homogeneous_point
        return transformed[:3]

    def inverse(self) -> 'Transform3D':
        """Get inverse transformation."""
        inv_scale = 1.0 / self.scale
        inv_rotation = self.rotation.T
        inv_position = -inv_rotation @ (self.position / self.scale)

        return Transform3D(
            position=inv_position,
            rotation=inv_rotation,
            scale=inv_scale
        )


class AdvancedCamera:
    """Advanced camera with multiple interaction modes."""

    def __init__(self, position: np.ndarray = None, target: np.ndarray = None):
        self.position = position or np.array([0.0, 0.0, 5.0])
        self.target = target or np.array([0.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])

        # Camera parameters
        self.fov = 60.0  # Field of view in degrees
        self.near = 0.1
        self.far = 1000.0

        # Interaction state
        self.mode = InteractionMode.ORBIT
        self.sensitivity = 1.0
        self.zoom_speed = 1.0
        self.pan_speed = 1.0

        # Orbital parameters
        self.orbit_distance = np.linalg.norm(self.position - self.target)
        self.orbit_theta = 0.0  # Horizontal angle
        self.orbit_phi = 0.0    # Vertical angle

        # First-person parameters
        self.yaw = 0.0
        self.pitch = 0.0

        # Constraints
        self.min_distance = 0.5
        self.max_distance = 100.0
        self.max_pitch = 89.0

    def set_mode(self, mode: InteractionMode):
        """Set camera interaction mode."""
        self.mode = mode
        logger.info(f"Camera mode set to: {mode.value}")

    def get_view_matrix(self) -> np.ndarray:
        """Get view matrix for rendering."""
        # Look-at matrix
        forward = self.target - self.position
        forward = forward / np.linalg.norm(forward)

        right = np.cross(forward, self.up)
        right = right / np.linalg.norm(right)

        up = np.cross(right, forward)

        view_matrix = np.eye(4)
        view_matrix[:3, 0] = right
        view_matrix[:3, 1] = up
        view_matrix[:3, 2] = -forward
        view_matrix[:3, 3] = -self.position

        return view_matrix

    def get_projection_matrix(self, aspect_ratio: float) -> np.ndarray:
        """Get projection matrix."""
        fov_rad = np.radians(self.fov)
        f = 1.0 / np.tan(fov_rad / 2.0)

        projection = np.zeros((4, 4))
        projection[0, 0] = f / aspect_ratio
        projection[1, 1] = f
        projection[2, 2] = (self.far + self.near) / (self.near - self.far)
        projection[2, 3] = (2.0 * self.far * self.near) / (self.near - self.far)
        projection[3, 2] = -1.0

        return projection

    def orbit(self, delta_theta: float, delta_phi: float):
        """Orbit around target."""
        if self.mode != InteractionMode.ORBIT:
            return

        self.orbit_theta += delta_theta * self.sensitivity
        self.orbit_phi += delta_phi * self.sensitivity

        # Constrain vertical angle
        self.orbit_phi = np.clip(self.orbit_phi, -self.max_pitch, self.max_pitch)

        # Convert spherical to cartesian
        theta_rad = np.radians(self.orbit_theta)
        phi_rad = np.radians(self.orbit_phi)

        x = self.orbit_distance * np.cos(phi_rad) * np.sin(theta_rad)
        y = self.orbit_distance * np.sin(phi_rad)
        z = self.orbit_distance * np.cos(phi_rad) * np.cos(theta_rad)

        self.position = self.target + np.array([x, y, z])

    def zoom(self, delta: float):
        """Zoom in/out."""
        if self.mode == InteractionMode.ORBIT:
            self.orbit_distance *= (1.0 + delta * self.zoom_speed)
            self.orbit_distance = np.clip(self.orbit_distance, self.min_distance, self.max_distance)

            # Update position
            direction = self.position - self.target
            direction = direction / np.linalg.norm(direction)
            self.position = self.target + direction * self.orbit_distance

        elif self.mode == InteractionMode.FLY:
            # Move along view direction
            forward = self.target - self.position
            forward = forward / np.linalg.norm(forward)
            self.position += forward * delta * self.zoom_speed

    def pan(self, delta_x: float, delta_y: float):
        """Pan camera."""
        # Calculate right and up vectors
        forward = self.target - self.position
        forward = forward / np.linalg.norm(forward)

        right = np.cross(forward, self.up)
        right = right / np.linalg.norm(right)

        up = np.cross(right, forward)

        # Move camera and target together
        offset = (right * delta_x + up * delta_y) * self.pan_speed
        self.position += offset
        self.target += offset

    def first_person_look(self, delta_yaw: float, delta_pitch: float):
        """First-person camera look."""
        if self.mode != InteractionMode.FIRST_PERSON:
            return

        self.yaw += delta_yaw * self.sensitivity
        self.pitch += delta_pitch * self.sensitivity

        # Constrain pitch
        self.pitch = np.clip(self.pitch, -self.max_pitch, self.max_pitch)

        # Update target based on yaw/pitch
        yaw_rad = np.radians(self.yaw)
        pitch_rad = np.radians(self.pitch)

        direction = np.array([
            np.cos(pitch_rad) * np.sin(yaw_rad),
            np.sin(pitch_rad),
            np.cos(pitch_rad) * np.cos(yaw_rad)
        ])

        self.target = self.position + direction

    def move_first_person(self, forward: float, right: float, up: float):
        """Move in first-person mode."""
        if self.mode != InteractionMode.FIRST_PERSON:
            return

        # Calculate movement vectors
        view_direction = self.target - self.position
        view_direction = view_direction / np.linalg.norm(view_direction)

        right_vector = np.cross(view_direction, self.up)
        right_vector = right_vector / np.linalg.norm(right_vector)

        up_vector = self.up

        # Apply movement
        movement = (view_direction * forward +
                   right_vector * right +
                   up_vector * up) * self.pan_speed

        self.position += movement
        self.target += movement


class GestureRecognizer:
    """Advanced gesture recognition for 3D interaction."""

    def __init__(self):
        self.gesture_history = []
        self.touch_points = {}
        self.gesture_callbacks = {}

        # Gesture thresholds
        self.tap_time_threshold = 0.3  # seconds
        self.double_tap_time_threshold = 0.5
        self.long_press_time_threshold = 1.0
        self.pinch_distance_threshold = 10.0  # pixels
        self.swipe_distance_threshold = 50.0

    def register_gesture_callback(self, gesture: GestureType, callback: Callable):
        """Register callback for gesture events."""
        self.gesture_callbacks[gesture] = callback

    def add_touch_point(self, touch_id: int, position: Tuple[float, float], timestamp: float):
        """Add touch point."""
        self.touch_points[touch_id] = {
            'position': position,
            'start_position': position,
            'timestamp': timestamp,
            'start_timestamp': timestamp
        }

    def update_touch_point(self, touch_id: int, position: Tuple[float, float], timestamp: float):
        """Update touch point position."""
        if touch_id in self.touch_points:
            self.touch_points[touch_id]['position'] = position
            self.touch_points[touch_id]['timestamp'] = timestamp

    def remove_touch_point(self, touch_id: int, timestamp: float):
        """Remove touch point and analyze gesture."""
        if touch_id not in self.touch_points:
            return

        touch = self.touch_points[touch_id]
        duration = timestamp - touch['start_timestamp']

        start_pos = np.array(touch['start_position'])
        end_pos = np.array(touch['position'])
        distance = np.linalg.norm(end_pos - start_pos)

        # Analyze single-touch gestures
        if len(self.touch_points) == 1:
            if duration < self.tap_time_threshold and distance < 10:
                self._trigger_gesture(GestureType.TAP, {'position': end_pos})
            elif duration >= self.long_press_time_threshold:
                self._trigger_gesture(GestureType.LONG_PRESS, {'position': end_pos, 'duration': duration})
            elif distance >= self.swipe_distance_threshold:
                direction = end_pos - start_pos
                self._trigger_gesture(GestureType.SWIPE, {
                    'start': start_pos,
                    'end': end_pos,
                    'direction': direction,
                    'distance': distance
                })

        del self.touch_points[touch_id]

    def analyze_multi_touch(self):
        """Analyze multi-touch gestures."""
        if len(self.touch_points) == 2:
            touches = list(self.touch_points.values())

            # Current distance between touches
            pos1 = np.array(touches[0]['position'])
            pos2 = np.array(touches[1]['position'])
            current_distance = np.linalg.norm(pos2 - pos1)

            # Initial distance
            start_pos1 = np.array(touches[0]['start_position'])
            start_pos2 = np.array(touches[1]['start_position'])
            initial_distance = np.linalg.norm(start_pos2 - start_pos1)

            # Detect pinch
            distance_change = abs(current_distance - initial_distance)
            if distance_change > self.pinch_distance_threshold:
                scale_factor = current_distance / initial_distance if initial_distance > 0 else 1.0
                self._trigger_gesture(GestureType.PINCH, {
                    'scale_factor': scale_factor,
                    'center': (pos1 + pos2) / 2
                })

            # Detect rotation
            initial_vector = start_pos2 - start_pos1
            current_vector = pos2 - pos1

            if np.linalg.norm(initial_vector) > 0 and np.linalg.norm(current_vector) > 0:
                dot_product = np.dot(initial_vector, current_vector)
                norms = np.linalg.norm(initial_vector) * np.linalg.norm(current_vector)
                angle = np.arccos(np.clip(dot_product / norms, -1.0, 1.0))

                if angle > 0.1:  # Minimum rotation threshold
                    self._trigger_gesture(GestureType.ROTATE, {
                        'angle': angle,
                        'center': (pos1 + pos2) / 2
                    })

    def _trigger_gesture(self, gesture_type: GestureType, data: dict):
        """Trigger gesture callback."""
        if gesture_type in self.gesture_callbacks:
            self.gesture_callbacks[gesture_type](data)

        # Log gesture for debugging
        logger.debug(f"Gesture detected: {gesture_type.value} with data: {data}")


class PhysicsEngine:
    """Simple physics engine for 3D interactions."""

    def __init__(self):
        self.objects = []
        self.gravity = np.array([0.0, -9.81, 0.0])
        self.time_step = 1.0 / 60.0  # 60 FPS
        self.damping = 0.98

    def add_object(self, obj):
        """Add physics object."""
        self.objects.append(obj)

    def update(self, dt: float = None):
        """Update physics simulation."""
        dt = dt or self.time_step

        for obj in self.objects:
            if hasattr(obj, 'velocity') and hasattr(obj, 'position'):
                # Apply gravity
                obj.velocity += self.gravity * dt

                # Apply damping
                obj.velocity *= self.damping

                # Update position
                obj.position += obj.velocity * dt

                # Check bounds/collisions
                self._check_collisions(obj)

    def _check_collisions(self, obj):
        """Simple collision detection."""
        # Ground collision
        if obj.position[1] < 0:
            obj.position[1] = 0
            obj.velocity[1] = -obj.velocity[1] * 0.7  # Bounce with energy loss


class Interactive3DObject:
    """3D object with interaction capabilities."""

    def __init__(self, position: np.ndarray = None, name: str = "Object"):
        self.name = name
        self.position = position or np.zeros(3)
        self.transform = Transform3D(position=self.position)

        # Physics properties
        self.velocity = np.zeros(3)
        self.mass = 1.0

        # Interaction properties
        self.selectable = True
        self.selected = False
        self.draggable = True
        self.hoverable = True

        # Visual properties
        self.color = np.array([0.7, 0.7, 0.7, 1.0])
        self.highlight_color = np.array([1.0, 0.8, 0.0, 1.0])

        # Callbacks
        self.on_select = None
        self.on_deselect = None
        self.on_hover = None
        self.on_drag = None

    def select(self):
        """Select this object."""
        if not self.selectable:
            return False

        self.selected = True
        if self.on_select:
            self.on_select(self)
        return True

    def deselect(self):
        """Deselect this object."""
        self.selected = False
        if self.on_deselect:
            self.on_deselect(self)

    def hover(self, position: np.ndarray):
        """Handle hover event."""
        if self.hoverable and self.on_hover:
            self.on_hover(self, position)

    def drag(self, delta: np.ndarray):
        """Handle drag event."""
        if self.draggable:
            self.position += delta
            self.transform.position = self.position
            if self.on_drag:
                self.on_drag(self, delta)

    def get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get object bounding box."""
        # Default unit cube bounds
        min_bounds = self.position - 0.5
        max_bounds = self.position + 0.5
        return min_bounds, max_bounds

    def contains_point(self, point: np.ndarray) -> bool:
        """Check if point is inside object."""
        min_bounds, max_bounds = self.get_bounds()
        return np.all(point >= min_bounds) and np.all(point <= max_bounds)


class Advanced3DScene:
    """Advanced 3D scene with interaction management."""

    def __init__(self):
        self.camera = AdvancedCamera()
        self.objects = []
        self.selected_objects = []
        self.gesture_recognizer = GestureRecognizer()
        self.physics_engine = PhysicsEngine()

        # Scene properties
        self.background_color = np.array([0.1, 0.1, 0.1, 1.0])
        self.ambient_light = 0.2

        # Interaction state
        self.interaction_enabled = True
        self.physics_enabled = True

        # Setup gesture callbacks
        self._setup_gesture_callbacks()

    def add_object(self, obj: Interactive3DObject):
        """Add object to scene."""
        self.objects.append(obj)
        if self.physics_enabled:
            self.physics_engine.add_object(obj)

    def remove_object(self, obj: Interactive3DObject):
        """Remove object from scene."""
        if obj in self.objects:
            self.objects.remove(obj)
        if obj in self.selected_objects:
            self.selected_objects.remove(obj)

    def select_object(self, obj: Interactive3DObject):
        """Select an object."""
        if obj.select():
            if obj not in self.selected_objects:
                self.selected_objects.append(obj)

    def deselect_object(self, obj: Interactive3DObject):
        """Deselect an object."""
        obj.deselect()
        if obj in self.selected_objects:
            self.selected_objects.remove(obj)

    def clear_selection(self):
        """Clear all selected objects."""
        for obj in self.selected_objects[:]:
            self.deselect_object(obj)

    def get_object_at_position(self, position: np.ndarray) -> Optional[Interactive3DObject]:
        """Get object at world position."""
        for obj in self.objects:
            if obj.contains_point(position):
                return obj
        return None

    def update(self, dt: float):
        """Update scene."""
        if self.physics_enabled:
            self.physics_engine.update(dt)

    def _setup_gesture_callbacks(self):
        """Setup gesture recognition callbacks."""
        self.gesture_recognizer.register_gesture_callback(
            GestureType.TAP, self._handle_tap
        )
        self.gesture_recognizer.register_gesture_callback(
            GestureType.PINCH, self._handle_pinch
        )
        self.gesture_recognizer.register_gesture_callback(
            GestureType.PAN, self._handle_pan
        )
        self.gesture_recognizer.register_gesture_callback(
            GestureType.ROTATE, self._handle_rotate
        )

    def _handle_tap(self, data: dict):
        """Handle tap gesture."""
        # Convert screen position to world position (simplified)
        screen_pos = data['position']
        world_pos = self._screen_to_world(screen_pos)

        # Check for object selection
        obj = self.get_object_at_position(world_pos)
        if obj:
            if obj.selected:
                self.deselect_object(obj)
            else:
                self.select_object(obj)
        else:
            self.clear_selection()

    def _handle_pinch(self, data: dict):
        """Handle pinch gesture for zooming."""
        scale_factor = data['scale_factor']
        zoom_delta = (scale_factor - 1.0) * 0.1
        self.camera.zoom(-zoom_delta)

    def _handle_pan(self, data: dict):
        """Handle pan gesture for camera movement."""
        delta = data.get('delta', np.zeros(2))
        self.camera.pan(delta[0] * 0.01, delta[1] * 0.01)

    def _handle_rotate(self, data: dict):
        """Handle rotate gesture for camera rotation."""
        angle = data['angle']
        # Simple rotation around Y axis
        self.camera.orbit(np.degrees(angle), 0)

    def _screen_to_world(self, screen_pos: np.ndarray) -> np.ndarray:
        """Convert screen coordinates to world coordinates (simplified)."""
        # This would normally involve proper projection matrix inverse
        # For now, return a simple mapping
        return np.array([screen_pos[0] / 100.0 - 5.0, 0.0, screen_pos[1] / 100.0 - 5.0])

    def render_info(self):
        """Print scene information."""
        print(f"🎮 Advanced 3D Scene")
        print(f"Objects: {len(self.objects)}")
        print(f"Selected: {len(self.selected_objects)}")
        print(f"Camera Mode: {self.camera.mode.value}")
        print(f"Physics: {'Enabled' if self.physics_enabled else 'Disabled'}")
        print(f"Interaction: {'Enabled' if self.interaction_enabled else 'Disabled'}")