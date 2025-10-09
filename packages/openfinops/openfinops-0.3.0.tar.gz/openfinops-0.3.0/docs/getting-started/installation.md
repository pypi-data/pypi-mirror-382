# Installation Guide

Complete installation guide for OpenFinOps.

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM
- **Disk Space**: 500MB for installation
- **Operating System**: Linux, macOS, or Windows

### Recommended Requirements
- **Python**: 3.10 or higher
- **Memory**: 4GB+ RAM
- **Disk Space**: 2GB+ for data storage
- **Operating System**: Linux (Ubuntu 20.04+) or macOS

## Installation Methods

### Option 1: Install from Source (Recommended for Development)

This is the recommended method for development and contributing to OpenFinOps.

```bash
# Clone the repository
git clone https://github.com/rdmurugan/OpenFinOps.git
cd OpenFinOps

# Create and activate virtual environment
python -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install in development mode
pip install -e .

# Verify installation
python -c "import openfinops; print(openfinops.__version__)"
```

### Option 2: Install with Specific Features

Install OpenFinOps with only the features you need.

```bash
# Install with AWS support only
pip install -e ".[aws]"

# Install with Azure support only
pip install -e ".[azure]"

# Install with GCP support only
pip install -e ".[gcp]"

# Install with all cloud providers
pip install -e ".[aws,azure,gcp]"

# Install with AI platforms
pip install -e ".[openai,anthropic]"

# Install with database support
pip install -e ".[postgres,mongodb]"

# Install everything
pip install -e ".[all]"
```

### Option 3: Install Development Tools

For development and testing:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# This includes:
# - pytest (testing)
# - black (code formatting)
# - ruff (linting)
# - mypy (type checking)
```

## Docker Installation

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  openfinops:
    image: openfinops/openfinops:latest
    ports:
      - "8080:8080"
    environment:
      - OPENFINOPS_CONFIG=/config/openfinops.yaml
    volumes:
      - ./config:/config
      - ./data:/data
    restart: unless-stopped

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=openfinops
      - POSTGRES_USER=openfinops
      - POSTGRES_PASSWORD=changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

Start services:

```bash
docker-compose up -d
```

### Building Docker Image Manually

```bash
# Clone repository
git clone https://github.com/rdmurugan/OpenFinOps.git
cd OpenFinOps

# Build image
docker build -t openfinops:latest .

# Run container
docker run -d \
  --name openfinops \
  -p 8080:8080 \
  -v $(pwd)/config:/config \
  -v $(pwd)/data:/data \
  openfinops:latest
```

## Kubernetes Installation

### Using Helm

```bash
# Add OpenFinOps Helm repository (coming soon)
helm repo add openfinops https://openfinops.github.io/helm-charts
helm repo update

# Install OpenFinOps
helm install openfinops openfinops/openfinops \
  --namespace openfinops \
  --create-namespace \
  --set config.aws.enabled=true \
  --set config.azure.enabled=true
```

### Manual Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openfinops

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openfinops
  namespace: openfinops
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openfinops
  template:
    metadata:
      labels:
        app: openfinops
    spec:
      containers:
      - name: openfinops
        image: openfinops/openfinops:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENFINOPS_CONFIG
          value: /config/openfinops.yaml
        volumeMounts:
        - name: config
          mountPath: /config
      volumes:
      - name: config
        configMap:
          name: openfinops-config

---
apiVersion: v1
kind: Service
metadata:
  name: openfinops
  namespace: openfinops
spec:
  selector:
    app: openfinops
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

Apply:

```bash
kubectl apply -f k8s/deployment.yaml
```

## Post-Installation Setup

### 1. Verify Installation

```bash
# Check Python package
python -c "import openfinops; print('✓ OpenFinOps installed')"

# Check CLI
openfinops --version

# Run quick test
python examples/quickstart.py
```

### 2. Initialize Configuration

```bash
# Initialize default configuration
openfinops init --config config.yaml

# Edit configuration
nano config.yaml
```

### 3. Set Up Environment Variables

Create `.env` file:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-west-2

# Azure Credentials
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
AZURE_TENANT_ID=your_tenant_id

# GCP Credentials
GCP_PROJECT_ID=your_project_id
GCP_CREDENTIALS_FILE=/path/to/credentials.json

# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key

# OpenFinOps
OPENFINOPS_API_KEY=your_api_key
```

Load environment variables:

```bash
source .env
```

### 4. Set Up Database (Optional)

#### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE openfinops;
CREATE USER openfinops WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE openfinops TO openfinops;
\q

# Update configuration
# Edit config.yaml and set database connection string
```

#### MongoDB Setup

```bash
# Install MongoDB
sudo apt update
sudo apt install mongodb

# Create database and user
mongo
use openfinops
db.createUser({
  user: "openfinops",
  pwd: "changeme",
  roles: ["readWrite", "dbAdmin"]
})
exit

# Update configuration
```

## Platform-Specific Instructions

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install OpenFinOps
python3 -m venv venv
source venv/bin/activate
git clone https://github.com/rdmurugan/OpenFinOps.git
cd OpenFinOps
pip install -e .
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Install OpenFinOps
python3 -m venv venv
source venv/bin/activate
git clone https://github.com/rdmurugan/OpenFinOps.git
cd OpenFinOps
pip install -e .
```

### Windows

```powershell
# Install Python from python.org
# Then in PowerShell:

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install OpenFinOps
git clone https://github.com/rdmurugan/OpenFinOps.git
cd OpenFinOps
pip install -e .
```

## Upgrading

### From Source

```bash
cd OpenFinOps
git pull origin main
pip install -e . --upgrade
```

### Docker

```bash
docker pull openfinops/openfinops:latest
docker-compose down
docker-compose up -d
```

## Uninstallation

### Remove Python Package

```bash
pip uninstall openfinops
```

### Remove Docker Containers

```bash
docker-compose down -v
docker rmi openfinops/openfinops:latest
```

### Remove Kubernetes Deployment

```bash
kubectl delete namespace openfinops
```

## Troubleshooting

### Common Installation Issues

#### Issue: Python version too old

```bash
# Check Python version
python --version

# Install Python 3.10
sudo apt install python3.10 python3.10-venv
```

#### Issue: pip install fails

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Try again
pip install -e .
```

#### Issue: Permission denied

```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -e .

# Or use --user flag
pip install -e . --user
```

#### Issue: Missing dependencies

```bash
# Install build dependencies (Ubuntu/Debian)
sudo apt install build-essential python3-dev

# Install build dependencies (macOS)
brew install gcc
```

#### Issue: Docker permission denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo docker-compose up -d
```

## Next Steps

After successful installation:

1. **[Quick Start Guide](quickstart.md)** - Get started in 5 minutes
2. **[Configuration](configuration.md)** - Configure OpenFinOps
3. **[Basic Tutorial](../tutorials/basic-usage.md)** - Learn the basics
4. **[API Reference](../api/observability-api.md)** - Explore the API

## Getting Help

- **Documentation**: [docs/README.md](../README.md)
- **Examples**: [examples/](../../examples/)
- **Issues**: [GitHub Issues](https://github.com/rdmurugan/OpenFinOps/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rdmurugan/OpenFinOps/discussions)
