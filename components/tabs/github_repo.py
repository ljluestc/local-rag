import streamlit as st

import utils.helpers as func
import utils.rag_pipeline as rag
import utils.logs as logs


def github_repo():
    # st.header("Import files from a GitHub repo")
    # st.caption("Convert a GitHub repo to embeddings for utilization during chat")
    
    # Allow GitHub repo input even without model configured (for auto-ingest)
    # Show warning if model not configured, but don't block input
    if st.session_state.get("selected_model") is None:
        st.warning(
            "⚠️ Ollama model not configured. Repo can be cloned and indexed, but chat requires a model. "
            "Configure Settings → Ollama → Model to enable chat.",
            icon="⚠️"
        )
    
    st.text_input(
        "Select a GitHub.com repo",
        placeholder="jonfairbanks/local-rag",
        key="github_repo",
    )

    repo_processed = st.button(
        "Process",
        on_click=func.clone_github_repo,
        args=(st.session_state.get("github_repo"),),
        key="process_github",
    )

    if repo_processed is True:
        # Check if model is configured before processing
        if st.session_state.get("selected_model") is None:
            st.error(
                "❌ Cannot process repo without an Ollama model configured. "
                "Please go to Settings → Ollama → Model and select a model, then try again."
            )
        else:
            with st.spinner("Processing..."):
                # Only proceed if cloning succeeded
                if st.session_state.get("github_clone_success") is True:
                    # Initiate the RAG pipeline, providing documents to be saved on disk if necessary
                    error = rag.rag_pipeline()

                    if error is not None:
                        st.exception(error)
                    else:
                        st.write("Your files are ready. Let's chat! 😎")
                else:
                    err_msg = st.session_state.get("github_clone_error") or "Failed to clone repository."
                    st.error(err_msg)
