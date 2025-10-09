"""
3D Scene Management System
Provides scene graph, object management, and rendering coordination.
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
from typing import List, Dict, Optional, Any, Callable, Tuple
from abc import ABC, abstractmethod

from .camera import CameraController, OrbitController
from .manipulation import Transform3D, ObjectManipulator, TransformMode
from .selection import SelectionManager


class Object3D(ABC):
    """Base class for all 3D objects in the scene."""

    def __init__(self, name: str = None, transform: Transform3D = None):
        self.name = name or f"Object3D_{id(self)}"
        self.transform = transform or Transform3D()
        self.visible = True
        self.selected = False
        self.material_properties = {}

        # Bounding box
        self._bounds_cache = None
        self._bounds_dirty = True

    @abstractmethod
    def get_geometry(self) -> Dict[str, Any]:
        """Get geometry data for rendering."""
        pass

    @abstractmethod
    def get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get axis-aligned bounding box (min, max)."""
        pass

    def set_position(self, position: np.ndarray):
        """Set object position."""
        self.transform.set_position(position)
        self._bounds_dirty = True

    def set_rotation(self, rotation: np.ndarray):
        """Set object rotation (Euler angles)."""
        self.transform.set_rotation(rotation)
        self._bounds_dirty = True

    def set_scale(self, scale: np.ndarray):
        """Set object scale."""
        self.transform.set_scale(scale)
        self._bounds_dirty = True

    def translate(self, offset: np.ndarray):
        """Translate object by offset."""
        self.transform.translate(offset)
        self._bounds_dirty = True

    def rotate(self, angles: np.ndarray):
        """Rotate object by angles."""
        self.transform.rotate(angles)
        self._bounds_dirty = True

    def scale_by(self, factors: np.ndarray):
        """Scale object by factors."""
        self.transform.scale_by(factors)
        self._bounds_dirty = True

    def set_material_property(self, property_name: str, value: Any):
        """Set material property."""
        self.material_properties[property_name] = value

    def get_material_property(self, property_name: str, default: Any = None):
        """Get material property."""
        return self.material_properties.get(property_name, default)


