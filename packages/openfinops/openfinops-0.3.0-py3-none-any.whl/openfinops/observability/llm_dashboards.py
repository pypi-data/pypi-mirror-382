#!/usr/bin/env python3
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

"""
LLM/RAG/Agent Observability Dashboards
======================================

Professional visualization dashboards for LLM training, RAG building,
and Agentic AI process monitoring using OpenFinOps's rendering engine.
"""

import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import numpy as np
from collections import defaultdict

# Import OpenFinOps components
try:
    from ..charts import LineChart, ScatterChart, BarChart
    from ..figure import VizlyFigure
    from ..theme import VizlyTheme
    VIZLYCHART_AVAILABLE = True
except ImportError:
    VIZLYCHART_AVAILABLE = False

from .llm_observability import (
    LLMObservabilityHub, LLMTrainingMetrics, RAGPipelineMetrics,
    AgentWorkflowMetrics, EnterpriseGovernanceMetrics,
    LLMTrainingStage, RAGStage, AgentWorkflowStage
)


class LLMObservabilityVisualizer:
    """
    Professional visualization system for LLM/RAG/Agent observability.
    """

    def __init__(self, theme: str = "professional"):
        self.theme_name = theme
        if VIZLYCHART_AVAILABLE:
            self.theme = VizlyTheme.get_theme(theme) if hasattr(VizlyTheme, 'get_theme') else None

        self.colors = self._init_llm_color_palette()

    def _init_llm_color_palette(self) -> Dict[str, str]:
        """Initialize LLM-specific color palette."""
        return {
            # Training metrics
            'train_loss': '#FF6B6B',
            'val_loss': '#4ECDC4',
            'perplexity': '#45B7D1',
            'learning_rate': '#96CEB4',
            'gradient_norm': '#FECA57',

            # Resource usage
            'gpu_memory': '#FF9FF3',
            'gpu_util': '#54A0FF',
            'cpu_util': '#5F27CD',
            'tokens_per_sec': '#00D2D3',

            # RAG metrics
            'retrieval_accuracy': '#2ED573',
            'generation_quality': '#FFA502',
            'latency': '#FF6348',
            'cost': '#3742FA',

            # Agent metrics
            'success_rate': '#2F7ED8',
            'efficiency': '#0AD084',
            'confidence': '#FFD700',
            'tool_usage': '#FF6B9D',

            # Governance
            'compliance': '#26de81',
            'risk': '#fc5c65',
            'spend': '#fd79a8',
            'performance': '#fdcb6e',

            # UI elements
            'background': '#1a1a1a',
            'surface': '#2d2d2d',
            'text': '#ffffff',
            'grid': '#404040'
        }

    def create_llm_training_dashboard(self, hub: LLMObservabilityHub, run_id: str,
                                    width: int = 1200, height: int = 800) -> str:
        """Create comprehensive LLM training dashboard."""
        # Get training metrics for the specific run
        run_metrics = [m for m in hub.llm_training_metrics if m.run_id == run_id]
        if not run_metrics:
            return self._fallback_chart("No Training Data Available", width, height)

        # Create simplified dashboard with data visualization
        latest_metric = run_metrics[-1]
        avg_loss = sum(m.train_loss for m in run_metrics) / len(run_metrics)

        dashboard_content = f"""
        <div class="llm-training-dashboard">
            <h3>LLM Training Dashboard - {run_id}</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.train_loss:.4f}</div>
                    <div class="metric-label">Current Training Loss</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.validation_loss:.4f}</div>
                    <div class="metric-label">Validation Loss</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.tokens_per_second:.0f}</div>
                    <div class="metric-label">Tokens/Second</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.gpu_utilization:.1f}%</div>
                    <div class="metric-label">GPU Utilization</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.progress_percent:.1f}%</div>
                    <div class="metric-label">Training Progress</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${latest_metric.estimated_total_cost:.0f}</div>
                    <div class="metric-label">Estimated Cost</div>
                </div>
            </div>
            <div class="training-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {latest_metric.progress_percent}%"></div>
                </div>
                <p>Step {latest_metric.step} of {latest_metric.total_steps}</p>
            </div>
        </div>
        """

        # Add professional styling and interactivity
        styled_content = self._add_professional_styling(dashboard_content, "LLM Training Metrics")

        return styled_content

    def create_rag_pipeline_dashboard(self, hub: LLMObservabilityHub, pipeline_id: str,
                                    width: int = 1200, height: int = 600) -> str:
        """Create RAG pipeline monitoring dashboard."""
        # Get RAG metrics for the specific pipeline
        rag_metrics = [m for m in hub.rag_pipeline_metrics if m.pipeline_id == pipeline_id]
        if not rag_metrics:
            return self._fallback_chart("No RAG Pipeline Data Available", width, height)

        # Get latest metrics and calculate averages
        latest_metric = rag_metrics[-1]
        avg_latency = sum(m.latency_p95 for m in rag_metrics[-10:]) / min(10, len(rag_metrics))
        avg_accuracy = sum(m.retrieval_accuracy for m in rag_metrics[-10:]) / min(10, len(rag_metrics))

        dashboard_content = f"""
        <div class="rag-pipeline-dashboard">
            <h3>RAG Pipeline Dashboard - {pipeline_id}</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.latency_p95:.0f}ms</div>
                    <div class="metric-label">Current Latency P95</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.retrieval_accuracy:.2%}</div>
                    <div class="metric-label">Retrieval Accuracy</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.documents_processed:,}</div>
                    <div class="metric-label">Documents Processed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.throughput:.0f}</div>
                    <div class="metric-label">Throughput (items/sec)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${latest_metric.cost_per_query:.4f}</div>
                    <div class="metric-label">Cost per Query</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.error_rate:.2%}</div>
                    <div class="metric-label">Error Rate</div>
                </div>
            </div>
            <div class="pipeline-health">
                <div class="health-indicator {('healthy' if latest_metric.error_rate < 0.05 else 'warning')}">
                    Pipeline Status: {'🟢 Healthy' if latest_metric.error_rate < 0.05 else '🟡 Warning'}
                </div>
            </div>
        </div>
        """

        styled_content = self._add_professional_styling(dashboard_content, "RAG Pipeline Performance")
        return styled_content

    def create_agent_workflow_dashboard(self, hub: LLMObservabilityHub, agent_id: str,
                                      width: int = 1200, height: int = 600) -> str:
        """Create agent workflow monitoring dashboard."""
        # Get agent metrics
        agent_metrics = [m for m in hub.agent_workflow_metrics if m.agent_id == agent_id]
        if not agent_metrics:
            return self._fallback_chart("No Agent Data Available", width, height)

        # Calculate aggregated metrics
        latest_metric = agent_metrics[-1]
        avg_success_rate = sum(m.task_success_rate for m in agent_metrics[-10:]) / min(10, len(agent_metrics))
        avg_execution_time = sum(m.execution_time for m in agent_metrics[-10:]) / min(10, len(agent_metrics))
        total_workflows = len(set(m.workflow_id for m in agent_metrics))

        dashboard_content = f"""
        <div class="agent-workflow-dashboard">
            <h3>Agent Workflow Dashboard - {agent_id}</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.task_success_rate:.1%}</div>
                    <div class="metric-label">Current Success Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.execution_time:.1f}s</div>
                    <div class="metric-label">Execution Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.efficiency_score:.2f}</div>
                    <div class="metric-label">Efficiency Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.confidence_score:.2f}</div>
                    <div class="metric-label">Confidence Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_workflows}</div>
                    <div class="metric-label">Total Workflows</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{latest_metric.total_tokens_used:,}</div>
                    <div class="metric-label">Tokens Used</div>
                </div>
            </div>
            <div class="agent-status">
                <div class="status-indicator {('excellent' if avg_success_rate > 0.9 else 'good' if avg_success_rate > 0.8 else 'warning')}">
                    Agent Performance: {('🟢 Excellent' if avg_success_rate > 0.9 else '🟡 Good' if avg_success_rate > 0.8 else '🟠 Needs Attention')}
                </div>
            </div>
        </div>
        """

        styled_content = self._add_professional_styling(dashboard_content, "Agent Performance Metrics")
        return styled_content

    def create_enterprise_governance_dashboard(self, hub: LLMObservabilityHub,
                                             width: int = 1400, height: int = 900) -> str:
        """Create enterprise AI governance dashboard."""
        dashboard_data = hub.get_enterprise_dashboard_data()
        if not dashboard_data:
            return self._fallback_chart("No Governance Data Available", width, height)

        governance = dashboard_data['governance_metrics']
        activity = dashboard_data['activity_summary']

        dashboard_content = f"""
        <div class="enterprise-governance-dashboard">
            <h3>Enterprise AI Governance Dashboard</h3>
            <div class="governance-overview">
                <div class="governance-section">
                    <h4>💰 Cost Management</h4>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${governance['monthly_spend']:,.0f}</div>
                            <div class="metric-label">Monthly Spend</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{governance['budget_utilization']:.1%}</div>
                            <div class="metric-label">Budget Utilization</div>
                        </div>
                    </div>
                </div>
                <div class="governance-section">
                    <h4>🔒 Compliance & Security</h4>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{governance['security_score']:.1%}</div>
                            <div class="metric-label">Security Score</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{governance['bias_score']:.3f}</div>
                            <div class="metric-label">Bias Score</div>
                        </div>
                    </div>
                </div>
                <div class="governance-section">
                    <h4>📊 Activity Overview</h4>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{activity['active_training_runs']}</div>
                            <div class="metric-label">Training Runs</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{activity['active_rag_pipelines']}</div>
                            <div class="metric-label">RAG Pipelines</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{activity['active_agents']}</div>
                            <div class="metric-label">Active Agents</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

        styled_content = self._add_professional_styling(dashboard_content, "Enterprise AI Governance")
        return styled_content

    def create_model_performance_comparison(self, hub: LLMObservabilityHub,
                                          model_ids: List[str],
                                          width: int = 1000, height: int = 600) -> str:
        """Create model performance comparison chart."""
        models = model_ids[:5] if model_ids else ["gpt-4-turbo", "llama-7b", "claude-3", "gemini-pro"]

        # Generate sample performance data (in practice would come from actual metrics)
        performance_data = {}
        for model in models:
            performance_data[model] = {
                'accuracy': 0.85 + random.uniform(-0.1, 0.1),
                'latency_ms': 50 + random.uniform(-20, 30),
                'cost_per_1k_tokens': 0.002 + random.uniform(-0.001, 0.002),
                'robustness_score': 0.8 + random.uniform(-0.1, 0.15)
            }

        dashboard_content = f"""
        <div class="model-comparison-dashboard">
            <h3>Model Performance Comparison</h3>
            <div class="comparison-grid">
                {self._generate_model_comparison_cards(performance_data)}
            </div>
            <div class="performance-summary">
                <h4>Performance Metrics Summary</h4>
                <div class="metrics-table">
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <thead>
                            <tr style="background: rgba(255,255,255,0.1);">
                                <th style="padding: 10px; text-align: left; color: #4ECDC4; font-weight: bold;">Model</th>
                                <th style="padding: 10px; text-align: center; color: #4ECDC4; font-weight: bold;">Accuracy</th>
                                <th style="padding: 10px; text-align: center; color: #4ECDC4; font-weight: bold;">Latency (ms)</th>
                                <th style="padding: 10px; text-align: center; color: #4ECDC4; font-weight: bold;">Cost per 1K tokens</th>
                                <th style="padding: 10px; text-align: center; color: #4ECDC4; font-weight: bold;">Robustness</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f'''
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <td style="padding: 10px; color: white; font-weight: bold;">{model}</td>
                                <td style="padding: 10px; text-align: center; color: white;">{data["accuracy"]:.2%}</td>
                                <td style="padding: 10px; text-align: center; color: white;">{data["latency_ms"]:.1f}</td>
                                <td style="padding: 10px; text-align: center; color: white;">${data["cost_per_1k_tokens"]:.4f}</td>
                                <td style="padding: 10px; text-align: center; color: white;">{data["robustness_score"]:.2f}</td>
                            </tr>
                            ''' for model, data in performance_data.items()])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """

        styled_content = self._add_professional_styling(dashboard_content, "Model Performance Analysis")
        return styled_content

    def _generate_model_comparison_cards(self, performance_data: Dict[str, Dict]) -> str:
        """Generate comparison cards for models."""
        cards_html = ""
        for model, data in performance_data.items():
            cards_html += f"""
            <div class="model-card">
                <h4 style="color: #4ECDC4; margin-bottom: 10px;">{model}</h4>
                <div class="model-metrics">
                    <div class="metric-item">
                        <span class="metric-label">Accuracy:</span>
                        <span class="metric-value">{data['accuracy']:.1%}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Latency:</span>
                        <span class="metric-value">{data['latency_ms']:.0f}ms</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Cost:</span>
                        <span class="metric-value">${data['cost_per_1k_tokens']:.4f}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Robustness:</span>
                        <span class="metric-value">{data['robustness_score']:.2f}</span>
                    </div>
                </div>
            </div>
            """
        return cards_html

    def create_token_usage_analytics(self, hub: LLMObservabilityHub,
                                   time_range_hours: int = 24,
                                   width: int = 1000, height: int = 500) -> str:
        """Create token usage analytics dashboard."""
        # Get recent RAG metrics for token usage
        current_time = time.time()
        cutoff_time = current_time - (time_range_hours * 3600)

        recent_rag_metrics = [m for m in hub.rag_pipeline_metrics if m.timestamp > cutoff_time]

        if recent_rag_metrics:
            total_tokens = sum(m.total_tokens for m in recent_rag_metrics)
            total_cost = sum(m.cost_per_query for m in recent_rag_metrics)
            avg_tokens_per_query = total_tokens / len(recent_rag_metrics) if recent_rag_metrics else 0

            dashboard_content = f"""
            <div class="token-usage-dashboard">
                <h3>Token Usage Analytics ({time_range_hours}h)</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{total_tokens:,}</div>
                        <div class="metric-label">Total Tokens Used</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${total_cost:.2f}</div>
                        <div class="metric-label">Total Cost</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{avg_tokens_per_query:.0f}</div>
                        <div class="metric-label">Avg Tokens/Query</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{len(recent_rag_metrics)}</div>
                        <div class="metric-label">Total Queries</div>
                    </div>
                </div>
            </div>
            """
        else:
            dashboard_content = f"""
            <div class="token-usage-dashboard">
                <h3>Token Usage Analytics</h3>
                <p>No recent token usage data available for the last {time_range_hours} hours.</p>
            </div>
            """

        styled_content = self._add_professional_styling(dashboard_content, "Token Usage Trends")
        return styled_content

    def _add_professional_styling(self, svg_content: str, title: str) -> str:
        """Add professional styling and interactivity to SVG."""
        styled_svg = f"""
        <div class="openfinops-llm-dashboard">
            <style>
                .openfinops-llm-dashboard {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    margin: 10px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }}
                .chart-title {{
                    color: white;
                    font-size: 16px;
                    font-weight: 600;
                    margin-bottom: 15px;
                    text-align: center;
                }}
                .chart-container {{
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 8px;
                    padding: 15px;
                    backdrop-filter: blur(10px);
                }}
                .performance-indicator {{
                    display: inline-block;
                    background: rgba(46, 213, 115, 0.2);
                    color: #1e3799;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    margin: 5px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 15px;
                    margin: 15px 0;
                }}
                .metric-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #4ECDC4;
                    margin-bottom: 5px;
                }}
                .metric-label {{
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.8);
                }}
                .progress-bar {{
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 10px;
                    height: 20px;
                    margin: 10px 0;
                    overflow: hidden;
                }}
                .progress-fill {{
                    background: linear-gradient(90deg, #4ECDC4, #44a08d);
                    height: 100%;
                    transition: width 0.3s ease;
                }}
                .health-indicator, .status-indicator {{
                    padding: 10px;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    margin: 15px 0;
                }}
                .healthy, .excellent {{
                    background: rgba(46, 213, 115, 0.2);
                    color: #2ed573;
                    border: 1px solid #2ed573;
                }}
                .warning, .good {{
                    background: rgba(255, 212, 59, 0.2);
                    color: #ffd43b;
                    border: 1px solid #ffd43b;
                }}
                .governance-section {{
                    margin: 20px 0;
                    padding: 20px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                }}
            </style>
            <div class="chart-title">{title}</div>
            <div class="chart-container">
                {svg_content}
            </div>
            <div style="text-align: center; margin-top: 10px;">
                <span class="performance-indicator">OpenFinOps Enterprise LLM Observability</span>
            </div>
        </div>
        """
        return styled_svg

    def _fallback_chart(self, title: str, width: int, height: int) -> str:
        """Fallback chart when OpenFinOps is not available."""
        return f"""
        <div style="width: {width}px; height: {height}px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 12px; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div class="chart-title" style="color: white; font-size: 18px; font-weight: 600;
                 margin-bottom: 15px; text-align: center;">{title}</div>
            <div style="background: rgba(255, 255, 255, 0.95); border-radius: 8px;
                 padding: 20px; backdrop-filter: blur(10px); height: calc(100% - 60px);">
                <div style="text-align: center; color: #4ECDC4; font-size: 16px; font-weight: 500;">
                    ✅ OpenFinOps Professional Rendering Engine<br/>
                    📊 Enterprise-Grade Visualization Ready
                </div>
            </div>
        </div>
        """


class LLMDashboardCreator:
    """
    Dashboard creator for comprehensive LLM observability.
    """

    def __init__(self, hub: LLMObservabilityHub):
        self.hub = hub
        self.visualizer = LLMObservabilityVisualizer(theme="professional")

    def create_unified_llm_dashboard(self) -> str:
        """Create unified dashboard with all LLM observability components."""

        # Get active training runs
        active_runs = list(self.hub.active_training_runs.keys())[:3]  # Show top 3
        active_pipelines = list(self.hub.active_rag_pipelines.keys())[:3]
        active_agents = list(set(m.agent_id for m in self.hub.agent_workflow_metrics
                               if time.time() - m.timestamp < 3600))[:3]

        charts = {}

        # LLM Training Charts
        for run_id in active_runs:
            charts[f"LLM Training - {run_id}"] = self.visualizer.create_llm_training_dashboard(
                self.hub, run_id
            )

        # RAG Pipeline Charts
        for pipeline_id in active_pipelines:
            charts[f"RAG Pipeline - {pipeline_id}"] = self.visualizer.create_rag_pipeline_dashboard(
                self.hub, pipeline_id
            )

        # Agent Workflow Charts
        for agent_id in active_agents:
            charts[f"Agent - {agent_id}"] = self.visualizer.create_agent_workflow_dashboard(
                self.hub, agent_id
            )

        # Enterprise Governance
        charts["Enterprise Governance"] = self.visualizer.create_enterprise_governance_dashboard(self.hub)

        # Token Usage Analytics
        charts["Token Usage Analytics"] = self.visualizer.create_token_usage_analytics(self.hub)

        # Create unified HTML dashboard
        return self._create_unified_html(charts)

    def _create_unified_html(self, charts: Dict[str, str]) -> str:
        """Create unified HTML dashboard."""
        charts_html = ""
        for title, chart_svg in charts.items():
            charts_html += f"""
            <div class="dashboard-section">
                <h2 class="section-title">{title}</h2>
                <div class="chart-wrapper">
                    {chart_svg}
                </div>
            </div>
            """

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OpenFinOps Enterprise LLM Observability Platform</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    min-height: 100vh;
                    color: #333;
                }}

                .header {{
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    padding: 20px 0;
                    text-align: center;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .header h1 {{
                    color: white;
                    font-size: 32px;
                    font-weight: 300;
                    margin-bottom: 8px;
                }}

                .header p {{
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 16px;
                }}

                .dashboard-container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 30px 20px;
                }}

                .dashboard-section {{
                    margin-bottom: 40px;
                }}

                .section-title {{
                    color: white;
                    font-size: 24px;
                    font-weight: 500;
                    margin-bottom: 20px;
                    padding-left: 10px;
                    border-left: 4px solid #4ECDC4;
                }}

                .chart-wrapper {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 20px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .footer {{
                    text-align: center;
                    padding: 30px 20px;
                    color: rgba(255, 255, 255, 0.7);
                    border-top: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .status-indicator {{
                    display: inline-block;
                    padding: 6px 12px;
                    background: rgba(46, 213, 115, 0.2);
                    border: 1px solid #2ed573;
                    border-radius: 20px;
                    color: #2ed573;
                    font-size: 14px;
                    font-weight: 500;
                    margin: 0 10px;
                }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}

                .stat-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    backdrop-filter: blur(10px);
                }}

                .stat-value {{
                    font-size: 28px;
                    font-weight: 600;
                    color: #4ECDC4;
                    margin-bottom: 8px;
                }}

                .stat-label {{
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 OpenFinOps Enterprise LLM Observability</h1>
                <p>Comprehensive AI Training, RAG, and Agent Monitoring Platform</p>
                <div style="margin-top: 15px;">
                    <span class="status-indicator">🟢 LLM Training Active</span>
                    <span class="status-indicator">🟢 RAG Pipelines Running</span>
                    <span class="status-indicator">🟢 Agents Operational</span>
                </div>
            </div>

            <div class="dashboard-container">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{len(self.hub.active_training_runs)}</div>
                        <div class="stat-label">Active Training Runs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(self.hub.active_rag_pipelines)}</div>
                        <div class="stat-label">RAG Pipelines</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(set(m.agent_id for m in self.hub.agent_workflow_metrics if time.time() - m.timestamp < 3600))}</div>
                        <div class="stat-label">Active Agents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(self.hub.active_alerts)}</div>
                        <div class="stat-label">Active Alerts</div>
                    </div>
                </div>

                {charts_html}
            </div>

            <div class="footer">
                <p>🎯 OpenFinOps Enterprise LLM Observability Platform</p>
                <p>Professional-grade monitoring for AI training, RAG building, and agent workflows</p>
                <p style="margin-top: 10px; font-size: 12px;">Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </body>
        </html>
        """

        return html_template

    def save_dashboard(self, filename: str = "llm_observability_dashboard.html"):
        """Save the unified dashboard to file."""
        dashboard_html = self.create_unified_llm_dashboard()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        return filename