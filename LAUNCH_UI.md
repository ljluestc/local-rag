# 🚀 How to Launch the UI

## Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Navigate to the project directory
cd /home/calelin/dev/local-rag-dev

# 2. Build the Docker image (if not already built)
docker build -t local-rag-dev:latest .

# 3. Stop any existing container (if running)
docker rm -f local-rag-8502

# 4. Launch the UI
docker run -d \
  --name local-rag-8502 \
  --add-host host.docker.internal:host-gateway \
  -p 8502:8501 \
  -v $(pwd)/storage:/home/appuser/storage \
  -v $(pwd)/data:/home/appuser/data \
  local-rag-dev:latest

# 5. Wait for UI to be ready (about 10-15 seconds)
sleep 15

# 6. Verify UI is running
curl http://localhost:8502/_stcore/health

# 7. Open in browser
# http://localhost:8502
```

### Option 2: One-Line Launch Script

```bash
cd /home/calelin/dev/local-rag-dev && \
docker rm -f local-rag-8502 2>/dev/null; \
docker run -d \
  --name local-rag-8502 \
  --add-host host.docker.internal:host-gateway \
  -p 8502:8501 \
  -v $(pwd)/storage:/home/appuser/storage \
  -v $(pwd)/data:/home/appuser/data \
  local-rag-dev:latest && \
sleep 15 && \
echo "✅ UI is ready at: http://localhost:8502"
```

## Detailed Steps

### Prerequisites

1. **Docker** installed and running
2. **Ollama** (optional, for local LLM support)
   - Install from: https://ollama.ai
   - Run: `ollama serve` (if using local models)

### Step-by-Step Launch

#### 1. Check Current Status

```bash
# Check if UI is already running
docker ps --filter "name=local-rag"

# Check if port 8502 is in use
lsof -i :8502 || echo "Port 8502 is available"
```

#### 2. Stop Existing Container (if any)

```bash
docker rm -f local-rag-8502
```

#### 3. Build Docker Image

```bash
cd /home/calelin/dev/local-rag-dev
docker build -t local-rag-dev:latest .
```

**Note:** This step is only needed if:
- You've made code changes
- The image doesn't exist yet
- Dependencies have changed

#### 4. Launch the Container

```bash
docker run -d \
  --name local-rag-8502 \
  --add-host host.docker.internal:host-gateway \
  -p 8502:8501 \
  -v $(pwd)/storage:/home/appuser/storage \
  -v $(pwd)/data:/home/appuser/data \
  local-rag-dev:latest
```

**Explanation of flags:**
- `-d`: Run in detached mode (background)
- `--name local-rag-8502`: Container name
- `--add-host host.docker.internal:host-gateway`: Allows container to access host's Ollama
- `-p 8502:8501`: Map host port 8502 to container port 8501
- `-v $(pwd)/storage:/home/appuser/storage`: Persist index storage
- `-v $(pwd)/data:/home/appuser/data`: Access data directory

#### 5. Verify UI is Running

```bash
# Wait a few seconds for Streamlit to start
sleep 15

# Check health endpoint
curl http://localhost:8502/_stcore/health

# Check container logs
docker logs local-rag-8502

# Check container status
docker ps --filter "name=local-rag-8502"
```

#### 6. Access the UI

Open your browser and navigate to:
```
http://localhost:8502
```

## Troubleshooting

### Port Already in Use

If port 8502 is already in use:

```bash
# Option 1: Use a different port
docker run -d --name local-rag-8503 -p 8503:8501 ... local-rag-dev:latest

# Option 2: Stop the existing container
docker rm -f local-rag-8502
```

### Container Won't Start

```bash
# Check logs for errors
docker logs local-rag-8502

# Check if image exists
docker images | grep local-rag-dev

# Rebuild if needed
docker build -t local-rag-dev:latest .
```

### UI Not Loading

```bash
# Check if container is running
docker ps --filter "name=local-rag"

# Check container logs
docker logs local-rag-8502 --tail 50

# Restart container
docker restart local-rag-8502

# Check health
curl -v http://localhost:8502/_stcore/health
```

### Ollama Connection Issues

If using Ollama locally:

```bash
# Ensure Ollama is running on host
ollama serve

# Test connection from host
curl http://localhost:11434/api/tags

# The container uses host.docker.internal:11434 to connect
```

## Useful Commands

### View Logs

```bash
# Follow logs in real-time
docker logs -f local-rag-8502

# View last 50 lines
docker logs --tail 50 local-rag-8502
```

### Stop UI

```bash
docker stop local-rag-8502
```

### Remove Container

```bash
docker rm -f local-rag-8502
```

### Restart UI

```bash
docker restart local-rag-8502
```

### Access Container Shell

```bash
docker exec -it local-rag-8502 /bin/bash
```

## Configuration

### Environment Variables

You can set environment variables when launching:

```bash
docker run -d \
  --name local-rag-8502 \
  -e OPENAI_API_KEY="your-key-here" \
  -e ANTHROPIC_API_KEY="your-key-here" \
  -p 8502:8501 \
  local-rag-dev:latest
```

### Volume Mounts

- `storage/`: Persists the vector index and embeddings
- `data/`: Directory for document ingestion

## Next Steps After Launch

1. **Configure LLM Provider**
   - Go to Settings → LLM Provider
   - Select: Ollama, OpenAI, Claude, Gemini, Grok, or MCP
   - Enter API keys if needed

2. **Ingest Documents**
   - Go to Sources tab
   - Upload files, import GitHub repo, or add website

3. **Start Chatting**
   - Go to Admin tab
   - Type your questions
   - Get context-aware responses with citations

## Support

- **Documentation**: See `docs/` directory
- **Issues**: Check `docs/troubleshooting.md`
- **Tests**: Run `./run_tests_docker.sh` to verify everything works

