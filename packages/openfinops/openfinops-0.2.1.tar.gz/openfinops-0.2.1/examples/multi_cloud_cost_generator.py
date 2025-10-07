#!/usr/bin/env python3
"""
Multi-Cloud Model Cost Attribution Mock Data Generator
=====================================================

Generates realistic mock data for model cost attribution across multiple cloud providers
with different pricing models, resource types, and regional variations.

This script creates comprehensive test data for:
- AWS, GCP, Azure, and on-premise deployments
- Different model types and sizes
- Realistic cost patterns and usage scenarios
- Build vs production phase costs
- Resource optimization opportunities
"""

import json
import time
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import math

# Mock cloud provider pricing (realistic approximations)
CLOUD_PRICING = {
    "aws": {
        "regions": {
            "us-west-2": {"multiplier": 1.0, "name": "Oregon"},
            "us-east-1": {"multiplier": 0.95, "name": "N. Virginia"},
            "eu-west-1": {"multiplier": 1.12, "name": "Ireland"},
            "ap-northeast-1": {"multiplier": 1.18, "name": "Tokyo"}
        },
        "gpu_instances": {
            "p3.2xlarge": {"vcpu": 8, "memory": 61, "gpu": "V100", "hourly": 3.06},
            "p3.8xlarge": {"vcpu": 32, "memory": 244, "gpu": "4xV100", "hourly": 12.24},
            "p4d.xlarge": {"vcpu": 4, "memory": 16, "gpu": "A100", "hourly": 4.50},
            "g4dn.xlarge": {"vcpu": 4, "memory": 16, "gpu": "T4", "hourly": 1.25}
        },
        "cpu_instances": {
            "c5.large": {"vcpu": 2, "memory": 4, "hourly": 0.085},
            "c5.xlarge": {"vcpu": 4, "memory": 8, "hourly": 0.17},
            "c5.2xlarge": {"vcpu": 8, "memory": 16, "hourly": 0.34}
        },
        "storage": {
            "gp3": 0.08,  # per GB-month
            "gp2": 0.10,
            "io2": 0.125,
            "s3_standard": 0.023
        },
        "network": {
            "data_transfer_out": 0.09,  # per GB
            "data_transfer_in": 0.0
        }
    },
    "gcp": {
        "regions": {
            "us-west1": {"multiplier": 1.0, "name": "Oregon"},
            "us-central1": {"multiplier": 0.95, "name": "Iowa"},
            "europe-west1": {"multiplier": 1.15, "name": "Belgium"},
            "asia-northeast1": {"multiplier": 1.20, "name": "Tokyo"}
        },
        "gpu_instances": {
            "n1-standard-4-k80": {"vcpu": 4, "memory": 15, "gpu": "K80", "hourly": 1.95},
            "n1-standard-8-v100": {"vcpu": 8, "memory": 30, "gpu": "V100", "hourly": 2.85},
            "a2-highgpu-1g": {"vcpu": 12, "memory": 85, "gpu": "A100", "hourly": 4.20},
            "n1-standard-4-t4": {"vcpu": 4, "memory": 15, "gpu": "T4", "hourly": 1.12}
        },
        "cpu_instances": {
            "n1-standard-2": {"vcpu": 2, "memory": 7.5, "hourly": 0.095},
            "n1-standard-4": {"vcpu": 4, "memory": 15, "hourly": 0.19},
            "n1-standard-8": {"vcpu": 8, "memory": 30, "hourly": 0.38}
        },
        "storage": {
            "pd-standard": 0.04,
            "pd-ssd": 0.17,
            "pd-extreme": 0.65,
            "cloud_storage": 0.020
        },
        "network": {
            "data_transfer_out": 0.12,
            "data_transfer_in": 0.0
        }
    },
    "azure": {
        "regions": {
            "westus2": {"multiplier": 1.0, "name": "West US 2"},
            "eastus": {"multiplier": 0.93, "name": "East US"},
            "westeurope": {"multiplier": 1.16, "name": "West Europe"},
            "japaneast": {"multiplier": 1.22, "name": "Japan East"}
        },
        "gpu_instances": {
            "Standard_NC6": {"vcpu": 6, "memory": 56, "gpu": "K80", "hourly": 1.80},
            "Standard_NC12": {"vcpu": 12, "memory": 112, "gpu": "2xK80", "hourly": 3.60},
            "Standard_NC24": {"vcpu": 24, "memory": 224, "gpu": "4xK80", "hourly": 7.20},
            "Standard_ND40rs_v2": {"vcpu": 40, "memory": 672, "gpu": "8xV100", "hourly": 22.80}
        },
        "cpu_instances": {
            "Standard_D2s_v3": {"vcpu": 2, "memory": 8, "hourly": 0.096},
            "Standard_D4s_v3": {"vcpu": 4, "memory": 16, "hourly": 0.192},
            "Standard_D8s_v3": {"vcpu": 8, "memory": 32, "hourly": 0.384}
        },
        "storage": {
            "premium_ssd": 0.15,
            "standard_ssd": 0.075,
            "standard_hdd": 0.045,
            "blob_storage": 0.018
        },
        "network": {
            "data_transfer_out": 0.087,
            "data_transfer_in": 0.0
        }
    },
    "on_premise": {
        "regions": {
            "datacenter_1": {"multiplier": 0.70, "name": "Primary DC"},
            "datacenter_2": {"multiplier": 0.75, "name": "Secondary DC"},
            "edge_location": {"multiplier": 0.85, "name": "Edge Computing"}
        },
        "gpu_instances": {
            "dgx_a100": {"vcpu": 128, "memory": 2048, "gpu": "8xA100", "hourly": 15.00},
            "custom_v100": {"vcpu": 32, "memory": 256, "gpu": "4xV100", "hourly": 8.00},
            "custom_rtx": {"vcpu": 16, "memory": 64, "gpu": "2xRTX", "hourly": 3.50}
        },
        "cpu_instances": {
            "standard_server": {"vcpu": 16, "memory": 64, "hourly": 0.50},
            "high_memory": {"vcpu": 32, "memory": 256, "hourly": 1.20},
            "compute_optimized": {"vcpu": 64, "memory": 128, "hourly": 1.80}
        },
        "storage": {
            "nvme_ssd": 0.05,
            "sas_ssd": 0.03,
            "nas_storage": 0.02
        },
        "network": {
            "data_transfer_out": 0.01,
            "data_transfer_in": 0.0
        }
    }
}

