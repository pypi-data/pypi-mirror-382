"""
CAD File Import and Rendering Module
===================================

Supports importing and rendering CAD models from various formats:
- IGES (.iges, .igs)
- STEP (.step, .stp)
- STL (.stl)

Provides GPU-accelerated 3D rendering with WebXR export capabilities.
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
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    warnings.warn("trimesh not available. Install with: pip install trimesh")

try:
    import pythreejs
    THREEJS_AVAILABLE = True
except ImportError:
    THREEJS_AVAILABLE = False


@dataclass
class CADModel:
    """Represents a CAD model with geometry and metadata."""
    vertices: np.ndarray
    faces: np.ndarray
    normals: Optional[np.ndarray] = None
    colors: Optional[np.ndarray] = None
    metadata: Optional[Dict] = None
    bounds: Optional[Tuple[np.ndarray, np.ndarray]] = None

    def __post_init__(self):
        """Calculate bounds and normals if not provided."""
        if self.bounds is None:
            self.bounds = (
                np.min(self.vertices, axis=0),
                np.max(self.vertices, axis=0)
            )

        if self.normals is None and len(self.faces) > 0:
            self.normals = self._calculate_normals()

    def _calculate_normals(self) -> np.ndarray:
        """Calculate face normals from vertices and faces."""
        if len(self.faces) == 0:
            return np.array([])

        # Get vertices for each face
        v0 = self.vertices[self.faces[:, 0]]
        v1 = self.vertices[self.faces[:, 1]]
        v2 = self.vertices[self.faces[:, 2]]

        # Calculate face normals using cross product
        normal = np.cross(v1 - v0, v2 - v0)

        # Normalize
        norm_length = np.linalg.norm(normal, axis=1, keepdims=True)
        norm_length[norm_length == 0] = 1  # Avoid division by zero

        return normal / norm_length


class IGESImporter:
    """Import CAD models from IGES files."""

    def __init__(self):
        """Initialize IGES importer."""
        self.supported_extensions = ['.iges', '.igs']

    def load_file(self, file_path: Union[str, Path]) -> CADModel:
        """
        Load IGES file and return CAD model.

        Args:
            file_path: Path to IGES file

        Returns:
            CADModel object containing geometry data
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"IGES file not found: {file_path}")

        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")

        if TRIMESH_AVAILABLE:
            return self._load_with_trimesh(file_path)
        else:
            return self._load_fallback(file_path)

    def _load_with_trimesh(self, file_path: Path) -> CADModel:
        """Load IGES using trimesh library."""
        try:
            # Load mesh using trimesh
            mesh = trimesh.load(str(file_path))

            if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
                # Single mesh
                vertices = np.array(mesh.vertices, dtype=np.float32)
                faces = np.array(mesh.faces, dtype=np.int32)

                metadata = {
                    'file_path': str(file_path),
                    'format': 'IGES',
                    'volume': getattr(mesh, 'volume', 0),
                    'area': getattr(mesh, 'area', 0),
                    'is_watertight': getattr(mesh, 'is_watertight', False)
                }

                return CADModel(
                    vertices=vertices,
                    faces=faces,
                    metadata=metadata
                )
            else:
                # Multiple meshes - combine them
                all_vertices = []
                all_faces = []
                face_offset = 0

                if hasattr(mesh, 'geometry'):
                    geometries = mesh.geometry.values()
                else:
                    geometries = [mesh]

                for geom in geometries:
                    if hasattr(geom, 'vertices') and hasattr(geom, 'faces'):
                        all_vertices.append(geom.vertices)
                        faces_adjusted = geom.faces + face_offset
                        all_faces.append(faces_adjusted)
                        face_offset += len(geom.vertices)

                if all_vertices:
                    vertices = np.vstack(all_vertices).astype(np.float32)
                    faces = np.vstack(all_faces).astype(np.int32)

                    metadata = {
                        'file_path': str(file_path),
                        'format': 'IGES',
                        'num_parts': len(all_vertices)
                    }

                    return CADModel(
                        vertices=vertices,
                        faces=faces,
                        metadata=metadata
                    )
                else:
                    raise ValueError("No valid geometry found in IGES file")

        except Exception as e:
            raise RuntimeError(f"Failed to load IGES file: {e}")

    def _load_fallback(self, file_path: Path) -> CADModel:
        """Fallback loader when trimesh is not available."""
        # Create a simple geometric shape as placeholder
        warnings.warn(
            "IGES loading requires trimesh library. "
            "Install with: pip install trimesh[easy]. "
            "Generating placeholder geometry."
        )

        # Generate a simple box as placeholder
        vertices = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Bottom
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Top
        ], dtype=np.float32)

        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # Bottom
            [4, 7, 6], [4, 6, 5],  # Top
            [0, 4, 5], [0, 5, 1],  # Front
            [2, 6, 7], [2, 7, 3],  # Back
            [0, 3, 7], [0, 7, 4],  # Left
            [1, 5, 6], [1, 6, 2]   # Right
        ], dtype=np.int32)

        metadata = {
            'file_path': str(file_path),
            'format': 'IGES',
            'placeholder': True,
            'note': 'Placeholder geometry - install trimesh for actual IGES support'
        }

        return CADModel(
            vertices=vertices,
            faces=faces,
            metadata=metadata
        )


