#!/bin/bash
# DAGnostics MLOps Environment Setup Script
# Start complete MLOps stack with Docker Compose

set -e

echo "🚀 Starting DAGnostics MLOps Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    if ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Create necessary directories
print_status "Creating MLOps directories..."
mkdir -p {data/training,mlops/{experiments,data_reports,models,artifacts,logs,pipeline_results,evaluations,optuna_studies},notebooks}

# Stop existing containers (if any)
print_status "Stopping existing MLOps containers..."
$COMPOSE_CMD -f docker/docker-compose.mlops.yml down >/dev/null 2>&1 || true

# Pull/build images
print_status "Building MLOps containers..."
$COMPOSE_CMD -f docker/docker-compose.mlops.yml build --no-cache

# Start the MLOps stack
print_status "Starting MLOps stack..."
$COMPOSE_CMD -f docker/docker-compose.mlops.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to start..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check PostgreSQL
if $COMPOSE_CMD -f docker/docker-compose.mlops.yml ps postgres | grep -q "Up"; then
    print_success "PostgreSQL is running"
else
    print_warning "PostgreSQL may not be ready yet"
fi

# Check MLflow
if curl -s http://localhost:5000/health >/dev/null 2>&1; then
    print_success "MLflow is running on http://localhost:5000"
else
    print_warning "MLflow is starting up... (may take a moment)"
fi

# Check Jupyter
if curl -s http://localhost:8888 >/dev/null 2>&1; then
    print_success "Jupyter Lab is running on http://localhost:8888"
else
    print_warning "Jupyter Lab is starting up..."
fi

# Check Optuna Dashboard
if curl -s http://localhost:8080 >/dev/null 2>&1; then
    print_success "Optuna Dashboard is running on http://localhost:8080"
else
    print_warning "Optuna Dashboard is starting up..."
fi

# Check Model Registry API
if curl -s http://localhost:8001 >/dev/null 2>&1; then
    print_success "Model Registry API is running on http://localhost:8001"
else
    print_warning "Model Registry API is starting up..."
fi

echo ""
print_success "DAGnostics MLOps Environment is starting up!"
echo ""
echo "📊 Available Services:"
echo "  • MLflow Tracking:     http://localhost:5000"
echo "  • Jupyter Lab:         http://localhost:8888"  
echo "  • Optuna Dashboard:    http://localhost:8080"
echo "  • Model Registry API:  http://localhost:8001"
echo ""
echo "🔧 MLOps Commands:"
echo "  • Run training:        docker exec dagnostics-mlops-training python -m mlops.cli train"
echo "  • Validate data:       docker exec dagnostics-mlops-training python -m mlops.cli validate-data data/training/train_dataset.jsonl"
echo "  • List models:         docker exec dagnostics-mlops-training python -m mlops.cli list-models"
echo "  • System status:       docker exec dagnostics-mlops-training python -m mlops.cli status"
echo ""
echo "📋 Container Management:"
echo "  • View logs:           $COMPOSE_CMD -f docker/docker-compose.mlops.yml logs -f [service_name]"
echo "  • Stop environment:    $COMPOSE_CMD -f docker/docker-compose.mlops.yml down"
echo "  • Restart service:     $COMPOSE_CMD -f docker/docker-compose.mlops.yml restart [service_name]"
echo ""

# Wait for all services to be fully ready
print_status "Waiting for all services to be ready..."
sleep 30

# Test MLOps functionality
print_status "Testing MLOps functionality..."
docker exec dagnostics-mlops-training python -m mlops.cli status || print_warning "MLOps CLI test failed"

print_success "MLOps Environment setup complete!"
print_status "You can now use your production-grade MLOps pipeline."

# Show running containers
echo ""
echo "🐳 Running Containers:"
$COMPOSE_CMD -f docker/docker-compose.mlops.yml ps