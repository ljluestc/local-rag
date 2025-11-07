# Multi-Provider & Multi-Chat Support

## Overview

Local RAG now supports multiple LLM providers and concurrent chat sessions.

## Features

### 1. Multiple LLM Providers

The application now supports the following providers:

- **Ollama** (default) - Local open-source models
- **OpenAI** - GPT-3.5, GPT-4, GPT-4 Turbo, GPT-4o
- **Claude** (Anthropic) - Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
- **Gemini** (Google) - Gemini Pro, Gemini Pro Vision, Gemini 1.5 Pro
- **Grok** (xAI) - Grok Beta, Grok 2
- **MCP** (Model Context Protocol) - Custom MCP endpoints

### 2. Multiple Concurrent Chat Sessions

- Create unlimited chat sessions
- Switch between sessions seamlessly
- Each session maintains its own message history
- Session management UI in the chat interface

### 3. Provider Configuration

Configure providers in **Settings → LLM Provider**:

1. Select your provider from the dropdown
2. Enter API keys (if required)
3. Select the model variant
4. Start chatting!

### 4. MCP Support

MCP (Model Context Protocol) allows you to connect to custom LLM endpoints:

1. Set the MCP endpoint URL (e.g., `http://localhost:8000/v1/chat/completions`)
2. Configure the model name
3. Use it like any other provider

## Usage

### Switching Providers

1. Go to **Settings** in the sidebar
2. Under **LLM Provider**, select your desired provider
3. Enter API keys if needed
4. Select the model
5. Return to **Admin** to start chatting

### Creating New Chat Sessions

1. In the chat interface, click the **➕ New Chat** button
2. A new session will be created
3. Use the session selector dropdown to switch between sessions

### API Keys

API keys can be set via:
- Environment variables (recommended for production)
- Settings UI (for development/testing)

Environment variables:
- `OPENAI_API_KEY` - OpenAI
- `ANTHROPIC_API_KEY` - Claude
- `GOOGLE_API_KEY` - Gemini
- `GROK_API_KEY` - Grok
- `MCP_ENDPOINT` - MCP endpoint URL

## Testing

Comprehensive Playwright tests are available in `tests/test_ui.py`:

```bash
# Install test dependencies
pipenv install --dev

# Run tests
pytest tests/test_ui.py -v
```

Test coverage includes:
- All UI components
- Provider switching
- Chat functionality
- Session management
- Settings configuration
- Responsive design
- Error handling

## Architecture

### Provider System

Providers are implemented as classes inheriting from `LLMProvider`:

- `utils/providers.py` - Provider implementations
- `utils/chat_sessions.py` - Session management
- `components/chatbox.py` - UI integration
- `components/tabs/settings.py` - Configuration UI

### Session Management

Sessions are stored in Streamlit's session state:
- Each session has a unique ID
- Messages are stored per session
- Sessions persist for the duration of the Streamlit session

## Notes

- Document-based RAG (with indexed documents) currently works best with Ollama
- Other providers work for general chat without document context
- MCP endpoints should follow OpenAI-compatible API format
- API keys are stored in session state (not persisted across restarts)

