"""WebXR integration for browser-based VR/AR visualization."""

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

import json
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import threading

logger = logging.getLogger(__name__)


@dataclass
class WebXRCapabilities:
    """WebXR session capabilities."""
    vr_supported: bool = False
    ar_supported: bool = False
    immersive_vr: bool = False
    immersive_ar: bool = False
    hand_tracking: bool = False
    eye_tracking: bool = False
    plane_detection: bool = False
    hit_testing: bool = False


@dataclass
class WebXRPose:
    """WebXR pose data."""
    position: List[float]  # [x, y, z]
    orientation: List[float]  # [x, y, z, w] quaternion
    linear_velocity: Optional[List[float]] = None
    angular_velocity: Optional[List[float]] = None
    timestamp: float = 0.0


@dataclass
class WebXRInputSource:
    """WebXR input source (controller, hand, etc.)."""
    source_id: str
    handedness: str  # "left", "right", "none"
    target_ray_mode: str  # "gaze", "tracked-pointer", "screen"
    grip_pose: Optional[WebXRPose] = None
    target_ray_pose: Optional[WebXRPose] = None
    profiles: List[str] = field(default_factory=list)
    gamepad: Optional[Dict] = None


class WebXRSession:
    """WebXR session manager for immersive web experiences."""

    def __init__(self, mode: str = "immersive-vr"):
        self.mode = mode  # "immersive-vr", "immersive-ar", "inline"
        self.is_active = False
        self.frame_rate = 90.0  # Target frame rate

        # Session state
        self.reference_space = None
        self.base_layer = None
        self.viewer_pose: Optional[WebXRPose] = None
        self.input_sources: Dict[str, WebXRInputSource] = {}

        # Event handlers
        self.on_session_start: Optional[Callable] = None
        self.on_session_end: Optional[Callable] = None
        self.on_input_change: Optional[Callable] = None
        self.on_frame: Optional[Callable] = None

        # Capabilities
        self.capabilities = WebXRCapabilities()

        # Visualization objects
        self.scene_objects: List[WebXRObject] = []
        self.charts: List[Dict] = []

        # Performance tracking
        self.frame_count = 0
        self.last_frame_time = 0.0
        self.current_fps = 0.0

    async def request_session(self, required_features: Optional[List[str]] = None,
                            optional_features: Optional[List[str]] = None) -> bool:
        """Request WebXR session with specified features."""
        required_features = required_features or []
        optional_features = optional_features or []

        logger.info(f"Requesting WebXR session: {self.mode}")
        logger.info(f"Required features: {required_features}")
        logger.info(f"Optional features: {optional_features}")

        # Simulate WebXR session request
        self.is_active = True

        # Update capabilities based on requested features
        self._update_capabilities(required_features + optional_features)

        if self.on_session_start:
            self.on_session_start(self)

        return True

    async def end_session(self):
        """End the WebXR session."""
        if self.is_active:
            self.is_active = False

            if self.on_session_end:
                self.on_session_end(self)

            logger.info("WebXR session ended")

    def add_chart(self, chart_data: Dict, transform: Optional[Dict] = None) -> str:
        """Add a chart to the WebXR scene."""
        chart_id = f"chart_{len(self.charts)}"

        webxr_chart = {
            'id': chart_id,
            'type': chart_data.get('type', 'unknown'),
            'data': chart_data,
            'transform': transform or {
                'position': [0, 1.5, -2],
                'rotation': [0, 0, 0, 1],
                'scale': [1, 1, 1]
            },
            'interactive': True,
            'visible': True
        }

        self.charts.append(webxr_chart)
        logger.info(f"Added chart {chart_id} to WebXR scene")

        return chart_id

    def update_chart(self, chart_id: str, data: Dict):
        """Update chart data in real-time."""
        for chart in self.charts:
            if chart['id'] == chart_id:
                chart['data'].update(data)
                break

    def remove_chart(self, chart_id: str):
        """Remove a chart from the scene."""
        self.charts = [chart for chart in self.charts if chart['id'] != chart_id]

    def set_reference_space(self, space_type: str = "local-floor"):
        """Set the reference space for tracking."""
        self.reference_space = space_type
        logger.info(f"Reference space set to: {space_type}")

    def update_viewer_pose(self, pose: WebXRPose):
        """Update the viewer's head pose."""
        self.viewer_pose = pose

    def update_input_source(self, source: WebXRInputSource):
        """Update input source state."""
        self.input_sources[source.source_id] = source

        if self.on_input_change:
            self.on_input_change(source)

    def render_frame(self, timestamp: float) -> Dict[str, Any]:
        """Render a WebXR frame."""
        self.frame_count += 1

        # Calculate FPS
        if self.last_frame_time > 0:
            delta_time = timestamp - self.last_frame_time
            if delta_time > 0:
                self.current_fps = 1000.0 / delta_time  # timestamp is in milliseconds

        self.last_frame_time = timestamp

        # Prepare frame data
        frame_data = {
            'timestamp': timestamp,
            'viewer_pose': self._pose_to_dict(self.viewer_pose) if self.viewer_pose else None,
            'input_sources': {
                source_id: self._input_source_to_dict(source)
                for source_id, source in self.input_sources.items()
            },
            'charts': self.charts,
            'scene_objects': [obj.to_dict() for obj in self.scene_objects],
            'frame_count': self.frame_count,
            'fps': self.current_fps
        }

        if self.on_frame:
            self.on_frame(frame_data)

        return frame_data

    def export_scene_gltf(self) -> Dict[str, Any]:
        """Export the WebXR scene as glTF for sharing."""
        gltf_scene = {
            'asset': {
                'version': '2.0',
                'generator': 'Vizly WebXR Exporter'
            },
            'scene': 0,
            'scenes': [{
                'name': 'Vizly VR Scene',
                'nodes': []
            }],
            'nodes': [],
            'meshes': [],
            'materials': [],
            'accessors': [],
            'bufferViews': [],
            'buffers': []
        }

        # Add charts as nodes
        for i, chart in enumerate(self.charts):
            node = {
                'name': f"Chart_{chart['id']}",
                'translation': chart['transform']['position'],
                'rotation': chart['transform']['rotation'],
                'scale': chart['transform']['scale'],
                'extras': {
                    'vizly_chart_data': chart['data']
                }
            }
            gltf_scene['nodes'].append(node)
            gltf_scene['scenes'][0]['nodes'].append(i)

        return gltf_scene

    def _update_capabilities(self, features: List[str]):
        """Update capabilities based on requested features."""
        for feature in features:
            if feature == "hand-tracking":
                self.capabilities.hand_tracking = True
            elif feature == "plane-detection":
                self.capabilities.plane_detection = True
            elif feature == "hit-test":
                self.capabilities.hit_testing = True
            elif feature == "eye-tracking":
                self.capabilities.eye_tracking = True

    def _pose_to_dict(self, pose: WebXRPose) -> Dict:
        """Convert pose to dictionary."""
        return {
            'position': pose.position,
            'orientation': pose.orientation,
            'linear_velocity': pose.linear_velocity,
            'angular_velocity': pose.angular_velocity,
            'timestamp': pose.timestamp
        }

    def _input_source_to_dict(self, source: WebXRInputSource) -> Dict:
        """Convert input source to dictionary."""
        return {
            'handedness': source.handedness,
            'target_ray_mode': source.target_ray_mode,
            'grip_pose': self._pose_to_dict(source.grip_pose) if source.grip_pose else None,
            'target_ray_pose': self._pose_to_dict(source.target_ray_pose) if source.target_ray_pose else None,
            'profiles': source.profiles,
            'gamepad': source.gamepad
        }


