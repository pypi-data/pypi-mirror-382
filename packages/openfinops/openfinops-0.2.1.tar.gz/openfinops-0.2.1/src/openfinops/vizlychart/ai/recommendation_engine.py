"""
OpenFinOps - AI-Powered Recommendation Engine
Real ML-based recommendations for LLM operations optimization
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
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class RecommendationContext:
    """Context for generating recommendations"""
    current_metrics: Dict[str, float]
    historical_data: List[Dict[str, Any]]
    goals: List[str]  # 'cost_reduction', 'performance_improvement', 'reliability'
    constraints: Dict[str, Any]


@dataclass
class Recommendation:
    """Single AI recommendation"""
    recommendation_id: str
    category: str  # 'cost', 'performance', 'reliability', 'security'
    title: str
    description: str
    impact_score: float  # 0-1, higher = more impact
    confidence: float  # 0-1, model confidence
    priority: str  # 'high', 'medium', 'low'
    implementation_effort: str  # 'low', 'medium', 'high'
    expected_outcomes: Dict[str, float]
    action_items: List[str]
    reasoning: str
    supporting_data: Dict[str, Any]


class AIRecommendationEngine:
    """ML-powered recommendation system for LLM operations"""

    def __init__(self):
        self.models = {
            'cost_optimizer': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'performance_classifier': RandomForestClassifier(n_estimators=100, random_state=42),
            'anomaly_detector': None,  # Will be initialized later
            'usage_clusterer': KMeans(n_clusters=5, random_state=42)
        }

        self.scalers = {
            'features': StandardScaler(),
            'performance_targets': StandardScaler()
        }

        self.encoders = {
            'categorical': LabelEncoder()
        }

        self.feature_columns = [
            'tokens_per_minute', 'requests_per_hour', 'avg_response_time',
            'error_rate', 'cache_hit_rate', 'concurrent_users',
            'model_size_params', 'context_length', 'temperature',
            'cost_per_request', 'gpu_utilization', 'memory_usage'
        ]

        self.training_data: List[Dict[str, Any]] = []
        self.is_trained = False

        # Rule-based recommendation templates
        self.recommendation_templates = self._load_recommendation_templates()

    def _load_recommendation_templates(self) -> Dict[str, Dict]:
        """Load predefined recommendation templates"""
        return {
            'high_cost_per_token': {
                'category': 'cost',
                'title': 'Optimize Token Usage Efficiency',
                'base_description': 'High cost per token detected. Consider optimization strategies.',
                'action_items': [
                    'Implement response caching for similar queries',
                    'Optimize prompt engineering to reduce token usage',
                    'Consider using smaller models for simple tasks',
                    'Implement request batching where possible'
                ]
            },
            'low_cache_hit_rate': {
                'category': 'performance',
                'title': 'Improve Response Caching Strategy',
                'base_description': 'Low cache hit rate impacting performance and cost.',
                'action_items': [
                    'Implement semantic similarity caching',
                    'Increase cache size and retention time',
                    'Pre-warm cache with common queries',
                    'Add cache analytics and monitoring'
                ]
            },
            'high_error_rate': {
                'category': 'reliability',
                'title': 'Address High Error Rate',
                'base_description': 'Elevated error rate affecting user experience.',
                'action_items': [
                    'Investigate root cause of errors',
                    'Implement retry logic with exponential backoff',
                    'Add circuit breaker patterns',
                    'Set up comprehensive error monitoring'
                ]
            },
            'gpu_underutilization': {
                'category': 'performance',
                'title': 'Optimize GPU Resource Usage',
                'base_description': 'GPU resources are underutilized.',
                'action_items': [
                    'Increase batch size for training/inference',
                    'Consider model parallelism',
                    'Implement dynamic batching',
                    'Right-size GPU instances'
                ]
            },
            'model_size_optimization': {
                'category': 'cost',
                'title': 'Consider Model Size Optimization',
                'base_description': 'Large model usage where smaller models might suffice.',
                'action_items': [
                    'Evaluate task complexity requirements',
                    'Test smaller models for similar performance',
                    'Implement model routing based on query complexity',
                    'Consider fine-tuned smaller models'
                ]
            }
        }

    def add_training_data(self, data_point: Dict[str, Any]):
        """Add training data point"""
        self.training_data.append(data_point)

    def add_batch_training_data(self, data_points: List[Dict[str, Any]]):
        """Add multiple training data points"""
        self.training_data.extend(data_points)

    def _prepare_features(self, data_points: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare features for ML models"""
        features = []

        for point in data_points:
            feature_row = {}

            # Extract numeric features with defaults
            for col in self.feature_columns:
                feature_row[col] = point.get(col, 0.0)

            # Add derived features
            feature_row['cost_efficiency'] = (
                feature_row['tokens_per_minute'] / max(feature_row['cost_per_request'], 0.001)
            )
            feature_row['performance_score'] = (
                (1 - feature_row['error_rate']) * feature_row['cache_hit_rate'] *
                (1 / max(feature_row['avg_response_time'], 0.1))
            )

            # Time-based features
            timestamp = point.get('timestamp', time.time())
            dt = datetime.fromtimestamp(timestamp)
            feature_row['hour_of_day'] = dt.hour
            feature_row['day_of_week'] = dt.weekday()
            feature_row['is_weekend'] = dt.weekday() >= 5

            features.append(feature_row)

        return pd.DataFrame(features)

    def train_models(self, min_data_points: int = 50) -> bool:
        """Train ML models on collected data"""
        if len(self.training_data) < min_data_points:
            print(f"Need at least {min_data_points} data points for training")
            return False

        print(f"Training recommendation models on {len(self.training_data)} data points...")

        # Prepare features
        df = self._prepare_features(self.training_data)

        # Prepare feature matrix
        feature_cols = [col for col in df.columns if col not in ['cost_per_request', 'performance_score']]
        X = df[feature_cols].fillna(0)

        # Scale features
        X_scaled = self.scalers['features'].fit_transform(X)

        # Train cost optimization model
        if 'cost_per_request' in df.columns:
            y_cost = df['cost_per_request'].fillna(df['cost_per_request'].mean())
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_cost, test_size=0.2, random_state=42)

            self.models['cost_optimizer'].fit(X_train, y_train)
            y_pred = self.models['cost_optimizer'].predict(X_test)
            cost_mse = mean_squared_error(y_test, y_pred)
            print(f"Cost model MSE: {cost_mse:.4f}")

        # Train performance classifier
        if 'performance_score' in df.columns:
            # Create performance categories
            performance_scores = df['performance_score'].fillna(df['performance_score'].mean())
            performance_categories = pd.cut(performance_scores, bins=3, labels=['low', 'medium', 'high'])
            performance_encoded = self.encoders['categorical'].fit_transform(performance_categories)

            X_train, X_test, y_train, y_test = train_test_split(X_scaled, performance_encoded, test_size=0.2, random_state=42)

            self.models['performance_classifier'].fit(X_train, y_train)
            y_pred = self.models['performance_classifier'].predict(X_test)
            perf_accuracy = accuracy_score(y_test, y_pred)
            print(f"Performance model accuracy: {perf_accuracy:.4f}")

        # Train usage clusterer
        self.models['usage_clusterer'].fit(X_scaled)

        self.is_trained = True
        print("✅ AI recommendation models trained successfully")
        return True

    def generate_recommendations(self, context: RecommendationContext) -> List[Recommendation]:
        """Generate AI-powered recommendations"""
        recommendations = []

        # Rule-based recommendations
        rule_based = self._generate_rule_based_recommendations(context)
        recommendations.extend(rule_based)

        # ML-based recommendations (if trained)
        if self.is_trained:
            ml_based = self._generate_ml_based_recommendations(context)
            recommendations.extend(ml_based)

        # Rank and filter recommendations
        ranked_recommendations = self._rank_recommendations(recommendations, context)

        return ranked_recommendations[:10]  # Return top 10

    def _generate_rule_based_recommendations(self, context: RecommendationContext) -> List[Recommendation]:
        """Generate recommendations using rule-based logic"""
        recommendations = []
        metrics = context.current_metrics

        # High cost per token
        if metrics.get('cost_per_request', 0) > 0.05:  # Threshold: $0.05 per request
            template = self.recommendation_templates['high_cost_per_token']
            rec = self._create_recommendation_from_template(
                template,
                impact_score=0.8,
                confidence=0.9,
                context_data={'current_cost': metrics.get('cost_per_request', 0)}
            )
            recommendations.append(rec)

        # Low cache hit rate
        if metrics.get('cache_hit_rate', 1.0) < 0.5:
            template = self.recommendation_templates['low_cache_hit_rate']
            rec = self._create_recommendation_from_template(
                template,
                impact_score=0.7,
                confidence=0.85,
                context_data={'current_hit_rate': metrics.get('cache_hit_rate', 0)}
            )
            recommendations.append(rec)

        # High error rate
        if metrics.get('error_rate', 0) > 0.05:  # 5% error rate threshold
            template = self.recommendation_templates['high_error_rate']
            rec = self._create_recommendation_from_template(
                template,
                impact_score=0.9,
                confidence=0.95,
                context_data={'current_error_rate': metrics.get('error_rate', 0)}
            )
            recommendations.append(rec)

        # GPU underutilization
        if metrics.get('gpu_utilization', 0) < 0.6:  # 60% threshold
            template = self.recommendation_templates['gpu_underutilization']
            rec = self._create_recommendation_from_template(
                template,
                impact_score=0.6,
                confidence=0.8,
                context_data={'current_gpu_util': metrics.get('gpu_utilization', 0)}
            )
            recommendations.append(rec)

        # Model size optimization
        tokens_per_minute = metrics.get('tokens_per_minute', 0)
        model_size = metrics.get('model_size_params', 7e9)
        if model_size > 50e9 and tokens_per_minute < 1000:  # Large model, low usage
            template = self.recommendation_templates['model_size_optimization']
            rec = self._create_recommendation_from_template(
                template,
                impact_score=0.75,
                confidence=0.8,
                context_data={
                    'model_size': model_size,
                    'usage_rate': tokens_per_minute
                }
            )
            recommendations.append(rec)

        return recommendations

    def _generate_ml_based_recommendations(self, context: RecommendationContext) -> List[Recommendation]:
        """Generate recommendations using trained ML models"""
        recommendations = []

        if not self.is_trained:
            return recommendations

        # Prepare current metrics as features
        feature_data = [context.current_metrics]
        df = self._prepare_features(feature_data)

        # Get features for prediction
        feature_cols = [col for col in df.columns if col in self.feature_columns + ['cost_efficiency', 'performance_score', 'hour_of_day', 'day_of_week', 'is_weekend']]
        X = df[feature_cols].fillna(0)
        X_scaled = self.scalers['features'].transform(X)

        # Cost optimization prediction
        try:
            predicted_cost = self.models['cost_optimizer'].predict(X_scaled)[0]
            current_cost = context.current_metrics.get('cost_per_request', 0)

            if predicted_cost < current_cost * 0.8:  # 20% cost reduction potential
                rec = Recommendation(
                    recommendation_id=f"ml_cost_opt_{int(time.time())}",
                    category='cost',
                    title='ML-Identified Cost Optimization Opportunity',
                    description=f'Model predicts {((current_cost - predicted_cost) / current_cost * 100):.1f}% cost reduction potential',
                    impact_score=0.8,
                    confidence=0.7,
                    priority='high',
                    implementation_effort='medium',
                    expected_outcomes={'cost_reduction': current_cost - predicted_cost},
                    action_items=[
                        'Analyze usage patterns for optimization opportunities',
                        'Implement ML-recommended configuration changes',
                        'Monitor cost impact of changes',
                        'Fine-tune based on results'
                    ],
                    reasoning='Machine learning model identified patterns suggesting cost optimization potential',
                    supporting_data={'predicted_cost': predicted_cost, 'current_cost': current_cost}
                )
                recommendations.append(rec)
        except Exception as e:
            print(f"ML cost prediction error: {e}")

        # Performance classification
        try:
            performance_pred = self.models['performance_classifier'].predict_proba(X_scaled)[0]
            performance_categories = ['low', 'medium', 'high']

            # If predicted to be low/medium performance with high confidence
            if performance_pred[0] > 0.7 or performance_pred[1] > 0.7:  # Low or medium performance
                predicted_category = performance_categories[np.argmax(performance_pred)]

                rec = Recommendation(
                    recommendation_id=f"ml_perf_opt_{int(time.time())}",
                    category='performance',
                    title='ML-Identified Performance Improvement',
                    description=f'Model predicts current performance category: {predicted_category}',
                    impact_score=0.75,
                    confidence=max(performance_pred),
                    priority='medium' if predicted_category == 'medium' else 'high',
                    implementation_effort='medium',
                    expected_outcomes={'performance_improvement': 0.2},
                    action_items=[
                        'Implement performance optimization strategies',
                        'Monitor key performance metrics',
                        'A/B test optimization changes',
                        'Establish performance baselines'
                    ],
                    reasoning=f'ML model classified current performance as {predicted_category}',
                    supporting_data={'performance_probabilities': performance_pred.tolist()}
                )
                recommendations.append(rec)
        except Exception as e:
            print(f"ML performance prediction error: {e}")

        # Usage pattern clustering
        try:
            cluster = self.models['usage_clusterer'].predict(X_scaled)[0]
            cluster_centers = self.models['usage_clusterer'].cluster_centers_

            # Analyze cluster characteristics for recommendations
            rec = Recommendation(
                recommendation_id=f"ml_pattern_opt_{int(time.time())}",
                category='performance',
                title='Usage Pattern Optimization',
                description=f'Your usage pattern belongs to cluster {cluster}, suggesting specific optimizations',
                impact_score=0.6,
                confidence=0.7,
                priority='medium',
                implementation_effort='low',
                expected_outcomes={'efficiency_improvement': 0.15},
                action_items=[
                    f'Optimize for cluster {cluster} characteristics',
                    'Benchmark against similar usage patterns',
                    'Implement cluster-specific best practices',
                    'Monitor pattern changes over time'
                ],
                reasoning=f'ML clustering identified your usage pattern as cluster {cluster}',
                supporting_data={'cluster_id': int(cluster), 'cluster_center': cluster_centers[cluster].tolist()}
            )
            recommendations.append(rec)
        except Exception as e:
            print(f"ML clustering error: {e}")

        return recommendations

    def _create_recommendation_from_template(self, template: Dict, impact_score: float,
                                           confidence: float, context_data: Dict) -> Recommendation:
        """Create recommendation from template"""
        return Recommendation(
            recommendation_id=f"rule_{template['category']}_{int(time.time())}",
            category=template['category'],
            title=template['title'],
            description=template['base_description'],
            impact_score=impact_score,
            confidence=confidence,
            priority='high' if impact_score > 0.8 else 'medium' if impact_score > 0.6 else 'low',
            implementation_effort='medium',  # Default
            expected_outcomes={f'{template["category"]}_improvement': impact_score * 0.3},
            action_items=template['action_items'],
            reasoning=f"Rule-based analysis of {template['category']} metrics",
            supporting_data=context_data
        )

    def _rank_recommendations(self, recommendations: List[Recommendation],
                            context: RecommendationContext) -> List[Recommendation]:
        """Rank recommendations by priority and relevance"""

        # Calculate composite score
        for rec in recommendations:
            # Base score from impact and confidence
            base_score = rec.impact_score * rec.confidence

            # Adjust based on user goals
            goal_bonus = 0
            if rec.category in context.goals:
                goal_bonus = 0.2

            # Adjust based on priority
            priority_multiplier = {'high': 1.2, 'medium': 1.0, 'low': 0.8}
            priority_bonus = priority_multiplier.get(rec.priority, 1.0)

            # Adjust based on implementation effort
            effort_penalty = {'low': 0, 'medium': 0.1, 'high': 0.2}
            effort_adjustment = effort_penalty.get(rec.implementation_effort, 0.1)

            # Final composite score
            rec.composite_score = (base_score + goal_bonus) * priority_bonus - effort_adjustment

        # Sort by composite score
        return sorted(recommendations, key=lambda x: x.composite_score, reverse=True)

    def explain_recommendation(self, recommendation: Recommendation) -> Dict[str, Any]:
        """Provide detailed explanation for a recommendation"""
        explanation = {
            'recommendation_id': recommendation.recommendation_id,
            'title': recommendation.title,
            'detailed_reasoning': recommendation.reasoning,
            'confidence_breakdown': {
                'model_confidence': recommendation.confidence,
                'impact_assessment': recommendation.impact_score,
                'priority_level': recommendation.priority
            },
            'expected_benefits': recommendation.expected_outcomes,
            'implementation_plan': {
                'effort_level': recommendation.implementation_effort,
                'action_items': recommendation.action_items,
                'estimated_timeline': self._estimate_timeline(recommendation.implementation_effort)
            },
            'supporting_evidence': recommendation.supporting_data,
            'risk_assessment': self._assess_risks(recommendation)
        }

        return explanation

    def _estimate_timeline(self, effort_level: str) -> str:
        """Estimate implementation timeline based on effort"""
        timelines = {
            'low': '1-2 weeks',
            'medium': '3-6 weeks',
            'high': '2-3 months'
        }
        return timelines.get(effort_level, '4-8 weeks')

    def _assess_risks(self, recommendation: Recommendation) -> Dict[str, str]:
        """Assess implementation risks"""
        risk_levels = {
            'cost': 'low',  # Cost optimizations usually low risk
            'performance': 'medium',  # Performance changes need testing
            'reliability': 'high',  # Reliability changes need careful testing
            'security': 'high'  # Security changes need thorough review
        }

        return {
            'overall_risk': risk_levels.get(recommendation.category, 'medium'),
            'risk_factors': [
                'Monitor metrics during implementation',
                'Implement changes gradually',
                'Have rollback plan ready',
                'Test in staging environment first'
            ]
        }

    def export_recommendations(self, recommendations: List[Recommendation],
                             filename: Optional[str] = None) -> str:
        """Export recommendations to JSON file"""
        if filename is None:
            filename = f"ai_recommendations_{int(time.time())}.json"

        export_data = {
            'timestamp': time.time(),
            'total_recommendations': len(recommendations),
            'recommendations': [
                {
                    'id': rec.recommendation_id,
                    'category': rec.category,
                    'title': rec.title,
                    'description': rec.description,
                    'impact_score': rec.impact_score,
                    'confidence': rec.confidence,
                    'priority': rec.priority,
                    'implementation_effort': rec.implementation_effort,
                    'expected_outcomes': rec.expected_outcomes,
                    'action_items': rec.action_items,
                    'reasoning': rec.reasoning,
                    'supporting_data': rec.supporting_data
                } for rec in recommendations
            ]
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"📋 Recommendations exported to: {filename}")
        return filename


