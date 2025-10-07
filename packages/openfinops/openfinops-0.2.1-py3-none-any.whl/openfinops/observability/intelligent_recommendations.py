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
Intelligent Recommendations Coordinator
========================================

Unified interface for hardware and scaling recommendations powered by configurable LLMs.
Coordinates:
- LLM-powered intelligent analysis
- Hardware optimization recommendations
- Scaling strategy recommendations
- Cost optimization suggestions
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from .llm_config import LLMRecommendationEngine, LLMConfig, get_llm_config
from .hardware_recommendations import HardwareRecommendationEngine, WorkloadType
from .scaling_recommendations import ScalingRecommendationEngine


@dataclass
class IntelligentRecommendation:
    """Unified recommendation from all sources."""
    id: str
    type: str  # 'hardware', 'scaling', 'cost', 'performance'
    category: str
    title: str
    description: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    impact: Dict[str, Any]  # cost, performance, etc.
    implementation: Dict[str, Any]
    confidence_score: float
    source: str  # 'llm', 'rule_based', 'hardware_engine', 'scaling_engine'
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            'created_at': self.created_at.isoformat()
        }


class IntelligentRecommendationsCoordinator:
    """Coordinates all recommendation engines with LLM support."""

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """Initialize with optional LLM configuration."""
        self.logger = logging.getLogger(__name__)

        # Initialize engines
        self.llm_engine = LLMRecommendationEngine(llm_config or get_llm_config())
        self.hardware_engine = HardwareRecommendationEngine()
        self.scaling_engine = ScalingRecommendationEngine()

        self.logger.info(f"Initialized recommendations with LLM provider: {self.llm_engine.config.provider.value}")

    def get_all_recommendations(
        self,
        current_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
        workload_type: str = "inference",
        cloud_provider: str = "aws",
        use_llm: bool = True
    ) -> List[IntelligentRecommendation]:
        """Get comprehensive recommendations from all engines."""

        all_recommendations = []

        # 1. Hardware Recommendations
        try:
            workload_type_enum = WorkloadType[workload_type.upper()] if isinstance(workload_type, str) else workload_type
            hardware_recs = self.hardware_engine.analyze_workload(
                current_metrics,
                workload_type_enum,
                cloud_provider
            )

            for rec in hardware_recs:
                # Enhance with LLM if enabled
                if use_llm and self.llm_engine.config.provider.value != 'rule_based':
                    llm_enhancement = self._enhance_with_llm(rec.to_dict(), 'hardware')
                    unified_rec = self._create_unified_recommendation(
                        rec.to_dict(),
                        'hardware',
                        llm_enhancement,
                        source='llm_enhanced'
                    )
                else:
                    unified_rec = self._create_unified_recommendation(
                        rec.to_dict(),
                        'hardware',
                        source='hardware_engine'
                    )
                all_recommendations.append(unified_rec)

        except Exception as e:
            self.logger.error(f"Hardware recommendations failed: {e}")

        # 2. Scaling Recommendations
        try:
            scaling_recs = self.scaling_engine.analyze_scaling_needs(
                current_metrics,
                historical_data
            )

            for rec in scaling_recs:
                if use_llm and self.llm_engine.config.provider.value != 'rule_based':
                    llm_enhancement = self._enhance_with_llm(rec.to_dict(), 'scaling')
                    unified_rec = self._create_unified_recommendation(
                        rec.to_dict(),
                        'scaling',
                        llm_enhancement,
                        source='llm_enhanced'
                    )
                else:
                    unified_rec = self._create_unified_recommendation(
                        rec.to_dict(),
                        'scaling',
                        source='scaling_engine'
                    )
                all_recommendations.append(unified_rec)

        except Exception as e:
            self.logger.error(f"Scaling recommendations failed: {e}")

        # 3. Pure LLM Recommendations (if enabled)
        if use_llm and self.llm_engine.config.provider.value != 'rule_based':
            try:
                llm_rec = self.llm_engine.generate_recommendation(
                    context={
                        'current_metrics': current_metrics,
                        'workload_type': workload_type,
                        'cloud_provider': cloud_provider
                    },
                    recommendation_type='optimization'
                )

                unified_rec = self._create_unified_recommendation(
                    llm_rec,
                    'optimization',
                    source='llm'
                )
                all_recommendations.append(unified_rec)

            except Exception as e:
                self.logger.error(f"LLM recommendations failed: {e}")

        # Sort by priority and confidence
        all_recommendations.sort(
            key=lambda x: (
                {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.priority, 4),
                -x.confidence_score
            )
        )

        return all_recommendations

    def get_hardware_recommendations(
        self,
        current_metrics: Dict[str, Any],
        workload_type: str = "inference",
        cloud_provider: str = "aws"
    ) -> List[IntelligentRecommendation]:
        """Get hardware-specific recommendations."""

        workload_type_enum = WorkloadType[workload_type.upper()]
        hardware_recs = self.hardware_engine.analyze_workload(
            current_metrics,
            workload_type_enum,
            cloud_provider
        )

        return [
            self._create_unified_recommendation(rec.to_dict(), 'hardware', source='hardware_engine')
            for rec in hardware_recs
        ]

    def get_scaling_recommendations(
        self,
        current_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[IntelligentRecommendation]:
        """Get scaling-specific recommendations."""

        scaling_recs = self.scaling_engine.analyze_scaling_needs(
            current_metrics,
            historical_data
        )

        return [
            self._create_unified_recommendation(rec.to_dict(), 'scaling', source='scaling_engine')
            for rec in scaling_recs
        ]

    def get_llm_recommendation(
        self,
        context: Dict[str, Any],
        recommendation_type: str = 'general'
    ) -> Optional[IntelligentRecommendation]:
        """Get LLM-powered recommendation."""

        if self.llm_engine.config.provider.value == 'rule_based':
            self.logger.info("LLM not configured. Using rule-based recommendations.")
            return None

        try:
            llm_rec = self.llm_engine.generate_recommendation(
                context,
                recommendation_type
            )

            return self._create_unified_recommendation(
                llm_rec,
                recommendation_type,
                source='llm'
            )

        except Exception as e:
            self.logger.error(f"LLM recommendation failed: {e}")
            return None

    def _enhance_with_llm(
        self,
        base_recommendation: Dict[str, Any],
        rec_type: str
    ) -> Dict[str, Any]:
        """Enhance rule-based recommendation with LLM insights."""

        try:
            prompt_context = {
                'base_recommendation': base_recommendation,
                'task': 'enhance',
                'type': rec_type
            }

            enhancement = self.llm_engine.generate_recommendation(
                prompt_context,
                f'{rec_type}_enhancement'
            )

            return enhancement

        except Exception as e:
            self.logger.warning(f"LLM enhancement failed: {e}")
            return {}

    def _create_unified_recommendation(
        self,
        rec_data: Dict[str, Any],
        rec_type: str,
        llm_enhancement: Optional[Dict[str, Any]] = None,
        source: str = 'rule_based'
    ) -> IntelligentRecommendation:
        """Create unified recommendation from engine output."""

        # Generate unique ID
        rec_id = f"{rec_type}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # Extract common fields
        title = rec_data.get('title', llm_enhancement.get('title') if llm_enhancement else 'Optimization Recommendation')
        description = rec_data.get('description', rec_data.get('justification', ''))

        # Merge LLM enhancement if available
        if llm_enhancement:
            description = llm_enhancement.get('description', description)
            if 'additional_context' in llm_enhancement:
                description += f"\n\nLLM Insight: {llm_enhancement['additional_context']}"

        # Extract impact
        impact = {
            'cost_monthly_usd': rec_data.get('cost_impact', rec_data.get('estimated_savings', 0)),
            'performance': rec_data.get('performance_impact', 'Unknown'),
            'effort': rec_data.get('implementation_effort', rec_data.get('implementation_complexity', 'Medium'))
        }

        # Extract implementation details
        implementation = {
            'steps': rec_data.get('implementation_steps', rec_data.get('recommended_actions', [])),
            'complexity': rec_data.get('implementation_complexity', rec_data.get('implementation_effort', 'Medium')),
            'estimated_time': rec_data.get('estimated_implementation_time', 'Unknown'),
            'config': rec_data.get('recommended_config', rec_data.get('auto_scaling_policy'))
        }

        return IntelligentRecommendation(
            id=rec_id,
            type=rec_type,
            category=rec_data.get('category', rec_type),
            title=title,
            description=description,
            priority=rec_data.get('priority', 'medium'),
            impact=impact,
            implementation=implementation,
            confidence_score=rec_data.get('confidence_score', rec_data.get('confidence', 0.75)),
            source=source,
            created_at=datetime.now()
        )

    def export_recommendations(
        self,
        recommendations: List[IntelligentRecommendation],
        format: str = 'json'
    ) -> str:
        """Export recommendations in specified format."""

        if format == 'json':
            return json.dumps(
                [rec.to_dict() for rec in recommendations],
                indent=2,
                default=str
            )
        elif format == 'markdown':
            return self._export_as_markdown(recommendations)
        elif format == 'html':
            return self._export_as_html(recommendations)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_as_markdown(self, recommendations: List[IntelligentRecommendation]) -> str:
        """Export as markdown report."""

        md = "# AI/ML Infrastructure Recommendations\n\n"
        md += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += f"Total Recommendations: {len(recommendations)}\n\n"

        for rec in recommendations:
            md += f"## {rec.title}\n\n"
            md += f"**Priority:** {rec.priority.upper()} | "
            md += f"**Type:** {rec.type} | "
            md += f"**Confidence:** {rec.confidence_score:.0%}\n\n"
            md += f"{rec.description}\n\n"

            md += "### Impact\n"
            md += f"- **Cost:** ${rec.impact.get('cost_monthly_usd', 0):.2f}/month\n"
            md += f"- **Performance:** {rec.impact.get('performance', 'N/A')}\n"
            md += f"- **Effort:** {rec.impact.get('effort', 'Unknown')}\n\n"

            md += "### Implementation Steps\n"
            for step in rec.implementation.get('steps', []):
                md += f"1. {step}\n"
            md += "\n---\n\n"

        return md

    def _export_as_html(self, recommendations: List[IntelligentRecommendation]) -> str:
        """Export as HTML report."""

        html = f"""
        <html>
        <head>
            <title>AI/ML Infrastructure Recommendations</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .recommendation {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; }}
                .critical {{ border-left: 5px solid #d32f2f; }}
                .high {{ border-left: 5px solid #f57c00; }}
                .medium {{ border-left: 5px solid #fbc02d; }}
                .low {{ border-left: 5px solid #388e3c; }}
                .badge {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>AI/ML Infrastructure Recommendations</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total Recommendations: {len(recommendations)}</p>
        """

        for rec in recommendations:
            html += f"""
            <div class="recommendation {rec.priority}">
                <h2>{rec.title}</h2>
                <p>
                    <span class="badge">{rec.priority.upper()}</span>
                    <span class="badge">{rec.type}</span>
                    <span class="badge">Confidence: {rec.confidence_score:.0%}</span>
                </p>
                <p>{rec.description}</p>
                <h3>Impact</h3>
                <ul>
                    <li>Cost: ${rec.impact.get('cost_monthly_usd', 0):.2f}/month</li>
                    <li>Performance: {rec.impact.get('performance', 'N/A')}</li>
                    <li>Effort: {rec.impact.get('effort', 'Unknown')}</li>
                </ul>
                <h3>Implementation Steps</h3>
                <ol>
            """

            for step in rec.implementation.get('steps', []):
                html += f"<li>{step}</li>"

            html += """
                </ol>
            </div>
            """

        html += """
        </body>
        </html>
        """

        return html


# Convenience function
def get_recommendations(
    current_metrics: Dict[str, Any],
    historical_data: Optional[List[Dict[str, Any]]] = None,
    workload_type: str = "inference",
    cloud_provider: str = "aws",
    llm_config: Optional[LLMConfig] = None
) -> List[IntelligentRecommendation]:
    """
    Get intelligent recommendations with one function call.

    Args:
        current_metrics: Current infrastructure metrics
        historical_data: Historical metrics for pattern detection
        workload_type: Type of workload (training, inference, etc.)
        cloud_provider: Cloud provider (aws, gcp, azure)
        llm_config: Optional LLM configuration

    Returns:
        List of intelligent recommendations
    """
    coordinator = IntelligentRecommendationsCoordinator(llm_config)
    return coordinator.get_all_recommendations(
        current_metrics,
        historical_data,
        workload_type,
        cloud_provider
    )
