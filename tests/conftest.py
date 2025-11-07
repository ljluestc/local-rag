"""
Pytest configuration and fixtures for Local RAG tests.
"""
import pytest
import os
import sys
from typing import Generator

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get base URL from environment or default"""
    return os.getenv("STREAMLIT_URL", "http://localhost:8501")


@pytest.fixture(scope="session")
def playwright_browser():
    """Setup Playwright browser (session-scoped)"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            yield browser
            browser.close()
    except ImportError:
        pytest.skip("Playwright not installed. Run: pip install playwright && playwright install chromium")


@pytest.fixture(scope="function")
def page(playwright_browser):
    """Create a new page for each test"""
    if playwright_browser is None:
        pytest.skip("Playwright browser not available")
    
    page = playwright_browser.new_page()
    yield page
    page.close()


@pytest.fixture(autouse=True)
def check_streamlit_running(base_url):
    """Check if Streamlit is running before tests"""
    import socket
    from urllib.parse import urlparse
    
    parsed = urlparse(base_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 8501
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            pytest.skip(f"Streamlit not running at {base_url}. Start the UI first.")
    except Exception:
        pytest.skip(f"Could not connect to {base_url}. Start the UI first.")

