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
FinOps Dashboards for LLM Observability
======================================

Comprehensive financial operations dashboards for tracking true cost of LLM operations,
training, and executions with cost optimization insights.
"""

import time
import math
from typing import Dict, Any, List, Optional
from .llm_observability import LLMObservabilityHub, LLMFinOpsMetrics, ComputeResourceCosts, CostOptimizationInsights


class LLMFinOpsDashboardCreator:
    """
    Specialized dashboard creator for FinOps and cost optimization in LLM operations.
    """

    def __init__(self):
        self.theme = "professional"

    def _create_gauge_svg(self, value: float, max_value: float, title: str, unit: str = "", color: str = "#4ECDC4") -> str:
        """Create an SVG gauge visualization."""
        percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
        angle = (percentage / 100) * 180  # Semi-circle gauge

        # Calculate the position of the needle
        needle_x = 50 + 35 * math.cos(math.radians(180 - angle))
        needle_y = 75 - 35 * math.sin(math.radians(180 - angle))

        return f"""
        <div class="gauge-container">
            <svg width="120" height="90" viewBox="0 0 100 90" class="gauge-svg">
                <!-- Gauge background -->
                <path d="M 15 75 A 35 35 0 0 1 85 75"
                      fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="8"/>

                <!-- Gauge fill -->
                <path d="M 15 75 A 35 35 0 0 1 85 75"
                      fill="none" stroke="{color}" stroke-width="8"
                      stroke-dasharray="{percentage * 1.1} 110"
                      stroke-linecap="round"/>

                <!-- Center dot -->
                <circle cx="50" cy="75" r="3" fill="#ffffff"/>

                <!-- Needle -->
                <line x1="50" y1="75" x2="{needle_x}" y2="{needle_y}"
                      stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>

                <!-- Value text -->
                <text x="50" y="50" text-anchor="middle" fill="#ffffff"
                      font-size="12" font-weight="bold">{value:.1f}{unit}</text>

                <!-- Title -->
                <text x="50" y="15" text-anchor="middle" fill="rgba(255,255,255,0.9)"
                      font-size="8" font-weight="500">{title}</text>
            </svg>
        </div>
        """

    def _create_progress_bar_svg(self, value: float, max_value: float, title: str, color: str = "#4ECDC4") -> str:
        """Create an SVG progress bar visualization."""
        percentage = min(value / max_value * 100, 100) if max_value > 0 else 0

        return f"""
        <div class="progress-container">
            <div class="progress-title">{title}</div>
            <svg width="200" height="30" class="progress-svg">
                <!-- Background bar -->
                <rect x="10" y="10" width="180" height="10"
                      fill="rgba(255,255,255,0.2)" rx="5"/>

                <!-- Progress fill -->
                <rect x="10" y="10" width="{percentage * 1.8}" height="10"
                      fill="{color}" rx="5"/>

                <!-- Percentage text -->
                <text x="100" y="28" text-anchor="middle" fill="#ffffff"
                      font-size="10" font-weight="bold">{percentage:.1f}%</text>
            </svg>
            <div class="progress-value">{value:.2f} / {max_value:.2f}</div>
        </div>
        """

    def _create_trend_chart_svg(self, values: list, title: str, color: str = "#4ECDC4") -> str:
        """Create a simple trend line chart."""
        if not values or len(values) < 2:
            values = [10, 15, 12, 18, 22, 19, 25]  # Sample data

        # Normalize values to fit in 150x60 viewbox
        max_val = max(values)
        min_val = min(values)
        height_range = max_val - min_val if max_val != min_val else 1

        points = []
        for i, val in enumerate(values):
            x = 10 + (i * 130 / (len(values) - 1))
            y = 50 - ((val - min_val) / height_range * 40)
            points.append(f"{x},{y}")

        path = "M " + " L ".join(points)

        return f"""
        <div class="trend-container">
            <div class="trend-title">{title}</div>
            <svg width="150" height="60" class="trend-svg">
                <!-- Grid lines -->
                <line x1="10" y1="10" x2="140" y2="10" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                <line x1="10" y1="30" x2="140" y2="30" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                <line x1="10" y1="50" x2="140" y2="50" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>

                <!-- Trend line -->
                <path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>

                <!-- Data points -->
                {' '.join([f'<circle cx="{10 + (i * 130 / (len(values) - 1))}" cy="{50 - ((val - min_val) / height_range * 40)}" r="2" fill="{color}"/>' for i, val in enumerate(values)])}
            </svg>
        </div>
        """

    def _wrap_dashboard(self, content: str, title: str) -> str:
        """Wrap dashboard content with enhanced visual styling."""
        return f"""<html><body>
        <div class="openfinops-llm-dashboard">
            <style>
                .openfinops-llm-dashboard {{
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    border-radius: 16px;
                    padding: 25px;
                    box-shadow: 0 25px 50px rgba(0,0,0,0.15);
                    margin: 15px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    min-height: 100vh;
                }}
                .chart-title {{
                    color: #ffffff;
                    font-size: 28px;
                    font-weight: 700;
                    margin-bottom: 25px;
                    text-align: center;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }}
                .chart-container {{
                    background: rgba(255, 255, 255, 0.98);
                    border-radius: 12px;
                    padding: 25px;
                    backdrop-filter: blur(15px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                }}
                .performance-indicator {{
                    display: inline-block;
                    background: linear-gradient(45deg, #00d2ff, #3a7bd5);
                    color: #ffffff;
                    padding: 8px 16px;
                    border-radius: 25px;
                    font-size: 13px;
                    font-weight: 600;
                    margin: 8px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                }}

                /* Enhanced Gauge Styles */
                .gauge-container {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    background: linear-gradient(145deg, #f0f2f5, #e1e5ea);
                    border-radius: 12px;
                    padding: 15px;
                    box-shadow: inset 0 2px 8px rgba(0,0,0,0.1);
                    margin: 10px;
                }}
                .gauge-svg {{
                    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
                }}

                /* Enhanced Progress Bar Styles */
                .progress-container {{
                    background: linear-gradient(145deg, #f0f2f5, #e1e5ea);
                    border-radius: 12px;
                    padding: 15px;
                    margin: 10px;
                    box-shadow: inset 0 2px 8px rgba(0,0,0,0.1);
                }}
                .progress-title {{
                    font-size: 14px;
                    font-weight: 600;
                    color: #2c3e50;
                    margin-bottom: 8px;
                    text-align: center;
                }}
                .progress-value {{
                    font-size: 12px;
                    color: #7f8c8d;
                    text-align: center;
                    margin-top: 5px;
                }}
                .progress-svg {{
                    filter: drop-shadow(0 1px 3px rgba(0,0,0,0.1));
                }}

                /* Enhanced Trend Chart Styles */
                .trend-container {{
                    background: linear-gradient(145deg, #f0f2f5, #e1e5ea);
                    border-radius: 12px;
                    padding: 15px;
                    margin: 10px;
                    box-shadow: inset 0 2px 8px rgba(0,0,0,0.1);
                }}
                .trend-title {{
                    font-size: 14px;
                    font-weight: 600;
                    color: #2c3e50;
                    margin-bottom: 8px;
                    text-align: center;
                }}
                .trend-svg {{
                    filter: drop-shadow(0 1px 3px rgba(0,0,0,0.1));
                }}

                /* Enhanced Grid and Card Styles */
                .visual-metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 25px 0;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: linear-gradient(145deg, #ffffff, #f8fafc);
                    border-radius: 16px;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid rgba(0,0,0,0.05);
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }}
                .metric-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
                }}
                .metric-value {{
                    font-size: 32px;
                    font-weight: 800;
                    color: #2c3e50;
                    margin-bottom: 8px;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.1);
                }}
                .metric-label {{
                    font-size: 14px;
                    color: #7f8c8d;
                    font-weight: 500;
                    letter-spacing: 0.5px;
                }}
                .metric-description {{
                    font-size: 12px;
                    color: #95a5a6;
                    margin-top: 8px;
                    line-height: 1.4;
                }}
                /* FinOps Dashboard Styles */
                .finops-dashboard, .cost-optimization-dashboard {{
                    color: #333;
                }}
                .cost-overview-section, .cost-breakdown-section, .resource-costs-section,
                .optimization-section, .savings-overview, .quick-wins-section, .resource-optimization-section {{
                    margin: 20px 0;
                    padding: 20px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                }}
                .resource-cost-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 15px;
                    margin: 15px 0;
                }}
                .resource-cost-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .resource-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                    font-weight: bold;
                    color: #4ECDC4;
                }}
                .resource-provider {{
                    background: rgba(78, 205, 196, 0.2);
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 10px;
                }}
                .resource-metrics {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }}
                .resource-metric {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                }}
                .optimization-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                    margin: 15px 0;
                }}
                .optimization-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .optimization-header {{
                    font-weight: bold;
                    color: #4ECDC4;
                    margin-bottom: 10px;
                }}
                .optimization-content {{
                    font-size: 14px;
                }}
                .optimization-metric {{
                    margin: 5px 0;
                    color: rgba(255, 255, 255, 0.9);
                }}
                .budget-bar {{
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 10px;
                    height: 20px;
                    margin: 10px 0;
                    overflow: hidden;
                }}
                .budget-fill {{
                    background: linear-gradient(90deg, #4ECDC4, #44a08d);
                    height: 100%;
                    transition: width 0.3s ease;
                }}
                .budget-text {{
                    text-align: center;
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.8);
                }}
                .recommendations-list {{
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }}
                .recommendation-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-left: 4px solid #4ECDC4;
                }}
                .recommendation-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                }}
                .recommendation-priority {{
                    background: rgba(78, 205, 196, 0.2);
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .recommendation-savings {{
                    color: #2ed573;
                    font-weight: bold;
                    font-size: 14px;
                }}
                .recommendation-title {{
                    font-weight: bold;
                    color: #4ECDC4;
                    margin-bottom: 5px;
                }}
                .recommendation-description {{
                    font-size: 13px;
                    color: rgba(255, 255, 255, 0.8);
                }}
                .optimization-categories {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                }}
                .optimization-category {{
                    text-align: center;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 20px;
                }}
                .optimization-category h5 {{
                    color: #4ECDC4;
                    margin-bottom: 10px;
                }}
                .metric-description {{
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.7);
                    margin-top: 5px;
                }}
                .no-data-dashboard {{
                    text-align: center;
                    padding: 40px;
                    color: #333;
                }}
                .no-data-icon {{
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
                .no-data-text {{
                    font-size: 18px;
                    margin-bottom: 10px;
                    color: #666;
                }}
                .no-data-suggestion {{
                    font-size: 14px;
                    color: #999;
                }}
                .cost-trend {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 5px;
                    margin-top: 5px;
                }}
                .trend-arrow {{
                    font-size: 16px;
                }}
                .trend-up {{ color: #ff6b6b; }}
                .trend-down {{ color: #2ed573; }}
                .trend-stable {{ color: #ffd43b; }}

                /* Enhanced Resource Card Styles */
                .resource-cost-card.enhanced {{
                    background: linear-gradient(145deg, #ffffff, #f8fafc);
                    border-radius: 16px;
                    padding: 20px;
                    border: 1px solid rgba(0,0,0,0.05);
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    margin: 15px;
                }}
                .resource-visual-section {{
                    display: flex;
                    justify-content: space-around;
                    margin: 15px 0;
                    padding: 10px;
                    background: rgba(52, 152, 219, 0.05);
                    border-radius: 12px;
                }}
                .mini-gauge-container {{
                    transform: scale(0.7);
                }}
                .resource-metric.full-width {{
                    grid-column: 1 / -1;
                    text-align: center;
                    background: rgba(241, 196, 15, 0.1);
                    padding: 8px;
                    border-radius: 6px;
                    margin-top: 10px;
                }}

                /* Enhanced Department Allocation */
                .allocation-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .allocation-card {{
                    background: linear-gradient(145deg, #ffffff, #f8fafc);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid rgba(0,0,0,0.05);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
                }}
                .allocation-header {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .allocation-amount {{
                    font-size: 24px;
                    font-weight: 800;
                    color: #3498db;
                    margin-bottom: 5px;
                }}
                .allocation-percentage {{
                    font-size: 12px;
                    color: #7f8c8d;
                    margin-bottom: 10px;
                }}
                .allocation-bar {{
                    background: rgba(52, 152, 219, 0.2);
                    border-radius: 10px;
                    height: 8px;
                    overflow: hidden;
                }}
                .allocation-fill {{
                    background: linear-gradient(90deg, #3498db, #2980b9);
                    height: 100%;
                    transition: width 0.3s ease;
                }}

                /* Enhanced Forecasting */
                .forecasting-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .forecast-card {{
                    background: linear-gradient(145deg, #ffffff, #f8fafc);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid rgba(0,0,0,0.05);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
                }}
                .forecast-header {{
                    font-size: 14px;
                    font-weight: 600;
                    color: #7f8c8d;
                    margin-bottom: 8px;
                }}
                .forecast-trend {{
                    font-size: 20px;
                    font-weight: 700;
                    color: #2c3e50;
                    margin-bottom: 8px;
                }}
                .forecast-description {{
                    font-size: 12px;
                    color: #95a5a6;
                    line-height: 1.4;
                }}

                /* Enhanced Alert Cards */
                .alerts-grid {{
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 15px;
                    margin: 20px 0;
                }}
                .alert-card {{
                    background: linear-gradient(145deg, #ffffff, #f8fafc);
                    border-radius: 12px;
                    padding: 20px;
                    border: 1px solid rgba(0,0,0,0.05);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
                }}
                .alert-header {{
                    font-size: 16px;
                    font-weight: 600;
                    margin-bottom: 10px;
                }}
                .alert-content {{
                    font-size: 14px;
                }}
                .alert-metric {{
                    margin: 8px 0;
                    font-weight: 500;
                }}
                .alert-description {{
                    font-size: 12px;
                    color: #7f8c8d;
                    margin-top: 8px;
                    line-height: 1.4;
                }}
            </style>
            <div class="chart-title">{title}</div>
            <div class="chart-container">
                {content}
            </div>
            <div style="text-align: center; margin-top: 10px;">
                <span class="performance-indicator">OpenFinOps Enterprise FinOps</span>
            </div>
        </div>
        </body></html>
        """

    def create_finops_dashboard(self, hub: LLMObservabilityHub, organization_id: str) -> str:
        """Create comprehensive FinOps dashboard for LLM operations."""
        cost_summary = hub.get_cost_summary(organization_id)

        if 'error' in cost_summary:
            return self._create_no_data_dashboard("FinOps Dashboard", "No cost data available")

        # Get recent FinOps metrics
        recent_finops = [m for m in hub.finops_metrics
                        if m.organization_id == organization_id][-10:]  # Last 10 entries

        recent_compute_costs = list(hub.compute_cost_metrics)[-10:]

        # Create visual gauges for key metrics
        total_cost_gauge = self._create_gauge_svg(
            cost_summary['total_cost'], 50000, "Total Spend", "$", "#e74c3c"
        )
        efficiency_gauge = self._create_gauge_svg(
            cost_summary['efficiency_score'] * 100, 100, "Cost Efficiency", "%", "#27ae60"
        )
        waste_progress = self._create_progress_bar_svg(
            cost_summary['waste_cost'], cost_summary['total_cost'], "Waste vs Total Cost", "#f39c12"
        )
        optimization_chart = self._create_trend_chart_svg(
            [2500, 3200, 2800, 3600, 3621], "Cost Trend (Last 5 Months)", "#3498db"
        )

        dashboard_content = f"""
        <div class="finops-dashboard">
            <h3>💰 FinOps Dashboard - {organization_id}</h3>

            <!-- Visual Cost Overview -->
            <div class="cost-overview-section">
                <h4>💸 True Cost of LLM Operations - Visual Overview</h4>
                <div class="visual-metrics-grid">
                    {total_cost_gauge}
                    {efficiency_gauge}
                    {waste_progress}
                    {optimization_chart}
                </div>

                <!-- Detailed Digital Metrics -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">${cost_summary['total_cost']:,.2f}</div>
                        <div class="metric-label">Total Spend</div>
                        <div class="cost-trend">
                            <span class="trend-arrow trend-up">↑</span>
                            <span style="font-size: 12px;">+15% vs last month</span>
                        </div>
                        <div class="metric-description">
                            Comprehensive cost including compute, infrastructure, and operational expenses
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${cost_summary['waste_cost']:,.2f}</div>
                        <div class="metric-label">Waste Cost</div>
                        <div class="cost-trend">
                            <span class="trend-arrow trend-down">↓</span>
                            <span style="font-size: 12px;">-5% waste reduction</span>
                        </div>
                        <div class="metric-description">
                            Idle resources, oversized instances, and inefficient utilization
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{cost_summary['efficiency_score']:.1%}</div>
                        <div class="metric-label">Cost Efficiency</div>
                        <div class="cost-trend">
                            <span class="trend-arrow trend-up">↑</span>
                            <span style="font-size: 12px;">Improving</span>
                        </div>
                        <div class="metric-description">
                            Ratio of productive costs to total spend
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${cost_summary['optimization_potential']:,.2f}</div>
                        <div class="metric-label">Optimization Potential</div>
                        <div class="cost-trend">
                            <span class="trend-arrow trend-stable">→</span>
                            <span style="font-size: 12px;">Available savings</span>
                        </div>
                        <div class="metric-description">
                            Immediate cost reduction opportunities identified
                        </div>
                    </div>
                </div>
            </div>

            <!-- Cost Breakdown -->
            <div class="cost-breakdown-section">
                <h4>📊 Cost Breakdown by Operation Type</h4>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">${cost_summary['cost_breakdown']['training']:,.2f}</div>
                        <div class="metric-label">Training Costs</div>
                        <div class="metric-description">GPU-intensive model training operations</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${cost_summary['cost_breakdown']['inference']:,.2f}</div>
                        <div class="metric-label">Inference Costs</div>
                        <div class="metric-description">Real-time model serving and API calls</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${cost_summary['cost_breakdown']['fine_tuning']:,.2f}</div>
                        <div class="metric-label">Fine-tuning Costs</div>
                        <div class="metric-description">Custom model adaptation and optimization</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${cost_summary['carbon_cost']:,.2f}</div>
                        <div class="metric-label">Carbon Cost</div>
                        <div class="metric-description">Environmental impact and sustainability fees</div>
                    </div>
                </div>
            </div>

            <!-- Real-time Resource Costs -->
            <div class="resource-costs-section">
                <h4>⚡ Real-time Compute Resource Costs</h4>
                <div class="resource-cost-grid">
        """

        # Add recent compute resource costs with visual elements
        for resource in recent_compute_costs[:4]:  # Show top 4 resources with visuals
            efficiency_color = "#27ae60" if resource.cost_efficiency_score > 0.8 else "#f39c12" if resource.cost_efficiency_score > 0.6 else "#e74c3c"

            # Create mini gauges for each resource
            utilization_gauge = self._create_gauge_svg(
                resource.utilization_percentage, 100, "Utilization", "%", efficiency_color
            )
            efficiency_gauge = self._create_gauge_svg(
                resource.cost_efficiency_score * 100, 100, "Efficiency", "%", efficiency_color
            )
            dashboard_content += f"""
                    <div class="resource-cost-card enhanced">
                        <div class="resource-header">
                            <strong>{resource.resource_type.upper()} - {resource.instance_type}</strong>
                            <span class="resource-provider">{resource.provider.upper()}</span>
                        </div>

                        <!-- Visual Gauges -->
                        <div class="resource-visual-section">
                            <div class="mini-gauge-container">
                                {utilization_gauge}
                            </div>
                            <div class="mini-gauge-container">
                                {efficiency_gauge}
                            </div>
                        </div>

                        <!-- Detailed Metrics -->
                        <div class="resource-metrics">
                            <div class="resource-metric">
                                <span class="metric-label">Current Cost/Hour</span>
                                <span class="metric-value">${resource.current_hourly_cost:.3f}</span>
                            </div>
                            <div class="resource-metric">
                                <span class="metric-label">Estimated Daily</span>
                                <span class="metric-value">${resource.estimated_daily_cost:.2f}</span>
                            </div>
                            <div class="resource-metric">
                                <span class="metric-label">Waste Cost</span>
                                <span class="metric-value" style="color: #e74c3c">${resource.waste_cost:.2f}</span>
                            </div>
                            <div class="resource-metric full-width">
                                <span class="metric-label">Optimization</span>
                                <span class="metric-value" style="font-size: 11px;">{resource.optimization_recommendation[:45]}...</span>
                            </div>
                        </div>
                    </div>
            """

        # Add cost optimization recommendations
        if recent_finops:
            latest_finops = recent_finops[-1]
            dashboard_content += f"""
            </div>
            </div>

            <!-- Cost Optimization Insights -->
            <div class="optimization-section">
                <h4>🎯 Cost Optimization Insights</h4>
                <div class="optimization-grid">
                    <div class="optimization-card">
                        <div class="optimization-header">💡 Quick Wins</div>
                        <div class="optimization-content">
                            <div class="optimization-metric">
                                <span>Waste Reduction: {latest_finops.waste_percentage:.1f}%</span>
                            </div>
                            <div class="optimization-metric">
                                <span>Efficiency Target: {latest_finops.efficiency_score:.1%}</span>
                            </div>
                            <div class="optimization-metric">
                                <span>Cost per Token: ${latest_finops.cost_per_token:.6f}</span>
                            </div>
                            <div class="optimization-recommendation">
                                Consider spot instances for training workloads - potential 60% savings
                            </div>
                        </div>
                    </div>

                    <div class="optimization-card">
                        <div class="optimization-header">📈 Budget Status</div>
                        <div class="optimization-content">
                            <div class="budget-bar">
                                <div class="budget-fill" style="width: {(latest_finops.budget_consumed/latest_finops.budget_allocated)*100:.1f}%"></div>
                            </div>
                            <div class="budget-text">
                                ${latest_finops.budget_consumed:,.0f} / ${latest_finops.budget_allocated:,.0f}
                                ({(latest_finops.budget_consumed/latest_finops.budget_allocated)*100:.1f}%)
                            </div>
                            <div class="optimization-metric">
                                <span>Projected Monthly: ${latest_finops.projected_monthly_cost:,.0f}</span>
                            </div>
                            <div class="optimization-metric">
                                <span>Budget Remaining: ${latest_finops.budget_remaining:,.0f}</span>
                            </div>
                        </div>
                    </div>

                    <div class="optimization-card">
                        <div class="optimization-header">🌱 Sustainability</div>
                        <div class="optimization-content">
                            <div class="optimization-metric">
                                <span>Carbon Cost: ${latest_finops.carbon_cost_usd:.2f}</span>
                            </div>
                            <div class="optimization-metric">
                                <span>Green Premium: ${latest_finops.green_compute_premium:.2f}</span>
                            </div>
                            <div class="optimization-metric">
                                <span>Sustainability Penalty: ${latest_finops.sustainability_penalty:.2f}</span>
                            </div>
                            <div class="optimization-recommendation">
                                Switch to renewable energy regions for 15% carbon cost reduction
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        else:
            dashboard_content += """
            </div>
            </div>
        </div>
        """

        return self._wrap_dashboard(dashboard_content, "FinOps Dashboard - True Cost of LLM Operations")

    def create_cost_optimization_dashboard(self, hub: LLMObservabilityHub) -> str:
        """Create dashboard focused on cost optimization recommendations."""

        if not hub.cost_optimization_insights:
            return self._create_no_data_dashboard("Cost Optimization", "No optimization insights available")

        latest_insights = list(hub.cost_optimization_insights)[-1]

        dashboard_content = f"""
        <div class="cost-optimization-dashboard">
            <h3>🎯 Cost Optimization Recommendations</h3>

            <!-- Savings Overview -->
            <div class="savings-overview">
                <h4>💰 Potential Savings Overview</h4>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">${latest_insights.potential_savings:,.2f}</div>
                        <div class="metric-label">Total Potential Savings</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{latest_insights.savings_percentage:.1%}</div>
                        <div class="metric-label">Savings Percentage</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{latest_insights.confidence_score:.1%}</div>
                        <div class="metric-label">Confidence Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{latest_insights.implementation_risk}</div>
                        <div class="metric-label">Implementation Risk</div>
                    </div>
                </div>
            </div>

            <!-- Quick Wins -->
            <div class="quick-wins-section">
                <h4>⚡ Quick Wins (&lt;1 Week Implementation)</h4>
                <div class="recommendations-list">
        """

        # Sample recommendations if none exist
        sample_recommendations = [
            {'title': 'Implement Spot Instance Training', 'description': 'Use spot instances for non-critical training workloads to reduce costs by 60-90%', 'estimated_savings': 15000},
            {'title': 'Optimize Model Quantization', 'description': 'Apply INT8 quantization to reduce memory requirements and inference costs by 30%', 'estimated_savings': 8500},
            {'title': 'Auto-shutdown Idle Resources', 'description': 'Implement automated resource shutdown for idle periods longer than 30 minutes', 'estimated_savings': 5200},
            {'title': 'Regional Cost Optimization', 'description': 'Migrate non-latency sensitive workloads to lower-cost regions', 'estimated_savings': 3800},
            {'title': 'Reserved Instance Planning', 'description': 'Purchase reserved instances for predictable long-term workloads', 'estimated_savings': 12000}
        ]

        recommendations = latest_insights.quick_wins if latest_insights.quick_wins else sample_recommendations

        for i, recommendation in enumerate(recommendations[:5]):
            dashboard_content += f"""
                    <div class="recommendation-card">
                        <div class="recommendation-header">
                            <span class="recommendation-priority">High Priority #{i+1}</span>
                            <span class="recommendation-savings">💰 ${recommendation.get('estimated_savings', 0):,.0f}/month</span>
                        </div>
                        <div class="recommendation-title">{recommendation.get('title', 'Resource Optimization')}</div>
                        <div class="recommendation-description">{recommendation.get('description', 'Optimize resource allocation for better cost efficiency')}</div>
                    </div>
            """

        dashboard_content += f"""
                </div>
            </div>

            <!-- Resource Optimization -->
            <div class="resource-optimization-section">
                <h4>🔧 Resource Optimization Opportunities</h4>
                <div class="optimization-categories">
                    <div class="optimization-category">
                        <h5>📉 Model Optimization</h5>
                        <div class="metric-value">${latest_insights.model_compression_savings:,.0f}</div>
                        <div class="metric-description">Potential savings from model compression, quantization, and distillation</div>
                    </div>

                    <div class="optimization-category">
                        <h5>⏰ Scheduling Optimization</h5>
                        <div class="metric-value">${latest_insights.non_peak_hour_savings:,.0f}</div>
                        <div class="metric-description">Savings from off-peak hour scheduling and workload distribution</div>
                    </div>

                    <div class="optimization-category">
                        <h5>🤖 Automation Savings</h5>
                        <div class="metric-value">${latest_insights.automated_shutdown_savings:,.0f}</div>
                        <div class="metric-description">Automated resource shutdown and intelligent scaling</div>
                    </div>

                    <div class="optimization-category">
                        <h5>📊 Data Transfer Optimization</h5>
                        <div class="metric-value">${latest_insights.data_transfer_optimization:,.0f}</div>
                        <div class="metric-description">Optimize data movement and reduce network costs</div>
                    </div>
                </div>
            </div>
        </div>
        """

        return self._wrap_dashboard(dashboard_content, "Cost Optimization Dashboard")

    def create_budget_management_dashboard(self, hub: LLMObservabilityHub, organization_id: str) -> str:
        """Create budget management and forecasting dashboard."""

        recent_finops = [m for m in hub.finops_metrics
                        if m.organization_id == organization_id][-30:]  # Last 30 entries

        if not recent_finops:
            return self._create_no_data_dashboard("Budget Management", "No budget data available")

        latest_finops = recent_finops[-1]
        total_allocated = sum(m.budget_allocated for m in recent_finops) / len(recent_finops)
        total_consumed = sum(m.budget_consumed for m in recent_finops)

        # Create visual budget representations
        budget_utilization = (latest_finops.budget_consumed / latest_finops.budget_allocated) * 100
        budget_gauge = self._create_gauge_svg(
            budget_utilization, 100, "Budget Utilization", "%",
            "#e74c3c" if budget_utilization > 90 else "#f39c12" if budget_utilization > 75 else "#27ae60"
        )

        spending_trend = self._create_trend_chart_svg(
            [28000, 32000, 29500, 31000, 28500], "Monthly Spending Trend", "#3498db"
        )

        forecast_progress = self._create_progress_bar_svg(
            latest_finops.projected_monthly_cost, latest_finops.budget_allocated,
            "Projected vs Allocated", "#9b59b6"
        )

        burn_rate_gauge = self._create_gauge_svg(
            (total_consumed/30), 2000, "Daily Burn Rate", "$/day", "#e67e22"
        )

        dashboard_content = f"""
        <div class="budget-management-dashboard">
            <h3>📊 Budget Management & Forecasting - {organization_id}</h3>

            <!-- Visual Budget Overview -->
            <div class="budget-overview-section">
                <h4>💳 Budget Overview - Visual Monitoring</h4>
                <div class="visual-metrics-grid">
                    {budget_gauge}
                    {spending_trend}
                    {forecast_progress}
                    {burn_rate_gauge}
                </div>

                <!-- Detailed Digital Metrics -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">${total_allocated:,.0f}</div>
                        <div class="metric-label">Monthly Budget</div>
                        <div class="metric-description">
                            Total allocated budget for LLM operations this month
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${total_consumed:,.0f}</div>
                        <div class="metric-label">Consumed to Date</div>
                        <div class="metric-description">
                            Total spend accumulated in current budget period
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${latest_finops.budget_remaining:,.0f}</div>
                        <div class="metric-label">Remaining Budget</div>
                        <div class="metric-description">
                            Available budget for remaining period
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${latest_finops.projected_monthly_cost:,.0f}</div>
                        <div class="metric-label">Projected Monthly Cost</div>
                        <div class="metric-description">
                            Forecasted total monthly cost based on current trends
                        </div>
                    </div>
                </div>
            </div>

            <!-- Budget Allocation by Department -->
            <div class="budget-allocation-section">
                <h4>🏢 Budget Allocation by Department</h4>
                <div class="allocation-grid">
        """

        # Sample department allocation
        for dept, amount in latest_finops.department_allocation.items():
            percentage = (amount / total_allocated) * 100 if total_allocated > 0 else 0
            dashboard_content += f"""
                    <div class="allocation-card">
                        <div class="allocation-header">{dept.title()}</div>
                        <div class="allocation-amount">${amount:,.0f}</div>
                        <div class="allocation-percentage">{percentage:.1f}% of total budget</div>
                        <div class="allocation-bar">
                            <div class="allocation-fill" style="width: {percentage:.1f}%"></div>
                        </div>
                    </div>
            """

        dashboard_content += f"""
                </div>
            </div>

            <!-- Cost Forecasting -->
            <div class="forecasting-section">
                <h4>📈 Cost Forecasting & Trends</h4>
                <div class="forecasting-grid">
                    <div class="forecast-card">
                        <div class="forecast-header">Current Trend</div>
                        <div class="forecast-trend">{latest_finops.cost_trend.title()}</div>
                        <div class="forecast-description">
                            Based on last 30 days of usage patterns
                        </div>
                    </div>

                    <div class="forecast-card">
                        <div class="forecast-header">Budget Burn Rate</div>
                        <div class="forecast-trend">${(total_consumed/30):,.0f}/day</div>
                        <div class="forecast-description">
                            Average daily spend rate
                        </div>
                    </div>

                    <div class="forecast-card">
                        <div class="forecast-header">Days Until Budget Exhausted</div>
                        <div class="forecast-trend">{int(latest_finops.budget_remaining / (total_consumed/30)) if total_consumed > 0 else 'N/A'} days</div>
                        <div class="forecast-description">
                            At current burn rate
                        </div>
                    </div>
                </div>
            </div>

            <!-- Budget Alerts -->
            <div class="budget-alerts-section">
                <h4>🚨 Budget Alerts & Thresholds</h4>
                <div class="alerts-grid">
        """

        # Budget alert status
        budget_utilization = (latest_finops.budget_consumed / latest_finops.budget_allocated) * 100

        if budget_utilization > 90:
            alert_status = "CRITICAL"
            alert_color = "#ff6b6b"
        elif budget_utilization > 75:
            alert_status = "WARNING"
            alert_color = "#ffd43b"
        else:
            alert_status = "HEALTHY"
            alert_color = "#2ed573"

        dashboard_content += f"""
                    <div class="alert-card" style="border-left: 4px solid {alert_color}">
                        <div class="alert-header">Budget Status: {alert_status}</div>
                        <div class="alert-content">
                            <div class="alert-metric">Utilization: {budget_utilization:.1f}%</div>
                            <div class="alert-description">
                                {'Budget nearly exhausted - immediate action required' if alert_status == 'CRITICAL'
                                 else 'Budget utilization high - monitor closely' if alert_status == 'WARNING'
                                 else 'Budget utilization within normal range'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

        return self._wrap_dashboard(dashboard_content, "Budget Management & Forecasting Dashboard")

    def _create_no_data_dashboard(self, title: str, message: str) -> str:
        """Create a dashboard when no data is available."""
        content = f"""
        <div class="no-data-dashboard">
            <div class="no-data-icon">📊</div>
            <div class="no-data-text">{message}</div>
            <div class="no-data-suggestion">Start collecting FinOps metrics to see cost insights here.</div>
        </div>
        """
        return self._wrap_dashboard(content, title)

    def generate_all_finops_dashboards(self, hub: LLMObservabilityHub, organization_id: str = "enterprise-001") -> List[str]:
        """Generate all FinOps dashboards and save to files."""
        dashboards = []

        # Generate all dashboard types
        finops_dashboard = self.create_finops_dashboard(hub, organization_id)
        cost_optimization_dashboard = self.create_cost_optimization_dashboard(hub)
        budget_management_dashboard = self.create_budget_management_dashboard(hub, organization_id)

        # Save to files
        dashboard_files = [
            ("finops_main_dashboard.html", finops_dashboard),
            ("cost_optimization_dashboard.html", cost_optimization_dashboard),
            ("budget_management_dashboard.html", budget_management_dashboard)
        ]

        for filename, content in dashboard_files:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            dashboards.append(filename)

        return dashboards