class Cube(Object3D):
    """3D Cube primitive."""

    def __init__(
        self, name: str = None, position: np.ndarray = None, size: float = 1.0
    ):
        transform = Transform3D()
        if position is not None:
            transform.set_position(position)

        super().__init__(name or "Cube", transform)
        self.size = size

        # Default material properties
        self.material_properties = {
            "color": np.array([0.8, 0.8, 0.8]),
            "wireframe": False,
            "opacity": 1.0,
        }

    def get_geometry(self) -> Dict[str, Any]:
        """Get cube geometry data."""
        half_size = self.size / 2.0

        # Cube vertices
        vertices = np.array(
            [
                [-half_size, -half_size, -half_size],  # 0
                [half_size, -half_size, -half_size],  # 1
                [half_size, half_size, -half_size],  # 2
                [-half_size, half_size, -half_size],  # 3
                [-half_size, -half_size, half_size],  # 4
                [half_size, -half_size, half_size],  # 5
                [half_size, half_size, half_size],  # 6
                [-half_size, half_size, half_size],  # 7
            ]
        )

        # Transform vertices
        transformed_vertices = []
        for vertex in vertices:
            transformed_vertex = self.transform.transform_point(vertex)
            transformed_vertices.append(transformed_vertex)

        # Cube faces (triangulated)
        faces = np.array(
            [
                # Front face
                [0, 1, 2],
                [0, 2, 3],
                # Back face
                [4, 7, 6],
                [4, 6, 5],
                # Left face
                [0, 3, 7],
                [0, 7, 4],
                # Right face
                [1, 5, 6],
                [1, 6, 2],
                # Top face
                [3, 2, 6],
                [3, 6, 7],
                # Bottom face
                [0, 4, 5],
                [0, 5, 1],
            ]
        )

        # Face normals
        normals = np.array(
            [
                [0, 0, -1],
                [0, 0, -1],  # Front
                [0, 0, 1],
                [0, 0, 1],  # Back
                [-1, 0, 0],
                [-1, 0, 0],  # Left
                [1, 0, 0],
                [1, 0, 0],  # Right
                [0, 1, 0],
                [0, 1, 0],  # Top
                [0, -1, 0],
                [0, -1, 0],  # Bottom
            ]
        )

        # Transform normals
        transformed_normals = []
        for normal in normals:
            transformed_normal = self.transform.transform_normal(normal)
            transformed_normals.append(transformed_normal)

        return {
            "type": "mesh",
            "vertices": np.array(transformed_vertices),
            "faces": faces,
            "normals": np.array(transformed_normals),
            "material": self.material_properties,
        }

    def get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get cube bounding box."""
        if not self._bounds_dirty and self._bounds_cache is not None:
            return self._bounds_cache

        half_size = self.size / 2.0
        corners = np.array(
            [
                [-half_size, -half_size, -half_size],
                [half_size, -half_size, -half_size],
                [half_size, half_size, -half_size],
                [-half_size, half_size, -half_size],
                [-half_size, -half_size, half_size],
                [half_size, -half_size, half_size],
                [half_size, half_size, half_size],
                [-half_size, half_size, half_size],
            ]
        )

        # Transform corners
        transformed_corners = []
        for corner in corners:
            transformed_corner = self.transform.transform_point(corner)
            transformed_corners.append(transformed_corner)

        transformed_corners = np.array(transformed_corners)

        min_bounds = np.min(transformed_corners, axis=0)
        max_bounds = np.max(transformed_corners, axis=0)

        self._bounds_cache = (min_bounds, max_bounds)
        self._bounds_dirty = False

        return self._bounds_cache


class Sphere(Object3D):
    """3D Sphere primitive."""

    def __init__(
        self,
        name: str = None,
        position: np.ndarray = None,
        radius: float = 1.0,
        subdivisions: int = 16,
    ):
        transform = Transform3D()
        if position is not None:
            transform.set_position(position)

        super().__init__(name or "Sphere", transform)
        self.radius = radius
        self.subdivisions = max(4, subdivisions)  # Minimum 4 subdivisions

        # Default material properties
        self.material_properties = {
            "color": np.array([0.8, 0.8, 0.8]),
            "wireframe": False,
            "opacity": 1.0,
        }

    def get_geometry(self) -> Dict[str, Any]:
        """Get sphere geometry data using UV sphere generation."""
        vertices = []
        normals = []
        faces = []

        # Generate vertices and normals
        for i in range(self.subdivisions + 1):
            lat = math.pi * (-0.5 + float(i) / self.subdivisions)

            for j in range(self.subdivisions * 2):
                lon = 2 * math.pi * float(j) / (self.subdivisions * 2)

                # Spherical to Cartesian coordinates
                x = self.radius * math.cos(lat) * math.cos(lon)
                y = self.radius * math.sin(lat)
                z = self.radius * math.cos(lat) * math.sin(lon)

                vertex = np.array([x, y, z])
                normal = vertex / self.radius  # Normalized position is the normal

                # Transform vertex and normal
                transformed_vertex = self.transform.transform_point(vertex)
                transformed_normal = self.transform.transform_normal(normal)

                vertices.append(transformed_vertex)
                normals.append(transformed_normal)

        # Generate faces
        for i in range(self.subdivisions):
            for j in range(self.subdivisions * 2):
                # Current quad indices
                i0 = i * (self.subdivisions * 2) + j
                i1 = (
                    i0 + 1
                    if j < (self.subdivisions * 2) - 1
                    else i * (self.subdivisions * 2)
                )
                i2 = (i + 1) * (self.subdivisions * 2) + j
                i3 = (
                    i2 + 1
                    if j < (self.subdivisions * 2) - 1
                    else (i + 1) * (self.subdivisions * 2)
                )

                # Skip degenerate triangles at poles
                if i > 0:  # Not north pole
                    faces.append([i0, i1, i2])
                if i < self.subdivisions - 1:  # Not south pole
                    faces.append([i1, i3, i2])

        return {
            "type": "mesh",
            "vertices": np.array(vertices),
            "faces": np.array(faces),
            "normals": np.array(normals),
            "material": self.material_properties,
        }

    def get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get sphere bounding box."""
        if not self._bounds_dirty and self._bounds_cache is not None:
            return self._bounds_cache

        center = self.transform.position

        # For sphere, bounds are simply center +/- radius (with scale)
        max_scale = np.max(self.transform.scale)
        effective_radius = self.radius * max_scale

        min_bounds = center - effective_radius
        max_bounds = center + effective_radius

        self._bounds_cache = (min_bounds, max_bounds)
        self._bounds_dirty = False

        return self._bounds_cache