# Model scenarios with different characteristics
MODEL_SCENARIOS = {
    "enterprise_llm": {
        "name": "Enterprise LLM Assistant",
        "type": "transformer",
        "size": "175B",
        "development_days": 90,
        "training_gpu_hours": 2400,
        "preferred_gpu": "A100",
        "production_requests_daily": 100000,
        "model_complexity": "high",
        "data_size_gb": 5000
    },
    "fraud_detection": {
        "name": "Real-time Fraud Detection",
        "type": "ensemble",
        "size": "ensemble",
        "development_days": 45,
        "training_gpu_hours": 240,
        "preferred_gpu": "V100",
        "production_requests_daily": 50000,
        "model_complexity": "medium",
        "data_size_gb": 800
    },
    "recommendation_engine": {
        "name": "Personalization Engine",
        "type": "deep_learning",
        "size": "1.5B",
        "development_days": 60,
        "training_gpu_hours": 480,
        "preferred_gpu": "V100",
        "production_requests_daily": 200000,
        "model_complexity": "medium",
        "data_size_gb": 1200
    },
    "computer_vision": {
        "name": "Computer Vision Classifier",
        "type": "cnn",
        "size": "ResNet-152",
        "development_days": 30,
        "training_gpu_hours": 120,
        "preferred_gpu": "T4",
        "production_requests_daily": 25000,
        "model_complexity": "low",
        "data_size_gb": 300
    },
    "nlp_sentiment": {
        "name": "Sentiment Analysis Model",
        "type": "bert",
        "size": "BERT-Large",
        "development_days": 25,
        "training_gpu_hours": 80,
        "preferred_gpu": "T4",
        "production_requests_daily": 75000,
        "model_complexity": "low",
        "data_size_gb": 150
    },
    "speech_recognition": {
        "name": "Speech-to-Text Engine",
        "type": "transformer",
        "size": "Whisper-Large",
        "development_days": 50,
        "training_gpu_hours": 360,
        "preferred_gpu": "V100",
        "production_requests_daily": 30000,
        "model_complexity": "medium",
        "data_size_gb": 2000
    }
}