class STEPImporter:
    """Import CAD models from STEP files."""

    def __init__(self):
        """Initialize STEP importer."""
        self.supported_extensions = ['.step', '.stp']

    def load_file(self, file_path: Union[str, Path]) -> CADModel:
        """
        Load STEP file and return CAD model.

        Args:
            file_path: Path to STEP file

        Returns:
            CADModel object containing geometry data
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"STEP file not found: {file_path}")

        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")

        # Similar implementation to IGES but for STEP format
        if TRIMESH_AVAILABLE:
            return self._load_with_trimesh(file_path)
        else:
            return self._load_fallback(file_path)

    def _load_with_trimesh(self, file_path: Path) -> CADModel:
        """Load STEP using trimesh library."""
        # Implementation similar to IGES loader
        return IGESImporter()._load_with_trimesh(file_path)

    def _load_fallback(self, file_path: Path) -> CADModel:
        """Fallback loader for STEP files."""
        warnings.warn(
            "STEP loading requires trimesh library. "
            "Generating placeholder geometry."
        )

        # Generate a cylinder as placeholder for STEP
        theta = np.linspace(0, 2*np.pi, 16)
        height = 2.0
        radius = 1.0

        # Create cylinder vertices
        vertices = []
        # Bottom circle
        for t in theta:
            vertices.append([radius*np.cos(t), radius*np.sin(t), 0])
        # Top circle
        for t in theta:
            vertices.append([radius*np.cos(t), radius*np.sin(t), height])

        vertices = np.array(vertices, dtype=np.float32)

        # Create faces
        faces = []
        n = len(theta)

        # Side faces
        for i in range(n):
            j = (i + 1) % n
            # Two triangles per side face
            faces.append([i, j, j + n])
            faces.append([i, j + n, i + n])

        faces = np.array(faces, dtype=np.int32)

        metadata = {
            'file_path': str(file_path),
            'format': 'STEP',
            'placeholder': True,
            'note': 'Placeholder geometry - install trimesh for actual STEP support'
        }

        return CADModel(
            vertices=vertices,
            faces=faces,
            metadata=metadata
        )


class STLImporter:
    """Import CAD models from STL files."""

    def __init__(self):
        """Initialize STL importer."""
        self.supported_extensions = ['.stl']

    def load_file(self, file_path: Union[str, Path]) -> CADModel:
        """
        Load STL file and return CAD model.

        Args:
            file_path: Path to STL file

        Returns:
            CADModel object containing geometry data
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"STL file not found: {file_path}")

        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")

        if TRIMESH_AVAILABLE:
            return self._load_with_trimesh(file_path)
        else:
            return self._load_manual(file_path)

    def _load_with_trimesh(self, file_path: Path) -> CADModel:
        """Load STL using trimesh library."""
        try:
            mesh = trimesh.load(str(file_path))

            vertices = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.int32)

            metadata = {
                'file_path': str(file_path),
                'format': 'STL',
                'volume': getattr(mesh, 'volume', 0),
                'area': getattr(mesh, 'area', 0),
                'is_watertight': getattr(mesh, 'is_watertight', False)
            }

            return CADModel(
                vertices=vertices,
                faces=faces,
                metadata=metadata
            )

        except Exception as e:
            raise RuntimeError(f"Failed to load STL file: {e}")

    def _load_manual(self, file_path: Path) -> CADModel:
        """Manual STL loader without external dependencies."""
        try:
            return self._parse_stl_ascii(file_path)
        except:
            try:
                return self._parse_stl_binary(file_path)
            except Exception as e:
                raise RuntimeError(f"Failed to parse STL file: {e}")

    def _parse_stl_ascii(self, file_path: Path) -> CADModel:
        """Parse ASCII STL file."""
        vertices = []
        faces = []

        with open(file_path, 'r') as f:
            lines = f.readlines()

        vertex_count = 0
        current_face = []

        for line in lines:
            line = line.strip().lower()

            if line.startswith('vertex'):
                coords = [float(x) for x in line.split()[1:4]]
                vertices.append(coords)
                current_face.append(vertex_count)
                vertex_count += 1

                if len(current_face) == 3:
                    faces.append(current_face)
                    current_face = []

        vertices = np.array(vertices, dtype=np.float32)
        faces = np.array(faces, dtype=np.int32)

        metadata = {
            'file_path': str(file_path),
            'format': 'STL',
            'encoding': 'ASCII'
        }

        return CADModel(
            vertices=vertices,
            faces=faces,
            metadata=metadata
        )

    def _parse_stl_binary(self, file_path: Path) -> CADModel:
        """Parse binary STL file."""
        import struct

        with open(file_path, 'rb') as f:
            # Skip header (80 bytes)
            f.read(80)

            # Read number of triangles
            num_triangles = struct.unpack('<I', f.read(4))[0]

            vertices = []
            faces = []
            vertex_count = 0

            for i in range(num_triangles):
                # Skip normal vector (12 bytes)
                f.read(12)

                # Read 3 vertices (36 bytes total)
                triangle_vertices = []
                for j in range(3):
                    x, y, z = struct.unpack('<fff', f.read(12))
                    vertices.append([x, y, z])
                    triangle_vertices.append(vertex_count)
                    vertex_count += 1

                faces.append(triangle_vertices)

                # Skip attribute byte count (2 bytes)
                f.read(2)

        vertices = np.array(vertices, dtype=np.float32)
        faces = np.array(faces, dtype=np.int32)

        metadata = {
            'file_path': str(file_path),
            'format': 'STL',
            'encoding': 'Binary',
            'num_triangles': num_triangles
        }

        return CADModel(
            vertices=vertices,
            faces=faces,
            metadata=metadata
        )


