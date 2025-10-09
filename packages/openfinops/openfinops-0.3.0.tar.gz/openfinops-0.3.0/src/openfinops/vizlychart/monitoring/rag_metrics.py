"""
OpenFinOps - RAG Retrieval Accuracy Metrics
Real implementation of NDCG, MRR, MAP, and other retrieval quality metrics
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
import math
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from collections import defaultdict
import json
import time


@dataclass
class RetrievalResult:
    """Single retrieval result with relevance score"""
    document_id: str
    content: str
    score: float
    relevance: Optional[float] = None  # Ground truth relevance (0-1 or 0-4 scale)
    metadata: Optional[Dict] = None


@dataclass
class QueryResult:
    """Complete query result with retrieved documents"""
    query_id: str
    query_text: str
    retrieved_docs: List[RetrievalResult]
    timestamp: float
    retrieval_time_ms: float
    total_candidates: int


class RetrievalMetricsCalculator:
    """Production-ready retrieval accuracy metrics"""

    def __init__(self):
        self.query_results: List[QueryResult] = []
        self.relevance_judgments: Dict[str, Dict[str, float]] = {}

    def add_relevance_judgments(self, query_id: str, judgments: Dict[str, float]):
        """Add ground truth relevance judgments for a query

        Args:
            query_id: Query identifier
            judgments: Dict mapping document_id -> relevance_score (0-4 scale typically)
        """
        self.relevance_judgments[query_id] = judgments

    def calculate_ndcg(self, retrieved_docs: List[RetrievalResult],
                      relevance_judgments: Dict[str, float],
                      k: int = 10) -> float:
        """Calculate Normalized Discounted Cumulative Gain (NDCG@k)

        Args:
            retrieved_docs: List of retrieved documents in rank order
            relevance_judgments: Dict mapping doc_id -> relevance score
            k: Cut-off rank for evaluation

        Returns:
            NDCG@k score (0-1, higher is better)
        """
        if not retrieved_docs or not relevance_judgments:
            return 0.0

        # Calculate DCG@k
        dcg = 0.0
        for i, doc in enumerate(retrieved_docs[:k]):
            if doc.document_id in relevance_judgments:
                relevance = relevance_judgments[doc.document_id]
                # DCG formula: (2^relevance - 1) / log2(rank + 1)
                dcg += (2**relevance - 1) / math.log2(i + 2)

        # Calculate IDCG@k (Ideal DCG)
        ideal_relevances = sorted(relevance_judgments.values(), reverse=True)[:k]
        idcg = 0.0
        for i, relevance in enumerate(ideal_relevances):
            idcg += (2**relevance - 1) / math.log2(i + 2)

        # NDCG = DCG / IDCG
        return dcg / idcg if idcg > 0 else 0.0

    def calculate_mrr(self, retrieved_docs: List[RetrievalResult],
                     relevance_judgments: Dict[str, float],
                     relevance_threshold: float = 1.0) -> float:
        """Calculate Mean Reciprocal Rank (MRR)

        Args:
            retrieved_docs: List of retrieved documents in rank order
            relevance_judgments: Dict mapping doc_id -> relevance score
            relevance_threshold: Minimum relevance to consider relevant

        Returns:
            MRR score (0-1, higher is better)
        """
        for i, doc in enumerate(retrieved_docs):
            if doc.document_id in relevance_judgments:
                relevance = relevance_judgments[doc.document_id]
                if relevance >= relevance_threshold:
                    return 1.0 / (i + 1)
        return 0.0

    def calculate_map(self, retrieved_docs: List[RetrievalResult],
                     relevance_judgments: Dict[str, float],
                     relevance_threshold: float = 1.0) -> float:
        """Calculate Mean Average Precision (MAP)

        Args:
            retrieved_docs: List of retrieved documents in rank order
            relevance_judgments: Dict mapping doc_id -> relevance score
            relevance_threshold: Minimum relevance to consider relevant

        Returns:
            MAP score (0-1, higher is better)
        """
        relevant_found = 0
        precision_sum = 0.0
        total_relevant = sum(1 for rel in relevance_judgments.values()
                           if rel >= relevance_threshold)

        if total_relevant == 0:
            return 0.0

        for i, doc in enumerate(retrieved_docs):
            if doc.document_id in relevance_judgments:
                relevance = relevance_judgments[doc.document_id]
                if relevance >= relevance_threshold:
                    relevant_found += 1
                    precision_at_i = relevant_found / (i + 1)
                    precision_sum += precision_at_i

        return precision_sum / total_relevant

    def calculate_precision_at_k(self, retrieved_docs: List[RetrievalResult],
                                relevance_judgments: Dict[str, float],
                                k: int = 10,
                                relevance_threshold: float = 1.0) -> float:
        """Calculate Precision@k

        Args:
            retrieved_docs: List of retrieved documents in rank order
            relevance_judgments: Dict mapping doc_id -> relevance score
            k: Cut-off rank for evaluation
            relevance_threshold: Minimum relevance to consider relevant

        Returns:
            Precision@k score (0-1, higher is better)
        """
        if k <= 0 or not retrieved_docs:
            return 0.0

        relevant_in_k = 0
        for doc in retrieved_docs[:k]:
            if doc.document_id in relevance_judgments:
                relevance = relevance_judgments[doc.document_id]
                if relevance >= relevance_threshold:
                    relevant_in_k += 1

        return relevant_in_k / k

    def calculate_recall_at_k(self, retrieved_docs: List[RetrievalResult],
                             relevance_judgments: Dict[str, float],
                             k: int = 10,
                             relevance_threshold: float = 1.0) -> float:
        """Calculate Recall@k

        Args:
            retrieved_docs: List of retrieved documents in rank order
            relevance_judgments: Dict mapping doc_id -> relevance score
            k: Cut-off rank for evaluation
            relevance_threshold: Minimum relevance to consider relevant

        Returns:
            Recall@k score (0-1, higher is better)
        """
        total_relevant = sum(1 for rel in relevance_judgments.values()
                           if rel >= relevance_threshold)

        if total_relevant == 0:
            return 0.0

        relevant_in_k = 0
        for doc in retrieved_docs[:k]:
            if doc.document_id in relevance_judgments:
                relevance = relevance_judgments[doc.document_id]
                if relevance >= relevance_threshold:
                    relevant_in_k += 1

        return relevant_in_k / total_relevant

    def calculate_hit_rate(self, retrieved_docs: List[RetrievalResult],
                          relevance_judgments: Dict[str, float],
                          k: int = 10,
                          relevance_threshold: float = 1.0) -> float:
        """Calculate Hit Rate@k (binary: did we find any relevant document?)

        Returns:
            Hit rate (0 or 1)
        """
        for doc in retrieved_docs[:k]:
            if doc.document_id in relevance_judgments:
                relevance = relevance_judgments[doc.document_id]
                if relevance >= relevance_threshold:
                    return 1.0
        return 0.0

    def evaluate_query(self, query_result: QueryResult,
                      relevance_judgments: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Evaluate a single query with all metrics

        Returns:
            Dictionary with all calculated metrics
        """
        if relevance_judgments is None:
            relevance_judgments = self.relevance_judgments.get(query_result.query_id, {})

        if not relevance_judgments:
            return {
                'ndcg_5': 0.0, 'ndcg_10': 0.0, 'ndcg_20': 0.0,
                'mrr': 0.0, 'map': 0.0,
                'precision_1': 0.0, 'precision_5': 0.0, 'precision_10': 0.0,
                'recall_5': 0.0, 'recall_10': 0.0, 'recall_20': 0.0,
                'hit_rate_1': 0.0, 'hit_rate_5': 0.0, 'hit_rate_10': 0.0
            }

        metrics = {
            # NDCG at different cut-offs
            'ndcg_5': self.calculate_ndcg(query_result.retrieved_docs, relevance_judgments, 5),
            'ndcg_10': self.calculate_ndcg(query_result.retrieved_docs, relevance_judgments, 10),
            'ndcg_20': self.calculate_ndcg(query_result.retrieved_docs, relevance_judgments, 20),

            # MRR and MAP
            'mrr': self.calculate_mrr(query_result.retrieved_docs, relevance_judgments),
            'map': self.calculate_map(query_result.retrieved_docs, relevance_judgments),

            # Precision at different cut-offs
            'precision_1': self.calculate_precision_at_k(query_result.retrieved_docs, relevance_judgments, 1),
            'precision_5': self.calculate_precision_at_k(query_result.retrieved_docs, relevance_judgments, 5),
            'precision_10': self.calculate_precision_at_k(query_result.retrieved_docs, relevance_judgments, 10),

            # Recall at different cut-offs
            'recall_5': self.calculate_recall_at_k(query_result.retrieved_docs, relevance_judgments, 5),
            'recall_10': self.calculate_recall_at_k(query_result.retrieved_docs, relevance_judgments, 10),
            'recall_20': self.calculate_recall_at_k(query_result.retrieved_docs, relevance_judgments, 20),

            # Hit rates
            'hit_rate_1': self.calculate_hit_rate(query_result.retrieved_docs, relevance_judgments, 1),
            'hit_rate_5': self.calculate_hit_rate(query_result.retrieved_docs, relevance_judgments, 5),
            'hit_rate_10': self.calculate_hit_rate(query_result.retrieved_docs, relevance_judgments, 10),
        }

        # Additional performance metrics
        metrics.update({
            'retrieval_time_ms': query_result.retrieval_time_ms,
            'total_candidates': query_result.total_candidates,
            'retrieved_count': len(query_result.retrieved_docs)
        })

        return metrics

    def evaluate_batch(self, query_results: List[QueryResult]) -> Dict[str, float]:
        """Evaluate multiple queries and return aggregate metrics

        Returns:
            Dictionary with averaged metrics across all queries
        """
        if not query_results:
            return {}

        all_metrics = []
        for query_result in query_results:
            metrics = self.evaluate_query(query_result)
            all_metrics.append(metrics)

        # Calculate averages
        avg_metrics = {}
        metric_names = all_metrics[0].keys()

        for metric_name in metric_names:
            values = [m[metric_name] for m in all_metrics if m[metric_name] is not None]
            avg_metrics[f'avg_{metric_name}'] = sum(values) / len(values) if values else 0.0
            avg_metrics[f'min_{metric_name}'] = min(values) if values else 0.0
            avg_metrics[f'max_{metric_name}'] = max(values) if values else 0.0

        # Add count metrics
        avg_metrics['total_queries'] = len(query_results)
        avg_metrics['queries_with_relevance'] = len([
            q for q in query_results if q.query_id in self.relevance_judgments
        ])

        return avg_metrics

    def calculate_semantic_similarity_metrics(self, query_results: List[QueryResult],
                                            embeddings_model=None) -> Dict[str, float]:
        """Calculate semantic similarity based metrics (requires embeddings model)

        This would typically use sentence transformers or similar
        """
        if embeddings_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                return {'semantic_similarity': 0.0, 'embedding_error': 'sentence-transformers not available'}

        similarities = []

        for query_result in query_results:
            query_embedding = embeddings_model.encode([query_result.query_text])

            for doc in query_result.retrieved_docs[:10]:  # Top 10 only
                doc_embedding = embeddings_model.encode([doc.content])

                # Calculate cosine similarity
                similarity = np.dot(query_embedding[0], doc_embedding[0]) / (
                    np.linalg.norm(query_embedding[0]) * np.linalg.norm(doc_embedding[0])
                )
                similarities.append(similarity)

        return {
            'avg_semantic_similarity': np.mean(similarities) if similarities else 0.0,
            'min_semantic_similarity': np.min(similarities) if similarities else 0.0,
            'max_semantic_similarity': np.max(similarities) if similarities else 0.0,
            'semantic_similarity_std': np.std(similarities) if similarities else 0.0
        }

    def generate_retrieval_report(self, query_results: List[QueryResult],
                                 output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive retrieval performance report"""

        # Calculate all metrics
        batch_metrics = self.evaluate_batch(query_results)

        # Individual query analysis
        query_analyses = []
        for query_result in query_results:
            query_metrics = self.evaluate_query(query_result)
            query_analyses.append({
                'query_id': query_result.query_id,
                'query_text': query_result.query_text,
                'metrics': query_metrics,
                'retrieved_count': len(query_result.retrieved_docs)
            })

        # Performance analysis
        retrieval_times = [q.retrieval_time_ms for q in query_results]

        report = {
            'summary': {
                'total_queries': len(query_results),
                'evaluation_timestamp': time.time(),
                'avg_retrieval_time_ms': np.mean(retrieval_times) if retrieval_times else 0,
                'queries_with_judgments': len([q for q in query_results if q.query_id in self.relevance_judgments])
            },
            'aggregate_metrics': batch_metrics,
            'query_analyses': query_analyses,
            'performance_stats': {
                'min_retrieval_time_ms': min(retrieval_times) if retrieval_times else 0,
                'max_retrieval_time_ms': max(retrieval_times) if retrieval_times else 0,
                'avg_retrieved_per_query': np.mean([len(q.retrieved_docs) for q in query_results]),
                'total_documents_retrieved': sum(len(q.retrieved_docs) for q in query_results)
            }
        }

        # Add semantic similarity if possible
        try:
            semantic_metrics = self.calculate_semantic_similarity_metrics(query_results)
            report['semantic_metrics'] = semantic_metrics
        except Exception as e:
            report['semantic_metrics'] = {'error': str(e)}

        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📊 Retrieval report saved to: {output_file}")

        return report


# Example usage and testing
if __name__ == "__main__":
    # Create calculator
    calculator = RetrievalMetricsCalculator()

    # Example: Add relevance judgments for a query
    calculator.add_relevance_judgments("query_1", {
        "doc_a": 3.0,  # Highly relevant
        "doc_b": 2.0,  # Moderately relevant
        "doc_c": 1.0,  # Slightly relevant
        "doc_d": 0.0,  # Not relevant
        "doc_e": 4.0   # Perfect match
    })

    # Example: Create a query result
    retrieved_docs = [
        RetrievalResult("doc_b", "Content B", 0.95),
        RetrievalResult("doc_a", "Content A", 0.87),
        RetrievalResult("doc_f", "Content F", 0.82),  # Not in judgments
        RetrievalResult("doc_c", "Content C", 0.76),
        RetrievalResult("doc_d", "Content D", 0.65),
    ]

    query_result = QueryResult(
        query_id="query_1",
        query_text="Find relevant documents",
        retrieved_docs=retrieved_docs,
        timestamp=time.time(),
        retrieval_time_ms=150.0,
        total_candidates=1000
    )

    # Evaluate single query
    metrics = calculator.evaluate_query(query_result)
    print("Single Query Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")

    # Evaluate batch
    batch_metrics = calculator.evaluate_batch([query_result])
    print("\nBatch Metrics:")
    for metric, value in batch_metrics.items():
        print(f"  {metric}: {value:.4f}")

    # Generate full report
    report = calculator.generate_retrieval_report([query_result], "retrieval_report.json")
    print(f"\nGenerated report with {len(report['query_analyses'])} queries analyzed")