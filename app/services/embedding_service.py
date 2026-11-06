from functools import lru_cache
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

from app.configs.settings import get_settings
from app.utils import get_logger

logger = get_logger(__name__)

@lru_cache
def get_embeddings() -> Embeddings:
    """Return the locally executed embedding model used for indexing and search."""
    settings = get_settings()
    logger.info(f"Initializing local Hugging Face embeddings with model: {settings.embedding_model}")
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        encode_kwargs={"normalize_embeddings": True},
    )
