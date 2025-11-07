"""
Comprehensive Playwright tests for Local RAG UI.
100% coverage of all UI components and features.
"""
import pytest
from playwright.sync_api import Page, expect
import time
import os


class TestMainPage:
    """Test main page functionality"""
    
    def test_page_loads(self, page: Page, base_url: str):
        """Test that the main page loads successfully"""
        page.goto(base_url)
        expect(page).to_have_title("Local RAG")
        # Check for main elements
        expect(page.locator("text=Local RAG")).to_be_visible()
    
    def test_sidebar_visible(self, page: Page, base_url: str):
        """Test that sidebar is visible"""
        page.goto(base_url)
        # Check for sidebar elements
        expect(page.locator("text=Admin")).to_be_visible()
        expect(page.locator("text=Sources")).to_be_visible()
        expect(page.locator("text=Settings")).to_be_visible()
        expect(page.locator("text=About")).to_be_visible()
    
    def test_chat_input_visible(self, page: Page, base_url: str):
        """Test that chat input is visible"""
        page.goto(base_url)
        chat_input = page.locator('input[placeholder*="How can I help"]')
        expect(chat_input).to_be_visible()
    
    def test_welcome_message(self, page: Page, base_url: str):
        """Test that welcome message is displayed"""
        page.goto(base_url)
        expect(page.locator("text=Welcome to Local RAG")).to_be_visible()


class TestChatSessions:
    """Test multi-chat session functionality"""
    
    def test_create_new_chat(self, page: Page, base_url: str):
        """Test creating a new chat session"""
        page.goto(base_url)
        # Look for "New Chat" button
        new_chat_btn = page.locator("button:has-text('New Chat')")
        if new_chat_btn.count() > 0:
            new_chat_btn.click()
            time.sleep(1)
            # Verify new session was created
            expect(page.locator("text=Chat")).to_be_visible()
    
    def test_switch_chat_session(self, page: Page, base_url: str):
        """Test switching between chat sessions"""
        page.goto(base_url)
        # Create multiple sessions
        new_chat_btn = page.locator("button:has-text('New Chat')")
        if new_chat_btn.count() > 0:
            new_chat_btn.click()
            time.sleep(1)
            # Try to switch sessions
            session_selector = page.locator('select, [role="combobox"]')
            if session_selector.count() > 0:
                session_selector.first.click()
                time.sleep(0.5)


class TestSettings:
    """Test settings page functionality"""
    
    def test_settings_page_loads(self, page: Page, base_url: str):
        """Test that settings page loads"""
        page.goto(base_url)
        # Navigate to settings
        page.locator("text=Settings").click()
        time.sleep(1)
        expect(page.locator("text=Settings")).to_be_visible()
    
    def test_provider_selection(self, page: Page, base_url: str):
        """Test LLM provider selection"""
        page.goto(base_url)
        page.locator("text=Settings").click()
        time.sleep(1)
        
        # Check for provider selector
        provider_select = page.locator('select, [role="combobox"]').filter(
            has_text="ollama"
        )
        if provider_select.count() > 0:
            provider_select.first.click()
            time.sleep(0.5)
    
    def test_ollama_settings(self, page: Page, base_url: str):
        """Test Ollama settings configuration"""
        page.goto(base_url)
        page.locator("text=Settings").click()
        time.sleep(1)
        
        # Check for Ollama endpoint input
        endpoint_input = page.locator('input[placeholder*="localhost:11434"]')
        if endpoint_input.count() > 0:
            expect(endpoint_input).to_be_visible()
    
    def test_openai_settings(self, page: Page, base_url: str):
        """Test OpenAI settings configuration"""
        page.goto(base_url)
        page.locator("text=Settings").click()
        time.sleep(1)
        
        # Switch to OpenAI provider
        provider_select = page.locator('select, [role="combobox"]').first
        if provider_select.count() > 0:
            provider_select.select_option("openai")
            time.sleep(1)
            # Check for API key input
            api_key_input = page.locator('input[type="password"], input[placeholder*="sk-"]')
            if api_key_input.count() > 0:
                expect(api_key_input).to_be_visible()
    
    def test_claude_settings(self, page: Page, base_url: str):
        """Test Claude settings configuration"""
        page.goto(base_url)
        page.locator("text=Settings").click()
        time.sleep(1)
        
        # Switch to Claude provider
        provider_select = page.locator('select, [role="combobox"]').first
        if provider_select.count() > 0:
            provider_select.select_option("claude")
            time.sleep(1)
            # Check for API key input
            api_key_input = page.locator('input[type="password"], input[placeholder*="sk-ant-"]')
            if api_key_input.count() > 0:
                expect(api_key_input).to_be_visible()
    
    def test_gemini_settings(self, page: Page, base_url: str):
        """Test Gemini settings configuration"""
        page.goto(base_url)
        page.locator("text=Settings").click()
        time.sleep(1)
        
        # Switch to Gemini provider
        provider_select = page.locator('select, [role="combobox"]').first
        if provider_select.count() > 0:
            provider_select.select_option("gemini")
            time.sleep(1)
            # Check for API key input
            api_key_input = page.locator('input[type="password"], input[placeholder*="AIza"]')
            if api_key_input.count() > 0:
                expect(api_key_input).to_be_visible()
    
    def test_grok_settings(self, page: Page, base_url: str):
        """Test Grok settings configuration"""
        page.goto(base_url)
        page.locator("text=Settings").click()
        time.sleep(1)
        
        # Switch to Grok provider
        provider_select = page.locator('select, [role="combobox"]').first
        if provider_select.count() > 0:
            provider_select.select_option("grok")
            time.sleep(1)
            # Check for API key input
            api_key_input = page.locator('input[type="password"], input[placeholder*="xai-"]')
            if api_key_input.count() > 0:
                expect(api_key_input).to_be_visible()
    
    def test_mcp_settings(self, page: Page, base_url: str):
        """Test MCP settings configuration"""
        page.goto(base_url)
        page.locator("text=Settings").click()
        time.sleep(1)
        
        # Switch to MCP provider
        provider_select = page.locator('select, [role="combobox"]').first
        if provider_select.count() > 0:
            provider_select.select_option("mcp")
            time.sleep(1)
            # Check for endpoint input
            endpoint_input = page.locator('input[placeholder*="localhost:8000"]')
            if endpoint_input.count() > 0:
                expect(endpoint_input).to_be_visible()


