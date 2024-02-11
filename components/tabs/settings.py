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

    st.subheader("Chat")
    chat_settings = st.container(border=True)
    with chat_settings:
        st.text_input(
            "Ollama Endpoint",
            key="ollama_endpoint",
            placeholder="http://localhost:11434",
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
        show_key = st.toggle("Show OpenAI Key", key="show_openai_key", value=False)
        input_type = "password" if not show_key else "default"
        st.text_input(
            "OpenAI API Key (optional)",
            key="openai_api_key",
            placeholder="sk-...",
            type=input_type,
            help="Only needed if a persisted index or component requires OpenAI. Not used for Ollama."
        )
        # Apply/remove env var based on current value
        if st.session_state.get("openai_api_key"):
            os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]
        else:
            os.environ.pop("OPENAI_API_KEY", None)
        if st.button("Clear OpenAI Key"):
            # Defer clearing until next rerun to avoid modifying after widget instantiation
            st.session_state["_clear_openai_key_requested"] = True
            st.rerun()
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
