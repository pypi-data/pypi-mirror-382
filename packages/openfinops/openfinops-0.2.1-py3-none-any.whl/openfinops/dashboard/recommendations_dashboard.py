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
Recommendations Dashboard
=========================

Interactive dashboard for viewing and acting on intelligent recommendations.
Displays hardware, scaling, and cost optimization recommendations powered by AI/LLM.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from ..observability.intelligent_recommendations import (
    IntelligentRecommendationsCoordinator,
    IntelligentRecommendation
)
from ..observability.llm_config import LLMConfig, LLMProvider


class RecommendationsDashboard:
    """Dashboard for intelligent recommendations."""

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """Initialize recommendations dashboard."""
        self.logger = logging.getLogger(__name__)
        self.coordinator = IntelligentRecommendationsCoordinator(llm_config)
        self.active_recommendations = []

    def get_dashboard_data(
        self,
        current_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
        workload_type: str = "inference",
        cloud_provider: str = "aws"
    ) -> Dict[str, Any]:
        """Get complete dashboard data."""

        # Get all recommendations
        recommendations = self.coordinator.get_all_recommendations(
            current_metrics,
            historical_data,
            workload_type,
            cloud_provider
        )

        self.active_recommendations = recommendations

        # Calculate statistics
        total_potential_savings = sum(
            -rec.impact.get('cost_monthly_usd', 0)
            for rec in recommendations
            if rec.impact.get('cost_monthly_usd', 0) < 0
        )

        critical_count = sum(1 for rec in recommendations if rec.priority == 'critical')
        high_count = sum(1 for rec in recommendations if rec.priority == 'high')

        # Group by type
        by_type = {}
        for rec in recommendations:
            if rec.type not in by_type:
                by_type[rec.type] = []
            by_type[rec.type].append(rec)

        return {
            'summary': {
                'total_recommendations': len(recommendations),
                'critical_count': critical_count,
                'high_priority_count': high_count,
                'potential_monthly_savings': total_potential_savings,
                'llm_provider': self.coordinator.llm_engine.config.provider.value,
                'llm_model': self.coordinator.llm_engine.config.model_name
            },
            'recommendations': [rec.to_dict() for rec in recommendations],
            'by_type': {
                type_name: [rec.to_dict() for rec in recs]
                for type_name, recs in by_type.items()
            },
            'quick_wins': self._get_quick_wins(recommendations),
            'high_impact': self._get_high_impact(recommendations),
            'generated_at': datetime.now().isoformat()
        }

    def get_hardware_recommendations_view(
        self,
        current_metrics: Dict[str, Any],
        workload_type: str = "inference",
        cloud_provider: str = "aws"
    ) -> Dict[str, Any]:
        """Get hardware-specific recommendations view."""

        recommendations = self.coordinator.get_hardware_recommendations(
            current_metrics,
            workload_type,
            cloud_provider
        )

        return {
            'title': 'Hardware Optimization Recommendations',
            'count': len(recommendations),
            'recommendations': [rec.to_dict() for rec in recommendations],
            'gpu_recommendations': [
                rec.to_dict() for rec in recommendations
                if 'gpu' in rec.description.lower()
            ],
            'cpu_recommendations': [
                rec.to_dict() for rec in recommendations
                if 'cpu' in rec.description.lower() or 'vcpu' in rec.description.lower()
            ],
            'memory_recommendations': [
                rec.to_dict() for rec in recommendations
                if 'memory' in rec.description.lower()
            ]
        }

    def get_scaling_recommendations_view(
        self,
        current_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Get scaling-specific recommendations view."""

        recommendations = self.coordinator.get_scaling_recommendations(
            current_metrics,
            historical_data
        )

        return {
            'title': 'Scaling Strategy Recommendations',
            'count': len(recommendations),
            'recommendations': [rec.to_dict() for rec in recommendations],
            'autoscaling_recommendations': [
                rec.to_dict() for rec in recommendations
                if 'auto' in rec.description.lower() or 'scaling' in rec.type.lower()
            ],
            'spot_instance_opportunities': [
                rec.to_dict() for rec in recommendations
                if 'spot' in rec.description.lower() or 'preemptible' in rec.description.lower()
            ]
        }

    def get_cost_optimization_view(
        self,
        recommendations: Optional[List[IntelligentRecommendation]] = None
    ) -> Dict[str, Any]:
        """Get cost optimization focused view."""

        if recommendations is None:
            recommendations = self.active_recommendations

        # Filter for cost-saving recommendations
        cost_saving_recs = [
            rec for rec in recommendations
            if rec.impact.get('cost_monthly_usd', 0) < 0
        ]

        # Sort by potential savings (highest first)
        cost_saving_recs.sort(
            key=lambda x: x.impact.get('cost_monthly_usd', 0)
        )

        total_savings = sum(
            -rec.impact.get('cost_monthly_usd', 0)
            for rec in cost_saving_recs
        )

        return {
            'title': 'Cost Optimization Opportunities',
            'total_potential_savings_monthly': total_savings,
            'total_potential_savings_annual': total_savings * 12,
            'recommendations_count': len(cost_saving_recs),
            'recommendations': [rec.to_dict() for rec in cost_saving_recs],
            'top_savings_opportunity': cost_saving_recs[0].to_dict() if cost_saving_recs else None
        }

    def _get_quick_wins(
        self,
        recommendations: List[IntelligentRecommendation]
    ) -> List[Dict[str, Any]]:
        """Get quick win recommendations (low effort, high impact)."""

        quick_wins = [
            rec for rec in recommendations
            if rec.implementation.get('complexity', '').lower() in ['low', 'medium']
            and rec.priority in ['high', 'critical']
        ]

        # Sort by confidence and priority
        quick_wins.sort(
            key=lambda x: (
                {'critical': 0, 'high': 1}.get(x.priority, 2),
                -x.confidence_score
            )
        )

        return [rec.to_dict() for rec in quick_wins[:5]]  # Top 5

    def _get_high_impact(
        self,
        recommendations: List[IntelligentRecommendation]
    ) -> List[Dict[str, Any]]:
        """Get high impact recommendations."""

        high_impact = [
            rec for rec in recommendations
            if rec.priority in ['critical', 'high']
            and abs(rec.impact.get('cost_monthly_usd', 0)) > 500  # Significant cost impact
        ]

        high_impact.sort(
            key=lambda x: abs(x.impact.get('cost_monthly_usd', 0)),
            reverse=True
        )

        return [rec.to_dict() for rec in high_impact[:5]]  # Top 5

    def export_recommendations_report(
        self,
        format: str = 'markdown',
        recommendations: Optional[List[IntelligentRecommendation]] = None
    ) -> str:
        """Export recommendations as report."""

        if recommendations is None:
            recommendations = self.active_recommendations

        return self.coordinator.export_recommendations(recommendations, format)

    def get_llm_config_info(self) -> Dict[str, Any]:
        """Get information about current LLM configuration."""

        config = self.coordinator.llm_engine.config

        return {
            'provider': config.provider.value,
            'model_name': config.model_name,
            'is_llm_enabled': config.provider != LLMProvider.RULE_BASED,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens,
            'track_api_costs': config.track_api_costs,
            'max_monthly_cost': config.max_monthly_cost
        }

    def update_llm_config(self, new_config: LLMConfig):
        """Update LLM configuration."""

        self.coordinator = IntelligentRecommendationsCoordinator(new_config)
        self.logger.info(f"Updated LLM config to provider: {new_config.provider.value}")

    def get_recommendation_by_id(self, rec_id: str) -> Optional[Dict[str, Any]]:
        """Get specific recommendation by ID."""

        for rec in self.active_recommendations:
            if rec.id == rec_id:
                return rec.to_dict()
        return None

    def mark_recommendation_implemented(self, rec_id: str) -> bool:
        """Mark recommendation as implemented."""

        for rec in self.active_recommendations:
            if rec.id == rec_id:
                # In a real implementation, this would update a database
                self.logger.info(f"Recommendation {rec_id} marked as implemented")
                return True
        return False

    def get_implementation_status(self) -> Dict[str, Any]:
        """Get implementation status of recommendations."""

        # This is a simplified version
        # In production, track actual implementation status
        return {
            'total_recommendations': len(self.active_recommendations),
            'implemented': 0,
            'in_progress': 0,
            'pending': len(self.active_recommendations),
            'dismissed': 0
        }


# Example usage functions for dashboards
def create_recommendations_widget(
    current_metrics: Dict[str, Any],
    historical_data: Optional[List[Dict[str, Any]]] = None,
    llm_config: Optional[LLMConfig] = None
) -> Dict[str, Any]:
    """
    Create a recommendations widget for embedding in dashboards.

    Returns widget data that can be rendered in any dashboard.
    """

    dashboard = RecommendationsDashboard(llm_config)
    data = dashboard.get_dashboard_data(current_metrics, historical_data)

    # Format for widget display
    widget_data = {
        'type': 'recommendations_widget',
        'summary': {
            'total': data['summary']['total_recommendations'],
            'critical': data['summary']['critical_count'],
            'savings': f"${data['summary']['potential_monthly_savings']:.2f}/mo",
            'llm_enabled': data['summary']['llm_provider'] != 'rule_based'
        },
        'top_recommendations': data['recommendations'][:3],  # Top 3
        'quick_wins': data['quick_wins'],
        'view_all_link': '/dashboard/recommendations'
    }

    return widget_data
