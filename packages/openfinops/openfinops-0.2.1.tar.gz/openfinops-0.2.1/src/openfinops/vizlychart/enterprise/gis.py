"""
Enterprise GIS & Geospatial Analytics Engine
===========================================

Advanced geospatial visualization and analytics for enterprise applications
including mapping, spatial analysis, and location-based business intelligence.
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

import json
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

import numpy as np
try:
    import geopandas as gpd
    import shapely.geometry as geom
    from shapely.ops import transform
    import pyproj
    HAS_GIS_LIBS = True
except ImportError:
    HAS_GIS_LIBS = False
    warnings.warn("GIS libraries not available. Install with: pip install geopandas shapely pyproj")

from ..charts.base import BaseChart


class MapProvider(Enum):
    """Supported map tile providers."""
    OPENSTREETMAP = "osm"
    MAPBOX = "mapbox"
    GOOGLE_MAPS = "google"
    ESRI_WORLD = "esri_world"
    CARTODB = "cartodb"
    STAMEN = "stamen"


class CoordinateSystem(Enum):
    """Common coordinate reference systems."""
    WGS84 = "EPSG:4326"  # GPS coordinates
    WEB_MERCATOR = "EPSG:3857"  # Web mapping standard
    UTM_ZONE_10N = "EPSG:32610"  # UTM Zone 10 North (US West Coast)
    STATE_PLANE_CA = "EPSG:2227"  # California State Plane
    BRITISH_NATIONAL_GRID = "EPSG:27700"  # UK grid system


@dataclass
class GeoLocation:
    """Geographic location with coordinate system support."""
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    coordinate_system: CoordinateSystem = CoordinateSystem.WGS84
    accuracy: Optional[float] = None  # meters
    timestamp: Optional[str] = None


@dataclass
class BoundingBox:
    """Geographic bounding box for map regions."""
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
    coordinate_system: CoordinateSystem = CoordinateSystem.WGS84


@dataclass
class SpatialAnalysisResult:
    """Results from spatial analysis operations."""
    operation: str
    input_geometries: List[str]
    result_geometry: Optional[Any] = None
    result_value: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnterpriseGISEngine:
    """
    Comprehensive GIS engine for enterprise geospatial visualization and analysis.

    Features:
    - Multi-provider map tile support
    - Coordinate system transformations
    - Spatial analysis operations
    - Real-time location tracking
    - Geofencing and proximity alerts
    - Custom map styling
    """

    def __init__(self, default_provider: MapProvider = MapProvider.OPENSTREETMAP):
        self.default_provider = default_provider
        self.map_providers = {
            MapProvider.OPENSTREETMAP: {
                "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "attribution": "© OpenStreetMap contributors",
                "max_zoom": 19
            },
            MapProvider.MAPBOX: {
                "url": "https://api.mapbox.com/styles/v1/{style_id}/tiles/{z}/{x}/{y}",
                "attribution": "© Mapbox © OpenStreetMap",
                "max_zoom": 22,
                "requires_api_key": True
            },
            MapProvider.ESRI_WORLD: {
                "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                "attribution": "© Esri © DigitalGlobe © GeoEye",
                "max_zoom": 19
            }
        }
        self.api_keys: Dict[MapProvider, str] = {}
        self.spatial_engine = SpatialAnalyticsEngine()

    def set_api_key(self, provider: MapProvider, api_key: str) -> None:
        """Set API key for commercial map providers."""
        self.api_keys[provider] = api_key

    def create_base_map(self, center: GeoLocation, zoom_level: int = 10,
                       width: int = 800, height: int = 600,
                       provider: Optional[MapProvider] = None) -> "MapChart":
        """
        Create base map with specified center and zoom level.
        """
        provider = provider or self.default_provider

        return MapChart(
            center=center,
            zoom_level=zoom_level,
            width=width,
            height=height,
            provider=provider,
            gis_engine=self
        )

    def create_choropleth_map(self, geodata: Dict[str, Any], values: Dict[str, float],
                             color_scheme: str = "viridis") -> "ChoroplethChart":
        """
        Create choropleth (filled polygon) map for regional data visualization.
        """
        return ChoroplethChart(
            geodata=geodata,
            values=values,
            color_scheme=color_scheme,
            gis_engine=self
        )

    def create_heat_map(self, locations: List[GeoLocation], values: Optional[List[float]] = None,
                       radius: float = 25, blur: float = 15) -> "HeatMapChart":
        """
        Create density heat map from point locations.
        """
        return HeatMapChart(
            locations=locations,
            values=values,
            radius=radius,
            blur=blur,
            gis_engine=self
        )

    def create_route_map(self, waypoints: List[GeoLocation],
                        optimization: str = "fastest") -> "RouteMapChart":
        """
        Create route visualization with turn-by-turn directions.
        """
        return RouteMapChart(
            waypoints=waypoints,
            optimization=optimization,
            gis_engine=self
        )

    def transform_coordinates(self, coordinates: List[Tuple[float, float]],
                            source_crs: CoordinateSystem,
                            target_crs: CoordinateSystem) -> List[Tuple[float, float]]:
        """
        Transform coordinates between different coordinate reference systems.
        """
        if not HAS_GIS_LIBS:
            warnings.warn("Coordinate transformation requires geopandas and pyproj")
            return coordinates

        transformer = pyproj.Transformer.from_crs(source_crs.value, target_crs.value, always_xy=True)
        return [transformer.transform(lon, lat) for lon, lat in coordinates]

    def calculate_distance(self, point1: GeoLocation, point2: GeoLocation,
                          method: str = "haversine") -> float:
        """
        Calculate distance between two geographic points.

        Args:
            point1: First location
            point2: Second location
            method: Distance calculation method ("haversine", "vincenty", "euclidean")

        Returns:
            Distance in meters
        """
        if method == "haversine":
            return self._haversine_distance(point1, point2)
        elif method == "euclidean":
            # Simple Euclidean distance (less accurate for long distances)
            lat_diff = point2.latitude - point1.latitude
            lon_diff = point2.longitude - point1.longitude
            return math.sqrt(lat_diff**2 + lon_diff**2) * 111319.9  # Approximate meters per degree
        else:
            warnings.warn(f"Distance method '{method}' not implemented, using haversine")
            return self._haversine_distance(point1, point2)

    def _haversine_distance(self, point1: GeoLocation, point2: GeoLocation) -> float:
        """
        Calculate haversine distance between two points on Earth's surface.
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lon1 = math.radians(point1.latitude), math.radians(point1.longitude)
        lat2, lon2 = math.radians(point2.latitude), math.radians(point2.longitude)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Radius of Earth in meters
        earth_radius = 6371000
        return earth_radius * c


