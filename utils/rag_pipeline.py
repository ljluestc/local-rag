import os
import sys
import shutil
import inspect
import time

import streamlit as st

import utils.helpers as func
import utils.ollama as ollama
import utils.llama_index as llama_index
import utils.logs as logs


def rag_pipeline(uploaded_files: list = None):
    """
    RAG pipeline for Llama-based chatbots.

    Parameters:
        - uploaded_files (list, optional): List of files to be processed.
            If none are provided, the function will load files from the current working directory.

    Yields:
        - str: Successive chunks of conversation from the Ollama model with context.

    Raises:
        - Exception: If there is an error retrieving answers from the Ollama model or creating the service context.

    Notes:
        This function initiates a chat with context using the Llama-Index library and the Ollama language model. It takes one optional parameter, `uploaded_files`, which should be a list of files to be processed. If no files are provided, the function will load files from the current working directory. The function returns an iterable yielding successive chunks of conversation from the Ollama model with context. If there is an error retrieving answers from the Ollama model or creating the service context, the function raises an exception.

    Context:
        - logs.log: A logger for logging events related to this function.

    Side Effects:
        - Creates a service context using the provided Ollama model and embedding file.
        - Loads documents from the current working directory or the provided list of files.
        - Removes the loaded documents and any temporary files created during processing.
    """
    error = None
    progress = st.progress(0)

    #################################
    # (OPTIONAL) Save Files to Disk #
    #################################

    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                save_dir = os.getcwd() + "/data"
                func.save_uploaded_file(uploaded_file, save_dir)

        st.caption("✔️ Files Uploaded")
        progress.progress(10)

    #############################################
    # Pre-ingest checks and user confirmation   #
    #############################################

    # If ingesting from local data directory, estimate workload and confirm if very large
    save_dir = os.path.join(os.getcwd(), "data")
    try:
        total_bytes = 0
        total_files = 0
        largest_file = (None, 0)
        if os.path.isdir(save_dir):
            for root, _, files in os.walk(save_dir):
                for fname in files:
                    total_files += 1
                    fpath = os.path.join(root, fname)
                    try:
                        size = os.path.getsize(fpath)
                        total_bytes += size
                        if size > largest_file[1]:
                            largest_file = (fpath, size)
                    except Exception:
                        pass

        # Heuristics for "large" ingest
        bytes_gb = total_bytes / (1024 ** 3) if total_bytes else 0
        is_large = total_files > 5000 or total_bytes > (1 * 1024 ** 3)

        if is_large and not st.session_state.get("confirm_large_ingest"):
            with st.expander("Ingest looks large; confirm to proceed", expanded=True):
                st.warning(
                    f"This ingest looks large and may take a long time. Files: {total_files:,}, Size: {bytes_gb:.2f} GB"
                )
                if largest_file[0]:
                    st.caption(
                        f"Largest file: {os.path.relpath(largest_file[0], save_dir)} ({largest_file[1] / (1024 ** 2):.1f} MB)"
                    )
                col1, col2 = st.columns(2)
                with col1:
                    proceed = st.button("Proceed anyway", key="confirm_large_ingest_btn")
                with col2:
                    cancel = st.button("Cancel")
            if proceed:
                st.session_state["confirm_large_ingest"] = True
                st.rerun()
            if cancel:
                st.info("Ingest cancelled.")
                return "Ingest cancelled by user"
            # Stop this run until user clicks one of the buttons
            st.stop()
    except Exception:
        # Non-blocking if stats fail
        pass

    ######################################
    # Create Llama-Index service-context  #
    # to use local LLMs and embeddings    #
    ######################################

    try:
        t0 = time.time()
        llm = ollama.create_ollama_llm(
            st.session_state["selected_model"],
            st.session_state["ollama_endpoint"],
            st.session_state["system_prompt"],
            request_timeout=st.session_state.get("ollama_timeout", 120),
        )
        st.session_state["llm"] = llm
        st.caption("✔️ LLM Initialized")
        progress.progress(20)
        logs.log.info(f"LLM setup took {time.time() - t0:.2f}s")

        # resp = llm.complete("Hello!")
        # print(resp)
    except Exception as err:
        logs.log.error(f"Failed to setup LLM: {str(err)}")
        error = err
        st.exception(error)
        st.stop()

    ####################################
    # Determine embedding model to use #
    ####################################

    embedding_model = st.session_state["embedding_model"]
    hf_embedding_model = None

    if embedding_model == None:
        hf_embedding_model = "BAAI/bge-large-en-v1.5"

    if embedding_model == "Default (bge-large-en-v1.5)":
        hf_embedding_model = "BAAI/bge-large-en-v1.5"

    if embedding_model == "Large (Salesforce/SFR-Embedding-Mistral)":
        hf_embedding_model = "Salesforce/SFR-Embedding-Mistral"

    if embedding_model == "Other":
        hf_embedding_model = st.session_state["other_embedding_model"]

    try:
        t0 = time.time()
        llama_index.setup_embedding_model(
            hf_embedding_model,
        )
        st.caption("✔️ Embedding Model Created")
        progress.progress(30)
        logs.log.info(f"Embedding setup took {time.time() - t0:.2f}s")
    except Exception as err:
        logs.log.error(f"Setting up Embedding Model failed: {str(err)}")
        error = err
        st.exception(error)
        st.stop()

    #######################################
    # Load files from the data/ directory #
    #######################################

    # if documents already exists in state
    if (
        st.session_state["documents"] is not None
        and len(st.session_state["documents"]) > 0
    ):
        logs.log.info("Documents are already available; skipping document loading")
        st.caption("✔️ Processed File Data")
    else:
        try:
            t0 = time.time()
            save_dir = os.getcwd() + "/data"
            documents = llama_index.load_documents(save_dir)
            st.session_state["documents"] = documents
            load_s = time.time() - t0
            if len(documents) > 20000 or load_s > 30:
                st.warning(
                    f"Processed {len(documents):,} documents in {load_s:.1f}s. Indexing may take a while; keep this tab open."
                )
            st.caption("✔️ Data Processed")
            progress.progress(60)
        except Exception as err:
            logs.log.error(f"Document Load Error: {str(err)}")
            error = err
            st.exception(error)
            st.stop()

    ###########################################
    # Create and persist index, then query eng #
    ###########################################

    try:
        t0 = time.time()
        index = llama_index.create_index(
            st.session_state["documents"],
        )
        index_s = time.time() - t0
        if index_s > 60:
            st.warning(
                f"Indexing completed in {index_s/60:.1f} minutes. For very large corpora, consider reducing chunk size or scope."
            )
        st.caption("✔️ Created File Index")
        progress.progress(85)

        # Persist index to disk so chat page can load it without admin
        persist_dir = st.session_state.get("persist_dir") or os.path.join(os.getcwd(), "storage")
        llama_index.persist_index(index, persist_dir)
        st.caption("✔️ Saved Index to Disk")
        progress.progress(95)

        # Create query engine for immediate use
        llama_index.create_query_engine_from_index(index)
        st.caption("✔️ Query Engine Ready")
        progress.progress(100)
    except Exception as err:
        logs.log.error(f"Index Creation/Persist Error: {str(err)}")
        error = err
        st.exception(error)
        st.stop()

    #####################
    # Remove data files #
    #####################

    if len(st.session_state["file_list"]) > 0:
        try:
            save_dir = os.getcwd() + "/data"
            shutil.rmtree(save_dir)
            st.caption("✔️ Removed Temp Files")
        except Exception as err:
            logs.log.warning(
                f"Unable to delete data files, you may want to clean-up manually: {str(err)}"
            )
            pass

    return error  # If no errors occurred, None is returned
