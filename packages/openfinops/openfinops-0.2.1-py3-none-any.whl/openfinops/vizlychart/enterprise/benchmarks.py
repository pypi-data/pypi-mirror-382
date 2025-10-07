"""
Enterprise Performance Benchmarking System
==========================================

Comprehensive benchmarking suite for enterprise performance validation,
optimization recommendations, and competitive analysis.
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



from __future__ import annotations

import gc
import time
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False


@dataclass
class BenchmarkResult:
    """Performance benchmark result."""
    test_name: str
    dataset_size: int
    render_time: float
    memory_usage_mb: float
    fps: float
    points_per_second: float
    cpu_usage: float
    gpu_usage: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    optimization_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SystemInfo:
    """System configuration information."""
    cpu_cores: int
    cpu_frequency: float
    total_memory_gb: float
    available_memory_gb: float
    gpu_available: bool
    gpu_name: Optional[str] = None
    gpu_memory_gb: Optional[float] = None
    python_version: str = ""
    matplotlib_version: str = ""


class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking for enterprise deployments.

    Features:
    - Multi-scale dataset testing
    - CPU vs GPU performance comparison
    - Memory optimization analysis
    - Rendering performance metrics
    - Competitive benchmarking
    - Optimization recommendations
    """

    def __init__(self):
        self.system_info = self._gather_system_info()
        self.benchmark_results: List[BenchmarkResult] = []

    def run_benchmark(self, dataset_size: int = 1_000_000,
                     chart_type: str = "scatter",
                     use_gpu: bool = False) -> Dict[str, Any]:
        """
        Run comprehensive performance benchmark.
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for benchmarking")

        print(f"🚀 Running performance benchmark...")
        print(f"   Dataset: {dataset_size:,} points")
        print(f"   Chart type: {chart_type}")
        print(f"   GPU acceleration: {'Enabled' if use_gpu and CUPY_AVAILABLE else 'Disabled'}")

        # Generate test data
        start_time = time.time()
        x_data, y_data = self._generate_test_data(dataset_size, use_gpu)
        data_gen_time = time.time() - start_time

        # Measure baseline system metrics
        initial_memory = psutil.virtual_memory().used / (1024**2)  # MB
        initial_cpu = psutil.cpu_percent(interval=1)

        # Run rendering benchmark
        render_start = time.time()
        chart_result = self._benchmark_chart_rendering(
            x_data, y_data, chart_type, use_gpu
        )
        render_time = time.time() - render_start

        # Measure post-render metrics
        final_memory = psutil.virtual_memory().used / (1024**2)  # MB
        memory_used = final_memory - initial_memory
        cpu_usage = psutil.cpu_percent(interval=1)

        # Calculate performance metrics
        fps = 1.0 / render_time if render_time > 0 else 0
        points_per_second = dataset_size / render_time if render_time > 0 else 0

        # GPU metrics
        gpu_usage, gpu_memory = self._get_gpu_metrics() if use_gpu and CUPY_AVAILABLE else (None, None)

        # Create benchmark result
        result = BenchmarkResult(
            test_name=f"{chart_type}_{dataset_size}",
            dataset_size=dataset_size,
            render_time=render_time,
            memory_usage_mb=memory_used,
            fps=fps,
            points_per_second=points_per_second,
            cpu_usage=cpu_usage,
            gpu_usage=gpu_usage,
            gpu_memory_mb=gpu_memory
        )

        # Generate optimization recommendations
        result.recommendations = self._generate_recommendations(result)
        result.optimization_score = self._calculate_optimization_score(result)

        self.benchmark_results.append(result)

        # Clean up
        gc.collect()

        return {
            "render_time": render_time,
            "fps": fps,
            "memory_mb": memory_used,
            "points_per_second": points_per_second,
            "cpu_usage": cpu_usage,
            "gpu_usage": gpu_usage,
            "gpu_memory_mb": gpu_memory,
            "data_generation_time": data_gen_time,
            "optimization_score": result.optimization_score,
            "recommendations": result.recommendations,
            "system_info": self._system_info_dict()
        }

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """
        Run comprehensive benchmark across multiple scenarios.
        """
        print("🔬 Running comprehensive performance benchmark suite...")

        scenarios = [
            (10_000, "scatter", False),
            (100_000, "scatter", False),
            (1_000_000, "scatter", False),
            (10_000, "line", False),
            (100_000, "line", False),
            (1_000_000, "line", False),
            (10_000, "heatmap", False),
            (50_000, "heatmap", False),
        ]

        # Add GPU scenarios if available
        if CUPY_AVAILABLE:
            scenarios.extend([
                (1_000_000, "scatter", True),
                (5_000_000, "scatter", True),
                (1_000_000, "line", True),
            ])

        results = []
        for dataset_size, chart_type, use_gpu in scenarios:
            try:
                result = self.run_benchmark(dataset_size, chart_type, use_gpu)
                results.append(result)
                time.sleep(1)  # Cool down between tests
            except Exception as e:
                print(f"⚠️  Benchmark failed for {chart_type} {dataset_size:,}: {e}")

        return {
            "summary": self._generate_benchmark_summary(results),
            "detailed_results": results,
            "system_info": self._system_info_dict(),
            "competitive_analysis": self._generate_competitive_analysis(results)
        }

    def _generate_test_data(self, size: int, use_gpu: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        """Generate test dataset for benchmarking."""
        if use_gpu and CUPY_AVAILABLE:
            # Generate data on GPU
            x = cp.random.random(size).astype(cp.float32)
            y = cp.sin(x * 10) + cp.random.normal(0, 0.1, size).astype(cp.float32)
            return cp.asnumpy(x), cp.asnumpy(y)
        else:
            # Generate data on CPU
            np.random.seed(42)  # Reproducible results
            x = np.random.random(size).astype(np.float32)
            y = np.sin(x * 10) + np.random.normal(0, 0.1, size).astype(np.float32)
            return x, y

    def _benchmark_chart_rendering(self, x_data: np.ndarray, y_data: np.ndarray,
                                 chart_type: str, use_gpu: bool = False) -> Dict[str, Any]:
        """Benchmark chart rendering performance."""
        fig, ax = plt.subplots(figsize=(12, 8))

        start_time = time.time()

        if chart_type == "scatter":
            # Test scatter plot performance
            alpha = min(1.0, 1000 / len(x_data))  # Adaptive alpha
            ax.scatter(x_data, y_data, alpha=alpha, s=1)

        elif chart_type == "line":
            # Test line plot performance
            # Sample data for large datasets
            if len(x_data) > 100_000:
                indices = np.linspace(0, len(x_data)-1, 100_000, dtype=int)
                x_sampled = x_data[indices]
                y_sampled = y_data[indices]
            else:
                x_sampled, y_sampled = x_data, y_data

            ax.plot(x_sampled, y_sampled, linewidth=0.5)

        elif chart_type == "heatmap":
            # Test heatmap performance
            grid_size = min(int(np.sqrt(len(x_data))), 200)
            hist, x_edges, y_edges = np.histogram2d(x_data, y_data, bins=grid_size)
            ax.imshow(hist.T, origin='lower', aspect='auto',
                     extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]])

        # Force rendering
        canvas = FigureCanvasAgg(fig)
        canvas.draw()

        render_time = time.time() - start_time

        plt.close(fig)

        return {
            "render_time": render_time,
            "chart_type": chart_type,
            "data_points": len(x_data)
        }

    def _get_gpu_metrics(self) -> Tuple[Optional[float], Optional[float]]:
        """Get GPU usage metrics if available."""
        if not CUPY_AVAILABLE:
            return None, None

        try:
            # Get GPU memory info
            mempool = cp.get_default_memory_pool()
            memory_used = mempool.used_bytes() / (1024**2)  # MB

            # GPU utilization would require nvidia-ml-py
            # For now, return memory usage
            return None, memory_used

        except Exception:
            return None, None

    def _generate_recommendations(self, result: BenchmarkResult) -> List[str]:
        """Generate optimization recommendations based on benchmark results."""
        recommendations = []

        # Memory recommendations
        if result.memory_usage_mb > 1000:  # > 1GB
            recommendations.append("Consider data sampling for large datasets")
            recommendations.append("Implement progressive loading for better memory efficiency")

        # Performance recommendations
        if result.fps < 1.0:  # Less than 1 FPS
            recommendations.append("Enable data sampling for datasets > 1M points")
            if CUPY_AVAILABLE and not result.gpu_usage:
                recommendations.append("Consider GPU acceleration for large datasets")

        if result.render_time > 5.0:  # > 5 seconds
            recommendations.append("Implement adaptive rendering based on data size")
            recommendations.append("Consider using web-based rendering for interactive charts")

        # CPU recommendations
        if result.cpu_usage > 80:
            recommendations.append("High CPU usage detected - consider background processing")

        # GPU recommendations
        if CUPY_AVAILABLE and result.dataset_size > 500_000 and not result.gpu_usage:
            recommendations.append("GPU acceleration recommended for this dataset size")

        # General recommendations
        if result.dataset_size > 1_000_000:
            recommendations.append("Consider streaming data updates for real-time applications")

        return recommendations

    def _calculate_optimization_score(self, result: BenchmarkResult) -> float:
        """Calculate optimization score (0-100)."""
        score = 100.0

        # Penalize slow rendering
        if result.render_time > 1.0:
            score -= min(50, (result.render_time - 1.0) * 10)

        # Penalize high memory usage
        if result.memory_usage_mb > 500:
            score -= min(30, (result.memory_usage_mb - 500) / 100)

        # Penalize low FPS
        if result.fps < 10:
            score -= (10 - result.fps) * 2

        # Bonus for good performance
        if result.points_per_second > 1_000_000:
            score += 10

        return max(0, min(100, score))

    def _generate_benchmark_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of benchmark results."""
        if not results:
            return {}

        render_times = [r["render_time"] for r in results]
        memory_usage = [r["memory_mb"] for r in results]
        fps_values = [r["fps"] for r in results]

        return {
            "total_tests": len(results),
            "average_render_time": np.mean(render_times),
            "best_render_time": np.min(render_times),
            "worst_render_time": np.max(render_times),
            "average_memory_usage": np.mean(memory_usage),
            "peak_memory_usage": np.max(memory_usage),
            "average_fps": np.mean(fps_values),
            "best_fps": np.max(fps_values),
            "overall_score": np.mean([r.get("optimization_score", 0) for r in results])
        }

    def _generate_competitive_analysis(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate competitive analysis against industry benchmarks."""
        if not results:
            return {}

        # Industry benchmark targets (hypothetical)
        industry_benchmarks = {
            "render_time_target": 2.0,  # seconds for 1M points
            "memory_efficiency_target": 500,  # MB for 1M points
            "fps_target": 30  # for interactive applications
        }

        # Find 1M point benchmark for comparison
        million_point_result = next(
            (r for r in results if r.get("system_info", {}).get("dataset_size") == 1_000_000),
            None
        )

        if not million_point_result:
            return {"status": "No 1M point benchmark available for comparison"}

        comparison = {
            "render_performance": {
                "our_time": million_point_result["render_time"],
                "industry_target": industry_benchmarks["render_time_target"],
                "performance_ratio": industry_benchmarks["render_time_target"] / million_point_result["render_time"]
            },
            "memory_efficiency": {
                "our_usage": million_point_result["memory_mb"],
                "industry_target": industry_benchmarks["memory_efficiency_target"],
                "efficiency_ratio": industry_benchmarks["memory_efficiency_target"] / million_point_result["memory_mb"]
            },
            "interactive_performance": {
                "our_fps": million_point_result["fps"],
                "industry_target": industry_benchmarks["fps_target"],
                "fps_ratio": million_point_result["fps"] / industry_benchmarks["fps_target"]
            }
        }

        # Overall competitive score
        ratios = [
            comparison["render_performance"]["performance_ratio"],
            comparison["memory_efficiency"]["efficiency_ratio"],
            comparison["interactive_performance"]["fps_ratio"]
        ]
        comparison["overall_competitive_score"] = np.mean(ratios) * 100

        return comparison

    def _gather_system_info(self) -> SystemInfo:
        """Gather system configuration information."""
        import sys
        import platform

        gpu_info = self._get_gpu_info() if CUPY_AVAILABLE else (False, None, None)

        matplotlib_version = "Not available"
        if MATPLOTLIB_AVAILABLE:
            try:
                import matplotlib
                matplotlib_version = matplotlib.__version__
            except:
                matplotlib_version = "Unknown"

        return SystemInfo(
            cpu_cores=psutil.cpu_count(),
            cpu_frequency=psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            total_memory_gb=psutil.virtual_memory().total / (1024**3),
            available_memory_gb=psutil.virtual_memory().available / (1024**3),
            gpu_available=gpu_info[0],
            gpu_name=gpu_info[1],
            gpu_memory_gb=gpu_info[2],
            python_version=sys.version,
            matplotlib_version=matplotlib_version
        )

    def _get_gpu_info(self) -> Tuple[bool, Optional[str], Optional[float]]:
        """Get GPU information."""
        if not CUPY_AVAILABLE:
            return False, None, None

        try:
            device = cp.cuda.Device()
            memory_info = cp.cuda.MemoryInfo()
            total_memory_gb = memory_info.total / (1024**3)
            return True, device.name.decode(), total_memory_gb
        except Exception:
            return False, None, None

    def _system_info_dict(self) -> Dict[str, Any]:
        """Convert system info to dictionary."""
        return {
            "cpu_cores": self.system_info.cpu_cores,
            "cpu_frequency_mhz": self.system_info.cpu_frequency,
            "total_memory_gb": round(self.system_info.total_memory_gb, 1),
            "available_memory_gb": round(self.system_info.available_memory_gb, 1),
            "gpu_available": self.system_info.gpu_available,
            "gpu_name": self.system_info.gpu_name,
            "gpu_memory_gb": self.system_info.gpu_memory_gb,
            "python_version": self.system_info.python_version.split()[0],
            "matplotlib_version": self.system_info.matplotlib_version
        }

    def export_benchmark_report(self, filename: str = "vizly_benchmark_report.json") -> None:
        """Export benchmark results to JSON file."""
        import json

        report = {
            "timestamp": time.time(),
            "system_info": self._system_info_dict(),
            "benchmark_results": [
                {
                    "test_name": result.test_name,
                    "dataset_size": result.dataset_size,
                    "render_time": result.render_time,
                    "memory_usage_mb": result.memory_usage_mb,
                    "fps": result.fps,
                    "points_per_second": result.points_per_second,
                    "optimization_score": result.optimization_score,
                    "recommendations": result.recommendations
                }
                for result in self.benchmark_results
            ]
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📊 Benchmark report exported to {filename}")