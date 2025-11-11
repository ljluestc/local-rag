# Environment Variables & GitHub Secrets Setup Guide

## 📋 Overview

This guide shows you how to set up environment variables locally and configure GitHub secrets for CI/CD workflows.

## 🔧 Local Development Setup

### Option 1: Using .env file (Recommended)

1. **Create a `.env` file** in the project root:

```bash
cd /home/calelin/dev/local-rag-dev
cat > .env << 'EOF'
# Ollama Configuration
OLLAMA_ENDPOINT=http://localhost:11434

# Streamlit Configuration
STREAMLIT_URL=http://localhost:8501

# Optional API Keys
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
GROK_API_KEY=your-key-here
MCP_ENDPOINT=http://localhost:8000
EOF
```

2. **Load environment variables** before running:

```bash
# Option A: Use load_env.sh (Recommended - handles comments properly)
./load_env.sh

# Option B: Manual export (skip comments)
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Option C: Source method
set -a; source .env; set +a

# Option D: Manually export
export OLLAMA_ENDPOINT=http://localhost:11434
export STREAMLIT_URL=http://localhost:8501
```

3. **Launch the UI**:

```bash
./launch_ui.sh
```

### Option 2: Export directly in shell

```bash
# Set environment variables
export OLLAMA_ENDPOINT=http://localhost:11434
export STREAMLIT_URL=http://localhost:8501

# Optional API keys
export OPENAI_API_KEY=your-key-here
export ANTHROPIC_API_KEY=your-key-here
export GOOGLE_API_KEY=your-key-here
export GROK_API_KEY=your-key-here
export MCP_ENDPOINT=http://localhost:8000

# Launch UI
./launch_ui.sh
```

### Option 3: Add to ~/.bashrc or ~/.zshrc

```bash
# Add to your shell profile
echo 'export OLLAMA_ENDPOINT=http://localhost:11434' >> ~/.bashrc
echo 'export STREAMLIT_URL=http://localhost:8501' >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

## 🐳 Docker Setup

### Using environment variables with Docker

```bash
# Launch with environment variables
docker run -d \
  --name local-rag-8502 \
  --add-host host.docker.internal:host-gateway \
  -p 8502:8501 \
  -e OLLAMA_ENDPOINT=http://host.docker.internal:11434 \
  -e STREAMLIT_URL=http://localhost:8501 \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
  -v $(pwd)/storage:/home/appuser/storage \
  -v $(pwd)/data:/home/appuser/data \
  local-rag-dev:latest
```

### Using .env file with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  local-rag:
    build: .
    ports:
      - "8502:8501"
    environment:
      - OLLAMA_ENDPOINT=${OLLAMA_ENDPOINT:-http://host.docker.internal:11434}
      - STREAMLIT_URL=${STREAMLIT_URL:-http://localhost:8501}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./storage:/home/appuser/storage
      - ./data:/home/appuser/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Run with:

```bash
docker-compose up -d
```

## 🔐 GitHub Secrets Setup

### Step 1: Navigate to Repository Settings

1. Go to your GitHub repository
2. Click **Settings** (top navigation)
3. Click **Secrets and variables** → **Actions** (left sidebar)

### Step 2: Add Repository Secrets

Click **New repository secret** and add each secret:

#### Required Secrets (with defaults)

1. **OLLAMA_ENDPOINT**
   - Name: `OLLAMA_ENDPOINT`
   - Value: `http://host.docker.internal:11434`
   - Click **Add secret**

2. **STREAMLIT_URL**
   - Name: `STREAMLIT_URL`
   - Value: `http://localhost:8501`
   - Click **Add secret**

#### Optional API Keys

3. **OPENAI_API_KEY**
   - Name: `OPENAI_API_KEY`
   - Value: `sk-...` (your OpenAI API key)
   - Click **Add secret**

4. **ANTHROPIC_API_KEY**
   - Name: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-...` (your Anthropic API key)
   - Click **Add secret**

5. **GOOGLE_API_KEY**
   - Name: `GOOGLE_API_KEY`
   - Value: `AIza...` (your Google API key)
   - Click **Add secret**

6. **GROK_API_KEY**
   - Name: `GROK_API_KEY`
   - Value: `xai-...` (your Grok API key)
   - Click **Add secret**

7. **MCP_ENDPOINT**
   - Name: `MCP_ENDPOINT`
   - Value: `http://localhost:8000` (your MCP endpoint)
   - Click **Add secret**

### Step 3: Verify Secrets

After adding secrets, you should see them listed under **Repository secrets**:

```
OLLAMA_ENDPOINT        ●●●●●●●●●●●●●●●●●●●
STREAMLIT_URL          ●●●●●●●●●●●●●●●●●●●
OPENAI_API_KEY         ●●●●●●●●●●●●●●●●●●●
ANTHROPIC_API_KEY      ●●●●●●●●●●●●●●●●●●●
...
```

## ✅ Verification

### Verify Local Setup

```bash
# Check if environment variables are set
echo $OLLAMA_ENDPOINT
echo $STREAMLIT_URL

# Test UI launch
./launch_ui.sh

# Check if UI is using environment variables
curl http://localhost:8502/_stcore/health
```

### Verify GitHub Secrets

1. **Check workflow file** (`.github/workflows/main.yaml`):
   - Should reference `${{ secrets.OLLAMA_ENDPOINT }}`
   - Should reference `${{ secrets.STREAMLIT_URL }}`

2. **Run a test workflow**:
   - Push to repository
   - Go to **Actions** tab
   - Check workflow run
   - Verify it uses secrets correctly

### Verify in Code

The application checks environment variables in this order:

1. **Environment variable** (`OLLAMA_ENDPOINT`)
2. **Session state** (`st.session_state["ollama_endpoint"]`)
3. **Auto-detection** (Docker vs local)
4. **Default** (`http://localhost:11434`)

## 🔍 Troubleshooting

### Environment variables not working

```bash
# Check if variables are set
env | grep OLLAMA_ENDPOINT
env | grep STREAMLIT_URL

# Reload shell
source ~/.bashrc  # or ~/.zshrc

# Check in Python
python3 -c "import os; print(os.getenv('OLLAMA_ENDPOINT'))"
```

### GitHub secrets not working

1. **Check secret names** - must match exactly (case-sensitive)
2. **Check workflow syntax** - `${{ secrets.SECRET_NAME }}`
3. **Check workflow logs** - Actions tab → Workflow run → Job → Step

### Docker not using environment variables

```bash
# Check container environment
docker exec local-rag-8502 env | grep OLLAMA

# Restart with explicit environment variables
docker stop local-rag-8502
docker rm local-rag-8502
docker run -d -e OLLAMA_ENDPOINT=http://host.docker.internal:11434 ...
```

## 📝 Quick Reference

### Local Development

```bash
# Set variables
export OLLAMA_ENDPOINT=http://localhost:11434
export STREAMLIT_URL=http://localhost:8501

# Launch
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

Secrets are automatically used in workflows:
- `.github/workflows/main.yaml` - Uses secrets for build args
- `.github/workflows/test.yml` - Uses secrets for test environment

## 🎯 Next Steps

1. ✅ Set up local environment variables
2. ✅ Configure GitHub secrets
3. ✅ Test locally
4. ✅ Push to repository and verify workflows use secrets
5. ✅ Monitor workflow runs in Actions tab

