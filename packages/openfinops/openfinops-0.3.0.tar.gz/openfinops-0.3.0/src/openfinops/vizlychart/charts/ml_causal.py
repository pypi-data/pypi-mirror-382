"""
Machine Learning & Causal Inference Visualization
=================================================

Specialized charts for ML model explainability, causal analysis, and data science workflows.
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

import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

from .base import BaseChart
from ..figure import VizlyFigure

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


@dataclass
class CausalNode:
    """Node in a causal graph."""
    name: str
    x: float = 0.0
    y: float = 0.0
    node_type: str = "variable"  # variable, treatment, outcome, confounder
    color: str = "lightblue"
    size: float = 1.0


@dataclass
class CausalEdge:
    """Edge in a causal graph."""
    source: str
    target: str
    strength: float = 1.0
    edge_type: str = "causal"  # causal, confounding, selection
    color: str = "black"
    style: str = "solid"  # solid, dashed, dotted


class CausalDAGChart(BaseChart):
    """Directed Acyclic Graph visualization for causal inference."""

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)
        self.nodes: List[CausalNode] = []
        self.edges: List[CausalEdge] = []
        self._positions_computed = False

    def add_node(self, name: str, node_type: str = "variable",
                 position: Optional[Tuple[float, float]] = None, **kwargs) -> 'CausalDAGChart':
        """Add a node to the causal graph."""
        color_map = {
            "variable": "#87CEEB",      # SkyBlue
            "treatment": "#32CD32",     # LimeGreen
            "outcome": "#FF6347",       # Tomato
            "confounder": "#FFD700",    # Gold
            "mediator": "#DA70D6"       # Orchid
        }

        x, y = position if position else (0, 0)
        node = CausalNode(
            name=name,
            x=x, y=y,
            node_type=node_type,
            color=color_map.get(node_type, "#87CEEB"),
            **kwargs
        )
        self.nodes.append(node)
        return self

    def add_edge(self, source: str, target: str, strength: float = 1.0,
                 edge_type: str = "causal", **kwargs) -> 'CausalDAGChart':
        """Add a causal edge between nodes."""
        color_map = {
            "causal": "black",
            "confounding": "red",
            "selection": "blue",
            "instrumental": "green"
        }

        edge = CausalEdge(
            source=source,
            target=target,
            strength=strength,
            edge_type=edge_type,
            color=color_map.get(edge_type, "black"),
            **kwargs
        )
        self.edges.append(edge)
        return self

    def auto_layout(self, layout: str = "hierarchical") -> 'CausalDAGChart':
        """Automatically compute node positions."""
        if not HAS_NETWORKX:
            warnings.warn("NetworkX required for auto-layout. Using manual positioning.")
            return self._manual_layout()

        # Create NetworkX graph
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node.name, node_type=node.node_type)

        for edge in self.edges:
            G.add_edge(edge.source, edge.target, weight=edge.strength)

        # Compute layout
        if layout == "hierarchical":
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            except:
                pos = self._hierarchical_layout(G)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "spring":
            pos = nx.spring_layout(G, k=2, iterations=50)
        else:
            pos = nx.spring_layout(G)

        # Update node positions
        for node in self.nodes:
            if node.name in pos:
                node.x, node.y = pos[node.name]

        self._positions_computed = True
        return self

    def _hierarchical_layout(self, G) -> Dict[str, Tuple[float, float]]:
        """Manual hierarchical layout when graphviz is unavailable."""
        # Topological sort to get hierarchy
        try:
            topo_order = list(nx.topological_sort(G))
        except:
            topo_order = list(G.nodes())

        pos = {}
        levels = {}

        # Assign levels
        for i, node in enumerate(topo_order):
            level = 0
            for pred in G.predecessors(node):
                if pred in levels:
                    level = max(level, levels[pred] + 1)
            levels[node] = level

        # Position nodes
        level_counts = {}
        for node, level in levels.items():
            if level not in level_counts:
                level_counts[level] = 0

            x = level * 3.0
            y = level_counts[level] * 2.0
            pos[node] = (x, y)
            level_counts[level] += 1

        return pos

    def _manual_layout(self) -> 'CausalDAGChart':
        """Fallback manual layout."""
        for i, node in enumerate(self.nodes):
            angle = 2 * np.pi * i / len(self.nodes)
            node.x = 5 * np.cos(angle)
            node.y = 5 * np.sin(angle)
        return self

    def plot(self) -> 'CausalDAGChart':
        """Render the causal DAG."""
        if not self._positions_computed:
            self.auto_layout()

        ax = self._get_axes()

        # Draw edges first (so they appear behind nodes)
        for edge in self.edges:
            source_node = next((n for n in self.nodes if n.name == edge.source), None)
            target_node = next((n for n in self.nodes if n.name == edge.target), None)

            if source_node and target_node:
                # Draw arrow
                ax.annotate('', xy=(target_node.x, target_node.y),
                           xytext=(source_node.x, source_node.y),
                           arrowprops=dict(
                               arrowstyle='->',
                               color=edge.color,
                               lw=edge.strength * 2,
                               linestyle=edge.style
                           ))

        # Draw nodes
        for node in self.nodes:
            circle = plt.Circle((node.x, node.y), 0.5 * node.size,
                               color=node.color, ec='black', linewidth=2)
            ax.add_patch(circle)

            # Add node label
            ax.text(node.x, node.y, node.name, ha='center', va='center',
                   fontsize=10, fontweight='bold')

        # Set axis properties
        all_x = [n.x for n in self.nodes]
        all_y = [n.y for n in self.nodes]

        margin = 1.5
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        ax.set_aspect('equal')
        ax.axis('off')

        return self

    def add_legend(self) -> 'CausalDAGChart':
        """Add legend explaining node and edge types."""
        import matplotlib.patches as mpatches

        ax = self._get_axes()

        # Node type legend
        node_types = set(node.node_type for node in self.nodes)
        node_legend = []

        color_map = {
            "variable": "#87CEEB",
            "treatment": "#32CD32",
            "outcome": "#FF6347",
            "confounder": "#FFD700",
            "mediator": "#DA70D6"
        }

        for node_type in node_types:
            patch = mpatches.Patch(color=color_map.get(node_type, "#87CEEB"),
                                 label=node_type.title())
            node_legend.append(patch)

        if node_legend:
            ax.legend(handles=node_legend, loc='upper right', title='Node Types')

        return self


class FeatureImportanceChart(BaseChart):
    """Chart for visualizing ML model feature importance."""

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)

    def plot(self, features: List[str], importance: np.ndarray,
             importance_type: str = "permutation", **kwargs) -> 'FeatureImportanceChart':
        """
        Plot feature importance.

        Args:
            features: Feature names
            importance: Importance values
            importance_type: Type of importance (permutation, shap, etc.)
        """
        ax = self._get_axes()

        # Sort by importance
        sorted_idx = np.argsort(importance)
        sorted_features = [features[i] for i in sorted_idx]
        sorted_importance = importance[sorted_idx]

        # Color scheme based on importance type
        color_map = {
            "permutation": "steelblue",
            "shap": "forestgreen",
            "gini": "orangered",
            "mutual_info": "purple"
        }
        color = color_map.get(importance_type, "steelblue")

        # Horizontal bar chart
        y_pos = np.arange(len(sorted_features))
        bars = ax.barh(y_pos, sorted_importance, color=color, alpha=0.7)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, sorted_importance)):
            ax.text(bar.get_width() + max(sorted_importance) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'{value:.3f}', va='center', fontsize=9)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(sorted_features)
        ax.set_xlabel(f'{importance_type.title()} Importance')
        ax.set_title(f'Feature Importance ({importance_type.title()})')
        ax.grid(axis='x', alpha=0.3)

        return self


class SHAPWaterfallChart(BaseChart):
    """SHAP waterfall chart for model explainability."""

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)

    def plot(self, features: List[str], shap_values: np.ndarray,
             base_value: float, prediction: float, **kwargs) -> 'SHAPWaterfallChart':
        """
        Plot SHAP waterfall chart.

        Args:
            features: Feature names
            shap_values: SHAP values for each feature
            base_value: Model's base/expected value
            prediction: Final prediction value
        """
        ax = self._get_axes()

        # Sort by absolute SHAP values
        sorted_idx = np.argsort(np.abs(shap_values))[::-1]
        sorted_features = [features[i] for i in sorted_idx]
        sorted_shap = shap_values[sorted_idx]

        # Calculate cumulative values for waterfall
        cumulative = np.zeros(len(sorted_shap) + 2)
        cumulative[0] = base_value

        for i, shap_val in enumerate(sorted_shap):
            cumulative[i + 1] = cumulative[i] + shap_val

        cumulative[-1] = prediction

        # Plot waterfall bars
        x_pos = range(len(cumulative))
        colors = ['gray']  # Base value

        for shap_val in sorted_shap:
            colors.append('green' if shap_val > 0 else 'red')
        colors.append('blue')  # Final prediction

        # Draw connecting lines and bars
        for i in range(len(cumulative) - 1):
            # Connecting line
            ax.plot([i + 0.4, i + 0.6], [cumulative[i], cumulative[i]],
                   'k--', alpha=0.5, linewidth=1)

            # Bar
            if i == 0:  # Base value
                ax.bar(i, cumulative[i], color=colors[i], alpha=0.7, width=0.8)
            else:  # Feature contributions
                bar_height = sorted_shap[i-1]
                bar_bottom = cumulative[i] - bar_height if bar_height > 0 else cumulative[i]
                ax.bar(i, abs(bar_height), bottom=bar_bottom,
                      color=colors[i], alpha=0.7, width=0.8)

        # Final prediction bar
        ax.bar(len(cumulative) - 1, prediction, color=colors[-1], alpha=0.7, width=0.8)

        # Labels
        labels = ['Base'] + sorted_features + ['Prediction']
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylabel('Value')
        ax.set_title('SHAP Waterfall Chart')
        ax.grid(axis='y', alpha=0.3)

        # Add value annotations
        for i, val in enumerate(cumulative):
            ax.text(i, val + (max(cumulative) - min(cumulative)) * 0.01,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=9)

        return self


class ModelPerformanceChart(BaseChart):
    """Chart for comparing model performance metrics."""

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)

    def plot_roc_curves(self, roc_data: Dict[str, Tuple[np.ndarray, np.ndarray, float]],
                       **kwargs) -> 'ModelPerformanceChart':
        """
        Plot ROC curves for multiple models.

        Args:
            roc_data: Dict mapping model names to (fpr, tpr, auc) tuples
        """
        ax = self._get_axes()

        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

        for i, (model_name, (fpr, tpr, auc)) in enumerate(roc_data.items()):
            color = colors[i % len(colors)]
            ax.plot(fpr, tpr, color=color, linewidth=2,
                   label=f'{model_name} (AUC = {auc:.3f})')

        # Diagonal line for random classifier
        ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random')

        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('ROC Curves Comparison')
        ax.legend()
        ax.grid(alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])

        return self

    def plot_precision_recall(self, pr_data: Dict[str, Tuple[np.ndarray, np.ndarray, float]],
                             **kwargs) -> 'ModelPerformanceChart':
        """
        Plot Precision-Recall curves for multiple models.

        Args:
            pr_data: Dict mapping model names to (precision, recall, ap) tuples
        """
        ax = self._get_axes()

        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

        for i, (model_name, (precision, recall, ap)) in enumerate(pr_data.items()):
            color = colors[i % len(colors)]
            ax.plot(recall, precision, color=color, linewidth=2,
                   label=f'{model_name} (AP = {ap:.3f})')

        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        ax.set_title('Precision-Recall Curves Comparison')
        ax.legend()
        ax.grid(alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])

        return self


class ConfusionMatrixChart(BaseChart):
    """Enhanced confusion matrix visualization."""

    def __init__(self, figure: Optional[VizlyFigure] = None):
        super().__init__(figure)

    def plot(self, confusion_matrix: np.ndarray, class_names: Optional[List[str]] = None,
             normalize: bool = False, **kwargs) -> 'ConfusionMatrixChart':
        """
        Plot confusion matrix with enhanced visualization.

        Args:
            confusion_matrix: 2D array of confusion matrix
            class_names: Names of classes
            normalize: Whether to normalize the matrix
        """
        ax = self._get_axes()

        if normalize:
            cm = confusion_matrix.astype('float') / confusion_matrix.sum(axis=1)[:, np.newaxis]
            fmt = '.2f'
            title = 'Normalized Confusion Matrix'
        else:
            cm = confusion_matrix
            fmt = 'd'
            title = 'Confusion Matrix'

        # Plot heatmap
        im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
        ax.figure.colorbar(im, ax=ax)

        # Add labels
        if class_names is None:
            class_names = [f'Class {i}' for i in range(cm.shape[0])]

        ax.set_xticks(np.arange(cm.shape[1]))
        ax.set_yticks(np.arange(cm.shape[0]))
        ax.set_xticklabels(class_names)
        ax.set_yticklabels(class_names)

        # Rotate the tick labels and set their alignment
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add text annotations
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], fmt),
                       ha="center", va="center",
                       color="white" if cm[i, j] > thresh else "black",
                       fontweight='bold')

        ax.set_title(title)
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')

        return self


# Import matplotlib.pyplot here to avoid circular imports
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches
except ImportError:
    plt = None