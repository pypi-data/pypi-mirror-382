# 🌟 OpenFinOps

**Open Source FinOps Platform for AI/ML Cost Observability and Optimization**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/openfinops.svg)](https://pypi.org/project/openfinops/)
[![PyPI downloads](https://img.shields.io/pypi/dm/openfinops.svg)](https://pypi.org/project/openfinops/)
[![Total downloads](https://pepy.tech/badge/openfinops)](https://pepy.tech/project/openfinops)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🎯 Overview

OpenFinOps is a comprehensive, open-source platform for tracking, analyzing, and optimizing costs across AI/ML infrastructure and operations. It provides real-time visibility into:

- **LLM Training Costs** - Track GPU utilization, training jobs, and compute expenses
- **RAG Pipeline Monitoring** - Monitor vector databases, embeddings, and retrieval costs
- **Multi-Cloud Cost Tracking** - Unified view across AWS, Azure, GCP
- **AI API Usage** - Track OpenAI, Anthropic, and other LLM API costs
- **Executive Dashboards** - Role-based views for CFO, COO, Infrastructure Leaders
- **Cost Attribution** - Per-model, per-team, per-project cost breakdown
- **AI-Powered Optimization** - Intelligent recommendations for cost savings

## ✨ Key Features

### 📊 Comprehensive Observability
- **Real-time Monitoring**: Live metrics for all AI/ML operations
- **Multi-Cloud Support**: AWS, Azure, GCP telemetry integration
- **LLM Training Tracking**: GPU utilization, loss curves, cost per epoch
- **RAG Analytics**: Document processing, embedding generation, retrieval accuracy
- **API Cost Tracking**: OpenAI, Anthropic, and custom API endpoints

### 💰 FinOps Intelligence
- **Cost Observatory**: Centralized cost tracking and analysis
- **Cost Attribution**: Per-model, per-project, per-team breakdowns
- **Budget Management**: Set budgets, track spending, get alerts
- **Optimization Recommendations**: AI-powered cost-saving suggestions
- **Trend Analysis**: Historical cost patterns and forecasting

### 📈 Professional Visualizations
- **VizlyChart**: Built-in visualization library for charts and graphs
- **Executive Dashboards**: Role-based dashboards (CFO, COO, Infrastructure)
- **Real-time Charts**: Live updating metrics and KPIs
- **Custom Reports**: Generate and export custom cost reports

### 🔐 Enterprise-Grade Security
- **Role-Based Access Control (RBAC)**: Fine-grained permissions
- **IAM Integration**: Identity and access management system
- **Audit Logging**: Complete audit trail for all operations
- **Secure API**: Authentication and authorization built-in

### 🚀 Easy Deployment
- **Docker Support**: Containerized deployment ready
- **Kubernetes Ready**: Helm charts for K8s deployment
- **Cloud-Native**: Deploy on any cloud provider
- **On-Premise**: Run in your own datacenter

## 🏗️ Architecture

```
openfinops/
├── observability/          # Core observability platform
│   ├── observability_hub.py        # Central monitoring hub
│   ├── llm_observability.py        # LLM training & RAG monitoring
│   ├── finops_dashboards.py        # FinOps dashboards
│   ├── cost_observatory.py         # Cost tracking
│   ├── cost_reporting.py           # Cost reporting
│   ├── ai_recommendations.py       # AI-powered optimization
│   └── alerting_engine.py          # Intelligent alerting
│
├── vizlychart/             # Visualization library
│   ├── charts/                     # Chart implementations
│   ├── rendering/                  # Rendering engine
│   └── core/                       # Core utilities
│
├── dashboard/              # Role-based dashboards
│   ├── cfo_dashboard.py            # CFO financial view
│   ├── coo_dashboard.py            # COO operations view
│   ├── infrastructure_leader_dashboard.py
│   └── iam_system.py               # Access control
│
└── agents/                 # Cloud telemetry agents
    ├── aws_telemetry_agent.py
    ├── azure_telemetry_agent.py
    ├── gcp_telemetry_agent.py
    └── generic_telemetry_agent.py
```

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/openfinops/openfinops.git
cd openfinops
pip install -e .

# Or with all features
pip install -e ".[all]"

# Or specific cloud providers
pip install -e ".[aws,azure,gcp]"
```

### Basic Usage

```python
from openfinops.observability import ObservabilityHub
from openfinops.observability import LLMObservabilityHub

# Initialize observability
hub = ObservabilityHub()
llm_hub = LLMObservabilityHub()

# Register training cluster
llm_hub.register_training_cluster(
    cluster_name="gpu-cluster-1",
    nodes=["node-1", "node-2"]
)

# Track training metrics
llm_hub.track_training_metrics(
    model_id="gpt-custom",
    epoch=1,
    step=100,
    loss=0.5,
    gpu_memory_usage=8000
)

# Get cost summary
cost_summary = hub.get_cost_summary()
print(f"Total spend: ${cost_summary['total']}")
```

### Running the Dashboard

```bash
# Start the web dashboard
openfinops-dashboard

# Or with custom port
openfinops-dashboard --port 8080

# Access at http://localhost:8080
```

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed installation instructions
- **[Quick Start](docs/quickstart.md)** - Get started in 5 minutes
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Architecture](docs/architecture.md)** - System architecture overview
- **[Deployment Guide](docs/deployment.md)** - Production deployment guide
- **[Contributing](CONTRIBUTING.md)** - How to contribute

## 🎯 Use Cases

### For Engineering Teams
- Monitor LLM training job costs in real-time
- Track GPU utilization and optimize resource allocation
- Debug cost anomalies and inefficiencies
- Set up alerts for budget overruns

### For Finance Teams
- Get complete visibility into AI/ML spending
- Track cost attribution by team, project, or model
- Generate reports for stakeholders
- Forecast future AI infrastructure costs

### For Leadership
- Executive dashboards with key metrics
- ROI analysis for AI initiatives
- Budget vs. actual spending tracking
- Strategic cost optimization recommendations

## 🌐 Multi-Cloud Support

OpenFinOps supports telemetry from:

- **AWS**: CloudWatch metrics, Cost Explorer, EC2, SageMaker
- **Azure**: Azure Monitor, Cost Management, Azure ML
- **GCP**: Cloud Monitoring, Cloud Billing, Vertex AI
- **AI Platforms**: OpenAI, Anthropic, Hugging Face, Custom APIs

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/openfinops/openfinops.git
cd openfinops

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/
```

## 📊 Roadmap

- [ ] Kubernetes operator for auto-scaling based on cost
- [ ] Integration with Prometheus and Grafana
- [ ] Support for more AI platforms (Cohere, AI21, etc.)
- [ ] Advanced anomaly detection with ML models
- [ ] Mobile app for cost monitoring
- [ ] Slack/Teams integration for alerts
- [ ] Custom webhook support
- [ ] Cost allocation tagging system

## 📄 License

OpenFinOps is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

OpenFinOps is built with inspiration from the FinOps Foundation principles and best practices from the cloud cost optimization community.

## 📝 Citing OpenFinOps

If you use OpenFinOps in your research, please cite it using the following references:

### BibTeX

```bibtex
@software{openfinops2024,
  title = {{OpenFinOps}: Open Source FinOps Platform for AI/ML Cost Observability and Optimization},
  author = {Durai and {OpenFinOps Contributors}},
  year = {2024},
  month = {10},
  version = {0.1.0},
  url = {https://github.com/rdmurugan/OpenFinOps},
  license = {Apache-2.0},
  keywords = {finops, cost-optimization, observability, ai-ml, cloud-cost, llm-monitoring}
}


## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/openfinops/openfinops/issues)
- **Discussions**: [Community discussions](https://github.com/openfinops/openfinops/discussions)
- **Email**: durai@infinidatum.net

## ⭐ Star Us!

If you find OpenFinOps useful, please consider giving us a star on GitHub! It helps the project grow and reach more users.

---

**Made with ❤️ by the OpenFinOps community**
