"""
Advanced 3D Interaction System for Vizly
========================================

Comprehensive 3D visualization, interaction, and VR/AR capabilities.
Supports WebGL, physics simulation, and immersive environments.
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
import time
import threading
import json
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

# Optional dependencies
try:
    import socketio
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False


@dataclass
class Vector3:
    """3D vector representation."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def magnitude(self) -> float:
        return np.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self) -> 'Vector3':
        mag = self.magnitude()
        if mag == 0:
            return Vector3()
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def dot(self, other: 'Vector3') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vector3') -> 'Vector3':
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'Vector3':
        return cls(float(arr[0]), float(arr[1]), float(arr[2]))


@dataclass
class Transform3D:
    """3D transformation matrix representation."""
    position: Vector3 = None
    rotation: Vector3 = None  # Euler angles in radians
    scale: Vector3 = None

    def __post_init__(self):
        if self.position is None:
            self.position = Vector3()
        if self.rotation is None:
            self.rotation = Vector3()
        if self.scale is None:
            self.scale = Vector3(1.0, 1.0, 1.0)

    def to_matrix(self) -> np.ndarray:
        """Convert to 4x4 transformation matrix."""
        # Translation matrix
        T = np.eye(4)
        T[0:3, 3] = [self.position.x, self.position.y, self.position.z]

        # Rotation matrices
        cos_x, sin_x = np.cos(self.rotation.x), np.sin(self.rotation.x)
        cos_y, sin_y = np.cos(self.rotation.y), np.sin(self.rotation.y)
        cos_z, sin_z = np.cos(self.rotation.z), np.sin(self.rotation.z)

        Rx = np.array([
            [1, 0, 0, 0],
            [0, cos_x, -sin_x, 0],
            [0, sin_x, cos_x, 0],
            [0, 0, 0, 1]
        ])

        Ry = np.array([
            [cos_y, 0, sin_y, 0],
            [0, 1, 0, 0],
            [-sin_y, 0, cos_y, 0],
            [0, 0, 0, 1]
        ])

        Rz = np.array([
            [cos_z, -sin_z, 0, 0],
            [sin_z, cos_z, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # Scale matrix
        S = np.eye(4)
        S[0, 0] = self.scale.x
        S[1, 1] = self.scale.y
        S[2, 2] = self.scale.z

        # Combine transformations: T * Rz * Ry * Rx * S
        return T @ Rz @ Ry @ Rx @ S


class Object3D(ABC):
    """Abstract base class for 3D objects."""

    def __init__(self, name: str, transform: Transform3D = None):
        self.name = name
        self.transform = transform or Transform3D()
        self.visible = True
        self.interactive = True
        self.properties: Dict[str, Any] = {}
        self.children: List['Object3D'] = []
        self.parent: Optional['Object3D'] = None

    @abstractmethod
    def get_vertices(self) -> np.ndarray:
        """Get object vertices in local coordinates."""
        pass

    @abstractmethod
    def get_faces(self) -> np.ndarray:
        """Get object face indices."""
        pass

    def get_world_vertices(self) -> np.ndarray:
        """Get object vertices in world coordinates."""
        vertices = self.get_vertices()
        if vertices.size == 0:
            return vertices

        # Convert to homogeneous coordinates
        ones = np.ones((vertices.shape[0], 1))
        vertices_h = np.hstack([vertices, ones])

        # Apply transformation
        transform_matrix = self.transform.to_matrix()
        world_vertices_h = (transform_matrix @ vertices_h.T).T

        return world_vertices_h[:, :3]

    def add_child(self, child: 'Object3D'):
        """Add child object."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: 'Object3D'):
        """Remove child object."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def get_bounds(self) -> Tuple[Vector3, Vector3]:
        """Get object bounding box in world coordinates."""
        vertices = self.get_world_vertices()
        if vertices.size == 0:
            return Vector3(), Vector3()

        min_bounds = Vector3.from_array(np.min(vertices, axis=0))
        max_bounds = Vector3.from_array(np.max(vertices, axis=0))
        return min_bounds, max_bounds


class Mesh3D(Object3D):
    """3D mesh object."""

    def __init__(self, name: str, vertices: np.ndarray, faces: np.ndarray,
                 transform: Transform3D = None):
        super().__init__(name, transform)
        self._vertices = vertices
        self._faces = faces
        self.material_properties = {
            'color': [0.7, 0.7, 0.7, 1.0],
            'metallic': 0.0,
            'roughness': 0.5,
            'emission': [0.0, 0.0, 0.0]
        }

    def get_vertices(self) -> np.ndarray:
        return self._vertices

    def get_faces(self) -> np.ndarray:
        return self._faces

    def set_color(self, color: Union[str, List[float]]):
        """Set mesh color."""
        if isinstance(color, str):
            # Convert color name to RGB
            color_map = {
                'red': [1.0, 0.0, 0.0, 1.0],
                'green': [0.0, 1.0, 0.0, 1.0],
                'blue': [0.0, 0.0, 1.0, 1.0],
                'white': [1.0, 1.0, 1.0, 1.0],
                'black': [0.0, 0.0, 0.0, 1.0],
                'yellow': [1.0, 1.0, 0.0, 1.0],
                'cyan': [0.0, 1.0, 1.0, 1.0],
                'magenta': [1.0, 0.0, 1.0, 1.0],
            }
            self.material_properties['color'] = color_map.get(color, [0.7, 0.7, 0.7, 1.0])
        else:
            self.material_properties['color'] = list(color)


class Camera3D:
    """3D camera for rendering and interaction."""

    def __init__(self, position: Vector3 = None, target: Vector3 = None,
                 up: Vector3 = None):
        self.position = position or Vector3(0, 0, 5)
        self.target = target or Vector3(0, 0, 0)
        self.up = up or Vector3(0, 1, 0)

        # Camera parameters
        self.fov = 75.0  # Field of view in degrees
        self.near = 0.1
        self.far = 1000.0
        self.aspect_ratio = 16.0 / 9.0

    def get_view_matrix(self) -> np.ndarray:
        """Get view matrix for camera."""
        forward = (self.target - self.position).normalize()
        right = forward.cross(self.up).normalize()
        up = right.cross(forward).normalize()

        view = np.eye(4)
        view[0, :3] = right.to_array()
        view[1, :3] = up.to_array()
        view[2, :3] = (-forward).to_array()

        translation = np.eye(4)
        translation[0:3, 3] = (-self.position).to_array()

        return view @ translation

    def get_projection_matrix(self) -> np.ndarray:
        """Get perspective projection matrix."""
        fov_rad = np.radians(self.fov)
        f = 1.0 / np.tan(fov_rad / 2.0)

        projection = np.zeros((4, 4))
        projection[0, 0] = f / self.aspect_ratio
        projection[1, 1] = f
        projection[2, 2] = (self.far + self.near) / (self.near - self.far)
        projection[2, 3] = (2 * self.far * self.near) / (self.near - self.far)
        projection[3, 2] = -1.0

        return projection

    def orbit(self, theta: float, phi: float, radius: float):
        """Orbit camera around target."""
        x = radius * np.sin(phi) * np.cos(theta)
        y = radius * np.cos(phi)
        z = radius * np.sin(phi) * np.sin(theta)

        self.position = Vector3(x, y, z) + self.target

    def look_at(self, target: Vector3):
        """Point camera at target."""
        self.target = target


class PhysicsBody:
    """Simple physics body for 3D objects."""

    def __init__(self, obj: Object3D, mass: float = 1.0, is_static: bool = False):
        self.object = obj
        self.mass = mass
        self.is_static = is_static

        # Physics properties
        self.velocity = Vector3()
        self.angular_velocity = Vector3()
        self.force = Vector3()
        self.torque = Vector3()

        # Material properties
        self.restitution = 0.5  # Bounciness
        self.friction = 0.3
        self.damping = 0.98

    def apply_force(self, force: Vector3):
        """Apply force to the body."""
        if not self.is_static:
            self.force = self.force + force

    def apply_impulse(self, impulse: Vector3):
        """Apply instantaneous impulse."""
        if not self.is_static:
            self.velocity = self.velocity + impulse * (1.0 / self.mass)

    def update(self, dt: float):
        """Update physics simulation."""
        if self.is_static:
            return

        # Apply forces
        acceleration = self.force * (1.0 / self.mass)
        self.velocity = self.velocity + acceleration * dt

        # Apply damping
        self.velocity = self.velocity * self.damping
        self.angular_velocity = self.angular_velocity * self.damping

        # Update position
        displacement = self.velocity * dt
        self.object.transform.position = self.object.transform.position + displacement

        # Update rotation
        angular_displacement = self.angular_velocity * dt
        self.object.transform.rotation = self.object.transform.rotation + angular_displacement

        # Reset forces
        self.force = Vector3()
        self.torque = Vector3()


class Scene3D:
    """3D scene container and manager."""

    def __init__(self, name: str = "Scene"):
        self.name = name
        self.objects: Dict[str, Object3D] = {}
        self.lights: List[Dict[str, Any]] = []
        self.cameras: Dict[str, Camera3D] = {}
        self.active_camera = "default"
        self.physics_bodies: Dict[str, PhysicsBody] = {}

        # Scene properties
        self.background_color = [0.1, 0.1, 0.1, 1.0]
        self.ambient_light = [0.2, 0.2, 0.2]
        self.gravity = Vector3(0, -9.81, 0)

        # Add default camera
        self.cameras["default"] = Camera3D()

        # Add default lighting
        self.add_directional_light(
            direction=Vector3(-1, -1, -1),
            color=[1.0, 1.0, 1.0],
            intensity=1.0
        )

    def add_object(self, obj: Object3D):
        """Add object to scene."""
        self.objects[obj.name] = obj

    def remove_object(self, name: str):
        """Remove object from scene."""
        if name in self.objects:
            del self.objects[name]
        if name in self.physics_bodies:
            del self.physics_bodies[name]

    def get_object(self, name: str) -> Optional[Object3D]:
        """Get object by name."""
        return self.objects.get(name)

    def add_camera(self, name: str, camera: Camera3D):
        """Add camera to scene."""
        self.cameras[name] = camera

    def set_active_camera(self, name: str):
        """Set active camera."""
        if name in self.cameras:
            self.active_camera = name

    def get_active_camera(self) -> Camera3D:
        """Get currently active camera."""
        return self.cameras[self.active_camera]

    def add_directional_light(self, direction: Vector3, color: List[float],
                            intensity: float = 1.0):
        """Add directional light."""
        light = {
            'type': 'directional',
            'direction': direction.to_array().tolist(),
            'color': color,
            'intensity': intensity
        }
        self.lights.append(light)

    def add_point_light(self, position: Vector3, color: List[float],
                       intensity: float = 1.0, range_limit: float = 100.0):
        """Add point light."""
        light = {
            'type': 'point',
            'position': position.to_array().tolist(),
            'color': color,
            'intensity': intensity,
            'range': range_limit
        }
        self.lights.append(light)

    def add_physics_body(self, obj: Object3D, mass: float = 1.0,
                        is_static: bool = False):
        """Add physics body to object."""
        body = PhysicsBody(obj, mass, is_static)
        self.physics_bodies[obj.name] = body

    def update_physics(self, dt: float):
        """Update physics simulation."""
        # Apply gravity
        for body in self.physics_bodies.values():
            if not body.is_static:
                gravity_force = self.gravity * body.mass
                body.apply_force(gravity_force)

        # Update all bodies
        for body in self.physics_bodies.values():
            body.update(dt)

    def raycast(self, origin: Vector3, direction: Vector3) -> Optional[Tuple[Object3D, Vector3]]:
        """Perform raycast against scene objects."""
        direction = direction.normalize()
        closest_hit = None
        closest_distance = float('inf')

        for obj in self.objects.values():
            if not obj.interactive:
                continue

            # Simple sphere collision for now
            center = obj.transform.position
            radius = 1.0  # Default radius

            # Ray-sphere intersection
            oc = origin - center
            a = direction.dot(direction)
            b = 2.0 * oc.dot(direction)
            c = oc.dot(oc) - radius * radius

            discriminant = b * b - 4 * a * c
            if discriminant >= 0:
                t = (-b - np.sqrt(discriminant)) / (2 * a)
                if 0 < t < closest_distance:
                    closest_distance = t
                    hit_point = origin + direction * t
                    closest_hit = (obj, hit_point)

        return closest_hit

    def to_dict(self) -> Dict[str, Any]:
        """Export scene to dictionary for serialization."""
        scene_data = {
            'name': self.name,
            'background_color': self.background_color,
            'ambient_light': self.ambient_light,
            'lights': self.lights,
            'objects': [],
            'cameras': {}
        }

        # Export objects
        for obj in self.objects.values():
            obj_data = {
                'name': obj.name,
                'type': obj.__class__.__name__,
                'transform': {
                    'position': obj.transform.position.to_array().tolist(),
                    'rotation': obj.transform.rotation.to_array().tolist(),
                    'scale': obj.transform.scale.to_array().tolist()
                },
                'visible': obj.visible,
                'interactive': obj.interactive,
                'properties': obj.properties
            }

            if isinstance(obj, Mesh3D):
                obj_data['material'] = obj.material_properties

            scene_data['objects'].append(obj_data)

        # Export cameras
        for name, camera in self.cameras.items():
            scene_data['cameras'][name] = {
                'position': camera.position.to_array().tolist(),
                'target': camera.target.to_array().tolist(),
                'up': camera.up.to_array().tolist(),
                'fov': camera.fov,
                'near': camera.near,
                'far': camera.far,
                'aspect_ratio': camera.aspect_ratio
            }

        return scene_data


class InteractionManager:
    """Manages 3D interactions and events."""

    def __init__(self, scene: Scene3D):
        self.scene = scene
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.selected_objects: List[Object3D] = []
        self.interaction_mode = "select"  # "select", "move", "rotate", "scale"

    def on(self, event: str, handler: Callable):
        """Register event handler."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def emit(self, event: str, data: Any = None):
        """Emit event to handlers."""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

    def handle_click(self, screen_pos: Tuple[float, float],
                    viewport_size: Tuple[int, int]):
        """Handle mouse click."""
        # Convert screen coordinates to ray
        camera = self.scene.get_active_camera()
        ray_origin, ray_direction = self._screen_to_ray(
            screen_pos, viewport_size, camera
        )

        # Perform raycast
        hit = self.scene.raycast(ray_origin, ray_direction)

        if hit:
            obj, hit_point = hit
            self.select_object(obj)
            self.emit('object_clicked', {
                'object': obj,
                'hit_point': hit_point.to_array().tolist(),
                'screen_pos': screen_pos
            })
        else:
            self.clear_selection()
            self.emit('background_clicked', {
                'screen_pos': screen_pos
            })

    def select_object(self, obj: Object3D):
        """Select an object."""
        if obj not in self.selected_objects:
            self.selected_objects.append(obj)
            self.emit('object_selected', obj)

    def deselect_object(self, obj: Object3D):
        """Deselect an object."""
        if obj in self.selected_objects:
            self.selected_objects.remove(obj)
            self.emit('object_deselected', obj)

    def clear_selection(self):
        """Clear all selections."""
        for obj in self.selected_objects:
            self.emit('object_deselected', obj)
        self.selected_objects.clear()

    def _screen_to_ray(self, screen_pos: Tuple[float, float],
                      viewport_size: Tuple[int, int],
                      camera: Camera3D) -> Tuple[Vector3, Vector3]:
        """Convert screen coordinates to world space ray."""
        # Normalize screen coordinates to [-1, 1]
        x = (2.0 * screen_pos[0]) / viewport_size[0] - 1.0
        y = 1.0 - (2.0 * screen_pos[1]) / viewport_size[1]

        # Create ray in clip space
        ray_clip = np.array([x, y, -1.0, 1.0])

        # Transform to eye space
        proj_inv = np.linalg.inv(camera.get_projection_matrix())
        ray_eye = proj_inv @ ray_clip
        ray_eye = np.array([ray_eye[0], ray_eye[1], -1.0, 0.0])

        # Transform to world space
        view_inv = np.linalg.inv(camera.get_view_matrix())
        ray_world = view_inv @ ray_eye

        ray_direction = Vector3.from_array(ray_world[:3]).normalize()

        return camera.position, ray_direction


class Advanced3DScene:
    """Advanced 3D scene with physics, interactions, and WebGL export."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.scene = Scene3D("Advanced3DScene")
        self.interaction_manager = InteractionManager(self.scene)

        # Rendering settings
        self.render_settings = {
            'antialias': True,
            'shadows': True,
            'post_processing': True,
            'wireframe': False,
            'show_grid': True,
            'show_axes': True
        }

        # Animation
        self.animation_frame = 0
        self.animation_speed = 1.0
        self.is_animating = False
        self._animation_thread = None

        # Performance monitoring
        self.frame_times = []
        self.max_frame_history = 60

    def add_cube(self, name: str, position: Vector3 = None, size: float = 1.0,
                color: str = "blue") -> Mesh3D:
        """Add a cube to the scene."""
        # Create cube vertices
        s = size / 2
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],  # Back face
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]        # Front face
        ])

        # Create cube faces (triangles)
        faces = np.array([
            [0, 1, 2], [2, 3, 0],  # Back
            [4, 7, 6], [6, 5, 4],  # Front
            [0, 4, 5], [5, 1, 0],  # Bottom
            [2, 6, 7], [7, 3, 2],  # Top
            [0, 3, 7], [7, 4, 0],  # Left
            [1, 5, 6], [6, 2, 1]   # Right
        ])

        transform = Transform3D(position=position or Vector3())
        cube = Mesh3D(name, vertices, faces, transform)
        cube.set_color(color)

        self.scene.add_object(cube)
        return cube

    def add_sphere(self, name: str, position: Vector3 = None, radius: float = 1.0,
                  color: str = "red", resolution: int = 16) -> Mesh3D:
        """Add a sphere to the scene."""
        vertices = []
        faces = []

        # Generate sphere vertices
        for i in range(resolution + 1):
            lat = np.pi * (-0.5 + float(i) / resolution)
            for j in range(resolution):
                lon = 2 * np.pi * float(j) / resolution

                x = radius * np.cos(lat) * np.cos(lon)
                y = radius * np.sin(lat)
                z = radius * np.cos(lat) * np.sin(lon)

                vertices.append([x, y, z])

        # Generate sphere faces
        for i in range(resolution):
            for j in range(resolution):
                first = i * resolution + j
                second = first + resolution

                faces.append([first, second, first + 1])
                faces.append([second, second + 1, first + 1])

        vertices = np.array(vertices)
        faces = np.array(faces)

        transform = Transform3D(position=position or Vector3())
        sphere = Mesh3D(name, vertices, faces, transform)
        sphere.set_color(color)

        self.scene.add_object(sphere)
        return sphere

    def add_interactive_object(self, obj_type: str, name: str = None,
                             position: Vector3 = None, **kwargs) -> Object3D:
        """Add an interactive object to the scene."""
        if name is None:
            name = f"{obj_type}_{len(self.scene.objects)}"

        if obj_type == "cube":
            obj = self.add_cube(name, position, **kwargs)
        elif obj_type == "sphere":
            obj = self.add_sphere(name, position, **kwargs)
        else:
            raise ValueError(f"Unknown object type: {obj_type}")

        # Make object interactive
        obj.interactive = True
        obj.properties['created_time'] = time.time()

        return obj

    def enable_physics(self, gravity: Vector3 = None):
        """Enable physics simulation."""
        if gravity:
            self.scene.gravity = gravity

        # Add physics bodies to existing objects
        for obj in self.scene.objects.values():
            if obj.name not in self.scene.physics_bodies:
                self.scene.add_physics_body(obj, mass=1.0, is_static=False)

    def add_ground_plane(self, size: float = 20.0) -> Mesh3D:
        """Add ground plane for physics."""
        vertices = np.array([
            [-size, 0, -size], [size, 0, -size],
            [size, 0, size], [-size, 0, size]
        ])
        faces = np.array([[0, 1, 2], [2, 3, 0]])

        ground = Mesh3D("ground", vertices, faces)
        ground.set_color("gray")
        ground.interactive = False

        self.scene.add_object(ground)
        self.scene.add_physics_body(ground, mass=0.0, is_static=True)

        return ground

    def start_animation(self):
        """Start animation loop."""
        if self.is_animating:
            return

        self.is_animating = True
        self._animation_thread = threading.Thread(target=self._animation_loop)
        self._animation_thread.daemon = True
        self._animation_thread.start()

    def stop_animation(self):
        """Stop animation loop."""
        self.is_animating = False
        if self._animation_thread:
            self._animation_thread.join()

    def _animation_loop(self):
        """Main animation loop."""
        last_time = time.time()

        while self.is_animating:
            current_time = time.time()
            dt = (current_time - last_time) * self.animation_speed
            last_time = current_time

            # Update physics
            self.scene.update_physics(dt)

            # Update animation frame
            self.animation_frame += 1

            # Track performance
            self.frame_times.append(dt)
            if len(self.frame_times) > self.max_frame_history:
                self.frame_times.pop(0)

            # Target 60 FPS
            time.sleep(max(0, 1.0/60.0 - dt))

    def set_camera_orbit(self, theta: float, phi: float, radius: float):
        """Set camera to orbit position."""
        camera = self.scene.get_active_camera()
        camera.orbit(theta, phi, radius)

    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics."""
        if not self.frame_times:
            return {'fps': 0.0, 'frame_time': 0.0}

        avg_frame_time = np.mean(self.frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0

        return {
            'fps': fps,
            'frame_time': avg_frame_time * 1000,  # in milliseconds
            'objects': len(self.scene.objects),
            'physics_bodies': len(self.scene.physics_bodies)
        }

    def export_webgl_scene(self) -> Dict[str, Any]:
        """Export scene for WebGL rendering."""
        scene_data = self.scene.to_dict()
        scene_data.update({
            'width': self.width,
            'height': self.height,
            'render_settings': self.render_settings,
            'animation_frame': self.animation_frame
        })
        return scene_data

    def save_scene(self, filename: str):
        """Save scene to JSON file."""
        scene_data = self.export_webgl_scene()
        with open(filename, 'w') as f:
            json.dump(scene_data, f, indent=2)

    def load_scene(self, filename: str):
        """Load scene from JSON file."""
        with open(filename, 'r') as f:
            scene_data = json.load(f)

        # Reconstruct scene from data
        self.scene = Scene3D(scene_data.get('name', 'LoadedScene'))

        # Load objects
        for obj_data in scene_data.get('objects', []):
            # This would need more sophisticated object reconstruction
            # For now, just log the loaded objects
            logger.info(f"Would load object: {obj_data['name']}")

    def create_data_visualization(self, data: np.ndarray, chart_type: str = "scatter3d"):
        """Create 3D data visualization from numpy array."""
        if chart_type == "scatter3d" and data.shape[1] >= 3:
            for i, point in enumerate(data):
                self.add_sphere(
                    f"data_point_{i}",
                    Vector3(float(point[0]), float(point[1]), float(point[2])),
                    radius=0.1,
                    color="blue"
                )
        elif chart_type == "surface3d" and data.ndim == 2:
            # Create surface from 2D data
            rows, cols = data.shape
            for i in range(rows - 1):
                for j in range(cols - 1):
                    # Create small plane segment
                    vertices = np.array([
                        [i, data[i, j], j],
                        [i+1, data[i+1, j], j],
                        [i+1, data[i+1, j+1], j+1],
                        [i, data[i, j+1], j+1]
                    ])
                    faces = np.array([[0, 1, 2], [2, 3, 0]])

                    segment = Mesh3D(f"surface_{i}_{j}", vertices, faces)
                    segment.set_color("green")
                    self.scene.add_object(segment)

    def start(self):
        """Start the 3D scene (for compatibility)."""
        logger.info("Advanced 3D Scene started")
        logger.info(f"Scene contains {len(self.scene.objects)} objects")
        logger.info(f"Resolution: {self.width}x{self.height}")
        logger.info("Use .start_animation() to begin physics simulation")
        logger.info("Use .export_webgl_scene() to get WebGL-compatible data")


# Utility functions for creating common objects
def create_cube(size: float = 1.0, color: str = "blue") -> Mesh3D:
    """Create a cube mesh."""
    scene = Advanced3DScene()
    return scene.add_cube("cube", size=size, color=color)

def create_sphere(radius: float = 1.0, color: str = "red") -> Mesh3D:
    """Create a sphere mesh."""
    scene = Advanced3DScene()
    return scene.add_sphere("sphere", radius=radius, color=color)

def create_scene_from_data(data: np.ndarray, chart_type: str = "scatter3d") -> Advanced3DScene:
    """Create 3D scene from data array."""
    scene = Advanced3DScene()
    scene.create_data_visualization(data, chart_type)
    return scene