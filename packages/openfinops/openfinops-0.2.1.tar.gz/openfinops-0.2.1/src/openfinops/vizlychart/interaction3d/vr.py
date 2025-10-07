"""
VR/AR Visualization Support
Provides immersive visualization capabilities for virtual and augmented reality.
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
from typing import List, Tuple, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class VRDevice(Enum):
    """Supported VR device types."""

    OCULUS_RIFT = "oculus_rift"
    OCULUS_QUEST = "oculus_quest"
    HTC_VIVE = "htc_vive"
    VALVE_INDEX = "valve_index"
    WINDOWS_MR = "windows_mr"
    PICO = "pico"
    GENERIC_OPENVR = "generic_openvr"
    WEBXR = "webxr"


class ARDevice(Enum):
    """Supported AR device types."""

    HOLOLENS = "hololens"
    MAGIC_LEAP = "magic_leap"
    ARCORE = "arcore"
    ARKIT = "arkit"
    WEBXR_AR = "webxr_ar"


class TrackingSpace(Enum):
    """VR tracking space types."""

    SEATED = "seated"
    STANDING = "standing"
    ROOM_SCALE = "room_scale"


@dataclass
class Eye:
    """VR eye configuration."""

    projection_matrix: np.ndarray
    view_matrix: np.ndarray
    viewport: Tuple[int, int, int, int]  # x, y, width, height


@dataclass
class VRPose:
    """VR device pose information."""

    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    rotation: np.ndarray = field(
        default_factory=lambda: np.array([0, 0, 0, 1])
    )  # Quaternion
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    angular_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    is_valid: bool = True
    timestamp: float = 0.0

    def to_matrix(self) -> np.ndarray:
        """Convert pose to 4x4 transformation matrix."""
        # Convert quaternion to rotation matrix
        q = self.rotation
        qx, qy, qz, qw = q[0], q[1], q[2], q[3]

        rotation_matrix = np.array(
            [
                [
                    1 - 2 * (qy * qy + qz * qz),
                    2 * (qx * qy - qz * qw),
                    2 * (qx * qz + qy * qw),
                    0,
                ],
                [
                    2 * (qx * qy + qz * qw),
                    1 - 2 * (qx * qx + qz * qz),
                    2 * (qy * qz - qx * qw),
                    0,
                ],
                [
                    2 * (qx * qz - qy * qw),
                    2 * (qy * qz + qx * qw),
                    1 - 2 * (qx * qx + qy * qy),
                    0,
                ],
                [0, 0, 0, 1],
            ]
        )

        # Add translation
        rotation_matrix[:3, 3] = self.position
        return rotation_matrix


@dataclass
class VRController:
    """VR controller state."""

    device_id: int
    pose: VRPose
    buttons: Dict[str, bool] = field(default_factory=dict)
    axes: Dict[str, float] = field(default_factory=dict)
    trigger: float = 0.0
    grip: float = 0.0
    touchpad: Tuple[float, float] = (0.0, 0.0)
    is_connected: bool = False

    def is_button_pressed(self, button_name: str) -> bool:
        """Check if button is pressed."""
        return self.buttons.get(button_name, False)

    def get_axis_value(self, axis_name: str) -> float:
        """Get axis value."""
        return self.axes.get(axis_name, 0.0)


class VRRenderer:
    """VR-specific rendering system."""

    def __init__(self, device_type: VRDevice = VRDevice.GENERIC_OPENVR):
        self.device_type = device_type
        self.is_initialized = False
        self.render_width = 2160  # Per eye
        self.render_height = 1200  # Per eye

        # VR session state
        self.hmd_pose = VRPose()
        self.controllers: Dict[int, VRController] = {}
        self.tracking_space = TrackingSpace.ROOM_SCALE

        # Eye configurations
        self.left_eye = Eye(
            projection_matrix=np.eye(4),
            view_matrix=np.eye(4),
            viewport=(0, 0, self.render_width, self.render_height),
        )
        self.right_eye = Eye(
            projection_matrix=np.eye(4),
            view_matrix=np.eye(4),
            viewport=(self.render_width, 0, self.render_width, self.render_height),
        )

        # Rendering settings
        self.ipd = 0.064  # Interpupillary distance in meters
        self.near_plane = 0.1
        self.far_plane = 1000.0

        # Performance settings
        self.enable_reprojection = True
        self.enable_foveated_rendering = False
        self.supersampling_factor = 1.0

        # Event callbacks
        self.on_controller_connected: Optional[Callable[[VRController], None]] = None
        self.on_controller_disconnected: Optional[Callable[[int], None]] = None
        self.on_button_press: Optional[Callable[[int, str], None]] = None
        self.on_button_release: Optional[Callable[[int, str], None]] = None

    def initialize(self) -> bool:
        """Initialize VR system."""
        try:
            # Platform-specific initialization would go here
            if self.device_type == VRDevice.WEBXR:
                return self._initialize_webxr()
            elif self.device_type in [VRDevice.OCULUS_RIFT, VRDevice.OCULUS_QUEST]:
                return self._initialize_oculus()
            elif self.device_type in [VRDevice.HTC_VIVE, VRDevice.VALVE_INDEX]:
                return self._initialize_openvr()
            else:
                return self._initialize_generic()

        except Exception as e:
            print(f"VR initialization failed: {e}")
            return False

    def shutdown(self):
        """Shutdown VR system."""
        self.is_initialized = False
        self.controllers.clear()

    def update_poses(self):
        """Update all device poses."""
        if not self.is_initialized:
            return

        # Update HMD pose
        self._update_hmd_pose()

        # Update controller poses
        self._update_controller_poses()

        # Update eye matrices
        self._update_eye_matrices()

    def render_frame(self, render_func: Callable[[Eye], None]):
        """Render a VR frame for both eyes."""
        if not self.is_initialized:
            return

        # Render left eye
        self._setup_eye_rendering(self.left_eye)
        render_func(self.left_eye)

        # Render right eye
        self._setup_eye_rendering(self.right_eye)
        render_func(self.right_eye)

        # Submit frame to VR system
        self._submit_frame()

    def get_hmd_pose(self) -> VRPose:
        """Get current HMD pose."""
        return self.hmd_pose

    def get_controller(self, controller_id: int) -> Optional[VRController]:
        """Get controller by ID."""
        return self.controllers.get(controller_id)

    def get_all_controllers(self) -> List[VRController]:
        """Get all connected controllers."""
        return list(self.controllers.values())

    def set_tracking_space(self, tracking_space: TrackingSpace):
        """Set the tracking space type."""
        self.tracking_space = tracking_space

    def vibrate_controller(self, controller_id: int, intensity: float, duration: float):
        """Trigger haptic feedback on controller."""
        controller = self.controllers.get(controller_id)
        if controller and controller.is_connected:
            # Platform-specific haptic implementation
            self._trigger_haptics(controller_id, intensity, duration)

    def ray_from_controller(
        self, controller_id: int
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Get ray from controller position and orientation."""
        controller = self.controllers.get(controller_id)
        if not controller or not controller.is_connected:
            return None

        # Ray starts at controller position
        origin = controller.pose.position

        # Ray direction is forward from controller
        controller_matrix = controller.pose.to_matrix()
        direction = controller_matrix[:3, 2]  # Forward vector

        return origin, direction

    def _initialize_webxr(self) -> bool:
        """Initialize WebXR for browser-based VR."""
        # WebXR initialization would use JavaScript bindings
        self.is_initialized = True
        return True

    def _initialize_oculus(self) -> bool:
        """Initialize Oculus SDK."""
        # Oculus SDK initialization
        self.is_initialized = True
        return True

    def _initialize_openvr(self) -> bool:
        """Initialize OpenVR for SteamVR devices."""
        # OpenVR initialization
        self.is_initialized = True
        return True

    def _initialize_generic(self) -> bool:
        """Initialize generic VR system."""
        self.is_initialized = True
        return True

    def _update_hmd_pose(self):
        """Update HMD pose from VR system."""
        # Platform-specific pose tracking
        # For demo purposes, create a simple pose
        self.hmd_pose.position = np.array([0.0, 1.7, 0.0])  # Standing height
        self.hmd_pose.rotation = np.array([0.0, 0.0, 0.0, 1.0])  # No rotation
        self.hmd_pose.is_valid = True

    def _update_controller_poses(self):
        """Update controller poses from VR system."""
        # Mock controller data for demo
        if 0 not in self.controllers:
            self.controllers[0] = VRController(
                device_id=0,
                pose=VRPose(
                    position=np.array([-0.3, 1.2, -0.3]),
                    rotation=np.array([0.0, 0.0, 0.0, 1.0]),
                ),
                is_connected=True,
            )

        if 1 not in self.controllers:
            self.controllers[1] = VRController(
                device_id=1,
                pose=VRPose(
                    position=np.array([0.3, 1.2, -0.3]),
                    rotation=np.array([0.0, 0.0, 0.0, 1.0]),
                ),
                is_connected=True,
            )

    def _update_eye_matrices(self):
        """Update eye projection and view matrices."""
        hmd_matrix = self.hmd_pose.to_matrix()

        # Left eye offset
        left_eye_offset = np.array([-self.ipd / 2, 0, 0, 1])
        left_eye_pos = hmd_matrix @ left_eye_offset
        left_eye_matrix = hmd_matrix.copy()
        left_eye_matrix[:3, 3] = left_eye_pos[:3]

        # Right eye offset
        right_eye_offset = np.array([self.ipd / 2, 0, 0, 1])
        right_eye_pos = hmd_matrix @ right_eye_offset
        right_eye_matrix = hmd_matrix.copy()
        right_eye_matrix[:3, 3] = right_eye_pos[:3]

        # Update view matrices (inverse of eye matrices)
        self.left_eye.view_matrix = np.linalg.inv(left_eye_matrix)
        self.right_eye.view_matrix = np.linalg.inv(right_eye_matrix)

        # Update projection matrices
        aspect_ratio = self.render_width / self.render_height
        fov = math.radians(90)  # 90 degree FOV

        self.left_eye.projection_matrix = self._create_projection_matrix(
            fov, aspect_ratio
        )
        self.right_eye.projection_matrix = self._create_projection_matrix(
            fov, aspect_ratio
        )

    def _create_projection_matrix(self, fov: float, aspect_ratio: float) -> np.ndarray:
        """Create perspective projection matrix."""
        f = 1.0 / math.tan(fov / 2.0)
        return np.array(
            [
                [f / aspect_ratio, 0, 0, 0],
                [0, f, 0, 0],
                [
                    0,
                    0,
                    (self.far_plane + self.near_plane)
                    / (self.near_plane - self.far_plane),
                    (2 * self.far_plane * self.near_plane)
                    / (self.near_plane - self.far_plane),
                ],
                [0, 0, -1, 0],
            ]
        )

    def _setup_eye_rendering(self, eye: Eye):
        """Setup rendering for specific eye."""
        # Set viewport
        # This would integrate with the graphics API
        pass

    def _submit_frame(self):
        """Submit rendered frame to VR system."""
        # Submit to VR compositor
        pass

    def _trigger_haptics(self, controller_id: int, intensity: float, duration: float):
        """Trigger haptic feedback."""
        # Platform-specific haptic implementation
        pass


