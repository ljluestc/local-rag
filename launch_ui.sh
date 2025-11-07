#!/bin/bash
# Launch script for Local RAG UI

set -e

echo "🚀 Launching Local RAG UI..."

# Navigate to project directory
cd "$(dirname "$0")"

# Stop existing container if running
echo "📦 Stopping existing container (if any)..."
docker rm -f local-rag-8502 2>/dev/null || true

# Build image if needed (check if it exists)
if ! docker images | grep -q "local-rag-dev.*latest"; then
    echo "🔨 Building Docker image..."
    docker build -t local-rag-dev:latest .
else
    echo "✅ Docker image already exists"
fi

# Launch the container
echo "🚀 Starting UI container..."
docker run -d \
  --name local-rag-8502 \
  --add-host host.docker.internal:host-gateway \
  -p 8502:8501 \
  -v "$(pwd)/storage:/home/appuser/storage" \
  -v "$(pwd)/data:/home/appuser/data" \
  local-rag-dev:latest

# Wait for UI to be ready
echo "⏳ Waiting for UI to start (15 seconds)..."
sleep 15

# Check if UI is ready
echo "🔍 Checking UI health..."
if curl -fsS http://localhost:8502/_stcore/health > /dev/null 2>&1; then
    echo ""
    echo "✅ UI is ready!"
    echo ""
    echo "🌐 Access the UI at: http://localhost:8502"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    docker logs -f local-rag-8502"
    echo "   Stop UI:      docker stop local-rag-8502"
    echo "   Restart UI:   docker restart local-rag-8502"
    echo "   Remove:       docker rm -f local-rag-8502"
    echo ""
else
    echo "⚠️  UI might still be starting. Check logs with:"
    echo "   docker logs local-rag-8502"
    echo ""
    echo "Or try accessing: http://localhost:8502"
fi

