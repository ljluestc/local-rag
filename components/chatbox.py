import streamlit as st

from utils.ollama import chat, context_chat


def chatbox():
    # Allow chat input - use context chat if index available, otherwise basic chat
    query_engine = st.session_state.get("query_engine")
    selected_model = st.session_state.get("selected_model")
    
    # Show helpful message if no index or model
    if not query_engine:
        if not selected_model:
            st.info("💡 **Tip**: Configure Ollama model in Settings to enable chat. Upload files in Admin to enable document-based Q&A.")
        else:
            st.info("💡 **Tip**: Upload files in Admin to enable document-based Q&A. You can still chat without documents.")
    
    prompt = st.chat_input("How can I help?")

    if prompt:
        # Add the user input to messages state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response - use context chat if index available, otherwise basic chat
        with st.chat_message("assistant"):
            try:
                response_text = ""
                source_nodes = []
                model_name = st.session_state.get("selected_model", "Unknown")
                using_openai = bool(st.session_state.get("openai_api_key"))
                
                if query_engine:
                    # Use context chat with document index
                    model_indicator = "🔵 **Ollama**" if not using_openai else "🟢 **OpenAI**"
                    st.caption(f"{model_indicator} | Model: {model_name} | 📚 Using indexed documents")
                    
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
                elif selected_model:
                    # Use basic chat without context
                    st.caption(f"🔵 **Ollama** | Model: {model_name} | ⚠️ No documents indexed")
                    with st.spinner("💬 Generating response..."):
                        response_stream = chat(prompt=prompt)
                        # st.write_stream returns the full response as string
                        response_text = st.write_stream(response_stream)
                else:
                    # No model configured
                    response_text = "⚠️ Please configure an Ollama model in Settings to enable chat. Go to Settings → Ollama → Model and select a model."
                    st.warning(response_text)
            except Exception as e:
                error_msg = f"❌ Error during chat: {str(e)}"
                st.error(error_msg)
                response_text = error_msg
                import utils.logs as logs
                logs.log.error(f"Chat error: {e}")

        # Add the final response to messages state
        if response_text:
            st.session_state["messages"].append({"role": "assistant", "content": response_text})
