# Contributing to Prompt Contracts

Thank you for your interest in contributing to prompt-contracts! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Specification Changes](#specification-changes)

## Code of Conduct

This project follows a standard code of conduct:
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/prompt-contracts.git
   cd prompt-contracts
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/prompt-contracts.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip and virtualenv
- Git

### Setup Development Environment

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Install Local LLM (Optional)

For testing with Ollama:
```bash
# macOS
brew install ollama
ollama serve
ollama pull llama3.1:8b
ollama pull mistral
```

## Development Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features (if used)
- `feature/[name]`: New features
- `fix/[name]`: Bug fixes
- `docs/[name]`: Documentation updates
- `release/v[version]`: Release preparation

### Working on a Feature

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** with frequent commits:
   ```bash
   git add .
   git commit -m "feat: add new check type for regex patterns"
   ```

3. **Keep your branch updated**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. **Push your changes**:
   ```bash
   git push origin feature/my-new-feature
   ```

### Commit Message Convention

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add case-insensitive enum check
fix: resolve JSON parsing error in normalization
docs: update README with new execution modes
test: add unit tests for retry logic
```

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

### Automated Formatting

Pre-commit hooks will automatically format your code:

- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting

Manual formatting:
```bash
black src/ tests/
isort src/ tests/
ruff check src/ tests/
```

### Code Structure

```python
"""Module docstring."""

import standard_library
import third_party
from promptcontracts import local_imports


def public_function(param: str) -> dict:
    """
    Function docstring.
    
    Args:
        param: Description
        
    Returns:
        Description
    """
    pass


class PublicClass:
    """Class docstring."""
    
    def __init__(self):
        """Initialize."""
        pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=promptcontracts --cov-report=html

# Run specific test file
pytest tests/test_loader.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for common setup
- Aim for high coverage of new code

Example:
```python
import pytest
from promptcontracts import run_contract


def test_contract_execution():
    """Test basic contract execution."""
    results = run_contract(
        pd="examples/support_ticket/pd.json",
        es="examples/support_ticket/es.json",
        ep="examples/support_ticket/ep.json",
    )
    assert results["status"] in ["PASS", "FAIL", "REPAIRED"]
```

### Integration Tests

For tests requiring LLMs:
- Mock LLM responses where possible
- Mark real LLM tests with `@pytest.mark.integration`
- Document required setup (e.g., Ollama running)

## Submitting Changes

### Before Submitting

1. **Run all checks**:
   ```bash
   # Linting
   ruff check src/ tests/
   black --check src/ tests/
   isort --check src/ tests/
   
   # Tests
   pytest
   
   # Pre-commit (runs all hooks)
   pre-commit run --all-files
   ```

2. **Update documentation**:
   - Update README.md if behavior changed
   - Update CHANGELOG.md
   - Update docstrings
   - Update PCSL spec if needed

3. **Add tests** for new functionality

### Pull Request Process

1. **Push your branch** to your fork
2. **Create a Pull Request** on GitHub
3. **Fill out the PR template** completely
4. **Ensure CI passes** (GitHub Actions)
5. **Request review** from maintainers
6. **Address feedback** if any
7. **Squash commits** if requested
8. **Merge** will be done by maintainers

### PR Review Criteria

- Code quality and style
- Test coverage
- Documentation completeness
- Backwards compatibility
- Performance impact
- Security considerations

## Specification Changes

### PCSL Spec Updates

Changes to the PCSL specification require:

1. **RFC Issue**: Open an issue labeled `spec-change` with:
   - Motivation
   - Proposed changes
   - Impact analysis
   - Migration path

2. **Community Discussion**: Allow time for feedback

3. **Version Bump**: Spec changes require version increment:
   - Patch: Clarifications, typos
   - Minor: Backwards-compatible additions
   - Major: Breaking changes

4. **Documentation**: Update:
   - `src/promptcontracts/spec/pcsl-vX.Y.md`
   - JSON Schemas in `src/promptcontracts/spec/schema/`
   - Examples
   - Migration guide (if breaking)

### JSON Schema Changes

When modifying schemas:
- Maintain backwards compatibility when possible
- Update all three schemas (PD, ES, EP) consistently
- Validate examples against new schemas
- Update loader validation logic

## Project Structure

```
prompt-contracts/
├── src/promptcontracts/          # Main package
│   ├── core/                     # Core logic
│   │   ├── loader.py            # Artifact loading
│   │   ├── validator.py         # Validation logic
│   │   ├── runner.py            # Execution orchestration
│   │   ├── adapters/            # LLM adapters
│   │   └── reporters/           # Output formatters
│   ├── checks/                  # Built-in checks
│   ├── utils/                   # Utilities
│   └── spec/                    # PCSL specification
├── tests/                       # Test suite
├── examples/                    # Example contracts
└── .github/                     # GitHub config
```

## Need Help?

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an issue with the bug report template
- **Features**: Open an issue with the feature request template
- **Security**: Email maintainers directly (see SECURITY.md)

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- GitHub contributors page
- Release notes

Thank you for contributing!

