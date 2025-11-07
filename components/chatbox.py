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
                if query_engine:
                    # Use context chat with document index
                    with st.spinner("Processing..."):
                        response_stream = context_chat(
                            prompt=prompt, query_engine=query_engine
                        )
                        # st.write_stream returns the full response as string
                        response_text = st.write_stream(response_stream)
                elif selected_model:
                    # Use basic chat without context
                    with st.spinner("Processing..."):
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
