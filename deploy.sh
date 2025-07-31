#!/bin/bash

# Cross-Chain Arbitrage Platform Deployment Script

set -e

echo "🚀 Deploying Cross-Chain Arbitrage Platform..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p deployment/nginx/ssl
mkdir -p deployment/grafana/dashboards
mkdir -p deployment/grafana/datasources

# Set environment variables
export DATABASE_URL="postgresql://arbitrage_user:password@localhost:5432/arbitrage_db"
export REDIS_URL="redis://localhost:6379"
export INDEXER_URL="http://your-indexer-url"
export SECRET_KEY="your_secret_key_here"
export JWT_SECRET="your_jwt_secret_here"

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Test API health
echo "🔍 Testing API health..."
curl -f http://localhost:8000/health || echo "❌ API health check failed"

# Test frontend
echo "🔍 Testing frontend..."
curl -f http://localhost:3000 || echo "❌ Frontend health check failed"

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Platform URLs:"
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Grafana: http://localhost:3001 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose up -d --build"
echo ""
echo "📝 Next steps:"
echo "   1. Update the INDEXER_URL in docker-compose.yml to point to your blockchain indexer"
echo "   2. Configure your API keys and secrets"
echo "   3. Set up SSL certificates for production"
echo "   4. Configure monitoring dashboards in Grafana"