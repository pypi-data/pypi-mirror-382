# OpenFinOps Quick Start Guide

Get OpenFinOps up and running in 5 minutes!

## 🚀 Quick Deploy Options

### Option 1: Docker (Recommended - Full Stack)

Deploy the complete OpenFinOps platform with website and demo in one command:

```bash
# Clone the repository
git clone https://github.com/rdmurugan/openfinops.git
cd openfinops

# Start everything with Docker Compose
docker-compose up -d

# Access the application
# Website: http://localhost
# Server/Demo: http://localhost:8080
```

**That's it!** 🎉

View logs:
```bash
docker-compose logs -f
```

Stop services:
```bash
docker-compose down
```

---

### Option 2: Local Development

Run on your local machine without Docker:

```bash
# Clone and setup
git clone https://github.com/rdmurugan/openfinops.git
cd openfinops

# Install OpenFinOps
pip install -e .

# Use the deployment script
./deploy.sh local
```

**Access:**
- Website: http://localhost:8888
- Server/Demo: http://localhost:8080

**Stop:**
```bash
./deploy.sh stop
```

---

### Option 3: GitHub Pages (Website Only)

Deploy the marketing website to GitHub Pages:

```bash
# Clone repository
git clone https://github.com/rdmurugan/openfinops.git
cd openfinops

# Deploy to GitHub Pages
./deploy.sh github-pages

# Or manually:
# 1. Push to GitHub
# 2. Go to Settings → Pages
# 3. Source: main branch, /website folder
```

---

### Option 4: Cloud Platforms

#### Netlify
```bash
./deploy.sh netlify
```

#### Vercel
```bash
./deploy.sh vercel
```

---

## 📊 What You Get

After deployment, you'll have access to:

### 1. **Marketing Website**
- Feature overview
- Complete documentation
- API reference
- Live demo links

### 2. **OpenFinOps Server** (with demo data)
- **Overview Dashboard** - Real-time cost metrics
- **CFO Dashboard** - Financial analytics and ROI
- **COO Dashboard** - Operational metrics
- **Infrastructure Dashboard** - Resource utilization
- **WebSocket Live Updates** - Real-time data every 5 seconds

### 3. **REST API**
- `/api/metrics` - Cost and usage metrics
- `/api/dashboard/cfo` - CFO dashboard data
- `/api/dashboard/coo` - COO dashboard data
- `/api/dashboard/infrastructure` - Infrastructure data
- `/api/v1/telemetry/ingest` - Telemetry data ingestion

---

## 🔧 Next Steps

### 1. Deploy Telemetry Agents

Start collecting real cost data from your infrastructure:

#### AWS Agent
```bash
python agents/aws_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --aws-region us-west-2
```

#### Databricks Agent
```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi***

python agents/databricks_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --databricks-host $DATABRICKS_HOST \
  --databricks-token $DATABRICKS_TOKEN
```

#### Snowflake Agent
```bash
export SNOWFLAKE_USER=admin_user
export SNOWFLAKE_PASSWORD=***

python agents/snowflake_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --snowflake-account xy12345.us-east-1 \
  --edition enterprise
```

#### SaaS Services Agent
```bash
# Create configuration
python agents/saas_services_telemetry_agent.py --create-config config.json

# Edit config.json with your credentials
# Then run:
python agents/saas_services_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --config config.json
```

### 2. Configure Custom Domain

#### For GitHub Pages:
```bash
# Add CNAME file
echo "openfinops.io" > website/CNAME

# Configure DNS:
# Type: CNAME
# Name: www
# Value: yourusername.github.io
```

#### For Netlify/Vercel:
1. Go to domain settings in dashboard
2. Add custom domain
3. Follow DNS configuration instructions

### 3. Enable SSL/HTTPS

#### Using Let's Encrypt (Certbot):
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d openfinops.io -d www.openfinops.io

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 📖 Documentation

