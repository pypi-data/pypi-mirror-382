"""Model related utilities."""

from __future__ import annotations

from langchain_ollama import OllamaEmbeddings


# Map LLM control options to their type.
LLM_OPTIONS = {
    'mirostat': int,
    'mirostat_eta': float,
    'mirostat_tau': float,
    'num_ctx': int,
    'num_predict': int,
    'repeat_last_n': int,
    'repeat_penalty': float,
    'temperature': float,
    'seed': int,
    'stop': str,
    'tfs_z': float,
    'top_k': int,
    'top_p': float,
}


# ------------------------------------------------------------------------------
def get_embedding_dimensions(model: str) -> int:
    """Get the embedding dimensions of a model."""

    return len(OllamaEmbeddings(model=model).embed_documents(['Hello world'])[0])
