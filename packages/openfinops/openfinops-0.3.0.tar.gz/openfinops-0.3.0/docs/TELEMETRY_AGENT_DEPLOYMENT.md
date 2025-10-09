# OpenFinOps Telemetry Agent Deployment Guide

## 🚀 Overview

This guide covers how to deploy OpenFinOps telemetry agents in new instances and multicloud environments. Our telemetry system provides comprehensive monitoring for AI workloads, distributed training, and agent workflows.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+), macOS, Windows 10+
- **Python**: 3.8+ with pip
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Network**: Outbound HTTPS access to telemetry endpoints
- **Storage**: 10GB+ available disk space

### Dependencies
```bash
# Core Python packages
pip install opentelemetry-api>=1.20.0
pip install opentelemetry-sdk>=1.20.0
pip install opentelemetry-instrumentation>=0.41b0
pip install prometheus-client>=0.17.0
pip install requests>=2.31.0
```

## 🛠️ Agent Installation Methods

### Method 1: Automated Installation Script

Create the automated installer script:

```bash
#!/bin/bash
# openfinops-telemetry-installer.sh

set -e

# Configuration
TELEMETRY_VERSION="1.0.0"
INSTALL_DIR="/opt/openfinops-telemetry"
SERVICE_NAME="openfinops-telemetry"
CONFIG_DIR="/etc/openfinops"

echo "🔧 Installing OpenFinOps Telemetry Agent v${TELEMETRY_VERSION}"

# Create directories
sudo mkdir -p "${INSTALL_DIR}" "${CONFIG_DIR}"
sudo mkdir -p "/var/log/openfinops" "/var/lib/openfinops"

# Download and install agent
cd /tmp
wget "https://releases.openfinops.com/telemetry/v${TELEMETRY_VERSION}/openfinops-telemetry-${TELEMETRY_VERSION}.tar.gz"
tar -xzf "openfinops-telemetry-${TELEMETRY_VERSION}.tar.gz"
sudo cp -r openfinops-telemetry/* "${INSTALL_DIR}/"

# Install Python dependencies
sudo "${INSTALL_DIR}/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

# Create configuration
sudo tee "${CONFIG_DIR}/telemetry.yaml" > /dev/null <<EOF
# OpenFinOps Telemetry Configuration
service:
  name: "${HOSTNAME}-telemetry"
  version: "${TELEMETRY_VERSION}"
  environment: "production"

telemetry:
  endpoint: "https://telemetry.openfinops.com"
  api_key: "${OPENFINOPS_API_KEY}"

collection:
  metrics_interval: 30
  trace_sampling_rate: 0.1
  log_level: "info"

features:
  distributed_tracing: true
  llm_monitoring: true
  agent_workflows: true
  cost_tracking: true
EOF

# Create systemd service
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<EOF
[Unit]
Description=OpenFinOps Telemetry Agent
After=network.target
Wants=network.target

[Service]
Type=simple
User=openfinops
Group=openfinops
WorkingDirectory=${INSTALL_DIR}
ExecStart=${INSTALL_DIR}/bin/python -m openfinops.telemetry.agent
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
Environment=OPENFINOPS_CONFIG=${CONFIG_DIR}/telemetry.yaml

[Install]
WantedBy=multi-user.target
EOF

# Create user and set permissions
sudo useradd -r -s /bin/false openfinops || true
sudo chown -R openfinops:openfinops "${INSTALL_DIR}" "/var/log/openfinops" "/var/lib/openfinops"
sudo chmod 600 "${CONFIG_DIR}/telemetry.yaml"

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl start "${SERVICE_NAME}"

echo "✅ OpenFinOps Telemetry Agent installed successfully"
echo "📊 Status: sudo systemctl status ${SERVICE_NAME}"
echo "📝 Logs: sudo journalctl -u ${SERVICE_NAME} -f"
```

### Method 2: Docker Container Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  openfinops-telemetry:
    image: openfinops/telemetry-agent:1.0.0
    container_name: openfinops-telemetry
    restart: unless-stopped
    environment:
      - OPENFINOPS_API_KEY=${OPENFINOPS_API_KEY}
      - OPENFINOPS_SERVICE_NAME=${HOSTNAME}-telemetry
      - OPENFINOPS_ENVIRONMENT=production
      - OPENFINOPS_ENDPOINT=https://telemetry.openfinops.com
    volumes:
      - ./config/telemetry.yaml:/etc/openfinops/telemetry.yaml:ro
      - telemetry_data:/var/lib/openfinops
      - /var/run/docker.sock:/var/run/docker.sock:ro
    ports:
      - "8888:8888"  # Health check endpoint
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

volumes:
  telemetry_data:
```

### Method 3: Kubernetes Deployment

```yaml
# k8s-telemetry-agent.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: openfinops-telemetry
  namespace: monitoring
  labels:
    app: openfinops-telemetry
