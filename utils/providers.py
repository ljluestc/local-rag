"""
Multi-provider LLM support for Local RAG.
Supports: Ollama, OpenAI, Anthropic (Claude), Google (Gemini), Grok (xAI), and MCP.
"""
import os
import streamlit as st
from typing import Generator, Optional, Dict, Any
import utils.logs as logs

# Provider imports
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    def stream_chat(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream chat response"""
        raise NotImplementedError
    
    def get_model_name(self) -> str:
        """Get the current model name"""
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    """Ollama provider"""
    
    def __init__(self):
        super().__init__("Ollama")
        from utils.ollama import create_ollama_llm
        self.create_llm = create_ollama_llm
    
    def stream_chat(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        try:
            # Check if model is configured
            selected_model = st.session_state.get("selected_model")
            if not selected_model or selected_model == "None":
                yield "[Error] No Ollama model configured. Please go to Settings → Ollama → Model and select a model."
                return
            
            # Create LLM instance - use environment variable or session state
            ollama_endpoint = os.getenv("OLLAMA_ENDPOINT") or st.session_state.get("ollama_endpoint", "http://localhost:11434")
            llm = self.create_llm(
                selected_model,
                ollama_endpoint,
            )
            
            # Check if LLM creation failed
            if llm is None:
                ollama_endpoint = os.getenv("OLLAMA_ENDPOINT") or st.session_state.get("ollama_endpoint", "http://localhost:11434")
                yield f"[Connection Error] Failed to connect to Ollama at {ollama_endpoint}. Please check:\n1. Ollama is installed and running (https://ollama.com/download)\n2. The endpoint is correct in Settings → Ollama → Endpoint\n3. If running in Docker, ensure Ollama is accessible from the container\n4. Try: `curl {ollama_endpoint}/api/tags` to test the connection"
                return
            
            # Stream response
            stream = llm.stream_complete(prompt)
            for chunk in stream:
                yield chunk.delta
        except AttributeError as err:
            if "'NoneType' object has no attribute" in str(err):
                logs.log.error(f"Ollama chat error: Model not configured - {err}")
                yield "[Error] No Ollama model configured. Please go to Settings → Ollama → Model and select a model."
            else:
                logs.log.error(f"Ollama chat error: {err}")
                yield f"[Error] {str(err)}"
        except Exception as err:
            msg = str(err)
            logs.log.error(f"Ollama chat error: {msg}")
            
            # Provide more helpful error messages
            if "timed out" in msg.lower() or "timeout" in msg.lower():
                yield "[Timeout] The model took too long to respond. Try increasing the Ollama timeout in Settings or reduce your prompt size."
            elif "connection" in msg.lower() or "refused" in msg.lower() or "unreachable" in msg.lower() or "failed to connect" in msg.lower():
                ollama_endpoint = os.getenv("OLLAMA_ENDPOINT") or st.session_state.get("ollama_endpoint", "http://localhost:11434")
                yield f"[Connection Error] Failed to connect to Ollama at {ollama_endpoint}. Please check:\n1. Ollama is installed and running (https://ollama.com/download)\n2. The endpoint is correct in Settings → Ollama → Endpoint\n3. If running in Docker, ensure Ollama is accessible from the container"
            elif "model" in msg.lower() and ("not found" in msg.lower() or "does not exist" in msg.lower()):
                yield f"[Model Error] Model '{selected_model}' not found. Please:\n1. Install the model: `ollama pull {selected_model}`\n2. Or select a different model in Settings → Ollama → Model"
            else:
                yield f"[Error] {msg}"
    
    def get_model_name(self) -> str:
        return st.session_state.get("selected_model", "Unknown")


class OpenAIProvider(LLMProvider):
    """OpenAI provider"""
    
    def __init__(self):
        super().__init__("OpenAI")
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=st.session_state.get("openai_api_key"))
        except ImportError:
            self.client = None
    
    def stream_chat(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        if not self.client:
            yield "[Error] OpenAI client not available. Install openai package."
            return
        
        try:
            model = kwargs.get("model", "gpt-3.5-turbo")
            messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
            
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as err:
            logs.log.error(f"OpenAI chat error: {err}")
            yield f"[Error] {str(err)}"
    
    def get_model_name(self) -> str:
        return st.session_state.get("openai_model", "gpt-3.5-turbo")


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self):
        super().__init__("Claude")
        api_key = st.session_state.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
        if ANTHROPIC_AVAILABLE and api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None
    
    def stream_chat(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        if not self.client:
            yield "[Error] Claude not available. Set ANTHROPIC_API_KEY or install anthropic package."
            return
        
        try:
            model = kwargs.get("model", "claude-3-5-sonnet-20241022")
            messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
            
            with self.client.messages.stream(
                model=model,
                max_tokens=4096,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as err:
            logs.log.error(f"Claude chat error: {err}")
            yield f"[Error] {str(err)}"
    
    def get_model_name(self) -> str:
        return st.session_state.get("claude_model", "claude-3-5-sonnet-20241022")


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self):
        super().__init__("Gemini")
        api_key = st.session_state.get("gemini_api_key") or os.getenv("GOOGLE_API_KEY")
        if GEMINI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(st.session_state.get("gemini_model", "gemini-pro"))
        else:
            self.model = None
    
    def stream_chat(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        if not self.model:
            yield "[Error] Gemini not available. Set GOOGLE_API_KEY or install google-generativeai package."
            return
        
        try:
            response = self.model.generate_content(
                prompt,
                stream=True
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as err:
            logs.log.error(f"Gemini chat error: {err}")
            yield f"[Error] {str(err)}"
    
    def get_model_name(self) -> str:
        return st.session_state.get("gemini_model", "gemini-pro")


class GrokProvider(LLMProvider):
    """Grok (xAI) provider"""
    
    def __init__(self):
        super().__init__("Grok")
        api_key = st.session_state.get("grok_api_key") or os.getenv("GROK_API_KEY")
        if REQUESTS_AVAILABLE and api_key:
            self.api_key = api_key
            self.base_url = "https://api.x.ai/v1"
        else:
            self.api_key = None
    
    def stream_chat(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        if not self.api_key:
            yield "[Error] Grok not available. Set GROK_API_KEY."
            return
        
        try:
            model = kwargs.get("model", "grok-beta")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            }
            
            import requests
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        import json
                        try:
                            chunk_data = json.loads(line_str[6:])
                            if 'choices' in chunk_data and chunk_data['choices']:
                                delta = chunk_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        except Exception as err:
            logs.log.error(f"Grok chat error: {err}")
            yield f"[Error] {str(err)}"
    
    def get_model_name(self) -> str:
        return st.session_state.get("grok_model", "grok-beta")


class MCPProvider(LLMProvider):
    """MCP (Model Context Protocol) provider"""
    
    def __init__(self):
        super().__init__("MCP")
        self.mcp_endpoint = st.session_state.get("mcp_endpoint") or os.getenv("MCP_ENDPOINT")
    
    def stream_chat(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        if not self.mcp_endpoint:
            yield "[Error] MCP endpoint not configured. Set MCP_ENDPOINT."
            return
        
        try:
            import requests
            headers = {"Content-Type": "application/json"}
            data = {
                "method": "chat/completions",
                "params": {
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True
                }
            }
            
            response = requests.post(
                self.mcp_endpoint,
                headers=headers,
                json=data,
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        import json
                        try:
                            chunk_data = json.loads(line_str[6:])
                            if 'choices' in chunk_data and chunk_data['choices']:
                                delta = chunk_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        except Exception as err:
            logs.log.error(f"MCP chat error: {err}")
            yield f"[Error] {str(err)}"
    
    def get_model_name(self) -> str:
        return st.session_state.get("mcp_model", "mcp-model")


def get_provider(provider_name: str) -> Optional[LLMProvider]:
    """Get a provider instance by name"""
    providers = {
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
        "grok": GrokProvider,
        "mcp": MCPProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if provider_class:
        try:
            return provider_class()
        except Exception as e:
            logs.log.error(f"Failed to initialize {provider_name}: {e}")
            return None
    return None

