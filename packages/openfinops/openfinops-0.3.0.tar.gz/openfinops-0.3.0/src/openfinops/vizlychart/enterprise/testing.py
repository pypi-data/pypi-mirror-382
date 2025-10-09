"""
Enterprise API Testing Framework
===============================

Comprehensive testing tools for API validation, integration testing,
and developer onboarding.
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

import json
import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    warnings.warn("requests library not available for API testing")

from .api import VizlyEnterpriseClient, APIResponse


@dataclass
class TestCase:
    """Individual API test case."""
    name: str
    description: str
    method: str
    endpoint: str
    headers: Dict[str, str] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    expected_fields: List[str] = field(default_factory=list)
    validator: Optional[Callable[[Dict[str, Any]], bool]] = None
    requires_auth: bool = True


@dataclass
class TestResult:
    """Test execution result."""
    test_name: str
    success: bool
    status_code: int
    response_time: float
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    assertions: List[str] = field(default_factory=list)


class APITestSuite:
    """
    Comprehensive test suite for Vizly Enterprise API.

    Provides automated testing for all endpoints including
    authentication, chart creation, user management, and error handling.
    """

    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url
        self.client: Optional[VizlyEnterpriseClient] = None
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
        self._setup_test_cases()

    def _setup_test_cases(self) -> None:
        """Initialize standard test cases."""

        # Health check tests
        self.test_cases.extend([
            TestCase(
                name="health_check",
                description="Server health check endpoint",
                method="GET",
                endpoint="/health",
                expected_fields=["status", "timestamp", "version"],
                requires_auth=False,
                validator=lambda data: data.get("status") == "healthy"
            ),
            TestCase(
                name="metrics_check",
                description="System metrics endpoint",
                method="GET",
                endpoint="/metrics",
                expected_fields=["cpu_usage", "memory_usage", "active_sessions"],
                requires_auth=False,
                validator=lambda data: isinstance(data.get("cpu_usage"), (int, float))
            )
        ])

        # Authentication tests
        self.test_cases.extend([
            TestCase(
                name="login_valid",
                description="Valid user authentication",
                method="POST",
                endpoint="/api/auth/login",
                data={"username": "admin@company.com", "password": "password123"},
                expected_fields=["token", "user_id", "roles"],
                requires_auth=False,
                validator=lambda data: "token" in data and len(data["token"]) > 20
            ),
            TestCase(
                name="login_invalid",
                description="Invalid credentials should fail",
                method="POST",
                endpoint="/api/auth/login",
                data={"username": "invalid", "password": "wrong"},
                expected_status=401,
                requires_auth=False
            )
        ])

        # Chart management tests
        self.test_cases.extend([
            TestCase(
                name="create_executive_dashboard",
                description="Create executive dashboard chart",
                method="POST",
                endpoint="/api/charts",
                data={
                    "type": "executive_dashboard",
                    "title": "Test Executive Dashboard",
                    "security_level": "internal",
                    "compliance_tags": ["Test"],
                    "kpis": {
                        "Revenue": {"value": 1000000, "target": 950000, "status": "good"},
                        "Profit": {"value": 150000, "target": 160000, "status": "warning"}
                    }
                },
                expected_fields=["id", "title", "type", "security_level"],
                validator=lambda data: data.get("type") == "executive_dashboard"
            ),
            TestCase(
                name="create_financial_chart",
                description="Create financial analytics chart",
                method="POST",
                endpoint="/api/charts",
                data={
                    "type": "financial_analytics",
                    "title": "Test Financial Chart",
                    "security_level": "confidential",
                    "compliance_tags": ["SOX", "Financial"]
                },
                expected_fields=["id", "title", "type"],
                validator=lambda data: data.get("security_level") == "confidential"
            ),
            TestCase(
                name="create_compliance_chart",
                description="Create compliance scorecard",
                method="POST",
                endpoint="/api/charts",
                data={
                    "type": "compliance",
                    "title": "Test Compliance Scorecard",
                    "metrics": {
                        "Data Protection": {"score": 95, "threshold_good": 90},
                        "Security": {"score": 88, "threshold_good": 90}
                    }
                },
                expected_fields=["id", "title", "audit_trail_count"],
                validator=lambda data: data.get("audit_trail_count", 0) > 0
            ),
            TestCase(
                name="list_charts",
                description="List all charts",
                method="GET",
                endpoint="/api/charts",
                expected_fields=["charts"],
                validator=lambda data: isinstance(data.get("charts"), list)
            )
        ])

        # User management tests (admin required)
        self.test_cases.extend([
            TestCase(
                name="list_users_unauthorized",
                description="Non-admin user should not access user list",
                method="GET",
                endpoint="/api/users",
                expected_status=403
            ),
            TestCase(
                name="create_chart_invalid_type",
                description="Invalid chart type should fail",
                method="POST",
                endpoint="/api/charts",
                data={
                    "type": "invalid_type",
                    "title": "Invalid Chart"
                },
                expected_status=400
            )
        ])

    def authenticate_test_user(self, username: str = "admin@company.com",
                              password: str = "password123") -> bool:
        """Authenticate test user for protected endpoints."""
        try:
            self.client = VizlyEnterpriseClient(self.base_url, username=username, password=password)
            return self.client.token is not None
        except Exception:
            return False

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case."""
        start_time = time.time()

        try:
            if not REQUESTS_AVAILABLE:
                return TestResult(
                    test_name=test_case.name,
                    success=False,
                    status_code=500,
                    response_time=0,
                    error_message="requests library not available"
                )

            # Prepare request
            url = f"{self.base_url}{test_case.endpoint}"
            headers = {"Content-Type": "application/json"}
            headers.update(test_case.headers)

            # Add authentication if required
            if test_case.requires_auth and self.client and self.client.token:
                headers["Authorization"] = f"Bearer {self.client.token}"

            # Make request
            if test_case.method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif test_case.method.upper() == "POST":
                response = requests.post(url, headers=headers, json=test_case.data)
            elif test_case.method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=test_case.data)
            elif test_case.method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {test_case.method}")

            response_time = time.time() - start_time

            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}

            # Validate result
            assertions = []
            success = True

            # Check status code
            if response.status_code != test_case.expected_status:
                success = False
                assertions.append(f"Expected status {test_case.expected_status}, got {response.status_code}")
            else:
                assertions.append(f"✓ Status code {response.status_code} as expected")

            # Check expected fields
            if test_case.expected_status == 200 and test_case.expected_fields:
                for field in test_case.expected_fields:
                    if field not in response_data:
                        success = False
                        assertions.append(f"✗ Missing expected field: {field}")
                    else:
                        assertions.append(f"✓ Field '{field}' present")

            # Run custom validator
            if test_case.validator and response.status_code == 200:
                try:
                    if not test_case.validator(response_data):
                        success = False
                        assertions.append("✗ Custom validation failed")
                    else:
                        assertions.append("✓ Custom validation passed")
                except Exception as e:
                    success = False
                    assertions.append(f"✗ Validation error: {str(e)}")

            return TestResult(
                test_name=test_case.name,
                success=success,
                status_code=response.status_code,
                response_time=response_time,
                response_data=response_data,
                assertions=assertions
            )

        except Exception as e:
            return TestResult(
                test_name=test_case.name,
                success=False,
                status_code=500,
                response_time=time.time() - start_time,
                error_message=str(e)
            )

    def run_all_tests(self, include_auth_tests: bool = True) -> Dict[str, Any]:
        """Run complete test suite."""
        print("🧪 Running Vizly Enterprise API Test Suite")
        print("=" * 50)

        self.results = []

        # Authenticate if needed
        if include_auth_tests:
            print("🔐 Authenticating test user...")
            if self.authenticate_test_user():
                print("✅ Authentication successful")
            else:
                print("❌ Authentication failed - some tests may fail")

        # Run tests
        total_tests = len(self.test_cases)
        passed_tests = 0

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n[{i}/{total_tests}] {test_case.name}: {test_case.description}")

            result = self.run_test_case(test_case)
            self.results.append(result)

            if result.success:
                passed_tests += 1
                print(f"✅ PASS ({result.response_time:.3f}s)")
            else:
                print(f"❌ FAIL ({result.response_time:.3f}s)")
                if result.error_message:
                    print(f"   Error: {result.error_message}")

            # Show assertions
            for assertion in result.assertions:
                print(f"   {assertion}")

        # Generate summary
        success_rate = (passed_tests / total_tests) * 100
        total_time = sum(r.response_time for r in self.results)

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "total_time": total_time,
            "average_response_time": total_time / total_tests if total_tests > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }

        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Time: {total_time:.3f}s")
        print(f"   Average Response Time: {summary['average_response_time']:.3f}s")

        return summary

    def generate_test_report(self, output_file: str = "api_test_report.json") -> None:
        """Generate detailed test report."""
        report = {
            "test_suite": "Vizly Enterprise API",
            "base_url": self.base_url,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "passed_tests": len([r for r in self.results if r.success]),
                "failed_tests": len([r for r in self.results if not r.success]),
                "success_rate": len([r for r in self.results if r.success]) / len(self.results) * 100
            },
            "results": [
                {
                    "test_name": result.test_name,
                    "success": result.success,
                    "status_code": result.status_code,
                    "response_time": result.response_time,
                    "error_message": result.error_message,
                    "assertions": result.assertions
                }
                for result in self.results
            ]
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📄 Test report saved to {output_file}")


