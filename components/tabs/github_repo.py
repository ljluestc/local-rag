import streamlit as st

import utils.helpers as func
import utils.rag_pipeline as rag
import utils.logs as logs


def github_repo():
    # st.header("Import files from a GitHub repo")
    # st.caption("Convert a GitHub repo to embeddings for utilization during chat")
    if st.session_state["selected_model"] is not None:
        st.text_input(
            "Select a GitHub.com repo",
            placeholder="jonfairbanks/local-rag",
            key="github_repo",
        )

        repo_processed = st.button(
            "Process",
            on_click=func.clone_github_repo,
            args=(st.session_state["github_repo"],),
            key="process_github",
        )

        if repo_processed is True:
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

    else:
        st.text_input(
            "Select a GitHub.com repo",
            placeholder="jonfairbanks/local-rag",
            disabled=True,
        )
        st.button(
            "Process Repo",
            disabled=True,
        )
