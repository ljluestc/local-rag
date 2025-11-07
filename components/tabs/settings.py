import json
import os

import streamlit as st

import utils.ollama as ollama

from datetime import datetime


def settings():
    st.header("Settings")
    st.caption("Configure Local RAG settings and integrations")

    # Handle default and clear actions for OpenAI key BEFORE widgets render
    # 1) Initialize from environment on first run (default is set in page_state.py)
    if "openai_api_key" not in st.session_state:
        st.session_state["openai_api_key"] = os.getenv("OPENAI_API_KEY", "")
        if st.session_state["openai_api_key"]:
            os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]

    # 2) If a previous run requested clearing the key, do it now (pre-widget)
    if st.session_state.get("_clear_openai_key_requested"):
        st.session_state["_clear_openai_key_requested"] = False
        st.session_state["openai_api_key"] = ""
        os.environ.pop("OPENAI_API_KEY", None)

    st.subheader("LLM Provider")
    provider_settings = st.container(border=True)
    with provider_settings:
        provider = st.selectbox(
            "Select Provider",
            ["ollama", "openai", "claude", "gemini", "grok", "mcp"],
            key="llm_provider",
            help="Choose which LLM provider to use for chat"
        )
        
        if provider == "openai":
            show_key = st.toggle("Show OpenAI Key", key="show_openai_key", value=False)
            input_type = "password" if not show_key else "default"
            st.text_input(
                "OpenAI API Key",
                key="openai_api_key",
                placeholder="sk-...",
                type=input_type,
            )
            st.selectbox(
                "OpenAI Model",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"],
                key="openai_model",
            )
            if st.session_state.get("openai_api_key"):
                os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]
        
        elif provider == "claude":
            show_key = st.toggle("Show Claude Key", key="show_claude_key", value=False)
            input_type = "password" if not show_key else "default"
            st.text_input(
                "Anthropic API Key",
                key="anthropic_api_key",
                placeholder="sk-ant-...",
                type=input_type,
            )
            st.selectbox(
                "Claude Model",
                ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                key="claude_model",
            )
            if st.session_state.get("anthropic_api_key"):
                os.environ["ANTHROPIC_API_KEY"] = st.session_state["anthropic_api_key"]
        
        elif provider == "gemini":
            show_key = st.toggle("Show Gemini Key", key="show_gemini_key", value=False)
            input_type = "password" if not show_key else "default"
            st.text_input(
                "Google API Key",
                key="gemini_api_key",
                placeholder="AIza...",
                type=input_type,
            )
            st.selectbox(
                "Gemini Model",
                ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"],
                key="gemini_model",
            )
            if st.session_state.get("gemini_api_key"):
                os.environ["GOOGLE_API_KEY"] = st.session_state["gemini_api_key"]
        
        elif provider == "grok":
            show_key = st.toggle("Show Grok Key", key="show_grok_key", value=False)
            input_type = "password" if not show_key else "default"
            st.text_input(
                "Grok API Key",
                key="grok_api_key",
                placeholder="xai-...",
                type=input_type,
            )
            st.selectbox(
                "Grok Model",
                ["grok-beta", "grok-2"],
                key="grok_model",
            )
            if st.session_state.get("grok_api_key"):
                os.environ["GROK_API_KEY"] = st.session_state["grok_api_key"]
        
        elif provider == "mcp":
            st.text_input(
                "MCP Endpoint",
                key="mcp_endpoint",
                placeholder="http://localhost:8000/v1/chat/completions",
                help="MCP (Model Context Protocol) endpoint URL"
            )
            st.text_input(
                "MCP Model",
                key="mcp_model",
                placeholder="mcp-model",
            )
            if st.session_state.get("mcp_endpoint"):
                os.environ["MCP_ENDPOINT"] = st.session_state["mcp_endpoint"]

    st.subheader("Chat")
    chat_settings = st.container(border=True)
    with chat_settings:
        # Get default from environment or use current session state
        default_endpoint = os.getenv("OLLAMA_ENDPOINT") or st.session_state.get("ollama_endpoint", "http://localhost:11434")
        st.text_input(
            "Ollama Endpoint",
            key="ollama_endpoint",
            placeholder=default_endpoint,
            value=default_endpoint if "ollama_endpoint" not in st.session_state else st.session_state["ollama_endpoint"],
            on_change=ollama.get_models,
        )
        st.number_input(
            "Ollama Request Timeout (seconds)",
            min_value=10,
            max_value=600,
            step=10,
            key="ollama_timeout",
            help="Increase if responses time out during generation.",
        )
        st.selectbox(
            "Model",
            st.session_state["ollama_models"],
            key="selected_model",
            disabled= len(st.session_state["ollama_models"])==0,
            placeholder= "Select Model" if len(st.session_state["ollama_models"])>0 else "No Models Available",
        )
        if len(st.session_state["ollama_models"]) == 0:
            manual_model = st.text_input(
                "Model (manual)",
                key="manual_model",
                placeholder="llama3:8b",
                help="Enter a model name installed in Ollama, e.g. llama3:8b",
            )
            if manual_model and manual_model.strip() != "":
                st.session_state["selected_model"] = manual_model.strip()
        st.button(
            "Refresh",
            on_click=ollama.get_models,
        )
        reset_chat = st.button(
            "Reset Chat",
            help="Clear chat history and restart the conversation",
        )
        if reset_chat:
            if "messages" in st.session_state:
                del st.session_state["messages"]
            st.rerun()
        if st.session_state["advanced"] == True:
            st.select_slider(
                "Top K",
                options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                help="The number of most similar documents to retrieve in response to a query.",
                value=st.session_state["top_k"],
                key="top_k",
            )
            # st.text_area(
            #     "System Prompt",
            #     value=st.session_state["system_prompt"],
            #     key="system_prompt",
            # )
            st.selectbox(
                "Chat Mode",
                (
                    "compact",
                    "refine",
                    "tree_summarize",
                    "simple_summarize",
                    "accumulate",
                    "compact_accumulate",
                ),
                help="Sets the [Llama Index Query Engine chat mode](https://github.com/run-llama/llama_index/blob/main/docs/module_guides/deploying/query_engine/response_modes.md) used when creating the Query Engine. Default: `compact`.",
                key="chat_mode",
                disabled=True,
            )
            st.write("")

    st.subheader(
        "Embeddings",
        help="Embeddings are numerical representations of data, useful for tasks like document clustering and similarity detection when processing files, as they encode semantic meaning for efficient manipulation and retrieval.",
    )
    embedding_settings = st.container(border=True)
    with embedding_settings:
        embedding_model = st.selectbox(
            "Model",
            [
                "Default (bge-large-en-v1.5)",
                "Large (Salesforce/SFR-Embedding-Mistral)",
                "Other",
            ],
            key="embedding_model",
        )
        if embedding_model == "Other":
            st.text_input(
                "HuggingFace Model",
                key="other_embedding_model",
                placeholder="Salesforce/SFR-Embedding-Mistral",
            )
        if st.session_state["advanced"] == True:
            st.caption(
                "View the [MTEB Embeddings Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)"
            )
            st.text_input(
                "Chunk Size",
                help="Reducing `chunk_size` improves embedding precision by focusing on smaller text portions. This enhances information retrieval accuracy but escalates computational demands due to processing more chunks.",
                key="chunk_size",
                placeholder="1024",
                value=st.session_state["chunk_size"],
            )
            st.text_input(
                "Chunk Overlap",
                help="The amount of overlap between two consecutive chunks. A higher overlap value helps maintain continuity and context across chunks.",
                key="chunk_overlap",
                placeholder="200",
                value=st.session_state["chunk_overlap"],
            )

    st.subheader("Export Data")
    export_data_settings = st.container(border=True)
    with export_data_settings:
        st.write("Chat History")
        st.download_button(
            label="Download",
            data=json.dumps(st.session_state["messages"]),
            file_name=f"local-rag-chat-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json",
            mime="application/json",
        )

    st.toggle("Advanced Settings", key="advanced")

    if st.session_state["advanced"] == True:
        with st.expander("Current Application State"):
            state = dict(sorted(st.session_state.items()))
            st.write(state)
