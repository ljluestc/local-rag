import ollama
import os

import streamlit as st

import utils.logs as logs

# Do not set OPENAI_API_KEY here; we use Ollama + HF embeddings only.

from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine

###################################
#
# Create Client
#
###################################


def create_client(host: str):
    """
    Creates a client for interacting with the Ollama API.

    Parameters:
        - host (str): The hostname or IP address of the Ollama server.

    Returns:
        - An instance of the Ollama client.

    Raises:
        - Exception: If there is an error creating the client.

    Notes:
        This function creates a client for interacting with the Ollama API using the `ollama` library. It takes a single parameter, `host`, which should be the hostname or IP address of the Ollama server. The function returns an instance of the Ollama client, or raises an exception if there is an error creating the client.
    """
    try:
        client = ollama.Client(host=host)
        logs.log.info("Ollama chat client created successfully")
        return client
    except Exception as err:
        logs.log.error(f"Failed to create Ollama client: {err}")
        return False


###################################
#
# Get Models
#
###################################


def get_models():
    """
    Retrieves a list of available language models from the Ollama server.

    Returns:
        - models (list[str]): A list of available language model names.

    Raises:
        - Exception: If there is an error retrieving the list of models.

    Notes:
        This function retrieves a list of available language models from the Ollama server using the `ollama` library. It takes no parameters and returns a list of available language model names.

        The function raises an exception if there is an error retrieving the list of models.

    Side Effects:
        - st.session_state["ollama_models"] is set to the list of available language models.
    """
    try:
        chat_client = create_client(st.session_state["ollama_endpoint"])
        if chat_client is False:
            st.session_state["ollama_models"] = []
            return []

        data = chat_client.list()
        models: list[str] = []

        # Normalize various shapes returned by different client versions
        items = None
        if isinstance(data, dict) and "models" in data:
            items = data["models"]
        elif hasattr(data, "models"):
            items = getattr(data, "models")
        else:
            items = data

        if items is None:
            items = []

        for item in items:
            name = None
            if isinstance(item, dict):
                name = item.get("name") or item.get("model")
            else:
                name = getattr(item, "name", None) or getattr(item, "model", None)
                if name is None and isinstance(item, str):
                    name = item
            if name:
                models.append(name)

        st.session_state["ollama_models"] = models

        if len(models) > 0:
            logs.log.info("Ollama models loaded successfully")
            # Auto-select a model if none is currently selected
            current_model = st.session_state.get("selected_model")
            if not current_model or current_model == "None" or current_model is None:
                # Prefer llama3:8b, then llama2:7b, then first available
                if "llama3:8b" in models:
                    st.session_state["selected_model"] = "llama3:8b"
                    logs.log.info("Auto-selected default model: llama3:8b")
                elif "llama2:7b" in models:
                    st.session_state["selected_model"] = "llama2:7b"
                    logs.log.info("Auto-selected default model: llama2:7b")
                else:
                    st.session_state["selected_model"] = models[0]
                    logs.log.info(f"Auto-selected first available model: {models[0]}")
        else:
            logs.log.warn("Ollama returned no models; enable manual model input in Settings.")

        return models
    except Exception as err:
        logs.log.error(f"Failed to retrieve Ollama model list: {err}")
        st.session_state["ollama_models"] = []
        return []


###################################
#
# Create Ollama LLM instance
#
###################################


@st.cache_data(show_spinner=False)
def create_ollama_llm(model: str, base_url: str, system_prompt: str = None, request_timeout: int | None = None) -> Ollama:
    """
    Create an instance of the Ollama language model.

    Parameters:
        - model (str): The name of the model to use for language processing.
        - base_url (str): The base URL for making API requests.
        - request_timeout (int, optional): The timeout for API requests in seconds. Defaults to 60.

    Returns:
        - llm: An instance of the Ollama language model with the specified configuration.
    """
    try:
        if request_timeout is None:
            request_timeout = st.session_state.get("ollama_timeout", 120)
        
        # Test connection first
        try:
            test_client = create_client(base_url)
            if test_client is False:
                logs.log.error(f"Failed to connect to Ollama at {base_url}")
                return None
            
            # Try to list models to verify connection
            try:
                test_client.list()
            except Exception as list_err:
                logs.log.warning(f"Could not list models (connection may still work): {list_err}")
        except Exception as conn_err:
            logs.log.error(f"Connection test failed: {conn_err}")
            return None
        
        # Settings.llm = Ollama(model=model, base_url=base_url, system_prompt=system_prompt, request_timeout=request_timeout)
        Settings.llm = Ollama(model=model, base_url=base_url, request_timeout=request_timeout)
        logs.log.info(f"Ollama LLM instance created successfully with model {model} at {base_url}")
        return Settings.llm
    except Exception as e:
        error_msg = str(e)
        logs.log.error(f"Error creating Ollama language model: {error_msg}")
        # Check for common connection errors
        if "connection" in error_msg.lower() or "refused" in error_msg.lower() or "unreachable" in error_msg.lower():
            logs.log.error(f"Ollama connection error - check that Ollama is running at {base_url}")
        return None


