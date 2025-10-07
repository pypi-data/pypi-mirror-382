"""
Interactive Early Stopping Analysis System
=========================================

Advanced early stopping analysis with interactive visualization for AI/ML training.
Provides real-time recommendations for optimal stopping points with statistical analysis.
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
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class EarlyStoppingStrategy(Enum):
    """Different early stopping strategies."""
    PATIENCE_BASED = "patience_based"
    IMPROVEMENT_THRESHOLD = "improvement_threshold"
    STATISTICAL_SIGNIFICANCE = "statistical_significance"
    PLATEAU_DETECTION = "plateau_detection"
    OVERFITTING_DETECTION = "overfitting_detection"


@dataclass
class EarlyStoppingRecommendation:
    """Early stopping recommendation with detailed analysis."""
    should_stop: bool
    confidence: float
    reason: str
    optimal_epoch: int
    performance_at_optimal: float
    potential_improvement: float
    risk_assessment: str
    suggested_actions: List[str]


class EarlyStoppingAnalyzer:
    """
    Advanced early stopping analyzer with multiple strategies and interactive visualization.
    """

    def __init__(self):
        self.training_history = []
        self.validation_history = []
        self.epochs = []
        self.learning_rates = []
        self.analysis_results = {}

    def add_epoch_data(self,
                      epoch: int,
                      train_loss: float,
                      val_loss: Optional[float] = None,
                      train_metric: Optional[float] = None,
                      val_metric: Optional[float] = None,
                      learning_rate: Optional[float] = None):
        """Add training data for a single epoch."""

        self.epochs.append(epoch)
        self.training_history.append({
            'epoch': epoch,
            'train_loss': train_loss,
            'val_loss': val_loss,
            'train_metric': train_metric,
            'val_metric': val_metric,
            'learning_rate': learning_rate
        })

        if learning_rate is not None:
            self.learning_rates.append(learning_rate)

    def analyze_training_curve(self,
                             patience: int = 10,
                             min_delta: float = 0.001,
                             monitor_metric: str = 'val_loss',
                             restore_best_weights: bool = True) -> EarlyStoppingRecommendation:
        """
        Comprehensive analysis of training curve for early stopping decision.

        Args:
            patience: Number of epochs to wait for improvement
            min_delta: Minimum change to qualify as improvement
            monitor_metric: Metric to monitor ('val_loss', 'val_metric', etc.)
            restore_best_weights: Whether to recommend restoring best weights
        """

        if len(self.training_history) < 3:
            return EarlyStoppingRecommendation(
                should_stop=False,
                confidence=0.0,
                reason="Insufficient data for analysis",
                optimal_epoch=0,
                performance_at_optimal=0.0,
                potential_improvement=0.0,
                risk_assessment="low",
                suggested_actions=["Continue training to gather more data"]
            )

        # Extract metric values
        metric_values = []
        for record in self.training_history:
            if monitor_metric == 'val_loss' and record['val_loss'] is not None:
                metric_values.append(record['val_loss'])
            elif monitor_metric == 'val_metric' and record['val_metric'] is not None:
                metric_values.append(record['val_metric'])
            else:
                metric_values.append(record['train_loss'])

        if not metric_values:
            return EarlyStoppingRecommendation(
                should_stop=False,
                confidence=0.0,
                reason="No valid metric values found",
                optimal_epoch=0,
                performance_at_optimal=0.0,
                potential_improvement=0.0,
                risk_assessment="low",
                suggested_actions=["Check data logging"]
            )

        # Run multiple analysis strategies
        patience_analysis = self._patience_based_analysis(metric_values, patience, min_delta)
        plateau_analysis = self._plateau_detection_analysis(metric_values)
        overfitting_analysis = self._overfitting_analysis()
        statistical_analysis = self._statistical_significance_analysis(metric_values)

        # Combine analyses for final recommendation
        return self._combine_analyses(
            patience_analysis,
            plateau_analysis,
            overfitting_analysis,
            statistical_analysis,
            metric_values
        )

    def _patience_based_analysis(self,
                                metric_values: List[float],
                                patience: int,
                                min_delta: float) -> Dict[str, Any]:
        """Traditional patience-based early stopping analysis."""

        is_loss_metric = True  # Assume lower is better
        best_value = float('inf')
        best_epoch = 0
        patience_counter = 0

        for i, value in enumerate(metric_values):
            if is_loss_metric:
                improved = value < (best_value - min_delta)
            else:
                improved = value > (best_value + min_delta)

            if improved:
                best_value = value
                best_epoch = i
                patience_counter = 0
            else:
                patience_counter += 1

        should_stop_patience = patience_counter >= patience

        return {
            'should_stop': should_stop_patience,
            'best_epoch': best_epoch,
            'best_value': best_value,
            'patience_counter': patience_counter,
            'confidence': min(patience_counter / patience, 1.0)
        }

    def _plateau_detection_analysis(self, metric_values: List[float]) -> Dict[str, Any]:
        """Detect if training has plateaued using statistical methods."""

        if len(metric_values) < 10:
            return {'plateau_detected': False, 'confidence': 0.0}

        # Use last 10 epochs to detect plateau
        recent_values = metric_values[-10:]

        # Calculate coefficient of variation
        mean_val = np.mean(recent_values)
        std_val = np.std(recent_values)
        cv = std_val / abs(mean_val) if mean_val != 0 else float('inf')

        # Calculate trend
        x = np.arange(len(recent_values))
        slope = np.corrcoef(x, recent_values)[0, 1] if len(recent_values) > 1 else 0

        # Plateau criteria: low coefficient of variation and flat trend
        plateau_detected = cv < 0.01 and abs(slope) < 0.1
        confidence = 1.0 - cv if cv < 1.0 else 0.0

        return {
            'plateau_detected': plateau_detected,
            'confidence': confidence,
            'coefficient_variation': cv,
            'trend_slope': slope
        }

    def _overfitting_analysis(self) -> Dict[str, Any]:
        """Analyze overfitting by comparing training and validation metrics."""

        train_losses = [r['train_loss'] for r in self.training_history if r['train_loss'] is not None]
        val_losses = [r['val_loss'] for r in self.training_history if r['val_loss'] is not None]

        if len(train_losses) < 5 or len(val_losses) < 5:
            return {'overfitting_detected': False, 'confidence': 0.0}

        # Calculate recent trends
        recent_train = train_losses[-5:]
        recent_val = val_losses[-5:]

        # Training loss should be decreasing, validation loss should be increasing for overfitting
        train_trend = np.polyfit(range(len(recent_train)), recent_train, 1)[0]
        val_trend = np.polyfit(range(len(recent_val)), recent_val, 1)[0]

        # Gap between train and validation
        avg_train = np.mean(recent_train)
        avg_val = np.mean(recent_val)
        gap = avg_val - avg_train

        # Overfitting criteria
        overfitting_detected = train_trend < -0.001 and val_trend > 0.001 and gap > 0.1
        confidence = min(abs(train_trend) + val_trend + gap/10, 1.0) if overfitting_detected else 0.0

        return {
            'overfitting_detected': overfitting_detected,
            'confidence': confidence,
            'train_trend': train_trend,
            'val_trend': val_trend,
            'performance_gap': gap
        }

    def _statistical_significance_analysis(self, metric_values: List[float]) -> Dict[str, Any]:
        """Statistical significance test for improvement."""

        if len(metric_values) < 20:
            return {'statistically_significant': False, 'confidence': 0.0}

        # Split into two halves
        mid_point = len(metric_values) // 2
        first_half = metric_values[:mid_point]
        second_half = metric_values[mid_point:]

        # Simple t-test-like analysis
        mean1, std1 = np.mean(first_half), np.std(first_half)
        mean2, std2 = np.mean(second_half), np.std(second_half)

        # Calculate effect size (Cohen's d)
        pooled_std = math.sqrt((std1**2 + std2**2) / 2)
        effect_size = abs(mean2 - mean1) / pooled_std if pooled_std > 0 else 0

        # Statistical significance criteria
        significant = effect_size > 0.8  # Large effect size
        confidence = min(effect_size / 2.0, 1.0)

        return {
            'statistically_significant': significant,
            'confidence': confidence,
            'effect_size': effect_size,
            'improvement': mean1 - mean2  # Assuming lower is better
        }

    def _combine_analyses(self,
                         patience_analysis: Dict[str, Any],
                         plateau_analysis: Dict[str, Any],
                         overfitting_analysis: Dict[str, Any],
                         statistical_analysis: Dict[str, Any],
                         metric_values: List[float]) -> EarlyStoppingRecommendation:
        """Combine multiple analyses into final recommendation."""

        # Weight different factors
        patience_weight = 0.4
        plateau_weight = 0.3
        overfitting_weight = 0.2
        statistical_weight = 0.1

        # Calculate overall confidence for stopping
        stop_confidence = (
            patience_analysis['confidence'] * patience_weight +
            plateau_analysis['confidence'] * plateau_weight +
            overfitting_analysis['confidence'] * overfitting_weight +
            statistical_analysis['confidence'] * statistical_weight
        )

        should_stop = stop_confidence > 0.7

        # Determine primary reason
        if patience_analysis['should_stop'] and patience_analysis['confidence'] > 0.8:
            reason = f"Patience exhausted: no improvement for {patience_analysis['patience_counter']} epochs"
        elif plateau_analysis['plateau_detected']:
            reason = f"Training plateaued: CV={plateau_analysis['coefficient_variation']:.4f}"
        elif overfitting_analysis['overfitting_detected']:
            reason = f"Overfitting detected: validation gap={overfitting_analysis['performance_gap']:.4f}"
        elif statistical_analysis['statistically_significant']:
            reason = f"No statistically significant improvement: effect size={statistical_analysis['effect_size']:.3f}"
        else:
            reason = "Training appears to be progressing normally"

        # Risk assessment
        if stop_confidence > 0.9:
            risk = "low"
        elif stop_confidence > 0.7:
            risk = "medium"
        else:
            risk = "high"

        # Suggested actions
        suggested_actions = []
        if should_stop:
            suggested_actions.extend([
                f"Stop training and use model from epoch {patience_analysis['best_epoch']}",
                "Consider reducing learning rate and resuming training",
                "Evaluate model performance on test set"
            ])
        else:
            if stop_confidence > 0.5:
                suggested_actions.append("Monitor closely - consider stopping soon")
            suggested_actions.extend([
                "Continue training with current settings",
                "Consider learning rate scheduling",
                "Monitor for overfitting signs"
            ])

        return EarlyStoppingRecommendation(
            should_stop=should_stop,
            confidence=stop_confidence,
            reason=reason,
            optimal_epoch=patience_analysis['best_epoch'],
            performance_at_optimal=patience_analysis['best_value'],
            potential_improvement=abs(metric_values[-1] - patience_analysis['best_value']) if metric_values else 0.0,
            risk_assessment=risk,
            suggested_actions=suggested_actions
        )

    def create_interactive_analysis_dashboard(self) -> str:
        """Create interactive early stopping analysis dashboard."""

        if not self.training_history:
            return self._create_empty_analysis_dashboard()

        # Get current recommendation
        recommendation = self.analyze_training_curve()

        # Prepare data for visualization
        train_losses = [r['train_loss'] for r in self.training_history]
        val_losses = [r['val_loss'] for r in self.training_history if r['val_loss'] is not None]
        epochs = list(range(len(train_losses)))

        dashboard_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Early Stopping Analysis - OpenFinOps</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }}

        .analysis-container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}

        .recommendation-panel {{
            background: {'rgba(244, 67, 54, 0.1)' if recommendation.should_stop else 'rgba(76, 175, 80, 0.1)'};
            border: 2px solid {'#f44336' if recommendation.should_stop else '#4caf50'};
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}

        .recommendation-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}

        .recommendation-icon {{
            font-size: 2em;
            margin-right: 15px;
        }}

        .confidence-bar {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 15px 0;
        }}

        .confidence-fill {{
            height: 100%;
            background: {'linear-gradient(90deg, #f44336, #ff9800)' if recommendation.should_stop else 'linear-gradient(90deg, #4caf50, #8bc34a)'};
            width: {recommendation.confidence * 100:.1f}%;
            border-radius: 10px;
            transition: all 0.5s ease;
        }}

        .controls-panel {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .control-group {{
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .slider-container {{
            margin: 15px 0;
        }}

        .slider {{
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.3);
            outline: none;
        }}

        .chart-container {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }}

        .actions-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .action-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 15px;
            border-left: 4px solid #2196f3;
        }}

        .action-item {{
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .metrics-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}

        .metric-box {{
            background: rgba(255, 255, 255, 0.08);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #64ffda;
        }}
    </style>
</head>
<body>
    <div class="analysis-container">
        <div class="header">
            <h1>🎯 Interactive Early Stopping Analysis</h1>
            <p>Advanced AI Training Decision Support System</p>
        </div>

        <div class="recommendation-panel">
            <div class="recommendation-header">
                <span class="recommendation-icon">{'🛑' if recommendation.should_stop else '✅'}</span>
                <div>
                    <h2>{'STOP TRAINING RECOMMENDED' if recommendation.should_stop else 'CONTINUE TRAINING'}</h2>
                    <p>{recommendation.reason}</p>
                </div>
            </div>

            <div class="confidence-bar">
                <div class="confidence-fill"></div>
            </div>
            <p>Confidence: {recommendation.confidence:.1%} | Risk Assessment: {recommendation.risk_assessment.title()}</p>
        </div>

        <div class="metrics-summary">
            <div class="metric-box">
                <div class="metric-value">{len(self.training_history)}</div>
                <div>Total Epochs</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{recommendation.optimal_epoch}</div>
                <div>Best Epoch</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{recommendation.performance_at_optimal:.4f}</div>
                <div>Best Performance</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{recommendation.potential_improvement:.4f}</div>
                <div>Potential Improvement</div>
            </div>
        </div>

        <div class="controls-panel">
            <div class="control-group">
                <h3>🎛️ Patience Settings</h3>
                <div class="slider-container">
                    <label>Patience: <span id="patienceValue">10</span> epochs</label>
                    <input type="range" class="slider" id="patienceSlider" min="1" max="50" value="10"
                           oninput="updatePatienceValue(this.value)">
                </div>
                <div class="slider-container">
                    <label>Min Delta: <span id="deltaValue">0.001</span></label>
                    <input type="range" class="slider" id="deltaSlider" min="0.0001" max="0.01" step="0.0001" value="0.001"
                           oninput="updateDeltaValue(this.value)">
                </div>
            </div>

            <div class="control-group">
                <h3>📊 Monitor Settings</h3>
                <select id="metricSelect" onchange="updateMonitorMetric()"
                        style="width: 100%; padding: 10px; border-radius: 5px; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.3);">
                    <option value="val_loss">Validation Loss</option>
                    <option value="val_metric">Validation Metric</option>
                    <option value="train_loss">Training Loss</option>
                </select>
                <label style="margin-top: 15px; display: block;">
                    <input type="checkbox" id="restoreWeights" checked> Restore Best Weights
                </label>
            </div>

            <div class="control-group">
                <h3>🔍 Analysis Methods</h3>
                <label><input type="checkbox" id="patienceMethod" checked> Patience-Based</label><br>
                <label><input type="checkbox" id="plateauMethod" checked> Plateau Detection</label><br>
                <label><input type="checkbox" id="overfittingMethod" checked> Overfitting Analysis</label><br>
                <label><input type="checkbox" id="statisticalMethod" checked> Statistical Significance</label>
            </div>

            <div class="control-group">
                <h3>⚙️ Actions</h3>
                <button onclick="reanalyzeTraining()"
                        style="width: 100%; padding: 10px; background: #2196f3; color: white; border: none; border-radius: 5px; margin-bottom: 10px; cursor: pointer;">
                    🔄 Re-analyze with New Settings
                </button>
                <button onclick="exportAnalysis()"
                        style="width: 100%; padding: 10px; background: #4caf50; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    💾 Export Analysis
                </button>
            </div>
        </div>

        <div class="chart-container">
            <h3>📈 Training Progress Visualization</h3>
            <div id="trainingChart">
                <svg width="100%" height="400" id="trainingSvg"></svg>
            </div>
        </div>

        <div class="actions-grid">
            <div class="action-card">
                <h3>💡 Suggested Actions</h3>
                <div id="suggestedActions">
                    {"".join([f'<div class="action-item">• {action}</div>' for action in recommendation.suggested_actions])}
                </div>
            </div>

            <div class="action-card">
                <h3>📊 Analysis Details</h3>
                <div class="action-item">
                    <strong>Optimal Stopping Point:</strong> Epoch {recommendation.optimal_epoch}
                </div>
                <div class="action-item">
                    <strong>Performance at Optimal:</strong> {recommendation.performance_at_optimal:.6f}
                </div>
                <div class="action-item">
                    <strong>Current Performance:</strong> {train_losses[-1]:.6f}
                </div>
                <div class="action-item">
                    <strong>Risk Level:</strong> {recommendation.risk_assessment.title()}
                </div>
            </div>
        </div>
    </div>

    <script>
        // Training data
        const trainingData = {{
            epochs: {epochs},
            trainLosses: {train_losses},
            valLosses: {val_losses},
            recommendation: {{
                'should_stop': {str(recommendation.should_stop).lower()},
                'confidence': {recommendation.confidence},
                'optimal_epoch': {recommendation.optimal_epoch},
                'reason': '{recommendation.reason}'
            }}
        }};

        function updatePatienceValue(value) {{
            document.getElementById('patienceValue').textContent = value;
        }}

        function updateDeltaValue(value) {{
            document.getElementById('deltaValue').textContent = parseFloat(value).toFixed(4);
        }}

        function updateMonitorMetric() {{
            const metric = document.getElementById('metricSelect').value;
            console.log('Monitor metric changed to:', metric);
        }}

        function reanalyzeTraining() {{
            // Get current settings
            const settings = {{
                patience: document.getElementById('patienceSlider').value,
                minDelta: document.getElementById('deltaSlider').value,
                monitorMetric: document.getElementById('metricSelect').value,
                restoreWeights: document.getElementById('restoreWeights').checked
            }};

            console.log('Re-analyzing with settings:', settings);
            alert('Analysis updated with new settings!\\nNote: This would trigger server-side re-analysis in a full implementation.');
        }}

        function exportAnalysis() {{
            const analysisData = {{
                trainingData: trainingData,
                recommendation: trainingData.recommendation,
                timestamp: new Date().toISOString()
            }};

            const blob = new Blob([JSON.stringify(analysisData, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'early_stopping_analysis.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}

        function generateTrainingChart() {{
            const svg = document.getElementById('trainingSvg');
            const width = svg.clientWidth || 800;
            const height = 400;

            svg.setAttribute('width', width);
            svg.setAttribute('height', height);

            // Clear existing content
            svg.innerHTML = '';

            const margin = 50;
            const chartWidth = width - 2 * margin;
            const chartHeight = height - 2 * margin;

            // Background
            const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            bg.setAttribute('width', '100%');
            bg.setAttribute('height', '100%');
            bg.setAttribute('fill', 'rgba(0,0,0,0.3)');
            svg.appendChild(bg);

            if (trainingData.trainLosses.length === 0) return;

            // Calculate scales
            const maxEpoch = Math.max(...trainingData.epochs);
            const minLoss = Math.min(...trainingData.trainLosses);
            const maxLoss = Math.max(...trainingData.trainLosses);

            const xScale = chartWidth / maxEpoch;
            const yScale = chartHeight / (maxLoss - minLoss);

            // Draw training loss line
            if (trainingData.trainLosses.length > 1) {{
                let pathData = `M ${{margin + trainingData.epochs[0] * xScale}} ${{margin + (maxLoss - trainingData.trainLosses[0]) * yScale}}`;
                for (let i = 1; i < trainingData.trainLosses.length; i++) {{
                    pathData += ` L ${{margin + trainingData.epochs[i] * xScale}} ${{margin + (maxLoss - trainingData.trainLosses[i]) * yScale}}`;
                }}

                const trainPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                trainPath.setAttribute('d', pathData);
                trainPath.setAttribute('stroke', '#2196f3');
                trainPath.setAttribute('stroke-width', '2');
                trainPath.setAttribute('fill', 'none');
                svg.appendChild(trainPath);
            }}

            // Draw validation loss line if available
            if (trainingData.valLosses.length > 1) {{
                let pathData = `M ${{margin + 0 * xScale}} ${{margin + (maxLoss - trainingData.valLosses[0]) * yScale}}`;
                for (let i = 1; i < trainingData.valLosses.length; i++) {{
                    pathData += ` L ${{margin + i * xScale}} ${{margin + (maxLoss - trainingData.valLosses[i]) * yScale}}`;
                }}

                const valPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                valPath.setAttribute('d', pathData);
                valPath.setAttribute('stroke', '#f44336');
                valPath.setAttribute('stroke-width', '2');
                valPath.setAttribute('fill', 'none');
                valPath.setAttribute('stroke-dasharray', '5,5');
                svg.appendChild(valPath);
            }}

            // Mark optimal epoch
            const optimalX = margin + trainingData.recommendation.optimal_epoch * xScale;
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', optimalX);
            line.setAttribute('y1', margin);
            line.setAttribute('x2', optimalX);
            line.setAttribute('y2', height - margin);
            line.setAttribute('stroke', '#4caf50');
            line.setAttribute('stroke-width', '2');
            line.setAttribute('stroke-dasharray', '10,5');
            svg.appendChild(line);

            // Add labels
            const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            title.setAttribute('x', width / 2);
            title.setAttribute('y', 30);
            title.setAttribute('text-anchor', 'middle');
            title.setAttribute('fill', '#cfd8dc');
            title.setAttribute('font-size', '16');
            title.setAttribute('font-weight', 'bold');
            title.textContent = 'Training Progress Analysis';
            svg.appendChild(title);

            // Legend
            const legend = document.createElementNS('http://www.w3.org/2000/svg', 'g');

            const trainLegend = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            trainLegend.setAttribute('x', margin);
            trainLegend.setAttribute('y', height - 10);
            trainLegend.setAttribute('fill', '#2196f3');
            trainLegend.setAttribute('font-size', '12');
            trainLegend.textContent = 'Training Loss';
            legend.appendChild(trainLegend);

            if (trainingData.valLosses.length > 0) {{
                const valLegend = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                valLegend.setAttribute('x', margin + 120);
                valLegend.setAttribute('y', height - 10);
                valLegend.setAttribute('fill', '#f44336');
                valLegend.setAttribute('font-size', '12');
                valLegend.textContent = 'Validation Loss';
                legend.appendChild(valLegend);
            }}

            const optimalLegend = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            optimalLegend.setAttribute('x', margin + 240);
            optimalLegend.setAttribute('y', height - 10);
            optimalLegend.setAttribute('fill', '#4caf50');
            optimalLegend.setAttribute('font-size', '12');
            optimalLegend.textContent = 'Optimal Stop Point';
            legend.appendChild(optimalLegend);

            svg.appendChild(legend);
        }}

        // Initialize chart
        generateTrainingChart();

        // Auto-refresh chart on window resize
        window.addEventListener('resize', generateTrainingChart);

        console.log('🎯 Interactive Early Stopping Analysis loaded successfully!');
    </script>
</body>
</html>
        """

        return dashboard_html

    def _create_empty_analysis_dashboard(self) -> str:
        """Create empty dashboard when no training data is available."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Early Stopping Analysis - No Data</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .waiting { font-size: 24px; color: #666; }
    </style>
</head>
<body>
    <div class="waiting">
        🎯 Early Stopping Analysis<br><br>
        No training data available...<br>
        <small>Add epoch data with add_epoch_data() method</small>
    </div>
</body>
</html>
        """

    def save_analysis_dashboard(self, filename: str = 'early_stopping_analysis.html') -> str:
        """Save the interactive analysis dashboard."""
        html_content = self.create_interactive_analysis_dashboard()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return filename