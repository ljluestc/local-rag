# How to Start and Run Tests - COMPLETE FIXED CODE

## ✅ All Test Code Has Been Fixed

### Key Fixes Applied:
1. **tests/conftest.py** - Fixed browser launch with Docker compatibility (`--no-sandbox` flags)
2. **tests/test_ui.py** - Fixed all selectors with `.first` to avoid multiple element errors
3. **Dockerfile.test** - Added all system dependencies for Playwright
4. **Timeouts** - Increased to 10-30 seconds for stability
5. **Wait Conditions** - Added `networkidle` and `domcontentloaded` for proper page loading

## Quick Start (3 Steps)

### Step 1: Verify UI is Running

```bash
# Check if UI is running
curl http://localhost:8502/_stcore/health

# If not running, start it:
cd /home/calelin/dev/local-rag-dev
docker rm -f local-rag-8502 2>/dev/null || true
docker run -d --name local-rag-8502 \
  --no-healthcheck \
  --add-host host.docker.internal:host-gateway \
  -p 8502:8501 \
  -v $(pwd)/storage:/home/appuser/storage \
  -v $(pwd)/data:/home/appuser/data \
  local-rag-dev:latest

# Wait for UI to be ready
sleep 5
curl http://localhost:8502/_stcore/health
```

### Step 2: Choose Your Test Method

#### Method A: Docker Test Runner (Easiest - Recommended)

```bash
cd /home/calelin/dev/local-rag-dev

# Make script executable (if not already)
chmod +x run_tests_docker.sh

# Run all tests
./run_tests_docker.sh

# Run specific test
./run_tests_docker.sh -k test_page_loads

# Run with more verbose output
./run_tests_docker.sh -v -s
```

**What this does:**
- Builds test Docker image (first time only)
- Checks if UI is running
- Runs all tests in isolated container
- Shows test results

#### Method B: Manual Docker

```bash
cd /home/calelin/dev/local-rag-dev

# Build test image (first time only)
docker build -f Dockerfile.test -t local-rag-test .

# Run tests
docker run --rm --network host \
  -e STREAMLIT_URL=http://localhost:8502 \
  -v $(pwd):/app \
  -w /app \
  local-rag-test \
  pytest tests/test_ui.py -v
```

#### Method C: Local with Pipenv

```bash
cd /home/calelin/dev/local-rag-dev

# Install dependencies (first time only)
pipenv install --dev

# Install Playwright browsers (first time only)
pipenv run playwright install chromium

# Run tests
pipenv run pytest tests/test_ui.py -v

# Run specific test
pipenv run pytest tests/test_ui.py::TestMainPage::test_page_loads -v

# Run with output
pipenv run pytest tests/test_ui.py -v -s
```

#### Method D: Local Test Runner Script

```bash
cd /home/calelin/dev/local-rag-dev

# Make executable
chmod +x run_tests.sh

# Run tests
./run_tests.sh

# Run specific test
./run_tests.sh -k test_page_loads
```

### Step 3: View Results

Tests will show:
- ✓ Passed tests (green)
- ✗ Failed tests (red)
- Test execution time
- Summary at the end

## Example Output

```
============================= test session starts ==============================
tests/test_ui.py::TestMainPage::test_page_loads PASSED              [ 10%]
tests/test_ui.py::TestMainPage::test_sidebar_visible PASSED          [ 20%]
tests/test_ui.py::TestChatSessions::test_create_new_chat PASSED      [ 30%]
...
============================= 25 passed in 45.23s ==============================
```

## Troubleshooting

### UI Not Running

```bash
# Start UI
docker run -d --name local-rag-8502 \
  --add-host host.docker.internal:host-gateway \
  -p 8502:8501 \
  -v $(pwd)/storage:/home/appuser/storage \
  -v $(pwd)/data:/home/appuser/data \
  local-rag-dev:latest

# Wait and check
sleep 5
curl http://localhost:8502/_stcore/health
```

### Playwright Not Found (Local)

```bash
# Use Docker method instead, or:
pipenv install --dev
pipenv run playwright install chromium
```

### Tests Timing Out

```bash
# Increase timeout
pytest tests/test_ui.py -v --timeout=60
```

### Run Specific Test Class

```bash
# Run only main page tests
pytest tests/test_ui.py::TestMainPage -v

# Run only chat tests
pytest tests/test_ui.py::TestChat -v

# Run only settings tests
pytest tests/test_ui.py::TestSettings -v
```

## Test Categories

- `TestMainPage` - Main page functionality
- `TestChatSessions` - Multi-chat session management
- `TestSettings` - Settings and provider configuration
- `TestSources` - File/GitHub/Website import
- `TestAdmin` - Admin page
- `TestChat` - Chat functionality
- `TestResponsive` - Responsive design
- `TestErrorHandling` - Error handling

## Quick Commands Reference

```bash
# Start UI
docker run -d --name local-rag-8502 --add-host host.docker.internal:host-gateway -p 8502:8501 -v $(pwd)/storage:/home/appuser/storage -v $(pwd)/data:/home/appuser/data local-rag-dev:latest

# Check UI status
curl http://localhost:8502/_stcore/health

# Run tests (Docker - Recommended)
./run_tests_docker.sh

# Run tests (Local)
./run_tests.sh

# Run specific test
pytest tests/test_ui.py::TestMainPage::test_page_loads -v

# Run with coverage
pytest tests/test_ui.py -v --cov=. --cov-report=html
```

