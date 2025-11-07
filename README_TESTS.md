# Running Tests

## Prerequisites

- Python 3.10+
- Playwright browsers installed
- Streamlit UI running (for integration tests)

## Local Testing

### Option 1: Using the test runner script

```bash
# Make script executable (if not already)
chmod +x run_tests.sh

# Run tests
./run_tests.sh

# Run specific test
./run_tests.sh -k test_page_loads

# Run with verbose output
./run_tests.sh -v
```

### Option 2: Using pipenv

```bash
# Install dependencies
pipenv install --dev

# Install Playwright browsers
pipenv run playwright install chromium

# Run tests
pipenv run pytest tests/test_ui.py -v

# Run specific test
pipenv run pytest tests/test_ui.py::TestMainPage::test_page_loads -v
```

### Option 3: Using system Python

```bash
# Install dependencies
pip install playwright pytest pytest-playwright

# Install Playwright browsers
playwright install chromium

# Run tests
pytest tests/test_ui.py -v
```

## Docker Testing

### Option 1: Test against running UI container

```bash
# Start UI in background
docker run -d --name local-rag-ui -p 8501:8501 local-rag-dev:latest

# Run tests in Docker
docker run --rm --network host \
  -e STREAMLIT_URL=http://localhost:8501 \
  -v $(pwd):/app \
  -w /app \
  local-rag-dev:latest \
  pytest tests/test_ui.py -v

# Cleanup
docker rm -f local-rag-ui
```

### Option 2: Using docker-compose

```bash
# Start UI and run tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Cleanup
docker-compose -f docker-compose.test.yml down
```

## Test Configuration

Tests are configured via `pytest.ini`:

- Test paths: `tests/`
- Test file pattern: `test_*.py`
- Test class pattern: `Test*`
- Test function pattern: `test_*`

## Environment Variables

- `STREAMLIT_URL`: URL of the Streamlit UI (default: `http://localhost:8501`)

## Test Coverage

The test suite includes:

- ✅ Main page loading
- ✅ Sidebar navigation
- ✅ Chat input functionality
- ✅ Welcome message display
- ✅ Multi-chat session management
- ✅ Provider selection (Ollama, OpenAI, Claude, Gemini, Grok, MCP)
- ✅ Settings configuration
- ✅ Sources/import functionality
- ✅ Admin page
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Error handling

## Troubleshooting

### Playwright not found

```bash
pip install playwright
playwright install chromium
```

### Streamlit not running

Start the UI first:
```bash
# Local
streamlit run main.py

# Docker
docker run -d -p 8501:8501 local-rag-dev:latest
```

### Tests timing out

Increase timeout in `pytest.ini`:
```ini
[pytest]
timeout = 30
```

### Browser launch fails

Install browser dependencies:
```bash
# Linux
playwright install-deps chromium

# Docker
RUN playwright install-deps chromium
```

