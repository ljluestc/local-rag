import streamlit as st
import os
import struct

import utils.logs as logs

from utils.ollama import get_models


def set_initial_state():

    ###########
    # General #
    ###########

    if "sidebar_state" not in st.session_state:
        st.session_state["sidebar_state"] = "expanded"

    if "ollama_endpoint" not in st.session_state:
        # Get from environment variable first, then auto-detect Docker environment
        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
        if not ollama_endpoint:
            # Check if using host network (no separate network namespace)
            # In host network mode, localhost works directly
            try:
                # Check if we can access host's localhost directly
                # If we're in host network mode, localhost should work
                import socket
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(0.1)
                result = test_sock.connect_ex(('localhost', 11434))
                test_sock.close()
                if result == 0:
                    # Port is accessible, likely host network mode
                    ollama_endpoint = "http://localhost:11434"
                else:
                    # Not accessible, check if we're in Docker
                    if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
                        # Try host.docker.internal first (works with --add-host flag)
                        ollama_endpoint = "http://host.docker.internal:11434"
                        # Alternative: Try to detect gateway IP
                        try:
                            # Get default gateway (usually 172.17.0.1)
                            gateway_ip = None
                            with open('/proc/net/route') as f:
                                for line in f:
                                    fields = line.strip().split()
                                    if fields[1] == '00000000':  # Default route
                                        gateway_ip = socket.inet_ntoa(struct.pack('<L', int(fields[2], 16)))
                                        break
                            if gateway_ip:
                                # Store as alternative endpoint
                                st.session_state["ollama_endpoint_alt"] = f"http://{gateway_ip}:11434"
                        except Exception:
                            pass
                    else:
                        ollama_endpoint = "http://localhost:11434"
            except Exception:
                # Fallback: assume localhost if not in Docker, otherwise host.docker.internal
                if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
                    ollama_endpoint = "http://host.docker.internal:11434"
                else:
                    ollama_endpoint = "http://localhost:11434"
        st.session_state["ollama_endpoint"] = ollama_endpoint

    if "ollama_timeout" not in st.session_state:
        st.session_state["ollama_timeout"] = 120

    if "embedding_model" not in st.session_state:
        st.session_state["embedding_model"] = "Default (bge-large-en-v1.5)"

    if "ollama_models" not in st.session_state:
        try:
            models = get_models()
            st.session_state["ollama_models"] = models if models else []
            if models and len(models) > 0:
                logs.log.info(f"Successfully connected to Ollama and found {len(models)} model(s)")
        except Exception as e:
            logs.log.warning(f"Failed to fetch Ollama models on init: {e}")
            st.session_state["ollama_models"] = []

    if "selected_model" not in st.session_state:
        try:
            models = st.session_state.get("ollama_models", [])
            if models and len(models) > 0:
                # Prefer llama3:8b, then llama2:7b, then first available
                if "llama3:8b" in models:
                    st.session_state["selected_model"] = "llama3:8b"
                    logs.log.info("Auto-selected default model: llama3:8b")
                elif "llama2:7b" in models:
                    st.session_state["selected_model"] = "llama2:7b"
                    logs.log.info("Auto-selected default model: llama2:7b")
                else:
                    st.session_state["selected_model"] = models[0]
                    logs.log.info(f"Auto-selected first available model: {models[0]}")
            else:
                # No models available - try to set a default manual model
                # Check if we can connect to Ollama and use a common default
                default_manual_model = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3:8b")
                st.session_state["selected_model"] = default_manual_model
                logs.log.info(f"No models fetched, using default manual model: {default_manual_model}")
        except Exception as e:
            logs.log.warning(f"Failed to set default model: {e}")
            # Set a default manual model as fallback
            default_manual_model = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3:8b")
            st.session_state["selected_model"] = default_manual_model
            logs.log.info(f"Using fallback default manual model: {default_manual_model}")
    else:
        # Re-check and auto-select if model is None but models are available
        current_model = st.session_state.get("selected_model")
        models = st.session_state.get("ollama_models", [])
        if (not current_model or current_model == "None" or current_model is None):
            if len(models) > 0:
                # Models are available, select one
                try:
                    if "llama3:8b" in models:
                        st.session_state["selected_model"] = "llama3:8b"
                        logs.log.info("Auto-selected default model: llama3:8b")
                    elif "llama2:7b" in models:
                        st.session_state["selected_model"] = "llama2:7b"
                        logs.log.info("Auto-selected default model: llama2:7b")
                    else:
                        st.session_state["selected_model"] = models[0]
                        logs.log.info(f"Auto-selected first available model: {models[0]}")
                except Exception as e:
                    logs.log.warning(f"Failed to auto-select model: {e}")
            else:
                # No models available, use default manual model
                default_manual_model = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3:8b")
                if not current_model or current_model == "None":
                    st.session_state["selected_model"] = default_manual_model
                    logs.log.info(f"No models available, using default manual model: {default_manual_model}")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Welcome to Local RAG! I'm ready to help you explore your documents. Here's how I work:\n\n1. **Document Ingestion**: Upload files or import from GitHub/websites to build a knowledge base.\n2. **Query Processing**: I'll search through your documents to find relevant information.\n3. **Contextual Responses**: I provide answers based on the content in your indexed documents.\n\nTo get started, you can:\n- Upload files using the 'Local Files' tab\n- Import a GitHub repository\n- Or ask me questions if you already have documents indexed\n\nTry asking: 'What documents do you have access to?' or 'Summarize the main topics in the indexed documents.'",
            },
            {
                "role": "user",
                "content": "What can you help me with?",
            },
            {
                "role": "assistant",
                "content": "I can help you with:\n\n📚 **Document Analysis**: Ask questions about your uploaded documents, get summaries, find specific information\n🔍 **Information Retrieval**: Search through your knowledge base to find relevant content\n💬 **Conversational Q&A**: Have natural conversations about your documents\n📊 **Content Summarization**: Get overviews and key points from your documents\n\nOnce you've indexed some documents, I'll be able to provide detailed answers based on that content. Would you like to upload some files to get started?",
            }
        ]

    ################################
    #  Files, Documents & Websites #
    ################################

    if "file_list" not in st.session_state:
        st.session_state["file_list"] = []

    if "github_repo" not in st.session_state:
        st.session_state["github_repo"] = None

    if "websites" not in st.session_state:
        st.session_state["websites"] = []

    ###############
    # Llama-Index #
    ###############

    if "llm" not in st.session_state:
        st.session_state["llm"] = None

    if "documents" not in st.session_state:
        st.session_state["documents"] = None

    if "query_engine" not in st.session_state:
        st.session_state["query_engine"] = None

    if "persist_dir" not in st.session_state:
        st.session_state["persist_dir"] = os.path.join(os.getcwd(), "storage")

    if "chat_mode" not in st.session_state:
        st.session_state["chat_mode"] = "compact"

    #####################
    # Advanced Settings #
    #####################

    if "advanced" not in st.session_state:
        st.session_state["advanced"] = False

    if "system_prompt" not in st.session_state:
        st.session_state["system_prompt"] = (
            "You are a sophisticated virtual assistant designed to assist users in comprehensively understanding and extracting insights from a wide range of documents at their disposal. Your expertise lies in tackling complex inquiries and providing insightful analyses based on the information contained within these documents."
        )

    if "top_k" not in st.session_state:
        st.session_state["top_k"] = 3

    if "embedding_model" not in st.session_state:
        st.session_state["embedding_model"] = None

    if "other_embedding_model" not in st.session_state:
        st.session_state["other_embedding_model"] = None

    if "chunk_size" not in st.session_state:
        st.session_state["chunk_size"] = 1024

    if "chunk_overlap" not in st.session_state:
        st.session_state["chunk_overlap"] = 200

    #####################
    # OpenAI API Key     #
    #####################

    if "openai_api_key" not in st.session_state:
        # Get OpenAI API key from environment variable only (no hardcoded defaults)
        api_key = os.getenv("OPENAI_API_KEY", "")
        st.session_state["openai_api_key"] = api_key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    #####################
    # Multi-Provider     #
    #####################

    if "llm_provider" not in st.session_state:
        st.session_state["llm_provider"] = "ollama"  # Default to Ollama

    if "anthropic_api_key" not in st.session_state:
        st.session_state["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY", "")

    if "gemini_api_key" not in st.session_state:
        st.session_state["gemini_api_key"] = os.getenv("GOOGLE_API_KEY", "")

    if "grok_api_key" not in st.session_state:
        st.session_state["grok_api_key"] = os.getenv("GROK_API_KEY", "")

    if "mcp_endpoint" not in st.session_state:
        st.session_state["mcp_endpoint"] = os.getenv("MCP_ENDPOINT", "")

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "claude_model" not in st.session_state:
        st.session_state["claude_model"] = "claude-3-5-sonnet-20241022"

    if "gemini_model" not in st.session_state:
        st.session_state["gemini_model"] = "gemini-pro"

    if "grok_model" not in st.session_state:
        st.session_state["grok_model"] = "grok-beta"

    if "mcp_model" not in st.session_state:
        st.session_state["mcp_model"] = "mcp-model"

    #####################
    # Chat Sessions     #
    #####################

    if "chat_sessions" not in st.session_state:
        st.session_state["chat_sessions"] = {}

    if "current_chat_id" not in st.session_state:
        st.session_state["current_chat_id"] = None