spec:
  selector:
    matchLabels:
      app: openfinops-telemetry
  template:
    metadata:
      labels:
        app: openfinops-telemetry
    spec:
      serviceAccountName: openfinops-telemetry
      hostNetwork: true
      hostPID: true
      containers:
      - name: telemetry-agent
        image: openfinops/telemetry-agent:1.0.0
        imagePullPolicy: Always
        env:
        - name: OPENFINOPS_API_KEY
          valueFrom:
            secretKeyRef:
              name: openfinops-credentials
              key: api-key
        - name: OPENFINOPS_NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: OPENFINOPS_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        volumeMounts:
        - name: config
          mountPath: /etc/openfinops
        - name: var-log
          mountPath: /var/log
        - name: var-lib-docker
          mountPath: /var/lib/docker
          readOnly: true
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: openfinops-telemetry-config
      - name: var-log
        hostPath:
          path: /var/log
      - name: var-lib-docker
        hostPath:
          path: /var/lib/docker
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: openfinops-telemetry-config
  namespace: monitoring
data:
  telemetry.yaml: |
    service:
      name: "k8s-telemetry"
      environment: "kubernetes"
    telemetry:
      endpoint: "https://telemetry.openfinops.com"
    collection:
      kubernetes: true
      container_metrics: true
      node_metrics: true
```

## 🌐 Multicloud Deployment Strategies

### 1. Cloud-Agnostic Deployment

#### Universal Installation Script
```bash
#!/bin/bash
# multicloud-telemetry-installer.sh

# Detect cloud provider
detect_cloud_provider() {
    if curl -s -m 5 "http://169.254.169.254/latest/meta-data/" > /dev/null 2>&1; then
        echo "aws"
    elif curl -s -m 5 "http://169.254.169.254/metadata/instance" -H "Metadata-Flavor: Google" > /dev/null 2>&1; then
        echo "gcp"
    elif curl -s -m 5 "http://169.254.169.254/metadata/instance?api-version=2021-02-01" -H "Metadata:true" > /dev/null 2>&1; then
        echo "azure"
    else
        echo "on-premises"
    fi
}

CLOUD_PROVIDER=$(detect_cloud_provider)
echo "🌐 Detected cloud provider: ${CLOUD_PROVIDER}"

# Cloud-specific configurations
case ${CLOUD_PROVIDER} in
    "aws")
        INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
        REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
        AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
        ;;
    "gcp")
        INSTANCE_ID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/id" -H "Metadata-Flavor: Google")
        REGION=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google" | cut -d'/' -f4)
        ;;
    "azure")
        INSTANCE_ID=$(curl -s -H "Metadata:true" "http://169.254.169.254/metadata/instance/compute/vmId?api-version=2021-02-01&format=text")
        REGION=$(curl -s -H "Metadata:true" "http://169.254.169.254/metadata/instance/compute/location?api-version=2021-02-01&format=text")
        ;;
esac

# Generate cloud-specific configuration
generate_config() {
    cat > /etc/openfinops/telemetry.yaml <<EOF
service:
  name: "${HOSTNAME}-telemetry"
  cloud_provider: "${CLOUD_PROVIDER}"
  instance_id: "${INSTANCE_ID}"
  region: "${REGION}"
  availability_zone: "${AZ}"

telemetry:
  endpoint: "https://telemetry.openfinops.com"
  api_key: "${OPENFINOPS_API_KEY}"

cloud_metadata:
  enabled: true
  collection_interval: 300

collection:
  cloud_specific_metrics: true
  cost_attribution: true
EOF
}
```

### 2. Infrastructure as Code Templates

#### Terraform Module
```hcl
# modules/openfinops-telemetry/main.tf
variable "cloud_provider" {
  description = "Cloud provider (aws, gcp, azure)"
  type        = string
}

variable "api_key" {
  description = "OpenFinOps API key"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# AWS Implementation
resource "aws_instance" "telemetry_agent" {
  count                  = var.cloud_provider == "aws" ? 1 : 0
  ami                   = data.aws_ami.ubuntu.id
  instance_type         = "t3.small"
  vpc_security_group_ids = [aws_security_group.telemetry[0].id]

  user_data = templatefile("${path.module}/scripts/install-agent.sh", {
    api_key      = var.api_key
    environment  = var.environment
    cloud_provider = "aws"
  })

  tags = {
    Name = "openfinops-telemetry"
    Environment = var.environment
  }
}

# GCP Implementation
resource "google_compute_instance" "telemetry_agent" {
  count        = var.cloud_provider == "gcp" ? 1 : 0
  name         = "openfinops-telemetry"
  machine_type = "e2-small"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
    }
  }

  metadata_startup_script = templatefile("${path.module}/scripts/install-agent.sh", {
    api_key      = var.api_key
    environment  = var.environment
    cloud_provider = "gcp"
  })

  service_account {
    email  = google_service_account.telemetry[0].email
    scopes = ["cloud-platform"]
  }
}

