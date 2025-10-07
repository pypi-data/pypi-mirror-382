#!/bin/bash

#####################################################
# OpenFinOps Deployment Script
#
# Deploys the OpenFinOps website and server
# Supports: GitHub Pages, Netlify, Vercel, Docker
#####################################################

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEMO_URL="${DEMO_URL:-http://localhost:8080}"
DEPLOYMENT_METHOD="${1:-help}"

print_header() {
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════"
    echo "  OpenFinOps Deployment Script"
    echo "═══════════════════════════════════════════════"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update demo URLs in HTML files
update_demo_urls() {
    local demo_url="$1"
    print_info "Updating demo URLs to: $demo_url"

    # Create backup
    cp website/demo.html website/demo.html.bak

    # Update URLs (handle both http://localhost:8080 and custom URLs)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|http://localhost:8080|$demo_url|g" website/demo.html
        sed -i '' "s|http://127.0.0.1:8080|$demo_url|g" website/demo.html
    else
        # Linux
        sed -i "s|http://localhost:8080|$demo_url|g" website/demo.html
        sed -i "s|http://127.0.0.1:8080|$demo_url|g" website/demo.html
    fi

    print_success "Demo URLs updated"
}

# Restore original URLs
restore_demo_urls() {
    if [ -f website/demo.html.bak ]; then
        mv website/demo.html.bak website/demo.html
        print_info "Restored original demo URLs"
    fi
}

# Deploy to GitHub Pages
deploy_github_pages() {
    print_header
    echo "Deploying to GitHub Pages..."
    echo

    # Check if git is available
    if ! command_exists git; then
        print_error "Git is not installed"
        exit 1
    fi

    # Check for demo URL
    read -p "Enter demo server URL (default: http://localhost:8080): " demo_input
    demo_url="${demo_input:-http://localhost:8080}"

    update_demo_urls "$demo_url"

    # Commit and push
    git add website/
    git commit -m "Deploy OpenFinOps website to GitHub Pages

- Updated demo URLs to $demo_url
- Deployed on $(date)"

    git push origin main

    print_success "Pushed to GitHub"
    echo
    print_info "Next steps:"
    echo "1. Go to https://github.com/rdmurugan/openfinops"
    echo "2. Settings → Pages"
    echo "3. Set source to 'main' branch '/website' folder"
    echo "4. Your site will be live at: https://rdmurugan.github.io/openfinops/"
    echo
}

# Deploy to Netlify
deploy_netlify() {
    print_header
    echo "Deploying to Netlify..."
    echo

    # Check if netlify-cli is installed
    if ! command_exists netlify; then
        print_warning "Netlify CLI not found. Installing..."
        npm install -g netlify-cli
    fi

    # Check for demo URL
    read -p "Enter demo server URL (default: http://localhost:8080): " demo_input
    demo_url="${demo_input:-http://localhost:8080}"

    update_demo_urls "$demo_url"

    # Login if needed
    print_info "Logging into Netlify..."
    netlify login

    # Deploy
    cd website
    netlify deploy --prod
    cd ..

    restore_demo_urls

    print_success "Deployed to Netlify"
}

# Deploy to Vercel
deploy_vercel() {
    print_header
    echo "Deploying to Vercel..."
    echo

    # Check if vercel is installed
    if ! command_exists vercel; then
        print_warning "Vercel CLI not found. Installing..."
        npm install -g vercel
    fi

    # Check for demo URL
    read -p "Enter demo server URL (default: http://localhost:8080): " demo_input
    demo_url="${demo_input:-http://localhost:8080}"

    update_demo_urls "$demo_url"

    # Deploy
    cd website
    vercel --prod
    cd ..

    restore_demo_urls

    print_success "Deployed to Vercel"
}

# Deploy with Docker
deploy_docker() {
    print_header
    echo "Deploying with Docker..."
    echo

    # Check if docker is installed
    if ! command_exists docker; then
        print_error "Docker is not installed"
        exit 1
    fi

    # Build OpenFinOps server
    print_info "Building OpenFinOps server..."
    docker build -t openfinops-server .

    # Build website
    print_info "Building website..."
    cd website
    docker build -t openfinops-website .
    cd ..

    # Check if docker-compose is available
    if command_exists docker-compose; then
        print_info "Starting services with docker-compose..."
        docker-compose up -d

        print_success "Services started"
        echo
        print_info "Services running:"
        echo "  - OpenFinOps Server: http://localhost:8080"
        echo "  - Website: http://localhost:80"
        echo
        print_info "View logs: docker-compose logs -f"
        print_info "Stop services: docker-compose down"
    else
        # Manual docker run
        print_info "Starting OpenFinOps server..."
        docker run -d \
            --name openfinops-server \
            -p 8080:8080 \
            openfinops-server

        print_info "Starting website..."
        docker run -d \
            --name openfinops-website \
            -p 80:80 \
            --link openfinops-server:openfinops-server \
            openfinops-website

        print_success "Containers started"
        echo
        print_info "Services running:"
        echo "  - OpenFinOps Server: http://localhost:8080"
        echo "  - Website: http://localhost:80"
        echo
        print_info "View logs:"
        echo "  docker logs -f openfinops-server"
        echo "  docker logs -f openfinops-website"
        echo
        print_info "Stop containers:"
        echo "  docker stop openfinops-server openfinops-website"
        echo "  docker rm openfinops-server openfinops-website"
    fi
}

# Start local development
deploy_local() {
    print_header
    echo "Starting local development environment..."
    echo

    # Start OpenFinOps server in background
    print_info "Starting OpenFinOps server on port 8080..."
    python -m openfinops.webui.server --host 127.0.0.1 --port 8080 > /tmp/openfinops-server.log 2>&1 &
    SERVER_PID=$!

    # Wait for server to start
    sleep 3

    # Check if server is running
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        print_success "OpenFinOps server started (PID: $SERVER_PID)"
    else
        print_error "Failed to start OpenFinOps server"
        print_info "Check logs: tail -f /tmp/openfinops-server.log"
        exit 1
    fi

    # Start website server
    print_info "Starting website server on port 8888..."
    cd website
    python -m http.server 8888 > /tmp/openfinops-website.log 2>&1 &
    WEBSITE_PID=$!
    cd ..

    sleep 2

    print_success "Website server started (PID: $WEBSITE_PID)"
    echo
    print_success "Development environment ready!"
    echo
    print_info "Access the application:"
    echo "  - Website: http://localhost:8888"
    echo "  - Server/Demo: http://localhost:8080"
    echo
    print_info "Logs:"
    echo "  - Server: tail -f /tmp/openfinops-server.log"
    echo "  - Website: tail -f /tmp/openfinops-website.log"
    echo
    print_info "Stop services:"
    echo "  kill $SERVER_PID $WEBSITE_PID"
    echo

    # Save PIDs
    echo "$SERVER_PID" > /tmp/openfinops-server.pid
    echo "$WEBSITE_PID" > /tmp/openfinops-website.pid
}

# Stop local development
stop_local() {
    print_header
    echo "Stopping local development environment..."
    echo

    # Kill processes
    if [ -f /tmp/openfinops-server.pid ]; then
        SERVER_PID=$(cat /tmp/openfinops-server.pid)
        if kill -0 $SERVER_PID 2>/dev/null; then
            kill $SERVER_PID
            print_success "Stopped OpenFinOps server (PID: $SERVER_PID)"
        fi
        rm /tmp/openfinops-server.pid
    fi

    if [ -f /tmp/openfinops-website.pid ]; then
        WEBSITE_PID=$(cat /tmp/openfinops-website.pid)
        if kill -0 $WEBSITE_PID 2>/dev/null; then
            kill $WEBSITE_PID
            print_success "Stopped website server (PID: $WEBSITE_PID)"
        fi
        rm /tmp/openfinops-website.pid
    fi

    # Also kill any running http.server on port 8888
    lsof -ti:8888 | xargs kill -9 2>/dev/null || true

    print_success "All services stopped"
}

# Show help
show_help() {
    print_header
    cat << EOF
Usage: ./deploy.sh [METHOD]

Deployment Methods:
  github-pages    Deploy to GitHub Pages
  netlify         Deploy to Netlify
  vercel          Deploy to Vercel
  docker          Deploy with Docker
  local           Start local development environment
  stop            Stop local development environment
  help            Show this help message

Environment Variables:
  DEMO_URL        URL of demo server (default: http://localhost:8080)

Examples:
  # Deploy to GitHub Pages with custom demo URL
  DEMO_URL=https://demo.openfinops.io ./deploy.sh github-pages

  # Start local development
  ./deploy.sh local

  # Deploy with Docker
  ./deploy.sh docker

  # Stop local environment
  ./deploy.sh stop

For detailed deployment instructions, see:
  website/DEPLOYMENT.md

EOF
}

# Main script
case "$DEPLOYMENT_METHOD" in
    github-pages)
        deploy_github_pages
        ;;
    netlify)
        deploy_netlify
        ;;
    vercel)
        deploy_vercel
        ;;
    docker)
        deploy_docker
        ;;
    local)
        deploy_local
        ;;
    stop)
        stop_local
        ;;
    help|--help|-h|*)
        show_help
        ;;
esac