class MultiCloudCostGenerator:
    """Generate realistic multi-cloud model cost attribution data"""

    def __init__(self):
        self.current_time = time.time()
        self.generated_data = {
            "models": [],
            "cost_entries": [],
            "configurations": {},
            "summary_stats": {},
            "generation_metadata": {
                "timestamp": self.current_time,
                "total_models": 0,
                "total_cost_entries": 0,
                "clouds_covered": list(CLOUD_PRICING.keys()),
                "time_span_days": 120
            }
        }

    def generate_complete_dataset(self) -> Dict[str, Any]:
        """Generate complete multi-cloud cost attribution dataset"""
        print("🌐 Generating Multi-Cloud Model Cost Attribution Dataset...")
        print("=" * 60)

        # Generate models across different cloud providers
        self._generate_multi_cloud_models()

        # Generate cost data with realistic patterns
        self._generate_cost_data()

        # Calculate summary statistics
        self._calculate_summary_stats()

        # Generate cloud comparison data
        self._generate_cloud_comparisons()

        print(f"\n✅ Generated complete dataset:")
        print(f"   📊 Models: {len(self.generated_data['models'])}")
        print(f"   💰 Cost Entries: {len(self.generated_data['cost_entries'])}")
        print(f"   ☁️  Cloud Providers: {len(CLOUD_PRICING)}")
        print(f"   📈 Total Simulated Cost: ${self.generated_data['summary_stats']['total_cost']:,.2f}")

        return self.generated_data

    def _generate_multi_cloud_models(self):
        """Generate models distributed across cloud providers"""
        print("🤖 Generating models across cloud providers...")

        model_count = 0
        for scenario_key, scenario in MODEL_SCENARIOS.items():
            # Create multiple versions of each model type across different clouds
            for cloud in CLOUD_PRICING.keys():
                for region in list(CLOUD_PRICING[cloud]["regions"].keys())[:2]:  # Use 2 regions per cloud
                    model_id = f"{scenario_key}_{cloud}_{region}_{uuid.uuid4().hex[:8]}"

                    model_data = {
                        "model_id": model_id,
                        "model_name": f"{scenario['name']} ({cloud.upper()})",
                        "model_version": f"v{random.randint(1,5)}.{random.randint(0,9)}",
                        "model_type": scenario["type"],
                        "size_description": scenario["size"],
                        "owner": f"{cloud}-team",
                        "project_id": f"{scenario_key.replace('_', '-')}-{cloud}",
                        "cloud_provider": cloud,
                        "primary_region": region,
                        "created_at": self.current_time - random.randint(30, 120) * 24 * 3600,
                        "scenario": scenario,
                        "tags": {
                            "environment": random.choice(["production", "staging", "development"]),
                            "team": f"{cloud}-ml-team",
                            "cost_center": f"ai-{cloud}",
                            "model_family": scenario["type"]
                        }
                    }

                    self.generated_data["models"].append(model_data)
                    model_count += 1

        self.generated_data["generation_metadata"]["total_models"] = model_count
        print(f"   ✅ Generated {model_count} models across {len(CLOUD_PRICING)} cloud providers")

    def _generate_cost_data(self):
        """Generate realistic cost data for all models"""
        print("💰 Generating cost data across model lifecycles...")

        total_entries = 0

        for model in self.generated_data["models"]:
            model_id = model["model_id"]
            cloud = model["cloud_provider"]
            region = model["primary_region"]
            scenario = model["scenario"]

            # Generate development phase costs
            dev_entries = self._generate_development_costs(model_id, cloud, region, scenario)
            total_entries += len(dev_entries)

            # Generate training phase costs
            training_entries = self._generate_training_costs(model_id, cloud, region, scenario)
            total_entries += len(training_entries)

            # Generate production phase costs
            production_entries = self._generate_production_costs(model_id, cloud, region, scenario)
            total_entries += len(production_entries)

            # Add some monitoring and maintenance costs
            monitoring_entries = self._generate_monitoring_costs(model_id, cloud, region, scenario)
            total_entries += len(monitoring_entries)

        self.generated_data["generation_metadata"]["total_cost_entries"] = total_entries
        print(f"   ✅ Generated {total_entries} cost entries across all phases")

    def _generate_development_costs(self, model_id: str, cloud: str, region: str, scenario: Dict) -> List[Dict]:
        """Generate development phase costs"""
        entries = []
        dev_days = scenario["development_days"]
        start_time = self.current_time - (dev_days + 60) * 24 * 3600

        # CPU costs for development
        cpu_instance = self._select_cpu_instance(cloud, "development")
        daily_cpu_hours = random.uniform(8, 16)  # Development hours per day

        for day in range(dev_days):
            timestamp = start_time + day * 24 * 3600

            # Add some randomness to daily usage
            actual_hours = daily_cpu_hours * random.uniform(0.7, 1.3)
            base_cost = CLOUD_PRICING[cloud]["cpu_instances"][cpu_instance]["hourly"]
            regional_multiplier = CLOUD_PRICING[cloud]["regions"][region]["multiplier"]
            cost = actual_hours * base_cost * regional_multiplier

            entry = {
                "entry_id": str(uuid.uuid4()),
                "model_id": model_id,
                "phase": "development",
                "resource_type": "compute_cpu",
                "cloud_provider": cloud,
                "region": region,
                "instance_type": cpu_instance,
                "usage_amount": actual_hours,
                "unit_cost": base_cost * regional_multiplier,
                "total_cost": cost,
                "timestamp": timestamp,
                "metadata": {
                    "development_activity": random.choice([
                        "data_exploration", "model_design", "prototyping",
                        "feature_engineering", "testing"
                    ]),
                    "team_size": random.randint(2, 5)
                }
            }
            entries.append(entry)

            # Storage costs for development data
            storage_gb = scenario["data_size_gb"] * 0.1  # Use 10% of full dataset for dev
            storage_type = list(CLOUD_PRICING[cloud]["storage"].keys())[1]  # Use second storage type
            storage_cost_per_gb = CLOUD_PRICING[cloud]["storage"][storage_type] / 30  # Daily cost
            storage_cost = storage_gb * storage_cost_per_gb * regional_multiplier

            storage_entry = {
                "entry_id": str(uuid.uuid4()),
                "model_id": model_id,
                "phase": "development",
                "resource_type": "storage_ssd",
                "cloud_provider": cloud,
                "region": region,
                "usage_amount": storage_gb,
                "unit_cost": storage_cost_per_gb * regional_multiplier,
                "total_cost": storage_cost,
                "timestamp": timestamp,
                "metadata": {
                    "storage_type": storage_type,
                    "data_type": "development_dataset"
                }
            }
            entries.append(storage_entry)

        self.generated_data["cost_entries"].extend(entries)
        return entries

    def _generate_training_costs(self, model_id: str, cloud: str, region: str, scenario: Dict) -> List[Dict]:
        """Generate training phase costs"""
        entries = []
        total_gpu_hours = scenario["training_gpu_hours"]
        training_start = self.current_time - 45 * 24 * 3600

        # Select appropriate GPU instance
        gpu_instance = self._select_gpu_instance(cloud, scenario["preferred_gpu"])

        # Distribute training over multiple days
        training_days = max(5, total_gpu_hours // 24)
        hours_per_day = total_gpu_hours / training_days

        for day in range(int(training_days)):
            timestamp = training_start + day * 24 * 3600

            # Add variation to daily training hours
            actual_hours = hours_per_day * random.uniform(0.8, 1.2)
            base_cost = CLOUD_PRICING[cloud]["gpu_instances"][gpu_instance]["hourly"]
            regional_multiplier = CLOUD_PRICING[cloud]["regions"][region]["multiplier"]

            # Apply volume discounting for large training runs
            volume_discount = self._calculate_volume_discount(total_gpu_hours)
            cost = actual_hours * base_cost * regional_multiplier * (1 - volume_discount)

            entry = {
                "entry_id": str(uuid.uuid4()),
                "model_id": model_id,
                "phase": "training",
                "resource_type": "compute_gpu",
                "cloud_provider": cloud,
                "region": region,
                "instance_type": gpu_instance,
                "usage_amount": actual_hours,
                "unit_cost": base_cost * regional_multiplier,
                "total_cost": cost,
                "timestamp": timestamp,
                "metadata": {
                    "volume_discount_applied": volume_discount,
                    "training_step": f"epoch_{day+1}",
                    "gpu_type": CLOUD_PRICING[cloud]["gpu_instances"][gpu_instance]["gpu"]
                }
            }
            entries.append(entry)

            # Training data storage costs
            storage_gb = scenario["data_size_gb"]
            storage_type = list(CLOUD_PRICING[cloud]["storage"].keys())[0]  # Use fastest storage
            storage_cost_per_gb = CLOUD_PRICING[cloud]["storage"][storage_type] / 30
            storage_cost = storage_gb * storage_cost_per_gb * regional_multiplier

            storage_entry = {
                "entry_id": str(uuid.uuid4()),
                "model_id": model_id,
                "phase": "training",
                "resource_type": "storage_ssd",
                "cloud_provider": cloud,
                "region": region,
                "usage_amount": storage_gb,
                "unit_cost": storage_cost_per_gb * regional_multiplier,
                "total_cost": storage_cost,
                "timestamp": timestamp,
                "metadata": {
                    "storage_type": storage_type,
                    "data_type": "training_dataset"
                }
            }
            entries.append(storage_entry)

        self.generated_data["cost_entries"].extend(entries)
        return entries

    def _generate_production_costs(self, model_id: str, cloud: str, region: str, scenario: Dict) -> List[Dict]:
        """Generate production phase costs"""
        entries = []
        production_start = self.current_time - 30 * 24 * 3600  # Last 30 days
        daily_requests = scenario["production_requests_daily"]

        # Cost per inference request (varies by cloud and complexity)
        base_inference_cost = self._calculate_inference_cost(cloud, scenario["model_complexity"])

        for day in range(30):
            timestamp = production_start + day * 24 * 3600

            # Add daily variation to request volume
            actual_requests = daily_requests * random.uniform(0.7, 1.4)

            # Weekend effects (lower usage on weekends)
            day_of_week = (day % 7)
            if day_of_week >= 5:  # Weekend
                actual_requests *= 0.6

            regional_multiplier = CLOUD_PRICING[cloud]["regions"][region]["multiplier"]
            inference_cost = actual_requests * base_inference_cost * regional_multiplier

            entry = {
                "entry_id": str(uuid.uuid4()),
                "model_id": model_id,
                "phase": "production",
                "resource_type": "inference_request",
                "cloud_provider": cloud,
                "region": region,
                "usage_amount": actual_requests,
                "unit_cost": base_inference_cost * regional_multiplier,
                "total_cost": inference_cost,
                "timestamp": timestamp,
                "metadata": {
                    "day_of_week": day_of_week,
                    "request_pattern": "weekend" if day_of_week >= 5 else "weekday"
                }
            }
            entries.append(entry)

            # CPU serving costs
            cpu_instance = self._select_cpu_instance(cloud, "production")
            serving_hours = 24  # Always-on serving
            cpu_cost = (serving_hours *
                       CLOUD_PRICING[cloud]["cpu_instances"][cpu_instance]["hourly"] *
                       regional_multiplier)

            cpu_entry = {
                "entry_id": str(uuid.uuid4()),
                "model_id": model_id,
                "phase": "production",
                "resource_type": "compute_cpu",
                "cloud_provider": cloud,
                "region": region,
                "instance_type": cpu_instance,
                "usage_amount": serving_hours,
                "unit_cost": CLOUD_PRICING[cloud]["cpu_instances"][cpu_instance]["hourly"] * regional_multiplier,
                "total_cost": cpu_cost,
                "timestamp": timestamp,
                "metadata": {
                    "service_type": "model_serving",
                    "availability": "24x7"
                }
            }
            entries.append(cpu_entry)

            # Data transfer costs
            data_transfer_gb = actual_requests * 0.001  # Assume 1KB per request
            transfer_cost = (data_transfer_gb *
                           CLOUD_PRICING[cloud]["network"]["data_transfer_out"] *
                           regional_multiplier)

            if transfer_cost > 0:
                transfer_entry = {
                    "entry_id": str(uuid.uuid4()),
                    "model_id": model_id,
                    "phase": "production",
                    "resource_type": "network_egress",
                    "cloud_provider": cloud,
                    "region": region,
                    "usage_amount": data_transfer_gb,
                    "unit_cost": CLOUD_PRICING[cloud]["network"]["data_transfer_out"] * regional_multiplier,
                    "total_cost": transfer_cost,
                    "timestamp": timestamp,
                    "metadata": {
                        "transfer_type": "model_responses"
                    }
                }
                entries.append(transfer_entry)

        self.generated_data["cost_entries"].extend(entries)
        return entries

    def _generate_monitoring_costs(self, model_id: str, cloud: str, region: str, scenario: Dict) -> List[Dict]:
        """Generate monitoring and maintenance costs"""
        entries = []
        monitoring_start = self.current_time - 30 * 24 * 3600

        for day in range(30):
            timestamp = monitoring_start + day * 24 * 3600

            # Monitoring infrastructure costs
            monitoring_hours = random.uniform(2, 6)  # Variable monitoring activity
            cpu_instance = self._select_cpu_instance(cloud, "monitoring")
            regional_multiplier = CLOUD_PRICING[cloud]["regions"][region]["multiplier"]

            monitoring_cost = (monitoring_hours *
                             CLOUD_PRICING[cloud]["cpu_instances"][cpu_instance]["hourly"] *
                             regional_multiplier)

            entry = {
                "entry_id": str(uuid.uuid4()),
                "model_id": model_id,
                "phase": "monitoring",
                "resource_type": "compute_cpu",
                "cloud_provider": cloud,
                "region": region,
                "instance_type": cpu_instance,
                "usage_amount": monitoring_hours,
                "unit_cost": CLOUD_PRICING[cloud]["cpu_instances"][cpu_instance]["hourly"] * regional_multiplier,
                "total_cost": monitoring_cost,
                "timestamp": timestamp,
                "metadata": {
                    "monitoring_type": random.choice([
                        "performance_tracking", "data_drift_detection",
                        "model_health_check", "business_metrics"
                    ])
                }
            }
            entries.append(entry)

        self.generated_data["cost_entries"].extend(entries)
        return entries

    def _select_gpu_instance(self, cloud: str, preferred_gpu: str) -> str:
        """Select appropriate GPU instance based on preference"""
        gpu_instances = CLOUD_PRICING[cloud]["gpu_instances"]

        # Try to match preferred GPU type
        for instance, specs in gpu_instances.items():
            if preferred_gpu.lower() in specs["gpu"].lower():
                return instance

        # Fall back to first available GPU instance
        return list(gpu_instances.keys())[0]

    def _select_cpu_instance(self, cloud: str, workload_type: str) -> str:
        """Select appropriate CPU instance based on workload"""
        cpu_instances = list(CLOUD_PRICING[cloud]["cpu_instances"].keys())

        if workload_type == "development":
            return cpu_instances[0]  # Smallest instance
        elif workload_type == "production":
            return cpu_instances[-1]  # Largest instance
        else:
            return cpu_instances[len(cpu_instances)//2]  # Medium instance

    def _calculate_volume_discount(self, total_hours: float) -> float:
        """Calculate volume discount based on usage"""
        if total_hours >= 1000:
            return 0.25  # 25% discount
        elif total_hours >= 500:
            return 0.15  # 15% discount
        elif total_hours >= 100:
            return 0.08  # 8% discount
        else:
            return 0.0   # No discount

    def _calculate_inference_cost(self, cloud: str, complexity: str) -> float:
        """Calculate cost per inference request based on complexity"""
        base_costs = {
            "aws": {"low": 0.0001, "medium": 0.00025, "high": 0.0005},
            "gcp": {"low": 0.00012, "medium": 0.0003, "high": 0.0006},
            "azure": {"low": 0.00015, "medium": 0.00035, "high": 0.0007},
            "on_premise": {"low": 0.00005, "medium": 0.00015, "high": 0.0003}
        }

        return base_costs[cloud][complexity]

    def _calculate_summary_stats(self):
        """Calculate summary statistics for the generated data"""
        print("📊 Calculating summary statistics...")

        total_cost = sum(entry["total_cost"] for entry in self.generated_data["cost_entries"])

        # Cost by cloud provider
        cost_by_cloud = {}
        cost_by_phase = {}
        cost_by_resource = {}

        for entry in self.generated_data["cost_entries"]:
            cloud = entry["cloud_provider"]
            phase = entry["phase"]
            resource = entry["resource_type"]
            cost = entry["total_cost"]

            cost_by_cloud[cloud] = cost_by_cloud.get(cloud, 0) + cost
            cost_by_phase[phase] = cost_by_phase.get(phase, 0) + cost
            cost_by_resource[resource] = cost_by_resource.get(resource, 0) + cost

        # Build vs Production analysis
        build_phases = ["development", "training", "validation", "deployment_prep"]
        production_phases = ["production", "monitoring", "retraining"]

        build_cost = sum(cost_by_phase.get(phase, 0) for phase in build_phases)
        production_cost = sum(cost_by_phase.get(phase, 0) for phase in production_phases)

        self.generated_data["summary_stats"] = {
            "total_cost": total_cost,
            "cost_by_cloud": cost_by_cloud,
            "cost_by_phase": cost_by_phase,
            "cost_by_resource": cost_by_resource,
            "build_vs_production": {
                "build_cost": build_cost,
                "production_cost": production_cost,
                "build_percentage": (build_cost / total_cost * 100) if total_cost > 0 else 0,
                "production_percentage": (production_cost / total_cost * 100) if total_cost > 0 else 0
            },
            "average_cost_per_model": total_cost / len(self.generated_data["models"]) if self.generated_data["models"] else 0
        }

    def _generate_cloud_comparisons(self):
        """Generate cloud provider comparison data"""
        print("☁️  Generating cloud provider comparisons...")

        comparisons = {}

        for cloud in CLOUD_PRICING.keys():
            cloud_entries = [e for e in self.generated_data["cost_entries"] if e["cloud_provider"] == cloud]
            cloud_models = [m for m in self.generated_data["models"] if m["cloud_provider"] == cloud]

            total_cost = sum(entry["total_cost"] for entry in cloud_entries)

            comparisons[cloud] = {
                "total_cost": total_cost,
                "model_count": len(cloud_models),
                "average_cost_per_model": total_cost / len(cloud_models) if cloud_models else 0,
                "cost_efficiency_score": self._calculate_efficiency_score(cloud_entries),
                "resource_breakdown": self._get_resource_breakdown(cloud_entries),
                "regional_distribution": self._get_regional_distribution(cloud_entries)
            }

        self.generated_data["cloud_comparisons"] = comparisons

    def _calculate_efficiency_score(self, entries: List[Dict]) -> float:
        """Calculate efficiency score for a cloud provider"""
        if not entries:
            return 0.0

        # Simple efficiency metric based on GPU vs total cost ratio
        gpu_cost = sum(e["total_cost"] for e in entries if e["resource_type"] == "compute_gpu")
        total_cost = sum(e["total_cost"] for e in entries)

        gpu_ratio = (gpu_cost / total_cost) if total_cost > 0 else 0
        return min(100, gpu_ratio * 150)  # Higher GPU usage = higher efficiency score

    def _get_resource_breakdown(self, entries: List[Dict]) -> Dict[str, float]:
        """Get resource cost breakdown for cloud provider"""
        breakdown = {}
        total_cost = sum(e["total_cost"] for e in entries)

        for entry in entries:
            resource = entry["resource_type"]
            breakdown[resource] = breakdown.get(resource, 0) + entry["total_cost"]

        # Convert to percentages
        for resource in breakdown:
            breakdown[resource] = (breakdown[resource] / total_cost * 100) if total_cost > 0 else 0

        return breakdown

    def _get_regional_distribution(self, entries: List[Dict]) -> Dict[str, float]:
        """Get regional cost distribution for cloud provider"""
        distribution = {}
        total_cost = sum(e["total_cost"] for e in entries)

        for entry in entries:
            region = entry["region"]
            distribution[region] = distribution.get(region, 0) + entry["total_cost"]

        # Convert to percentages
        for region in distribution:
            distribution[region] = (distribution[region] / total_cost * 100) if total_cost > 0 else 0

        return distribution

    def export_data(self, filename: str = "multi_cloud_cost_data.json"):
        """Export generated data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.generated_data, f, indent=2, default=str)

        print(f"\n💾 Data exported to: {filename}")
        return filename

    def generate_dashboard_ready_data(self) -> Dict[str, Any]:
        """Generate data formatted for web dashboard consumption"""
        dashboard_data = {
            "overview": {
                "total_models": len(self.generated_data["models"]),
                "total_cost": self.generated_data["summary_stats"]["total_cost"],
                "cloud_providers": len(CLOUD_PRICING),
                "active_regions": len(set(e["region"] for e in self.generated_data["cost_entries"])),
                "cost_by_cloud": self.generated_data["summary_stats"]["cost_by_cloud"],
                "build_vs_production": self.generated_data["summary_stats"]["build_vs_production"]
            },
            "models": self.generated_data["models"],
            "cost_trends": self._generate_cost_trends(),
            "cloud_comparisons": self.generated_data["cloud_comparisons"],
            "resource_utilization": self.generated_data["summary_stats"]["cost_by_resource"],
            "regional_analysis": self._generate_regional_analysis(),
            "optimization_opportunities": self._generate_optimization_recommendations()
        }

        return dashboard_data

    def _generate_cost_trends(self) -> List[Dict]:
        """Generate cost trend data for visualization"""
        # Group costs by date
        daily_costs = {}

        for entry in self.generated_data["cost_entries"]:
            date = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d")
            if date not in daily_costs:
                daily_costs[date] = {"date": date, "total": 0}
            daily_costs[date]["total"] += entry["total_cost"]

        return list(daily_costs.values())

    def _generate_regional_analysis(self) -> Dict[str, Any]:
        """Generate regional cost analysis"""
        regional_data = {}

        for entry in self.generated_data["cost_entries"]:
            region = entry["region"]
            cloud = entry["cloud_provider"]
            key = f"{cloud}_{region}"

            if key not in regional_data:
                regional_data[key] = {
                    "cloud": cloud,
                    "region": region,
                    "total_cost": 0,
                    "model_count": 0,
                    "efficiency_score": 0
                }

            regional_data[key]["total_cost"] += entry["total_cost"]

        # Add model counts
        for model in self.generated_data["models"]:
            key = f"{model['cloud_provider']}_{model['primary_region']}"
            if key in regional_data:
                regional_data[key]["model_count"] += 1

        return list(regional_data.values())

    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        stats = self.generated_data["summary_stats"]

        # Check for cost imbalances
        if stats["build_vs_production"]["build_percentage"] > 80:
            recommendations.append("High build costs detected - consider optimizing training efficiency")

        # Check for underutilized resources
        gpu_percentage = (stats["cost_by_resource"].get("compute_gpu", 0) / stats["total_cost"] * 100)
        if gpu_percentage < 30:
            recommendations.append("Low GPU utilization - consider consolidating workloads")

        # Cloud cost comparison
        cloud_costs = stats["cost_by_cloud"]
        if len(cloud_costs) > 1:
            max_cost_cloud = max(cloud_costs, key=cloud_costs.get)
            min_cost_cloud = min(cloud_costs, key=cloud_costs.get)
            if cloud_costs[max_cost_cloud] > cloud_costs[min_cost_cloud] * 1.5:
                recommendations.append(f"Consider migrating workloads from {max_cost_cloud} to {min_cost_cloud}")

        return recommendations


def main():
    """Generate multi-cloud cost attribution demo data"""
    print("🌐 Multi-Cloud Model Cost Attribution Data Generator")
    print("=" * 55)
    print()

    generator = MultiCloudCostGenerator()

    # Generate complete dataset
    dataset = generator.generate_complete_dataset()

    # Export data
    generator.export_data("multi_cloud_cost_data.json")

    # Generate dashboard-ready data
    dashboard_data = generator.generate_dashboard_ready_data()
    with open("dashboard_cost_data.json", 'w') as f:
        json.dump(dashboard_data, f, indent=2, default=str)

    print("\n📊 Dataset Summary:")
    print(f"   Total Cost Simulated: ${dataset['summary_stats']['total_cost']:,.2f}")
    print(f"   Cloud Providers: {', '.join(dataset['summary_stats']['cost_by_cloud'].keys())}")
    print(f"   Build vs Production: {dataset['summary_stats']['build_vs_production']['build_percentage']:.1f}% / {dataset['summary_stats']['build_vs_production']['production_percentage']:.1f}%")
    print()
    print("Files generated:")
    print("   📄 multi_cloud_cost_data.json - Complete dataset")
    print("   📄 dashboard_cost_data.json - Dashboard-ready data")


if __name__ == "__main__":
    main()