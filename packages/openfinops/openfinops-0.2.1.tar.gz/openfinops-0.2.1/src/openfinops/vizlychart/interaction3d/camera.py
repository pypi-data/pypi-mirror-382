"""
Advanced Camera Controls for 3D Visualization
Provides multiple camera control paradigms for different use cases.
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
from abc import ABC, abstractmethod


class CameraController(ABC):
    """Base class for all camera controllers."""

    def __init__(self, position: np.ndarray = None, target: np.ndarray = None):
        self.position = position if position is not None else np.array([0.0, 0.0, 5.0])
        self.target = target if target is not None else np.array([0.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])

        # View parameters
        self.fov = 60.0
        self.near = 0.1
        self.far = 1000.0
        self.aspect_ratio = 16.0 / 9.0

        # Animation state
        self.is_animating = False
        self.animation_duration = 1.0
        self.animation_start_time = 0.0

    @abstractmethod
    def update(
        self,
        dt: float,
        mouse_dx: float = 0,
        mouse_dy: float = 0,
        scroll_delta: float = 0,
        keys_pressed: set = None,
    ) -> None:
        """Update camera state based on input."""
        pass

    def get_view_matrix(self) -> np.ndarray:
        """Get the view transformation matrix."""
        return self._look_at(self.position, self.target, self.up)

    def get_projection_matrix(self) -> np.ndarray:
        """Get the projection transformation matrix."""
        return self._perspective(self.fov, self.aspect_ratio, self.near, self.far)

    def _look_at(
        self, eye: np.ndarray, center: np.ndarray, up: np.ndarray
    ) -> np.ndarray:
        """Create a look-at view matrix."""
        f = (center - eye) / np.linalg.norm(center - eye)
        s = np.cross(f, up) / np.linalg.norm(np.cross(f, up))
        u = np.cross(s, f)

        return np.array(
            [
                [s[0], s[1], s[2], -np.dot(s, eye)],
                [u[0], u[1], u[2], -np.dot(u, eye)],
                [-f[0], -f[1], -f[2], np.dot(f, eye)],
                [0, 0, 0, 1],
            ]
        )

    def _perspective(
        self, fovy: float, aspect: float, near: float, far: float
    ) -> np.ndarray:
        """Create a perspective projection matrix."""
        fovy_rad = math.radians(fovy)
        f = 1.0 / math.tan(fovy_rad / 2.0)

        return np.array(
            [
                [f / aspect, 0, 0, 0],
                [0, f, 0, 0],
                [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
                [0, 0, -1, 0],
            ]
        )


class OrbitController(CameraController):
    """Orbit camera controller for CAD-style navigation."""

    def __init__(
        self,
        position: np.ndarray = None,
        target: np.ndarray = None,
        distance: float = 5.0,
    ):
        super().__init__(position, target)

        # Spherical coordinates
        self.distance = distance
        self.azimuth = 0.0  # Horizontal rotation
        self.elevation = 30.0  # Vertical rotation

        # Control sensitivity
        self.rotation_speed = 0.5
        self.zoom_speed = 0.1
        self.pan_speed = 0.01

        # Constraints
        self.min_distance = 0.1
        self.max_distance = 100.0
        self.min_elevation = -89.0
        self.max_elevation = 89.0

        self._update_position()

    def update(
        self,
        dt: float,
        mouse_dx: float = 0,
        mouse_dy: float = 0,
        scroll_delta: float = 0,
        keys_pressed: set = None,
    ) -> None:
        """Update orbit camera based on mouse input."""
        keys_pressed = keys_pressed or set()

        # Handle rotation (left mouse button)
        if "mouse_left" in keys_pressed:
            self.azimuth += mouse_dx * self.rotation_speed
            self.elevation -= mouse_dy * self.rotation_speed
            self.elevation = np.clip(
                self.elevation, self.min_elevation, self.max_elevation
            )

        # Handle panning (middle mouse button or shift+left)
        elif "mouse_middle" in keys_pressed or (
            "shift" in keys_pressed and "mouse_left" in keys_pressed
        ):
            # Calculate pan vectors
            right = np.cross(self.position - self.target, self.up)
            right = (
                right / np.linalg.norm(right)
                if np.linalg.norm(right) > 0
                else np.array([1, 0, 0])
            )
            up = np.cross(right, self.position - self.target)
            up = up / np.linalg.norm(up) if np.linalg.norm(up) > 0 else self.up

            # Apply panning
            pan_offset = (
                (right * mouse_dx + up * mouse_dy) * self.pan_speed * self.distance
            )
            self.target += pan_offset

        # Handle zoom (scroll wheel)
        if scroll_delta != 0:
            zoom_factor = 1.0 + (scroll_delta * self.zoom_speed)
            self.distance *= zoom_factor
            self.distance = np.clip(self.distance, self.min_distance, self.max_distance)

        self._update_position()

    def _update_position(self):
        """Update camera position based on spherical coordinates."""
        azimuth_rad = math.radians(self.azimuth)
        elevation_rad = math.radians(self.elevation)

        x = self.distance * math.cos(elevation_rad) * math.cos(azimuth_rad)
        y = self.distance * math.sin(elevation_rad)
        z = self.distance * math.cos(elevation_rad) * math.sin(azimuth_rad)

        self.position = self.target + np.array([x, y, z])

    def focus_on_bounds(self, min_bounds: np.ndarray, max_bounds: np.ndarray):
        """Focus camera to fit given bounding box."""
        center = (min_bounds + max_bounds) / 2
        size = np.linalg.norm(max_bounds - min_bounds)

        self.target = center
        self.distance = size * 1.5  # Add some padding
        self._update_position()


class FlyController(CameraController):
    """Free-flying camera controller for exploration."""

    def __init__(self, position: np.ndarray = None, target: np.ndarray = None):
        super().__init__(position, target)

        # Rotation angles
        self.yaw = 0.0  # Horizontal rotation
        self.pitch = 0.0  # Vertical rotation

        # Movement parameters
        self.movement_speed = 5.0
        self.rotation_speed = 0.1
        self.sprint_multiplier = 3.0

        # Smoothing
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.acceleration = 20.0
        self.damping = 0.9

        self._update_orientation()

    def update(
        self,
        dt: float,
        mouse_dx: float = 0,
        mouse_dy: float = 0,
        scroll_delta: float = 0,
        keys_pressed: set = None,
    ) -> None:
        """Update fly camera based on input."""
        keys_pressed = keys_pressed or set()

        # Handle mouse look
        if "mouse_right" in keys_pressed:
            self.yaw += mouse_dx * self.rotation_speed
            self.pitch -= mouse_dy * self.rotation_speed
            self.pitch = np.clip(self.pitch, -89.0, 89.0)
            self._update_orientation()

        # Calculate movement vectors
        forward = self.target - self.position
        forward = forward / np.linalg.norm(forward)
        right = np.cross(forward, self.up)
        right = right / np.linalg.norm(right)

        # Handle movement keys
        movement = np.array([0.0, 0.0, 0.0])
        speed = self.movement_speed

        if "shift" in keys_pressed:
            speed *= self.sprint_multiplier

        if "w" in keys_pressed:
            movement += forward
        if "s" in keys_pressed:
            movement -= forward
        if "a" in keys_pressed:
            movement -= right
        if "d" in keys_pressed:
            movement += right
        if "q" in keys_pressed:
            movement -= self.up
        if "e" in keys_pressed:
            movement += self.up

        # Apply acceleration and damping
        if np.linalg.norm(movement) > 0:
            movement = movement / np.linalg.norm(movement)
            target_velocity = movement * speed
            self.velocity += (target_velocity - self.velocity) * self.acceleration * dt
        else:
            self.velocity *= self.damping

        # Update position
        self.position += self.velocity * dt
        self.target = self.position + forward

    def _update_orientation(self):
        """Update camera orientation based on yaw and pitch."""
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        direction = np.array(
            [
                math.cos(pitch_rad) * math.cos(yaw_rad),
                math.sin(pitch_rad),
                math.cos(pitch_rad) * math.sin(yaw_rad),
            ]
        )

        self.target = self.position + direction


class FirstPersonController(CameraController):
    """First-person camera controller with ground constraints."""

    def __init__(self, position: np.ndarray = None, eye_height: float = 1.8):
        target = (
            position + np.array([0, 0, -1])
            if position is not None
            else np.array([0, 0, -1])
        )
        super().__init__(position, target)

        self.eye_height = eye_height
        self.ground_level = 0.0

        # Rotation angles
        self.yaw = 0.0
        self.pitch = 0.0

        # Movement parameters
        self.walk_speed = 3.0
        self.run_speed = 6.0
        self.rotation_speed = 0.1

        # Physics
        self.gravity = -9.81
        self.jump_velocity = 5.0
        self.is_grounded = True
        self.vertical_velocity = 0.0

        # Ensure proper height
        self.position[1] = self.ground_level + self.eye_height
        self._update_orientation()

    def update(
        self,
        dt: float,
        mouse_dx: float = 0,
        mouse_dy: float = 0,
        scroll_delta: float = 0,
        keys_pressed: set = None,
    ) -> None:
        """Update first-person camera with ground constraints."""
        keys_pressed = keys_pressed or set()

        # Handle mouse look
        self.yaw += mouse_dx * self.rotation_speed
        self.pitch -= mouse_dy * self.rotation_speed
        self.pitch = np.clip(self.pitch, -89.0, 89.0)
        self._update_orientation()

        # Calculate movement (only on horizontal plane)
        forward_2d = np.array(
            [math.cos(math.radians(self.yaw)), 0, math.sin(math.radians(self.yaw))]
        )
        right_2d = np.array(
            [math.sin(math.radians(self.yaw)), 0, -math.cos(math.radians(self.yaw))]
        )

        movement = np.array([0.0, 0.0, 0.0])
        speed = self.run_speed if "shift" in keys_pressed else self.walk_speed

        if "w" in keys_pressed:
            movement += forward_2d
        if "s" in keys_pressed:
            movement -= forward_2d
        if "a" in keys_pressed:
            movement -= right_2d
        if "d" in keys_pressed:
            movement += right_2d

        # Apply horizontal movement
        if np.linalg.norm(movement) > 0:
            movement = movement / np.linalg.norm(movement)
            self.position += movement * speed * dt

        # Handle jumping
        if "space" in keys_pressed and self.is_grounded:
            self.vertical_velocity = self.jump_velocity
            self.is_grounded = False

        # Apply gravity
        if not self.is_grounded:
            self.vertical_velocity += self.gravity * dt
            self.position[1] += self.vertical_velocity * dt

            # Check ground collision
            if self.position[1] <= self.ground_level + self.eye_height:
                self.position[1] = self.ground_level + self.eye_height
                self.vertical_velocity = 0.0
                self.is_grounded = True

        self._update_orientation()

    def _update_orientation(self):
        """Update camera orientation based on yaw and pitch."""
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        direction = np.array(
            [
                math.cos(pitch_rad) * math.cos(yaw_rad),
                math.sin(pitch_rad),
                math.cos(pitch_rad) * math.sin(yaw_rad),
            ]
        )

        self.target = self.position + direction

    def set_ground_level(self, ground_y: float):
        """Set the ground level for physics calculations."""
        self.ground_level = ground_y
        if self.is_grounded:
            self.position[1] = self.ground_level + self.eye_height


class CameraAnimator:
    """Handles smooth camera transitions and animations."""

    def __init__(self, camera: CameraController):
        self.camera = camera
        self.is_animating = False
        self.animation_start_time = 0.0
        self.animation_duration = 1.0
        self.start_position = None
        self.target_position = None
        self.start_target = None
        self.target_target = None
        self.easing_function = self._ease_in_out_cubic

    def animate_to_position(
        self,
        target_pos: np.ndarray,
        target_target: np.ndarray = None,
        duration: float = 1.0,
        easing: str = "cubic",
    ) -> None:
        """Smoothly animate camera to new position."""
        self.start_position = self.camera.position.copy()
        self.target_position = target_pos.copy()

        if target_target is not None:
            self.start_target = self.camera.target.copy()
            self.target_target = target_target.copy()
        else:
            self.start_target = self.camera.target.copy()
            self.target_target = self.camera.target.copy()

        self.animation_duration = duration
        self.animation_start_time = 0.0
        self.is_animating = True

        # Set easing function
        easing_functions = {
            "linear": self._ease_linear,
            "cubic": self._ease_in_out_cubic,
            "elastic": self._ease_out_elastic,
            "bounce": self._ease_out_bounce,
        }
        self.easing_function = easing_functions.get(easing, self._ease_in_out_cubic)

    def update(self, dt: float) -> bool:
        """Update animation state. Returns True if still animating."""
        if not self.is_animating:
            return False

        self.animation_start_time += dt
        progress = min(self.animation_start_time / self.animation_duration, 1.0)

        # Apply easing
        eased_progress = self.easing_function(progress)

        # Interpolate position and target
        self.camera.position = self._lerp(
            self.start_position, self.target_position, eased_progress
        )
        self.camera.target = self._lerp(
            self.start_target, self.target_target, eased_progress
        )

        # Check if animation is complete
        if progress >= 1.0:
            self.is_animating = False
            self.camera.position = self.target_position.copy()
            self.camera.target = self.target_target.copy()

        return self.is_animating

    def _lerp(self, start: np.ndarray, end: np.ndarray, t: float) -> np.ndarray:
        """Linear interpolation between two vectors."""
        return start + (end - start) * t

    def _ease_linear(self, t: float) -> float:
        """Linear easing function."""
        return t

    def _ease_in_out_cubic(self, t: float) -> float:
        """Cubic ease-in-out function."""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

    def _ease_out_elastic(self, t: float) -> float:
        """Elastic ease-out function."""
        c4 = (2 * math.pi) / 3
        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

    def _ease_out_bounce(self, t: float) -> float:
        """Bounce ease-out function."""
        n1 = 7.5625
        d1 = 2.75

        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
