import streamlit as st

from utils.ollama import chat, context_chat
from utils.chat_sessions import (
    init_chat_sessions,
    get_current_chat_session,
    create_new_chat_session,
    get_all_chat_sessions,
    switch_chat_session,
    delete_chat_session,
    rename_chat_session,
)
from utils.providers import get_provider


def chatbox():
    # Initialize chat sessions
    init_chat_sessions()
    
    # Chat session management UI
    col1, col2 = st.columns([3, 1])
    with col1:
        sessions = get_all_chat_sessions()
        if sessions:
            session_names = [s["name"] for s in sessions]
            current_session = get_current_chat_session()
            current_idx = 0
            if current_session:
                try:
                    current_idx = next(i for i, s in enumerate(sessions) if s["id"] == current_session["id"])
                except StopIteration:
                    current_idx = 0
            
            selected_idx = st.selectbox(
                "Chat Session",
                range(len(session_names)),
                format_func=lambda x: session_names[x],
                index=current_idx,
                key="session_selector"
            )
            if selected_idx != current_idx and sessions:
                switch_chat_session(sessions[selected_idx]["id"])
    
    with col2:
        if st.button("➕ New Chat", use_container_width=True):
            create_new_chat_session()
            st.rerun()
    
    # Get current session
    current_session = get_current_chat_session()
    if not current_session:
        create_new_chat_session()
        current_session = get_current_chat_session()
    
    # Use session-specific messages
    messages = current_session.get("messages", [])
    query_engine = st.session_state.get("query_engine")  # Global query engine
    
    # Get provider
    provider_name = st.session_state.get("llm_provider", "ollama")
    provider = get_provider(provider_name)
    
    # Show helpful message if no index or model
    if not query_engine:
        if not provider:
            st.info("💡 **Tip**: Configure a model provider in Settings to enable chat. Upload files in Admin to enable document-based Q&A.")
        else:
            st.info("💡 **Tip**: Upload files in Admin to enable document-based Q&A. You can still chat without documents.")
    
    # Display messages
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    prompt = st.chat_input("How can I help?")

    if prompt:
        # Add the user input to current session
        current_session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response - use context chat if index available, otherwise provider chat
        with st.chat_message("assistant"):
            try:
                response_text = ""
                source_nodes = []
                
                if query_engine and provider_name == "ollama":
                    # Use context chat with document index (Ollama only for now)
                    model_name = provider.get_model_name() if provider else "Unknown"
                    st.caption(f"🔵 **{provider_name.upper()}** | Model: {model_name} | 📚 Using indexed documents")
                    
                    with st.spinner("🔍 Searching documents..."):
                        response_stream = context_chat(
                            prompt=prompt, query_engine=query_engine
                        )
                        # Stream response and collect source nodes
                        full_response = []
                        response_container = st.empty()
                        
                        for chunk in response_stream:
                            if isinstance(chunk, tuple) and len(chunk) == 2 and chunk[0] == "__SOURCES__":
                                # This is the source nodes marker
                                source_nodes = chunk[1] if chunk[1] else []
                            else:
                                chunk_str = str(chunk)
                                full_response.append(chunk_str)
                                # Update display as we stream
                                response_container.markdown("".join(full_response))
                        
                        response_text = "".join(full_response)
                        
                        # Display source citations if available
                        if source_nodes:
                            with st.expander(f"📄 **Sources** ({len(source_nodes)} document(s) referenced)", expanded=True):
                                for i, node in enumerate(source_nodes[:5], 1):  # Show top 5 sources
                                    try:
                                        # Get metadata
                                        metadata = {}
                                        if hasattr(node, 'metadata'):
                                            metadata = node.metadata
                                        elif hasattr(node, 'node') and hasattr(node.node, 'metadata'):
                                            metadata = node.node.metadata
                                        
                                        # Extract file information
                                        file_path = metadata.get('file_path', metadata.get('file_name', 'Unknown'))
                                        page_label = metadata.get('page_label', metadata.get('page', ''))
                                        
                                        # Get score if available
                                        score = None
                                        if hasattr(node, 'score'):
                                            score = node.score
                                        
                                        # Format source info
                                        source_info = f"**{i}.** `{file_path}`"
                                        if page_label:
                                            source_info += f" (page {page_label})"
                                        if score is not None:
                                            source_info += f" | Relevance: {score:.2f}"
                                        st.caption(source_info)
                                        
                                        # Show snippet
                                        text_content = ""
                                        if hasattr(node, 'text'):
                                            text_content = node.text
                                        elif hasattr(node, 'node') and hasattr(node.node, 'text'):
                                            text_content = node.node.text
                                        elif hasattr(node, 'get_content'):
                                            text_content = node.get_content()
                                        
                                        if text_content:
                                            snippet = text_content[:300] + "..." if len(text_content) > 300 else text_content
                                            st.text(snippet)
                                    except Exception as e:
                                        st.caption(f"**{i}.** Source {i} (error displaying: {str(e)})")
                elif provider:
                    # Use provider chat without context
                    model_name = provider.get_model_name()
                    provider_icons = {
                        "ollama": "🔵",
                        "openai": "🟢",
                        "claude": "🟣",
                        "gemini": "🟠",
                        "grok": "🔴",
                        "mcp": "⚪",
                    }
                    icon = provider_icons.get(provider_name.lower(), "🤖")
                    st.caption(f"{icon} **{provider_name.upper()}** | Model: {model_name} | ⚠️ No documents indexed")
                    
                    with st.spinner("💬 Generating response..."):
                        # Build message history for context
                        messages_for_provider = [
                            {"role": msg["role"], "content": msg["content"]}
                            for msg in current_session["messages"][:-1]  # Exclude current prompt
                        ]
                        messages_for_provider.append({"role": "user", "content": prompt})
                        
                        response_stream = provider.stream_chat(
                            prompt=prompt,
                            messages=messages_for_provider
                        )
                        response_text = st.write_stream(response_stream)
                else:
                    # No provider configured
                    response_text = "⚠️ Please configure a model provider in Settings to enable chat."
                    st.warning(response_text)
            except Exception as e:
                error_msg = f"❌ Error during chat: {str(e)}"
                st.error(error_msg)
                response_text = error_msg
                import utils.logs as logs
                logs.log.error(f"Chat error: {e}")

        # Add the final response to current session
        if response_text:
            current_session["messages"].append({"role": "assistant", "content": response_text})
