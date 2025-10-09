"""Base adapter interface."""

from abc import ABC, abstractmethod
from typing import Any, NamedTuple


class Capability(NamedTuple):
    """Adapter capabilities."""

    schema_guided_json: bool = False
    tool_calling: bool = False
    function_call_json: bool = False


class AbstractAdapter(ABC):
    """Base class for LLM adapters."""

    def __init__(self, model: str, params: dict[str, Any] = None):
        """
        Initialize adapter.

        Args:
            model: Model identifier
            params: Provider-specific parameters
        """
        self.model = model
        self.params = params or {}

    def capabilities(self) -> Capability:
        """
        Return adapter capabilities.

        Returns:
            Capability tuple with supported features
        """
        return Capability()

    @abstractmethod
    def generate(self, prompt: str, schema: dict[str, Any] | None = None) -> tuple[str, int]:
        """
        Generate a response from the LLM.

        Args:
            prompt: The prompt text
            schema: Optional JSON schema for schema-guided generation (if supported)

        Returns:
            (response_text, latency_ms)
        """
        pass
