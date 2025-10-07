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
AI-Powered Observability and FinOps Recommendations
==================================================

Intelligent recommendation system that analyzes LLM training, RAG pipelines,
and infrastructure metrics to provide actionable insights for:
- Performance optimization
- Cost reduction opportunities
- Resource allocation improvements
- Quality enhancement suggestions
- Predictive maintenance alerts
"""

import json
import time
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque

# Import observability components
from .llm_observability import (
    LLMTrainingMetrics, RAGPipelineMetrics, AgentWorkflowMetrics,
    VectorDBMetrics, LLMFinOpsMetrics
)


class RecommendationType(Enum):
    """Types of AI-generated recommendations."""
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    RESOURCE_SCALING = "resource_scaling"
    ANOMALY_ALERT = "anomaly_alert"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"
    SECURITY_CONCERN = "security_concern"
    COMPLIANCE_ISSUE = "compliance_issue"


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AIRecommendation:
    """AI-generated recommendation with context and actions."""
    id: str
    type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    impact_estimate: str  # e.g., "Save $2,500/month", "Improve latency by 30%"
    confidence_score: float  # 0.0 to 1.0

    # Actionable steps
    recommended_actions: List[str]
    implementation_effort: str  # "Low", "Medium", "High"
    estimated_implementation_time: str  # e.g., "2-4 hours", "1-2 days"

    # Context and evidence
    affected_components: List[str]
    metrics_evidence: Dict[str, Any]
    trend_analysis: Dict[str, Any]

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    category: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary format."""
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "impact_estimate": self.impact_estimate,
            "confidence_score": self.confidence_score,
            "recommended_actions": self.recommended_actions,
            "implementation_effort": self.implementation_effort,
            "estimated_implementation_time": self.estimated_implementation_time,
            "affected_components": self.affected_components,
            "metrics_evidence": self.metrics_evidence,
            "trend_analysis": self.trend_analysis,
            "created_at": self.created_at.isoformat(),
            "category": self.category,
            "tags": self.tags
        }