### Full Documentation
- **Getting Started:** http://localhost:8888/documentation.html
- **API Reference:** http://localhost:8888/api.html
- **Features:** http://localhost:8888/features.html
- **Deployment Guide:** [website/DEPLOYMENT.md](website/DEPLOYMENT.md)
- **Agent README:** [agents/README.md](agents/README.md)

### Quick Links
- 📘 [Installation Guide](website/DEPLOYMENT.md#installation)
- 🔧 [Configuration](website/DEPLOYMENT.md#configuration)
- 🚀 [Deployment Options](website/DEPLOYMENT.md#deployment-options)
- 🔌 [Agent Setup](agents/README.md)
- 🐛 [Troubleshooting](website/DEPLOYMENT.md#troubleshooting)

---

## 🎯 Common Use Cases

### Use Case 1: Monitor AWS + Databricks Costs
```bash
# Terminal 1: Start OpenFinOps server
docker-compose up -d

# Terminal 2: Start AWS agent
python agents/aws_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --aws-region us-west-2

# Terminal 3: Start Databricks agent
python agents/databricks_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --databricks-host $DATABRICKS_HOST \
  --databricks-token $DATABRICKS_TOKEN

# View in browser: http://localhost:8080
```

### Use Case 2: Track Snowflake + SaaS Costs
```bash
# Start server
docker-compose up -d

# Configure SaaS services
cat > saas_config.json << 'EOF'
{
  "mongodb_atlas": {"enabled": true, ...},
  "github_actions": {"enabled": true, ...}
}
EOF

# Start agents
python agents/snowflake_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --snowflake-account xy12345.us-east-1

python agents/saas_services_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --config saas_config.json
```

### Use Case 3: Public Demo Website
```bash
# Deploy website to GitHub Pages
./deploy.sh github-pages

# Deploy server to cloud (e.g., AWS EC2)
ssh your-server
git clone https://github.com/rdmurugan/openfinops.git
cd openfinops
docker-compose up -d

# Update website demo URLs to point to cloud server
# Edit website/demo.html:
# Change http://localhost:8080 to https://demo.openfinops.io
```

---

## 🐳 Docker Commands Cheat Sheet

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f openfinops-server
docker-compose logs -f openfinops-website

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild images
docker-compose build

# Remove all data (fresh start)
docker-compose down -v

# Check service status
docker-compose ps

# Execute command in container
docker-compose exec openfinops-server bash
```

---

## 🔍 Health Checks

### Check if services are running:

```bash
# OpenFinOps server
curl http://localhost:8080/health
# Expected: {"status": "healthy"}

# Website
curl http://localhost/health
# Expected: healthy

# Check specific dashboard
curl http://localhost:8080/dashboard/cfo
# Should return HTML
```

---

## 🐛 Troubleshooting

### Server not starting
```bash
# Check logs
docker-compose logs openfinops-server

# Common issues:
# 1. Port 8080 already in use
lsof -ti:8080 | xargs kill -9

# 2. Missing dependencies
pip install -r requirements.txt
```

### Website not loading
```bash
# Check logs
docker-compose logs openfinops-website

# Verify nginx config
docker-compose exec openfinops-website nginx -t

# Restart nginx
docker-compose restart openfinops-website
```

### Agents not connecting
```bash
# Test connectivity
curl http://localhost:8080/api/v1/agents/register

# Check agent logs
python agents/aws_telemetry_agent.py --openfinops-endpoint http://localhost:8080 --aws-region us-west-2 2>&1 | tee agent.log
```

---

## 📞 Getting Help

- **Issues:** https://github.com/rdmurugan/openfinops/issues
- **Documentation:** http://localhost:8888/documentation.html
- **API Reference:** http://localhost:8888/api.html

---

## 🎉 Success!

You should now have:
- ✅ OpenFinOps server running on http://localhost:8080
- ✅ Website running on http://localhost (or http://localhost:8888)
- ✅ Live dashboards with demo data
- ✅ Real-time WebSocket updates

**Ready to deploy to production?** See [DEPLOYMENT.md](website/DEPLOYMENT.md)

**Want to connect real data sources?** See [agents/README.md](agents/README.md)

Happy cost optimizing! 💰📊🚀