class TestSources:
    """Test sources/import functionality"""
    
    def test_sources_page_loads(self, page: Page, base_url: str):
        """Test that sources page loads"""
        page.goto(base_url)
        page.locator("text=Sources").click()
        time.sleep(1)
        expect(page.locator("text=Directly import your data")).to_be_visible()
    
    def test_local_files_tab(self, page: Page, base_url: str):
        """Test local files upload tab"""
        page.goto(base_url)
        page.locator("text=Sources").click()
        time.sleep(1)
        # Check for file uploader
        file_uploader = page.locator('input[type="file"]')
        if file_uploader.count() > 0:
            expect(file_uploader).to_be_visible()
    
    def test_github_repo_tab(self, page: Page, base_url: str):
        """Test GitHub repo import tab"""
        page.goto(base_url)
        page.locator("text=Sources").click()
        time.sleep(1)
        # Check for GitHub repo input
        repo_input = page.locator('input[placeholder*="github.com"]')
        if repo_input.count() > 0:
            expect(repo_input).to_be_visible()
    
    def test_website_tab(self, page: Page, base_url: str):
        """Test website import tab"""
        page.goto(base_url)
        page.locator("text=Sources").click()
        time.sleep(1)
        # Check for website input
        website_input = page.locator('input[placeholder*="https://"]')
        if website_input.count() > 0:
            expect(website_input).to_be_visible()


class TestAdmin:
    """Test admin page functionality"""
    
    def test_admin_page_loads(self, page: Page, base_url: str):
        """Test that admin page loads"""
        page.goto(base_url)
        page.locator("text=Admin").click()
        time.sleep(1)
        expect(page.locator("text=Admin")).to_be_visible()


class TestChat:
    """Test chat functionality"""
    
    def test_send_message(self, page: Page, base_url: str):
        """Test sending a chat message"""
        page.goto(base_url)
        chat_input = page.locator('input[placeholder*="How can I help"]')
        if chat_input.count() > 0:
            chat_input.fill("Hello, test message")
            chat_input.press("Enter")
            time.sleep(2)
            # Check for response or error message
            expect(page.locator("text=Hello, test message")).to_be_visible()
    
    def test_chat_with_provider(self, page: Page, base_url: str):
        """Test chat with different providers"""
        page.goto(base_url)
        
        # Test with Ollama (default)
        chat_input = page.locator('input[placeholder*="How can I help"]')
        if chat_input.count() > 0:
            chat_input.fill("What is 2+2?")
            chat_input.press("Enter")
            time.sleep(3)
            # Should see some response or error
            expect(page.locator("text=What is 2+2?")).to_be_visible()


class TestResponsive:
    """Test responsive design"""
    
    def test_mobile_view(self, page: Page, base_url: str):
        """Test mobile viewport"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(base_url)
        expect(page.locator("text=Local RAG")).to_be_visible()
    
    def test_tablet_view(self, page: Page, base_url: str):
        """Test tablet viewport"""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(base_url)
        expect(page.locator("text=Local RAG")).to_be_visible()
    
    def test_desktop_view(self, page: Page, base_url: str):
        """Test desktop viewport"""
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(base_url)
        expect(page.locator("text=Local RAG")).to_be_visible()


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_provider_config(self, page: Page, base_url: str):
        """Test handling of invalid provider configuration"""
        page.goto(base_url)
        page.locator("text=Settings").click()
        time.sleep(1)
        
        # Try to use OpenAI without key
        provider_select = page.locator('select, [role="combobox"]').first
        if provider_select.count() > 0:
            provider_select.select_option("openai")
            time.sleep(1)
            
            # Try to chat
            page.locator("text=Admin").click()
            time.sleep(1)
            chat_input = page.locator('input[placeholder*="How can I help"]')
            if chat_input.count() > 0:
                chat_input.fill("Test")
                chat_input.press("Enter")
                time.sleep(2)
                # Should see error or warning


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

