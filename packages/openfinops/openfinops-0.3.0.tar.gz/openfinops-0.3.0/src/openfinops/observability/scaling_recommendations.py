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
Intelligent Scaling Recommendations for AI/ML Infrastructure
=============================================================

Provides intelligent auto-scaling and capacity planning recommendations:
- Horizontal vs Vertical scaling analysis
- Auto-scaling configuration optimization
- Load prediction and capacity planning
- Cost-aware scaling strategies
- GPU cluster auto-scaling
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from collections import deque


class ScalingStrategy(Enum):
    """Scaling strategy types."""
    HORIZONTAL = "horizontal"  # More instances
    VERTICAL = "vertical"      # Larger instances
    HYBRID = "hybrid"          # Combination
    AUTO_SCALING = "auto_scaling"
    PREDICTIVE = "predictive"
    SPOT_INSTANCES = "spot_instances"


class ScalingTrigger(Enum):
    """What triggers scaling."""
    CPU_UTILIZATION = "cpu_utilization"
    GPU_UTILIZATION = "gpu_utilization"
    MEMORY_PRESSURE = "memory_pressure"
    REQUEST_RATE = "request_rate"
    QUEUE_DEPTH = "queue_depth"
    LATENCY = "latency"
    SCHEDULED = "scheduled"
    PREDICTIVE_ML = "predictive_ml"


@dataclass
class ScalingRecommendation:
    """Scaling recommendation with implementation details."""
    strategy: ScalingStrategy
    trigger: ScalingTrigger
    current_config: Dict[str, Any]
    recommended_config: Dict[str, Any]
    justification: str
    cost_impact: float  # Monthly USD change (negative = savings)
    performance_impact: str
    implementation_complexity: str  # "Low", "Medium", "High"
    implementation_steps: List[str]
    auto_scaling_policy: Optional[Dict[str, Any]] = None
    estimated_roi_days: int = 30
    confidence_score: float = 0.85
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy": self.strategy.value,
            "trigger": self.trigger.value,
            "current_config": self.current_config,
            "recommended_config": self.recommended_config,
            "justification": self.justification,
            "cost_impact": self.cost_impact,
            "performance_impact": self.performance_impact,
            "implementation_complexity": self.implementation_complexity,
            "implementation_steps": self.implementation_steps,
            "auto_scaling_policy": self.auto_scaling_policy,
            "estimated_roi_days": self.estimated_roi_days,
            "confidence_score": self.confidence_score,
            "priority": self.priority,
            "created_at": self.created_at.isoformat()
        }


