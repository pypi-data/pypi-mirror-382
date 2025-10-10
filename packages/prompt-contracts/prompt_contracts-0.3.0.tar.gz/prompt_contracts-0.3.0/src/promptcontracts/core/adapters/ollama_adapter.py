"""Ollama adapter."""

import time
from typing import Any

import httpx

from .base import AbstractAdapter, Capability


class OllamaAdapter(AbstractAdapter):
    """Adapter for Ollama models."""

    def __init__(self, model: str, params: dict = None, base_url: str = "http://localhost:11434"):
        super().__init__(model, params)
        self.base_url = base_url

    def capabilities(self) -> Capability:
        """Return Ollama capabilities (no schema enforcement)."""
        return Capability(
            schema_guided_json=False,
            tool_calling=False,
            function_call_json=False,
            supports_seed=True,
            supports_temperature=True,
            supports_top_p=True,
            max_tokens=None,
        )

    def generate(self, prompt: str, schema: dict[str, Any] | None = None) -> tuple[str, int]:
        """
        Generate response using Ollama API.

        Args:
            prompt: The prompt text
            schema: Optional JSON schema (ignored by Ollama)

        Returns:
            (response_text, latency_ms)
        """
        # Note: Ollama doesn't support schema-guided generation, so schema is ignored
        start_time = time.time()

        # Build request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        # Add optional parameters
        options = {}
        if "temperature" in self.params:
            options["temperature"] = self.params["temperature"]
        if "top_p" in self.params:
            options["top_p"] = self.params["top_p"]
        if "seed" in self.params:
            options["seed"] = self.params["seed"]

        if options:
            payload["options"] = options

        # Make request
        with httpx.Client(timeout=120.0) as client:
            response = client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        response_text = data.get("response", "")

        return response_text, latency_ms
