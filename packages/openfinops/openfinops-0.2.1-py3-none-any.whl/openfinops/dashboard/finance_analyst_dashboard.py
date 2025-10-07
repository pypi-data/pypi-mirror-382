"""
Finance Analyst Dashboard
========================

Detailed financial analytics dashboard for Finance Analysts with comprehensive
cost analysis, budget management, and operational financial metrics.
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
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from dataclasses import dataclass, field
import sqlite3
from decimal import Decimal

# Import VizlyChart for professional visualizations
try:
    import openfinops.vizlychart as vc
    from openfinops.vizlychart.charts.financial import FinancialChart
    from openfinops.vizlychart.charts.advanced import AdvancedAnalytics
    from openfinops.vizlychart.enterprise.themes import AnalystTheme
    VIZLYCHART_AVAILABLE = True
except ImportError:
    VIZLYCHART_AVAILABLE = False
    # VizlyChart is optional - dashboards work with fallback visualizations

from .iam_system import get_iam_manager, DashboardType, DataClassification

logger = logging.getLogger(__name__)


@dataclass
class CostAnalysis:
    """Detailed cost analysis with variance and trend data."""
    category: str
    subcategory: Optional[str]
    current_amount: Decimal
    budget_amount: Decimal
    previous_period: Decimal
    variance_amount: Decimal
    variance_percent: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    cost_per_unit: Optional[Decimal] = None
    volume_driver: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class BudgetItem:
    """Budget item with detailed tracking and forecasting."""
    item_id: str
    category: str
    subcategory: str
    budget_amount: Decimal
    spent_amount: Decimal
    committed_amount: Decimal
    available_amount: Decimal
    utilization_percent: float
    forecast_final: Decimal
    variance_forecast: Decimal
    risk_level: str  # 'low', 'medium', 'high'
    owner: str
    approval_status: str


@dataclass
class FinancialMetric:
    """Financial metric with detailed analysis."""
    name: str
    value: Decimal
    unit: str
    period: str
    comparison_periods: Dict[str, Decimal]
    trend_analysis: Dict[str, Any]
    benchmark_comparison: Optional[Dict[str, Any]] = None
    calculation_method: Optional[str] = None


class FinanceAnalystDashboard:
    """Finance Analyst Dashboard with detailed financial analytics and reporting."""

    def __init__(self):
        self.iam_manager = get_iam_manager()
        self.theme = self._get_analyst_theme()
        self.data_sources = self._initialize_data_sources()
        self.db_connection = self._initialize_database()

    def _get_analyst_theme(self) -> Dict[str, Any]:
        """Get finance analyst theme configuration."""
        return {
            "name": "Finance Analyst Professional",
            "colors": {
                "primary": "#1e40af",        # Professional blue
                "secondary": "#0891b2",      # Teal
                "success": "#059669",        # Green
                "warning": "#d97706",        # Orange
                "danger": "#dc2626",         # Red
                "info": "#7c3aed",          # Purple
                "neutral": "#6b7280",        # Gray
                "background": "#ffffff",     # White
                "surface": "#f8fafc",        # Light gray
                "text": "#1f2937",          # Dark gray
                "border": "#e5e7eb"         # Light border
            },
            "chart_palette": [
                "#1e40af", "#059669", "#d97706", "#dc2626",
                "#7c3aed", "#0891b2", "#be185d", "#7c2d12"
            ],
            "fonts": {
                "primary": "Inter, system-ui, sans-serif",
                "monospace": "SF Mono, Monaco, monospace",
                "headers": "Inter, system-ui, sans-serif"
            },
            "watermark": {
                "enabled": True,
                "text": "OpenFinOps Internal - Finance Analytics",
                "position": "bottom_right",
                "opacity": 0.08
            }
        }

    def _initialize_data_sources(self) -> Dict[str, Any]:
        """Initialize data sources for financial analytics."""
        return {
            "erp_system": {
                "url": "https://api.company.com/erp",
                "auth": "bearer_token",
                "refresh_interval": 3600
            },
            "cost_management": {
                "url": "https://api.openfinops.com/cost-management",
                "api_key": "fm_api_key",
                "refresh_interval": 900
            },
            "cloud_providers": {
                "aws": {
                    "cost_explorer": True,
                    "detailed_billing": True,
                    "resource_tagging": True
                },
                "azure": {
                    "cost_management": True,
                    "subscription_analysis": True
                },
                "gcp": {
                    "billing_api": True,
                    "cost_breakdown": True
                }
            },
            "ai_platforms": {
                "openai": {"cost_tracking": True, "usage_analytics": True},
                "anthropic": {"cost_tracking": True, "usage_analytics": True},
                "huggingface": {"inference_costs": True}
            },
            "budget_system": {
                "url": "https://api.company.com/budgets",
                "integration": "real_time"
            }
        }

    def _initialize_database(self) -> sqlite3.Connection:
        """Initialize local database for analytics cache."""
        conn = sqlite3.connect(':memory:')  # In production, use persistent database

        # Create tables for financial data
        conn.execute('''
            CREATE TABLE cost_analytics (
                id INTEGER PRIMARY KEY,
                date TEXT,
                category TEXT,
                subcategory TEXT,
                amount REAL,
                budget REAL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE budget_tracking (
                id INTEGER PRIMARY KEY,
                budget_id TEXT,
                category TEXT,
                budget_amount REAL,
                spent_amount REAL,
                period TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        return conn

    def generate_dashboard(self, user_id: str, time_period: str = "current_month",
                          analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate comprehensive finance analyst dashboard."""

        # Verify user access
        if not self.iam_manager.can_access_dashboard(user_id, DashboardType.FINANCE_ANALYST):
            raise PermissionError("User does not have access to Finance Analyst dashboard")

        user_access_level = self.iam_manager.get_user_data_access_level(user_id)
        if user_access_level not in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            raise PermissionError("Insufficient data access level for Finance Analyst dashboard")

        logger.info(f"Generating Finance Analyst dashboard for user {user_id}, period: {time_period}")

        # Generate dashboard components based on analysis type
        dashboard_data = {
            "metadata": self._get_dashboard_metadata(user_id, time_period, analysis_type),
            "cost_analytics": self._generate_cost_analytics(time_period),
            "budget_analysis": self._generate_budget_analysis(time_period),
            "ai_cost_breakdown": self._generate_ai_cost_breakdown(time_period),
            "variance_analysis": self._generate_variance_analysis(time_period),
            "trend_analysis": self._generate_trend_analysis(time_period),
            "cost_drivers": self._analyze_cost_drivers(time_period),
            "optimization_opportunities": self._identify_optimization_opportunities(time_period),
            "financial_metrics": self._calculate_financial_metrics(time_period),
            "forecasting": self._generate_financial_forecasts(time_period),
            "vendor_analysis": self._analyze_vendor_costs(time_period),
            "department_breakdown": self._analyze_department_costs(time_period),
            "visualizations": self._generate_visualizations(time_period, analysis_type)
        }

        # Add detailed analytics if requested
        if analysis_type == "detailed":
            dashboard_data.update({
                "drill_down_analysis": self._generate_drill_down_analysis(time_period),
                "correlation_analysis": self._perform_correlation_analysis(time_period),
                "statistical_analysis": self._perform_statistical_analysis(time_period)
            })

        # Log dashboard access
        self.iam_manager._log_audit_event("dashboard_access", user_id, {
            "dashboard_type": "finance_analyst",
            "time_period": time_period,
            "analysis_type": analysis_type,
            "components_generated": list(dashboard_data.keys())
        })

        return dashboard_data

    def _get_dashboard_metadata(self, user_id: str, time_period: str, analysis_type: str) -> Dict[str, Any]:
        """Get dashboard metadata and context."""
        user = self.iam_manager.users.get(user_id)

        return {
            "dashboard_id": f"finance_analyst_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "generated_for": {
                "user_id": user_id,
                "name": user.full_name if user else "Unknown",
                "department": user.department if user else "Unknown",
                "role": "Finance Analyst"
            },
            "time_period": time_period,
            "analysis_type": analysis_type,
            "data_classification": "CONFIDENTIAL",
            "refresh_interval": 900,  # 15 minutes
            "version": "2.1.0",
            "theme": self.theme["name"],
            "data_sources": list(self.data_sources.keys()),
            "last_data_refresh": datetime.utcnow().isoformat()
        }

    def _generate_cost_analytics(self, time_period: str) -> Dict[str, Any]:
        """Generate detailed cost analytics with multi-dimensional analysis."""

        # Simulate comprehensive cost data - in production, fetch from actual sources
        cost_categories = {
            "AI & Machine Learning": {
                "Model Training": {
                    "current": 4200000,
                    "budget": 3800000,
                    "previous": 3600000,
                    "subcategories": {
                        "GPU Compute": 2800000,
                        "Data Processing": 750000,
                        "Storage": 400000,
                        "Networking": 250000
                    }
                },
                "Inference & APIs": {
                    "current": 2100000,
                    "budget": 2000000,
                    "previous": 1850000,
                    "subcategories": {
                        "OpenAI API": 1200000,
                        "Anthropic API": 400000,
                        "Internal Hosting": 500000
                    }
                },
                "Research & Development": {
                    "current": 1800000,
                    "budget": 1900000,
                    "previous": 1650000,
                    "subcategories": {
                        "Experimental Models": 900000,
                        "Research Infrastructure": 600000,
                        "External Partnerships": 300000
                    }
                }
            },
            "Cloud Infrastructure": {
                "Compute Resources": {
                    "current": 7500000,
                    "budget": 7200000,
                    "previous": 6800000,
                    "subcategories": {
                        "Production Workloads": 4500000,
                        "Development/Testing": 1800000,
                        "AI Training": 1200000
                    }
                },
                "Storage Systems": {
                    "current": 2800000,
                    "budget": 2600000,
                    "previous": 2400000,
                    "subcategories": {
                        "Data Lakes": 1500000,
                        "Database Storage": 800000,
                        "Backup Systems": 500000
                    }
                },
                "Networking": {
                    "current": 1200000,
                    "budget": 1100000,
                    "previous": 1000000,
                    "subcategories": {
                        "CDN Services": 600000,
                        "VPN & Security": 350000,
                        "API Gateway": 250000
                    }
                }
            },
            "Software & Licensing": {
                "Enterprise Software": {
                    "current": 4200000,
                    "budget": 4300000,
                    "previous": 3900000,
                    "subcategories": {
                        "ERP System": 1800000,
                        "CRM Platform": 1200000,
                        "Analytics Tools": 800000,
                        "Security Software": 400000
                    }
                },
                "Development Tools": {
                    "current": 1500000,
                    "budget": 1400000,
                    "previous": 1300000,
                    "subcategories": {
                        "IDE Licenses": 600000,
                        "CI/CD Tools": 450000,
                        "Monitoring Tools": 450000
                    }
                }
            }
        }

        # Process cost data into analysis format
        cost_analyses = []
        total_variance = 0

        for main_category, subcategories in cost_categories.items():
            for subcategory, data in subcategories.items():
                variance_amount = data["current"] - data["budget"]
                variance_percent = (variance_amount / data["budget"]) * 100 if data["budget"] > 0 else 0
                total_variance += variance_amount

                # Determine trend
                if data["current"] > data["previous"] * 1.05:
                    trend = "increasing"
                elif data["current"] < data["previous"] * 0.95:
                    trend = "decreasing"
                else:
                    trend = "stable"

                cost_analysis = CostAnalysis(
                    category=main_category,
                    subcategory=subcategory,
                    current_amount=Decimal(str(data["current"])),
                    budget_amount=Decimal(str(data["budget"])),
                    previous_period=Decimal(str(data["previous"])),
                    variance_amount=Decimal(str(variance_amount)),
                    variance_percent=variance_percent,
                    trend_direction=trend,
                    tags=["operational"]
                )
                cost_analyses.append(cost_analysis)

        # Calculate summary metrics
        total_current = sum(float(ca.current_amount) for ca in cost_analyses)
        total_budget = sum(float(ca.budget_amount) for ca in cost_analyses)
        total_previous = sum(float(ca.previous_period) for ca in cost_analyses)

        return {
            "summary": {
                "total_current_costs": total_current,
                "total_budget": total_budget,
                "total_variance": float(total_variance),
                "variance_percent": (total_variance / total_budget) * 100 if total_budget > 0 else 0,
                "period_over_period_change": ((total_current - total_previous) / total_previous) * 100,
                "cost_categories_count": len(cost_categories),
                "over_budget_items": len([ca for ca in cost_analyses if ca.variance_amount > 0])
            },
            "detailed_analysis": [
                {
                    "category": ca.category,
                    "subcategory": ca.subcategory,
                    "current_amount": float(ca.current_amount),
                    "budget_amount": float(ca.budget_amount),
                    "variance_amount": float(ca.variance_amount),
                    "variance_percent": ca.variance_percent,
                    "trend_direction": ca.trend_direction,
                    "previous_period": float(ca.previous_period),
                    "tags": ca.tags
                } for ca in cost_analyses
            ],
            "top_variances": sorted([
                {
                    "category": ca.category,
                    "subcategory": ca.subcategory,
                    "variance_amount": float(ca.variance_amount),
                    "variance_percent": ca.variance_percent
                } for ca in cost_analyses
            ], key=lambda x: abs(x["variance_amount"]), reverse=True)[:10],
            "cost_efficiency_metrics": {
                "cost_per_revenue_dollar": total_current / 125000000,  # Assuming $125M revenue
                "cost_growth_rate": ((total_current - total_previous) / total_previous) * 100,
                "budget_accuracy": 100 - abs((total_variance / total_budget) * 100)
            }
        }

    def _generate_budget_analysis(self, time_period: str) -> Dict[str, Any]:
        """Generate comprehensive budget analysis and tracking."""

        # Simulate budget tracking data
        budget_items = [
            BudgetItem(
                item_id="BDG001",
                category="AI & ML",
                subcategory="Model Training",
                budget_amount=Decimal("3800000"),
                spent_amount=Decimal("2800000"),
                committed_amount=Decimal("600000"),
                available_amount=Decimal("400000"),
                utilization_percent=73.7,
                forecast_final=Decimal("4200000"),
                variance_forecast=Decimal("400000"),
                risk_level="medium",
                owner="Data Science Team",
                approval_status="approved"
            ),
            BudgetItem(
                item_id="BDG002",
                category="Cloud Infrastructure",
                subcategory="Compute Resources",
                budget_amount=Decimal("7200000"),
                spent_amount=Decimal("5400000"),
                committed_amount=Decimal("1200000"),
                available_amount=Decimal("600000"),
                utilization_percent=75.0,
                forecast_final=Decimal("7500000"),
                variance_forecast=Decimal("300000"),
                risk_level="low",
                owner="Infrastructure Team",
                approval_status="approved"
            ),
            BudgetItem(
                item_id="BDG003",
                category="Software Licensing",
                subcategory="Enterprise Software",
                budget_amount=Decimal("4300000"),
                spent_amount=Decimal("3200000"),
                committed_amount=Decimal("800000"),
                available_amount=Decimal("300000"),
                utilization_percent=74.4,
                forecast_final=Decimal("4200000"),
                variance_forecast=Decimal("-100000"),
                risk_level="low",
                owner="IT Operations",
                approval_status="approved"
            )
        ]

        # Calculate budget performance metrics
        total_budget = sum(float(item.budget_amount) for item in budget_items)
        total_spent = sum(float(item.spent_amount) for item in budget_items)
        total_committed = sum(float(item.committed_amount) for item in budget_items)
        total_available = sum(float(item.available_amount) for item in budget_items)
        total_forecast = sum(float(item.forecast_final) for item in budget_items)

        return {
            "budget_summary": {
                "total_budget": total_budget,
                "total_spent": total_spent,
                "total_committed": total_committed,
                "total_available": total_available,
                "utilization_percent": (total_spent / total_budget) * 100,
                "forecast_variance": total_forecast - total_budget,
                "forecast_variance_percent": ((total_forecast - total_budget) / total_budget) * 100
            },
            "budget_items": [
                {
                    "item_id": item.item_id,
                    "category": item.category,
                    "subcategory": item.subcategory,
                    "budget_amount": float(item.budget_amount),
                    "spent_amount": float(item.spent_amount),
                    "committed_amount": float(item.committed_amount),
                    "available_amount": float(item.available_amount),
                    "utilization_percent": item.utilization_percent,
                    "forecast_final": float(item.forecast_final),
                    "variance_forecast": float(item.variance_forecast),
                    "risk_level": item.risk_level,
                    "owner": item.owner,
                    "approval_status": item.approval_status
                } for item in budget_items
            ],
            "budget_alerts": [
                {
                    "category": "AI & ML",
                    "alert_type": "over_budget_forecast",
                    "severity": "medium",
                    "message": "Model Training budget forecasted to exceed by $400K",
                    "recommended_action": "Review training efficiency and consider optimization"
                },
                {
                    "category": "Cloud Infrastructure",
                    "alert_type": "utilization_high",
                    "severity": "low",
                    "message": "High utilization (75%) but within budget",
                    "recommended_action": "Monitor for potential overrun"
                }
            ],
            "budget_performance": {
                "on_track_items": len([item for item in budget_items if item.risk_level == "low"]),
                "at_risk_items": len([item for item in budget_items if item.risk_level == "medium"]),
                "over_budget_items": len([item for item in budget_items if item.risk_level == "high"]),
                "average_utilization": sum(item.utilization_percent for item in budget_items) / len(budget_items)
            }
        }

    def _generate_ai_cost_breakdown(self, time_period: str) -> Dict[str, Any]:
        """Generate detailed AI cost breakdown and analysis."""

        ai_costs = {
            "training_infrastructure": {
                "gpu_compute": {
                    "aws_p4": {"hours": 12500, "cost_per_hour": 32.77, "total": 409625},
                    "azure_nd": {"hours": 8200, "cost_per_hour": 31.20, "total": 255840},
                    "gcp_tpu": {"hours": 6800, "cost_per_hour": 28.50, "total": 193800}
                },
                "storage_costs": {
                    "training_data": 85000,
                    "model_checkpoints": 65000,
                    "intermediate_results": 45000
                },
                "data_transfer": {
                    "inter_region": 25000,
                    "ingress": 15000,
                    "egress": 35000
                }
            },
            "inference_costs": {
                "api_services": {
                    "openai_gpt4": {"requests": 2500000, "cost_per_request": 0.048, "total": 1200000},
                    "anthropic_claude": {"requests": 800000, "cost_per_request": 0.05, "total": 400000},
                    "internal_models": {"requests": 5000000, "cost_per_request": 0.01, "total": 500000}
                },
                "hosting_infrastructure": {
                    "production_servers": 350000,
                    "load_balancers": 25000,
                    "monitoring": 15000
                }
            },
            "data_processing": {
                "etl_pipelines": 180000,
                "feature_engineering": 120000,
                "data_validation": 65000
            },
            "research_development": {
                "experimental_training": 450000,
                "model_evaluation": 180000,
                "research_infrastructure": 220000
            }
        }

        # Calculate totals and metrics
        total_training = sum([
            sum(provider["total"] for provider in ai_costs["training_infrastructure"]["gpu_compute"].values()),
            sum(ai_costs["training_infrastructure"]["storage_costs"].values()),
            sum(ai_costs["training_infrastructure"]["data_transfer"].values())
        ])

        total_inference = sum([
            sum(service["total"] for service in ai_costs["inference_costs"]["api_services"].values()),
            sum(ai_costs["inference_costs"]["hosting_infrastructure"].values())
        ])

        total_data_processing = sum(ai_costs["data_processing"].values())
        total_research = sum(ai_costs["research_development"].values())
        total_ai_costs = total_training + total_inference + total_data_processing + total_research

        return {
            "cost_breakdown": {
                "training_infrastructure": total_training,
                "inference_operations": total_inference,
                "data_processing": total_data_processing,
                "research_development": total_research,
                "total_ai_costs": total_ai_costs
            },
            "detailed_costs": ai_costs,
            "cost_metrics": {
                "cost_per_model_trained": total_training / 125,  # Assuming 125 models trained
                "cost_per_inference": total_inference / 8300000,  # Total inferences
                "training_to_inference_ratio": total_training / total_inference,
                "ai_cost_as_percent_of_revenue": (total_ai_costs / 125000000) * 100  # Against $125M revenue
            },
            "efficiency_metrics": {
                "gpu_utilization_avg": 87.5,
                "training_cost_per_epoch": 2850,
                "inference_latency_cost_ratio": 0.045,
                "model_accuracy_vs_cost": {
                    "high_cost_models": {"accuracy": 94.2, "cost_ratio": 0.35},
                    "medium_cost_models": {"accuracy": 91.8, "cost_ratio": 0.45},
                    "low_cost_models": {"accuracy": 88.5, "cost_ratio": 0.20}
                }
            },
            "optimization_analysis": {
                "spot_instance_savings": {"potential": 380000, "risk": "medium"},
                "reserved_instance_opportunities": {"potential": 290000, "commitment": "1_year"},
                "api_optimization": {"potential": 150000, "implementation": "immediate"},
                "model_compression": {"potential": 220000, "accuracy_impact": "minimal"}
            }
        }

    def _generate_variance_analysis(self, time_period: str) -> Dict[str, Any]:
        """Generate comprehensive variance analysis."""

        # Simulate variance data across different dimensions
        variances = {
            "budget_variances": [
                {
                    "category": "AI Training",
                    "budget": 3800000,
                    "actual": 4200000,
                    "variance": 400000,
                    "variance_percent": 10.5,
                    "explanation": "Increased training volume for new product features",
                    "controllable": True,
                    "volume_variance": 250000,
                    "rate_variance": 150000
                },
                {
                    "category": "Cloud Infrastructure",
                    "budget": 7200000,
                    "actual": 7500000,
                    "variance": 300000,
                    "variance_percent": 4.2,
                    "explanation": "Higher than expected usage due to traffic growth",
                    "controllable": False,
                    "volume_variance": 180000,
                    "rate_variance": 120000
                },
                {
                    "category": "Software Licensing",
                    "budget": 4300000,
                    "actual": 4200000,
                    "variance": -100000,
                    "variance_percent": -2.3,
                    "explanation": "Negotiated better rates with vendors",
                    "controllable": True,
                    "volume_variance": 0,
                    "rate_variance": -100000
                }
            ],
            "time_based_variances": {
                "monthly_variances": [
                    {"month": "Jan", "budget": 28500000, "actual": 28200000, "variance": -300000},
                    {"month": "Feb", "budget": 29000000, "actual": 29800000, "variance": 800000},
                    {"month": "Mar", "budget": 30000000, "actual": 31200000, "variance": 1200000},
                    {"month": "Apr", "budget": 30500000, "actual": 30100000, "variance": -400000}
                ],
                "seasonal_patterns": {
                    "q1_variance": 1.8,  # percent
                    "q2_variance": 3.2,
                    "q3_variance": -0.8,
                    "q4_variance": 2.5
                }
            },
            "cost_driver_variances": {
                "volume_driven": {
                    "ai_training_hours": {"budgeted": 25000, "actual": 28500, "cost_impact": 315000},
                    "api_requests": {"budgeted": 7500000, "actual": 8300000, "cost_impact": 240000},
                    "storage_gb": {"budgeted": 850000, "actual": 920000, "cost_impact": 105000}
                },
                "rate_driven": {
                    "gpu_hourly_rate": {"budgeted": 32.50, "actual": 33.80, "cost_impact": 87500},
                    "api_cost_per_request": {"budgeted": 0.045, "actual": 0.048, "cost_impact": 249000},
                    "storage_cost_per_gb": {"budgeted": 0.15, "actual": 0.14, "cost_impact": -92000}
                }
            }
        }

        # Calculate variance analysis metrics
        total_budget = sum(item["budget"] for item in variances["budget_variances"])
        total_actual = sum(item["actual"] for item in variances["budget_variances"])
        total_variance = total_actual - total_budget

        return {
            "variance_summary": {
                "total_budget": total_budget,
                "total_actual": total_actual,
                "total_variance": total_variance,
                "variance_percent": (total_variance / total_budget) * 100,
                "favorable_variances": sum(v["variance"] for v in variances["budget_variances"] if v["variance"] < 0),
                "unfavorable_variances": sum(v["variance"] for v in variances["budget_variances"] if v["variance"] > 0),
                "controllable_variances": sum(v["variance"] for v in variances["budget_variances"] if v["controllable"]),
                "uncontrollable_variances": sum(v["variance"] for v in variances["budget_variances"] if not v["controllable"])
            },
            "detailed_variances": variances,
            "variance_drivers": {
                "primary_drivers": [
                    {"driver": "AI Training Volume", "impact": 315000, "controllable": True},
                    {"driver": "API Request Growth", "impact": 240000, "controllable": False},
                    {"driver": "GPU Rate Increases", "impact": 87500, "controllable": False}
                ],
                "volume_vs_rate_split": {
                    "volume_impact": 705000,
                    "rate_impact": 244500,
                    "volume_percent": 74.2
                }
            },
            "variance_trends": {
                "improving_categories": ["Software Licensing"],
                "worsening_categories": ["AI Training", "Cloud Infrastructure"],
                "stable_categories": [],
                "volatility_metrics": {
                    "coefficient_of_variation": 0.15,
                    "forecast_accuracy": 94.2
                }
            }
        }

    def _generate_trend_analysis(self, time_period: str) -> Dict[str, Any]:
        """Generate comprehensive trend analysis."""

        # Generate trend data for the last 12 months
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        cost_trends = {
            "monthly_costs": [
                {"month": month,
                 "total_costs": 25000000 + i * 500000 + np.random.normal(0, 200000),
                 "ai_costs": 5000000 + i * 150000 + np.random.normal(0, 50000),
                 "infrastructure": 12000000 + i * 200000 + np.random.normal(0, 100000),
                 "personnel": 8000000 + i * 150000 + np.random.normal(0, 75000)}
                for i, month in enumerate(months)
            ]
        }

        # Calculate trend metrics
        recent_months = cost_trends["monthly_costs"][-6:]  # Last 6 months

        total_cost_trend = np.polyfit(range(len(recent_months)),
                                    [m["total_costs"] for m in recent_months], 1)[0]
        ai_cost_trend = np.polyfit(range(len(recent_months)),
                                 [m["ai_costs"] for m in recent_months], 1)[0]

        return {
            "cost_trends": cost_trends,
            "trend_analysis": {
                "total_cost_monthly_change": total_cost_trend,
                "ai_cost_monthly_change": ai_cost_trend,
                "cost_growth_rate": {
                    "6_month": ((recent_months[-1]["total_costs"] - recent_months[0]["total_costs"]) / recent_months[0]["total_costs"]) * 100,
                    "12_month": ((cost_trends["monthly_costs"][-1]["total_costs"] - cost_trends["monthly_costs"][0]["total_costs"]) / cost_trends["monthly_costs"][0]["total_costs"]) * 100
                },
                "volatility_metrics": {
                    "cost_volatility": np.std([m["total_costs"] for m in cost_trends["monthly_costs"]]) / np.mean([m["total_costs"] for m in cost_trends["monthly_costs"]]),
                    "ai_cost_volatility": np.std([m["ai_costs"] for m in cost_trends["monthly_costs"]]) / np.mean([m["ai_costs"] for m in cost_trends["monthly_costs"]])
                }
            },
            "seasonal_patterns": {
                "q1_pattern": "stable_growth",
                "q2_pattern": "accelerated_growth",
                "q3_pattern": "moderate_growth",
                "q4_pattern": "peak_spending",
                "seasonal_adjustment_factor": 0.92
            },
            "forecast_trends": {
                "next_quarter_projection": {
                    "total_costs": recent_months[-1]["total_costs"] * 1.08,
                    "confidence_interval": 0.85,
                    "key_assumptions": ["Continued AI investment", "Stable infrastructure costs"]
                },
                "annual_projection": {
                    "total_costs": sum(m["total_costs"] for m in cost_trends["monthly_costs"]) * 1.12,
                    "growth_rate": 12.0,
                    "risk_factors": ["Cloud price increases", "AI scaling requirements"]
                }
            }
        }

    def _analyze_cost_drivers(self, time_period: str) -> Dict[str, Any]:
        """Analyze primary cost drivers and their relationships."""

        cost_drivers = {
            "volume_drivers": {
                "ai_training_hours": {
                    "current_volume": 28500,
                    "cost_per_unit": 33.80,
                    "total_cost": 963300,
                    "elasticity": 0.85,  # Cost elasticity
                    "correlation_with_revenue": 0.78
                },
                "api_requests": {
                    "current_volume": 8300000,
                    "cost_per_unit": 0.048,
                    "total_cost": 398400,
                    "elasticity": 1.2,
                    "correlation_with_revenue": 0.92
                },
                "storage_consumption": {
                    "current_volume": 920000,  # GB
                    "cost_per_unit": 0.14,
                    "total_cost": 128800,
                    "elasticity": 0.45,
                    "correlation_with_revenue": 0.65
                }
            },
            "efficiency_drivers": {
                "gpu_utilization": {
                    "current_rate": 87.5,
                    "optimal_rate": 90.0,
                    "efficiency_impact": 0.95,
                    "cost_optimization_potential": 125000
                },
                "model_accuracy": {
                    "current_rate": 94.2,
                    "cost_per_accuracy_point": 85000,
                    "diminishing_returns_threshold": 95.0
                },
                "automation_level": {
                    "current_rate": 72.5,
                    "target_rate": 85.0,
                    "cost_reduction_potential": 450000
                }
            },
            "external_factors": {
                "cloud_pricing": {
                    "price_volatility": 0.08,
                    "recent_changes": [
                        {"service": "GPU Compute", "change_percent": 3.2, "effective_date": "2024-01-01"},
                        {"service": "Storage", "change_percent": -2.1, "effective_date": "2024-02-01"}
                    ]
                },
                "market_conditions": {
                    "ai_demand_index": 145,  # 100 = baseline
                    "talent_cost_inflation": 8.5,
                    "technology_advancement_impact": -12.0  # Cost reduction from efficiency
                }
            }
        }

        return {
            "cost_driver_analysis": cost_drivers,
            "driver_rankings": [
                {"driver": "API Request Volume", "impact_score": 92, "controllability": "medium"},
                {"driver": "AI Training Hours", "impact_score": 85, "controllability": "high"},
                {"driver": "Cloud Pricing Changes", "impact_score": 73, "controllability": "low"},
                {"driver": "GPU Utilization", "impact_score": 68, "controllability": "high"},
                {"driver": "Storage Consumption", "impact_score": 45, "controllability": "medium"}
            ],
            "cost_elasticity": {
                "highly_elastic": ["ai_training_hours", "api_requests"],
                "moderately_elastic": ["storage_consumption", "personnel_costs"],
                "inelastic": ["software_licensing", "fixed_infrastructure"]
            },
            "optimization_levers": [
                {
                    "lever": "Improve GPU Utilization",
                    "current_state": 87.5,
                    "target_state": 90.0,
                    "cost_impact": 125000,
                    "implementation_effort": "medium"
                },
                {
                    "lever": "Automate Manual Processes",
                    "current_state": 72.5,
                    "target_state": 85.0,
                    "cost_impact": 450000,
                    "implementation_effort": "high"
                },
                {
                    "lever": "Optimize API Usage",
                    "current_state": "baseline",
                    "target_state": "15% reduction",
                    "cost_impact": 180000,
                    "implementation_effort": "low"
                }
            ]
        }

    def _identify_optimization_opportunities(self, time_period: str) -> Dict[str, Any]:
        """Identify and prioritize cost optimization opportunities."""

        opportunities = [
            {
                "id": "OPT001",
                "category": "Infrastructure",
                "title": "Implement GPU Auto-Scaling",
                "description": "Automatically scale GPU resources based on training queue depth",
                "potential_savings": 380000,
                "implementation_cost": 75000,
                "payback_months": 2.4,
                "risk_level": "low",
                "effort_level": "medium",
                "impact_on_operations": "minimal",
                "prerequisites": ["monitoring_upgrade", "automation_framework"],
                "timeline": "8 weeks",
                "confidence": 0.85
            },
            {
                "id": "OPT002",
                "category": "AI Operations",
                "title": "API Request Optimization",
                "description": "Implement request batching and caching to reduce API calls",
                "potential_savings": 280000,
                "implementation_cost": 35000,
                "payback_months": 1.5,
                "risk_level": "low",
                "effort_level": "low",
                "impact_on_operations": "none",
                "prerequisites": ["caching_infrastructure"],
                "timeline": "4 weeks",
                "confidence": 0.92
            },
            {
                "id": "OPT003",
                "category": "Storage",
                "title": "Implement Data Lifecycle Management",
                "description": "Automatically tier data to lower-cost storage based on access patterns",
                "potential_savings": 156000,
                "implementation_cost": 25000,
                "payback_months": 1.9,
                "risk_level": "low",
                "effort_level": "low",
                "impact_on_operations": "minimal",
                "prerequisites": ["data_classification"],
                "timeline": "6 weeks",
                "confidence": 0.88
            },
            {
                "id": "OPT004",
                "category": "Model Optimization",
                "title": "Model Quantization and Compression",
                "description": "Reduce model size while maintaining accuracy to lower inference costs",
                "potential_savings": 340000,
                "implementation_cost": 120000,
                "payback_months": 4.2,
                "risk_level": "medium",
                "effort_level": "high",
                "impact_on_operations": "moderate",
                "prerequisites": ["model_versioning", "performance_testing"],
                "timeline": "16 weeks",
                "confidence": 0.75
            },
            {
                "id": "OPT005",
                "category": "Vendor Management",
                "title": "Renegotiate Cloud Contracts",
                "description": "Leverage usage patterns to negotiate better rates and commit to reserved instances",
                "potential_savings": 420000,
                "implementation_cost": 15000,
                "payback_months": 0.4,
                "risk_level": "low",
                "effort_level": "low",
                "impact_on_operations": "none",
                "prerequisites": ["usage_analysis"],
                "timeline": "3 weeks",
                "confidence": 0.90
            }
        ]

        # Prioritize opportunities
        for opp in opportunities:
            opp["priority_score"] = (
                (opp["potential_savings"] / 1000) * 0.4 +  # Savings weight
                (1 / opp["payback_months"]) * 30 * 0.3 +    # Payback weight
                (1 - {"low": 0.1, "medium": 0.5, "high": 0.9}[opp["risk_level"]]) * 0.2 +  # Risk weight
                opp["confidence"] * 10 * 0.1  # Confidence weight
            )

        sorted_opportunities = sorted(opportunities, key=lambda x: x["priority_score"], reverse=True)

        return {
            "opportunities": sorted_opportunities,
            "summary": {
                "total_opportunities": len(opportunities),
                "total_potential_savings": sum(opp["potential_savings"] for opp in opportunities),
                "total_implementation_cost": sum(opp["implementation_cost"] for opp in opportunities),
                "average_payback_months": sum(opp["payback_months"] for opp in opportunities) / len(opportunities),
                "quick_wins": len([opp for opp in opportunities if opp["payback_months"] < 3 and opp["risk_level"] == "low"]),
                "high_impact_opportunities": len([opp for opp in opportunities if opp["potential_savings"] > 300000])
            },
            "implementation_roadmap": {
                "immediate": [opp["id"] for opp in sorted_opportunities if opp["payback_months"] < 2],
                "short_term": [opp["id"] for opp in sorted_opportunities if 2 <= opp["payback_months"] < 6],
                "long_term": [opp["id"] for opp in sorted_opportunities if opp["payback_months"] >= 6]
            },
            "risk_assessment": {
                "low_risk_savings": sum(opp["potential_savings"] for opp in opportunities if opp["risk_level"] == "low"),
                "medium_risk_savings": sum(opp["potential_savings"] for opp in opportunities if opp["risk_level"] == "medium"),
                "high_risk_savings": sum(opp["potential_savings"] for opp in opportunities if opp["risk_level"] == "high")
            }
        }

    def _calculate_financial_metrics(self, time_period: str) -> List[FinancialMetric]:
        """Calculate comprehensive financial metrics."""

        # Base financial data
        revenue = 125000000
        total_costs = 97500000
        ai_costs = 8100000
        infrastructure_costs = 12500000

        metrics = [
            FinancialMetric(
                name="Cost of Revenue",
                value=Decimal(str(total_costs)),
                unit="USD",
                period=time_period,
                comparison_periods={
                    "previous_month": Decimal("95200000"),
                    "previous_quarter": Decimal("89500000"),
                    "previous_year": Decimal("78000000")
                },
                trend_analysis={
                    "direction": "increasing",
                    "rate": 2.4,  # percent per month
                    "volatility": 0.08
                },
                calculation_method="Direct cost allocation"
            ),
            FinancialMetric(
                name="AI Cost Ratio",
                value=Decimal(str((ai_costs / revenue) * 100)),
                unit="percent",
                period=time_period,
                comparison_periods={
                    "previous_month": Decimal("6.2"),
                    "previous_quarter": Decimal("5.8"),
                    "previous_year": Decimal("4.5")
                },
                trend_analysis={
                    "direction": "increasing",
                    "rate": 0.3,  # percentage points per month
                    "volatility": 0.15
                },
                benchmark_comparison={
                    "industry_average": 5.5,
                    "top_quartile": 4.2,
                    "percentile": 75
                }
            ),
            FinancialMetric(
                name="Cost per AI Model",
                value=Decimal("64800"),
                unit="USD",
                period=time_period,
                comparison_periods={
                    "previous_month": Decimal("68200"),
                    "previous_quarter": Decimal("72500"),
                    "previous_year": Decimal("85000")
                },
                trend_analysis={
                    "direction": "decreasing",
                    "rate": -5.2,  # percent improvement per month
                    "volatility": 0.12
                }
            ),
            FinancialMetric(
                name="Infrastructure Efficiency",
                value=Decimal("87.5"),
                unit="percent",
                period=time_period,
                comparison_periods={
                    "previous_month": Decimal("85.2"),
                    "previous_quarter": Decimal("82.8"),
                    "previous_year": Decimal("78.5")
                },
                trend_analysis={
                    "direction": "increasing",
                    "rate": 1.8,  # percentage points per month
                    "volatility": 0.05
                },
                benchmark_comparison={
                    "industry_average": 82.0,
                    "top_quartile": 90.0,
                    "percentile": 70
                }
            ),
            FinancialMetric(
                name="Cost per API Request",
                value=Decimal("0.048"),
                unit="USD",
                period=time_period,
                comparison_periods={
                    "previous_month": Decimal("0.052"),
                    "previous_quarter": Decimal("0.058"),
                    "previous_year": Decimal("0.075")
                },
                trend_analysis={
                    "direction": "decreasing",
                    "rate": -7.8,  # percent per month
                    "volatility": 0.10
                }
            )
        ]

        return metrics

    def _generate_financial_forecasts(self, time_period: str) -> Dict[str, Any]:
        """Generate detailed financial forecasts."""

        # Base forecast parameters
        base_monthly_costs = 30000000
        growth_rate = 0.08  # 8% annual
        seasonality_factors = [0.95, 0.98, 1.02, 1.05, 1.03, 1.01, 0.97, 0.99, 1.01, 1.04, 1.06, 1.08]

        # Generate 12-month forecast
        monthly_forecasts = []
        for month in range(12):
            monthly_growth = (1 + growth_rate) ** (month / 12)
            seasonal_factor = seasonality_factors[month]
            base_cost = base_monthly_costs * monthly_growth * seasonal_factor

            # Add scenario variations
            conservative = base_cost * 0.92
            optimistic = base_cost * 1.15

            monthly_forecasts.append({
                "month": month + 1,
                "base_forecast": base_cost,
                "conservative": conservative,
                "optimistic": optimistic,
                "ai_costs": base_cost * 0.27,  # 27% of total costs
                "infrastructure": base_cost * 0.42,  # 42% of total costs
                "confidence_interval": [base_cost * 0.95, base_cost * 1.08]
            })

        return {
            "monthly_forecasts": monthly_forecasts,
            "annual_summary": {
                "total_forecast": sum(f["base_forecast"] for f in monthly_forecasts),
                "total_ai_costs": sum(f["ai_costs"] for f in monthly_forecasts),
                "growth_rate": growth_rate * 100,
                "confidence_level": 85
            },
            "scenario_analysis": {
                "best_case": sum(f["optimistic"] for f in monthly_forecasts),
                "worst_case": sum(f["conservative"] for f in monthly_forecasts),
                "probability_distribution": {
                    "conservative": 0.2,
                    "base": 0.6,
                    "optimistic": 0.2
                }
            },
            "key_assumptions": [
                "8% annual cost growth driven by AI expansion",
                "Seasonal patterns continue based on historical data",
                "No major technology disruptions",
                "Current vendor pricing remains stable",
                "Infrastructure scaling matches business growth"
            ],
            "risk_factors": [
                "Cloud provider price increases",
                "AI model complexity growth",
                "Talent market inflation",
                "Regulatory compliance costs"
            ]
        }

    def _analyze_vendor_costs(self, time_period: str) -> Dict[str, Any]:
        """Analyze vendor costs and performance."""

        vendors = {
            "cloud_providers": {
                "aws": {
                    "monthly_spend": 4200000,
                    "services": ["EC2", "S3", "SageMaker", "Lambda"],
                    "growth_rate": 12.5,
                    "contract_terms": "Pay-as-you-go with reserved instances",
                    "optimization_score": 78,
                    "relationship_score": 85
                },
                "azure": {
                    "monthly_spend": 2800000,
                    "services": ["Virtual Machines", "Blob Storage", "AI/ML"],
                    "growth_rate": 8.2,
                    "contract_terms": "Enterprise agreement",
                    "optimization_score": 82,
                    "relationship_score": 80
                },
                "gcp": {
                    "monthly_spend": 1500000,
                    "services": ["Compute Engine", "Cloud Storage", "TPU"],
                    "growth_rate": 15.8,
                    "contract_terms": "Committed use discounts",
                    "optimization_score": 75,
                    "relationship_score": 78
                }
            },
            "ai_platforms": {
                "openai": {
                    "monthly_spend": 1200000,
                    "services": ["GPT-4", "GPT-3.5", "Embeddings"],
                    "growth_rate": 25.5,
                    "usage_efficiency": 87,
                    "cost_per_request": 0.048
                },
                "anthropic": {
                    "monthly_spend": 400000,
                    "services": ["Claude-3", "Claude-2"],
                    "growth_rate": 18.2,
                    "usage_efficiency": 92,
                    "cost_per_request": 0.052
                }
            },
            "software_vendors": {
                "enterprise_software": {
                    "monthly_spend": 350000,
                    "license_type": "Enterprise",
                    "renewal_date": "2024-12-31",
                    "utilization_rate": 72,
                    "cost_per_user": 125
                },
                "development_tools": {
                    "monthly_spend": 125000,
                    "license_type": "Team",
                    "renewal_date": "2024-06-30",
                    "utilization_rate": 89,
                    "cost_per_developer": 280
                }
            }
        }

        return {
            "vendor_analysis": vendors,
            "spend_distribution": {
                "total_vendor_spend": 9575000,
                "top_5_vendors": [
                    {"vendor": "AWS", "spend": 4200000, "percentage": 43.9},
                    {"vendor": "Azure", "spend": 2800000, "percentage": 29.2},
                    {"vendor": "GCP", "spend": 1500000, "percentage": 15.7},
                    {"vendor": "OpenAI", "spend": 1200000, "percentage": 12.5},
                    {"vendor": "Anthropic", "spend": 400000, "percentage": 4.2}
                ]
            },
            "vendor_performance": {
                "cost_optimization_opportunities": [
                    {"vendor": "AWS", "opportunity": "Reserved Instance expansion", "savings": 420000},
                    {"vendor": "Enterprise Software", "opportunity": "License optimization", "savings": 84000},
                    {"vendor": "OpenAI", "opportunity": "Request batching", "savings": 180000}
                ],
                "contract_renewals": [
                    {"vendor": "Enterprise Software", "renewal_date": "2024-12-31", "spend": 4200000, "negotiation_potential": 8.5},
                    {"vendor": "Development Tools", "renewal_date": "2024-06-30", "spend": 1500000, "negotiation_potential": 5.2}
                ]
            },
            "vendor_risk_assessment": {
                "high_concentration_risk": ["AWS"],  # >40% of spend
                "contract_dependency": ["Enterprise Software"],
                "price_volatility_risk": ["OpenAI", "Anthropic"],
                "alternative_options": {
                    "cloud_providers": "Multi-cloud strategy in place",
                    "ai_platforms": "Evaluating additional providers",
                    "software": "Open source alternatives identified"
                }
            }
        }

    def _analyze_department_costs(self, time_period: str) -> Dict[str, Any]:
        """Analyze costs by department and business unit."""

        departments = {
            "engineering": {
                "total_costs": 45000000,
                "headcount": 280,
                "cost_per_employee": 160714,
                "cost_categories": {
                    "personnel": 35000000,
                    "infrastructure": 6500000,
                    "tools_software": 2200000,
                    "training": 800000,
                    "other": 500000
                },
                "ai_related_costs": 12000000,
                "productivity_metrics": {
                    "code_commits": 15680,
                    "features_delivered": 245,
                    "bugs_resolved": 1850
                }
            },
            "data_science": {
                "total_costs": 25000000,
                "headcount": 85,
                "cost_per_employee": 294118,
                "cost_categories": {
                    "personnel": 18000000,
                    "ai_infrastructure": 4200000,
                    "data_storage": 1800000,
                    "tools_software": 800000,
                    "research": 200000
                },
                "ai_related_costs": 6200000,
                "productivity_metrics": {
                    "models_trained": 125,
                    "experiments_run": 1850,
                    "accuracy_improvement": 4.2
                }
            },
            "operations": {
                "total_costs": 15000000,
                "headcount": 120,
                "cost_per_employee": 125000,
                "cost_categories": {
                    "personnel": 12000000,
                    "infrastructure": 2200000,
                    "monitoring_tools": 500000,
                    "security": 300000
                },
                "ai_related_costs": 800000,
                "productivity_metrics": {
                    "uptime_percentage": 99.8,
                    "incidents_resolved": 425,
                    "automation_scripts": 68
                }
            },
            "sales_marketing": {
                "total_costs": 18000000,
                "headcount": 150,
                "cost_per_employee": 120000,
                "cost_categories": {
                    "personnel": 15000000,
                    "marketing_campaigns": 1800000,
                    "sales_tools": 800000,
                    "travel": 400000
                },
                "ai_related_costs": 300000,
                "productivity_metrics": {
                    "leads_generated": 8500,
                    "deals_closed": 485,
                    "revenue_per_employee": 833333
                }
            }
        }

        return {
            "department_analysis": departments,
            "cost_efficiency_metrics": {
                "revenue_per_employee": {
                    "engineering": 125000000 / 280,
                    "data_science": 125000000 / 85,
                    "operations": 125000000 / 120,
                    "sales_marketing": 125000000 / 150
                },
                "ai_investment_ratio": {
                    "engineering": 12000000 / 45000000,
                    "data_science": 6200000 / 25000000,
                    "operations": 800000 / 15000000,
                    "sales_marketing": 300000 / 18000000
                }
            },
            "benchmarking": {
                "cost_per_employee_vs_industry": {
                    "engineering": {"internal": 160714, "industry_avg": 175000, "percentile": 35},
                    "data_science": {"internal": 294118, "industry_avg": 285000, "percentile": 55},
                    "operations": {"internal": 125000, "industry_avg": 135000, "percentile": 25},
                    "sales_marketing": {"internal": 120000, "industry_avg": 125000, "percentile": 40}
                }
            },
            "optimization_recommendations": [
                {
                    "department": "Engineering",
                    "recommendation": "Consolidate development tools",
                    "potential_savings": 280000,
                    "impact": "low"
                },
                {
                    "department": "Data Science",
                    "recommendation": "Optimize GPU utilization",
                    "potential_savings": 520000,
                    "impact": "medium"
                },
                {
                    "department": "Operations",
                    "recommendation": "Automate monitoring workflows",
                    "potential_savings": 185000,
                    "impact": "low"
                }
            ]
        }

    def _generate_drill_down_analysis(self, time_period: str) -> Dict[str, Any]:
        """Generate detailed drill-down analysis for specific cost areas."""

        return {
            "ai_training_deep_dive": {
                "cost_by_model_type": {
                    "llm_training": {"cost": 3100000, "models": 45, "avg_cost": 68889},
                    "computer_vision": {"cost": 750000, "models": 28, "avg_cost": 26786},
                    "nlp_specialized": {"cost": 350000, "models": 52, "avg_cost": 6731}
                },
                "resource_utilization": {
                    "gpu_hours_by_type": {
                        "A100": {"hours": 15680, "utilization": 89.2, "cost_per_hour": 32.77},
                        "V100": {"hours": 8920, "utilization": 85.5, "cost_per_hour": 24.50},
                        "T4": {"hours": 3400, "utilization": 82.1, "cost_per_hour": 12.80}
                    }
                }
            },
            "infrastructure_deep_dive": {
                "cost_by_service": {
                    "compute": {"cost": 4500000, "instances": 1250, "avg_monthly": 3600},
                    "storage": {"cost": 1800000, "tb_stored": 2400, "cost_per_tb": 750},
                    "networking": {"cost": 800000, "data_transfer_tb": 1600, "cost_per_tb": 500}
                }
            }
        }

    def _perform_correlation_analysis(self, time_period: str) -> Dict[str, Any]:
        """Perform correlation analysis between costs and business metrics."""

        correlations = {
            "cost_revenue_correlation": {
                "ai_costs_vs_revenue": 0.78,
                "infrastructure_vs_revenue": 0.65,
                "personnel_vs_revenue": 0.45
            },
            "efficiency_correlations": {
                "gpu_utilization_vs_cost_efficiency": -0.82,
                "automation_level_vs_cost_reduction": -0.75,
                "team_size_vs_productivity": 0.68
            }
        }

        return correlations

    def _perform_statistical_analysis(self, time_period: str) -> Dict[str, Any]:
        """Perform statistical analysis on financial data."""

        return {
            "variance_analysis": {
                "cost_variance": 0.15,
                "revenue_variance": 0.08,
                "margin_variance": 0.22
            },
            "regression_analysis": {
                "cost_growth_model": {
                    "r_squared": 0.89,
                    "coefficients": {"time": 0.08, "ai_investment": 0.65}
                }
            }
        }

    def _generate_visualizations(self, time_period: str, analysis_type: str) -> Dict[str, Any]:
        """Generate comprehensive visualizations for financial analysis."""

        visualizations = {}

        if VIZLYCHART_AVAILABLE:
            # Cost breakdown waterfall chart
            visualizations["cost_waterfall"] = self._create_cost_waterfall_chart()

            # Budget vs actual comparison
            visualizations["budget_comparison"] = self._create_budget_comparison_chart()

            # Cost trend analysis
            visualizations["cost_trends"] = self._create_cost_trend_chart()

            # Variance analysis heatmap
            visualizations["variance_heatmap"] = self._create_variance_heatmap()

            # Department cost analysis
            visualizations["department_costs"] = self._create_department_cost_chart()

            # AI cost breakdown
            visualizations["ai_cost_breakdown"] = self._create_ai_cost_breakdown_chart()

            if analysis_type == "detailed":
                # Additional detailed visualizations
                visualizations["correlation_matrix"] = self._create_correlation_matrix()
                visualizations["forecast_scenarios"] = self._create_forecast_scenario_chart()

        return visualizations

    def _create_cost_waterfall_chart(self) -> Dict[str, Any]:
        """Create cost waterfall chart showing period-over-period changes."""

        waterfall_data = [
            {"category": "Previous Period", "value": 95200000, "type": "base"},
            {"category": "AI Training Increase", "value": 420000, "type": "increase"},
            {"category": "Infrastructure Growth", "value": 580000, "type": "increase"},
            {"category": "Efficiency Improvements", "value": -320000, "type": "decrease"},
            {"category": "New Initiatives", "value": 1620000, "type": "increase"},
            {"category": "Current Period", "value": 97500000, "type": "total"}
        ]

        if VIZLYCHART_AVAILABLE:
            chart = FinancialChart()
            return chart.create_waterfall_chart(
                data=waterfall_data,
                title="Cost Analysis - Period over Period",
                subtitle="Breakdown of cost changes",
                theme="financial_analyst",
                currency="USD"
            )
        else:
            return {"chart_type": "waterfall", "data": waterfall_data}

    def _create_budget_comparison_chart(self) -> Dict[str, Any]:
        """Create budget vs actual comparison chart."""

        comparison_data = [
            {"category": "AI & ML", "budget": 7500000, "actual": 8100000, "variance": 8.0},
            {"category": "Infrastructure", "budget": 12000000, "actual": 12500000, "variance": 4.2},
            {"category": "Personnel", "budget": 44000000, "actual": 43500000, "variance": -1.1},
            {"category": "Software", "budget": 5800000, "actual": 5700000, "variance": -1.7}
        ]

        if VIZLYCHART_AVAILABLE:
            chart = FinancialChart()
            return chart.create_budget_comparison(
                data=comparison_data,
                title="Budget vs Actual Performance",
                theme="analyst_comparison"
            )
        else:
            return {"chart_type": "budget_comparison", "data": comparison_data}

    def _create_cost_trend_chart(self) -> Dict[str, Any]:
        """Create cost trend analysis chart."""

        trend_data = self._generate_trend_analysis("current_month")

        if VIZLYCHART_AVAILABLE:
            chart = AdvancedAnalytics()
            return chart.create_trend_analysis(
                data=trend_data["cost_trends"]["monthly_costs"],
                title="12-Month Cost Trend Analysis",
                metrics=["total_costs", "ai_costs", "infrastructure"],
                theme="analyst_trends"
            )
        else:
            return {"chart_type": "trend_analysis", "data": trend_data}

    def _create_variance_heatmap(self) -> Dict[str, Any]:
        """Create variance analysis heatmap."""

        variance_data = self._generate_variance_analysis("current_month")

        if VIZLYCHART_AVAILABLE:
            chart = AdvancedAnalytics()
            return chart.create_variance_heatmap(
                variances=variance_data["detailed_variances"]["budget_variances"],
                title="Budget Variance Analysis",
                theme="analyst_heatmap"
            )
        else:
            return {"chart_type": "variance_heatmap", "data": variance_data}

    def _create_department_cost_chart(self) -> Dict[str, Any]:
        """Create department cost analysis chart."""

        department_data = self._analyze_department_costs("current_month")

        if VIZLYCHART_AVAILABLE:
            chart = FinancialChart()
            return chart.create_department_analysis(
                departments=department_data["department_analysis"],
                title="Department Cost Analysis",
                theme="analyst_departments"
            )
        else:
            return {"chart_type": "department_analysis", "data": department_data}

    def _create_ai_cost_breakdown_chart(self) -> Dict[str, Any]:
        """Create AI cost breakdown visualization."""

        ai_data = self._generate_ai_cost_breakdown("current_month")

        if VIZLYCHART_AVAILABLE:
            chart = AdvancedAnalytics()
            return chart.create_ai_cost_breakdown(
                cost_data=ai_data["detailed_costs"],
                title="AI Cost Breakdown Analysis",
                theme="ai_analytics"
            )
        else:
            return {"chart_type": "ai_cost_breakdown", "data": ai_data}

    def _create_correlation_matrix(self) -> Dict[str, Any]:
        """Create correlation matrix visualization."""

        correlation_data = self._perform_correlation_analysis("current_month")

        if VIZLYCHART_AVAILABLE:
            chart = AdvancedAnalytics()
            return chart.create_correlation_matrix(
                correlations=correlation_data,
                title="Cost Correlation Analysis",
                theme="analyst_correlation"
            )
        else:
            return {"chart_type": "correlation_matrix", "data": correlation_data}

    def _create_forecast_scenario_chart(self) -> Dict[str, Any]:
        """Create forecast scenario analysis chart."""

        forecast_data = self._generate_financial_forecasts("current_month")

        if VIZLYCHART_AVAILABLE:
            chart = FinancialChart()
            return chart.create_scenario_analysis(
                forecasts=forecast_data["monthly_forecasts"],
                scenarios=forecast_data["scenario_analysis"],
                title="Financial Forecast Scenarios",
                theme="analyst_forecast"
            )
        else:
            return {"chart_type": "forecast_scenarios", "data": forecast_data}

    def export_analysis_report(self, dashboard_data: Dict[str, Any], format: str = "excel") -> str:
        """Export detailed analysis report."""

        report_id = f"finance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if format == "excel":
            # Generate comprehensive Excel workbook
            report_path = f"/exports/{report_id}.xlsx"
            logger.info(f"Generated Finance Analysis Excel report: {report_path}")

        elif format == "pdf":
            # Generate PDF report
            report_path = f"/exports/{report_id}.pdf"
            logger.info(f"Generated Finance Analysis PDF report: {report_path}")

        return report_path


# Initialize Finance Analyst Dashboard
finance_analyst_dashboard = FinanceAnalystDashboard()


def get_finance_analyst_dashboard() -> FinanceAnalystDashboard:
    """Get Finance Analyst dashboard instance."""
    return finance_analyst_dashboard