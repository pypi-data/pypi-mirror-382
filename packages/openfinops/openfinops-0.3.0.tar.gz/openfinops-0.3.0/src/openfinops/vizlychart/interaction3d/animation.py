"""
3D Animation System
Provides camera animations, object animations, and keyframe systems.
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
from typing import List, Tuple, Optional, Dict, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class AnimationType(Enum):
    """Animation type enumeration."""

    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    CUBIC_BEZIER = "cubic_bezier"
    SPRING = "spring"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class InterpolationMode(Enum):
    """Interpolation mode for animations."""

    LINEAR = "linear"
    SPHERICAL = "spherical"  # For quaternions
    CUBIC_SPLINE = "cubic_spline"
    CATMULL_ROM = "catmull_rom"


@dataclass
class KeyFrame:
    """Animation keyframe with time, value, and easing."""

    time: float
    value: Union[float, np.ndarray]
    easing: AnimationType = AnimationType.LINEAR
    tangent_in: Optional[np.ndarray] = None
    tangent_out: Optional[np.ndarray] = None

    def __post_init__(self):
        """Ensure value is numpy array."""
        if not isinstance(self.value, np.ndarray):
            if isinstance(self.value, (list, tuple)):
                self.value = np.array(self.value)
            else:
                self.value = np.array([self.value])


@dataclass
class AnimationTrack:
    """Animation track containing keyframes for a specific property."""

    name: str
    keyframes: List[KeyFrame] = field(default_factory=list)
    interpolation_mode: InterpolationMode = InterpolationMode.LINEAR
    is_looping: bool = False

    def add_keyframe(
        self,
        time: float,
        value: Union[float, np.ndarray],
        easing: AnimationType = AnimationType.LINEAR,
    ):
        """Add a keyframe to the track."""
        keyframe = KeyFrame(time, value, easing)

        # Insert in time order
        inserted = False
        for i, existing_kf in enumerate(self.keyframes):
            if time < existing_kf.time:
                self.keyframes.insert(i, keyframe)
                inserted = True
                break

        if not inserted:
            self.keyframes.append(keyframe)

    def evaluate(self, time: float) -> np.ndarray:
        """Evaluate the track at given time."""
        if not self.keyframes:
            return np.array([0.0])

        # Handle looping
        if self.is_looping and len(self.keyframes) >= 2:
            duration = self.keyframes[-1].time - self.keyframes[0].time
            if duration > 0:
                time = (
                    self.keyframes[0].time + (time - self.keyframes[0].time) % duration
                )

        # Find surrounding keyframes
        if time <= self.keyframes[0].time:
            return self.keyframes[0].value.copy()

        if time >= self.keyframes[-1].time:
            return self.keyframes[-1].value.copy()

        # Find interpolation range
        for i in range(len(self.keyframes) - 1):
            kf1 = self.keyframes[i]
            kf2 = self.keyframes[i + 1]

            if kf1.time <= time <= kf2.time:
                return self._interpolate_keyframes(kf1, kf2, time)

        return self.keyframes[-1].value.copy()

    def get_duration(self) -> float:
        """Get total duration of animation track."""
        if not self.keyframes:
            return 0.0
        return self.keyframes[-1].time - self.keyframes[0].time

    def _interpolate_keyframes(
        self, kf1: KeyFrame, kf2: KeyFrame, time: float
    ) -> np.ndarray:
        """Interpolate between two keyframes."""
        dt = kf2.time - kf1.time
        if dt <= 0:
            return kf1.value.copy()

        # Calculate normalized time
        t = (time - kf1.time) / dt

        # Apply easing function
        eased_t = self._apply_easing(t, kf2.easing)

        # Interpolate based on mode
        if self.interpolation_mode == InterpolationMode.LINEAR:
            return self._linear_interpolate(kf1.value, kf2.value, eased_t)
        elif self.interpolation_mode == InterpolationMode.SPHERICAL:
            return self._spherical_interpolate(kf1.value, kf2.value, eased_t)
        elif self.interpolation_mode == InterpolationMode.CUBIC_SPLINE:
            return self._cubic_spline_interpolate(kf1, kf2, eased_t)
        else:
            return self._linear_interpolate(kf1.value, kf2.value, eased_t)

    def _linear_interpolate(
        self, v1: np.ndarray, v2: np.ndarray, t: float
    ) -> np.ndarray:
        """Linear interpolation between two values."""
        return v1 + (v2 - v1) * t

    def _spherical_interpolate(
        self, q1: np.ndarray, q2: np.ndarray, t: float
    ) -> np.ndarray:
        """Spherical linear interpolation for quaternions."""
        if len(q1) != 4 or len(q2) != 4:
            return self._linear_interpolate(q1, q2, t)

        # Normalize quaternions
        q1 = q1 / np.linalg.norm(q1)
        q2 = q2 / np.linalg.norm(q2)

        # Calculate angle between quaternions
        dot = np.dot(q1, q2)

        # If dot product is negative, slerp won't take the shorter path
        if dot < 0.0:
            q2 = -q2
            dot = -dot

        # If quaternions are very close, use linear interpolation
        if dot > 0.9995:
            result = q1 + t * (q2 - q1)
            return result / np.linalg.norm(result)

        # Calculate slerp
        theta_0 = math.acos(abs(dot))
        sin_theta_0 = math.sin(theta_0)

        theta = theta_0 * t
        sin_theta = math.sin(theta)

        s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
        s1 = sin_theta / sin_theta_0

        return (s0 * q1) + (s1 * q2)

    def _cubic_spline_interpolate(
        self, kf1: KeyFrame, kf2: KeyFrame, t: float
    ) -> np.ndarray:
        """Cubic spline interpolation using tangents."""
        # Use tangents if available, otherwise calculate them
        if kf1.tangent_out is not None:
            tangent1 = kf1.tangent_out
        else:
            tangent1 = (kf2.value - kf1.value) * 0.5

        if kf2.tangent_in is not None:
            tangent2 = kf2.tangent_in
        else:
            tangent2 = (kf2.value - kf1.value) * 0.5

        # Hermite interpolation
        t2 = t * t
        t3 = t2 * t

        h1 = 2 * t3 - 3 * t2 + 1
        h2 = -2 * t3 + 3 * t2
        h3 = t3 - 2 * t2 + t
        h4 = t3 - t2

        return h1 * kf1.value + h2 * kf2.value + h3 * tangent1 + h4 * tangent2

    def _apply_easing(self, t: float, easing: AnimationType) -> float:
        """Apply easing function to normalized time."""
        if easing == AnimationType.LINEAR:
            return t
        elif easing == AnimationType.EASE_IN:
            return t * t
        elif easing == AnimationType.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif easing == AnimationType.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif easing == AnimationType.SPRING:
            return 1 - math.cos(t * math.pi * 0.5)
        elif easing == AnimationType.BOUNCE:
            if t < 1 / 2.75:
                return 7.5625 * t * t
            elif t < 2 / 2.75:
                t -= 1.5 / 2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5 / 2.75:
                t -= 2.25 / 2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625 / 2.75
                return 7.5625 * t * t + 0.984375
        elif easing == AnimationType.ELASTIC:
            if t == 0 or t == 1:
                return t
            p = 0.3
            s = p / 4
            return -(
                math.pow(2, 10 * (t - 1)) * math.sin((t - 1 - s) * (2 * math.pi) / p)
            )
        else:
            return t


class Animation:
    """Complete animation containing multiple tracks."""

    def __init__(self, name: str = ""):
        self.name = name
        self.tracks: Dict[str, AnimationTrack] = {}
        self.is_playing = False
        self.is_looping = False
        self.playback_speed = 1.0
        self.current_time = 0.0
        self.start_time = 0.0

        # Events
        self.on_animation_start: Optional[Callable[[], None]] = None
        self.on_animation_end: Optional[Callable[[], None]] = None
        self.on_animation_loop: Optional[Callable[[], None]] = None

    def add_track(self, track: AnimationTrack):
        """Add animation track."""
        self.tracks[track.name] = track

    def create_track(
        self,
        name: str,
        interpolation_mode: InterpolationMode = InterpolationMode.LINEAR,
    ) -> AnimationTrack:
        """Create and add new animation track."""
        track = AnimationTrack(name, interpolation_mode=interpolation_mode)
        self.tracks[name] = track
        return track

    def play(self, loop: bool = False):
        """Start playing animation."""
        self.is_playing = True
        self.is_looping = loop
        self.start_time = time.time()

        if self.on_animation_start:
            self.on_animation_start()

    def pause(self):
        """Pause animation."""
        self.is_playing = False

    def stop(self):
        """Stop and reset animation."""
        self.is_playing = False
        self.current_time = 0.0

    def seek(self, time_position: float):
        """Seek to specific time position."""
        self.current_time = max(0, time_position)

    def update(self, dt: float) -> Dict[str, np.ndarray]:
        """Update animation and return current values."""
        if not self.is_playing:
            return {}

        # Update current time
        self.current_time += dt * self.playback_speed

        # Check if animation finished
        duration = self.get_duration()
        if duration > 0 and self.current_time >= duration:
            if self.is_looping:
                self.current_time = 0.0
                if self.on_animation_loop:
                    self.on_animation_loop()
            else:
                self.is_playing = False
                self.current_time = duration
                if self.on_animation_end:
                    self.on_animation_end()

        # Evaluate all tracks
        values = {}
        for track_name, track in self.tracks.items():
            values[track_name] = track.evaluate(self.current_time)

        return values

    def get_duration(self) -> float:
        """Get total animation duration."""
        if not self.tracks:
            return 0.0
        return max(track.get_duration() for track in self.tracks.values())

    def blend_with(
        self, other: "Animation", blend_factor: float
    ) -> Dict[str, np.ndarray]:
        """Blend this animation with another."""
        self_values = self.update(0)  # Get current values without advancing time
        other_values = other.update(0)

        blended = {}

        # Blend common tracks
        for track_name in self.tracks:
            if track_name in other.tracks:
                self_val = self_values.get(track_name, np.array([0.0]))
                other_val = other_values.get(track_name, np.array([0.0]))
                blended[track_name] = (
                    self_val * (1 - blend_factor) + other_val * blend_factor
                )
            else:
                blended[track_name] = self_values.get(track_name, np.array([0.0]))

        # Add tracks that only exist in other animation
        for track_name in other.tracks:
            if track_name not in self.tracks:
                blended[track_name] = (
                    other_values.get(track_name, np.array([0.0])) * blend_factor
                )

        return blended


class CameraAnimator:
    """Specialized animator for camera movements."""

    def __init__(self, camera_controller=None):
        self.camera_controller = camera_controller
        self.active_animation: Optional[Animation] = None
        self.animation_library: Dict[str, Animation] = {}

    def create_position_animation(
        self,
        name: str,
        positions: List[np.ndarray],
        times: List[float],
        easing: AnimationType = AnimationType.EASE_IN_OUT,
    ) -> Animation:
        """Create camera position animation."""
        animation = Animation(name)

        position_track = animation.create_track("position")

        for time_val, pos in zip(times, positions):
            position_track.add_keyframe(time_val, pos, easing)

        self.animation_library[name] = animation
        return animation

    def create_orbit_animation(
        self,
        name: str,
        center: np.ndarray,
        radius: float,
        height: float,
        duration: float,
        revolutions: int = 1,
    ) -> Animation:
        """Create orbital camera animation."""
        animation = Animation(name)

        position_track = animation.create_track("position")
        target_track = animation.create_track("target")

        num_keyframes = max(16, revolutions * 8)

        for i in range(num_keyframes + 1):
            t = i / num_keyframes
            time_val = t * duration

            angle = 2 * math.pi * revolutions * t
            x = center[0] + radius * math.cos(angle)
            z = center[2] + radius * math.sin(angle)
            y = center[1] + height

            position = np.array([x, y, z])

            position_track.add_keyframe(time_val, position, AnimationType.LINEAR)
            target_track.add_keyframe(time_val, center, AnimationType.LINEAR)

        self.animation_library[name] = animation
        return animation

    def create_flythrough_animation(
        self,
        name: str,
        waypoints: List[Tuple[np.ndarray, np.ndarray]],
        duration: float,
        smooth: bool = True,
    ) -> Animation:
        """Create flythrough animation from waypoints (position, target pairs)."""
        animation = Animation(name)

        position_track = animation.create_track(
            "position",
            InterpolationMode.CUBIC_SPLINE if smooth else InterpolationMode.LINEAR,
        )
        target_track = animation.create_track(
            "target",
            InterpolationMode.CUBIC_SPLINE if smooth else InterpolationMode.LINEAR,
        )

        segment_duration = duration / max(1, len(waypoints) - 1)

        for i, (position, target) in enumerate(waypoints):
            time_val = i * segment_duration
            easing = AnimationType.EASE_IN_OUT if smooth else AnimationType.LINEAR

            position_track.add_keyframe(time_val, position, easing)
            target_track.add_keyframe(time_val, target, easing)

        self.animation_library[name] = animation
        return animation

    def create_focus_animation(
        self, name: str, target_position: np.ndarray, distance: float, duration: float
    ) -> Animation:
        """Create animation that focuses on a target."""
        if not self.camera_controller:
            return Animation(name)

        current_pos = self.camera_controller.position

        # Calculate optimal viewing position
        direction = current_pos - target_position
        direction = direction / np.linalg.norm(direction)
        final_position = target_position + direction * distance

        animation = Animation(name)

        position_track = animation.create_track("position")
        target_track = animation.create_track("target")

        # Start and end keyframes
        position_track.add_keyframe(0.0, current_pos, AnimationType.EASE_OUT)
        position_track.add_keyframe(duration, final_position, AnimationType.EASE_IN)

        target_track.add_keyframe(
            0.0, self.camera_controller.target, AnimationType.EASE_OUT
        )
        target_track.add_keyframe(duration, target_position, AnimationType.EASE_IN)

        self.animation_library[name] = animation
        return animation

    def play_animation(self, name: str, loop: bool = False) -> bool:
        """Play named animation."""
        if name in self.animation_library:
            self.active_animation = self.animation_library[name]
            self.active_animation.play(loop)
            return True
        return False

    def stop_animation(self):
        """Stop current animation."""
        if self.active_animation:
            self.active_animation.stop()
            self.active_animation = None

    def update(self, dt: float):
        """Update camera animation."""
        if not self.active_animation or not self.camera_controller:
            return

        values = self.active_animation.update(dt)

        # Apply values to camera
        if "position" in values:
            self.camera_controller.position = values["position"]

        if "target" in values:
            self.camera_controller.target = values["target"]

        # Handle animation completion
        if not self.active_animation.is_playing:
            self.active_animation = None


class ObjectAnimator:
    """Animator for 3D objects and their properties."""

    def __init__(self):
        self.object_animations: Dict[str, Animation] = {}
        self.active_animations: Dict[str, Animation] = {}

    def create_transform_animation(self, object_id: str, name: str) -> Animation:
        """Create transformation animation for object."""
        full_name = f"{object_id}_{name}"
        animation = Animation(full_name)

        # Add common transform tracks
        animation.create_track("position")
        animation.create_track("rotation", InterpolationMode.SPHERICAL)
        animation.create_track("scale")

        self.object_animations[full_name] = animation
        return animation

    def animate_to_position(
        self,
        object_id: str,
        target_position: np.ndarray,
        duration: float,
        easing: AnimationType = AnimationType.EASE_IN_OUT,
    ) -> str:
        """Create simple position animation."""
        name = f"{object_id}_move_{int(time.time())}"
        animation = Animation(name)

        position_track = animation.create_track("position")

        # Would need current position from object system
        current_position = np.array([0.0, 0.0, 0.0])  # Placeholder

        position_track.add_keyframe(0.0, current_position)
        position_track.add_keyframe(duration, target_position, easing)

        self.object_animations[name] = animation
        return name

    def play_object_animation(
        self, object_id: str, animation_name: str, loop: bool = False
    ) -> bool:
        """Play animation for specific object."""
        full_name = f"{object_id}_{animation_name}"

        if full_name in self.object_animations:
            animation = self.object_animations[full_name]
            animation.play(loop)
            self.active_animations[object_id] = animation
            return True

        return False

    def stop_object_animation(self, object_id: str):
        """Stop animation for object."""
        if object_id in self.active_animations:
            self.active_animations[object_id].stop()
            del self.active_animations[object_id]

    def update(self, dt: float) -> Dict[str, Dict[str, np.ndarray]]:
        """Update all object animations."""
        results = {}
        completed_objects = []

        for object_id, animation in self.active_animations.items():
            values = animation.update(dt)
            results[object_id] = values

            # Remove completed animations
            if not animation.is_playing:
                completed_objects.append(object_id)

        # Clean up completed animations
        for object_id in completed_objects:
            del self.active_animations[object_id]

        return results


class KeyFrameSystem:
    """Advanced keyframe animation system with timeline."""

    def __init__(self):
        self.timeline_animations: Dict[str, Animation] = {}
        self.global_time = 0.0
        self.is_playing = False
        self.playback_speed = 1.0

        # Timeline controls
        self.loop_start = 0.0
        self.loop_end = 10.0
        self.is_looping = False

    def add_animation(self, name: str, animation: Animation, start_time: float = 0.0):
        """Add animation to timeline."""
        # Offset all keyframes by start_time
        for track in animation.tracks.values():
            for keyframe in track.keyframes:
                keyframe.time += start_time

        self.timeline_animations[name] = animation

    def create_timeline_animation(
        self, name: str, start_time: float = 0.0
    ) -> Animation:
        """Create new animation on timeline."""
        animation = Animation(name)
        self.add_animation(name, animation, start_time)
        return animation

    def play_timeline(self, loop: bool = False):
        """Play entire timeline."""
        self.is_playing = True
        self.is_looping = loop

        # Start all animations
        for animation in self.timeline_animations.values():
            animation.play(loop)

    def pause_timeline(self):
        """Pause timeline."""
        self.is_playing = False
        for animation in self.timeline_animations.values():
            animation.pause()

    def stop_timeline(self):
        """Stop and reset timeline."""
        self.is_playing = False
        self.global_time = 0.0

        for animation in self.timeline_animations.values():
            animation.stop()

    def seek_timeline(self, time_position: float):
        """Seek timeline to specific time."""
        self.global_time = time_position

        for animation in self.timeline_animations.values():
            animation.seek(time_position)

    def update_timeline(self, dt: float) -> Dict[str, Dict[str, np.ndarray]]:
        """Update entire timeline."""
        if not self.is_playing:
            return {}

        self.global_time += dt * self.playback_speed

        # Handle looping
        if self.is_looping:
            loop_duration = self.loop_end - self.loop_start
            if self.global_time >= self.loop_end:
                self.global_time = (
                    self.loop_start + (self.global_time - self.loop_end) % loop_duration
                )

        # Update all animations
        results = {}
        for name, animation in self.timeline_animations.items():
            values = animation.update(dt * self.playback_speed)
            if values:  # Only include if animation is active
                results[name] = values

        return results

    def get_timeline_duration(self) -> float:
        """Get total timeline duration."""
        if not self.timeline_animations:
            return 0.0

        max_duration = 0.0
        for animation in self.timeline_animations.values():
            duration = animation.get_duration()
            if duration > max_duration:
                max_duration = duration

        return max_duration

    def set_loop_region(self, start_time: float, end_time: float):
        """Set loop region for timeline."""
        self.loop_start = start_time
        self.loop_end = end_time

    def export_keyframes(
        self, animation_name: str
    ) -> Dict[str, List[Tuple[float, Any]]]:
        """Export keyframes for external use."""
        if animation_name not in self.timeline_animations:
            return {}

        animation = self.timeline_animations[animation_name]
        exported = {}

        for track_name, track in animation.tracks.items():
            keyframe_data = []
            for kf in track.keyframes:
                keyframe_data.append(
                    (
                        kf.time,
                        (
                            kf.value.tolist()
                            if isinstance(kf.value, np.ndarray)
                            else kf.value
                        ),
                    )
                )
            exported[track_name] = keyframe_data

        return exported
