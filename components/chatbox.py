import streamlit as st

from utils.ollama import chat, context_chat


def chatbox():
    # Disable input entirely until the query engine is ready
    engine_ready = bool(st.session_state.get("query_engine"))
    prompt = st.chat_input("How can I help?", disabled=not engine_ready)

    # If not ready, show a small hint and do nothing else
    if not engine_ready:
        st.caption("Configure Ollama in Settings and load an index in Admin to start chatting.")
        return

    if prompt:

        # Add the user input to messages state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate llama-index stream with user input
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response = st.write_stream(
                    # chat(
                    #     prompt=prompt
                    # )
                    context_chat(
                        prompt=prompt, query_engine=st.session_state["query_engine"]
                    )
                )

        # Add the final response to messages state
        st.session_state["messages"].append({"role": "assistant", "content": response})
