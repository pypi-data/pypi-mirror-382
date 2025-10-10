"""
Formal capability negotiation for prompt contracts.

Implements μ(Acap, Mreq) -> Mactual mapping with detailed logging
to determine the effective execution mode based on provider capabilities.
"""

import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)


ExecutionMode = Literal["observe", "assist", "enforce", "auto"]
EffectiveMode = Literal["observe", "assist", "enforce"]


@dataclass
class ProviderCapabilities:
    """Capabilities of a model provider."""

    provider_type: str  # e.g., "openai", "ollama"
    model_name: str
    schema_guided_json: bool = False  # Structured output support
    function_calling: bool = False
    streaming: bool = False
    max_tokens: int | None = None
    supports_temperature: bool = True
    supports_top_p: bool = True
    supports_seed: bool = False


@dataclass
class ModeRequirements:
    """Requirements for a specific execution mode."""

    mode: ExecutionMode
    requires_schema_json: bool = False
    requires_function_calling: bool = False
    strict_enforce: bool = False


@dataclass
class NegotiationResult:
    """Result of capability negotiation."""

    requested_mode: ExecutionMode
    effective_mode: EffectiveMode
    is_nonenforceable: bool
    fallback_applied: bool
    negotiation_log: list[str]
    capabilities_used: dict[str, bool]


class CapabilityNegotiator:
    """
    Negotiates execution mode based on provider capabilities.

    Implements the mapping: μ(Acap, Mreq) -> Mactual
    where:
    - Acap = Provider capabilities
    - Mreq = Requested mode
    - Mactual = Actual/effective mode
    """

    def __init__(
        self,
        capabilities: ProviderCapabilities,
        strict_enforce: bool = False,
    ):
        """
        Initialize negotiator.

        Args:
            capabilities: Provider capabilities
            strict_enforce: If True, fail instead of falling back from enforce
        """
        self.capabilities = capabilities
        self.strict_enforce = strict_enforce
        self.log: list[str] = []

    def negotiate(self, requested_mode: ExecutionMode) -> NegotiationResult:
        """
        Negotiate effective execution mode.

        Args:
            requested_mode: Mode requested by user

        Returns:
            Negotiation result with effective mode and logs
        """
        self.log = []
        self._log(f"Starting negotiation for mode: {requested_mode}")
        self._log(f"Provider: {self.capabilities.provider_type}:{self.capabilities.model_name}")
        self._log(f"Capabilities: schema_json={self.capabilities.schema_guided_json}")

        # Determine requirements for requested mode
        requirements = self._get_mode_requirements(requested_mode)

        # Check if capabilities meet requirements
        can_fulfill, missing = self._check_capabilities(requirements)

        effective_mode: EffectiveMode
        is_nonenforceable = False
        fallback_applied = False

        if requested_mode == "observe":
            # Observe mode has no special requirements
            effective_mode = "observe"
            self._log("Mode: observe - no capabilities required")

        elif requested_mode == "assist":
            # Assist mode always works
            effective_mode = "assist"
            self._log("Mode: assist - capabilities sufficient")

        elif requested_mode == "enforce":
            if can_fulfill:
                effective_mode = "enforce"
                self._log("Mode: enforce - capabilities sufficient")
            else:
                self._log(f"Mode: enforce - missing capabilities: {missing}")
                if self.strict_enforce:
                    # Mark as non-enforceable but keep mode as enforce
                    effective_mode = "enforce"
                    is_nonenforceable = True
                    self._log("STRICT_ENFORCE: marked as NONENFORCEABLE")
                else:
                    # Fallback to assist
                    effective_mode = "assist"
                    fallback_applied = True
                    self._log("Falling back to assist mode")

        elif requested_mode == "auto":
            # Auto mode: use enforce if capable, otherwise assist
            if self.capabilities.schema_guided_json:
                effective_mode = "enforce"
                self._log("Mode: auto -> enforce (capabilities available)")
            else:
                effective_mode = "assist"
                fallback_applied = True
                self._log("Mode: auto -> assist (enforce not available)")

        else:
            # Default to observe for unknown modes
            effective_mode = "observe"
            fallback_applied = True
            self._log(f"Unknown mode '{requested_mode}' - fallback to observe")

        # Build capabilities usage report
        capabilities_used = {
            "schema_guided_json": (
                effective_mode == "enforce" and self.capabilities.schema_guided_json
            ),
            "function_calling": False,  # Not used in v0.3.0
        }

        result = NegotiationResult(
            requested_mode=requested_mode,
            effective_mode=effective_mode,
            is_nonenforceable=is_nonenforceable,
            fallback_applied=fallback_applied,
            negotiation_log=self.log.copy(),
            capabilities_used=capabilities_used,
        )

        self._log(f"Final: effective_mode={effective_mode}, fallback={fallback_applied}")
        logger.info(
            f"Capability negotiation: {requested_mode} -> {effective_mode} "
            f"(fallback={fallback_applied}, nonenforceable={is_nonenforceable})"
        )

        return result

    def _get_mode_requirements(self, mode: ExecutionMode) -> ModeRequirements:
        """Get requirements for a given mode."""
        if mode == "enforce":
            return ModeRequirements(
                mode=mode,
                requires_schema_json=True,
                strict_enforce=self.strict_enforce,
            )
        else:
            return ModeRequirements(mode=mode)

    def _check_capabilities(self, requirements: ModeRequirements) -> tuple[bool, list[str]]:
        """
        Check if capabilities meet requirements.

        Args:
            requirements: Mode requirements

        Returns:
            Tuple of (can_fulfill, missing_capabilities)
        """
        missing = []

        if requirements.requires_schema_json:
            if not self.capabilities.schema_guided_json:
                missing.append("schema_guided_json")

        if requirements.requires_function_calling:
            if not self.capabilities.function_calling:
                missing.append("function_calling")

        can_fulfill = len(missing) == 0
        return can_fulfill, missing

    def _log(self, message: str):
        """Add message to negotiation log."""
        self.log.append(message)


def negotiate_mode(
    capabilities: ProviderCapabilities,
    requested_mode: ExecutionMode,
    strict_enforce: bool = False,
) -> NegotiationResult:
    """
    Convenience function to negotiate execution mode.

    Args:
        capabilities: Provider capabilities
        requested_mode: Requested execution mode
        strict_enforce: If True, fail instead of falling back

    Returns:
        Negotiation result
    """
    negotiator = CapabilityNegotiator(capabilities, strict_enforce)
    return negotiator.negotiate(requested_mode)
