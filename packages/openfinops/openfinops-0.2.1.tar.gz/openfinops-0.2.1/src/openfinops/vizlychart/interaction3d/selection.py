"""
Advanced 3D Selection Systems
Provides multiple selection methods including raycasting, box selection, and spatial queries.
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
from typing import List, Tuple, Dict, Any, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum


class SelectionMode(Enum):
    """Selection mode enumeration."""

    SINGLE = "single"
    MULTIPLE = "multiple"
    ADDITIVE = "additive"
    SUBTRACTIVE = "subtractive"


@dataclass
class Ray:
    """3D ray for raycasting operations."""

    origin: np.ndarray
    direction: np.ndarray

    def point_at(self, t: float) -> np.ndarray:
        """Get point along ray at parameter t."""
        return self.origin + t * self.direction

    def distance_to_point(self, point: np.ndarray) -> float:
        """Calculate distance from ray to point."""
        to_point = point - self.origin
        projection = np.dot(to_point, self.direction)
        closest_point = self.origin + projection * self.direction
        return np.linalg.norm(point - closest_point)


@dataclass
class BoundingBox:
    """Axis-aligned bounding box."""

    min_point: np.ndarray
    max_point: np.ndarray

    @property
    def center(self) -> np.ndarray:
        """Get center of bounding box."""
        return (self.min_point + self.max_point) / 2

    @property
    def size(self) -> np.ndarray:
        """Get size of bounding box."""
        return self.max_point - self.min_point

    def contains_point(self, point: np.ndarray) -> bool:
        """Check if point is inside bounding box."""
        return np.all(point >= self.min_point) and np.all(point <= self.max_point)

    def intersects_ray(self, ray: Ray) -> Tuple[bool, float, float]:
        """Check if ray intersects bounding box. Returns (hit, t_near, t_far)."""
        inv_dir = np.where(ray.direction != 0, 1.0 / ray.direction, np.inf)

        t1 = (self.min_point - ray.origin) * inv_dir
        t2 = (self.max_point - ray.origin) * inv_dir

        t_min = np.minimum(t1, t2)
        t_max = np.maximum(t1, t2)

        t_near = np.max(t_min)
        t_far = np.min(t_max)

        return t_far >= t_near and t_far >= 0, t_near, t_far

    def intersects_box(self, other: "BoundingBox") -> bool:
        """Check if this box intersects another box."""
        return np.all(self.min_point <= other.max_point) and np.all(
            self.max_point >= other.min_point
        )


@dataclass
class Sphere:
    """3D sphere primitive."""

    center: np.ndarray
    radius: float

    def contains_point(self, point: np.ndarray) -> bool:
        """Check if point is inside sphere."""
        return np.linalg.norm(point - self.center) <= self.radius

    def intersects_ray(self, ray: Ray) -> Tuple[bool, float, float]:
        """Check if ray intersects sphere. Returns (hit, t1, t2)."""
        oc = ray.origin - self.center
        a = np.dot(ray.direction, ray.direction)
        b = 2.0 * np.dot(oc, ray.direction)
        c = np.dot(oc, oc) - self.radius * self.radius

        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return False, 0, 0

        sqrt_discriminant = math.sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2 * a)
        t2 = (-b + sqrt_discriminant) / (2 * a)

        return True, t1, t2


@dataclass
class Plane:
    """3D plane primitive."""

    point: np.ndarray
    normal: np.ndarray

    def __post_init__(self):
        """Normalize the normal vector."""
        self.normal = self.normal / np.linalg.norm(self.normal)

    def distance_to_point(self, point: np.ndarray) -> float:
        """Calculate signed distance from plane to point."""
        return np.dot(point - self.point, self.normal)

    def intersects_ray(self, ray: Ray) -> Tuple[bool, float]:
        """Check if ray intersects plane. Returns (hit, t)."""
        denom = np.dot(self.normal, ray.direction)

        if abs(denom) < 1e-6:  # Ray is parallel to plane
            return False, 0

        t = np.dot(self.point - ray.origin, self.normal) / denom
        return t >= 0, t


@dataclass
class SelectableObject:
    """Base class for selectable 3D objects."""

    id: str
    position: np.ndarray
    bounding_box: BoundingBox
    metadata: Dict[str, Any] = None
    selectable: bool = True

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Selector(ABC):
    """Base class for selection algorithms."""

    @abstractmethod
    def select(
        self, objects: List[SelectableObject], **kwargs
    ) -> List[SelectableObject]:
        """Perform selection on objects."""
        pass


class RaycastSelector(Selector):
    """Ray-based selection using 3D raycasting."""

    def __init__(self):
        self.tolerance = 0.1  # Distance tolerance for line/point selection

    def select(
        self,
        objects: List[SelectableObject],
        ray: Ray,
        max_distance: float = float("inf"),
    ) -> List[SelectableObject]:
        """Select objects intersected by ray."""
        intersections = []

        for obj in objects:
            if not obj.selectable:
                continue

            # Check bounding box intersection first
            hit, t_near, t_far = obj.bounding_box.intersects_ray(ray)

            if hit and t_near <= max_distance:
                # More detailed intersection testing could go here
                # For now, we use bounding box intersection
                intersections.append((obj, t_near))

        # Sort by distance and return objects
        intersections.sort(key=lambda x: x[1])
        return [obj for obj, _ in intersections]

    def create_ray_from_screen(
        self,
        screen_x: float,
        screen_y: float,
        viewport_width: int,
        viewport_height: int,
        view_matrix: np.ndarray,
        projection_matrix: np.ndarray,
    ) -> Ray:
        """Create a ray from screen coordinates."""
        # Convert screen coordinates to normalized device coordinates
        ndc_x = (2.0 * screen_x) / viewport_width - 1.0
        ndc_y = 1.0 - (2.0 * screen_y) / viewport_height

        # Create points in clip space
        near_point = np.array([ndc_x, ndc_y, -1.0, 1.0])
        far_point = np.array([ndc_x, ndc_y, 1.0, 1.0])

        # Transform to world space
        inv_view_proj = np.linalg.inv(projection_matrix @ view_matrix)

        world_near = inv_view_proj @ near_point
        world_far = inv_view_proj @ far_point

        # Perspective divide
        world_near = world_near[:3] / world_near[3]
        world_far = world_far[:3] / world_far[3]

        # Create ray
        direction = world_far - world_near
        direction = direction / np.linalg.norm(direction)

        return Ray(world_near, direction)


class BoxSelector(Selector):
    """Box-based selection for selecting multiple objects."""

    def __init__(self):
        self.selection_box = None

    def select(
        self,
        objects: List[SelectableObject],
        min_corner: np.ndarray,
        max_corner: np.ndarray,
    ) -> List[SelectableObject]:
        """Select objects within selection box."""
        selection_box = BoundingBox(min_corner, max_corner)
        selected = []

        for obj in objects:
            if not obj.selectable:
                continue

            # Check if object's bounding box intersects selection box
            if obj.bounding_box.intersects_box(selection_box):
                selected.append(obj)

        return selected

    def create_box_from_screen(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        viewport_width: int,
        viewport_height: int,
        view_matrix: np.ndarray,
        projection_matrix: np.ndarray,
        depth_near: float = 0.1,
        depth_far: float = 1000.0,
    ) -> BoundingBox:
        """Create selection box from screen coordinates."""
        # Ensure proper ordering
        min_x = min(start_x, end_x)
        max_x = max(start_x, end_x)
        min_y = min(start_y, end_y)
        max_y = max(start_y, end_y)

        # Create rays for corners
        raycast_selector = RaycastSelector()

        top_left = raycast_selector.create_ray_from_screen(
            min_x,
            min_y,
            viewport_width,
            viewport_height,
            view_matrix,
            projection_matrix,
        )
        bottom_right = raycast_selector.create_ray_from_screen(
            max_x,
            max_y,
            viewport_width,
            viewport_height,
            view_matrix,
            projection_matrix,
        )

        # Create bounding box that encompasses the selection frustum
        near_tl = top_left.point_at(depth_near)
        far_tl = top_left.point_at(depth_far)
        near_br = bottom_right.point_at(depth_near)
        far_br = bottom_right.point_at(depth_far)

        # Find min/max bounds
        all_points = np.array([near_tl, far_tl, near_br, far_br])
        min_point = np.min(all_points, axis=0)
        max_point = np.max(all_points, axis=0)

        return BoundingBox(min_point, max_point)


class FrustumSelector(Selector):
    """Frustum-based selection for camera view volumes."""

    def __init__(self):
        self.frustum_planes = []

    def set_frustum_from_camera(
        self, view_matrix: np.ndarray, projection_matrix: np.ndarray
    ):
        """Set frustum from camera matrices."""
        combined = projection_matrix @ view_matrix

        # Extract frustum planes from combined matrix
        self.frustum_planes = []

        # Left plane
        self.frustum_planes.append(
            Plane(
                np.array([0, 0, 0]),
                np.array(
                    [
                        combined[3, 0] + combined[0, 0],
                        combined[3, 1] + combined[0, 1],
                        combined[3, 2] + combined[0, 2],
                    ]
                ),
            )
        )

        # Right plane
        self.frustum_planes.append(
            Plane(
                np.array([0, 0, 0]),
                np.array(
                    [
                        combined[3, 0] - combined[0, 0],
                        combined[3, 1] - combined[0, 1],
                        combined[3, 2] - combined[0, 2],
                    ]
                ),
            )
        )

        # Bottom plane
        self.frustum_planes.append(
            Plane(
                np.array([0, 0, 0]),
                np.array(
                    [
                        combined[3, 0] + combined[1, 0],
                        combined[3, 1] + combined[1, 1],
                        combined[3, 2] + combined[1, 2],
                    ]
                ),
            )
        )

        # Top plane
        self.frustum_planes.append(
            Plane(
                np.array([0, 0, 0]),
                np.array(
                    [
                        combined[3, 0] - combined[1, 0],
                        combined[3, 1] - combined[1, 1],
                        combined[3, 2] - combined[1, 2],
                    ]
                ),
            )
        )

        # Near plane
        self.frustum_planes.append(
            Plane(
                np.array([0, 0, 0]),
                np.array(
                    [
                        combined[3, 0] + combined[2, 0],
                        combined[3, 1] + combined[2, 1],
                        combined[3, 2] + combined[2, 2],
                    ]
                ),
            )
        )

        # Far plane
        self.frustum_planes.append(
            Plane(
                np.array([0, 0, 0]),
                np.array(
                    [
                        combined[3, 0] - combined[2, 0],
                        combined[3, 1] - combined[2, 1],
                        combined[3, 2] - combined[2, 2],
                    ]
                ),
            )
        )

    def select(self, objects: List[SelectableObject]) -> List[SelectableObject]:
        """Select objects within frustum."""
        selected = []

        for obj in objects:
            if not obj.selectable:
                continue

            if self._is_box_in_frustum(obj.bounding_box):
                selected.append(obj)

        return selected

    def _is_box_in_frustum(self, box: BoundingBox) -> bool:
        """Check if bounding box is within frustum."""
        # Get all 8 corners of the box
        corners = np.array(
            [
                [box.min_point[0], box.min_point[1], box.min_point[2]],
                [box.max_point[0], box.min_point[1], box.min_point[2]],
                [box.min_point[0], box.max_point[1], box.min_point[2]],
                [box.max_point[0], box.max_point[1], box.min_point[2]],
                [box.min_point[0], box.min_point[1], box.max_point[2]],
                [box.max_point[0], box.min_point[1], box.max_point[2]],
                [box.min_point[0], box.max_point[1], box.max_point[2]],
                [box.max_point[0], box.max_point[1], box.max_point[2]],
            ]
        )

        # Check if box is completely outside any plane
        for plane in self.frustum_planes:
            outside_count = 0
            for corner in corners:
                if plane.distance_to_point(corner) < 0:
                    outside_count += 1

            # If all corners are outside this plane, box is not in frustum
            if outside_count == 8:
                return False

        return True


class SelectionManager:
    """Main selection manager coordinating different selection methods."""

    def __init__(self):
        self.selected_objects: Set[str] = set()
        self.selection_mode = SelectionMode.SINGLE
        self.objects: Dict[str, SelectableObject] = {}

        # Selection methods
        self.raycast_selector = RaycastSelector()
        self.box_selector = BoxSelector()
        self.frustum_selector = FrustumSelector()

        # Selection callbacks
        self.selection_callbacks = []

    def add_object(self, obj: SelectableObject):
        """Add object to selection system."""
        self.objects[obj.id] = obj

    def remove_object(self, obj_id: str):
        """Remove object from selection system."""
        if obj_id in self.objects:
            del self.objects[obj_id]
        self.selected_objects.discard(obj_id)

    def set_selection_mode(self, mode: SelectionMode):
        """Set the selection mode."""
        self.selection_mode = mode

    def select_by_ray(self, ray: Ray, max_distance: float = float("inf")) -> List[str]:
        """Select objects using ray casting."""
        objects_list = list(self.objects.values())
        selected_objects = self.raycast_selector.select(objects_list, ray, max_distance)

        selected_ids = [obj.id for obj in selected_objects]
        self._update_selection(selected_ids)
        return selected_ids

    def select_by_screen_point(
        self,
        screen_x: float,
        screen_y: float,
        viewport_width: int,
        viewport_height: int,
        view_matrix: np.ndarray,
        projection_matrix: np.ndarray,
    ) -> List[str]:
        """Select objects by screen point."""
        ray = self.raycast_selector.create_ray_from_screen(
            screen_x,
            screen_y,
            viewport_width,
            viewport_height,
            view_matrix,
            projection_matrix,
        )
        return self.select_by_ray(ray)

    def select_by_box(
        self, min_corner: np.ndarray, max_corner: np.ndarray
    ) -> List[str]:
        """Select objects within bounding box."""
        objects_list = list(self.objects.values())
        selected_objects = self.box_selector.select(
            objects_list, min_corner, max_corner
        )

        selected_ids = [obj.id for obj in selected_objects]
        self._update_selection(selected_ids)
        return selected_ids

    def select_by_screen_box(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        viewport_width: int,
        viewport_height: int,
        view_matrix: np.ndarray,
        projection_matrix: np.ndarray,
    ) -> List[str]:
        """Select objects by screen rectangle."""
        selection_box = self.box_selector.create_box_from_screen(
            start_x,
            start_y,
            end_x,
            end_y,
            viewport_width,
            viewport_height,
            view_matrix,
            projection_matrix,
        )
        return self.select_by_box(selection_box.min_point, selection_box.max_point)

    def select_in_frustum(
        self, view_matrix: np.ndarray, projection_matrix: np.ndarray
    ) -> List[str]:
        """Select all objects visible in camera frustum."""
        self.frustum_selector.set_frustum_from_camera(view_matrix, projection_matrix)
        objects_list = list(self.objects.values())
        selected_objects = self.frustum_selector.select(objects_list)

        selected_ids = [obj.id for obj in selected_objects]
        self._update_selection(selected_ids)
        return selected_ids

    def get_selected_objects(self) -> List[SelectableObject]:
        """Get currently selected objects."""
        return [
            self.objects[obj_id]
            for obj_id in self.selected_objects
            if obj_id in self.objects
        ]

    def is_selected(self, obj_id: str) -> bool:
        """Check if object is selected."""
        return obj_id in self.selected_objects

    def clear_selection(self):
        """Clear all selections."""
        old_selection = self.selected_objects.copy()
        self.selected_objects.clear()
        self._notify_selection_changed(old_selection, set())

    def toggle_selection(self, obj_id: str):
        """Toggle selection state of object."""
        if obj_id in self.selected_objects:
            self.selected_objects.remove(obj_id)
        else:
            self.selected_objects.add(obj_id)

        self._notify_selection_changed(set(), {obj_id})

    def add_selection_callback(self, callback):
        """Add callback for selection changes."""
        self.selection_callbacks.append(callback)

    def remove_selection_callback(self, callback):
        """Remove selection callback."""
        if callback in self.selection_callbacks:
            self.selection_callbacks.remove(callback)

    def _update_selection(self, new_selected_ids: List[str]):
        """Update selection based on mode."""
        old_selection = self.selected_objects.copy()

        if self.selection_mode == SelectionMode.SINGLE:
            self.selected_objects.clear()
            if new_selected_ids:
                self.selected_objects.add(new_selected_ids[0])

        elif self.selection_mode == SelectionMode.MULTIPLE:
            self.selected_objects.clear()
            self.selected_objects.update(new_selected_ids)

        elif self.selection_mode == SelectionMode.ADDITIVE:
            self.selected_objects.update(new_selected_ids)

        elif self.selection_mode == SelectionMode.SUBTRACTIVE:
            for obj_id in new_selected_ids:
                self.selected_objects.discard(obj_id)

        self._notify_selection_changed(old_selection, self.selected_objects)

    def _notify_selection_changed(
        self, old_selection: Set[str], new_selection: Set[str]
    ):
        """Notify callbacks of selection changes."""
        for callback in self.selection_callbacks:
            try:
                callback(old_selection, new_selection)
            except Exception as e:
                print(f"Error in selection callback: {e}")


class SelectionHighlighter:
    """Handles visual highlighting of selected objects."""

    def __init__(self):
        self.highlight_color = np.array([1.0, 0.5, 0.0])  # Orange
        self.outline_width = 2.0
        self.highlight_intensity = 0.3

    def highlight_objects(
        self, objects: List[SelectableObject], rendering_context: Any = None
    ):
        """Apply visual highlighting to selected objects."""
        # This would integrate with the rendering system
        # Implementation depends on the specific renderer being used
        pass

    def create_outline_effect(
        self, obj: SelectableObject, rendering_context: Any = None
    ):
        """Create outline effect for object."""
        # Implementation would depend on rendering backend
        pass

    def create_glow_effect(self, obj: SelectableObject, rendering_context: Any = None):
        """Create glow effect for object."""
        # Implementation would depend on rendering backend
        pass