class WebXRObject:
    """Base class for objects in WebXR scenes."""

    def __init__(self, object_id: str, object_type: str = "generic"):
        self.object_id = object_id
        self.object_type = object_type
        self.transform = {
            'position': [0, 0, 0],
            'rotation': [0, 0, 0, 1],
            'scale': [1, 1, 1]
        }
        self.visible = True
        self.interactive = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary."""
        return {
            'id': self.object_id,
            'type': self.object_type,
            'transform': self.transform,
            'visible': self.visible,
            'interactive': self.interactive
        }


class WebXRServer:
    """HTTP server for WebXR applications."""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.is_running = False
        self.sessions: Dict[str, WebXRSession] = {}

        # Server state
        self.connected_clients = 0
        self.total_sessions = 0

    async def start_server(self):
        """Start the WebXR server."""
        self.is_running = True
        self.total_sessions = 0

        logger.info(f"Starting WebXR server on http://{self.host}:{self.port}")

        # In a real implementation, this would start an actual HTTP server
        print(f"🌐 WebXR Server Started!")
        print(f"   URL: http://{self.host}:{self.port}")
        print(f"   VR Entry: http://{self.host}:{self.port}/vr")
        print(f"   AR Entry: http://{self.host}:{self.port}/ar")
        print(f"   Desktop Preview: http://{self.host}:{self.port}/preview")

    async def stop_server(self):
        """Stop the WebXR server."""
        self.is_running = False

        # End all active sessions
        for session in self.sessions.values():
            await session.end_session()

        self.sessions.clear()
        logger.info("WebXR server stopped")

    def create_session(self, session_id: str, mode: str = "immersive-vr") -> WebXRSession:
        """Create a new WebXR session."""
        session = WebXRSession(mode)
        self.sessions[session_id] = session
        self.total_sessions += 1

        logger.info(f"Created WebXR session {session_id} in {mode} mode")
        return session

    def get_session(self, session_id: str) -> Optional[WebXRSession]:
        """Get existing session."""
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        """Remove a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def generate_webxr_html(self, session_id: str, mode: str = "vr") -> str:
        """Generate HTML page for WebXR session."""
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Vizly WebXR - {mode.upper()} Visualization</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/three@0.150.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.150.0/examples/js/webxr/VRButton.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.150.0/examples/js/webxr/ARButton.js"></script>
    <style>
        body {{ margin: 0; background: #000; color: #fff; font-family: Arial; }}
        #info {{ position: absolute; top: 10px; left: 10px; z-index: 100; }}
        #container {{ width: 100%; height: 100vh; }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Vizly {mode.upper()} Visualization</h3>
        <p>Session: {session_id}</p>
        <p>Use {mode.upper()} device or desktop preview</p>
    </div>
    <div id="container"></div>

    <script>
        // Vizly WebXR initialization
        let scene, camera, renderer, session;

        function init() {{
            // Create Three.js scene
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.xr.enabled = true;

            document.getElementById('container').appendChild(renderer.domElement);

            // Add {mode.upper()} button
            {'document.body.appendChild(VRButton.createButton(renderer));' if mode == 'vr' else 'document.body.appendChild(ARButton.createButton(renderer));'}

            // Setup basic scene
            const geometry = new THREE.BoxGeometry();
            const material = new THREE.MeshBasicMaterial({{ color: 0x00ff00 }});
            const cube = new THREE.Mesh(geometry, material);
            cube.position.set(0, 1.5, -2);
            scene.add(cube);

            // Start render loop
            renderer.setAnimationLoop(animate);
        }}

        function animate() {{
            renderer.render(scene, camera);
        }}

        // Initialize when page loads
        init();

        // Connect to Vizly WebXR session
        console.log('Vizly WebXR session {session_id} initialized in {mode} mode');
    </script>
</body>
</html>
        """

        return html_template.strip()

    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            'running': self.is_running,
            'host': self.host,
            'port': self.port,
            'active_sessions': len(self.sessions),
            'total_sessions': self.total_sessions,
            'connected_clients': self.connected_clients,
            'session_modes': [session.mode for session in self.sessions.values()]
        }