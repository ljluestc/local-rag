# Fix Ollama Connection in Docker (Linux)

## Quick Fix Options

### Option 1: Use Gateway IP (Easiest)
1. Go to Settings → Ollama → Endpoint
2. Change endpoint to: `http://172.17.0.1:11434`
3. Click "Test Connection"

### Option 2: Use Host Network
Restart the container with host network:
```bash
docker rm -f local-rag-8502
docker run -d \
  --name local-rag-8502 \
  --network host \
  -v $(pwd)/storage:/home/appuser/storage \
  -v $(pwd)/data:/home/appuser/data \
  local-rag-dev:latest
```
Then set endpoint to: `http://localhost:11434`

### Option 3: Find Your Host IP
```bash
# Find gateway IP
ip route show default | awk '/default/ {print $3}'

# Or find your host IP
hostname -I | awk '{print $1}'
```
Use the IP in the endpoint: `http://<IP>:11434`

### Option 4: Test from Container
```bash
# Test different endpoints from inside container
docker exec -it local-rag-8502 curl http://172.17.0.1:11434/api/tags
docker exec -it local-rag-8502 curl http://host.docker.internal:11434/api/tags
```

## Verify Ollama is Running
```bash
# On host, check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