# Example usage
if __name__ == "__main__":
    # Create recommendation engine
    engine = AIRecommendationEngine()

    # Add training data
    training_data = []
    for i in range(100):
        data_point = {
            'timestamp': time.time() - i * 3600,
            'tokens_per_minute': np.random.randint(100, 2000),
            'requests_per_hour': np.random.randint(10, 500),
            'avg_response_time': np.random.uniform(0.5, 5.0),
            'error_rate': np.random.uniform(0, 0.1),
            'cache_hit_rate': np.random.uniform(0.3, 0.9),
            'concurrent_users': np.random.randint(1, 100),
            'model_size_params': np.random.choice([7e9, 13e9, 70e9]),
            'context_length': np.random.choice([2048, 4096, 8192]),
            'temperature': np.random.uniform(0.1, 1.0),
            'cost_per_request': np.random.uniform(0.01, 0.1),
            'gpu_utilization': np.random.uniform(0.3, 0.95),
            'memory_usage': np.random.uniform(0.4, 0.9)
        }
        training_data.append(data_point)

    engine.add_batch_training_data(training_data)

    # Train models
    engine.train_models()

    # Create context for recommendations
    context = RecommendationContext(
        current_metrics={
            'tokens_per_minute': 500,
            'requests_per_hour': 100,
            'avg_response_time': 2.0,
            'error_rate': 0.08,  # High error rate
            'cache_hit_rate': 0.3,  # Low cache hit rate
            'concurrent_users': 25,
            'model_size_params': 70e9,  # Large model
            'cost_per_request': 0.07,  # High cost
            'gpu_utilization': 0.45  # Low GPU utilization
        },
        historical_data=[],
        goals=['cost_reduction', 'performance_improvement'],
        constraints={'budget': 10000, 'implementation_time': '6 weeks'}
    )

    # Generate recommendations
    recommendations = engine.generate_recommendations(context)

    print(f"Generated {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Category: {rec.category}")
        print(f"   Impact: {rec.impact_score:.2f}, Confidence: {rec.confidence:.2f}")
        print(f"   Priority: {rec.priority}")
        print(f"   Description: {rec.description}")

    # Export recommendations
    engine.export_recommendations(recommendations)