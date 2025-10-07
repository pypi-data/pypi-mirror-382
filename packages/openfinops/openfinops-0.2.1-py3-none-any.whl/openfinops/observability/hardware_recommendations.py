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
Intelligent Hardware Recommendations for AI/ML Infrastructure
==============================================================

Analyzes workload patterns and provides specific hardware recommendations:
- GPU selection (A100, H100, T4, L4, etc.)
- CPU optimization (instance sizing, ARM vs x86)
- Memory requirements
- Storage configuration
- Network optimization
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class HardwareType(Enum):
    """Hardware component types."""
    GPU = "gpu"
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"


class WorkloadType(Enum):
    """AI/ML workload types."""
    TRAINING = "training"
    INFERENCE = "inference"
    FINE_TUNING = "fine_tuning"
    RAG_PIPELINE = "rag_pipeline"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME_SERVING = "real_time_serving"


@dataclass
class GPUSpec:
    """GPU specification and pricing."""
    name: str
    memory_gb: int
    compute_capability: float
    tensor_cores: bool
    fp16_tflops: float
    fp32_tflops: float
    cost_per_hour_aws: float
    cost_per_hour_gcp: float
    cost_per_hour_azure: float
    best_for: List[WorkloadType]
    characteristics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HardwareRecommendation:
    """Hardware recommendation with justification."""
    hardware_type: HardwareType
    current_config: Dict[str, Any]
    recommended_config: Dict[str, Any]
    justification: str
    estimated_savings: float  # USD per month
    performance_impact: str
    implementation_steps: List[str]
    confidence_score: float
    priority: str  # "critical", "high", "medium", "low"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hardware_type": self.hardware_type.value,
            "current_config": self.current_config,
            "recommended_config": self.recommended_config,
            "justification": self.justification,
            "estimated_savings": self.estimated_savings,
            "performance_impact": self.performance_impact,
            "implementation_steps": self.implementation_steps,
            "confidence_score": self.confidence_score,
            "priority": self.priority,
            "created_at": self.created_at.isoformat()
        }


