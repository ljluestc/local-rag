# Environment Variables Configuration

## Overview

All hardcoded endpoints have been replaced with environment variables. The application now supports configuration via environment variables with sensible defaults.

## Environment Variables

### Required (with defaults)

- `OLLAMA_ENDPOINT`: Ollama API endpoint (default: `http://localhost:11434` or `http://host.docker.internal:11434` in Docker)
- `STREAMLIT_URL`: Streamlit UI URL (default: `http://localhost:8501`)

### Optional API Keys

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic/Claude API key
- `GOOGLE_API_KEY`: Google/Gemini API key
- `GROK_API_KEY`: Grok/xAI API key
- `MCP_ENDPOINT`: MCP endpoint URL

### Docker Configuration

- `DOCKER_CONTAINER`: Set to `true` when running in Docker (auto-detected)

## Priority Order

1. **Environment variable** (highest priority)
2. **Session state** (from UI settings)
3. **Auto-detection** (Docker vs local)
4. **Default value** (fallback)

## Usage

### Local Development

```bash
export OLLAMA_ENDPOINT=http://localhost:11434
export STREAMLIT_URL=http://localhost:8501
./launch_ui.sh
```

### Docker

```bash
docker run -d \
  -e OLLAMA_ENDPOINT=http://host.docker.internal:11434 \
  -e STREAMLIT_URL=http://localhost:8501 \
  local-rag-dev:latest
```

### GitHub Actions

Set secrets in: Settings → Secrets and variables → Actions

- `OLLAMA_ENDPOINT`
- `STREAMLIT_URL`
- `OPENAI_API_KEY` (optional)
- `ANTHROPIC_API_KEY` (optional)
- `GOOGLE_API_KEY` (optional)
- `GROK_API_KEY` (optional)
- `MCP_ENDPOINT` (optional)

## Files Updated

- `components/page_state.py`: Reads `OLLAMA_ENDPOINT` from environment
- `utils/ollama.py`: Uses `OLLAMA_ENDPOINT` environment variable
- `utils/providers.py`: Uses `OLLAMA_ENDPOINT` environment variable
- `components/tabs/settings.py`: Shows environment value as default
- `.github/workflows/test.yml`: Uses GitHub secrets
- `.github/workflows/main.yaml`: Uses GitHub secrets for build args