class SpatialAnalyticsEngine:
    """
    Advanced spatial analysis operations for enterprise GIS applications.
    """

    def __init__(self):
        self.analysis_cache: Dict[str, SpatialAnalysisResult] = {}

    def buffer_analysis(self, geometries: List[Any], buffer_distance: float,
                       units: str = "meters") -> SpatialAnalysisResult:
        """
        Create buffer zones around geographic features.
        """
        if not HAS_GIS_LIBS:
            return SpatialAnalysisResult(
                operation="buffer",
                input_geometries=[str(g) for g in geometries],
                metadata={"error": "GIS libraries not available"}
            )

        try:
            # Convert to GeoDataFrame for analysis
            gdf = gpd.GeoDataFrame(geometry=geometries)

            # Apply buffer
            if units == "meters":
                # Project to UTM for accurate meter-based buffers
                utm_crs = gdf.estimate_utm_crs()
                gdf_projected = gdf.to_crs(utm_crs)
                buffered = gdf_projected.buffer(buffer_distance)
                result_geometry = buffered.to_crs("EPSG:4326")  # Back to WGS84
            else:
                # Assume degrees for geographic buffers
                result_geometry = gdf.buffer(buffer_distance)

            return SpatialAnalysisResult(
                operation="buffer",
                input_geometries=[str(g) for g in geometries],
                result_geometry=result_geometry,
                metadata={
                    "buffer_distance": buffer_distance,
                    "units": units,
                    "feature_count": len(result_geometry)
                }
            )

        except Exception as e:
            return SpatialAnalysisResult(
                operation="buffer",
                input_geometries=[str(g) for g in geometries],
                metadata={"error": str(e)}
            )

    def intersection_analysis(self, layer1: List[Any], layer2: List[Any]) -> SpatialAnalysisResult:
        """
        Find intersections between two sets of geographic features.
        """
        if not HAS_GIS_LIBS:
            return SpatialAnalysisResult(
                operation="intersection",
                input_geometries=[str(layer1), str(layer2)],
                metadata={"error": "GIS libraries not available"}
            )

        try:
            gdf1 = gpd.GeoDataFrame(geometry=layer1)
            gdf2 = gpd.GeoDataFrame(geometry=layer2)

            # Perform spatial intersection
            intersections = gpd.overlay(gdf1, gdf2, how='intersection')

            return SpatialAnalysisResult(
                operation="intersection",
                input_geometries=[f"layer1({len(layer1)})", f"layer2({len(layer2)})"],
                result_geometry=intersections.geometry,
                metadata={
                    "intersection_count": len(intersections),
                    "total_area": intersections.geometry.area.sum() if len(intersections) > 0 else 0
                }
            )

        except Exception as e:
            return SpatialAnalysisResult(
                operation="intersection",
                input_geometries=[f"layer1({len(layer1)})", f"layer2({len(layer2)})"],
                metadata={"error": str(e)}
            )

    def proximity_analysis(self, points: List[GeoLocation], features: List[Any],
                          max_distance: float = 1000) -> SpatialAnalysisResult:
        """
        Find features within specified distance of points.
        """
        if not HAS_GIS_LIBS:
            return SpatialAnalysisResult(
                operation="proximity",
                input_geometries=[f"points({len(points)})", f"features({len(features)})"],
                metadata={"error": "GIS libraries not available"}
            )

        try:
            # Convert points to GeoDataFrame
            point_geoms = [geom.Point(p.longitude, p.latitude) for p in points]
            points_gdf = gpd.GeoDataFrame(geometry=point_geoms, crs="EPSG:4326")

            # Convert features to GeoDataFrame
            features_gdf = gpd.GeoDataFrame(geometry=features, crs="EPSG:4326")

            # Project to UTM for accurate distance calculations
            utm_crs = points_gdf.estimate_utm_crs()
            points_projected = points_gdf.to_crs(utm_crs)
            features_projected = features_gdf.to_crs(utm_crs)

            # Find features within distance
            nearby_features = []
            for point_geom in points_projected.geometry:
                buffer_zone = point_geom.buffer(max_distance)
                intersecting = features_projected[features_projected.intersects(buffer_zone)]
                nearby_features.extend(intersecting.index.tolist())

            # Remove duplicates
            unique_nearby = list(set(nearby_features))

            return SpatialAnalysisResult(
                operation="proximity",
                input_geometries=[f"points({len(points)})", f"features({len(features)})"],
                result_value=len(unique_nearby),
                metadata={
                    "max_distance": max_distance,
                    "nearby_feature_indices": unique_nearby,
                    "total_nearby_features": len(unique_nearby)
                }
            )

        except Exception as e:
            return SpatialAnalysisResult(
                operation="proximity",
                input_geometries=[f"points({len(points)})", f"features({len(features)})"],
                metadata={"error": str(e)}
            )

    def density_analysis(self, points: List[GeoLocation], grid_size: float = 1000,
                        radius: float = 5000) -> SpatialAnalysisResult:
        """
        Calculate point density using kernel density estimation.
        """
        try:
            # Create density grid
            all_lats = [p.latitude for p in points]
            all_lons = [p.longitude for p in points]

            lat_min, lat_max = min(all_lats), max(all_lats)
            lon_min, lon_max = min(all_lons), max(all_lons)

            # Convert grid size from meters to degrees (approximate)
            grid_size_deg = grid_size / 111319.9

            # Create grid
            lat_grid = np.arange(lat_min, lat_max + grid_size_deg, grid_size_deg)
            lon_grid = np.arange(lon_min, lon_max + grid_size_deg, grid_size_deg)

            density_values = []
            grid_points = []

            for lat in lat_grid:
                for lon in lon_grid:
                    grid_point = GeoLocation(lat, lon)
                    grid_points.append(grid_point)

                    # Count points within radius
                    count = 0
                    for point in points:
                        distance = self._calculate_distance(grid_point, point)
                        if distance <= radius:
                            # Use Gaussian kernel for smooth density
                            weight = math.exp(-(distance ** 2) / (2 * (radius / 3) ** 2))
                            count += weight

                    density_values.append(count)

            return SpatialAnalysisResult(
                operation="density",
                input_geometries=[f"points({len(points)})"],
                result_value=max(density_values) if density_values else 0,
                metadata={
                    "grid_size": grid_size,
                    "radius": radius,
                    "grid_points": len(grid_points),
                    "max_density": max(density_values) if density_values else 0,
                    "avg_density": sum(density_values) / len(density_values) if density_values else 0
                }
            )

        except Exception as e:
            return SpatialAnalysisResult(
                operation="density",
                input_geometries=[f"points({len(points)})"],
                metadata={"error": str(e)}
            )

    def _calculate_distance(self, point1: GeoLocation, point2: GeoLocation) -> float:
        """Helper method for distance calculation."""
        # Simple haversine distance
        lat1, lon1 = math.radians(point1.latitude), math.radians(point1.longitude)
        lat2, lon2 = math.radians(point2.latitude), math.radians(point2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return 6371000 * c  # Earth radius in meters


# Enterprise GIS Chart Types
class MapChart(BaseChart):
    """Base interactive map chart with enterprise features."""

    def __init__(self, center: GeoLocation, zoom_level: int,
                 width: int, height: int, provider: MapProvider,
                 gis_engine: EnterpriseGISEngine, **kwargs):
        super().__init__(**kwargs)
        self.center = center
        self.zoom_level = zoom_level
        self.width = width
        self.height = height
        self.provider = provider
        self.gis_engine = gis_engine
        self.layers: List[Dict[str, Any]] = []

    def add_marker_layer(self, locations: List[GeoLocation], labels: Optional[List[str]] = None,
                        icon: str = "default", size: str = "medium") -> None:
        """Add marker layer to map."""
        self.layers.append({
            "type": "markers",
            "locations": locations,
            "labels": labels or [f"Point {i+1}" for i in range(len(locations))],
            "icon": icon,
            "size": size
        })

    def add_polygon_layer(self, polygons: List[Any], fill_color: str = "blue",
                         fill_opacity: float = 0.3, stroke_color: str = "blue",
                         stroke_width: int = 2) -> None:
        """Add polygon layer to map."""
        self.layers.append({
            "type": "polygons",
            "polygons": polygons,
            "fill_color": fill_color,
            "fill_opacity": fill_opacity,
            "stroke_color": stroke_color,
            "stroke_width": stroke_width
        })

    def add_heatmap_layer(self, points: List[GeoLocation], values: Optional[List[float]] = None,
                         radius: float = 25, max_zoom: int = 18) -> None:
        """Add heatmap layer to map."""
        self.layers.append({
            "type": "heatmap",
            "points": points,
            "values": values,
            "radius": radius,
            "max_zoom": max_zoom
        })


class ChoroplethChart(MapChart):
    """Choropleth map for regional data visualization."""

    def __init__(self, geodata: Dict[str, Any], values: Dict[str, float],
                 color_scheme: str, gis_engine: EnterpriseGISEngine, **kwargs):
        # Calculate appropriate center and zoom from geodata bounds
        center = GeoLocation(0, 0)  # TODO: Calculate from geodata
        super().__init__(center, 5, 800, 600, MapProvider.OPENSTREETMAP, gis_engine, **kwargs)
        self.geodata = geodata
        self.values = values
        self.color_scheme = color_scheme

    def update_values(self, new_values: Dict[str, float]) -> None:
        """Update choropleth values for dynamic visualization."""
        self.values.update(new_values)


class HeatMapChart(MapChart):
    """Heat map for point density visualization."""

    def __init__(self, locations: List[GeoLocation], values: Optional[List[float]],
                 radius: float, blur: float, gis_engine: EnterpriseGISEngine, **kwargs):
        # Calculate center from locations
        if locations:
            center_lat = sum(loc.latitude for loc in locations) / len(locations)
            center_lon = sum(loc.longitude for loc in locations) / len(locations)
            center = GeoLocation(center_lat, center_lon)
        else:
            center = GeoLocation(0, 0)

        super().__init__(center, 10, 800, 600, MapProvider.OPENSTREETMAP, gis_engine, **kwargs)
        self.locations = locations
        self.values = values
        self.radius = radius
        self.blur = blur


class RouteMapChart(MapChart):
    """Route visualization with turn-by-turn directions."""

    def __init__(self, waypoints: List[GeoLocation], optimization: str,
                 gis_engine: EnterpriseGISEngine, **kwargs):
        # Calculate center from waypoints
        if waypoints:
            center_lat = sum(wp.latitude for wp in waypoints) / len(waypoints)
            center_lon = sum(wp.longitude for wp in waypoints) / len(waypoints)
            center = GeoLocation(center_lat, center_lon)
        else:
            center = GeoLocation(0, 0)

        super().__init__(center, 12, 800, 600, MapProvider.OPENSTREETMAP, gis_engine, **kwargs)
        self.waypoints = waypoints
        self.optimization = optimization
        self.route_data: Optional[Dict[str, Any]] = None

    def calculate_route(self) -> Dict[str, Any]:
        """Calculate optimal route between waypoints."""
        # Placeholder for route calculation
        # In production, this would use routing services like:
        # - Google Directions API
        # - Mapbox Directions API
        # - OSRM (Open Source Routing Machine)
        # - HERE Routing API

        total_distance = 0
        for i in range(len(self.waypoints) - 1):
            distance = self.gis_engine.calculate_distance(
                self.waypoints[i], self.waypoints[i + 1]
            )
            total_distance += distance

        self.route_data = {
            "waypoints": self.waypoints,
            "total_distance": total_distance,
            "estimated_time": total_distance / 15000,  # Rough estimate (m/s to hours)
            "optimization": self.optimization
        }

        return self.route_data


# Real-time Tracking & Fleet Management
@dataclass
class TrackedAsset:
    """Represents a tracked asset (vehicle, person, equipment)."""
    asset_id: str
    asset_type: str
    current_location: GeoLocation
    last_update: str
    speed: Optional[float] = None  # km/h
    heading: Optional[float] = None  # degrees
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Geofence:
    """Geographic boundary for asset monitoring."""
    fence_id: str
    name: str
    boundary: Any  # Shapely geometry (Polygon, Circle)
    fence_type: str = "inclusion"  # "inclusion" or "exclusion"
    alerts_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeofenceAlert:
    """Alert when asset enters/exits geofence."""
    alert_id: str
    asset_id: str
    fence_id: str
    alert_type: str  # "entry", "exit", "dwell"
    timestamp: str
    location: GeoLocation
    message: str


class RealTimeTracker:
    """
    Real-time asset tracking and fleet management system.

    Features:
    - Live asset position tracking
    - Geofencing with entry/exit alerts
    - Route optimization for fleet management
    - Historical movement analysis
    - Real-time dashboard updates
    """

    def __init__(self, gis_engine: EnterpriseGISEngine):
        self.gis_engine = gis_engine
        self.tracked_assets: Dict[str, TrackedAsset] = {}
        self.geofences: Dict[str, Geofence] = {}
        self.alerts: List[GeofenceAlert] = []
        self.update_callbacks: List[callable] = []

    def register_asset(self, asset: TrackedAsset) -> None:
        """Register new asset for tracking."""
        self.tracked_assets[asset.asset_id] = asset

    def update_asset_location(self, asset_id: str, location: GeoLocation,
                             speed: Optional[float] = None, heading: Optional[float] = None) -> None:
        """Update asset location and trigger geofence checks."""
        if asset_id not in self.tracked_assets:
            raise ValueError(f"Asset {asset_id} not registered")

        asset = self.tracked_assets[asset_id]
        old_location = asset.current_location

        # Update asset location
        asset.current_location = location
        asset.speed = speed
        asset.heading = heading
        asset.last_update = "now"  # In production, use proper timestamp

        # Check geofences
        self._check_geofences(asset_id, old_location, location)

        # Notify callbacks
        for callback in self.update_callbacks:
            callback(asset)

    def create_geofence(self, fence_id: str, name: str, center: GeoLocation,
                       radius: float, fence_type: str = "inclusion") -> Geofence:
        """
        Create circular geofence.

        Args:
            fence_id: Unique identifier
            name: Human-readable name
            center: Center point
            radius: Radius in meters
            fence_type: "inclusion" or "exclusion"
        """
        if not HAS_GIS_LIBS:
            warnings.warn("Geofencing requires shapely geometry library")
            return None

        # Create circular boundary
        center_point = geom.Point(center.longitude, center.latitude)

        # Convert radius from meters to degrees (approximate)
        radius_deg = radius / 111319.9
        boundary = center_point.buffer(radius_deg)

        fence = Geofence(
            fence_id=fence_id,
            name=name,
            boundary=boundary,
            fence_type=fence_type
        )

        self.geofences[fence_id] = fence
        return fence

    def create_polygon_geofence(self, fence_id: str, name: str,
                               coordinates: List[Tuple[float, float]],
                               fence_type: str = "inclusion") -> Geofence:
        """Create polygon geofence from coordinates."""
        if not HAS_GIS_LIBS:
            warnings.warn("Geofencing requires shapely geometry library")
            return None

        boundary = geom.Polygon(coordinates)
        fence = Geofence(
            fence_id=fence_id,
            name=name,
            boundary=boundary,
            fence_type=fence_type
        )

        self.geofences[fence_id] = fence
        return fence

    def _check_geofences(self, asset_id: str, old_location: GeoLocation, new_location: GeoLocation) -> None:
        """Check if asset has crossed any geofence boundaries."""
        if not HAS_GIS_LIBS:
            return

        old_point = geom.Point(old_location.longitude, old_location.latitude)
        new_point = geom.Point(new_location.longitude, new_location.latitude)

        for fence_id, fence in self.geofences.items():
            if not fence.alerts_enabled:
                continue

            old_inside = fence.boundary.contains(old_point)
            new_inside = fence.boundary.contains(new_point)

            # Detect entry/exit
            if not old_inside and new_inside:
                # Entry
                alert = GeofenceAlert(
                    alert_id=f"{asset_id}_{fence_id}_entry_{len(self.alerts)}",
                    asset_id=asset_id,
                    fence_id=fence_id,
                    alert_type="entry",
                    timestamp="now",
                    location=new_location,
                    message=f"Asset {asset_id} entered geofence {fence.name}"
                )
                self.alerts.append(alert)

            elif old_inside and not new_inside:
                # Exit
                alert = GeofenceAlert(
                    alert_id=f"{asset_id}_{fence_id}_exit_{len(self.alerts)}",
                    asset_id=asset_id,
                    fence_id=fence_id,
                    alert_type="exit",
                    timestamp="now",
                    location=new_location,
                    message=f"Asset {asset_id} exited geofence {fence.name}"
                )
                self.alerts.append(alert)

    def get_assets_in_area(self, center: GeoLocation, radius: float) -> List[TrackedAsset]:
        """Get all assets within specified area."""
        assets_in_area = []

        for asset in self.tracked_assets.values():
            distance = self.gis_engine.calculate_distance(center, asset.current_location)
            if distance <= radius:
                assets_in_area.append(asset)

        return assets_in_area

    def get_asset_history(self, asset_id: str, time_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """Get historical movement data for asset."""
        # Placeholder for historical data retrieval
        # In production, this would query a time-series database
        if asset_id not in self.tracked_assets:
            return {"error": f"Asset {asset_id} not found"}

        return {
            "asset_id": asset_id,
            "current_location": self.tracked_assets[asset_id].current_location,
            "total_alerts": len([a for a in self.alerts if a.asset_id == asset_id]),
            "status": self.tracked_assets[asset_id].status
        }

    def optimize_fleet_routes(self, vehicles: List[str], destinations: List[GeoLocation],
                             constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize routes for fleet of vehicles.

        This is a simplified implementation. Production systems would use:
        - Vehicle Routing Problem (VRP) algorithms
        - Time windows and capacity constraints
        - Real-time traffic data
        - Machine learning for demand prediction
        """
        if not vehicles or not destinations:
            return {"error": "No vehicles or destinations provided"}

        # Simple nearest-neighbor assignment
        assignments = {}
        remaining_destinations = destinations.copy()

        for vehicle_id in vehicles:
            if not remaining_destinations:
                break

            if vehicle_id not in self.tracked_assets:
                continue

            vehicle_location = self.tracked_assets[vehicle_id].current_location

            # Find nearest destination
            min_distance = float('inf')
            nearest_dest = None
            nearest_idx = -1

            for i, dest in enumerate(remaining_destinations):
                distance = self.gis_engine.calculate_distance(vehicle_location, dest)
                if distance < min_distance:
                    min_distance = distance
                    nearest_dest = dest
                    nearest_idx = i

            if nearest_dest:
                assignments[vehicle_id] = {
                    "destination": nearest_dest,
                    "distance": min_distance,
                    "estimated_time": min_distance / 15000  # Rough time estimate
                }
                remaining_destinations.pop(nearest_idx)

        return {
            "assignments": assignments,
            "unassigned_destinations": remaining_destinations,
            "total_distance": sum(a["distance"] for a in assignments.values()),
            "optimization_method": "nearest_neighbor"
        }

    def register_update_callback(self, callback: callable) -> None:
        """Register callback for real-time updates."""
        self.update_callbacks.append(callback)

    def get_live_dashboard_data(self) -> Dict[str, Any]:
        """Get data for real-time dashboard display."""
        return {
            "total_assets": len(self.tracked_assets),
            "active_assets": len([a for a in self.tracked_assets.values() if a.status == "active"]),
            "total_geofences": len(self.geofences),
            "recent_alerts": self.alerts[-10:],  # Last 10 alerts
            "assets": list(self.tracked_assets.values()),
            "geofences": list(self.geofences.values())
        }