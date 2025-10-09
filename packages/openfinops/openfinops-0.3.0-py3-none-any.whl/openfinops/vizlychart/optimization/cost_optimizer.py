"""
OpenFinOps - Cost Optimization Engine
ML-powered cost optimization for LLM and AI infrastructure
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
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import json
import time
from datetime import datetime, timedelta


@dataclass
class CostDataPoint:
    """Single cost observation"""
    timestamp: float
    service_type: str  # 'llm_api', 'training', 'inference', 'storage', 'compute'
    provider: str  # 'openai', 'anthropic', 'aws', 'azure', 'gcp'
    resource_id: str
    cost_usd: float
    usage_metrics: Dict[str, float]  # tokens, compute_hours, storage_gb, etc.
    metadata: Dict[str, Any]


@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation"""
    recommendation_id: str
    recommendation_type: str
    current_cost: float
    projected_savings: float
    confidence: float
    description: str
    implementation_steps: List[str]
    risk_level: str  # 'low', 'medium', 'high'
    estimated_implementation_time: str


class CostOptimizationEngine:
    """ML-powered cost optimization engine"""

    def __init__(self, model_path: Optional[str] = None):
        self.cost_data: List[CostDataPoint] = []
        self.models = {
            'cost_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
            'anomaly_detector': IsolationForest(contamination=0.1, random_state=42),
            'usage_clusterer': KMeans(n_clusters=5, random_state=42)
        }
        self.scalers = {
            'features': StandardScaler(),
            'targets': StandardScaler()
        }
        self.feature_columns = [
            'hour_of_day', 'day_of_week', 'tokens_per_request',
            'requests_per_hour', 'avg_response_length', 'model_size_params',
            'concurrent_users', 'cache_hit_rate'
        ]
        self.is_trained = False

        if model_path:
            self.load_models(model_path)

    def add_cost_data(self, cost_point: CostDataPoint):
        """Add new cost data point"""
        self.cost_data.append(cost_point)

    def add_batch_cost_data(self, cost_points: List[CostDataPoint]):
        """Add multiple cost data points"""
        self.cost_data.extend(cost_points)

    def _extract_features(self, cost_points: List[CostDataPoint]) -> pd.DataFrame:
        """Extract features for ML models"""
        features = []

        for point in cost_points:
            dt = datetime.fromtimestamp(point.timestamp)

            feature_row = {
                'timestamp': point.timestamp,
                'hour_of_day': dt.hour,
                'day_of_week': dt.weekday(),
                'service_type': point.service_type,
                'provider': point.provider,
                'cost_usd': point.cost_usd,

                # Usage metrics with defaults
                'tokens_per_request': point.usage_metrics.get('tokens_per_request', 0),
                'requests_per_hour': point.usage_metrics.get('requests_per_hour', 0),
                'avg_response_length': point.usage_metrics.get('avg_response_length', 0),
                'model_size_params': point.usage_metrics.get('model_size_params', 7e9),  # Default 7B
                'concurrent_users': point.usage_metrics.get('concurrent_users', 1),
                'cache_hit_rate': point.usage_metrics.get('cache_hit_rate', 0.0),
                'gpu_hours': point.usage_metrics.get('gpu_hours', 0),
                'storage_gb': point.usage_metrics.get('storage_gb', 0),
            }
            features.append(feature_row)

        return pd.DataFrame(features)

    def train_models(self, min_data_points: int = 100) -> bool:
        """Train ML models on collected cost data"""
        if len(self.cost_data) < min_data_points:
            print(f"Need at least {min_data_points} data points, have {len(self.cost_data)}")
            return False

        print(f"Training cost optimization models on {len(self.cost_data)} data points...")

        # Extract features
        df = self._extract_features(self.cost_data)

        # Prepare features for training
        feature_df = df[self.feature_columns].fillna(0)
        cost_target = df['cost_usd'].values

        # Scale features
        X_scaled = self.scalers['features'].fit_transform(feature_df)
        y_scaled = self.scalers['targets'].fit_transform(cost_target.reshape(-1, 1)).flatten()

        # Train cost predictor
        self.models['cost_predictor'].fit(X_scaled, y_scaled)

        # Train anomaly detector
        self.models['anomaly_detector'].fit(X_scaled)

        # Train usage clusterer
        self.models['usage_clusterer'].fit(X_scaled)

        self.is_trained = True
        print("✅ Models trained successfully")
        return True

    def predict_cost(self, usage_metrics: Dict[str, float],
                    service_type: str = "llm_api",
                    provider: str = "openai") -> float:
        """Predict cost for given usage patterns"""
        if not self.is_trained:
            return 0.0

        # Create feature vector
        dt = datetime.now()
        features = pd.DataFrame([{
            'hour_of_day': dt.hour,
            'day_of_week': dt.weekday(),
            'tokens_per_request': usage_metrics.get('tokens_per_request', 0),
            'requests_per_hour': usage_metrics.get('requests_per_hour', 0),
            'avg_response_length': usage_metrics.get('avg_response_length', 0),
            'model_size_params': usage_metrics.get('model_size_params', 7e9),
            'concurrent_users': usage_metrics.get('concurrent_users', 1),
            'cache_hit_rate': usage_metrics.get('cache_hit_rate', 0.0),
        }])

        # Scale features
        X_scaled = self.scalers['features'].transform(features)

        # Predict scaled cost
        cost_scaled = self.models['cost_predictor'].predict(X_scaled)[0]

        # Inverse transform to get actual cost
        cost_actual = self.scalers['targets'].inverse_transform([[cost_scaled]])[0][0]

        return max(0, cost_actual)  # Ensure non-negative

    def detect_cost_anomalies(self) -> List[Dict[str, Any]]:
        """Detect unusual cost patterns"""
        if not self.is_trained or len(self.cost_data) < 10:
            return []

        # Extract recent data
        df = self._extract_features(self.cost_data[-100:])  # Last 100 points
        X = self.scalers['features'].transform(df[self.feature_columns].fillna(0))

        # Detect anomalies
        anomaly_scores = self.models['anomaly_detector'].decision_function(X)
        is_anomaly = self.models['anomaly_detector'].predict(X) == -1

        anomalies = []
        for i, (idx, is_anom) in enumerate(zip(df.index, is_anomaly)):
            if is_anom:
                point = self.cost_data[-(len(df) - i)]
                anomalies.append({
                    'timestamp': point.timestamp,
                    'service_type': point.service_type,
                    'provider': point.provider,
                    'cost_usd': point.cost_usd,
                    'anomaly_score': anomaly_scores[i],
                    'severity': 'high' if anomaly_scores[i] < -0.5 else 'medium'
                })

        return anomalies

    def generate_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate cost optimization recommendations"""
        if not self.is_trained:
            return []

        recommendations = []

        # Analyze usage patterns
        df = self._extract_features(self.cost_data)

        # 1. High-cost service analysis
        service_costs = df.groupby('service_type')['cost_usd'].agg(['sum', 'mean', 'count'])
        high_cost_services = service_costs.nlargest(3, 'sum')

        for service, stats in high_cost_services.iterrows():
            if stats['sum'] > 100:  # Only if significant cost
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"service_opt_{service}_{int(time.time())}",
                    recommendation_type="service_optimization",
                    current_cost=stats['sum'],
                    projected_savings=stats['sum'] * 0.15,  # Conservative 15% savings
                    confidence=0.8,
                    description=f"Optimize {service} usage - accounts for ${stats['sum']:.2f} ({stats['count']} requests)",
                    implementation_steps=[
                        f"Review {service} usage patterns",
                        "Implement caching strategies",
                        "Consider model size optimization",
                        "Set up usage alerts"
                    ],
                    risk_level="low",
                    estimated_implementation_time="1-2 weeks"
                ))

        # 2. Provider cost comparison
        provider_costs = df.groupby('provider')['cost_usd'].agg(['sum', 'mean'])
        if len(provider_costs) > 1:
            cheapest_provider = provider_costs.idxmin()['mean']
            most_expensive = provider_costs.idxmax()['sum']

            cost_diff = provider_costs.loc[most_expensive, 'sum'] - provider_costs.loc[cheapest_provider, 'sum']

            if cost_diff > 50:  # Significant difference
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"provider_switch_{int(time.time())}",
                    recommendation_type="provider_optimization",
                    current_cost=provider_costs.loc[most_expensive, 'sum'],
                    projected_savings=cost_diff * 0.7,  # Realistic savings after migration
                    confidence=0.7,
                    description=f"Consider migrating from {most_expensive} to {cheapest_provider}",
                    implementation_steps=[
                        "Benchmark model performance across providers",
                        "Test API compatibility",
                        "Implement gradual migration",
                        "Monitor quality metrics"
                    ],
                    risk_level="medium",
                    estimated_implementation_time="4-6 weeks"
                ))

        # 3. Usage pattern optimization
        hourly_costs = df.groupby('hour_of_day')['cost_usd'].mean()
        peak_hours = hourly_costs.nlargest(6).index.tolist()
        off_peak_hours = hourly_costs.nsmallest(6).index.tolist()

        if len(peak_hours) > 0 and hourly_costs.max() / hourly_costs.min() > 2:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"schedule_opt_{int(time.time())}",
                recommendation_type="scheduling_optimization",
                current_cost=hourly_costs.sum(),
                projected_savings=hourly_costs.sum() * 0.20,
                confidence=0.6,
                description="Optimize request scheduling to avoid peak cost periods",
                implementation_steps=[
                    f"Shift non-urgent requests to off-peak hours: {off_peak_hours}",
                    "Implement request queuing system",
                    "Set up dynamic rate limiting",
                    "Use batch processing where possible"
                ],
                risk_level="low",
                estimated_implementation_time="2-3 weeks"
            ))

        # 4. Cache optimization
        avg_cache_hit_rate = df['cache_hit_rate'].mean()
        if avg_cache_hit_rate < 0.5:  # Low cache hit rate
            total_requests = df['requests_per_hour'].sum()
            potential_cached = total_requests * (0.7 - avg_cache_hit_rate)  # Target 70% hit rate
            avg_cost_per_request = df['cost_usd'].sum() / total_requests if total_requests > 0 else 0

            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"cache_opt_{int(time.time())}",
                recommendation_type="caching_optimization",
                current_cost=df['cost_usd'].sum(),
                projected_savings=potential_cached * avg_cost_per_request,
                confidence=0.85,
                description=f"Improve caching strategy - current hit rate: {avg_cache_hit_rate:.1%}",
                implementation_steps=[
                    "Implement intelligent response caching",
                    "Add semantic similarity matching for cache hits",
                    "Set up cache warming for common queries",
                    "Monitor cache performance metrics"
                ],
                risk_level="low",
                estimated_implementation_time="1-2 weeks"
            ))

        return recommendations

    def calculate_cost_savings_potential(self) -> Dict[str, float]:
        """Calculate potential cost savings across different optimization areas"""
        if not self.cost_data:
            return {}

        df = self._extract_features(self.cost_data)
        total_cost = df['cost_usd'].sum()

        savings_potential = {
            'total_current_cost': total_cost,
            'caching_savings': total_cost * 0.15,  # 15% through better caching
            'provider_optimization_savings': total_cost * 0.12,  # 12% through provider optimization
            'model_size_optimization_savings': total_cost * 0.20,  # 20% through model optimization
            'scheduling_optimization_savings': total_cost * 0.10,  # 10% through better scheduling
            'total_potential_savings': total_cost * 0.35,  # Conservative total estimate
            'annual_projected_savings': total_cost * 0.35 * 12  # Annualized
        }

        return savings_potential

    def export_cost_analysis(self, filename: Optional[str] = None) -> str:
        """Export comprehensive cost analysis"""
        if filename is None:
            filename = f"cost_analysis_{int(time.time())}.json"

        analysis = {
            'analysis_timestamp': time.time(),
            'data_points_analyzed': len(self.cost_data),
            'time_range': {
                'start': min(p.timestamp for p in self.cost_data) if self.cost_data else 0,
                'end': max(p.timestamp for p in self.cost_data) if self.cost_data else 0
            },
            'cost_breakdown': {},
            'anomalies': self.detect_cost_anomalies(),
            'recommendations': [
                {
                    'id': r.recommendation_id,
                    'type': r.recommendation_type,
                    'current_cost': r.current_cost,
                    'projected_savings': r.projected_savings,
                    'confidence': r.confidence,
                    'description': r.description,
                    'implementation_steps': r.implementation_steps,
                    'risk_level': r.risk_level,
                    'estimated_time': r.estimated_implementation_time
                } for r in self.generate_optimization_recommendations()
            ],
            'savings_potential': self.calculate_cost_savings_potential()
        }

        if self.cost_data:
            df = self._extract_features(self.cost_data)
            analysis['cost_breakdown'] = {
                'by_service': df.groupby('service_type')['cost_usd'].sum().to_dict(),
                'by_provider': df.groupby('provider')['cost_usd'].sum().to_dict(),
                'daily_average': df['cost_usd'].sum() / max(1, (df['timestamp'].max() - df['timestamp'].min()) / 86400),
                'total_cost': df['cost_usd'].sum()
            }

        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"📊 Cost analysis exported to: {filename}")
        return filename

    def save_models(self, filepath: str):
        """Save trained models to disk"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        print(f"💾 Models saved to: {filepath}")

    def load_models(self, filepath: str):
        """Load trained models from disk"""
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data['is_trained']
            print(f"📁 Models loaded from: {filepath}")
        except Exception as e:
            print(f"❌ Failed to load models: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Create optimizer
    optimizer = CostOptimizationEngine()

    # Generate sample cost data
    import random

    for i in range(200):
        timestamp = time.time() - (200 - i) * 3600  # Last 200 hours

        cost_point = CostDataPoint(
            timestamp=timestamp,
            service_type=random.choice(['llm_api', 'training', 'inference']),
            provider=random.choice(['openai', 'anthropic', 'azure']),
            resource_id=f"resource_{i % 10}",
            cost_usd=random.uniform(0.1, 50.0),
            usage_metrics={
                'tokens_per_request': random.randint(100, 2000),
                'requests_per_hour': random.randint(10, 1000),
                'avg_response_length': random.randint(50, 500),
                'model_size_params': random.choice([7e9, 13e9, 70e9]),
                'concurrent_users': random.randint(1, 100),
                'cache_hit_rate': random.uniform(0.1, 0.9)
            },
            metadata={'region': 'us-east-1'}
        )
        optimizer.add_cost_data(cost_point)

    # Train models
    optimizer.train_models()

    # Generate recommendations
    recommendations = optimizer.generate_optimization_recommendations()
    print(f"\nGenerated {len(recommendations)} optimization recommendations:")
    for rec in recommendations:
        print(f"- {rec.description}")
        print(f"  Projected savings: ${rec.projected_savings:.2f}")
        print(f"  Confidence: {rec.confidence:.1%}")
        print()

    # Detect anomalies
    anomalies = optimizer.detect_cost_anomalies()
    print(f"Detected {len(anomalies)} cost anomalies")

    # Export analysis
    optimizer.export_cost_analysis()

    # Save models
    optimizer.save_models("cost_optimization_models.joblib")