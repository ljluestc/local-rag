# Testing Guide

## Quick Start

The UI is currently running at **http://localhost:8502**

### Run Tests (Recommended: Docker)

```bash
# Build test image
docker build -f Dockerfile.test -t local-rag-test .

# Run tests against running UI
docker run --rm --network host \
  -e STREAMLIT_URL=http://localhost:8502 \
  -v $(pwd):/app \
  -w /app \
  local-rag-test \
  pytest tests/test_ui.py -v
```

### Or use the test runner script:

```bash
# Make executable
chmod +x run_tests_docker.sh

# Run tests
./run_tests_docker.sh
```

## Test Setup Summary

✅ **Test Infrastructure Created:**
- `tests/test_ui.py` - Comprehensive Playwright test suite
- `tests/conftest.py` - Pytest configuration and fixtures
- `pytest.ini` - Pytest configuration
- `run_tests.sh` - Local test runner
- `run_tests_docker.sh` - Docker test runner
- `Dockerfile.test` - Test container image
- `docker-compose.test.yml` - Docker Compose test setup
- `README_TESTS.md` - Detailed test documentation

✅ **Test Coverage:**
- Main page loading
- Sidebar navigation
- Chat functionality
- Multi-chat session management
- Provider selection (Ollama, OpenAI, Claude, Gemini, Grok, MCP)
- Settings configuration
- Sources/import functionality
- Admin page
- Responsive design
- Error handling

✅ **UI Status:**
- Running at http://localhost:8502
- All features implemented
- Multi-provider support active
- Multi-chat sessions enabled

## Running Tests

### Option 1: Docker (Recommended)

```bash
./run_tests_docker.sh
```

This script will:
1. Check if UI container is running
2. Start UI if needed
3. Build test image
4. Run all tests

### Option 2: Local with Pipenv

```bash
# Install dependencies
pipenv install --dev

# Install Playwright browsers
pipenv run playwright install chromium

# Run tests
pipenv run pytest tests/test_ui.py -v
```

### Option 3: Local with System Python

```bash
# Install dependencies (if pipenv not available)
pip install --user playwright pytest pytest-playwright
python -m playwright install chromium

# Run tests
pytest tests/test_ui.py -v
```

## Test Configuration

- **Test URL**: Set via `STREAMLIT_URL` environment variable (default: `http://localhost:8501`)
- **Test Path**: `tests/test_ui.py`
- **Test Pattern**: `test_*.py` files in `tests/` directory

## Troubleshooting

### Playwright not found

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Or use Docker
./run_tests_docker.sh
```

### Streamlit not running

```bash
# Start UI
docker run -d --name local-rag-8502 \
  --add-host host.docker.internal:host-gateway \
  -p 8502:8501 \
  -v $(pwd)/storage:/home/appuser/storage \
  -v $(pwd)/data:/home/appuser/data \
  local-rag-dev:latest
```

### Tests timing out

Increase timeout in `pytest.ini` or use `--timeout` flag:
```bash
pytest tests/test_ui.py -v --timeout=60
```

## Next Steps

1. **Run tests** using one of the methods above
2. **Review test results** to ensure all features work
3. **Add more tests** as needed for new features
4. **Integrate into CI/CD** using the Docker setup

## Test Files

- `tests/test_ui.py` - Main test suite (335+ lines)
- `tests/conftest.py` - Pytest fixtures and configuration
- `pytest.ini` - Pytest settings
- `run_tests.sh` - Local test runner
- `run_tests_docker.sh` - Docker test runner
- `Dockerfile.test` - Test container image
- `docker-compose.test.yml` - Docker Compose test setup

