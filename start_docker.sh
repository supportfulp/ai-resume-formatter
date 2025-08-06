#!/bin/bash

# Script to start the Resume Processor application with Docker Compose

set -e

# Default to development mode
MODE=${1:-development}

case $MODE in
    "development"|"dev")
        echo "🚀 Starting Resume Processor in DEVELOPMENT mode..."
        echo "📱 React app will be available at: http://localhost:3000"
        echo "🔧 API server will be available at: http://localhost:8000"
        echo "🗄️  Database will be available at: localhost:5432"
        echo ""
        
        # Start services with development profile
        docker-compose --profile development up -d postgres api-server react-app
        
        echo "✅ Development services started!"
        echo "📊 View logs: docker-compose logs -f"
        echo "🛑 Stop services: docker-compose down"
        ;;
        
    "production"|"prod")
        echo "🚀 Starting Resume Processor in PRODUCTION mode..."
        echo "🌐 Application will be available at: http://localhost"
        echo "🗄️  Database will be available at: localhost:5432"
        echo ""
        
        # Start all services with production profile
        docker-compose --profile production up -d
        
        echo "✅ Production services started!"
        echo "📊 View logs: docker-compose logs -f"
        echo "🛑 Stop services: docker-compose down"
        ;;
        
    "full")
        echo "🚀 Starting Resume Processor with ALL services..."
        echo "🌐 Application will be available at: http://localhost (with nginx proxy)"
        echo "📱 React app will be available at: http://localhost:3000"
        echo "🔧 API server will be available at: http://localhost:8000"
        echo "🗄️  Database will be available at: localhost:5432"
        echo ""
        
        # Start all services
        docker-compose up -d
        
        echo "✅ All services started!"
        echo "📊 View logs: docker-compose logs -f"
        echo "🛑 Stop services: docker-compose down"
        ;;
        
    *)
        echo "❌ Invalid mode: $MODE"
        echo ""
        echo "Usage: $0 [development|dev|production|prod|full]"
        echo ""
        echo "Modes:"
        echo "  development, dev  - Start with development React app (hot reload)"
        echo "  production, prod  - Start with production React app (built)"
        echo "  full             - Start all services including nginx proxy"
        echo ""
        echo "Examples:"
        echo "  $0 development"
        echo "  $0 production"
        echo "  $0 full"
        exit 1
        ;;
esac

echo ""
echo "🔍 Checking service health..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running successfully!"
else
    echo "⚠️  Some services may not be running. Check logs with: docker-compose logs"
fi 