###################################
#
# Chat (no context)
#
###################################


def chat(prompt: str):
    """
    Initiates a chat with the Ollama language model using the provided parameters.

    Parameters:
        - prompt (str): The starting prompt for the conversation.

    Yields:
        - str: Successive chunks of conversation from the Ollama model.
    """

    try:
        # Check if model is configured
        selected_model = st.session_state.get("selected_model")
        if not selected_model or selected_model == "None":
            yield "[Error] No Ollama model configured. Please go to Settings → Ollama → Model and select a model."
            return
        
        # Create LLM instance - use environment variable or session state
        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT") or st.session_state.get("ollama_endpoint", "http://localhost:11434")
        llm = create_ollama_llm(
            selected_model,
            ollama_endpoint,
        )
        
        # Check if LLM creation failed
        if llm is None:
            ollama_endpoint = os.getenv("OLLAMA_ENDPOINT") or st.session_state.get("ollama_endpoint", "http://localhost:11434")
            yield f"[Connection Error] Failed to connect to Ollama at {ollama_endpoint}. Please check:\n1. Ollama is installed and running (https://ollama.com/download)\n2. The endpoint is correct in Settings → Ollama → Endpoint\n3. If running in Docker, ensure Ollama is accessible from the container\n4. Try: `curl {ollama_endpoint}/api/tags` to test the connection"
            return
        
        # Stream response
        stream = llm.stream_complete(prompt)
        for chunk in stream:
            yield chunk.delta
    except Exception as err:
        msg = str(err)
        logs.log.error(f"Ollama chat stream error: {msg}")
        
        # Provide more helpful error messages
        if "timed out" in msg.lower() or "timeout" in msg.lower():
            yield "[Timeout] The model took too long to respond. Try increasing the Ollama timeout in Settings or reduce your prompt size."
        elif "connection" in msg.lower() or "refused" in msg.lower() or "unreachable" in msg.lower() or "failed to connect" in msg.lower():
            ollama_endpoint = os.getenv("OLLAMA_ENDPOINT") or st.session_state.get("ollama_endpoint", "http://localhost:11434")
            yield f"[Connection Error] Failed to connect to Ollama at {ollama_endpoint}. Please check:\n1. Ollama is installed and running (https://ollama.com/download)\n2. The endpoint is correct in Settings → Ollama → Endpoint\n3. If running in Docker, ensure Ollama is accessible from the container"
        elif "model" in msg.lower() and ("not found" in msg.lower() or "does not exist" in msg.lower()):
            yield f"[Model Error] Model '{selected_model}' not found. Please:\n1. Install the model: `ollama pull {selected_model}`\n2. Or select a different model in Settings → Ollama → Model"
        else:
            yield f"[Error] {msg}"
        return


###################################
#
# Document Chat (with context)
#
###################################


def context_chat(prompt: str, query_engine: RetrieverQueryEngine):
    """
    Initiates a chat with context using the Llama-Index query_engine.

    Parameters:
        - prompt (str): The starting prompt for the conversation.
        - query_engine (RetrieverQueryEngine): The Llama-Index query engine to use for retrieving answers.

    Yields:
        - tuple: (text_chunk, source_nodes) - Successive chunks of conversation and source nodes.

    Raises:
        - Exception: If there is an error retrieving answers from the Llama-Index model.

    Notes:
        This function initiates a chat with context using the Llama-Index language model and index.

        It takes two parameters, `prompt` and `query_engine`, which should be the starting prompt for the conversation and the Llama-Index query engine to use for retrieving answers, respectively.

        The function returns an iterable yielding successive chunks of conversation from the Llama-Index index with context.

        If there is an error retrieving answers from the Llama-Index instance, the function raises an exception.

    Side Effects:
        - The chat conversation is generated and returned as successive chunks of text.
    """

    try:
        response = query_engine.query(prompt)
        source_nodes = []
        
        # Extract source nodes if available (after query completes)
        if hasattr(response, 'source_nodes') and response.source_nodes:
            source_nodes = response.source_nodes
        elif hasattr(response, 'get_formatted_sources'):
            try:
                sources = response.get_formatted_sources()
                if sources:
                    source_nodes = sources
            except:
                pass
        
        # Stream the response text
        for text in response.response_gen:
            yield str(text)
        
        # Yield source nodes as a special marker after streaming completes
        yield ("__SOURCES__", source_nodes)
    except Exception as err:
        msg = str(err)
        logs.log.error(f"Ollama chat stream error: {msg}")
        if "timed out" in msg.lower():
            yield "[Timeout] The model took too long to respond. Try increasing the Ollama timeout in Settings or reduce your prompt size."
        else:
            yield f"[Error] {msg}"
        return
