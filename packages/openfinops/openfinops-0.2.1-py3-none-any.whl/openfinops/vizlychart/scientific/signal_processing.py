"""
Signal Processing Visualization
===============================

Advanced signal analysis and frequency domain visualizations.
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

from typing import List, Optional, Union, Tuple, Dict, Any
import math

import numpy as np

try:
    import scipy.signal as signal
    import scipy.fft as fft
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    signal = None
    fft = None

from ..charts.professional_charts import ProfessionalChart
from ..charts.advanced_charts import HeatmapChart
from ..rendering.vizlyengine import ColorHDR, Font


def spectrogram(data: np.ndarray, fs: float = 1.0, window: str = 'hann',
                nperseg: int = 256, noverlap: int = None,
                title: str = "Spectrogram", **kwargs) -> HeatmapChart:
    """Create spectrogram visualization."""
    if SCIPY_AVAILABLE:
        f, t, Sxx = signal.spectrogram(data, fs, window=window,
                                     nperseg=nperseg, noverlap=noverlap)
    else:
        # Simple FFT-based spectrogram fallback
        if noverlap is None:
            noverlap = nperseg // 2

        hop_length = nperseg - noverlap
        n_frames = (len(data) - nperseg) // hop_length + 1

        Sxx = np.zeros((nperseg // 2 + 1, n_frames))
        t = np.arange(n_frames) * hop_length / fs
        f = np.fft.fftfreq(nperseg, 1/fs)[:nperseg//2 + 1]

        for i in range(n_frames):
            start = i * hop_length
            windowed = data[start:start + nperseg] * np.hanning(nperseg)
            fft_data = np.fft.fft(windowed)
            Sxx[:, i] = np.abs(fft_data[:nperseg//2 + 1])**2

    chart = HeatmapChart(**kwargs)
    chart.heatmap(10 * np.log10(Sxx + 1e-10), colormap='viridis', show_values=False)
    chart.set_title(title)
    chart.set_labels('Time (s)', 'Frequency (Hz)')
    return chart


def phase_plot(complex_data: np.ndarray, title: str = "Phase Plot", **kwargs) -> ProfessionalChart:
    """Create phase plot visualization."""
    from ..charts.professional_charts import ProfessionalScatterChart as ScatterChart

    chart = ScatterChart(**kwargs)
    real_part = np.real(complex_data)
    imag_part = np.imag(complex_data)

    chart.scatter(real_part, imag_part, c=ColorHDR.from_hex('#2E86C1'), alpha=0.7)
    chart.set_title(title)
    chart.set_labels("Real Part", "Imaginary Part")
    return chart


def bode_plot(frequencies: np.ndarray, transfer_function: np.ndarray,
              title: str = "Bode Plot", **kwargs) -> Tuple[ProfessionalChart, ProfessionalChart]:
    """Create Bode magnitude and phase plots."""
    from ..charts.professional_charts import ProfessionalLineChart as LineChart

    # Magnitude plot
    mag_chart = LineChart(**kwargs)
    magnitude_db = 20 * np.log10(np.abs(transfer_function))
    mag_chart.plot(frequencies, magnitude_db, color=ColorHDR.from_hex('#E74C3C'), line_width=2)
    mag_chart.set_title(f"{title} - Magnitude")
    mag_chart.set_labels("Frequency (Hz)", "Magnitude (dB)")

    # Phase plot
    phase_chart = LineChart(**kwargs)
    phase_deg = np.angle(transfer_function) * 180 / np.pi
    phase_chart.plot(frequencies, phase_deg, color=ColorHDR.from_hex('#3498DB'), line_width=2)
    phase_chart.set_title(f"{title} - Phase")
    phase_chart.set_labels("Frequency (Hz)", "Phase (degrees)")

    return mag_chart, phase_chart


def nyquist_plot(complex_response: np.ndarray, title: str = "Nyquist Plot", **kwargs) -> ProfessionalChart:
    """Create Nyquist plot for control systems."""
    from ..charts.professional_charts import ProfessionalLineChart as LineChart

    chart = LineChart(**kwargs)
    real_part = np.real(complex_response)
    imag_part = np.imag(complex_response)

    chart.plot(real_part, imag_part, color=ColorHDR.from_hex('#9B59B6'), line_width=2)

    # Add unit circle for reference
    theta = np.linspace(0, 2*np.pi, 100)
    unit_real = np.cos(theta)
    unit_imag = np.sin(theta)
    chart.plot(unit_real, unit_imag, color=ColorHDR.from_hex('#95A5A6'),
               line_width=1, line_style='dashed')

    chart.set_title(title)
    chart.set_labels("Real Part", "Imaginary Part")
    return chart


def waterfall_plot(data: np.ndarray, frequencies: np.ndarray = None,
                   time_steps: np.ndarray = None, title: str = "Waterfall Plot", **kwargs):
    """Create 3D waterfall plot for spectral analysis."""
    from ..charts.chart_3d import Chart3D

    chart_3d = Chart3D(**kwargs)

    if frequencies is None:
        frequencies = np.arange(data.shape[1])
    if time_steps is None:
        time_steps = np.arange(data.shape[0])

    # Create meshgrid for 3D plotting
    F, T = np.meshgrid(frequencies, time_steps)

    chart_3d.surface(F, T, data, colormap='plasma')
    chart_3d.set_title(title)
    chart_3d.set_labels("Frequency (Hz)", "Time", "Amplitude")
    return chart_3d