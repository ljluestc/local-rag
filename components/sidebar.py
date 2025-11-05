import streamlit as st

from components.tabs.about import about
from components.tabs.sources import sources
from components.tabs.settings import settings


def sidebar(show_sources: bool = True):
    with st.sidebar:
        if show_sources:
            tab1, tab2, tab3 = st.sidebar.tabs(["Data Sources", "Settings", "About"])

            with tab1:
                sources()

            with tab2:
                settings()

            with tab3:
                about()
        else:
            tab1, tab2 = st.sidebar.tabs(["Settings", "About"])

            with tab1:
                settings()

            with tab2:
                about()