# Azure Implementation
resource "azurerm_linux_virtual_machine" "telemetry_agent" {
  count               = var.cloud_provider == "azure" ? 1 : 0
  name                = "openfinops-telemetry"
  resource_group_name = var.resource_group_name
  location            = var.location
  size                = "Standard_B1s"

  custom_data = base64encode(templatefile("${path.module}/scripts/install-agent.sh", {
    api_key      = var.api_key
    environment  = var.environment
    cloud_provider = "azure"
  }))

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }
}
```

### 3. Cloud-Specific Agent Configurations

#### AWS Configuration
```yaml
# config/aws-telemetry.yaml
service:
  name: "aws-telemetry"
  cloud_provider: "aws"

aws:
  region: "us-east-1"
  credentials:
    role_arn: "arn:aws:iam::ACCOUNT:role/OpenFinOps-TelemetryRole"

collection:
  cloudwatch_metrics: true
  ec2_metadata: true
  ecs_tasks: true
  lambda_functions: true

integrations:
  aws_cost_explorer: true
  aws_cloudtrail: true
```

#### GCP Configuration
```yaml
# config/gcp-telemetry.yaml
service:
  name: "gcp-telemetry"
  cloud_provider: "gcp"

gcp:
  project_id: "your-project-id"
  credentials_file: "/etc/openfinops/gcp-credentials.json"

collection:
  stackdriver_metrics: true
  compute_metadata: true
  kubernetes_engine: true
  cloud_functions: true

integrations:
  gcp_billing: true
  gcp_audit_logs: true
```

#### Azure Configuration
```yaml
# config/azure-telemetry.yaml
service:
  name: "azure-telemetry"
  cloud_provider: "azure"

azure:
  subscription_id: "your-subscription-id"
  tenant_id: "your-tenant-id"
  client_id: "your-client-id"
  client_secret: "your-client-secret"

collection:
  azure_monitor: true
  vm_metadata: true
  aks_clusters: true
  azure_functions: true

integrations:
  azure_cost_management: true
  azure_activity_logs: true
```

## 🔧 Agent Configuration Options

### Core Configuration
```yaml
# /etc/openfinops/telemetry.yaml
service:
  name: "my-service-telemetry"
  version: "1.0.0"
  environment: "production"
  tags:
    team: "ai-ops"
    project: "openfinops"

telemetry:
  endpoint: "https://telemetry.openfinops.com"
  api_key: "${OPENFINOPS_API_KEY}"
  timeout: 30
  retry_attempts: 3

collection:
  # Metrics collection
  metrics_interval: 30          # seconds
  metrics_buffer_size: 1000

  # Tracing
  trace_sampling_rate: 0.1      # 10% sampling
  trace_max_spans: 1000

  # Logging
  log_level: "info"
  log_max_size: "100MB"
  log_retention_days: 30

features:
  # Core features
  distributed_tracing: true
  metrics_collection: true
  log_aggregation: true

  # AI-specific features
  llm_monitoring: true
  agent_workflows: true
  training_metrics: true
  cost_tracking: true

  # Advanced features
  anomaly_detection: true
  performance_profiling: false
  security_monitoring: true

filters:
  # Exclude sensitive data
  exclude_headers:
    - "authorization"
    - "x-api-key"
  exclude_query_params:
    - "password"
    - "token"

resource_limits:
  max_memory_mb: 512
  max_cpu_percent: 10
  max_disk_mb: 1000
```

## 📊 Monitoring and Verification

### Health Check Endpoints
```bash
# Check agent status
curl http://localhost:8888/health

# Get metrics
curl http://localhost:8888/metrics

# Check configuration
curl http://localhost:8888/config
```

### Verification Commands
```bash
# Service status
sudo systemctl status openfinops-telemetry

# Recent logs
sudo journalctl -u openfinops-telemetry -f --lines=100

# Configuration validation
openfinops-telemetry validate-config

# Connection test
openfinops-telemetry test-connection
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Issues**
```bash
# Test network connectivity
curl -v https://telemetry.openfinops.com/health

# Check DNS resolution
nslookup telemetry.openfinops.com
```

2. **Permission Issues**
```bash
# Check file permissions
ls -la /etc/openfinops/telemetry.yaml
sudo chown openfinops:openfinops /etc/openfinops/telemetry.yaml
```

3. **Memory Issues**
```bash
# Monitor memory usage
ps aux | grep openfinops-telemetry
sudo systemctl edit openfinops-telemetry
# Add: [Service]
#      MemoryLimit=512M
```

## 🔒 Security Considerations

### API Key Management
- Store API keys in secure vaults (AWS Secrets Manager, Azure Key Vault, etc.)
- Use environment variables for container deployments
- Rotate keys regularly

### Network Security
- Configure firewall rules for outbound HTTPS only
- Use VPC endpoints where available
- Enable TLS 1.3 for all connections

### Access Control
- Run agent with minimal privileges
- Use dedicated service accounts
- Enable audit logging

## 📈 Performance Tuning

### Resource Optimization
```yaml
# High-traffic environments
collection:
  metrics_interval: 60
  trace_sampling_rate: 0.01
  batch_size: 5000

# Low-latency requirements
collection:
  metrics_interval: 10
  trace_sampling_rate: 1.0
  real_time_streaming: true
```

This comprehensive deployment guide ensures reliable telemetry agent installation across any infrastructure while maintaining optimal performance and security.