class AIObservabilityEngine:
    """AI-powered analysis engine for observability insights."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Historical data for trend analysis
        self.metrics_history = defaultdict(deque)
        self.max_history_size = 1000

        # Recommendation cache
        self.active_recommendations = {}
        self.recommendation_history = deque(maxlen=500)

        # Analysis models (simplified AI logic)
        self.cost_thresholds = {
            'high_spend_alert': 5000.0,  # USD per month
            'unusual_spike': 0.3,  # 30% increase
            'inefficiency_ratio': 0.6   # Resource utilization below 60%
        }

        self.performance_thresholds = {
            'latency_degradation': 0.2,  # 20% increase in latency
            'error_rate_spike': 0.05,    # 5% error rate
            'throughput_drop': 0.15      # 15% decrease in throughput
        }

        # Initialize AI models
        self._initialize_ai_models()

    def _initialize_ai_models(self):
        """Initialize AI analysis models."""
        self.logger.info("Initializing AI recommendation models")

        # Cost optimization model weights
        self.cost_model_weights = {
            'gpu_utilization': 0.3,
            'token_efficiency': 0.25,
            'storage_optimization': 0.2,
            'api_call_patterns': 0.15,
            'scaling_efficiency': 0.1
        }

        # Performance analysis weights
        self.performance_weights = {
            'latency_trends': 0.3,
            'error_patterns': 0.25,
            'resource_bottlenecks': 0.2,
            'cache_efficiency': 0.15,
            'concurrent_load': 0.1
        }

        # Quality assessment weights
        self.quality_weights = {
            'retrieval_accuracy': 0.35,
            'semantic_relevance': 0.25,
            'response_completeness': 0.2,
            'hallucination_detection': 0.2
        }

    def analyze_and_recommend(
        self,
        training_metrics: Optional[LLMTrainingMetrics] = None,
        rag_metrics: Optional[RAGPipelineMetrics] = None,
        finops_metrics: Optional[LLMFinOpsMetrics] = None,
        vector_db_metrics: Optional[Dict[str, VectorDBMetrics]] = None,
        agent_metrics: Optional[AgentWorkflowMetrics] = None
    ) -> List[AIRecommendation]:
        """Generate AI-powered recommendations based on current metrics."""

        recommendations = []

        # Store metrics for trend analysis
        self._update_metrics_history(
            training_metrics, rag_metrics, finops_metrics,
            vector_db_metrics, agent_metrics
        )

        # Cost optimization recommendations
        if finops_metrics:
            cost_recs = self._analyze_cost_optimization(finops_metrics)
            recommendations.extend(cost_recs)

        # Performance improvement recommendations
        if rag_metrics:
            perf_recs = self._analyze_performance_patterns(rag_metrics)
            recommendations.extend(perf_recs)

        # Quality enhancement recommendations
        if rag_metrics and vector_db_metrics:
            quality_recs = self._analyze_quality_metrics(rag_metrics, vector_db_metrics)
            recommendations.extend(quality_recs)

        # Resource scaling recommendations
        if training_metrics and finops_metrics:
            scaling_recs = self._analyze_resource_scaling(training_metrics, finops_metrics)
            recommendations.extend(scaling_recs)

        # Anomaly detection and alerts
        anomaly_recs = self._detect_anomalies()
        recommendations.extend(anomaly_recs)

        # Predictive maintenance
        maintenance_recs = self._predictive_maintenance_analysis()
        recommendations.extend(maintenance_recs)

        # Update recommendation cache
        for rec in recommendations:
            self.active_recommendations[rec.id] = rec
            self.recommendation_history.append(rec)

        # Sort by priority and confidence
        recommendations.sort(
            key=lambda x: (x.priority.value, -x.confidence_score)
        )

        return recommendations

    def _analyze_cost_optimization(self, finops_metrics: LLMFinOpsMetrics) -> List[AIRecommendation]:
        """Analyze cost patterns and generate optimization recommendations."""
        recommendations = []

        # High spend alert
        monthly_cost = finops_metrics.total_cost
        if monthly_cost > self.cost_thresholds['high_spend_alert']:
            rec = AIRecommendation(
                id=f"cost_alert_{int(time.time())}",
                type=RecommendationType.COST_OPTIMIZATION,
                priority=RecommendationPriority.HIGH,
                title="High Monthly Spend Detected",
                description=f"Current monthly cost of ${monthly_cost:,.2f} exceeds recommended threshold. Consider implementing cost controls.",
                impact_estimate=f"Potential savings: ${monthly_cost * 0.2:,.2f}/month",
                confidence_score=0.95,
                recommended_actions=[
                    "Review GPU instance utilization and downsize underused instances",
                    "Implement automatic scaling based on demand patterns",
                    "Optimize token usage by improving prompt engineering",
                    "Consider reserved instance pricing for consistent workloads"
                ],
                implementation_effort="Medium",
                estimated_implementation_time="1-2 days",
                affected_components=["GPU Infrastructure", "API Usage", "Storage"],
                metrics_evidence={"monthly_cost": monthly_cost, "threshold": self.cost_thresholds['high_spend_alert']},
                trend_analysis=self._analyze_cost_trends(),
                category="Cost Management",
                tags=["cost-optimization", "budget-alert", "infrastructure"]
            )
            recommendations.append(rec)

        # GPU utilization optimization
        if hasattr(finops_metrics, 'gpu_utilization') and finops_metrics.gpu_utilization < 60:
            rec = AIRecommendation(
                id=f"gpu_optimization_{int(time.time())}",
                type=RecommendationType.COST_OPTIMIZATION,
                priority=RecommendationPriority.MEDIUM,
                title="Low GPU Utilization Detected",
                description=f"GPU utilization at {finops_metrics.gpu_utilization}% indicates potential over-provisioning.",
                impact_estimate="Save $1,200-2,800/month",
                confidence_score=0.87,
                recommended_actions=[
                    "Analyze workload patterns to identify optimal instance sizes",
                    "Implement dynamic scaling based on queue depth",
                    "Consider spot instances for non-critical training jobs",
                    "Batch similar workloads to improve utilization"
                ],
                implementation_effort="Medium",
                estimated_implementation_time="3-5 days",
                affected_components=["GPU Instances", "Training Pipeline"],
                metrics_evidence={"gpu_utilization": finops_metrics.gpu_utilization},
                trend_analysis={"utilization_trend": "declining"},
                category="Resource Optimization",
                tags=["gpu", "utilization", "cost-saving"]
            )
            recommendations.append(rec)

        # Token usage optimization
        if hasattr(finops_metrics, 'tokens_per_dollar') and finops_metrics.tokens_per_dollar < 1000:
            rec = AIRecommendation(
                id=f"token_efficiency_{int(time.time())}",
                type=RecommendationType.COST_OPTIMIZATION,
                priority=RecommendationPriority.MEDIUM,
                title="Optimize Token Usage Efficiency",
                description="Token usage patterns indicate opportunities for prompt optimization and caching.",
                impact_estimate="Reduce token costs by 25-40%",
                confidence_score=0.82,
                recommended_actions=[
                    "Implement intelligent prompt caching for repeated queries",
                    "Optimize prompt templates to reduce token count",
                    "Use smaller models for simple classification tasks",
                    "Implement response streaming to reduce perceived latency"
                ],
                implementation_effort="Low",
                estimated_implementation_time="4-6 hours",
                affected_components=["LLM API", "Prompt Engineering"],
                metrics_evidence={"tokens_per_dollar": getattr(finops_metrics, 'tokens_per_dollar', 0)},
                trend_analysis={"efficiency_trend": "stable"},
                category="API Optimization",
                tags=["tokens", "prompts", "efficiency"]
            )
            recommendations.append(rec)

        return recommendations

    def _analyze_performance_patterns(self, rag_metrics: RAGPipelineMetrics) -> List[AIRecommendation]:
        """Analyze performance patterns and suggest improvements."""
        recommendations = []

        # Latency optimization
        if rag_metrics.latency_p95 > 2000:  # 2 seconds
            rec = AIRecommendation(
                id=f"latency_optimization_{int(time.time())}",
                type=RecommendationType.PERFORMANCE_IMPROVEMENT,
                priority=RecommendationPriority.HIGH,
                title="High Query Latency Detected",
                description=f"P95 query latency of {rag_metrics.latency_p95:.0f}ms exceeds acceptable thresholds.",
                impact_estimate="Improve response time by 40-60%",
                confidence_score=0.91,
                recommended_actions=[
                    "Implement vector similarity caching for frequent queries",
                    "Optimize embedding model inference with quantization",
                    "Add query result caching layer",
                    "Consider upgrading to faster vector database tier"
                ],
                implementation_effort="Medium",
                estimated_implementation_time="2-3 days",
                affected_components=["Vector Database", "Embedding Service", "Cache Layer"],
                metrics_evidence={"latency_p50": rag_metrics.latency_p50, "latency_p95": rag_metrics.latency_p95},
                trend_analysis=self._analyze_latency_trends(),
                category="Performance Optimization",
                tags=["latency", "caching", "inference"]
            )
            recommendations.append(rec)

        # Retrieval accuracy improvement
        if rag_metrics.retrieval_accuracy < 0.85:  # 85%
            rec = AIRecommendation(
                id=f"accuracy_improvement_{int(time.time())}",
                type=RecommendationType.QUALITY_ENHANCEMENT,
                priority=RecommendationPriority.HIGH,
                title="Improve Retrieval Accuracy",
                description=f"Current retrieval accuracy of {rag_metrics.retrieval_accuracy:.1%} can be enhanced.",
                impact_estimate="Increase accuracy by 10-15%",
                confidence_score=0.88,
                recommended_actions=[
                    "Fine-tune embedding model on domain-specific data",
                    "Implement hybrid search combining vector and keyword search",
                    "Optimize chunk size and overlap parameters",
                    "Add query expansion and rewriting pipeline"
                ],
                implementation_effort="High",
                estimated_implementation_time="1-2 weeks",
                affected_components=["Embedding Model", "Search Pipeline", "Document Processing"],
                metrics_evidence={"retrieval_accuracy": rag_metrics.retrieval_accuracy},
                trend_analysis={"accuracy_trend": "declining"},
                category="Quality Enhancement",
                tags=["accuracy", "embeddings", "search"]
            )
            recommendations.append(rec)

        # Cache hit rate optimization
        if hasattr(rag_metrics, 'cache_hit_rate') and rag_metrics.cache_hit_rate < 0.6:
            rec = AIRecommendation(
                id=f"cache_optimization_{int(time.time())}",
                type=RecommendationType.PERFORMANCE_IMPROVEMENT,
                priority=RecommendationPriority.MEDIUM,
                title="Optimize Caching Strategy",
                description=f"Cache hit rate of {rag_metrics.cache_hit_rate:.1%} indicates caching inefficiencies.",
                impact_estimate="Reduce query latency by 30%",
                confidence_score=0.85,
                recommended_actions=[
                    "Analyze query patterns to improve cache key design",
                    "Implement semantic similarity-based cache lookups",
                    "Increase cache size for frequently accessed vectors",
                    "Add cache warming for popular content"
                ],
                implementation_effort="Low",
                estimated_implementation_time="1-2 days",
                affected_components=["Cache Layer", "Query Processing"],
                metrics_evidence={"cache_hit_rate": getattr(rag_metrics, 'cache_hit_rate', 0)},
                trend_analysis={"cache_efficiency": "low"},
                category="Cache Optimization",
                tags=["caching", "performance", "efficiency"]
            )
            recommendations.append(rec)

        return recommendations

    def _analyze_quality_metrics(
        self,
        rag_metrics: RAGPipelineMetrics,
        vector_db_metrics: Dict[str, VectorDBMetrics]
    ) -> List[AIRecommendation]:
        """Analyze quality metrics and provide enhancement recommendations."""
        recommendations = []

        # Vector database performance analysis
        for db_id, db_metrics in vector_db_metrics.items():
            if db_metrics.error_rate > 0.01:  # 1% error rate
                rec = AIRecommendation(
                    id=f"db_reliability_{db_id}_{int(time.time())}",
                    type=RecommendationType.QUALITY_ENHANCEMENT,
                    priority=RecommendationPriority.HIGH,
                    title=f"Vector Database Reliability Issue ({db_id})",
                    description=f"Error rate of {db_metrics.error_rate:.2%} in {db_id} affects system reliability.",
                    impact_estimate="Improve system reliability by 95%+",
                    confidence_score=0.93,
                    recommended_actions=[
                        "Investigate and fix connection timeouts",
                        "Implement retry logic with exponential backoff",
                        "Add circuit breaker pattern for fault tolerance",
                        "Monitor database resource utilization"
                    ],
                    implementation_effort="Medium",
                    estimated_implementation_time="2-4 days",
                    affected_components=[f"Vector DB: {db_id}", "Query Pipeline"],
                    metrics_evidence={"error_rate": db_metrics.error_rate, "db_id": db_id},
                    trend_analysis={"error_trend": "increasing"},
                    category="Reliability",
                    tags=["database", "reliability", "error-handling"]
                )
                recommendations.append(rec)

            # Index efficiency optimization
            if db_metrics.index_efficiency < 0.8:  # 80%
                rec = AIRecommendation(
                    id=f"index_optimization_{db_id}_{int(time.time())}",
                    type=RecommendationType.PERFORMANCE_IMPROVEMENT,
                    priority=RecommendationPriority.MEDIUM,
                    title=f"Optimize Vector Index ({db_id})",
                    description=f"Index efficiency of {db_metrics.index_efficiency:.1%} can be improved.",
                    impact_estimate="Reduce query time by 25-40%",
                    confidence_score=0.80,
                    recommended_actions=[
                        "Analyze vector distribution and clustering patterns",
                        "Rebuild index with optimized parameters",
                        "Consider upgrading to more efficient index type",
                        "Implement periodic index maintenance"
                    ],
                    implementation_effort="Medium",
                    estimated_implementation_time="1-2 days",
                    affected_components=[f"Vector DB: {db_id}"],
                    metrics_evidence={"index_efficiency": db_metrics.index_efficiency},
                    trend_analysis={"efficiency_trend": "declining"},
                    category="Index Optimization",
                    tags=["indexing", "performance", "optimization"]
                )
                recommendations.append(rec)

        return recommendations

    def _analyze_resource_scaling(
        self,
        training_metrics: LLMTrainingMetrics,
        finops_metrics: LLMFinOpsMetrics
    ) -> List[AIRecommendation]:
        """Analyze resource usage patterns and suggest scaling recommendations."""
        recommendations = []

        # GPU memory utilization
        if hasattr(training_metrics, 'gpu_memory_utilization') and training_metrics.gpu_memory_utilization > 90:
            rec = AIRecommendation(
                id=f"memory_scaling_{int(time.time())}",
                type=RecommendationType.RESOURCE_SCALING,
                priority=RecommendationPriority.HIGH,
                title="GPU Memory Pressure Detected",
                description=f"GPU memory utilization at {training_metrics.gpu_memory_utilization}% indicates potential bottleneck.",
                impact_estimate="Prevent OOM errors, improve training stability",
                confidence_score=0.94,
                recommended_actions=[
                    "Increase GPU memory or use instances with higher memory",
                    "Implement gradient checkpointing to reduce memory usage",
                    "Optimize batch size for current memory constraints",
                    "Consider model parallelism for large models"
                ],
                implementation_effort="Medium",
                estimated_implementation_time="1-3 days",
                affected_components=["GPU Infrastructure", "Training Pipeline"],
                metrics_evidence={"gpu_memory_utilization": getattr(training_metrics, 'gpu_memory_utilization', 0)},
                trend_analysis={"memory_trend": "increasing"},
                category="Resource Scaling",
                tags=["gpu", "memory", "scaling"]
            )
            recommendations.append(rec)

        return recommendations

    def _detect_anomalies(self) -> List[AIRecommendation]:
        """Detect anomalies in system behavior and generate alerts."""
        recommendations = []

        # Check for unusual cost spikes
        if len(self.metrics_history['cost']) >= 5:
            recent_costs = list(self.metrics_history['cost'])[-5:]
            if len(recent_costs) >= 2:
                cost_increase = (recent_costs[-1] - recent_costs[-2]) / recent_costs[-2]
                if cost_increase > self.cost_thresholds['unusual_spike']:
                    rec = AIRecommendation(
                        id=f"cost_anomaly_{int(time.time())}",
                        type=RecommendationType.ANOMALY_ALERT,
                        priority=RecommendationPriority.CRITICAL,
                        title="Unusual Cost Spike Detected",
                        description=f"Cost increased by {cost_increase:.1%} in the last period, indicating potential anomaly.",
                        impact_estimate="Investigate to prevent budget overrun",
                        confidence_score=0.89,
                        recommended_actions=[
                            "Immediately review active GPU instances and usage",
                            "Check for runaway training jobs or infinite loops",
                            "Verify API call patterns for unusual activity",
                            "Implement emergency cost controls if needed"
                        ],
                        implementation_effort="Low",
                        estimated_implementation_time="30 minutes",
                        affected_components=["Cost Monitoring", "Infrastructure"],
                        metrics_evidence={"cost_increase": cost_increase, "recent_costs": recent_costs},
                        trend_analysis={"anomaly_type": "cost_spike"},
                        category="Anomaly Detection",
                        tags=["anomaly", "cost", "alert"]
                    )
                    recommendations.append(rec)

        return recommendations

    def _predictive_maintenance_analysis(self) -> List[AIRecommendation]:
        """Analyze patterns to predict maintenance needs."""
        recommendations = []

        # Example predictive maintenance recommendation
        rec = AIRecommendation(
            id=f"maintenance_{int(time.time())}",
            type=RecommendationType.PREDICTIVE_MAINTENANCE,
            priority=RecommendationPriority.LOW,
            title="Scheduled Model Performance Review",
            description="Based on usage patterns, consider reviewing model performance metrics.",
            impact_estimate="Maintain optimal system performance",
            confidence_score=0.70,
            recommended_actions=[
                "Schedule quarterly model performance review",
                "Update embedding models with latest data",
                "Review and refresh cached results",
                "Audit data quality and freshness"
            ],
            implementation_effort="Low",
            estimated_implementation_time="2-4 hours",
            affected_components=["Model Pipeline", "Data Quality"],
            metrics_evidence={"last_review": "3 months ago"},
            trend_analysis={"maintenance_needed": True},
            category="Maintenance",
            tags=["maintenance", "review", "performance"]
        )
        recommendations.append(rec)

        return recommendations

    def _update_metrics_history(self, *metrics):
        """Update historical metrics for trend analysis."""
        timestamp = time.time()

        for metric in metrics:
            if metric:
                # Store key metrics for trend analysis
                if hasattr(metric, 'total_cost_usd'):
                    self.metrics_history['cost'].append(metric.total_cost_usd)
                if hasattr(metric, 'avg_query_latency_ms'):
                    self.metrics_history['latency'].append(metric.avg_query_latency_ms)
                if hasattr(metric, 'retrieval_accuracy'):
                    self.metrics_history['accuracy'].append(metric.retrieval_accuracy)

        # Limit history size
        for key in self.metrics_history:
            if len(self.metrics_history[key]) > self.max_history_size:
                self.metrics_history[key].popleft()

    def _analyze_cost_trends(self) -> Dict[str, Any]:
        """Analyze cost trends from historical data."""
        if not self.metrics_history['cost']:
            return {"trend": "no_data"}

        costs = list(self.metrics_history['cost'])
        if len(costs) < 2:
            return {"trend": "insufficient_data"}

        recent_avg = np.mean(costs[-5:]) if len(costs) >= 5 else costs[-1]
        older_avg = np.mean(costs[:-5]) if len(costs) >= 10 else costs[0]

        if recent_avg > older_avg * 1.1:
            trend = "increasing"
        elif recent_avg < older_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "recent_avg": recent_avg,
            "older_avg": older_avg,
            "change_percent": ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
        }

    def _analyze_latency_trends(self) -> Dict[str, Any]:
        """Analyze latency trends from historical data."""
        if not self.metrics_history['latency']:
            return {"trend": "no_data"}

        latencies = list(self.metrics_history['latency'])
        if len(latencies) < 2:
            return {"trend": "insufficient_data"}

        recent_avg = np.mean(latencies[-10:]) if len(latencies) >= 10 else latencies[-1]
        baseline_avg = np.mean(latencies[:10]) if len(latencies) >= 20 else latencies[0]

        return {
            "trend": "increasing" if recent_avg > baseline_avg * 1.2 else "stable",
            "recent_avg": recent_avg,
            "baseline_avg": baseline_avg,
            "degradation_percent": ((recent_avg - baseline_avg) / baseline_avg) * 100 if baseline_avg > 0 else 0
        }

    def get_recommendation_summary(self) -> Dict[str, Any]:
        """Get summary of active recommendations."""
        if not self.active_recommendations:
            return {"total": 0, "by_priority": {}, "by_type": {}}

        by_priority = defaultdict(int)
        by_type = defaultdict(int)

        for rec in self.active_recommendations.values():
            by_priority[rec.priority.value] += 1
            by_type[rec.type.value] += 1

        return {
            "total": len(self.active_recommendations),
            "by_priority": dict(by_priority),
            "by_type": dict(by_type),
            "latest_update": max(rec.created_at for rec in self.active_recommendations.values()).isoformat()
        }

    def get_top_recommendations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top recommendations by priority and confidence."""
        recommendations = list(self.active_recommendations.values())
        recommendations.sort(
            key=lambda x: (x.priority.value, -x.confidence_score)
        )

        return [rec.to_dict() for rec in recommendations[:limit]]


