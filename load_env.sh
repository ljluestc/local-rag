#!/bin/bash
# Load environment variables from .env file
# This script properly handles comments and empty lines

if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Run ./quick_setup.sh first."
    exit 1
fi

# Load .env file, skipping comments and empty lines
set -a
source <(grep -v '^#' .env | grep -v '^$')
set +a

echo "✅ Environment variables loaded from .env"
echo ""
echo "Current values:"
echo "  OLLAMA_ENDPOINT=${OLLAMA_ENDPOINT:-not set}"
echo "  STREAMLIT_URL=${STREAMLIT_URL:-not set}"

