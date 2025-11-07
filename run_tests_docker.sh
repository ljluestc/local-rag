#!/bin/bash
# Run tests in Docker container
# This script runs tests against a running UI container

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Running tests in Docker${NC}"
echo "================================"

# Check if UI container is running
if ! docker ps | grep -q local-rag-8502; then
    echo -e "${YELLOW}UI container not found. Starting...${NC}"
    cd "$(dirname "$0")"
    docker rm -f local-rag-8502 2>/dev/null || true
    docker run -d --name local-rag-8502 --no-healthcheck \
        --add-host host.docker.internal:host-gateway \
        -p 8502:8501 \
        -v "$(pwd)/storage:/home/appuser/storage" \
        -v "$(pwd)/data:/home/appuser/data" \
        local-rag-dev:latest
    
    echo "Waiting for UI to start..."
    sleep 5
    for i in {1..30}; do
        if curl -fsS http://localhost:8502/_stcore/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ UI is ready${NC}"
            break
        fi
        sleep 1
    done
fi

# Build test image if needed
if ! docker images | grep -q local-rag-test; then
    echo -e "${YELLOW}Building test image...${NC}"
    docker build -f Dockerfile.test -t local-rag-test .
fi

# Run tests
echo -e "${GREEN}Running tests...${NC}"
docker run --rm --network host \
    -e STREAMLIT_URL=http://localhost:8502 \
    -v "$(pwd):/app" \
    -w /app \
    local-rag-test \
    pytest tests/test_ui.py -v "$@"

