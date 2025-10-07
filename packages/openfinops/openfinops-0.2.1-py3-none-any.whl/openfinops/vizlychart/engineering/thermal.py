"""
Thermal Analysis Module
======================

Heat transfer simulation and temperature visualization.
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
from typing import Tuple, Dict, List, Optional
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
class ThermalResult:
    """Results from thermal analysis."""
    temperature: np.ndarray
    heat_flux: Tuple[np.ndarray, np.ndarray]
    convergence_history: Optional[List[float]] = None


class ThermalSolver:
    """GPU-accelerated thermal analysis solver."""

    def __init__(self, domain_shape: Tuple[int, int]):
        """
        Initialize thermal solver.

        Args:
            domain_shape: (nx, ny) grid dimensions
        """
        self.nx, self.ny = domain_shape
        self.dx = 1.0 / (self.nx - 1)
        self.dy = 1.0 / (self.ny - 1)

        # Material properties (default aluminum)
        self.thermal_conductivity = 200.0  # W/m·K
        self.density = 2700.0  # kg/m³
        self.specific_heat = 900.0  # J/kg·K

        # Boundary conditions
        self.temperature_bcs = {}
        self.heat_flux_bcs = {}

        # Heat sources
        self.heat_sources = np.zeros((self.nx, self.ny))

        # Use GPU if available
        self.use_gpu = CUPY_AVAILABLE

    def set_material_properties(self, thermal_conductivity: float,
                              density: float, specific_heat: float):
        """Set material properties."""
        self.thermal_conductivity = thermal_conductivity
        self.density = density
        self.specific_heat = specific_heat

    def set_temperature_bc(self, boundary: str, temperature: float):
        """
        Set temperature boundary condition.

        Args:
            boundary: 'left', 'right', 'top', 'bottom'
            temperature: Temperature value
        """
        self.temperature_bcs[boundary] = temperature

    def set_heat_flux_bc(self, boundary: str, heat_flux: float):
        """
        Set heat flux boundary condition.

        Args:
            boundary: 'left', 'right', 'top', 'bottom'
            heat_flux: Heat flux value (W/m²)
        """
        self.heat_flux_bcs[boundary] = heat_flux

    def add_heat_source(self, heat_source: np.ndarray):
        """
        Add volumetric heat source.

        Args:
            heat_source: Heat generation rate (W/m³)
        """
        if heat_source.shape != (self.nx, self.ny):
            raise ValueError(f"Heat source shape {heat_source.shape} must match domain shape {(self.nx, self.ny)}")

        self.heat_sources = heat_source

    def solve_steady_state(self) -> np.ndarray:
        """
        Solve steady-state heat conduction equation.

        Returns:
            Temperature field
        """
        if not SCIPY_AVAILABLE:
            raise RuntimeError("scipy is required for thermal analysis")

        if self.use_gpu and CUPY_AVAILABLE:
            return self._solve_steady_state_gpu()
        else:
            return self._solve_steady_state_cpu()

    def _solve_steady_state_cpu(self) -> np.ndarray:
        """CPU-based steady-state solver."""
        # Set up linear system: K * T = F
        K, F = self._assemble_thermal_system()

        # Solve linear system
        T_flat = spsolve(K, F)

        # Reshape to 2D grid
        T = T_flat.reshape((self.nx, self.ny))

        return T

    def _solve_steady_state_gpu(self) -> np.ndarray:
        """GPU-based steady-state solver."""
        import cupyx.scipy.sparse.linalg as cusp_linalg

        # Assemble system on CPU then transfer to GPU
        K, F = self._assemble_thermal_system()

        # Transfer to GPU
        K_gpu = cp.sparse.csr_matrix(K)
        F_gpu = cp.array(F)

        # Solve on GPU
        T_flat_gpu = cusp_linalg.spsolve(K_gpu, F_gpu)

        # Transfer back to CPU and reshape
        T_flat = cp.asnumpy(T_flat_gpu)
        T = T_flat.reshape((self.nx, self.ny))

        return T

    def _assemble_thermal_system(self) -> Tuple[sp.csr_matrix, np.ndarray]:
        """Assemble thermal conduction system matrices."""
        n_nodes = self.nx * self.ny

        # Initialize sparse matrix
        K = sp.lil_matrix((n_nodes, n_nodes))
        F = np.zeros(n_nodes)

        # Thermal diffusivity
        alpha = self.thermal_conductivity

        # Finite difference coefficients
        coeff_x = alpha / self.dx**2
        coeff_y = alpha / self.dy**2

        for i in range(self.nx):
            for j in range(self.ny):
                node = i * self.ny + j

                # Interior nodes
                if 1 <= i <= self.nx-2 and 1 <= j <= self.ny-2:
                    # Central difference for Laplacian
                    K[node, node] = -2 * (coeff_x + coeff_y)

                    # Neighbors
                    K[node, (i-1)*self.ny + j] = coeff_x  # Left
                    K[node, (i+1)*self.ny + j] = coeff_x  # Right
                    K[node, i*self.ny + (j-1)] = coeff_y  # Bottom
                    K[node, i*self.ny + (j+1)] = coeff_y  # Top

                    # Heat source
                    F[node] = -self.heat_sources[i, j]

                else:
                    # Boundary nodes
                    K[node, node] = 1.0
                    F[node] = self._get_boundary_value(i, j)

        return K.tocsr(), F

    def _get_boundary_value(self, i: int, j: int) -> float:
        """Get boundary condition value for node (i, j)."""
        # Left boundary
        if i == 0 and 'left' in self.temperature_bcs:
            return self.temperature_bcs['left']

        # Right boundary
        if i == self.nx-1 and 'right' in self.temperature_bcs:
            return self.temperature_bcs['right']

        # Bottom boundary
        if j == 0 and 'bottom' in self.temperature_bcs:
            return self.temperature_bcs['bottom']

        # Top boundary
        if j == self.ny-1 and 'top' in self.temperature_bcs:
            return self.temperature_bcs['top']

        # Default temperature if no BC specified
        return 20.0  # Room temperature

    def solve_transient(self, time_steps: int, dt: float,
                       initial_temperature: float = 20.0) -> List[np.ndarray]:
        """
        Solve transient heat conduction.

        Args:
            time_steps: Number of time steps
            dt: Time step size
            initial_temperature: Initial temperature

        Returns:
            List of temperature fields at each time step
        """
        if self.use_gpu and CUPY_AVAILABLE:
            return self._solve_transient_gpu(time_steps, dt, initial_temperature)
        else:
            return self._solve_transient_cpu(time_steps, dt, initial_temperature)

    def _solve_transient_cpu(self, time_steps: int, dt: float,
                           initial_temperature: float) -> List[np.ndarray]:
        """CPU-based transient solver."""
        # Initialize temperature field
        T = np.full((self.nx, self.ny), initial_temperature)

        # Thermal diffusivity
        alpha_thermal = self.thermal_conductivity / (self.density * self.specific_heat)

        # Stability check (CFL condition)
        dt_max = 0.25 * min(self.dx**2, self.dy**2) / alpha_thermal
        if dt > dt_max:
            print(f"Warning: Time step {dt} exceeds stability limit {dt_max}")

        temperature_history = [T.copy()]

        for step in range(time_steps):
            T_new = T.copy()

            # Update interior nodes
            for i in range(1, self.nx-1):
                for j in range(1, self.ny-1):
                    # Heat diffusion
                    d2T_dx2 = (T[i+1, j] - 2*T[i, j] + T[i-1, j]) / self.dx**2
                    d2T_dy2 = (T[i, j+1] - 2*T[i, j] + T[i, j-1]) / self.dy**2

                    # Time update
                    T_new[i, j] = T[i, j] + dt * (
                        alpha_thermal * (d2T_dx2 + d2T_dy2) +
                        self.heat_sources[i, j] / (self.density * self.specific_heat)
                    )

            # Apply boundary conditions
            T_new = self._apply_transient_bcs(T_new)

            T = T_new
            temperature_history.append(T.copy())

        return temperature_history

    def _solve_transient_gpu(self, time_steps: int, dt: float,
                           initial_temperature: float) -> List[np.ndarray]:
        """GPU-based transient solver."""
        # Transfer to GPU
        T = cp.full((self.nx, self.ny), initial_temperature, dtype=cp.float32)
        heat_sources_gpu = cp.array(self.heat_sources, dtype=cp.float32)

        alpha_thermal = self.thermal_conductivity / (self.density * self.specific_heat)

        temperature_history = [cp.asnumpy(T)]

        for step in range(time_steps):
            # Vectorized finite difference update
            T_new = T.copy()

            # Interior nodes update (vectorized)
            d2T_dx2 = cp.zeros_like(T)
            d2T_dy2 = cp.zeros_like(T)

            d2T_dx2[1:-1, :] = (T[2:, :] - 2*T[1:-1, :] + T[:-2, :]) / self.dx**2
            d2T_dy2[:, 1:-1] = (T[:, 2:] - 2*T[:, 1:-1] + T[:, :-2]) / self.dy**2

            T_new[1:-1, 1:-1] = T[1:-1, 1:-1] + dt * (
                alpha_thermal * (d2T_dx2[1:-1, 1:-1] + d2T_dy2[1:-1, 1:-1]) +
                heat_sources_gpu[1:-1, 1:-1] / (self.density * self.specific_heat)
            )

            # Apply boundary conditions
            T_new = self._apply_transient_bcs_gpu(T_new)

            T = T_new
            temperature_history.append(cp.asnumpy(T))

        return temperature_history

    def _apply_transient_bcs(self, T: np.ndarray) -> np.ndarray:
        """Apply boundary conditions for transient analysis (CPU)."""
        T_bc = T.copy()

        # Temperature BCs
        if 'left' in self.temperature_bcs:
            T_bc[0, :] = self.temperature_bcs['left']
        if 'right' in self.temperature_bcs:
            T_bc[-1, :] = self.temperature_bcs['right']
        if 'bottom' in self.temperature_bcs:
            T_bc[:, 0] = self.temperature_bcs['bottom']
        if 'top' in self.temperature_bcs:
            T_bc[:, -1] = self.temperature_bcs['top']

        # Heat flux BCs (simplified implementation)
        if 'left' in self.heat_flux_bcs:
            # Neumann BC: dT/dx = q/k
            q = self.heat_flux_bcs['left']
            T_bc[0, :] = T_bc[1, :] - q * self.dx / self.thermal_conductivity

        return T_bc

    def _apply_transient_bcs_gpu(self, T: cp.ndarray) -> cp.ndarray:
        """Apply boundary conditions for transient analysis (GPU)."""
        T_bc = T.copy()

        # Temperature BCs
        if 'left' in self.temperature_bcs:
            T_bc[0, :] = self.temperature_bcs['left']
        if 'right' in self.temperature_bcs:
            T_bc[-1, :] = self.temperature_bcs['right']
        if 'bottom' in self.temperature_bcs:
            T_bc[:, 0] = self.temperature_bcs['bottom']
        if 'top' in self.temperature_bcs:
            T_bc[:, -1] = self.temperature_bcs['top']

        return T_bc

    def calculate_heat_flux(self, temperature: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate heat flux from temperature field.

        Args:
            temperature: Temperature field

        Returns:
            Tuple of (heat_flux_x, heat_flux_y)
        """
        # Heat flux = -k * grad(T)
        heat_flux_x = np.zeros_like(temperature)
        heat_flux_y = np.zeros_like(temperature)

        # Finite difference gradients
        heat_flux_x[1:-1, :] = -self.thermal_conductivity * (
            temperature[2:, :] - temperature[:-2, :]) / (2 * self.dx)

        heat_flux_y[:, 1:-1] = -self.thermal_conductivity * (
            temperature[:, 2:] - temperature[:, :-2]) / (2 * self.dy)

        return heat_flux_x, heat_flux_y


class ThermalChart:
    """Specialized chart for thermal analysis visualization."""

    def __init__(self, figure):
        """Initialize thermal chart."""
        self.figure = figure

    def plot_temperature_contours(self, X, Y, temperature, **kwargs):
        """Plot temperature contours."""
        pass

    def plot_heat_flux_vectors(self, X, Y, flux_x, flux_y, **kwargs):
        """Plot heat flux vectors."""
        pass

    def set_title(self, title):
        """Set chart title."""
        pass

    def add_colorbar(self, label):
        """Add colorbar for temperature scale."""
        pass

    def set_labels(self, xlabel, ylabel):
        """Set axis labels."""
        pass