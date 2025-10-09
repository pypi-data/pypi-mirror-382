"""
Scientific Visualization Tools
==============================

Advanced scientific and technical visualization capabilities including
statistical plots, signal processing, and domain-specific visualizations.
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



from .statistics import *
from .signal_processing import *
from .specialized_plots import *

__all__ = [
    'qqplot',
    'residual_plot',
    'correlation_matrix',
    'pca_plot',
    'dendrogram',
    'spectrogram',
    'phase_plot',
    'bode_plot',
    'nyquist_plot',
    'waterfall_plot',
    'parallel_coordinates',
]