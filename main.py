import time

import streamlit as st

from components.chatbox import chatbox
from components.header import set_page_header
from components.sidebar import sidebar

from components.page_config import set_page_config
from components.page_state import set_initial_state
import os
import utils.llama_index as llama_index


def generate_welcome_message(msg):
    for char in msg:
        time.sleep(0.025)  # TODO: Find a better way -- This is blocking :(
        yield char


### Setup Initial State
set_initial_state()

### Page Setup
set_page_config()
set_page_header()

# Optional: reset chat via query param
try:
    if "reset_chat" in st.query_params:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Welcome to Local RAG! To begin, please either import some files or ingest a GitHub repo. Once you've completed those steps, we can continue the conversation and explore how I can assist you further.",
            }
        ]
        st.success("Chat reset.")
except Exception:
    pass

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])
    # st.chat_message(msg["role"]).write_stream(generate_welcome_message(msg['content']))

### Ensure persisted index is loaded for chat-only page
if st.session_state.get("query_engine") is None:
    persist_dir = st.session_state.get("persist_dir")
    try:
        if persist_dir and os.path.isdir(persist_dir) and len(os.listdir(persist_dir)) > 0:
            # Ensure a local embedding model is set before loading index (avoid OpenAI default)
            embedding_model = st.session_state.get("embedding_model")
            hf_embedding_model = None
            if embedding_model is None or embedding_model == "Default (bge-large-en-v1.5)":
                hf_embedding_model = "BAAI/bge-large-en-v1.5"
            elif embedding_model == "Large (Salesforce/SFR-Embedding-Mistral)":
                hf_embedding_model = "Salesforce/SFR-Embedding-Mistral"
            else:
                hf_embedding_model = st.session_state.get("other_embedding_model") or "BAAI/bge-large-en-v1.5"

            try:
                llama_index.setup_embedding_model(hf_embedding_model)
            except Exception:
                pass
            index = llama_index.load_persisted_index(persist_dir)
            llama_index.create_query_engine_from_index(index)
        else:
            # Attempt a one-time automatic index build from the default data/ directory
            try:
                if not st.session_state.get("auto_ingest_attempted"):
                    data_dir = os.path.join(os.getcwd(), "data")
                    has_files = False
                    try:
                        for root, _, files in os.walk(data_dir):
                            if any(not f.startswith(".") for f in files):
                                has_files = True
                                break
                    except Exception:
                        has_files = False

                    if has_files:
                        # Ensure a local embedding model is set before building the index (avoid OpenAI defaults)
                        embedding_model = st.session_state.get("embedding_model")
                        if embedding_model is None or embedding_model == "Default (bge-large-en-v1.5)":
                            hf_embedding_model = "BAAI/bge-large-en-v1.5"
                        elif embedding_model == "Large (Salesforce/SFR-Embedding-Mistral)":
                            hf_embedding_model = "Salesforce/SFR-Embedding-Mistral"
                        else:
                            hf_embedding_model = st.session_state.get("other_embedding_model") or "BAAI/bge-large-en-v1.5"

                        try:
                            llama_index.setup_embedding_model(hf_embedding_model)
                        except Exception:
                            pass

                        # Build and persist a new index from data/
                        docs = llama_index.load_documents(data_dir)
                        index = llama_index.create_index(docs)
                        llama_index.persist_index(index, persist_dir)

                        # Create a query engine if possible; otherwise the Admin page can still be used to chat
                        try:
                            llama_index.create_query_engine_from_index(index)
                        except Exception:
                            pass

                        st.success("Built and persisted a new index from the data/ directory.")
                    else:
                        st.info("No persisted index found. Please open the Admin page to ingest documents.")

                    st.session_state["auto_ingest_attempted"] = True
                else:
                    st.info("No persisted index found. Please open the Admin page to ingest documents.")
            except Exception:
                st.info("No persisted index found. Please open the Admin page to ingest documents.")
    except Exception:
        st.info("No persisted index found. Please open the Admin page to ingest documents.")

### Sidebar (chat page hides data sources)
sidebar(show_sources=False)

### Chat Box
chatbox()