class CADViewer:
    """3D CAD model viewer with GPU acceleration and WebXR export."""

    def __init__(self, figure=None):
        """
        Initialize CAD viewer.

        Args:
            figure: Vizly figure instance
        """
        self.figure = figure
        self.models = []
        self.materials = {}
        self.lighting = {
            'ambient': 0.4,
            'directional': 0.6,
            'specular': 0.3
        }
        self.camera_position = [5, 5, 5]
        self.camera_target = [0, 0, 0]

    def add_model(self, model: CADModel, **kwargs):
        """
        Add CAD model to viewer.

        Args:
            model: CADModel instance
            **kwargs: Rendering options (color, transparency, etc.)
        """
        rendering_options = {
            'color': kwargs.get('color', 'steel_blue'),
            'transparency': kwargs.get('transparency', 1.0),
            'edge_visibility': kwargs.get('edge_visibility', True),
            'surface_quality': kwargs.get('surface_quality', 'medium'),
            'wireframe': kwargs.get('wireframe', False)
        }

        self.models.append({
            'model': model,
            'options': rendering_options
        })

    def set_material(self, material_name: str):
        """Set material for all models."""
        materials = {
            'aluminum_brushed': {'color': '#C0C0C0', 'metallic': 0.8, 'roughness': 0.3},
            'steel_blue': {'color': '#4682B4', 'metallic': 0.7, 'roughness': 0.4},
            'copper': {'color': '#B87333', 'metallic': 0.9, 'roughness': 0.1},
            'plastic_white': {'color': '#FFFFFF', 'metallic': 0.0, 'roughness': 0.8}
        }

        if material_name in materials:
            self.current_material = materials[material_name]
        else:
            self.current_material = materials['steel_blue']

    def add_lighting(self, ambient=0.4, directional=0.6, specular=0.3):
        """Configure lighting setup."""
        self.lighting = {
            'ambient': ambient,
            'directional': directional,
            'specular': specular
        }

    def add_dimension(self, start_point, end_point, label):
        """Add dimension annotation."""
        # Store dimension for rendering
        dimension = {
            'start': start_point,
            'end': end_point,
            'label': label
        }

        if not hasattr(self, 'dimensions'):
            self.dimensions = []
        self.dimensions.append(dimension)

    def enable_rotation(self, enable: bool):
        """Enable/disable model rotation."""
        self.rotation_enabled = enable

    def enable_zoom(self, enable: bool):
        """Enable/disable zoom."""
        self.zoom_enabled = enable

    def enable_pan(self, enable: bool):
        """Enable/disable panning."""
        self.pan_enabled = enable

    def export_webxr(self, filename: str):
        """Export viewer as WebXR-compatible HTML."""
        html_content = self._generate_webxr_html()

        with open(filename, 'w') as f:
            f.write(html_content)

    def export_gltf(self, filename: str):
        """Export models to glTF format."""
        # Placeholder for glTF export
        gltf_data = self._generate_gltf()

        import json
        with open(filename, 'w') as f:
            json.dump(gltf_data, f, indent=2)

    def _generate_webxr_html(self) -> str:
        """Generate WebXR HTML content."""
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Vizly CAD Viewer - WebXR</title>
    <script src="https://cdn.jsdelivr.net/npm/three@0.150.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.150.0/examples/js/webxr/VRButton.js"></script>
    <style>
        body {{ margin: 0; background: #000; }}
        #container {{ width: 100%; height: 100vh; }}
    </style>
</head>
<body>
    <div id="container"></div>
    <script>
        let scene, camera, renderer;

        function init() {{
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.xr.enabled = true;

            document.getElementById('container').appendChild(renderer.domElement);
            document.body.appendChild(VRButton.createButton(renderer));

            // Add lighting
            const ambientLight = new THREE.AmbientLight(0x404040, {self.lighting['ambient']});
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, {self.lighting['directional']});
            directionalLight.position.set(5, 5, 5);
            scene.add(directionalLight);

            // Add CAD models
            {self._generate_threejs_models()}

            camera.position.set({self.camera_position[0]}, {self.camera_position[1]}, {self.camera_position[2]});
            camera.lookAt({self.camera_target[0]}, {self.camera_target[1]}, {self.camera_target[2]});

            renderer.setAnimationLoop(animate);
        }}

        function animate() {{
            renderer.render(scene, camera);
        }}

        init();
    </script>
</body>
</html>'''

    def _generate_threejs_models(self) -> str:
        """Generate Three.js code for models."""
        code = ""

        for i, model_data in enumerate(self.models):
            model = model_data['model']
            options = model_data['options']

            # Convert vertices and faces to Three.js format
            vertices_str = str(model.vertices.flatten().tolist())
            faces_str = str(model.faces.flatten().tolist())

            color = options.get('color', '#4682B4')
            if color.startswith('#'):
                color_hex = color
            else:
                color_map = {
                    'steel_blue': '#4682B4',
                    'aluminum': '#C0C0C0',
                    'copper': '#B87333'
                }
                color_hex = color_map.get(color, '#4682B4')

            code += f'''
            // Model {i}
            const geometry{i} = new THREE.BufferGeometry();
            const vertices{i} = new Float32Array({vertices_str});
            const indices{i} = new Uint16Array({faces_str});

            geometry{i}.setIndex(indices{i});
            geometry{i}.setAttribute('position', new THREE.BufferAttribute(vertices{i}, 3));
            geometry{i}.computeVertexNormals();

            const material{i} = new THREE.MeshPhongMaterial({{
                color: '{color_hex}',
                transparent: {str(options.get('transparency', 1.0) < 1.0).lower()},
                opacity: {options.get('transparency', 1.0)},
                wireframe: {str(options.get('wireframe', False)).lower()}
            }});

            const mesh{i} = new THREE.Mesh(geometry{i}, material{i});
            scene.add(mesh{i});
            '''

        return code

    def _generate_gltf(self) -> dict:
        """Generate glTF format data."""
        # Simplified glTF structure
        gltf = {
            "asset": {
                "version": "2.0",
                "generator": "Vizly CAD Viewer"
            },
            "scene": 0,
            "scenes": [{"nodes": list(range(len(self.models)))}],
            "nodes": [],
            "meshes": [],
            "accessors": [],
            "bufferViews": [],
            "buffers": []
        }

        # Add placeholder data for each model
        for i, model_data in enumerate(self.models):
            gltf["nodes"].append({
                "mesh": i,
                "name": f"CAD_Model_{i}"
            })

            gltf["meshes"].append({
                "primitives": [{
                    "attributes": {"POSITION": i * 2},
                    "indices": i * 2 + 1
                }]
            })

        return gltf