"""OpenAI adapter."""

import time
from typing import Any

from openai import OpenAI

from .base import AbstractAdapter, Capability


class OpenAIAdapter(AbstractAdapter):
    """Adapter for OpenAI models."""

    def __init__(self, model: str, params: dict = None):
        super().__init__(model, params)
        self.client = OpenAI()

    def capabilities(self) -> Capability:
        """Return OpenAI capabilities."""
        return Capability(schema_guided_json=True, tool_calling=True, function_call_json=False)

    def generate(self, prompt: str, schema: dict[str, Any] | None = None) -> tuple[str, int]:
        """
        Generate response using OpenAI API.

        Args:
            prompt: The prompt text
            schema: Optional JSON schema for structured output

        Returns:
            (response_text, latency_ms)
        """
        start_time = time.time()

        # Default parameters
        temperature = self.params.get("temperature", 0)
        max_tokens = self.params.get("max_tokens", None)

        # Build request params
        request_params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        if max_tokens:
            request_params["max_tokens"] = max_tokens

        # Add schema-guided JSON if schema provided
        if schema:
            # Use response_format with json_schema (for newer models)
            request_params["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "response", "strict": True, "schema": schema},
            }

        response = self.client.chat.completions.create(**request_params)

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        response_text = response.choices[0].message.content

        return response_text, latency_ms
