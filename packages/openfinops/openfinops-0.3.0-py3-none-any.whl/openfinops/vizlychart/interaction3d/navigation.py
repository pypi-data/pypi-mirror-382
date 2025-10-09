"""
3D Navigation System
Provides path planning, waypoint navigation, and automated camera movements.
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
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import heapq


class NavigationMode(Enum):
    """Navigation mode types."""

    FREE_FLIGHT = "free_flight"
    ORBIT = "orbit"
    GUIDED_TOUR = "guided_tour"
    WAYPOINT_FOLLOW = "waypoint_follow"
    PATH_CONSTRAINED = "path_constrained"


@dataclass
class Waypoint:
    """Navigation waypoint with position, orientation, and metadata."""

    position: np.ndarray
    orientation: np.ndarray = field(
        default_factory=lambda: np.array([0, 0, 0, 1])
    )  # Quaternion
    name: str = ""
    description: str = ""
    duration: float = 2.0  # Time to stay at waypoint
    transition_time: float = 1.0  # Time to travel to this waypoint
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_pose_matrix(self) -> np.ndarray:
        """Convert waypoint to 4x4 pose matrix."""
        # Convert quaternion to rotation matrix
        q = self.orientation
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

        rotation_matrix[:3, 3] = self.position
        return rotation_matrix

    @classmethod
    def from_position_target(
        cls, position: np.ndarray, target: np.ndarray, up: np.ndarray = None
    ) -> "Waypoint":
        """Create waypoint from position and target."""
        if up is None:
            up = np.array([0, 1, 0])

        # Calculate look-at orientation
        forward = target - position
        forward = forward / np.linalg.norm(forward)

        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)

        up = np.cross(right, forward)

        # Create rotation matrix
        rotation_matrix = np.column_stack([right, up, -forward])

        # Convert to quaternion
        orientation = cls._matrix_to_quaternion(rotation_matrix)

        return cls(position=position, orientation=orientation)

    @staticmethod
    def _matrix_to_quaternion(rotation_matrix: np.ndarray) -> np.ndarray:
        """Convert rotation matrix to quaternion."""
        trace = np.trace(rotation_matrix)

        if trace > 0:
            s = np.sqrt(trace + 1.0) * 2  # s = 4 * qw
            qw = 0.25 * s
            qx = (rotation_matrix[2, 1] - rotation_matrix[1, 2]) / s
            qy = (rotation_matrix[0, 2] - rotation_matrix[2, 0]) / s
            qz = (rotation_matrix[1, 0] - rotation_matrix[0, 1]) / s
        elif (
            rotation_matrix[0, 0] > rotation_matrix[1, 1]
            and rotation_matrix[0, 0] > rotation_matrix[2, 2]
        ):
            s = (
                np.sqrt(
                    1.0
                    + rotation_matrix[0, 0]
                    - rotation_matrix[1, 1]
                    - rotation_matrix[2, 2]
                )
                * 2
            )
            qw = (rotation_matrix[2, 1] - rotation_matrix[1, 2]) / s
            qx = 0.25 * s
            qy = (rotation_matrix[0, 1] + rotation_matrix[1, 0]) / s
            qz = (rotation_matrix[0, 2] + rotation_matrix[2, 0]) / s
        elif rotation_matrix[1, 1] > rotation_matrix[2, 2]:
            s = (
                np.sqrt(
                    1.0
                    + rotation_matrix[1, 1]
                    - rotation_matrix[0, 0]
                    - rotation_matrix[2, 2]
                )
                * 2
            )
            qw = (rotation_matrix[0, 2] - rotation_matrix[2, 0]) / s
            qx = (rotation_matrix[0, 1] + rotation_matrix[1, 0]) / s
            qy = 0.25 * s
            qz = (rotation_matrix[1, 2] + rotation_matrix[2, 1]) / s
        else:
            s = (
                np.sqrt(
                    1.0
                    + rotation_matrix[2, 2]
                    - rotation_matrix[0, 0]
                    - rotation_matrix[1, 1]
                )
                * 2
            )
            qw = (rotation_matrix[1, 0] - rotation_matrix[0, 1]) / s
            qx = (rotation_matrix[0, 2] + rotation_matrix[2, 0]) / s
            qy = (rotation_matrix[1, 2] + rotation_matrix[2, 1]) / s
            qz = 0.25 * s

        return np.array([qx, qy, qz, qw])


@dataclass
class NavMeshNode:
    """Navigation mesh node for pathfinding."""

    id: int
    position: np.ndarray
    connections: List[int] = field(default_factory=list)
    traversal_cost: float = 1.0
    is_walkable: bool = True


class PathPlanner:
    """Advanced pathfinding and route planning system."""

    def __init__(self):
        self.nav_mesh: Dict[int, NavMeshNode] = {}
        self.obstacles: List[Dict[str, Any]] = []
        self.path_smoothing_enabled = True
        self.path_optimization_enabled = True

    def add_nav_node(self, node: NavMeshNode):
        """Add navigation mesh node."""
        self.nav_mesh[node.id] = node

    def connect_nodes(self, node_id1: int, node_id2: int, bidirectional: bool = True):
        """Connect two navigation nodes."""
        if node_id1 in self.nav_mesh and node_id2 in self.nav_mesh:
            self.nav_mesh[node_id1].connections.append(node_id2)
            if bidirectional:
                self.nav_mesh[node_id2].connections.append(node_id1)

    def add_obstacle(self, center: np.ndarray, radius: float, height: float = None):
        """Add spherical or cylindrical obstacle."""
        obstacle = {
            "center": center,
            "radius": radius,
            "height": height,
            "type": "cylinder" if height is not None else "sphere",
        }
        self.obstacles.append(obstacle)

    def find_path(
        self, start: np.ndarray, goal: np.ndarray, algorithm: str = "astar"
    ) -> Optional[List[np.ndarray]]:
        """Find path between two points."""
        if algorithm == "astar":
            return self._astar_pathfind(start, goal)
        elif algorithm == "dijkstra":
            return self._dijkstra_pathfind(start, goal)
        elif algorithm == "straight_line":
            return self._straight_line_path(start, goal)
        else:
            raise ValueError(f"Unknown pathfinding algorithm: {algorithm}")

    def optimize_path(self, path: List[np.ndarray]) -> List[np.ndarray]:
        """Optimize path by removing unnecessary waypoints."""
        if len(path) <= 2:
            return path

        optimized = [path[0]]
        current_index = 0

        while current_index < len(path) - 1:
            # Look ahead to find the furthest visible point
            furthest_index = current_index + 1

            for i in range(current_index + 2, len(path)):
                if self._is_line_clear(path[current_index], path[i]):
                    furthest_index = i
                else:
                    break

            optimized.append(path[furthest_index])
            current_index = furthest_index

        return optimized

    def smooth_path(
        self, path: List[np.ndarray], smoothing_factor: float = 0.5
    ) -> List[np.ndarray]:
        """Smooth path using spline interpolation."""
        if len(path) <= 2:
            return path

        smoothed = [path[0]]

        for i in range(1, len(path) - 1):
            # Calculate control points for spline
            prev_point = path[i - 1]
            current_point = path[i]
            next_point = path[i + 1]

            # Apply smoothing
            smooth_point = (
                prev_point * (1 - smoothing_factor) / 2
                + current_point * smoothing_factor
                + next_point * (1 - smoothing_factor) / 2
            )

            # Check if smoothed point is valid (no collisions)
            if self._is_point_valid(smooth_point):
                smoothed.append(smooth_point)
            else:
                smoothed.append(current_point)

        smoothed.append(path[-1])
        return smoothed

    def create_waypoints_from_path(
        self, path: List[np.ndarray], look_ahead_distance: float = 2.0
    ) -> List[Waypoint]:
        """Convert path to waypoints with proper orientations."""
        if not path:
            return []

        waypoints = []

        for i, position in enumerate(path):
            # Calculate orientation by looking ahead
            if i < len(path) - 1:
                target = path[i + 1]
            else:
                # Last waypoint looks in same direction as previous
                if i > 0:
                    direction = position - path[i - 1]
                    target = position + direction
                else:
                    target = position + np.array([0, 0, -1])  # Default forward

            waypoint = Waypoint.from_position_target(position, target)
            waypoint.name = f"Waypoint_{i}"
            waypoints.append(waypoint)

        return waypoints

    def _astar_pathfind(
        self, start: np.ndarray, goal: np.ndarray
    ) -> Optional[List[np.ndarray]]:
        """A* pathfinding algorithm."""
        # Find closest nodes to start and goal
        start_node_id = self._find_closest_node(start)
        goal_node_id = self._find_closest_node(goal)

        if start_node_id is None or goal_node_id is None:
            return self._straight_line_path(start, goal)

        # A* implementation
        open_set = [(0, start_node_id)]
        came_from = {}
        g_score = {start_node_id: 0}
        f_score = {start_node_id: self._heuristic(start_node_id, goal_node_id)}

        while open_set:
            current_f, current_id = heapq.heappop(open_set)

            if current_id == goal_node_id:
                # Reconstruct path
                path = self._reconstruct_path(came_from, current_id)
                # Add start and goal points
                node_path = [self.nav_mesh[node_id].position for node_id in path]
                return [start] + node_path + [goal]

            for neighbor_id in self.nav_mesh[current_id].connections:
                if neighbor_id not in self.nav_mesh:
                    continue

                tentative_g = g_score[current_id] + self._distance(
                    current_id, neighbor_id
                )

                if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                    came_from[neighbor_id] = current_id
                    g_score[neighbor_id] = tentative_g
                    f_score[neighbor_id] = tentative_g + self._heuristic(
                        neighbor_id, goal_node_id
                    )
                    heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))

        return None  # No path found

    def _dijkstra_pathfind(
        self, start: np.ndarray, goal: np.ndarray
    ) -> Optional[List[np.ndarray]]:
        """Dijkstra pathfinding algorithm."""
        start_node_id = self._find_closest_node(start)
        goal_node_id = self._find_closest_node(goal)

        if start_node_id is None or goal_node_id is None:
            return self._straight_line_path(start, goal)

        distances = {start_node_id: 0}
        came_from = {}
        unvisited = [(0, start_node_id)]

        while unvisited:
            current_dist, current_id = heapq.heappop(unvisited)

            if current_id == goal_node_id:
                path = self._reconstruct_path(came_from, current_id)
                node_path = [self.nav_mesh[node_id].position for node_id in path]
                return [start] + node_path + [goal]

            if current_dist > distances.get(current_id, float("inf")):
                continue

            for neighbor_id in self.nav_mesh[current_id].connections:
                if neighbor_id not in self.nav_mesh:
                    continue

                distance = current_dist + self._distance(current_id, neighbor_id)

                if distance < distances.get(neighbor_id, float("inf")):
                    distances[neighbor_id] = distance
                    came_from[neighbor_id] = current_id
                    heapq.heappush(unvisited, (distance, neighbor_id))

        return None

    def _straight_line_path(
        self, start: np.ndarray, goal: np.ndarray
    ) -> List[np.ndarray]:
        """Create straight line path with obstacle avoidance."""
        if self._is_line_clear(start, goal):
            return [start, goal]

        # Simple obstacle avoidance - go around obstacles
        path = [start]
        current = start

        while np.linalg.norm(current - goal) > 0.1:
            # Find direction to goal
            direction = goal - current
            step_size = min(1.0, np.linalg.norm(direction))
            direction = direction / np.linalg.norm(direction) * step_size

            next_point = current + direction

            # Check for obstacles
            if not self._is_line_clear(current, next_point):
                # Simple avoidance - try perpendicular directions
                perpendicular1 = np.array([-direction[1], direction[0], direction[2]])
                perpendicular2 = -perpendicular1

                avoidance_distance = 1.0
                option1 = current + perpendicular1 * avoidance_distance
                option2 = current + perpendicular2 * avoidance_distance

                if self._is_point_valid(option1):
                    next_point = option1
                elif self._is_point_valid(option2):
                    next_point = option2

            path.append(next_point)
            current = next_point

        path.append(goal)
        return path

    def _find_closest_node(self, position: np.ndarray) -> Optional[int]:
        """Find closest navigation node to position."""
        min_distance = float("inf")
        closest_node_id = None

        for node_id, node in self.nav_mesh.items():
            if not node.is_walkable:
                continue

            distance = np.linalg.norm(node.position - position)
            if distance < min_distance:
                min_distance = distance
                closest_node_id = node_id

        return closest_node_id

    def _heuristic(self, node_id1: int, node_id2: int) -> float:
        """Heuristic function for A* (Euclidean distance)."""
        pos1 = self.nav_mesh[node_id1].position
        pos2 = self.nav_mesh[node_id2].position
        return np.linalg.norm(pos2 - pos1)

    def _distance(self, node_id1: int, node_id2: int) -> float:
        """Calculate distance between two nodes."""
        node1 = self.nav_mesh[node_id1]
        node2 = self.nav_mesh[node_id2]
        base_distance = np.linalg.norm(node2.position - node1.position)
        return base_distance * node2.traversal_cost

    def _reconstruct_path(
        self, came_from: Dict[int, int], current_id: int
    ) -> List[int]:
        """Reconstruct path from came_from mapping."""
        path = [current_id]
        while current_id in came_from:
            current_id = came_from[current_id]
            path.append(current_id)
        return list(reversed(path))

    def _is_line_clear(self, start: np.ndarray, end: np.ndarray) -> bool:
        """Check if line segment is clear of obstacles."""
        direction = end - start
        distance = np.linalg.norm(direction)

        if distance < 1e-6:
            return True

        direction = direction / distance

        # Sample points along the line
        num_samples = max(2, int(distance * 10))  # 10 samples per unit
        for i in range(num_samples + 1):
            t = i / num_samples
            point = start + t * direction * distance

            if not self._is_point_valid(point):
                return False

        return True

    def _is_point_valid(self, point: np.ndarray) -> bool:
        """Check if point is valid (not inside obstacles)."""
        for obstacle in self.obstacles:
            center = obstacle["center"]
            radius = obstacle["radius"]

            if obstacle["type"] == "sphere":
                if np.linalg.norm(point - center) < radius:
                    return False
            elif obstacle["type"] == "cylinder":
                # Check horizontal distance and height
                horizontal_dist = np.linalg.norm(point[:2] - center[:2])
                height_diff = abs(point[2] - center[2])

                if horizontal_dist < radius and height_diff < obstacle["height"] / 2:
                    return False

        return True


class NavigationController:
    """High-level navigation controller combining pathfinding and camera control."""

    def __init__(self, camera_controller=None):
        self.camera_controller = camera_controller
        self.path_planner = PathPlanner()
        self.mode = NavigationMode.FREE_FLIGHT

        # Navigation state
        self.current_path: List[np.ndarray] = []
        self.current_waypoints: List[Waypoint] = []
        self.current_waypoint_index = 0
        self.is_navigating = False

        # Navigation parameters
        self.movement_speed = 5.0
        self.rotation_speed = 2.0
        self.arrival_threshold = 0.5
        self.auto_advance = True

        # Events
        self.on_waypoint_reached: Optional[Callable[[Waypoint], None]] = None
        self.on_navigation_complete: Optional[Callable[[], None]] = None
        self.on_navigation_started: Optional[Callable[[], None]] = None

    def set_mode(self, mode: NavigationMode):
        """Set navigation mode."""
        self.mode = mode

    def navigate_to_position(
        self, target_position: np.ndarray, algorithm: str = "astar"
    ) -> bool:
        """Navigate to a specific position."""
        if not self.camera_controller:
            return False

        current_position = self.camera_controller.position

        # Find path
        path = self.path_planner.find_path(current_position, target_position, algorithm)

        if path:
            # Optimize and smooth path
            if self.path_planner.path_optimization_enabled:
                path = self.path_planner.optimize_path(path)

            if self.path_planner.path_smoothing_enabled:
                path = self.path_planner.smooth_path(path)

            # Convert to waypoints
            waypoints = self.path_planner.create_waypoints_from_path(path)

            return self.follow_waypoints(waypoints)

        return False

    def navigate_to_waypoint(self, waypoint: Waypoint) -> bool:
        """Navigate to a single waypoint."""
        return self.follow_waypoints([waypoint])

    def follow_waypoints(self, waypoints: List[Waypoint]) -> bool:
        """Follow a sequence of waypoints."""
        if not waypoints or not self.camera_controller:
            return False

        self.current_waypoints = waypoints
        self.current_waypoint_index = 0
        self.is_navigating = True

        if self.on_navigation_started:
            self.on_navigation_started()

        return True

    def start_guided_tour(
        self, tour_waypoints: List[Waypoint], auto_advance: bool = True
    ) -> bool:
        """Start a guided tour through waypoints."""
        self.mode = NavigationMode.GUIDED_TOUR
        self.auto_advance = auto_advance
        return self.follow_waypoints(tour_waypoints)

    def update(self, dt: float):
        """Update navigation state."""
        if not self.is_navigating or not self.current_waypoints:
            return

        if self.current_waypoint_index >= len(self.current_waypoints):
            self._complete_navigation()
            return

        current_waypoint = self.current_waypoints[self.current_waypoint_index]
        self._navigate_to_waypoint(current_waypoint, dt)

    def pause_navigation(self):
        """Pause current navigation."""
        self.is_navigating = False

    def resume_navigation(self):
        """Resume paused navigation."""
        if self.current_waypoints:
            self.is_navigating = True

    def stop_navigation(self):
        """Stop current navigation."""
        self.is_navigating = False
        self.current_waypoints.clear()
        self.current_waypoint_index = 0

    def advance_to_next_waypoint(self):
        """Manually advance to next waypoint."""
        if self.current_waypoint_index < len(self.current_waypoints) - 1:
            self.current_waypoint_index += 1
        else:
            self._complete_navigation()

    def go_to_previous_waypoint(self):
        """Go back to previous waypoint."""
        if self.current_waypoint_index > 0:
            self.current_waypoint_index -= 1

    def create_orbit_path(
        self, center: np.ndarray, radius: float, height: float, num_points: int = 16
    ) -> List[Waypoint]:
        """Create circular orbit path around a point."""
        waypoints = []

        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = center[0] + radius * math.cos(angle)
            z = center[2] + radius * math.sin(angle)
            y = center[1] + height

            position = np.array([x, y, z])
            waypoint = Waypoint.from_position_target(position, center)
            waypoint.name = f"Orbit_{i}"
            waypoints.append(waypoint)

        return waypoints

    def create_flyby_path(
        self, targets: List[np.ndarray], viewing_distance: float = 10.0
    ) -> List[Waypoint]:
        """Create flyby path that views multiple targets."""
        waypoints = []

        for i, target in enumerate(targets):
            # Position camera at viewing distance
            if i == 0:
                direction = np.array([1, 0.5, 1])  # Default approach direction
            else:
                # Approach from direction of previous target
                prev_target = targets[i - 1]
                direction = target - prev_target

            direction = direction / np.linalg.norm(direction)
            position = target - direction * viewing_distance

            waypoint = Waypoint.from_position_target(position, target)
            waypoint.name = f"Flyby_{i}"
            waypoint.duration = 3.0  # Longer viewing time
            waypoints.append(waypoint)

        return waypoints

    def _navigate_to_waypoint(self, waypoint: Waypoint, dt: float):
        """Navigate to a specific waypoint."""
        if not self.camera_controller:
            return

        current_pos = self.camera_controller.position
        target_pos = waypoint.position

        # Calculate distance to waypoint
        distance = np.linalg.norm(target_pos - current_pos)

        if distance < self.arrival_threshold:
            # Arrived at waypoint
            if self.on_waypoint_reached:
                self.on_waypoint_reached(waypoint)

            if self.auto_advance or self.mode == NavigationMode.GUIDED_TOUR:
                self.advance_to_next_waypoint()

        else:
            # Move towards waypoint
            direction = (target_pos - current_pos) / distance
            movement = direction * self.movement_speed * dt

            # Ensure we don't overshoot
            if np.linalg.norm(movement) > distance:
                movement = direction * distance

            self.camera_controller.position += movement

            # Update camera target for smooth rotation
            target_matrix = waypoint.to_pose_matrix()
            target_forward = target_matrix[:3, 2]
            new_target = self.camera_controller.position - target_forward

            # Smoothly interpolate rotation
            current_target = self.camera_controller.target
            interpolated_target = (
                current_target
                + (new_target - current_target) * self.rotation_speed * dt
            )

            self.camera_controller.target = interpolated_target

    def _complete_navigation(self):
        """Complete the current navigation."""
        self.is_navigating = False

        if self.on_navigation_complete:
            self.on_navigation_complete()

        # Reset for next navigation
        if self.mode != NavigationMode.GUIDED_TOUR:
            self.current_waypoints.clear()
            self.current_waypoint_index = 0
