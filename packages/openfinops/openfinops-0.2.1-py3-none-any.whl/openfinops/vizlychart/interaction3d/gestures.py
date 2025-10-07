"""
Advanced Gesture Recognition for 3D Interactions
Supports multi-touch, mouse gestures, and complex interaction patterns.
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



import time
import math
from typing import List, Tuple, Optional, Dict, Callable, Any
from dataclasses import dataclass
from enum import Enum


class GestureType(Enum):
    """Enumeration of supported gesture types."""

    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    DRAG = "drag"
    PINCH = "pinch"
    ROTATE = "rotate"
    SWIPE = "swipe"
    PAN = "pan"
    ZOOM = "zoom"
    MOUSE_WHEEL = "mouse_wheel"
    MOUSE_CLICK = "mouse_click"
    MOUSE_DRAG = "mouse_drag"


@dataclass
class TouchPoint:
    """Represents a single touch point."""

    id: int
    x: float
    y: float
    timestamp: float
    pressure: float = 1.0
    radius: float = 10.0


@dataclass
class GestureEvent:
    """Represents a recognized gesture event."""

    type: GestureType
    start_time: float
    end_time: float
    start_position: Tuple[float, float]
    end_position: Tuple[float, float]
    velocity: Tuple[float, float] = (0.0, 0.0)
    scale: float = 1.0
    rotation: float = 0.0
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class GestureRecognizer:
    """Main gesture recognition engine."""

    def __init__(self, viewport_width: int = 800, viewport_height: int = 600):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        # Gesture parameters
        self.tap_threshold = 10.0  # pixels
        self.tap_duration = 0.3  # seconds
        self.double_tap_interval = 0.5  # seconds
        self.long_press_duration = 0.8  # seconds
        self.swipe_min_distance = 50.0  # pixels
        self.swipe_max_duration = 0.5  # seconds
        self.pinch_threshold = 20.0  # pixels

        # State tracking
        self.active_touches: Dict[int, TouchPoint] = {}
        self.gesture_history: List[GestureEvent] = []
        self.last_tap_time = 0.0
        self.last_tap_position = (0, 0)

        # Callbacks
        self.gesture_callbacks: Dict[GestureType, List[Callable]] = {
            gesture_type: [] for gesture_type in GestureType
        }

    def add_gesture_callback(self, gesture_type: GestureType, callback: Callable):
        """Add a callback function for a specific gesture type."""
        self.gesture_callbacks[gesture_type].append(callback)

    def remove_gesture_callback(self, gesture_type: GestureType, callback: Callable):
        """Remove a callback function."""
        if callback in self.gesture_callbacks[gesture_type]:
            self.gesture_callbacks[gesture_type].remove(callback)

    def process_touch_down(
        self, touch_id: int, x: float, y: float, pressure: float = 1.0
    ):
        """Process touch down event."""
        timestamp = time.time()
        touch_point = TouchPoint(touch_id, x, y, timestamp, pressure)
        self.active_touches[touch_id] = touch_point

        # Check for potential gestures
        if len(self.active_touches) == 1:
            self._start_potential_tap(x, y, timestamp)
        elif len(self.active_touches) == 2:
            self._start_potential_pinch()

    def process_touch_move(
        self, touch_id: int, x: float, y: float, pressure: float = 1.0
    ):
        """Process touch move event."""
        if touch_id not in self.active_touches:
            return

        timestamp = time.time()
        old_touch = self.active_touches[touch_id]
        new_touch = TouchPoint(touch_id, x, y, timestamp, pressure)
        self.active_touches[touch_id] = new_touch

        # Analyze movement
        dx = x - old_touch.x
        dy = y - old_touch.y
        distance = math.sqrt(dx * dx + dy * dy)

        if len(self.active_touches) == 1:
            self._process_single_touch_move(old_touch, new_touch, distance)
        elif len(self.active_touches) == 2:
            self._process_multi_touch_move()

    def process_touch_up(self, touch_id: int, x: float, y: float):
        """Process touch up event."""
        if touch_id not in self.active_touches:
            return

        timestamp = time.time()
        touch_point = self.active_touches[touch_id]
        del self.active_touches[touch_id]

        # Finalize gestures
        if len(self.active_touches) == 0:
            self._finalize_single_touch_gesture(touch_point, x, y, timestamp)
        elif len(self.active_touches) == 1:
            self._finalize_multi_touch_gesture()

    def _start_potential_tap(self, x: float, y: float, timestamp: float):
        """Start tracking a potential tap gesture."""
        self.potential_tap_start = (x, y, timestamp)

    def _start_potential_pinch(self):
        """Start tracking a potential pinch gesture."""
        touches = list(self.active_touches.values())
        if len(touches) >= 2:
            self.pinch_start_distance = self._calculate_distance(touches[0], touches[1])
            self.pinch_start_center = self._calculate_center(touches[0], touches[1])

    def _process_single_touch_move(
        self, old_touch: TouchPoint, new_touch: TouchPoint, distance: float
    ):
        """Process movement of a single touch point."""
        if distance > self.tap_threshold:
            # This is likely a drag gesture
            dx = new_touch.x - old_touch.x
            dy = new_touch.y - old_touch.y
            dt = new_touch.timestamp - old_touch.timestamp

            velocity = (dx / dt, dy / dt) if dt > 0 else (0, 0)

            gesture = GestureEvent(
                type=GestureType.DRAG,
                start_time=old_touch.timestamp,
                end_time=new_touch.timestamp,
                start_position=(old_touch.x, old_touch.y),
                end_position=(new_touch.x, new_touch.y),
                velocity=velocity,
            )
            self._emit_gesture(gesture)

    def _process_multi_touch_move(self):
        """Process movement of multiple touch points."""
        touches = list(self.active_touches.values())
        if len(touches) >= 2:
            current_distance = self._calculate_distance(touches[0], touches[1])
            current_center = self._calculate_center(touches[0], touches[1])

            if hasattr(self, "pinch_start_distance"):
                # Calculate pinch/zoom
                scale = current_distance / self.pinch_start_distance
                if abs(scale - 1.0) > 0.1:  # Threshold for significant scaling
                    gesture = GestureEvent(
                        type=GestureType.PINCH,
                        start_time=touches[0].timestamp,
                        end_time=touches[1].timestamp,
                        start_position=self.pinch_start_center,
                        end_position=current_center,
                        scale=scale,
                    )
                    self._emit_gesture(gesture)

                # Calculate rotation
                start_angle = self._calculate_angle(touches[0], touches[1])
                if hasattr(self, "pinch_start_angle"):
                    rotation = start_angle - self.pinch_start_angle
                    if abs(rotation) > math.radians(10):  # 10 degree threshold
                        gesture = GestureEvent(
                            type=GestureType.ROTATE,
                            start_time=touches[0].timestamp,
                            end_time=touches[1].timestamp,
                            start_position=self.pinch_start_center,
                            end_position=current_center,
                            rotation=rotation,
                        )
                        self._emit_gesture(gesture)
                else:
                    self.pinch_start_angle = start_angle

    def _finalize_single_touch_gesture(
        self, touch_point: TouchPoint, end_x: float, end_y: float, timestamp: float
    ):
        """Finalize a single touch gesture."""
        if hasattr(self, "potential_tap_start"):
            start_x, start_y, start_time = self.potential_tap_start
            duration = timestamp - start_time
            distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)

            if distance <= self.tap_threshold:
                if duration <= self.tap_duration:
                    # Check for double tap
                    if (
                        timestamp - self.last_tap_time <= self.double_tap_interval
                        and math.sqrt(
                            (start_x - self.last_tap_position[0]) ** 2
                            + (start_y - self.last_tap_position[1]) ** 2
                        )
                        <= self.tap_threshold
                    ):
                        gesture = GestureEvent(
                            type=GestureType.DOUBLE_TAP,
                            start_time=start_time,
                            end_time=timestamp,
                            start_position=(start_x, start_y),
                            end_position=(end_x, end_y),
                        )
                    else:
                        gesture = GestureEvent(
                            type=GestureType.TAP,
                            start_time=start_time,
                            end_time=timestamp,
                            start_position=(start_x, start_y),
                            end_position=(end_x, end_y),
                        )
                    self._emit_gesture(gesture)
                    self.last_tap_time = timestamp
                    self.last_tap_position = (start_x, start_y)

                elif duration >= self.long_press_duration:
                    gesture = GestureEvent(
                        type=GestureType.LONG_PRESS,
                        start_time=start_time,
                        end_time=timestamp,
                        start_position=(start_x, start_y),
                        end_position=(end_x, end_y),
                    )
                    self._emit_gesture(gesture)

            else:
                # Check for swipe
                if (
                    distance >= self.swipe_min_distance
                    and duration <= self.swipe_max_duration
                ):
                    velocity = (
                        (end_x - start_x) / duration,
                        (end_y - start_y) / duration,
                    )
                    gesture = GestureEvent(
                        type=GestureType.SWIPE,
                        start_time=start_time,
                        end_time=timestamp,
                        start_position=(start_x, start_y),
                        end_position=(end_x, end_y),
                        velocity=velocity,
                    )
                    self._emit_gesture(gesture)

    def _finalize_multi_touch_gesture(self):
        """Finalize multi-touch gestures."""
        # Clean up multi-touch state
        if hasattr(self, "pinch_start_distance"):
            del self.pinch_start_distance
        if hasattr(self, "pinch_start_center"):
            del self.pinch_start_center
        if hasattr(self, "pinch_start_angle"):
            del self.pinch_start_angle

    def _calculate_distance(self, touch1: TouchPoint, touch2: TouchPoint) -> float:
        """Calculate distance between two touch points."""
        dx = touch2.x - touch1.x
        dy = touch2.y - touch1.y
        return math.sqrt(dx * dx + dy * dy)

    def _calculate_center(
        self, touch1: TouchPoint, touch2: TouchPoint
    ) -> Tuple[float, float]:
        """Calculate center point between two touches."""
        return ((touch1.x + touch2.x) / 2, (touch1.y + touch2.y) / 2)

    def _calculate_angle(self, touch1: TouchPoint, touch2: TouchPoint) -> float:
        """Calculate angle between two touch points."""
        dx = touch2.x - touch1.x
        dy = touch2.y - touch1.y
        return math.atan2(dy, dx)

    def _emit_gesture(self, gesture: GestureEvent):
        """Emit a gesture event to all registered callbacks."""
        self.gesture_history.append(gesture)

        # Keep history limited
        if len(self.gesture_history) > 100:
            self.gesture_history = self.gesture_history[-50:]

        # Call all registered callbacks
        for callback in self.gesture_callbacks[gesture.type]:
            try:
                callback(gesture)
            except Exception as e:
                print(f"Error in gesture callback: {e}")


class TouchHandler:
    """Specialized touch input handler for mobile devices."""

    def __init__(self, gesture_recognizer: GestureRecognizer):
        self.recognizer = gesture_recognizer
        self.touch_scale = 1.0  # Scale factor for touch coordinates

    def handle_touch_event(self, event_type: str, touches: List[Dict[str, Any]]):
        """Handle touch events from the platform."""
        if event_type == "touchstart":
            for touch in touches:
                self.recognizer.process_touch_down(
                    touch["identifier"],
                    touch["clientX"] * self.touch_scale,
                    touch["clientY"] * self.touch_scale,
                    touch.get("force", 1.0),
                )

        elif event_type == "touchmove":
            for touch in touches:
                self.recognizer.process_touch_move(
                    touch["identifier"],
                    touch["clientX"] * self.touch_scale,
                    touch["clientY"] * self.touch_scale,
                    touch.get("force", 1.0),
                )

        elif event_type == "touchend":
            for touch in touches:
                self.recognizer.process_touch_up(
                    touch["identifier"],
                    touch["clientX"] * self.touch_scale,
                    touch["clientY"] * self.touch_scale,
                )


class MouseHandler:
    """Mouse input handler for desktop interactions."""

    def __init__(self, gesture_recognizer: GestureRecognizer):
        self.recognizer = gesture_recognizer
        self.mouse_buttons = {"left": False, "middle": False, "right": False}
        self.last_mouse_pos = (0, 0)
        self.mouse_touch_id = 999  # Special ID for mouse events

    def handle_mouse_down(self, x: float, y: float, button: str):
        """Handle mouse button press."""
        self.mouse_buttons[button] = True
        self.last_mouse_pos = (x, y)

        if button == "left":
            self.recognizer.process_touch_down(self.mouse_touch_id, x, y)

    def handle_mouse_move(self, x: float, y: float):
        """Handle mouse movement."""
        dx = x - self.last_mouse_pos[0]
        dy = y - self.last_mouse_pos[1]
        self.last_mouse_pos = (x, y)

        if self.mouse_buttons["left"]:
            self.recognizer.process_touch_move(self.mouse_touch_id, x, y)

        # Emit drag gesture for mouse movement
        if any(self.mouse_buttons.values()):
            gesture = GestureEvent(
                type=GestureType.MOUSE_DRAG,
                start_time=time.time(),
                end_time=time.time(),
                start_position=self.last_mouse_pos,
                end_position=(x, y),
                velocity=(dx, dy),
                properties={"buttons": self.mouse_buttons.copy()},
            )
            self.recognizer._emit_gesture(gesture)

    def handle_mouse_up(self, x: float, y: float, button: str):
        """Handle mouse button release."""
        self.mouse_buttons[button] = False

        if button == "left":
            self.recognizer.process_touch_up(self.mouse_touch_id, x, y)

        # Emit click gesture
        gesture = GestureEvent(
            type=GestureType.MOUSE_CLICK,
            start_time=time.time(),
            end_time=time.time(),
            start_position=(x, y),
            end_position=(x, y),
            properties={"button": button},
        )
        self.recognizer._emit_gesture(gesture)

    def handle_mouse_wheel(self, x: float, y: float, delta_x: float, delta_y: float):
        """Handle mouse wheel scrolling."""
        gesture = GestureEvent(
            type=GestureType.MOUSE_WHEEL,
            start_time=time.time(),
            end_time=time.time(),
            start_position=(x, y),
            end_position=(x, y),
            properties={"delta_x": delta_x, "delta_y": delta_y},
        )
        self.recognizer._emit_gesture(gesture)


class GestureFilter:
    """Filters and processes gesture events for specific use cases."""

    def __init__(self):
        self.enabled_gestures = set(GestureType)
        self.gesture_transformers = {}

    def enable_gesture(self, gesture_type: GestureType):
        """Enable a specific gesture type."""
        self.enabled_gestures.add(gesture_type)

    def disable_gesture(self, gesture_type: GestureType):
        """Disable a specific gesture type."""
        self.enabled_gestures.discard(gesture_type)

    def add_transformer(self, gesture_type: GestureType, transformer: Callable):
        """Add a transformer function for a gesture type."""
        self.gesture_transformers[gesture_type] = transformer

    def filter_gesture(self, gesture: GestureEvent) -> Optional[GestureEvent]:
        """Filter and potentially transform a gesture event."""
        if gesture.type not in self.enabled_gestures:
            return None

        # Apply transformer if available
        if gesture.type in self.gesture_transformers:
            try:
                return self.gesture_transformers[gesture.type](gesture)
            except Exception as e:
                print(f"Error in gesture transformer: {e}")
                return gesture

        return gesture


class GestureComposer:
    """Composes complex gestures from simple ones."""

    def __init__(self, gesture_recognizer: GestureRecognizer):
        self.recognizer = gesture_recognizer
        self.composite_patterns = {}
        self.active_sequences = []

    def define_composite_gesture(
        self, name: str, pattern: List[GestureType], max_interval: float = 1.0
    ):
        """Define a composite gesture pattern."""
        self.composite_patterns[name] = {
            "pattern": pattern,
            "max_interval": max_interval,
        }

    def check_composite_gestures(self, new_gesture: GestureEvent):
        """Check if new gesture completes any composite patterns."""
        # Update active sequences
        self.active_sequences = [
            seq
            for seq in self.active_sequences
            if new_gesture.start_time - seq[-1].end_time <= 2.0  # Cleanup old sequences
        ]

        # Add to existing sequences
        for seq in self.active_sequences:
            seq.append(new_gesture)

        # Start new sequence
        self.active_sequences.append([new_gesture])

        # Check for pattern matches
        for name, config in self.composite_patterns.items():
            pattern = config["pattern"]
            max_interval = config["max_interval"]

            for seq in self.active_sequences:
                if self._matches_pattern(seq, pattern, max_interval):
                    # Create composite gesture event
                    composite = GestureEvent(
                        type=GestureType.TAP,  # Could add composite types
                        start_time=seq[0].start_time,
                        end_time=seq[-1].end_time,
                        start_position=seq[0].start_position,
                        end_position=seq[-1].end_position,
                        properties={"composite_name": name, "sequence": seq},
                    )
                    self.recognizer._emit_gesture(composite)

    def _matches_pattern(
        self,
        sequence: List[GestureEvent],
        pattern: List[GestureType],
        max_interval: float,
    ) -> bool:
        """Check if a sequence matches a pattern."""
        if len(sequence) != len(pattern):
            return False

        for i, (gesture, expected_type) in enumerate(zip(sequence, pattern)):
            if gesture.type != expected_type:
                return False

            if i > 0:
                interval = gesture.start_time - sequence[i - 1].end_time
                if interval > max_interval:
                    return False

        return True
