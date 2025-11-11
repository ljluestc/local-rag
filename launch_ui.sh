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
# Check if OLLAMA_USE_HOST_NETWORK is set to use host network mode
if [ "${OLLAMA_USE_HOST_NETWORK:-false}" = "true" ]; then
    echo "📡 Using host network mode (Ollama accessible at localhost:11434)"
    docker run -d \
      --name local-rag-8502 \
      --network host \
      -v "$(pwd)/storage:/home/appuser/storage" \
      -v "$(pwd)/data:/home/appuser/data" \
      local-rag-dev:latest
else
    echo "📡 Using bridge network mode (Ollama accessible at host.docker.internal:11434)"
    docker run -d \
      --name local-rag-8502 \
      --add-host host.docker.internal:host-gateway \
      -p 8502:8501 \
      -v "$(pwd)/storage:/home/appuser/storage" \
      -v "$(pwd)/data:/home/appuser/data" \
      local-rag-dev:latest
fi

# Wait for UI to be ready
echo "⏳ Waiting for UI to start (15 seconds)..."
sleep 15

# Check if UI is ready
echo "🔍 Checking UI health..."
# Use different port based on network mode
if [ "${OLLAMA_USE_HOST_NETWORK:-false}" = "true" ]; then
    # Host network mode: UI runs directly on port 8501
    HEALTH_PORT=8501
    UI_URL="http://localhost:8501"
else
    # Bridge network mode: UI is mapped to port 8502
    HEALTH_PORT=8502
    UI_URL="http://localhost:8502"
fi

if curl -fsS http://localhost:${HEALTH_PORT}/_stcore/health > /dev/null 2>&1; then
    echo ""
    echo "✅ UI is ready!"
    echo ""
    echo "🌐 Access the UI at: ${UI_URL}"
    if [ "${OLLAMA_USE_HOST_NETWORK:-false}" = "true" ]; then
        echo "📡 Ollama endpoint: http://localhost:11434 (auto-detected)"
    fi
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
    echo "Or try accessing: ${UI_URL}"
fi

