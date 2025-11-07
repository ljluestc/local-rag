"""
Multi-chat session management for Local RAG.
Supports multiple concurrent chat sessions.
"""
import streamlit as st
import uuid
from typing import Dict, List, Optional
from datetime import datetime


def init_chat_sessions():
    """Initialize chat sessions in session state"""
    if "chat_sessions" not in st.session_state:
        st.session_state["chat_sessions"] = {}
    
    if "current_chat_id" not in st.session_state:
        st.session_state["current_chat_id"] = None
    
    if "chat_session_counter" not in st.session_state:
        st.session_state["chat_session_counter"] = 0


def create_new_chat_session() -> str:
    """Create a new chat session and return its ID"""
    init_chat_sessions()
    
    chat_id = str(uuid.uuid4())
    st.session_state["chat_session_counter"] += 1
    
    st.session_state["chat_sessions"][chat_id] = {
        "id": chat_id,
        "name": f"Chat {st.session_state['chat_session_counter']}",
        "created_at": datetime.now().isoformat(),
        "messages": [
            {
                "role": "assistant",
                "content": "Welcome to Local RAG! I'm ready to help you explore your documents.",
            }
        ],
        "query_engine": None,  # Can be session-specific
    }
    
    st.session_state["current_chat_id"] = chat_id
    return chat_id


def get_current_chat_session() -> Optional[Dict]:
    """Get the current active chat session"""
    init_chat_sessions()
    
    current_id = st.session_state.get("current_chat_id")
    if current_id and current_id in st.session_state["chat_sessions"]:
        return st.session_state["chat_sessions"][current_id]
    
    # If no current session, create one
    if not current_id or current_id not in st.session_state["chat_sessions"]:
        create_new_chat_session()
        current_id = st.session_state["current_chat_id"]
    
    return st.session_state["chat_sessions"].get(current_id)


def switch_chat_session(chat_id: str):
    """Switch to a different chat session"""
    init_chat_sessions()
    
    if chat_id in st.session_state["chat_sessions"]:
        st.session_state["current_chat_id"] = chat_id
        return True
    return False


def delete_chat_session(chat_id: str):
    """Delete a chat session"""
    init_chat_sessions()
    
    if chat_id in st.session_state["chat_sessions"]:
        del st.session_state["chat_sessions"][chat_id]
        
        # If deleted session was current, switch to another or create new
        if st.session_state.get("current_chat_id") == chat_id:
            remaining = list(st.session_state["chat_sessions"].keys())
            if remaining:
                st.session_state["current_chat_id"] = remaining[0]
            else:
                create_new_chat_session()
        return True
    return False


def get_all_chat_sessions() -> List[Dict]:
    """Get all chat sessions"""
    init_chat_sessions()
    return list(st.session_state["chat_sessions"].values())


def rename_chat_session(chat_id: str, new_name: str):
    """Rename a chat session"""
    init_chat_sessions()
    
    if chat_id in st.session_state["chat_sessions"]:
        st.session_state["chat_sessions"][chat_id]["name"] = new_name
        return True
    return False

