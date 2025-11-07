#!/bin/bash
# Test runner script for Local RAG
# Supports both local and Docker execution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Local RAG Test Runner${NC}"
echo "================================"

# Check if running in Docker
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo -e "${YELLOW}Running in Docker container${NC}"
    MODE="docker"
else
    echo -e "${YELLOW}Running locally${NC}"
    MODE="local"
fi

# Check if Streamlit is running
STREAMLIT_URL=${STREAMLIT_URL:-"http://localhost:8501"}
echo -e "${BLUE}Checking if Streamlit is running at ${STREAMLIT_URL}...${NC}"

if curl -fsS "${STREAMLIT_URL}/_stcore/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Streamlit is running${NC}"
else
    echo -e "${RED}✗ Streamlit is not running at ${STREAMLIT_URL}${NC}"
    echo -e "${YELLOW}Please start the UI first:${NC}"
    echo "  Local: streamlit run main.py"
    echo "  Docker: docker run -d -p 8501:8501 local-rag-dev:latest"
    exit 1
fi

# Check if playwright is installed
if ! python3 -c "import playwright" 2>/dev/null; then
    echo -e "${YELLOW}Playwright not found.${NC}"
    if [ "$MODE" = "docker" ]; then
        echo -e "${YELLOW}Installing in Docker...${NC}"
        pip install playwright pytest pytest-playwright
        playwright install chromium
    else
        if command -v pipenv &> /dev/null; then
            echo -e "${YELLOW}Installing via pipenv...${NC}"
            pipenv install --dev
            pipenv run playwright install chromium
        else
            echo -e "${RED}Error: Playwright not installed and pipenv not available.${NC}"
            echo -e "${YELLOW}Please install dependencies:${NC}"
            echo "  pipenv install --dev"
            echo "  pipenv run playwright install chromium"
            echo ""
            echo -e "${YELLOW}Or run tests in Docker:${NC}"
            echo "  docker run --rm --network host -e STREAMLIT_URL=${STREAMLIT_URL} -v \$(pwd):/app -w /app local-rag-dev:latest pytest tests/test_ui.py -v"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}Running tests against: ${STREAMLIT_URL}${NC}"
echo ""

# Run tests
if [ "$MODE" = "docker" ]; then
    pytest tests/test_ui.py -v "$@"
else
    if command -v pipenv &> /dev/null; then
        pipenv run pytest tests/test_ui.py -v "$@"
    else
        pytest tests/test_ui.py -v "$@"
    fi
fi