class APILoadTester:
    """
    Load testing tool for API performance validation.
    """

    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url

    def run_load_test(self, endpoint: str, method: str = "GET",
                     data: Optional[Dict[str, Any]] = None,
                     concurrent_users: int = 10,
                     requests_per_user: int = 10,
                     auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Run load test against specific endpoint.

        Args:
            endpoint: API endpoint to test
            method: HTTP method
            data: Request payload for POST/PUT
            concurrent_users: Number of concurrent users to simulate
            requests_per_user: Number of requests each user makes
            auth_token: JWT token for authentication

        Returns:
            Load test results with performance metrics
        """
        import threading
        import queue
        from statistics import mean, median

        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for load testing")

        results_queue = queue.Queue()
        response_times = []
        status_codes = []
        errors = []

        def worker(user_id: int):
            """Worker function for each simulated user."""
            session = requests.Session()
            headers = {"Content-Type": "application/json"}

            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"

            for request_id in range(requests_per_user):
                try:
                    start_time = time.time()

                    if method.upper() == "GET":
                        response = session.get(f"{self.base_url}{endpoint}", headers=headers)
                    elif method.upper() == "POST":
                        response = session.post(f"{self.base_url}{endpoint}", headers=headers, json=data)
                    else:
                        raise ValueError(f"Unsupported method: {method}")

                    response_time = time.time() - start_time

                    results_queue.put({
                        "user_id": user_id,
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "success": response.status_code < 400
                    })

                except Exception as e:
                    results_queue.put({
                        "user_id": user_id,
                        "request_id": request_id,
                        "status_code": 500,
                        "response_time": 0,
                        "error": str(e),
                        "success": False
                    })

        # Start load test
        print(f"🚀 Starting load test: {concurrent_users} users, {requests_per_user} requests each")
        start_time = time.time()

        threads = []
        for user_id in range(concurrent_users):
            thread = threading.Thread(target=worker, args=(user_id,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        # Collect results
        results = []
        while not results_queue.empty():
            result = results_queue.get()
            results.append(result)

            if result["success"]:
                response_times.append(result["response_time"])
                status_codes.append(result["status_code"])
            else:
                errors.append(result.get("error", "Unknown error"))

        # Calculate metrics
        total_requests = len(results)
        successful_requests = len([r for r in results if r["success"]])
        failed_requests = total_requests - successful_requests

        metrics = {
            "test_configuration": {
                "endpoint": endpoint,
                "method": method,
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user,
                "total_requests": total_requests
            },
            "performance_metrics": {
                "total_time": total_time,
                "requests_per_second": total_requests / total_time,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": (successful_requests / total_requests) * 100
            },
            "response_time_metrics": {
                "mean": mean(response_times) if response_times else 0,
                "median": median(response_times) if response_times else 0,
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0
            },
            "errors": errors[:10]  # Show first 10 errors
        }

        # Print summary
        print(f"📊 Load Test Results:")
        print(f"   Total Requests: {total_requests}")
        print(f"   Successful: {successful_requests}")
        print(f"   Failed: {failed_requests}")
        print(f"   Success Rate: {metrics['performance_metrics']['success_rate']:.1f}%")
        print(f"   Requests/Second: {metrics['performance_metrics']['requests_per_second']:.1f}")
        print(f"   Average Response Time: {metrics['response_time_metrics']['mean']:.3f}s")

        return metrics


def run_api_tests(base_url: str = "http://localhost:8888") -> None:
    """Run comprehensive API test suite."""
    test_suite = APITestSuite(base_url)
    test_suite.run_all_tests()
    test_suite.generate_test_report()


def run_load_tests(base_url: str = "http://localhost:8888") -> None:
    """Run performance load tests."""
    load_tester = APILoadTester(base_url)

    # Test health endpoint
    print("\n🔥 Load Testing Health Endpoint")
    load_tester.run_load_test("/health", "GET", concurrent_users=20, requests_per_user=5)

    # Test metrics endpoint
    print("\n🔥 Load Testing Metrics Endpoint")
    load_tester.run_load_test("/metrics", "GET", concurrent_users=10, requests_per_user=10)