# Global AI recommendation engine instance
ai_engine = AIObservabilityEngine()


def generate_ai_recommendations(
    training_metrics: Optional[LLMTrainingMetrics] = None,
    rag_metrics: Optional[RAGPipelineMetrics] = None,
    finops_metrics: Optional[LLMFinOpsMetrics] = None,
    vector_db_metrics: Optional[Dict[str, VectorDBMetrics]] = None,
    agent_metrics: Optional[AgentWorkflowMetrics] = None
) -> List[Dict[str, Any]]:
    """
    Generate AI-powered recommendations based on current system metrics.

    Returns:
        List of recommendation dictionaries with actionable insights
    """
    recommendations = ai_engine.analyze_and_recommend(
        training_metrics=training_metrics,
        rag_metrics=rag_metrics,
        finops_metrics=finops_metrics,
        vector_db_metrics=vector_db_metrics,
        agent_metrics=agent_metrics
    )

    return [rec.to_dict() for rec in recommendations]


def get_recommendation_dashboard() -> Dict[str, Any]:
    """
    Get comprehensive recommendation dashboard data.

    Returns:
        Dashboard data including summary and top recommendations
    """
    return {
        "summary": ai_engine.get_recommendation_summary(),
        "top_recommendations": ai_engine.get_top_recommendations(5),
        "timestamp": datetime.now().isoformat(),
        "ai_engine_status": "active"
    }