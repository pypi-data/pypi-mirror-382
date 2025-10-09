"""LLM adapters for different providers."""

from .base import AbstractAdapter, Capability
from .ollama_adapter import OllamaAdapter
from .openai_adapter import OpenAIAdapter

__all__ = ["AbstractAdapter", "Capability", "OpenAIAdapter", "OllamaAdapter"]
