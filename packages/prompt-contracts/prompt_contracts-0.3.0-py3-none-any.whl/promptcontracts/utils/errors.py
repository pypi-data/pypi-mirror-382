"""Custom exception classes for prompt-contracts."""


class PromptContractsError(Exception):
    """Base exception for all prompt-contracts errors."""

    pass


class SpecValidationError(PromptContractsError):
    """Raised when a PCSL artifact fails schema validation."""

    def __init__(self, artifact_type: str, path: str, message: str):
        self.artifact_type = artifact_type
        self.path = path
        super().__init__(f"{artifact_type} validation failed for '{path}': {message}")


class AdapterError(PromptContractsError):
    """Raised when an LLM adapter encounters an error."""

    def __init__(self, adapter_name: str, message: str, original_error: Exception = None):
        self.adapter_name = adapter_name
        self.original_error = original_error
        super().__init__(f"Adapter '{adapter_name}' failed: {message}")


class ExecutionError(PromptContractsError):
    """Raised when contract execution fails."""

    def __init__(self, message: str, fixture_id: str = None):
        self.fixture_id = fixture_id
        super().__init__(message)


class CheckFailure(PromptContractsError):
    """Raised when a check fails during validation."""

    def __init__(self, check_type: str, message: str, details: dict = None):
        self.check_type = check_type
        self.details = details or {}
        super().__init__(f"Check '{check_type}' failed: {message}")
