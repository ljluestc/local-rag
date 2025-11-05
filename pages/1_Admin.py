import os

import streamlit as st

from components.page_config import set_page_config
from components.page_state import set_initial_state
from components.header import set_page_header
from components.sidebar import sidebar


# Initialize state and page
set_initial_state()
set_page_config()
set_page_header()


# Show current index status
persist_dir = st.session_state.get("persist_dir")
with st.container(border=True):
    st.subheader("Admin: Document Setup", anchor=False)
    if persist_dir and os.path.isdir(persist_dir) and len(os.listdir(persist_dir)) > 0:
        st.caption(f"✔️ Persisted index detected in: {persist_dir}")
    else:
        st.caption("ℹ️ No persisted index found yet. Ingest documents using the sidebar.")


# Admin sidebar with data sources, settings, about
sidebar(show_sources=True)