class ScalingRecommendationEngine:
    """Intelligent scaling recommendation engine."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.utilization_history = deque(maxlen=1000)
        self.request_rate_history = deque(maxlen=1000)

    def analyze_scaling_needs(
        self,
        current_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
        cost_constraints: Optional[Dict[str, float]] = None
    ) -> List[ScalingRecommendation]:
        """Analyze current state and generate scaling recommendations."""

        recommendations = []

        # Analyze current utilization patterns
        utilization_rec = self._analyze_utilization_pattern(current_metrics, historical_data)
        if utilization_rec:
            recommendations.append(utilization_rec)

        # Analyze auto-scaling configuration
        autoscaling_rec = self._analyze_autoscaling_config(current_metrics, historical_data)
        if autoscaling_rec:
            recommendations.append(autoscaling_rec)

        # Analyze GPU-specific scaling
        if current_metrics.get('has_gpu', False):
            gpu_scaling_rec = self._analyze_gpu_scaling(current_metrics, historical_data)
            if gpu_scaling_rec:
                recommendations.append(gpu_scaling_rec)

        # Analyze spot instance opportunities
        spot_rec = self._analyze_spot_instances(current_metrics, cost_constraints)
        if spot_rec:
            recommendations.append(spot_rec)

        # Predictive scaling recommendations
        if historical_data and len(historical_data) > 24:  # At least 24 hours of data
            predictive_rec = self._predictive_scaling_recommendation(historical_data, current_metrics)
            if predictive_rec:
                recommendations.append(predictive_rec)

        # Cost optimization through scheduled scaling
        scheduled_rec = self._scheduled_scaling_recommendation(historical_data, current_metrics)
        if scheduled_rec:
            recommendations.append(scheduled_rec)

        return recommendations

    def _analyze_utilization_pattern(
        self,
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> Optional[ScalingRecommendation]:
        """Analyze utilization and recommend horizontal or vertical scaling."""

        current_instances = metrics.get('instance_count', 1)
        avg_cpu_util = metrics.get('avg_cpu_utilization', 50)
        avg_gpu_util = metrics.get('avg_gpu_utilization', 0)
        peak_cpu_util = metrics.get('peak_cpu_utilization', 50)
        cost_per_instance = metrics.get('cost_per_instance_hour', 1.0)

        # Determine if under or over-provisioned
        if avg_cpu_util < 30 and current_instances > 1:
            # Over-provisioned - scale down
            recommended_instances = max(1, int(current_instances * (avg_cpu_util / 50)))
            monthly_savings = (current_instances - recommended_instances) * cost_per_instance * 730

            return ScalingRecommendation(
                strategy=ScalingStrategy.HORIZONTAL,
                trigger=ScalingTrigger.CPU_UTILIZATION,
                current_config={
                    "instance_count": current_instances,
                    "avg_cpu_utilization": avg_cpu_util,
                    "cost_per_month": current_instances * cost_per_instance * 730
                },
                recommended_config={
                    "instance_count": recommended_instances,
                    "target_cpu_utilization": "50-70%",
                    "cost_per_month": recommended_instances * cost_per_instance * 730
                },
                justification=f"Average CPU utilization is only {avg_cpu_util}% across {current_instances} instances. "
                              f"Consolidating to {recommended_instances} instances will maintain performance while reducing costs.",
                cost_impact=-monthly_savings,
                performance_impact="No degradation, maintains 50-70% target utilization",
                implementation_complexity="Low",
                implementation_steps=[
                    "Enable auto-scaling with min={} instances".format(recommended_instances),
                    "Set CPU target to 60%",
                    "Gradually reduce instance count",
                    "Monitor for 48 hours",
                    "Rollback if latency increases"
                ],
                confidence_score=0.88,
                priority="high"
            )

        elif peak_cpu_util > 85 or avg_cpu_util > 70:
            # Under-provisioned - scale up
            if avg_cpu_util > 70 and peak_cpu_util < 90:
                # Vertical scaling better for consistent high load
                return ScalingRecommendation(
                    strategy=ScalingStrategy.VERTICAL,
                    trigger=ScalingTrigger.CPU_UTILIZATION,
                    current_config={
                        "instance_count": current_instances,
                        "instance_size": metrics.get('instance_type', 'medium'),
                        "avg_cpu_utilization": avg_cpu_util
                    },
                    recommended_config={
                        "instance_count": current_instances,
                        "instance_size": "larger",
                        "expected_cpu_utilization": "50-60%"
                    },
                    justification=f"Consistent high CPU utilization ({avg_cpu_util}%) indicates need for larger instances. "
                                  "Vertical scaling is more efficient than adding more instances.",
                    cost_impact=current_instances * cost_per_instance * 0.5 * 730,  # 50% cost increase
                    performance_impact="50-70% performance improvement, better resource utilization",
                    implementation_complexity="Medium",
                    implementation_steps=[
                        "Test workload on larger instance type",
                        "Update instance configuration",
                        "Perform rolling update",
                        "Monitor performance improvements"
                    ],
                    confidence_score=0.82,
                    priority="high"
                )
            else:
                # Horizontal scaling for spiky load
                recommended_instances = int(current_instances * 1.5)
                return ScalingRecommendation(
                    strategy=ScalingStrategy.HORIZONTAL,
                    trigger=ScalingTrigger.CPU_UTILIZATION,
                    current_config={
                        "instance_count": current_instances,
                        "peak_cpu_utilization": peak_cpu_util,
                        "capacity_buffer": "None"
                    },
                    recommended_config={
                        "instance_count": recommended_instances,
                        "target_cpu_utilization": "60-70%",
                        "capacity_buffer": "30%"
                    },
                    justification=f"Peak CPU utilization reaches {peak_cpu_util}%. Add instances to handle spikes.",
                    cost_impact=(recommended_instances - current_instances) * cost_per_instance * 730,
                    performance_impact="Handle 50% more load, reduce latency during peaks",
                    implementation_complexity="Low",
                    implementation_steps=[
                        f"Scale to {recommended_instances} instances",
                        "Configure load balancing",
                        "Enable health checks",
                        "Test under peak load"
                    ],
                    confidence_score=0.85,
                    priority="high"
                )

        return None

    def _analyze_autoscaling_config(
        self,
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> Optional[ScalingRecommendation]:
        """Analyze and optimize auto-scaling configuration."""

        has_autoscaling = metrics.get('has_autoscaling', False)
        current_instances = metrics.get('instance_count', 1)
        min_instances = metrics.get('autoscaling_min', 1)
        max_instances = metrics.get('autoscaling_max', 10)

        if not has_autoscaling:
            # Recommend enabling auto-scaling
            return ScalingRecommendation(
                strategy=ScalingStrategy.AUTO_SCALING,
                trigger=ScalingTrigger.CPU_UTILIZATION,
                current_config={
                    "auto_scaling": False,
                    "instance_count": current_instances,
                    "scaling_method": "Manual"
                },
                recommended_config={
                    "auto_scaling": True,
                    "min_instances": max(1, current_instances - 1),
                    "max_instances": current_instances + 3,
                    "target_metric": "CPU 60%",
                    "scale_out_cooldown": 60,
                    "scale_in_cooldown": 180
                },
                justification="Enable auto-scaling to automatically adjust capacity based on demand, "
                              "reducing costs during low usage and ensuring performance during peaks.",
                cost_impact=-metrics.get('cost_per_instance_hour', 1.0) * 730 * 0.3,  # 30% average savings
                performance_impact="Automatic capacity adjustment, improved availability",
                implementation_complexity="Medium",
                implementation_steps=[
                    "Define auto-scaling policy with CPU target 60%",
                    "Set min={}, max={} instances".format(
                        max(1, current_instances - 1),
                        current_instances + 3
                    ),
                    "Configure scale-out cooldown: 60s",
                    "Configure scale-in cooldown: 180s",
                    "Enable CloudWatch alarms",
                    "Test scaling behavior under load"
                ],
                auto_scaling_policy={
                    "metric": "CPUUtilization",
                    "target_value": 60,
                    "min_capacity": max(1, current_instances - 1),
                    "max_capacity": current_instances + 3,
                    "scale_out_cooldown": 60,
                    "scale_in_cooldown": 180,
                    "predictive_scaling": False
                },
                confidence_score=0.90,
                priority="high"
            )

        # Optimize existing auto-scaling
        if historical_data:
            utilization_variance = self._calculate_utilization_variance(historical_data)
            if utilization_variance > 30:  # High variance
                return ScalingRecommendation(
                    strategy=ScalingStrategy.AUTO_SCALING,
                    trigger=ScalingTrigger.PREDICTIVE_ML,
                    current_config={
                        "auto_scaling": "reactive",
                        "min_instances": min_instances,
                        "max_instances": max_instances,
                        "utilization_variance": utilization_variance
                    },
                    recommended_config={
                        "auto_scaling": "predictive",
                        "min_instances": min_instances,
                        "max_instances": max_instances,
                        "forecast_horizon": "15 minutes",
                        "ml_model": "enabled"
                    },
                    justification=f"High utilization variance ({utilization_variance}%) detected. "
                                  "Predictive scaling will pre-emptively add capacity before spikes.",
                    cost_impact=-200,  # Saves on reactive scaling delays
                    performance_impact="Reduced latency spikes, smoother scaling",
                    implementation_complexity="Medium",
                    implementation_steps=[
                        "Enable AWS Predictive Scaling or equivalent",
                        "Train on 14 days of historical data",
                        "Set forecast horizon to 15 minutes",
                        "Monitor prediction accuracy",
                        "Fine-tune scaling parameters"
                    ],
                    auto_scaling_policy={
                        "predictive_scaling": True,
                        "forecast_horizon_minutes": 15,
                        "max_capacity_buffer_percent": 10
                    },
                    confidence_score=0.82,
                    priority="medium"
                )

        return None

    def _analyze_gpu_scaling(
        self,
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> Optional[ScalingRecommendation]:
        """Analyze GPU-specific scaling needs."""

        gpu_utilization = metrics.get('avg_gpu_utilization', 0)
        gpu_count = metrics.get('gpu_count', 1)
        workload_type = metrics.get('workload_type', 'inference')
        cost_per_gpu_hour = metrics.get('cost_per_gpu_hour', 3.0)

        if workload_type == 'training':
            # Training workloads benefit from distributed training
            if gpu_count == 1 and metrics.get('training_time_hours', 0) > 12:
                return ScalingRecommendation(
                    strategy=ScalingStrategy.HORIZONTAL,
                    trigger=ScalingTrigger.GPU_UTILIZATION,
                    current_config={
                        "gpu_count": 1,
                        "training_time_hours": metrics.get('training_time_hours', 0),
                        "distributed_training": False
                    },
                    recommended_config={
                        "gpu_count": 4,
                        "training_time_hours": metrics.get('training_time_hours', 0) / 3.5,  # Scaling efficiency
                        "distributed_training": True,
                        "framework": "PyTorch DDP or DeepSpeed"
                    },
                    justification="Long training time can be significantly reduced with multi-GPU distributed training.",
                    cost_impact=cost_per_gpu_hour * 3 * metrics.get('training_time_hours', 0) / 3.5 * 30,  # Per month
                    performance_impact="3.5x faster training, earlier model deployment",
                    implementation_complexity="High",
                    implementation_steps=[
                        "Implement distributed training (PyTorch DDP)",
                        "Configure multi-GPU instance (4x GPUs)",
                        "Optimize batch size for multi-GPU",
                        "Test scaling efficiency",
                        "Monitor GPU utilization across all devices"
                    ],
                    confidence_score=0.78,
                    priority="medium",
                    estimated_roi_days=7
                )

        elif workload_type == 'inference':
            # Inference benefits from auto-scaling based on request rate
            request_rate = metrics.get('requests_per_second', 0)
            if request_rate > 0:
                instances_needed = int(request_rate / 10) + 1  # Assume 10 req/s per GPU

                if instances_needed != gpu_count:
                    return ScalingRecommendation(
                        strategy=ScalingStrategy.AUTO_SCALING,
                        trigger=ScalingTrigger.REQUEST_RATE,
                        current_config={
                            "gpu_instances": gpu_count,
                            "requests_per_second": request_rate,
                            "auto_scaling": False
                        },
                        recommended_config={
                            "gpu_instances": "auto (1-{})".format(max(instances_needed * 2, 4)),
                            "target_requests_per_gpu": 10,
                            "auto_scaling": True
                        },
                        justification=f"Request rate of {request_rate} req/s requires dynamic GPU scaling. "
                                      "Auto-scaling based on request rate optimizes cost and performance.",
                        cost_impact=-cost_per_gpu_hour * gpu_count * 0.4 * 730,  # 40% savings on average
                        performance_impact="Maintain latency SLA, handle traffic spikes",
                        implementation_complexity="Medium",
                        implementation_steps=[
                            "Containerize inference service",
                            "Deploy on Kubernetes with GPU support",
                            "Configure HPA with custom request rate metric",
                            "Set min=1, max={} GPU pods".format(max(instances_needed * 2, 4)),
                            "Test scaling under various loads"
                        ],
                        auto_scaling_policy={
                            "metric": "requests_per_second_per_gpu",
                            "target_value": 10,
                            "min_capacity": 1,
                            "max_capacity": max(instances_needed * 2, 4),
                            "scale_out_cooldown": 30,
                            "scale_in_cooldown": 120
                        },
                        confidence_score=0.85,
                        priority="high"
                    )

        return None

    def _analyze_spot_instances(
        self,
        metrics: Dict[str, Any],
        cost_constraints: Optional[Dict[str, float]]
    ) -> Optional[ScalingRecommendation]:
        """Recommend spot/preemptible instance usage."""

        workload_type = metrics.get('workload_type', 'unknown')
        fault_tolerance = metrics.get('fault_tolerant', False)
        current_cost_per_hour = metrics.get('cost_per_instance_hour', 1.0)
        instance_count = metrics.get('instance_count', 1)

        # Spot instances good for fault-tolerant batch workloads
        if (workload_type in ['training', 'batch_processing', 'data_processing'] or fault_tolerance):
            spot_discount = 0.7  # Average 70% discount
            monthly_savings = current_cost_per_hour * instance_count * spot_discount * 730

            return ScalingRecommendation(
                strategy=ScalingStrategy.SPOT_INSTANCES,
                trigger=ScalingTrigger.CPU_UTILIZATION,
                current_config={
                    "instance_type": "on-demand",
                    "instance_count": instance_count,
                    "monthly_cost": current_cost_per_hour * instance_count * 730,
                    "interruption_handling": "None"
                },
                recommended_config={
                    "instance_type": "spot/preemptible",
                    "instance_count": instance_count,
                    "monthly_cost": current_cost_per_hour * instance_count * (1 - spot_discount) * 730,
                    "interruption_handling": "Checkpoint & resume",
                    "spot_fallback": "On-demand"
                },
                justification=f"Workload is fault-tolerant. Spot instances provide ~70% cost savings. "
                              f"Implement checkpointing to handle interruptions.",
                cost_impact=-monthly_savings,
                performance_impact="Same performance, potential interruptions handled via checkpointing",
                implementation_complexity="Medium",
                implementation_steps=[
                    "Implement checkpointing in training/batch jobs",
                    "Configure spot instance request",
                    "Set up interruption handler",
                    "Enable fallback to on-demand if spot unavailable",
                    "Test interruption recovery",
                    "Monitor spot pricing and availability"
                ],
                confidence_score=0.80,
                priority="high",
                estimated_roi_days=3
            )

        return None

    def _predictive_scaling_recommendation(
        self,
        historical_data: List[Dict[str, Any]],
        current_metrics: Dict[str, Any]
    ) -> Optional[ScalingRecommendation]:
        """Generate predictive scaling recommendation based on patterns."""

        # Extract time-series data
        timestamps = [d.get('timestamp') for d in historical_data]
        utilizations = [d.get('cpu_utilization', 0) for d in historical_data]

        # Simple pattern detection (can be replaced with ML model)
        hourly_pattern = self._detect_hourly_pattern(timestamps, utilizations)
        weekly_pattern = self._detect_weekly_pattern(timestamps, utilizations)

        if hourly_pattern or weekly_pattern:
            return ScalingRecommendation(
                strategy=ScalingStrategy.PREDICTIVE,
                trigger=ScalingTrigger.PREDICTIVE_ML,
                current_config={
                    "scaling": "reactive",
                    "pattern_detection": False
                },
                recommended_config={
                    "scaling": "predictive",
                    "hourly_pattern": hourly_pattern,
                    "weekly_pattern": weekly_pattern,
                    "forecast_enabled": True
                },
                justification="Detected repeatable usage patterns. Predictive scaling will pre-provision "
                              "capacity before demand increases, reducing latency and improving user experience.",
                cost_impact=-300,  # Reduced over-provisioning
                performance_impact="30% reduction in latency spikes",
                implementation_complexity="High",
                implementation_steps=[
                    "Enable predictive auto-scaling",
                    "Configure pattern detection parameters",
                    "Set forecast horizon based on pattern frequency",
                    "Monitor prediction accuracy",
                    "Adjust forecast parameters based on actuals"
                ],
                confidence_score=0.75,
                priority="medium",
                estimated_roi_days=14
            )

        return None

    def _scheduled_scaling_recommendation(
        self,
        historical_data: Optional[List[Dict[str, Any]]],
        current_metrics: Dict[str, Any]
    ) -> Optional[ScalingRecommendation]:
        """Recommend scheduled scaling for predictable patterns."""

        if not historical_data or len(historical_data) < 168:  # Need 1 week of data
            return None

        # Detect clear day/night or weekday/weekend patterns
        business_hours_util = self._get_business_hours_utilization(historical_data)
        off_hours_util = self._get_off_hours_utilization(historical_data)

        if business_hours_util > off_hours_util * 1.5:
            # Clear pattern - recommend scheduled scaling
            current_instances = current_metrics.get('instance_count', 1)
            off_hours_instances = max(1, int(current_instances * 0.4))
            cost_per_instance = current_metrics.get('cost_per_instance_hour', 1.0)

            # Savings calculation: 16 hours/day * 0.6 reduction * days/month
            monthly_savings = (current_instances - off_hours_instances) * cost_per_instance * 16 * 30

            return ScalingRecommendation(
                strategy=ScalingStrategy.HYBRID,
                trigger=ScalingTrigger.SCHEDULED,
                current_config={
                    "instances_24x7": current_instances,
                    "business_hours_util": business_hours_util,
                    "off_hours_util": off_hours_util
                },
                recommended_config={
                    "instances_business_hours": current_instances,
                    "instances_off_hours": off_hours_instances,
                    "schedule": "Scale down at 6PM, scale up at 8AM"
                },
                justification=f"Usage drops {int((1 - off_hours_util/business_hours_util) * 100)}% during off-hours. "
                              f"Scheduled scaling will reduce capacity when not needed.",
                cost_impact=-monthly_savings,
                performance_impact="No impact - maintains capacity during business hours",
                implementation_complexity="Low",
                implementation_steps=[
                    "Create scheduled scaling actions",
                    f"Scale down to {off_hours_instances} at 6PM weekdays",
                    f"Scale up to {current_instances} at 8AM weekdays",
                    "Keep full capacity on weekends if needed",
                    "Monitor and adjust schedule based on actual usage"
                ],
                auto_scaling_policy={
                    "schedule": [
                        {"time": "0 18 * * 1-5", "min_size": off_hours_instances, "max_size": off_hours_instances},
                        {"time": "0 8 * * 1-5", "min_size": current_instances, "max_size": current_instances * 2}
                    ]
                },
                confidence_score=0.90,
                priority="high",
                estimated_roi_days=1
            )

        return None

    def _calculate_utilization_variance(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate variance in utilization."""
        utilizations = [d.get('cpu_utilization', 0) for d in historical_data]
        return float(np.std(utilizations))

    def _detect_hourly_pattern(self, timestamps: List, utilizations: List) -> Optional[Dict]:
        """Detect hourly usage patterns."""
        # Simplified - can be enhanced with ML
        hourly_avg = {}
        for ts, util in zip(timestamps, utilizations):
            if ts:
                hour = datetime.fromisoformat(ts).hour if isinstance(ts, str) else ts.hour
                if hour not in hourly_avg:
                    hourly_avg[hour] = []
                hourly_avg[hour].append(util)

        if len(hourly_avg) >= 20:  # Significant data
            return {h: np.mean(utils) for h, utils in hourly_avg.items()}
        return None

    def _detect_weekly_pattern(self, timestamps: List, utilizations: List) -> Optional[Dict]:
        """Detect weekly usage patterns."""
        daily_avg = {}
        for ts, util in zip(timestamps, utilizations):
            if ts:
                day = datetime.fromisoformat(ts).weekday() if isinstance(ts, str) else ts.weekday()
                if day not in daily_avg:
                    daily_avg[day] = []
                daily_avg[day].append(util)

        if len(daily_avg) >= 5:
            return {d: np.mean(utils) for d, utils in daily_avg.items()}
        return None

    def _get_business_hours_utilization(self, historical_data: List[Dict[str, Any]]) -> float:
        """Get average utilization during business hours (8AM-6PM)."""
        business_hours_data = []
        for d in historical_data:
            ts = d.get('timestamp')
            if ts:
                hour = datetime.fromisoformat(ts).hour if isinstance(ts, str) else ts.hour
                if 8 <= hour <= 18:
                    business_hours_data.append(d.get('cpu_utilization', 0))

        return np.mean(business_hours_data) if business_hours_data else 50

    def _get_off_hours_utilization(self, historical_data: List[Dict[str, Any]]) -> float:
        """Get average utilization during off hours."""
        off_hours_data = []
        for d in historical_data:
            ts = d.get('timestamp')
            if ts:
                hour = datetime.fromisoformat(ts).hour if isinstance(ts, str) else ts.hour
                if hour < 8 or hour > 18:
                    off_hours_data.append(d.get('cpu_utilization', 0))

        return np.mean(off_hours_data) if off_hours_data else 30
