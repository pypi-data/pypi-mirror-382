"""
Finite Element Analysis Module
=============================

GPU-accelerated finite element analysis with stress visualization.
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
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

try:
    import scipy.sparse as sp
    from scipy.sparse.linalg import spsolve
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False


@dataclass
class FEMResult:
    """Results from FEM analysis."""
    displacement: np.ndarray
    stress: np.ndarray
    strain: np.ndarray
    von_mises_stress: np.ndarray
    nodes: np.ndarray
    elements: np.ndarray


class FEMSolver:
    """GPU-accelerated finite element solver."""

    def __init__(self, nodes: np.ndarray, elements: np.ndarray):
        """
        Initialize FEM solver.

        Args:
            nodes: Node coordinates (N x 2 or N x 3)
            elements: Element connectivity (M x 3 or M x 4)
        """
        self.nodes = np.array(nodes, dtype=np.float64)
        self.elements = np.array(elements, dtype=np.int32)
        self.num_nodes = len(nodes)
        self.num_elements = len(elements)
        self.dimension = self.nodes.shape[1]

        # Material properties (default steel)
        self.E = 200e9  # Young's modulus (Pa)
        self.nu = 0.3   # Poisson's ratio
        self.thickness = 0.01  # Thickness for 2D problems (m)

        # Boundary conditions and loads
        self.loads = {}
        self.boundary_conditions = {}

        # Use GPU if available
        self.use_gpu = CUPY_AVAILABLE

    def set_material_properties(self, E: float, nu: float, thickness: float = 0.01):
        """Set material properties."""
        self.E = E
        self.nu = nu
        self.thickness = thickness

    def apply_loads(self, loads: Dict[int, List[float]]):
        """
        Apply loads to nodes.

        Args:
            loads: Dictionary {node_id: [fx, fy, fz]}
        """
        self.loads = loads

    def apply_boundary_conditions(self, boundary_conditions: Dict[int, List[float]]):
        """
        Apply boundary conditions.

        Args:
            boundary_conditions: Dictionary {node_id: [ux, uy, uz]} (None for free DOF)
        """
        self.boundary_conditions = boundary_conditions

    def solve(self) -> FEMResult:
        """
        Solve FEM problem.

        Returns:
            FEMResult containing displacement, stress, and strain
        """
        if not SCIPY_AVAILABLE:
            raise RuntimeError("scipy is required for FEM solving. Install with: pip install scipy")

        # Assemble global stiffness matrix
        K = self._assemble_stiffness_matrix()

        # Assemble load vector
        F = self._assemble_load_vector()

        # Apply boundary conditions
        K_bc, F_bc, dof_map = self._apply_boundary_conditions(K, F)

        # Solve linear system
        if self.use_gpu and CUPY_AVAILABLE:
            displacement_free = self._solve_gpu(K_bc, F_bc)
        else:
            displacement_free = spsolve(K_bc, F_bc)

        # Reconstruct full displacement vector
        displacement = self._reconstruct_displacement(displacement_free, dof_map)

        # Calculate stress and strain
        stress, strain, von_mises = self._calculate_stress_strain(displacement)

        return FEMResult(
            displacement=displacement,
            stress=stress,
            strain=strain,
            von_mises_stress=von_mises,
            nodes=self.nodes,
            elements=self.elements
        )

    def _assemble_stiffness_matrix(self) -> sp.csr_matrix:
        """Assemble global stiffness matrix."""
        dof = self.dimension * self.num_nodes
        K = sp.lil_matrix((dof, dof), dtype=np.float64)

        for elem_id, element in enumerate(self.elements):
            ke = self._element_stiffness_matrix(element)

            # Get DOF indices for this element
            dof_indices = []
            for node in element:
                for d in range(self.dimension):
                    dof_indices.append(node * self.dimension + d)

            # Add element matrix to global matrix
            for i, gi in enumerate(dof_indices):
                for j, gj in enumerate(dof_indices):
                    K[gi, gj] += ke[i, j]

        return K.tocsr()

    def _element_stiffness_matrix(self, element: np.ndarray) -> np.ndarray:
        """Calculate element stiffness matrix."""
        if len(element) == 3:  # Triangle
            return self._triangle_stiffness_matrix(element)
        elif len(element) == 4:  # Quadrilateral
            return self._quad_stiffness_matrix(element)
        else:
            raise ValueError(f"Unsupported element type with {len(element)} nodes")

    def _triangle_stiffness_matrix(self, element: np.ndarray) -> np.ndarray:
        """Calculate stiffness matrix for triangular element."""
        nodes = self.nodes[element]

        # Calculate area and shape function derivatives
        x1, y1 = nodes[0]
        x2, y2 = nodes[1]
        x3, y3 = nodes[2]

        area = 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))

        if area < 1e-12:
            return np.zeros((6, 6))

        # Shape function derivatives
        b1 = y2 - y3
        b2 = y3 - y1
        b3 = y1 - y2
        c1 = x3 - x2
        c2 = x1 - x3
        c3 = x2 - x1

        # B matrix (strain-displacement)
        B = np.array([
            [b1, 0, b2, 0, b3, 0],
            [0, c1, 0, c2, 0, c3],
            [c1, b1, c2, b2, c3, b3]
        ]) / (2 * area)

        # Material matrix (plane stress)
        D = self._material_matrix()

        # Element stiffness matrix
        ke = B.T @ D @ B * area * self.thickness

        return ke

    def _quad_stiffness_matrix(self, element: np.ndarray) -> np.ndarray:
        """Calculate stiffness matrix for quadrilateral element."""
        # Simplified quad element - divide into two triangles
        tri1 = element[[0, 1, 2]]
        tri2 = element[[0, 2, 3]]

        ke1 = self._triangle_stiffness_matrix(tri1)
        ke2 = self._triangle_stiffness_matrix(tri2)

        # Combine triangle matrices (simplified approach)
        ke = np.zeros((8, 8))

        # Map triangle DOFs to quad DOFs
        tri1_map = [0, 1, 2, 3, 4, 5]  # nodes 0, 1, 2
        tri2_map = [0, 1, 4, 5, 6, 7]  # nodes 0, 2, 3

        for i, gi in enumerate(tri1_map):
            for j, gj in enumerate(tri1_map):
                ke[gi, gj] += ke1[i, j]

        for i, gi in enumerate(tri2_map):
            for j, gj in enumerate(tri2_map):
                ke[gi, gj] += ke2[i, j]

        return ke

    def _material_matrix(self) -> np.ndarray:
        """Calculate material matrix for plane stress."""
        factor = self.E / (1 - self.nu**2)
        D = factor * np.array([
            [1, self.nu, 0],
            [self.nu, 1, 0],
            [0, 0, (1 - self.nu) / 2]
        ])
        return D

    def _assemble_load_vector(self) -> np.ndarray:
        """Assemble global load vector."""
        dof = self.dimension * self.num_nodes
        F = np.zeros(dof)

        for node_id, load in self.loads.items():
            for i, force in enumerate(load):
                if i < self.dimension:
                    F[node_id * self.dimension + i] = force

        return F

    def _apply_boundary_conditions(self, K: sp.csr_matrix, F: np.ndarray) -> Tuple[sp.csr_matrix, np.ndarray, Dict]:
        """Apply boundary conditions using penalty method."""
        K_bc = K.copy()
        F_bc = F.copy()
        penalty = 1e12 * np.max(K.diagonal())

        constrained_dofs = set()
        dof_map = {}
        free_dof_count = 0

        for node_id, displacements in self.boundary_conditions.items():
            for i, disp in enumerate(displacements):
                if i < self.dimension and disp is not None:
                    dof = node_id * self.dimension + i
                    constrained_dofs.add(dof)

                    # Apply penalty method
                    K_bc[dof, dof] += penalty
                    F_bc[dof] += penalty * disp

        # Create mapping for free DOFs
        for dof in range(len(F)):
            if dof not in constrained_dofs:
                dof_map[free_dof_count] = dof
                free_dof_count += 1

        return K_bc, F_bc, dof_map

    def _solve_gpu(self, K: sp.csr_matrix, F: np.ndarray) -> np.ndarray:
        """Solve using GPU acceleration."""
        import cupyx.scipy.sparse.linalg as cusp_linalg

        # Transfer to GPU
        K_gpu = cp.sparse.csr_matrix(K)
        F_gpu = cp.array(F)

        # Solve
        x_gpu = cusp_linalg.spsolve(K_gpu, F_gpu)

        # Transfer back to CPU
        return cp.asnumpy(x_gpu)

    def _reconstruct_displacement(self, displacement_free: np.ndarray, dof_map: Dict) -> np.ndarray:
        """Reconstruct full displacement vector."""
        dof = self.dimension * self.num_nodes
        displacement = np.zeros(dof)

        # Fill in solved displacements
        for i, dof_id in dof_map.items():
            displacement[dof_id] = displacement_free[i] if i < len(displacement_free) else 0

        # Fill in prescribed displacements
        for node_id, displacements in self.boundary_conditions.items():
            for i, disp in enumerate(displacements):
                if i < self.dimension and disp is not None:
                    dof_id = node_id * self.dimension + i
                    displacement[dof_id] = disp

        return displacement

    def _calculate_stress_strain(self, displacement: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate stress and strain for each element."""
        stress_list = []
        strain_list = []
        von_mises_list = []

        for element in self.elements:
            # Get element displacements
            elem_disp = []
            for node in element:
                for d in range(self.dimension):
                    elem_disp.append(displacement[node * self.dimension + d])

            elem_disp = np.array(elem_disp)

            # Calculate strain
            if len(element) == 3:
                B = self._get_triangle_B_matrix(element)
            else:
                B = self._get_quad_B_matrix(element)

            strain = B @ elem_disp
            strain_list.append(strain)

            # Calculate stress
            D = self._material_matrix()
            stress = D @ strain
            stress_list.append(stress)

            # Calculate von Mises stress
            if len(stress) >= 3:
                sx, sy, txy = stress[0], stress[1], stress[2]
                vm_stress = np.sqrt(sx**2 + sy**2 - sx*sy + 3*txy**2)
            else:
                vm_stress = abs(stress[0])

            von_mises_list.append(vm_stress)

        return np.array(stress_list), np.array(strain_list), np.array(von_mises_list)

    def _get_triangle_B_matrix(self, element: np.ndarray) -> np.ndarray:
        """Get B matrix for triangular element."""
        nodes = self.nodes[element]
        x1, y1 = nodes[0]
        x2, y2 = nodes[1]
        x3, y3 = nodes[2]

        area = 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))

        b1 = y2 - y3
        b2 = y3 - y1
        b3 = y1 - y2
        c1 = x3 - x2
        c2 = x1 - x3
        c3 = x2 - x1

        B = np.array([
            [b1, 0, b2, 0, b3, 0],
            [0, c1, 0, c2, 0, c3],
            [c1, b1, c2, b2, c3, b3]
        ]) / (2 * area)

        return B

    def _get_quad_B_matrix(self, element: np.ndarray) -> np.ndarray:
        """Get B matrix for quadrilateral element (simplified)."""
        # Use average of two triangular B matrices
        tri1 = element[[0, 1, 2]]
        tri2 = element[[0, 2, 3]]

        B1 = self._get_triangle_B_matrix(tri1)
        B2 = self._get_triangle_B_matrix(tri2)

        # Simplified averaging
        B = np.zeros((3, 8))
        B[:, [0, 1, 2, 3, 4, 5]] = B1
        B[:, [0, 1, 4, 5, 6, 7]] += B2
        B[:, [0, 1]] /= 2  # Average overlapping DOFs

        return B


class FEMChart:
    """Specialized chart for FEM visualization."""

    def __init__(self, figure):
        """Initialize FEM chart."""
        self.figure = figure

    def plot_mesh(self, nodes, elements, **kwargs):
        """Plot FEM mesh with optional stress coloring."""
        # Implementation would integrate with main Vizly plotting
        pass

    def set_title(self, title):
        """Set chart title."""
        pass

    def add_colorbar(self, label):
        """Add colorbar for stress visualization."""
        pass