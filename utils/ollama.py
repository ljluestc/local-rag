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
        # Settings.llm = Ollama(model=model, base_url=base_url, system_prompt=system_prompt, request_timeout=request_timeout)
        Settings.llm = Ollama(model=model, base_url=base_url, request_timeout=request_timeout)
        logs.log.info("Ollama LLM instance created successfully")
        return Settings.llm
    except Exception as e:
        logs.log.error(f"Error creating Ollama language model: {e}")
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
        llm = create_ollama_llm(
            st.session_state["selected_model"],
            st.session_state["ollama_endpoint"],
        )
        stream = llm.stream_complete(prompt)
        for chunk in stream:
            yield chunk.delta
    except Exception as err:
        msg = str(err)
        logs.log.error(f"Ollama chat stream error: {msg}")
        if "timed out" in msg.lower():
            yield "[Timeout] The model took too long to respond. Try increasing the Ollama timeout in Settings or reduce your prompt size."
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