class ARRenderer:
    """AR-specific rendering system."""

    def __init__(self, device_type: ARDevice = ARDevice.ARCORE):
        self.device_type = device_type
        self.is_initialized = False

        # AR session state
        self.camera_pose = VRPose()
        self.camera_intrinsics = np.eye(3)
        self.render_width = 1920
        self.render_height = 1080

        # Tracking state
        self.is_tracking = False
        self.tracking_quality = 0.0

        # Detected planes and anchors
        self.detected_planes: List[Dict[str, Any]] = []
        self.anchors: Dict[str, VRPose] = {}

        # Lighting estimation
        self.ambient_light_intensity = 1.0
        self.light_direction = np.array([0, -1, 0])

    def initialize(self) -> bool:
        """Initialize AR system."""
        try:
            if self.device_type == ARDevice.ARCORE:
                return self._initialize_arcore()
            elif self.device_type == ARDevice.ARKIT:
                return self._initialize_arkit()
            elif self.device_type == ARDevice.WEBXR_AR:
                return self._initialize_webxr_ar()
            else:
                return self._initialize_generic_ar()

        except Exception as e:
            print(f"AR initialization failed: {e}")
            return False

    def update_tracking(self):
        """Update AR tracking state."""
        if not self.is_initialized:
            return

        # Update camera pose
        self._update_camera_pose()

        # Update plane detection
        self._update_plane_detection()

        # Update lighting estimation
        self._update_lighting_estimation()

    def render_frame(self, render_func: Callable[[np.ndarray, np.ndarray], None]):
        """Render AR frame with camera background."""
        if not self.is_initialized or not self.is_tracking:
            return

        # Get camera background
        self._render_camera_background()

        # Render 3D content
        view_matrix = np.linalg.inv(self.camera_pose.to_matrix())
        projection_matrix = self._get_camera_projection_matrix()

        render_func(view_matrix, projection_matrix)

    def hit_test(self, screen_x: float, screen_y: float) -> Optional[VRPose]:
        """Perform hit test against real world geometry."""
        # Convert screen coordinates to ray
        ray_origin, ray_direction = self._screen_to_ray(screen_x, screen_y)

        # Test against detected planes
        for plane in self.detected_planes:
            intersection = self._ray_plane_intersection(
                ray_origin, ray_direction, plane["center"], plane["normal"]
            )

            if intersection is not None:
                return VRPose(position=intersection)

        return None

    def create_anchor(self, pose: VRPose) -> str:
        """Create a tracking anchor at the given pose."""
        anchor_id = f"anchor_{len(self.anchors)}"
        self.anchors[anchor_id] = pose
        return anchor_id

    def remove_anchor(self, anchor_id: str):
        """Remove a tracking anchor."""
        self.anchors.pop(anchor_id, None)

    def get_detected_planes(self) -> List[Dict[str, Any]]:
        """Get all detected planes."""
        return self.detected_planes.copy()

    def _initialize_arcore(self) -> bool:
        """Initialize ARCore for Android."""
        self.is_initialized = True
        return True

    def _initialize_arkit(self) -> bool:
        """Initialize ARKit for iOS."""
        self.is_initialized = True
        return True

    def _initialize_webxr_ar(self) -> bool:
        """Initialize WebXR AR for browsers."""
        self.is_initialized = True
        return True

    def _initialize_generic_ar(self) -> bool:
        """Initialize generic AR system."""
        self.is_initialized = True
        return True

    def _update_camera_pose(self):
        """Update camera pose from AR tracking."""
        # Mock camera pose for demo
        self.camera_pose.position = np.array([0.0, 0.0, 0.0])
        self.camera_pose.rotation = np.array([0.0, 0.0, 0.0, 1.0])
        self.is_tracking = True
        self.tracking_quality = 1.0

    def _update_plane_detection(self):
        """Update detected plane information."""
        # Mock plane detection
        if not self.detected_planes:
            self.detected_planes.append(
                {
                    "id": "floor_plane",
                    "center": np.array([0.0, -1.0, -2.0]),
                    "normal": np.array([0.0, 1.0, 0.0]),
                    "extent": np.array([5.0, 5.0]),
                    "vertices": [],
                }
            )

    def _update_lighting_estimation(self):
        """Update environmental lighting estimation."""
        # Mock lighting estimation
        self.ambient_light_intensity = 0.8
        self.light_direction = np.array([0.3, -0.7, 0.2])

    def _render_camera_background(self):
        """Render camera feed as background."""
        # Platform-specific camera rendering
        pass

    def _get_camera_projection_matrix(self) -> np.ndarray:
        """Get camera projection matrix."""
        # Use camera intrinsics to create projection matrix
        fx, fy = self.camera_intrinsics[0, 0], self.camera_intrinsics[1, 1]
        cx, cy = self.camera_intrinsics[0, 2], self.camera_intrinsics[1, 2]

        near, far = 0.1, 100.0

        return np.array(
            [
                [2 * fx / self.render_width, 0, (2 * cx / self.render_width - 1), 0],
                [0, 2 * fy / self.render_height, (2 * cy / self.render_height - 1), 0],
                [0, 0, -(far + near) / (far - near), -2 * far * near / (far - near)],
                [0, 0, -1, 0],
            ]
        )

    def _screen_to_ray(
        self, screen_x: float, screen_y: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert screen coordinates to world ray."""
        # Convert to normalized device coordinates
        ndc_x = (2.0 * screen_x) / self.render_width - 1.0
        ndc_y = 1.0 - (2.0 * screen_y) / self.render_height

        # Create ray in camera space
        inv_projection = np.linalg.inv(self._get_camera_projection_matrix())
        ray_eye = inv_projection @ np.array([ndc_x, ndc_y, -1.0, 1.0])
        ray_eye = ray_eye[:3] / ray_eye[3]

        # Transform to world space
        camera_matrix = self.camera_pose.to_matrix()
        ray_world = camera_matrix[:3, :3] @ ray_eye
        ray_world = ray_world / np.linalg.norm(ray_world)

        return self.camera_pose.position, ray_world

    def _ray_plane_intersection(
        self,
        ray_origin: np.ndarray,
        ray_direction: np.ndarray,
        plane_center: np.ndarray,
        plane_normal: np.ndarray,
    ) -> Optional[np.ndarray]:
        """Calculate ray-plane intersection."""
        denom = np.dot(plane_normal, ray_direction)

        if abs(denom) < 1e-6:  # Ray parallel to plane
            return None

        t = np.dot(plane_center - ray_origin, plane_normal) / denom

        if t < 0:  # Intersection behind ray
            return None

        return ray_origin + t * ray_direction


class SpatialController:
    """Spatial interaction controller for VR/AR environments."""

    def __init__(
        self,
        vr_renderer: Optional[VRRenderer] = None,
        ar_renderer: Optional[ARRenderer] = None,
    ):
        self.vr_renderer = vr_renderer
        self.ar_renderer = ar_renderer

        # Interaction state
        self.is_vr_mode = vr_renderer is not None
        self.selected_objects: List[str] = []
        self.interaction_mode = "select"  # select, manipulate, create

        # Spatial gestures
        self.gesture_threshold = 0.1  # meters
        self.pinch_threshold = 0.05  # meters

    def update(self):
        """Update spatial interactions."""
        if self.is_vr_mode and self.vr_renderer:
            self._update_vr_interactions()
        elif self.ar_renderer:
            self._update_ar_interactions()

    def handle_controller_input(self, controller_id: int, button: str, pressed: bool):
        """Handle VR controller input."""
        if not self.vr_renderer:
            return

        controller = self.vr_renderer.get_controller(controller_id)
        if not controller:
            return

        if button == "trigger" and pressed:
            self._handle_trigger_press(controller)
        elif button == "grip" and pressed:
            self._handle_grip_press(controller)

    def handle_hand_tracking(self, hand_pose: VRPose, gesture: str):
        """Handle hand tracking input."""
        if gesture == "pinch":
            self._handle_pinch_gesture(hand_pose)
        elif gesture == "point":
            self._handle_point_gesture(hand_pose)
        elif gesture == "grab":
            self._handle_grab_gesture(hand_pose)

    def raycast_from_controller(self, controller_id: int) -> Optional[Dict[str, Any]]:
        """Perform raycast from VR controller."""
        if not self.vr_renderer:
            return None

        ray_data = self.vr_renderer.ray_from_controller(controller_id)
        if not ray_data:
            return None

        origin, direction = ray_data

        # Perform intersection tests
        # This would integrate with the scene graph
        return {
            "origin": origin,
            "direction": direction,
            "hit": False,
            "distance": 0.0,
            "object_id": None,
        }

    def place_object_in_ar(
        self, object_id: str, screen_x: float, screen_y: float
    ) -> bool:
        """Place object in AR scene using hit testing."""
        if not self.ar_renderer:
            return False

        hit_result = self.ar_renderer.hit_test(screen_x, screen_y)
        if hit_result:
            # Place object at hit location
            anchor_id = self.ar_renderer.create_anchor(hit_result)
            # Link object to anchor
            return True

        return False

    def _update_vr_interactions(self):
        """Update VR-specific interactions."""
        if not self.vr_renderer:
            return

        self.vr_renderer.update_poses()

        # Check for controller gestures
        for controller in self.vr_renderer.get_all_controllers():
            if controller.is_connected:
                self._process_controller_gestures(controller)

    def _update_ar_interactions(self):
        """Update AR-specific interactions."""
        if not self.ar_renderer:
            return

        self.ar_renderer.update_tracking()

    def _handle_trigger_press(self, controller: VRController):
        """Handle trigger button press."""
        # Perform selection or activation
        raycast_result = self.raycast_from_controller(controller.device_id)
        if raycast_result and raycast_result["hit"]:
            object_id = raycast_result["object_id"]
            if object_id:
                self.selected_objects.append(object_id)

    def _handle_grip_press(self, controller: VRController):
        """Handle grip button press."""
        # Start object manipulation
        self.interaction_mode = "manipulate"

    def _handle_pinch_gesture(self, hand_pose: VRPose):
        """Handle pinch gesture."""
        # Pinch-to-select or pinch-to-scale
        pass

    def _handle_point_gesture(self, hand_pose: VRPose):
        """Handle pointing gesture."""
        # UI interaction or object highlighting
        pass

    def _handle_grab_gesture(self, hand_pose: VRPose):
        """Handle grab gesture."""
        # Object manipulation
        pass

    def _process_controller_gestures(self, controller: VRController):
        """Process controller-based gestures."""
        # Analyze controller movement patterns for gestures
        pass
