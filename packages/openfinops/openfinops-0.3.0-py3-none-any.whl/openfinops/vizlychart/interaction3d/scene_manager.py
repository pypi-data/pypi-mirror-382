"""Advanced 3D scene management system for Vizly."""

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
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Transform3D:
    """3D transformation matrix wrapper."""
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))  # Euler angles
    scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))

    @property
    def matrix(self) -> np.ndarray:
        """Get 4x4 transformation matrix."""
        # Translation matrix
        T = np.eye(4)
        T[:3, 3] = self.position

        # Rotation matrices (ZYX order)
        rx, ry, rz = self.rotation

        Rx = np.array([
            [1, 0, 0, 0],
            [0, np.cos(rx), -np.sin(rx), 0],
            [0, np.sin(rx), np.cos(rx), 0],
            [0, 0, 0, 1]
        ])

        Ry = np.array([
            [np.cos(ry), 0, np.sin(ry), 0],
            [0, 1, 0, 0],
            [-np.sin(ry), 0, np.cos(ry), 0],
            [0, 0, 0, 1]
        ])

        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0, 0],
            [np.sin(rz), np.cos(rz), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # Scale matrix
        S = np.eye(4)
        S[0, 0], S[1, 1], S[2, 2] = self.scale

        return T @ Rz @ Ry @ Rx @ S


@dataclass
class BoundingBox:
    """3D axis-aligned bounding box."""
    min_point: np.ndarray
    max_point: np.ndarray

    @property
    def center(self) -> np.ndarray:
        return (self.min_point + self.max_point) / 2

    @property
    def size(self) -> np.ndarray:
        return self.max_point - self.min_point

    def contains_point(self, point: np.ndarray) -> bool:
        """Check if point is inside bounding box."""
        return np.all(point >= self.min_point) and np.all(point <= self.max_point)

    def intersects(self, other: 'BoundingBox') -> bool:
        """Check if this bounding box intersects with another."""
        return np.all(self.min_point <= other.max_point) and np.all(other.min_point <= self.max_point)


class SceneObject(ABC):
    """Abstract base class for 3D scene objects."""

    def __init__(self, object_id: str, transform: Optional[Transform3D] = None):
        self.object_id = object_id
        self.transform = transform or Transform3D()
        self.visible = True
        self.selectable = True
        self.metadata: Dict[str, Any] = {}
        self._bounding_box: Optional[BoundingBox] = None

    @property
    def bounding_box(self) -> BoundingBox:
        """Get world-space bounding box."""
        if self._bounding_box is None:
            self._bounding_box = self._compute_bounding_box()
        return self._bounding_box

    @abstractmethod
    def _compute_bounding_box(self) -> BoundingBox:
        """Compute the object's bounding box in local space."""
        pass

    @abstractmethod
    def render(self, view_matrix: np.ndarray, projection_matrix: np.ndarray) -> List[Dict]:
        """Render the object and return render data."""
        pass

    def invalidate_bounds(self):
        """Mark bounding box as needing recomputation."""
        self._bounding_box = None


class MeshObject(SceneObject):
    """3D mesh object with vertices and faces."""

    def __init__(self, object_id: str, vertices: np.ndarray, faces: np.ndarray,
                 transform: Optional[Transform3D] = None):
        super().__init__(object_id, transform)
        self.vertices = vertices  # Nx3 array
        self.faces = faces        # Mx3 array of vertex indices
        self.colors: Optional[np.ndarray] = None  # Nx3 or Nx4 colors

    def _compute_bounding_box(self) -> BoundingBox:
        """Compute bounding box from vertices."""
        if len(self.vertices) == 0:
            return BoundingBox(np.zeros(3), np.zeros(3))

        # Transform vertices to world space
        homogeneous_verts = np.column_stack([self.vertices, np.ones(len(self.vertices))])
        world_verts = (self.transform.matrix @ homogeneous_verts.T).T[:, :3]

        return BoundingBox(
            min_point=np.min(world_verts, axis=0),
            max_point=np.max(world_verts, axis=0)
        )

    def render(self, view_matrix: np.ndarray, projection_matrix: np.ndarray) -> List[Dict]:
        """Render mesh faces."""
        if not self.visible or len(self.vertices) == 0:
            return []

        # Transform pipeline
        model_view = view_matrix @ self.transform.matrix
        mvp = projection_matrix @ model_view

        # Transform vertices
        homogeneous_verts = np.column_stack([self.vertices, np.ones(len(self.vertices))])
        transformed_verts = (mvp @ homogeneous_verts.T).T

        # Perspective divide
        screen_verts = transformed_verts[:, :3] / transformed_verts[:, 3:4]

        # Generate render data for each face
        render_data = []
        for face in self.faces:
            face_verts = screen_verts[face]

            # Simple back-face culling
            if len(face) >= 3:
                v1, v2, v3 = face_verts[:3]
                normal = np.cross(v2 - v1, v3 - v1)
                if normal[2] < 0:  # Facing away
                    continue

            render_data.append({
                'type': 'face',
                'vertices': face_verts,
                'object_id': self.object_id,
                'colors': self.colors[face] if self.colors is not None else None
            })

        return render_data


class PointCloudObject(SceneObject):
    """Point cloud 3D object."""

    def __init__(self, object_id: str, points: np.ndarray,
                 transform: Optional[Transform3D] = None):
        super().__init__(object_id, transform)
        self.points = points  # Nx3 array
        self.colors: Optional[np.ndarray] = None  # Nx3 or Nx4 colors
        self.point_size = 1.0

    def _compute_bounding_box(self) -> BoundingBox:
        """Compute bounding box from points."""
        if len(self.points) == 0:
            return BoundingBox(np.zeros(3), np.zeros(3))

        # Transform points to world space
        homogeneous_points = np.column_stack([self.points, np.ones(len(self.points))])
        world_points = (self.transform.matrix @ homogeneous_points.T).T[:, :3]

        return BoundingBox(
            min_point=np.min(world_points, axis=0),
            max_point=np.max(world_points, axis=0)
        )

    def render(self, view_matrix: np.ndarray, projection_matrix: np.ndarray) -> List[Dict]:
        """Render point cloud."""
        if not self.visible or len(self.points) == 0:
            return []

        # Transform pipeline
        model_view = view_matrix @ self.transform.matrix
        mvp = projection_matrix @ model_view

        # Transform points
        homogeneous_points = np.column_stack([self.points, np.ones(len(self.points))])
        transformed_points = (mvp @ homogeneous_points.T).T

        # Perspective divide
        screen_points = transformed_points[:, :3] / transformed_points[:, 3:4]

        return [{
            'type': 'point_cloud',
            'points': screen_points,
            'colors': self.colors,
            'point_size': self.point_size,
            'object_id': self.object_id
        }]


class SceneGraph:
    """Hierarchical scene graph for managing 3D objects."""

    def __init__(self):
        self.objects: Dict[str, SceneObject] = {}
        self.hierarchy: Dict[str, List[str]] = defaultdict(list)  # parent -> children
        self.parents: Dict[str, Optional[str]] = {}  # child -> parent
        self.spatial_index: Dict[Tuple[int, int, int], List[str]] = defaultdict(list)
        self.grid_size = 10.0  # Size of spatial grid cells

    def add_object(self, obj: SceneObject, parent_id: Optional[str] = None):
        """Add object to scene graph."""
        self.objects[obj.object_id] = obj

        if parent_id and parent_id in self.objects:
            self.hierarchy[parent_id].append(obj.object_id)
            self.parents[obj.object_id] = parent_id
        else:
            self.parents[obj.object_id] = None

        self._update_spatial_index(obj)
        logger.info(f"Added object {obj.object_id} to scene graph")

    def remove_object(self, object_id: str):
        """Remove object and its children from scene graph."""
        if object_id not in self.objects:
            return

        # Remove children recursively
        for child_id in self.hierarchy[object_id][:]:
            self.remove_object(child_id)

        # Remove from parent's children
        parent_id = self.parents[object_id]
        if parent_id:
            self.hierarchy[parent_id].remove(object_id)

        # Remove from spatial index
        self._remove_from_spatial_index(self.objects[object_id])

        # Remove object
        del self.objects[object_id]
        del self.parents[object_id]
        if object_id in self.hierarchy:
            del self.hierarchy[object_id]

        logger.info(f"Removed object {object_id} from scene graph")

    def get_object(self, object_id: str) -> Optional[SceneObject]:
        """Get object by ID."""
        return self.objects.get(object_id)

    def get_children(self, object_id: str) -> List[SceneObject]:
        """Get all children of an object."""
        child_ids = self.hierarchy.get(object_id, [])
        return [self.objects[child_id] for child_id in child_ids if child_id in self.objects]

    def get_root_objects(self) -> List[SceneObject]:
        """Get all root objects (no parent)."""
        return [obj for obj_id, obj in self.objects.items() if self.parents[obj_id] is None]

    def query_region(self, center: np.ndarray, radius: float) -> List[SceneObject]:
        """Spatial query for objects near a point."""
        results = []

        # Get grid cells to check
        grid_radius = int(np.ceil(radius / self.grid_size))
        center_cell = self._world_to_grid(center)

        for dx in range(-grid_radius, grid_radius + 1):
            for dy in range(-grid_radius, grid_radius + 1):
                for dz in range(-grid_radius, grid_radius + 1):
                    cell = (center_cell[0] + dx, center_cell[1] + dy, center_cell[2] + dz)

                    for object_id in self.spatial_index.get(cell, []):
                        obj = self.objects.get(object_id)
                        if obj and object_id not in [r.object_id for r in results]:
                            # Check actual distance to bounding box
                            bbox = obj.bounding_box
                            closest_point = np.clip(center, bbox.min_point, bbox.max_point)
                            if np.linalg.norm(center - closest_point) <= radius:
                                results.append(obj)

        return results

    def _world_to_grid(self, position: np.ndarray) -> Tuple[int, int, int]:
        """Convert world position to grid cell."""
        grid_pos = position / self.grid_size
        return (int(np.floor(grid_pos[0])), int(np.floor(grid_pos[1])), int(np.floor(grid_pos[2])))

    def _update_spatial_index(self, obj: SceneObject):
        """Update spatial index for object."""
        # Remove from old cells
        self._remove_from_spatial_index(obj)

        # Add to new cells
        bbox = obj.bounding_box
        min_cell = self._world_to_grid(bbox.min_point)
        max_cell = self._world_to_grid(bbox.max_point)

        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    self.spatial_index[(x, y, z)].append(obj.object_id)

    def _remove_from_spatial_index(self, obj: SceneObject):
        """Remove object from spatial index."""
        for cell_objects in self.spatial_index.values():
            if obj.object_id in cell_objects:
                cell_objects.remove(obj.object_id)


class RenderPipeline:
    """Rendering pipeline for 3D scenes."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.clear_color = np.array([0.1, 0.1, 0.1, 1.0])
        self.depth_testing = True

    def render_scene(self, scene_graph: SceneGraph, camera_matrix: np.ndarray,
                    projection_matrix: np.ndarray) -> Dict[str, Any]:
        """Render entire scene."""
        start_time = time.time()

        # Collect all render data
        all_render_data = []
        rendered_objects = 0

        for obj in scene_graph.objects.values():
            if obj.visible:
                render_data = obj.render(camera_matrix, projection_matrix)
                all_render_data.extend(render_data)
                if render_data:
                    rendered_objects += 1

        # Sort by depth if depth testing enabled
        if self.depth_testing:
            all_render_data.sort(key=lambda x: self._get_depth(x), reverse=True)

        render_time = time.time() - start_time

        return {
            'render_data': all_render_data,
            'stats': {
                'render_time': render_time,
                'total_objects': len(scene_graph.objects),
                'rendered_objects': rendered_objects,
                'total_primitives': len(all_render_data)
            },
            'viewport': {
                'width': self.width,
                'height': self.height
            }
        }

    def _get_depth(self, render_item: Dict) -> float:
        """Get average depth of render item for sorting."""
        if 'vertices' in render_item:
            return np.mean(render_item['vertices'][:, 2])
        elif 'points' in render_item:
            return np.mean(render_item['points'][:, 2])
        return 0.0


class Scene3DManager:
    """High-level 3D scene manager with threading support."""

    def __init__(self, width: int = 800, height: int = 600):
        self.scene_graph = SceneGraph()
        self.render_pipeline = RenderPipeline(width, height)

        # Threading
        self._lock = threading.RLock()
        self._update_thread: Optional[threading.Thread] = None
        self._running = False
        self._frame_rate = 60.0

        # Event callbacks
        self.on_frame_rendered: Optional[Callable[[Dict], None]] = None
        self.on_object_added: Optional[Callable[[str], None]] = None
        self.on_object_removed: Optional[Callable[[str], None]] = None

        # Performance tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0.0

    def add_object(self, obj: SceneObject, parent_id: Optional[str] = None):
        """Thread-safe object addition."""
        with self._lock:
            self.scene_graph.add_object(obj, parent_id)
            if self.on_object_added:
                self.on_object_added(obj.object_id)

    def remove_object(self, object_id: str):
        """Thread-safe object removal."""
        with self._lock:
            self.scene_graph.remove_object(object_id)
            if self.on_object_removed:
                self.on_object_removed(object_id)

    def get_object(self, object_id: str) -> Optional[SceneObject]:
        """Thread-safe object retrieval."""
        with self._lock:
            return self.scene_graph.get_object(object_id)

    def query_objects(self, center: np.ndarray, radius: float) -> List[SceneObject]:
        """Thread-safe spatial query."""
        with self._lock:
            return self.scene_graph.query_region(center, radius)

    def render_frame(self, camera_matrix: np.ndarray, projection_matrix: np.ndarray) -> Dict[str, Any]:
        """Render a single frame."""
        with self._lock:
            frame_data = self.render_pipeline.render_scene(
                self.scene_graph, camera_matrix, projection_matrix
            )

            # Update FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                self.current_fps = self.frame_count / (current_time - self.last_fps_time)
                self.frame_count = 0
                self.last_fps_time = current_time

            frame_data['stats']['fps'] = self.current_fps

            if self.on_frame_rendered:
                self.on_frame_rendered(frame_data)

            return frame_data

    def start_update_loop(self, camera_matrix: np.ndarray, projection_matrix: np.ndarray):
        """Start continuous rendering loop in background thread."""
        if self._running:
            return

        self._running = True

        def update_loop():
            frame_time = 1.0 / self._frame_rate

            while self._running:
                start_time = time.time()

                try:
                    self.render_frame(camera_matrix, projection_matrix)
                except Exception as e:
                    logger.error(f"Error in render loop: {e}")

                # Frame rate limiting
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        self._update_thread = threading.Thread(target=update_loop, daemon=True)
        self._update_thread.start()
        logger.info(f"Started scene update loop at {self._frame_rate} FPS")

    def stop_update_loop(self):
        """Stop the background rendering loop."""
        if self._running:
            self._running = False
            if self._update_thread:
                self._update_thread.join(timeout=1.0)
            logger.info("Stopped scene update loop")

    def set_frame_rate(self, fps: float):
        """Set target frame rate."""
        self._frame_rate = max(1.0, min(120.0, fps))

    def get_scene_stats(self) -> Dict[str, Any]:
        """Get comprehensive scene statistics."""
        with self._lock:
            total_objects = len(self.scene_graph.objects)
            visible_objects = sum(1 for obj in self.scene_graph.objects.values() if obj.visible)
            root_objects = len(self.scene_graph.get_root_objects())

            # Compute total vertices/points
            total_vertices = 0
            total_points = 0
            for obj in self.scene_graph.objects.values():
                if isinstance(obj, MeshObject):
                    total_vertices += len(obj.vertices)
                elif isinstance(obj, PointCloudObject):
                    total_points += len(obj.points)

            return {
                'objects': {
                    'total': total_objects,
                    'visible': visible_objects,
                    'root': root_objects
                },
                'geometry': {
                    'total_vertices': total_vertices,
                    'total_points': total_points
                },
                'performance': {
                    'fps': self.current_fps,
                    'running': self._running,
                    'target_fps': self._frame_rate
                },
                'spatial_index': {
                    'grid_size': self.scene_graph.grid_size,
                    'occupied_cells': len([cell for cell, objects in self.scene_graph.spatial_index.items() if objects])
                }
            }