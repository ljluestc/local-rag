#!/bin/bash
# Quick setup script for environment variables

set -e

echo "🔧 Environment Variables Quick Setup"
echo "===================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping .env creation"
        exit 0
    fi
fi

# Create .env file (without inline comments to avoid export issues)
cat > .env << 'ENVEOF'
OLLAMA_ENDPOINT=http://localhost:11434
STREAMLIT_URL=http://localhost:8501
# Optional API Keys - uncomment and set values:
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# GOOGLE_API_KEY=
# GROK_API_KEY=
# MCP_ENDPOINT=
ENVEOF

echo "✅ Created .env file"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env file to add your API keys (optional)"
echo "   2. Load variables: set -a; source .env; set +a"
echo "   3. Launch UI: ./launch_ui.sh"
echo ""
echo "   Or use: export \$(grep -v '^#' .env | xargs)"
echo ""
echo "💡 Or add to ~/.bashrc:"
echo "   echo 'export OLLAMA_ENDPOINT=http://localhost:11434' >> ~/.bashrc"
echo "   echo 'export STREAMLIT_URL=http://localhost:8501' >> ~/.bashrc"
echo "   source ~/.bashrc"