class HardwareRecommendationEngine:
    """Intelligent hardware recommendation engine."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_hardware_catalog()

    def _initialize_hardware_catalog(self):
        """Initialize hardware specifications catalog."""

        # GPU catalog
        self.gpu_catalog = {
            "nvidia_a100_80gb": GPUSpec(
                name="NVIDIA A100 80GB",
                memory_gb=80,
                compute_capability=8.0,
                tensor_cores=True,
                fp16_tflops=312,
                fp32_tflops=19.5,
                cost_per_hour_aws=4.10,
                cost_per_hour_gcp=3.67,
                cost_per_hour_azure=3.87,
                best_for=[WorkloadType.TRAINING, WorkloadType.FINE_TUNING],
                characteristics={
                    "memory_bandwidth_gb_s": 2039,
                    "nvlink": True,
                    "multi_instance_gpu": True
                }
            ),
            "nvidia_h100_80gb": GPUSpec(
                name="NVIDIA H100 80GB",
                memory_gb=80,
                compute_capability=9.0,
                tensor_cores=True,
                fp16_tflops=1000,
                fp32_tflops=51,
                cost_per_hour_aws=8.20,
                cost_per_hour_gcp=7.45,
                cost_per_hour_azure=7.89,
                best_for=[WorkloadType.TRAINING, WorkloadType.FINE_TUNING],
                characteristics={
                    "memory_bandwidth_gb_s": 3350,
                    "nvlink": True,
                    "transformer_engine": True
                }
            ),
            "nvidia_l4": GPUSpec(
                name="NVIDIA L4",
                memory_gb=24,
                compute_capability=8.9,
                tensor_cores=True,
                fp16_tflops=242,
                fp32_tflops=30,
                cost_per_hour_aws=1.20,
                cost_per_hour_gcp=0.97,
                cost_per_hour_azure=1.12,
                best_for=[WorkloadType.INFERENCE, WorkloadType.REAL_TIME_SERVING],
                characteristics={
                    "memory_bandwidth_gb_s": 300,
                    "power_efficient": True,
                    "video_decode": True
                }
            ),
            "nvidia_t4": GPUSpec(
                name="NVIDIA T4",
                memory_gb=16,
                compute_capability=7.5,
                tensor_cores=True,
                fp16_tflops=65,
                fp32_tflops=8.1,
                cost_per_hour_aws=0.526,
                cost_per_hour_gcp=0.35,
                cost_per_hour_azure=0.45,
                best_for=[WorkloadType.INFERENCE, WorkloadType.BATCH_PROCESSING],
                characteristics={
                    "memory_bandwidth_gb_s": 320,
                    "power_efficient": True,
                    "cost_effective": True
                }
            ),
            "nvidia_v100_32gb": GPUSpec(
                name="NVIDIA V100 32GB",
                memory_gb=32,
                compute_capability=7.0,
                tensor_cores=True,
                fp16_tflops=125,
                fp32_tflops=15.7,
                cost_per_hour_aws=3.06,
                cost_per_hour_gcp=2.48,
                cost_per_hour_azure=2.76,
                best_for=[WorkloadType.TRAINING, WorkloadType.FINE_TUNING],
                characteristics={
                    "memory_bandwidth_gb_s": 900,
                    "nvlink": True,
                    "legacy_support": True
                }
            ),
        }

        # Instance type recommendations
        self.instance_types = {
            "aws": {
                "p4d.24xlarge": {"gpu": "nvidia_a100_80gb", "gpu_count": 8, "vcpu": 96, "memory_gb": 1152},
                "p5.48xlarge": {"gpu": "nvidia_h100_80gb", "gpu_count": 8, "vcpu": 192, "memory_gb": 2048},
                "g5.xlarge": {"gpu": "nvidia_a10g", "gpu_count": 1, "vcpu": 4, "memory_gb": 16},
                "g4dn.xlarge": {"gpu": "nvidia_t4", "gpu_count": 1, "vcpu": 4, "memory_gb": 16},
            },
            "gcp": {
                "a2-highgpu-8g": {"gpu": "nvidia_a100_80gb", "gpu_count": 8, "vcpu": 96, "memory_gb": 680},
                "g2-standard-4": {"gpu": "nvidia_l4", "gpu_count": 1, "vcpu": 4, "memory_gb": 16},
                "n1-standard-4": {"gpu": "nvidia_t4", "gpu_count": 1, "vcpu": 4, "memory_gb": 15},
            },
            "azure": {
                "Standard_ND96asr_v4": {"gpu": "nvidia_a100_80gb", "gpu_count": 8, "vcpu": 96, "memory_gb": 900},
                "Standard_NC4as_T4_v3": {"gpu": "nvidia_t4", "gpu_count": 1, "vcpu": 4, "memory_gb": 28},
            }
        }

    def analyze_workload(
        self,
        workload_metrics: Dict[str, Any],
        workload_type: WorkloadType,
        cloud_provider: str = "aws"
    ) -> List[HardwareRecommendation]:
        """Analyze workload and generate hardware recommendations."""

        recommendations = []

        # GPU recommendations
        gpu_recs = self._analyze_gpu_requirements(workload_metrics, workload_type, cloud_provider)
        recommendations.extend(gpu_recs)

        # CPU recommendations
        cpu_recs = self._analyze_cpu_requirements(workload_metrics, cloud_provider)
        recommendations.extend(cpu_recs)

        # Memory recommendations
        memory_recs = self._analyze_memory_requirements(workload_metrics, cloud_provider)
        recommendations.extend(memory_recs)

        # Storage recommendations
        storage_recs = self._analyze_storage_requirements(workload_metrics, cloud_provider)
        recommendations.extend(storage_recs)

        return recommendations

    def _analyze_gpu_requirements(
        self,
        metrics: Dict[str, Any],
        workload_type: WorkloadType,
        cloud_provider: str
    ) -> List[HardwareRecommendation]:
        """Analyze and recommend optimal GPU configuration."""

        recommendations = []
        current_gpu = metrics.get('current_gpu', 'nvidia_t4')
        gpu_utilization = metrics.get('gpu_utilization', 0)
        gpu_memory_usage = metrics.get('gpu_memory_usage_gb', 0)
        model_size_gb = metrics.get('model_size_gb', 0)
        batch_size = metrics.get('batch_size', 1)
        throughput_tokens_per_sec = metrics.get('throughput_tokens_per_sec', 0)

        # Get current GPU spec
        current_spec = self.gpu_catalog.get(current_gpu)
        if not current_spec:
            return recommendations

        # Analyze GPU utilization
        if gpu_utilization < 30 and workload_type == WorkloadType.INFERENCE:
            # Recommend downgrade to more cost-effective GPU
            recommended_gpu = self._find_cost_effective_gpu(
                required_memory_gb=gpu_memory_usage,
                workload_type=workload_type
            )

            if recommended_gpu and recommended_gpu != current_gpu:
                savings = self._calculate_savings(
                    current_spec,
                    self.gpu_catalog[recommended_gpu],
                    cloud_provider
                )

                recommendations.append(HardwareRecommendation(
                    hardware_type=HardwareType.GPU,
                    current_config={
                        "gpu_model": current_spec.name,
                        "utilization": gpu_utilization,
                        "memory_usage_gb": gpu_memory_usage
                    },
                    recommended_config={
                        "gpu_model": self.gpu_catalog[recommended_gpu].name,
                        "instance_type": self._get_instance_type(recommended_gpu, cloud_provider),
                        "expected_utilization": "60-80%"
                    },
                    justification=f"Current GPU utilization is only {gpu_utilization}%. "
                                  f"{self.gpu_catalog[recommended_gpu].name} provides sufficient capacity "
                                  f"at lower cost.",
                    estimated_savings=savings,
                    performance_impact="Minimal impact on inference latency",
                    implementation_steps=[
                        f"Test workload on {self.gpu_catalog[recommended_gpu].name}",
                        "Verify performance meets SLA requirements",
                        "Migrate production traffic gradually",
                        "Monitor performance metrics for 48 hours"
                    ],
                    confidence_score=0.85,
                    priority="medium"
                ))

        elif gpu_utilization > 85 or gpu_memory_usage > current_spec.memory_gb * 0.9:
            # Recommend upgrade
            recommended_gpu = self._find_high_performance_gpu(
                required_memory_gb=model_size_gb * 1.5,  # Safety margin
                workload_type=workload_type
            )

            if recommended_gpu and recommended_gpu != current_gpu:
                current_cost = self._get_gpu_cost(current_spec, cloud_provider)
                new_cost = self._get_gpu_cost(self.gpu_catalog[recommended_gpu], cloud_provider)

                recommendations.append(HardwareRecommendation(
                    hardware_type=HardwareType.GPU,
                    current_config={
                        "gpu_model": current_spec.name,
                        "utilization": gpu_utilization,
                        "memory_usage_gb": gpu_memory_usage,
                        "bottleneck": "GPU capacity"
                    },
                    recommended_config={
                        "gpu_model": self.gpu_catalog[recommended_gpu].name,
                        "instance_type": self._get_instance_type(recommended_gpu, cloud_provider),
                        "expected_improvement": "2-3x throughput"
                    },
                    justification=f"GPU is at capacity ({gpu_utilization}% utilization). "
                                  f"Upgrading to {self.gpu_catalog[recommended_gpu].name} will eliminate "
                                  f"bottleneck and improve throughput.",
                    estimated_savings=-(new_cost - current_cost) * 730,  # Negative = cost increase
                    performance_impact="2-3x improvement in training/inference speed",
                    implementation_steps=[
                        f"Provision {self.gpu_catalog[recommended_gpu].name} instance",
                        "Optimize model for new hardware",
                        "Run benchmark tests",
                        "Deploy with gradual traffic migration"
                    ],
                    confidence_score=0.90,
                    priority="high"
                ))

        # Check for multi-GPU opportunities
        if workload_type == WorkloadType.TRAINING and model_size_gb > 40:
            multi_gpu_rec = self._analyze_multi_gpu_setup(metrics, cloud_provider)
            if multi_gpu_rec:
                recommendations.append(multi_gpu_rec)

        return recommendations

    def _analyze_cpu_requirements(
        self,
        metrics: Dict[str, Any],
        cloud_provider: str
    ) -> List[HardwareRecommendation]:
        """Analyze CPU requirements and recommendations."""

        recommendations = []
        cpu_utilization = metrics.get('cpu_utilization', 0)
        current_vcpus = metrics.get('vcpus', 4)

        if cpu_utilization < 20:
            # Downsize CPU
            recommended_vcpus = max(2, current_vcpus // 2)
            savings_per_hour = (current_vcpus - recommended_vcpus) * 0.05  # Approximate

            recommendations.append(HardwareRecommendation(
                hardware_type=HardwareType.CPU,
                current_config={
                    "vcpus": current_vcpus,
                    "utilization": cpu_utilization
                },
                recommended_config={
                    "vcpus": recommended_vcpus,
                    "instance_type": "Smaller CPU instance"
                },
                justification=f"CPU utilization is {cpu_utilization}%. Reducing vCPUs saves costs.",
                estimated_savings=savings_per_hour * 730,
                performance_impact="No performance impact",
                implementation_steps=[
                    "Test with reduced vCPUs",
                    "Update instance configuration",
                    "Monitor application performance"
                ],
                confidence_score=0.80,
                priority="medium"
            ))

        elif cpu_utilization > 80:
            # Upsize CPU
            recommended_vcpus = current_vcpus * 2
            cost_increase = (recommended_vcpus - current_vcpus) * 0.05 * 730

            recommendations.append(HardwareRecommendation(
                hardware_type=HardwareType.CPU,
                current_config={
                    "vcpus": current_vcpus,
                    "utilization": cpu_utilization,
                    "bottleneck": True
                },
                recommended_config={
                    "vcpus": recommended_vcpus,
                    "instance_type": "Larger CPU instance"
                },
                justification=f"CPU is bottleneck at {cpu_utilization}%. Increase capacity.",
                estimated_savings=-cost_increase,
                performance_impact="Eliminate CPU bottleneck, improve throughput",
                implementation_steps=[
                    "Upgrade to larger instance type",
                    "Optimize CPU-bound operations",
                    "Monitor performance improvements"
                ],
                confidence_score=0.85,
                priority="high"
            ))

        return recommendations

    def _analyze_memory_requirements(
        self,
        metrics: Dict[str, Any],
        cloud_provider: str
    ) -> List[HardwareRecommendation]:
        """Analyze memory requirements."""

        recommendations = []
        memory_usage_gb = metrics.get('memory_usage_gb', 0)
        total_memory_gb = metrics.get('total_memory_gb', 16)
        memory_utilization = (memory_usage_gb / total_memory_gb * 100) if total_memory_gb > 0 else 0

        if memory_utilization > 85:
            recommended_memory = total_memory_gb * 1.5

            recommendations.append(HardwareRecommendation(
                hardware_type=HardwareType.MEMORY,
                current_config={
                    "total_gb": total_memory_gb,
                    "usage_gb": memory_usage_gb,
                    "utilization": memory_utilization
                },
                recommended_config={
                    "total_gb": recommended_memory,
                    "target_utilization": "60-70%"
                },
                justification=f"Memory usage at {memory_utilization:.1f}%. Risk of OOM errors.",
                estimated_savings=-200,  # Approximate cost increase
                performance_impact="Prevent OOM errors, enable larger batch sizes",
                implementation_steps=[
                    "Upgrade to memory-optimized instance",
                    "Increase batch size for better GPU utilization",
                    "Monitor memory patterns"
                ],
                confidence_score=0.88,
                priority="high"
            ))

        return recommendations

    def _analyze_storage_requirements(
        self,
        metrics: Dict[str, Any],
        cloud_provider: str
    ) -> List[HardwareRecommendation]:
        """Analyze storage requirements."""

        recommendations = []
        storage_type = metrics.get('storage_type', 'gp3')
        iops = metrics.get('iops', 3000)
        throughput_mb_s = metrics.get('throughput_mb_s', 125)
        data_size_tb = metrics.get('data_size_tb', 1)

        # Check if workload needs faster storage
        if metrics.get('io_wait_percent', 0) > 20:
            recommendations.append(HardwareRecommendation(
                hardware_type=HardwareType.STORAGE,
                current_config={
                    "type": storage_type,
                    "iops": iops,
                    "throughput_mb_s": throughput_mb_s,
                    "io_wait": metrics.get('io_wait_percent')
                },
                recommended_config={
                    "type": "io2" if cloud_provider == "aws" else "premium_ssd",
                    "iops": iops * 2,
                    "throughput_mb_s": throughput_mb_s * 2
                },
                justification="High I/O wait times detected. Faster storage will improve training speed.",
                estimated_savings=-100 * data_size_tb,  # Cost increase
                performance_impact="20-30% improvement in data loading",
                implementation_steps=[
                    "Upgrade to high-performance SSD",
                    "Enable storage caching",
                    "Optimize data loading pipeline"
                ],
                confidence_score=0.82,
                priority="medium"
            ))

        return recommendations

    def _find_cost_effective_gpu(
        self,
        required_memory_gb: float,
        workload_type: WorkloadType
    ) -> Optional[str]:
        """Find most cost-effective GPU meeting requirements."""

        candidates = []
        for gpu_id, spec in self.gpu_catalog.items():
            if (spec.memory_gb >= required_memory_gb and
                workload_type in spec.best_for):
                candidates.append((gpu_id, spec.cost_per_hour_aws))

        if candidates:
            return min(candidates, key=lambda x: x[1])[0]
        return None

    def _find_high_performance_gpu(
        self,
        required_memory_gb: float,
        workload_type: WorkloadType
    ) -> Optional[str]:
        """Find highest performance GPU for workload."""

        candidates = []
        for gpu_id, spec in self.gpu_catalog.items():
            if (spec.memory_gb >= required_memory_gb and
                workload_type in spec.best_for):
                candidates.append((gpu_id, spec.fp16_tflops))

        if candidates:
            return max(candidates, key=lambda x: x[1])[0]
        return None

    def _calculate_savings(
        self,
        current_gpu: GPUSpec,
        recommended_gpu: GPUSpec,
        cloud_provider: str
    ) -> float:
        """Calculate monthly savings."""

        current_cost = self._get_gpu_cost(current_gpu, cloud_provider)
        new_cost = self._get_gpu_cost(recommended_gpu, cloud_provider)
        return (current_cost - new_cost) * 730  # Hours per month

    def _get_gpu_cost(self, gpu_spec: GPUSpec, cloud_provider: str) -> float:
        """Get GPU cost per hour for cloud provider."""

        if cloud_provider == "aws":
            return gpu_spec.cost_per_hour_aws
        elif cloud_provider == "gcp":
            return gpu_spec.cost_per_hour_gcp
        elif cloud_provider == "azure":
            return gpu_spec.cost_per_hour_azure
        return gpu_spec.cost_per_hour_aws

    def _get_instance_type(self, gpu_id: str, cloud_provider: str) -> str:
        """Get recommended instance type."""

        for instance, config in self.instance_types.get(cloud_provider, {}).items():
            if config.get('gpu') == gpu_id:
                return instance
        return "Custom instance"

    def _analyze_multi_gpu_setup(
        self,
        metrics: Dict[str, Any],
        cloud_provider: str
    ) -> Optional[HardwareRecommendation]:
        """Analyze if multi-GPU setup would be beneficial."""

        model_size_gb = metrics.get('model_size_gb', 0)
        current_training_time_hours = metrics.get('training_time_hours', 0)

        if model_size_gb > 40 and current_training_time_hours > 24:
            return HardwareRecommendation(
                hardware_type=HardwareType.GPU,
                current_config={
                    "setup": "Single GPU",
                    "training_time_hours": current_training_time_hours,
                    "model_size_gb": model_size_gb
                },
                recommended_config={
                    "setup": "Multi-GPU (4-8 GPUs)",
                    "estimated_training_time_hours": current_training_time_hours / 4,
                    "data_parallelism": "Enabled"
                },
                justification=f"Large model ({model_size_gb}GB) with long training time. "
                              "Multi-GPU setup will significantly reduce training duration.",
                estimated_savings=0,  # Time savings, not cost
                performance_impact="4x faster training with 4 GPUs",
                implementation_steps=[
                    "Implement distributed training (PyTorch DDP or DeepSpeed)",
                    "Configure multi-GPU instance",
                    "Optimize gradient synchronization",
                    "Test scaling efficiency"
                ],
                confidence_score=0.88,
                priority="high"
            )
        return None
