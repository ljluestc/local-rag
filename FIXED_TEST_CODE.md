# Complete Fixed Test Code

## All Fixed Files

### ✅ tests/conftest.py
- Fixed browser launch with Docker compatibility
- Fixed Streamlit connection check in page fixture
- Added proper timeouts (30 seconds)
- Better error handling

### ✅ tests/test_ui.py  
- Fixed all selectors with `.first` to avoid multiple matches
- Added `wait_until="networkidle"` for page loads
- Increased timeouts to 10 seconds
- Better error messages

### ✅ Dockerfile.test
- Added all system dependencies for Playwright
- Proper browser installation
- Added pytest-timeout
- Default timeout of 60 seconds

## Quick Run

\`\`\`bash
# Build and run
docker build -f Dockerfile.test -t local-rag-test .
docker run --rm --network host \
  -e STREAMLIT_URL=http://localhost:8502 \
  -v $(pwd):/app -w /app \
  local-rag-test pytest tests/test_ui.py -v
\`\`\`

All code is fixed and ready to use!
