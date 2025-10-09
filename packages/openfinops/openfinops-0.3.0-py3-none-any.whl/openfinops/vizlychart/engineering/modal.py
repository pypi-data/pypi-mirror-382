"""
Modal Analysis Module
====================

Eigenvalue analysis and vibration mode visualization.
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
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass

try:
    import scipy.linalg as la
    from scipy.sparse import csc_matrix
    from scipy.sparse.linalg import eigsh
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@dataclass
class ModalResult:
    """Results from modal analysis."""
    frequencies: np.ndarray
    mode_shapes: np.ndarray
    modal_masses: Optional[np.ndarray] = None
    participation_factors: Optional[np.ndarray] = None


class ModalSolver:
    """Modal analysis solver for vibration problems."""

    def __init__(self, nodes: np.ndarray, beam_properties: Dict):
        """
        Initialize modal solver.

        Args:
            nodes: Node positions
            beam_properties: Material and geometric properties
        """
        self.nodes = np.array(nodes)
        self.properties = beam_properties
        self.num_nodes = len(nodes)

        # Extract properties
        self.E = beam_properties.get('young_modulus', 200e9)
        self.rho = beam_properties.get('density', 7850)
        self.A = beam_properties.get('cross_section', 0.01)
        self.I = beam_properties.get('moment_inertia', 8.33e-6)

        # Boundary conditions
        self.boundary_conditions = {}

    def set_boundary_conditions(self, **kwargs):
        """Set boundary conditions."""
        self.boundary_conditions = kwargs

    def solve_eigenvalue_problem(self, num_modes: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve eigenvalue problem for natural frequencies and mode shapes.

        Args:
            num_modes: Number of modes to compute

        Returns:
            Tuple of (frequencies, mode_shapes)
        """
        if not SCIPY_AVAILABLE:
            raise RuntimeError("scipy is required for modal analysis")

        # Assemble mass and stiffness matrices
        M = self._assemble_mass_matrix()
        K = self._assemble_stiffness_matrix()

        # Apply boundary conditions
        M_bc, K_bc = self._apply_modal_boundary_conditions(M, K)

        # Solve generalized eigenvalue problem
        eigenvalues, eigenvectors = self._solve_generalized_eigenvalue(
            K_bc, M_bc, num_modes
        )

        # Convert eigenvalues to frequencies
        frequencies = np.sqrt(eigenvalues) / (2 * np.pi)

        # Normalize mode shapes
        mode_shapes = self._normalize_mode_shapes(eigenvectors, M_bc)

        return frequencies, mode_shapes

    def _assemble_mass_matrix(self) -> np.ndarray:
        """Assemble global mass matrix."""
        n_dof = 2 * self.num_nodes  # 2 DOF per node (vertical displacement, rotation)
        M = np.zeros((n_dof, n_dof))

        for i in range(self.num_nodes - 1):
            # Element length
            L = self.nodes[i+1] - self.nodes[i]

            # Element mass matrix (Euler-Bernoulli beam)
            rho_A_L = self.rho * self.A * L
            me = rho_A_L / 420 * np.array([
                [156, 22*L, 54, -13*L],
                [22*L, 4*L**2, 13*L, -3*L**2],
                [54, 13*L, 156, -22*L],
                [-13*L, -3*L**2, -22*L, 4*L**2]
            ])

            # Assembly
            dofs = [2*i, 2*i+1, 2*(i+1), 2*(i+1)+1]
            for p, global_p in enumerate(dofs):
                for q, global_q in enumerate(dofs):
                    M[global_p, global_q] += me[p, q]

        return M

    def _assemble_stiffness_matrix(self) -> np.ndarray:
        """Assemble global stiffness matrix."""
        n_dof = 2 * self.num_nodes
        K = np.zeros((n_dof, n_dof))

        for i in range(self.num_nodes - 1):
            # Element length
            L = self.nodes[i+1] - self.nodes[i]

            # Element stiffness matrix (Euler-Bernoulli beam)
            EI_L3 = self.E * self.I / L**3
            ke = EI_L3 * np.array([
                [12, 6*L, -12, 6*L],
                [6*L, 4*L**2, -6*L, 2*L**2],
                [-12, -6*L, 12, -6*L],
                [6*L, 2*L**2, -6*L, 4*L**2]
            ])

            # Assembly
            dofs = [2*i, 2*i+1, 2*(i+1), 2*(i+1)+1]
            for p, global_p in enumerate(dofs):
                for q, global_q in enumerate(dofs):
                    K[global_p, global_q] += ke[p, q]

        return K

    def _apply_modal_boundary_conditions(self, M: np.ndarray, K: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Apply boundary conditions to mass and stiffness matrices."""
        # For cantilever beam: fix displacement and rotation at first node
        if 'fixed_end' in self.boundary_conditions:
            fixed_node = self.boundary_conditions['fixed_end']
            fixed_dofs = [2*fixed_node, 2*fixed_node+1]

            # Remove fixed DOFs
            free_dofs = [i for i in range(M.shape[0]) if i not in fixed_dofs]

            M_bc = M[np.ix_(free_dofs, free_dofs)]
            K_bc = K[np.ix_(free_dofs, free_dofs)]

            return M_bc, K_bc

        return M, K

    def _solve_generalized_eigenvalue(self, K: np.ndarray, M: np.ndarray,
                                    num_modes: int) -> Tuple[np.ndarray, np.ndarray]:
        """Solve generalized eigenvalue problem K*phi = lambda*M*phi."""
        if K.shape[0] > 100:
            # Use sparse solver for large problems
            K_sparse = csc_matrix(K)
            M_sparse = csc_matrix(M)
            eigenvalues, eigenvectors = eigsh(K_sparse, k=num_modes, M=M_sparse,
                                            which='SM', sigma=0)
        else:
            # Use dense solver for small problems
            eigenvalues, eigenvectors = la.eigh(K, M)
            # Sort and take first num_modes
            idx = np.argsort(eigenvalues)
            eigenvalues = eigenvalues[idx[:num_modes]]
            eigenvectors = eigenvectors[:, idx[:num_modes]]

        return eigenvalues, eigenvectors

    def _normalize_mode_shapes(self, eigenvectors: np.ndarray, M: np.ndarray) -> np.ndarray:
        """Normalize mode shapes with respect to mass matrix."""
        normalized_modes = np.zeros_like(eigenvectors)

        for i in range(eigenvectors.shape[1]):
            mode = eigenvectors[:, i]
            # Mass normalize: phi^T * M * phi = 1
            modal_mass = mode.T @ M @ mode
            normalized_modes[:, i] = mode / np.sqrt(modal_mass)

        return normalized_modes

    def calculate_frf(self, excitation_point: float, response_point: float,
                     frequencies: np.ndarray, damping_ratio: float = 0.02) -> np.ndarray:
        """
        Calculate frequency response function.

        Args:
            excitation_point: Position of excitation
            response_point: Position of response measurement
            frequencies: Frequency range for FRF
            damping_ratio: Modal damping ratio

        Returns:
            Complex frequency response function
        """
        # Get modal parameters
        natural_freqs, mode_shapes = self.solve_eigenvalue_problem()

        # Interpolate mode shapes to excitation and response points
        excite_idx = np.argmin(np.abs(self.nodes - excitation_point))
        response_idx = np.argmin(np.abs(self.nodes - response_point))

        omega = 2 * np.pi * frequencies
        frf = np.zeros(len(frequencies), dtype=complex)

        for mode_num in range(len(natural_freqs)):
            omega_n = 2 * np.pi * natural_freqs[mode_num]

            # Modal coordinates at excitation and response points
            phi_e = mode_shapes[2*excite_idx, mode_num]  # Displacement DOF
            phi_r = mode_shapes[2*response_idx, mode_num]

            # Modal FRF
            for i, w in enumerate(omega):
                h_modal = 1 / (omega_n**2 - w**2 + 2j * damping_ratio * omega_n * w)
                frf[i] += phi_r * phi_e * h_modal

        return frf


class ModalChart:
    """Specialized chart for modal analysis visualization."""

    def __init__(self, figure):
        """Initialize modal chart."""
        self.figure = figure
        self.mode_data = []

    def add_mode_shape(self, nodes, mode_shape, **kwargs):
        """Add mode shape to chart."""
        mode_info = {
            'nodes': nodes,
            'mode_shape': mode_shape,
            'frequency': kwargs.get('frequency', 0),
            'mode_number': kwargs.get('mode_number', 1),
            'animate': kwargs.get('animate', False),
            'amplitude_scale': kwargs.get('amplitude_scale', 1.0)
        }
        self.mode_data.append(mode_info)

    def plot_frf(self, frequencies, frf, **kwargs):
        """Plot frequency response function."""
        pass

    def set_title(self, title):
        """Set chart title."""
        pass

    def set_labels(self, xlabel, ylabel):
        """Set axis labels."""
        pass