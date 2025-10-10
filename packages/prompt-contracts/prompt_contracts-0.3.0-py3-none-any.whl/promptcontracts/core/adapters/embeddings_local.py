"""
Local embedding adapter using sentence-transformers.

Provides semantic similarity capabilities using MiniLM model.
Optional dependency: install with `pip install sentence-transformers`.
"""

from typing import Any


class EmbeddingAdapter:
    """Base class for embedding adapters."""

    def embed(self, text: str) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        raise NotImplementedError


class LocalEmbeddingAdapter(EmbeddingAdapter):
    """
    Local embedding using sentence-transformers.

    Requires: pip install sentence-transformers
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize local embedding adapter.

        Args:
            model_name: Hugging Face model name
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            ) from e

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class DummyEmbeddingAdapter(EmbeddingAdapter):
    """
    Dummy embedding adapter for testing.

    Returns random embeddings of fixed dimension.
    """

    def __init__(self, dimension: int = 384):
        """
        Initialize dummy adapter.

        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        """
        Generate dummy embedding.

        Args:
            text: Input text (ignored)

        Returns:
            Random embedding vector
        """
        import random

        random.seed(hash(text) % (2**32))
        return [random.random() for _ in range(self.dimension)]


def create_embedding_adapter(
    adapter_type: str = "local",
    model_name: str = "all-MiniLM-L6-v2",
    **kwargs: Any,
) -> EmbeddingAdapter:
    """
    Create an embedding adapter.

    Args:
        adapter_type: Type of adapter ("local" or "dummy")
        model_name: Model name for local adapter
        **kwargs: Additional arguments

    Returns:
        Configured EmbeddingAdapter
    """
    if adapter_type == "local":
        return LocalEmbeddingAdapter(model_name)
    elif adapter_type == "dummy":
        dimension = kwargs.get("dimension", 384)
        return DummyEmbeddingAdapter(dimension)
    else:
        raise ValueError(f"Unknown embedding adapter type: {adapter_type}")
