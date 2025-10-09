"""
AI Training Visualization System for OpenFinOps
==============================================

Real-time, interactive visualization tools for AI/ML model training monitoring,
early stopping analysis, and hyperparameter optimization visualization.

Key Features:
- Real-time training metrics streaming and visualization
- Interactive early stopping analysis with threshold controls
- Multi-model comparison dashboards
- Hyperparameter optimization 3D/4D visualization
- Training anomaly detection and alerting
- GPU utilization and resource monitoring
- Gradient flow visualization
- Loss landscape exploration
- Model architecture visualization

Usage:
    >>> import openfinops as vc
    >>> from openfinops.ai_training import TrainingMonitor
    >>>
    >>> # Real-time training visualization
    >>> monitor = TrainingMonitor()
    >>> monitor.log_metrics(epoch=1, loss=0.5, accuracy=0.8, lr=0.001)
    >>> monitor.show_realtime_dashboard()
    >>>
    >>> # Early stopping analysis
    >>> early_stop = vc.EarlyStoppingAnalyzer()
    >>> early_stop.analyze_training_curve(losses, patience=10)
    >>> early_stop.show_interactive_analysis()
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



from .training_monitor import TrainingMonitor, RealTimeTrainingDashboard
from .early_stopping import EarlyStoppingAnalyzer
from .hyperparameter_viz import HyperparameterOptimizer3D, ParamSpaceExplorer
from .model_comparison import ModelComparisonDashboard, TrainingComparator
from .streaming_metrics import MetricsStreamer, LiveMetricsServer
from .anomaly_detection import TrainingAnomalyDetector, AnomalyAlertSystem
from .gradient_viz import GradientFlowVisualizer, WeightDistributionTracker
from .loss_landscape import LossLandscapeExplorer, LossContourVisualizer
from .resource_monitor import GPUMonitor, ResourceDashboard

__all__ = [
    # Core Training Monitoring
    "TrainingMonitor",
    "RealTimeTrainingDashboard",

    # Early Stopping Analysis
    "EarlyStoppingAnalyzer",

    # Hyperparameter Optimization
    "HyperparameterOptimizer3D",
    "ParamSpaceExplorer",

    # Model Comparison
    "ModelComparisonDashboard",
    "TrainingComparator",

    # Streaming & Real-time
    "MetricsStreamer",
    "LiveMetricsServer",

    # Anomaly Detection
    "TrainingAnomalyDetector",
    "AnomalyAlertSystem",

    # Advanced Analysis
    "GradientFlowVisualizer",
    "WeightDistributionTracker",
    "LossLandscapeExplorer",
    "LossContourVisualizer",

    # Resource Monitoring
    "GPUMonitor",
    "ResourceDashboard",
]