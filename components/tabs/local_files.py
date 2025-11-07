import os
import shutil

import streamlit as st

import utils.helpers as func
import utils.ollama as ollama
import utils.llama_index as llama_index
import utils.logs as logs
import utils.rag_pipeline as rag

supported_files = (
    "csv",
    "docx",
    "epub",
    "ipynb",
    "json",
    "md",
    "pdf",
    "ppt",
    "pptx",
    "txt",
)


def local_files():
    # Allow file uploads even without model configured (for auto-ingest)
    # Show warning if model not configured, but don't block uploads
    if st.session_state.get("selected_model") is None:
        st.warning(
            "⚠️ Ollama model not configured. Files can be uploaded and indexed, but chat requires a model. "
            "Configure Settings → Ollama → Model to enable chat.",
            icon="⚠️"
        )
    
    uploaded_files = st.file_uploader(
        "Select Files",
        accept_multiple_files=True,
        type=supported_files,
    )

    if len(uploaded_files) > 0:
        st.session_state["file_list"] = uploaded_files

        # Check if model is configured before processing
        if st.session_state.get("selected_model") is None:
            st.error(
                "❌ Cannot process files without an Ollama model configured. "
                "Please go to Settings → Ollama → Model and select a model, then try again."
            )
        else:
            with st.spinner("Processing..."):
                # Initiate the RAG pipeline, providing documents to be saved on disk if necessary
                error = rag.rag_pipeline(uploaded_files)

                # Display errors (if any) or proceed
                if error is not None:
                    st.exception(error)
                else:
                    st.write("Your files are ready. Let's chat! 😎") # TODO: This should be a button.
