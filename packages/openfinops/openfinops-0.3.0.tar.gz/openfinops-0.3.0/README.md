# OpenFinOps

Open-source FinOps telemetry and cost observability for AI/ML and cloud.

## Status

The project is preparing a proposal for incubation at the Apache Software Foundation (ASF).

## License

Apache License 2.0

---

## Overview

OpenFinOps is a comprehensive platform for tracking, analyzing, and optimizing costs across AI/ML infrastructure and multi-cloud environments. It provides real-time visibility into LLM training costs, RAG pipeline monitoring, and cloud resource utilization.

### Key Features

- **AI/ML Cost Tracking**: Monitor GPU utilization, training jobs, and inference costs
- **Multi-Cloud Support**: Unified view across AWS, Azure, and GCP
- **FinOps-as-Code**: Terraform provider for infrastructure management
- **SaaS License Management**: Track and optimize SaaS spending
- **Executive Dashboards**: Role-based views for CFO, COO, and Infrastructure Leaders
- **AI-Powered Optimization**: Intelligent cost-saving recommendations

## Quick Start

```bash
# Install from source
git clone https://github.com/rdmurugan/openFinOps.git
cd openFinOps
pip install -e .

# Start the dashboard
openfinops-dashboard
```

## Documentation

- **[2025 Roadmap](ROADMAP_2025.md)** - Strategic initiatives and features
- **[Completed Features](docs/ROADMAP_2025_COMPLETED.md)** - Implementation status
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

## Architecture

OpenFinOps uses an agent-based architecture for automatic cost tracking:

- **Telemetry Agents**: Deployed in cloud accounts to discover resources and calculate costs
- **Observability Hub**: Central hub for receiving and processing telemetry data
- **Cost Observatory**: Cost aggregation, budgets, and alerts
- **Dashboards**: Role-based executive dashboards

## Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/rdmurugan/openFinOps/issues)
- **Email**: durai@infinidatum.net

## Acknowledgments

OpenFinOps is built with inspiration from the FinOps Foundation principles and best practices from the cloud cost optimization community.

---

**Made with ❤️ by the OpenFinOps community**