class Scene3D:
    """3D Scene management system."""

    def __init__(self, name: str = "Scene3D"):
        self.name = name
        self.objects: Dict[str, Object3D] = {}
        self.object_render_order: List[str] = []

        # Scene components
        self.camera: Optional[CameraController] = None
        self.manipulator = ObjectManipulator()
        self.selector = SelectionManager()

        # Scene properties
        self.background_color = np.array([0.2, 0.2, 0.2])
        self.ambient_light = np.array([0.3, 0.3, 0.3])

        # Interaction state
        self.interaction_enabled = True
        self.selection_enabled = False
        self.manipulation_enabled = False
        self.manipulation_mode = TransformMode.TRANSLATE

        # Event callbacks
        self.on_object_added: Optional[Callable] = None
        self.on_object_removed: Optional[Callable] = None
        self.on_selection_changed: Optional[Callable] = None

        # Performance tracking
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.fps = 0.0

    def add_object(self, obj: Object3D, object_id: str = None) -> str:
        """Add object to scene."""
        obj_id = object_id or obj.name

        # Ensure unique ID
        original_id = obj_id
        counter = 1
        while obj_id in self.objects:
            obj_id = f"{original_id}_{counter}"
            counter += 1

        self.objects[obj_id] = obj
        self.object_render_order.append(obj_id)

        # Add to manipulator if manipulation is enabled
        if self.manipulation_enabled:
            self.manipulator.add_object(obj_id, obj.transform)

        if self.on_object_added:
            self.on_object_added(obj_id, obj)

        return obj_id

    def add_objects(self, objects: List[Object3D]) -> List[str]:
        """Add multiple objects to scene."""
        object_ids = []
        for obj in objects:
            obj_id = self.add_object(obj)
            object_ids.append(obj_id)
        return object_ids

    def remove_object(self, object_id: str) -> bool:
        """Remove object from scene."""
        if object_id not in self.objects:
            return False

        obj = self.objects.pop(object_id)
        self.object_render_order.remove(object_id)

        # Remove from manipulator
        self.manipulator.remove_object(object_id)

        # Remove from selection
        if obj.selected:
            self.selector.deselect_object(object_id)

        if self.on_object_removed:
            self.on_object_removed(object_id, obj)

        return True

    def get_object(self, object_id: str) -> Optional[Object3D]:
        """Get object by ID."""
        return self.objects.get(object_id)

    def set_camera(self, camera: CameraController):
        """Set scene camera."""
        self.camera = camera

    def enable_selection(self, mode: str = "single"):
        """Enable object selection."""
        self.selection_enabled = True
        self.selector.set_selection_mode(mode)

    def enable_manipulation(self, transforms: List[str] = None):
        """Enable object manipulation."""
        self.manipulation_enabled = True

        # Add existing objects to manipulator
        for obj_id, obj in self.objects.items():
            self.manipulator.add_object(obj_id, obj.transform)

        # Set allowed transform types
        if transforms:
            if "translate" in transforms:
                self.manipulation_mode = TransformMode.TRANSLATE
            elif "rotate" in transforms:
                self.manipulation_mode = TransformMode.ROTATE
            elif "scale" in transforms:
                self.manipulation_mode = TransformMode.SCALE

        self.manipulator.set_manipulation_mode(self.manipulation_mode)

    def disable_selection(self):
        """Disable object selection."""
        self.selection_enabled = False
        self.selector.clear_selection()

    def disable_manipulation(self):
        """Disable object manipulation."""
        self.manipulation_enabled = False

    def select_object(self, object_id: str, append: bool = False):
        """Select object."""
        if not self.selection_enabled:
            return

        if not append:
            self.clear_selection()

        obj = self.objects.get(object_id)
        if obj:
            obj.selected = True
            self.selector.select_object(object_id)

            if self.on_selection_changed:
                self.on_selection_changed(self.get_selected_objects())

    def deselect_object(self, object_id: str):
        """Deselect object."""
        obj = self.objects.get(object_id)
        if obj:
            obj.selected = False
            self.selector.deselect_object(object_id)

            if self.on_selection_changed:
                self.on_selection_changed(self.get_selected_objects())

    def clear_selection(self):
        """Clear all selections."""
        for obj in self.objects.values():
            obj.selected = False

        self.selector.clear_selection()

        if self.on_selection_changed:
            self.on_selection_changed([])

    def get_selected_objects(self) -> List[str]:
        """Get list of selected object IDs."""
        return [obj_id for obj_id, obj in self.objects.items() if obj.selected]

    def get_scene_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get bounding box of entire scene."""
        if not self.objects:
            return np.array([0, 0, 0]), np.array([0, 0, 0])

        all_min = []
        all_max = []

        for obj in self.objects.values():
            if obj.visible:
                min_bounds, max_bounds = obj.get_bounds()
                all_min.append(min_bounds)
                all_max.append(max_bounds)

        if not all_min:
            return np.array([0, 0, 0]), np.array([0, 0, 0])

        scene_min = np.min(all_min, axis=0)
        scene_max = np.max(all_max, axis=0)

        return scene_min, scene_max

    def focus_camera_on_scene(self):
        """Focus camera to fit entire scene."""
        if not self.camera:
            return

        scene_min, scene_max = self.get_scene_bounds()

        if hasattr(self.camera, "focus_on_bounds"):
            self.camera.focus_on_bounds(scene_min, scene_max)

    def focus_camera_on_selection(self):
        """Focus camera on selected objects."""
        if not self.camera:
            return

        selected_objects = self.get_selected_objects()
        if not selected_objects:
            return

        # Calculate bounds of selected objects
        all_min = []
        all_max = []

        for obj_id in selected_objects:
            obj = self.objects[obj_id]
            min_bounds, max_bounds = obj.get_bounds()
            all_min.append(min_bounds)
            all_max.append(max_bounds)

        scene_min = np.min(all_min, axis=0)
        scene_max = np.max(all_max, axis=0)

        if hasattr(self.camera, "focus_on_bounds"):
            self.camera.focus_on_bounds(scene_min, scene_max)

    def get_render_data(self) -> Dict[str, Any]:
        """Get all data needed for rendering."""
        render_data = {
            "objects": [],
            "camera": None,
            "scene_properties": {
                "background_color": self.background_color,
                "ambient_light": self.ambient_light,
            },
            "gizmos": [],
        }

        # Collect object geometry
        for obj_id in self.object_render_order:
            obj = self.objects.get(obj_id)
            if obj and obj.visible:
                geometry = obj.get_geometry()
                geometry["object_id"] = obj_id
                geometry["selected"] = obj.selected
                render_data["objects"].append(geometry)

        # Camera data
        if self.camera:
            render_data["camera"] = {
                "view_matrix": self.camera.get_view_matrix(),
                "projection_matrix": self.camera.get_projection_matrix(),
                "position": self.camera.position,
                "target": self.camera.target,
            }

        # Manipulation gizmos
        if self.manipulation_enabled:
            for obj_id in self.get_selected_objects():
                gizmo = self.manipulator.get_gizmo(obj_id)
                if gizmo:
                    gizmo_geometry = gizmo.get_gizmo_geometry()
                    gizmo_geometry["object_id"] = obj_id
                    render_data["gizmos"].append(gizmo_geometry)

        return render_data

    def update(self, dt: float):
        """Update scene state."""
        # Update FPS
        current_time = time.time()
        self.frame_count += 1

        if current_time - self.last_frame_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_frame_time)
            self.frame_count = 0
            self.last_frame_time = current_time

    def run(self, renderer=None):
        """Start interactive scene session."""
        if not self.camera:
            # Set default camera
            self.camera = OrbitController(distance=10.0)
            self.focus_camera_on_scene()

        print(f"🎮 Starting interactive 3D scene: {self.name}")
        print(f"📊 Objects: {len(self.objects)}")
        print(f"📷 Camera: {type(self.camera).__name__}")
        print(
            f"🔧 Manipulation: {'Enabled' if self.manipulation_enabled else 'Disabled'}"
        )
        print(f"🎯 Selection: {'Enabled' if self.selection_enabled else 'Disabled'}")

        # Simple text-based display for now
        print("\n📋 Scene Objects:")
        for obj_id, obj in self.objects.items():
            obj_type = type(obj).__name__
            pos = obj.transform.position
            print(
                f"  • {obj_id} ({obj_type}) at [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]"
            )

        print(
            "\n🎯 Scene ready! (Note: Full interactive rendering requires a 3D renderer)"
        )
        print(
            "💡 This is a simulation - in a full implementation, this would launch an interactive 3D viewer."
        )

        return True


# Factory functions for convenience
def create_cube(
    position: np.ndarray = None, size: float = 1.0, color: np.ndarray = None
) -> Cube:
    """Create a cube with optional parameters."""
    cube = Cube(position=position, size=size)
    if color is not None:
        cube.set_material_property("color", color)
    return cube


def create_sphere(
    position: np.ndarray = None,
    radius: float = 1.0,
    color: np.ndarray = None,
    subdivisions: int = 16,
) -> Sphere:
    """Create a sphere with optional parameters."""
    sphere = Sphere(position=position, radius=radius, subdivisions=subdivisions)
    if color is not None:
        sphere.set_material_property("color", color)
    return sphere
