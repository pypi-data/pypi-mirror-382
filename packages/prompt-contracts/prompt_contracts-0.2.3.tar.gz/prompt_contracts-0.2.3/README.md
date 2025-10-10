# Prompt Contracts

[![CI](https://github.com/philippmelikidis/prompt-contracts/actions/workflows/ci.yml/badge.svg)](https://github.com/philippmelikidis/prompt-contracts/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/prompt-contracts.svg)](https://pypi.org/project/prompt-contracts/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Test your LLM prompts like code.**

Prompt-Contracts is a specification and toolkit that brings contract testing to LLM prompt interactions. When models drift due to provider updates, parameter changes, or switches to local models, integrations can silently break. This framework enables structural, semantic, and behavioral validation of LLM responses.

---

## What's New in v0.2.3

**Patch Release** - Improved CLI, artifact paths, and documentation:

- **CLI Enhancements**: Better help text with examples, verbose mode (-v), clarified exit codes
- **Absolute Artifact Paths**: All artifact paths in run.json and JSON reporter now use absolute paths
- **strict_enforce Fix**: Properly returns NONENFORCEABLE status when enforcement unavailable
- **TROUBLESHOOTING Guide**: New comprehensive troubleshooting documentation
- **Documentation Sync**: All docs updated to match actual implementation behavior

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
  - [Artefact Types](#artefact-types)
  - [Execution Modes](#execution-modes)
  - [Status Codes](#status-codes)
- [Examples](#examples)
- [Installation](#installation)
- [Usage](#usage)
  - [CLI Commands](#cli-commands)
  - [Execution Configuration](#execution-configuration)
  - [Artifact Saving](#artifact-saving)
- [Best Practices](BEST_PRACTICES.md) 📘
- [PCSL Specification](#pcsl-specification)
  - [Conformance Levels](#conformance-levels)
  - [Built-in Checks](#built-in-checks)
- [Adapters](#adapters)
- [Reporters](#reporters)
- [Architecture](#architecture)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Prompt-Contracts implements the **Prompt Contract Specification Language (PCSL)**, a formal specification for defining, validating, and enforcing LLM prompt behavior. Similar to how OpenAPI defines REST API contracts or JSON Schema defines data contracts, PCSL defines:

- **What** a prompt expects as input
- **How** the LLM should respond (structure, semantics, performance)
- **Where** these expectations should hold (which models, providers, parameters)

### Common Problems Solved

- **JSON Breakage**: Responses become invalid or wrapped in markdown code fences
- **Missing Fields**: Required fields disappear from structured outputs
- **Enum Drift**: Values drift from expected enums ("urgent" instead of "high")
- **Performance Regression**: Latency and token budgets exceed acceptable limits
- **Model Switching**: Behavior changes when switching between providers or model versions

---

## Key Features

### PCSL v0.1 Implementation

**Specification & Validation**
- Formal PCSL specification with JSON Schema validation
- Three artefact types: Prompt Definition (PD), Expectation Suite (ES), Evaluation Profile (EP)
- Progressive conformance levels (L1-L3)

**Execution Modes**
- **observe**: Validation-only mode with no modifications
- **assist**: Prompt augmentation with auto-generated constraints
- **enforce**: Schema-guided JSON generation (OpenAI structured outputs)
- **auto**: Adaptive mode with intelligent fallback chain

**Auto-Repair & Retries**
- Bounded retry mechanism with configurable limits
- Automatic output normalization (strip markdown fences, lowercase fields)
- Detailed repair tracking and status reporting

**Schema-Guided Enforcement**
- Automatic JSON Schema derivation from expectation suites
- OpenAI structured output integration via `response_format`
- Capability negotiation for provider-specific features

**Full IO Transparency**
- Complete artifact saving with `--save-io` flag
- Per-fixture storage of inputs, outputs, and metadata
- Cryptographic prompt hashing for reproducibility
- Timestamped execution traces

**Multi-Provider Support**
- OpenAI adapter with schema enforcement capabilities
- Ollama adapter for local model execution
- Extensible adapter architecture

**Comprehensive Reporting**
- CLI reporter with rich formatting
- JSON reporter for machine-readable output
- JUnit XML for CI/CD integration

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Ollama (for local models) or OpenAI API key

### Installation

**From PyPI (recommended):**

```bash
pip install prompt-contracts
```

**From source (for development):**

```bash
git clone https://github.com/philippmelikidis/prompt-contracts.git
cd prompt-contracts
pip install -e .
```

### Setup Ollama (Optional)

```bash
# Install Ollama
brew install ollama

# Start server
ollama serve

# Pull model
ollama pull mistral
```

### Run Example Contract

```bash
prompt-contracts run \
  --pd examples/support_ticket/pd.json \
  --es examples/support_ticket/es.json \
  --ep examples/support_ticket/ep.json \
  --report cli
```

**Expected Output:**
```
TARGET ollama:mistral
  mode: assist

Fixture: pwd_reset (latency: 2314ms, status: REPAIRED, retries: 0)
  Repairs applied: lowercased $.priority
  PASS | pc.check.json_valid
         Response is valid JSON
  PASS | pc.check.json_required
         All required fields present: ['category', 'priority', 'reason']
  PASS | pc.check.enum
         Value 'high' is in allowed values ['low', 'medium', 'high']
  ...

Summary: 11/11 checks passed (1 PASS, 1 REPAIRED) — status: YELLOW
```

---

## Core Concepts

### Artefact Types

#### Prompt Definition (PD)

Describes the canonical prompt and I/O expectations.

```json
{
  "pcsl": "0.1.0",
  "id": "support.ticket.classify.v1",
  "io": {
    "channel": "text",
    "expects": "structured/json"
  },
  "prompt": "You are a support classifier. Reply ONLY with strict JSON."
}
```

#### Expectation Suite (ES)

Declares validation checks as properties that must hold for every execution.

```json
{
  "pcsl": "0.1.0",
  "checks": [
    { "type": "pc.check.json_valid" },
    {
      "type": "pc.check.json_required",
      "fields": ["category", "priority", "reason"]
    },
    {
      "type": "pc.check.enum",
      "field": "$.priority",
      "allowed": ["low", "medium", "high"]
    },
    { "type": "pc.check.regex_absent", "pattern": "```" },
    { "type": "pc.check.token_budget", "max_out": 200 },
    { "type": "pc.check.latency_budget", "p95_ms": 5000 }
  ]
}
```

#### Evaluation Profile (EP)

Defines execution context: models, test fixtures, and tolerance thresholds.

```json
{
  "pcsl": "0.1.0",
  "targets": [
    {
      "type": "ollama",
      "model": "mistral",
      "params": { "temperature": 0 }
    }
  ],
  "fixtures": [
    { "id": "pwd_reset", "input": "User: My password doesn't work." },
    { "id": "billing", "input": "User: I was double charged." }
  ],
  "execution": {
    "mode": "assist",
    "max_retries": 1,
    "auto_repair": {
      "lowercase_fields": ["$.priority"],
      "strip_markdown_fences": true
    }
  },
  "tolerances": {
    "pc.check.json_valid": { "max_fail_rate": 0.0 },
    "pc.check.enum": { "max_fail_rate": 0.01 }
  }
}
```

### Execution Modes

Prompt-Contracts provides four execution modes with different strategies for ensuring LLM output quality:

#### observe (Validation Only)
**Purpose:** Pure validation without any modifications
**Behavior:** No changes to prompt or output
**Status Codes:** PASS or FAIL
**Use Case:** Monitoring, testing, baseline measurements

```json
{
  "execution": {
    "mode": "observe",
    "max_retries": 0
  }
}
```

**Example:**
```bash
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_observe.json
```

#### assist (Prompt Augmentation)
**Purpose:** Automatic prompt enhancement with constraints
**Behavior:** Adds auto-generated constraint blocks to prompt
**Status Codes:** PASS, REPAIRED, or FAIL
**Use Case:** Production systems with retry logic

The `assist` mode automatically enriches the prompt with structural requirements:

**Original Prompt:**
```
You are a support classifier. Reply with JSON containing category, priority, reason.
```

**Augmented Prompt (automatic):**
```
You are a support classifier. Reply with JSON containing category, priority, reason.

CONSTRAINTS:
- Response MUST be valid JSON
- Required fields: category, priority, reason
- Field "priority" MUST be one of: low, medium, high
- Do NOT use markdown code fences (```)
```

**Configuration:**
```json
{
  "execution": {
    "mode": "assist",
    "max_retries": 2,
    "auto_repair": {
      "lowercase_fields": ["$.priority", "$.category"],
      "strip_markdown_fences": true
    }
  }
}
```

**Auto-Repair Capabilities:**
- `strip_markdown_fences`: Removes ```json and ``` from responses
- `lowercase_fields`: Normalizes fields to lowercase (e.g., "High" → "high")

**Example:**
```bash
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_assist.json \
  --save-io artifacts/
```

#### enforce (Schema-Guided JSON)
**Purpose:** Leverages provider capabilities for guaranteed JSON structure
**Behavior:** Generates JSON Schema from ES and uses `response_format` (OpenAI)
**Status Codes:** PASS, REPAIRED, FAIL, or NONENFORCEABLE
**Use Case:** Maximum structural guarantee with supporting providers

The `enforce` mode uses native provider features like OpenAI's Structured Outputs:

**Auto-generated JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "category": { "type": "string", "enum": ["business", "personal", "spam", "support", "marketing"] },
    "priority": { "type": "string", "enum": ["low", "medium", "high"] },
    "reason": { "type": "string" }
  },
  "required": ["category", "priority", "reason"],
  "additionalProperties": false
}
```

**Configuration:**
```json
{
  "execution": {
    "mode": "enforce",
    "max_retries": 1,
    "strict_enforce": false
  }
}
```

**Adapter Support:**
- ✅ **OpenAI**: Full support via `response_format`
- ⚠️ **Ollama**: Falls back to `assist` (no schema enforcement)
- ⚠️ **Others**: Capability-based fallback

**strict_enforce Flag:**
- `false` (default): Silent fallback to `assist` when schema not supported
- `true`: Returns NONENFORCEABLE status instead of fallback

**Example:**
```bash
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_enforce.json
```

#### auto (Adaptive)
**Purpose:** Intelligent mode selection based on capabilities
**Behavior:** Fallback chain: enforce → assist → observe
**Status Codes:** Depends on selected mode
**Use Case:** Default mode for maximum compatibility

The `auto` mode automatically selects the best available mode:

**Fallback Logic:**
1. Checks adapter capabilities
2. If `schema_guided_json=true` → uses `enforce`
3. Otherwise → uses `assist`
4. On errors → fallback to `observe`

**Configuration:**
```json
{
  "execution": {
    "mode": "auto",
    "max_retries": 2,
    "auto_repair": {
      "lowercase_fields": ["$.priority"],
      "strip_markdown_fences": true
    }
  }
}
```

**Multi-Provider Example:**
```json
{
  "targets": [
    { "type": "openai", "model": "gpt-4o-mini" },
    { "type": "ollama", "model": "mistral" }
  ],
  "execution": { "mode": "auto" }
}
```

**Result:**
- OpenAI → uses `enforce` (has schema_guided_json)
- Ollama → uses `assist` (no schema_guided_json)

**Example:**
```bash
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_auto.json \
  --report cli
```

### Status Codes

#### Per-Fixture Status
- **PASS**: Validation succeeded on first attempt
- **REPAIRED**: Validation succeeded after auto-repair application
- **FAIL**: Validation failed after exhausting all retries
- **NONENFORCEABLE**: Enforcement requested but adapter lacks capability

#### Per-Target Status
- **GREEN**: All fixtures passed without repairs
- **YELLOW**: Some fixtures repaired or marked nonenforceable
- **RED**: One or more fixtures failed validation

---

## Examples

The repository contains several complete examples demonstrating various use cases and execution modes:

### Support Ticket Classification
**Directory:** `examples/support_ticket/`
**Use Case:** Support request classification
**Mode:** `assist`
**Provider:** Ollama (Mistral)

```bash
prompt-contracts run \
  --pd examples/support_ticket/pd.json \
  --es examples/support_ticket/es.json \
  --ep examples/support_ticket/ep.json \
  --report cli
```

### Email Classification
**Directory:** `examples/email_classification/`
**Use Case:** Email categorization with sentiment analysis
**Modes:** All four modes (`observe`, `assist`, `enforce`, `auto`)
**Provider:** Ollama / OpenAI

**Testing with different modes:**
```bash
# Observe Mode - Validation only
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_observe.json

# Assist Mode - With prompt augmentation
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_assist.json

# Enforce Mode - Schema-guided (OpenAI)
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_enforce.json

# Auto Mode - Adaptive
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_auto.json
```

### Product Recommendation
**Directory:** `examples/product_recommendation/`
**Use Case:** Personalized product recommendations
**Mode:** `assist`
**Provider:** Ollama (Mistral)

```bash
prompt-contracts run \
  --pd examples/product_recommendation/pd.json \
  --es examples/product_recommendation/es.json \
  --ep examples/product_recommendation/ep.json \
  --save-io artifacts/product_recs/
```

### Simple YAML Example
**Directory:** `examples/simple_yaml/`
**Use Case:** Minimal example in YAML format
**Format:** YAML (converted to JSON)

---

## Installation

### From Source

```bash
git clone https://github.com/promptcontracts/prompt-contracts.git
cd prompt-contracts
pip install -r requirements.txt
pip install -e .
```

### Verify Installation

```bash
prompt-contracts --help
```

---

## Usage

### CLI Commands

#### Validate Artefacts

Validate artefacts against PCSL schemas:

```bash
prompt-contracts validate pd examples/support_ticket/pd.json
prompt-contracts validate es examples/support_ticket/es.json
prompt-contracts validate ep examples/support_ticket/ep.json
```

#### Run Contract

Execute a complete contract with validation:

```bash
prompt-contracts run \
  --pd <path-to-pd> \
  --es <path-to-es> \
  --ep <path-to-ep> \
  [--report cli|json|junit] \
  [--out <output-path>] \
  [--save-io <artifacts-directory>] \
  [-v|--verbose]
```

**Arguments:**
- `--pd`: Path to Prompt Definition (JSON/YAML, required)
- `--es`: Path to Expectation Suite (JSON/YAML, required)
- `--ep`: Path to Evaluation Profile (JSON/YAML, required)
- `--report`: Report format - cli (default), json, or junit
- `--out`: Output path for report file (optional)
- `--save-io`: Directory to save execution artifacts (input_final.txt, output_raw.txt, output_norm.txt, run.json)
- `-v, --verbose`: Enable verbose output

**Exit Codes:**
- `0`: All fixtures passed or were repaired successfully
- `1`: One or more fixtures failed or marked NONENFORCEABLE
- `2`: PD/ES/EP validation error (schema mismatch)
- `3`: Runtime/adapter error

**Example with artifacts:**
```bash
prompt-contracts run \
  --pd examples/support_ticket/pd.json \
  --es examples/support_ticket/es.json \
  --ep examples/support_ticket/ep.json \
  --save-io artifacts/ \
  --report json --out results.json \
  --verbose
```

### Execution Configuration

Configure execution behavior in the Evaluation Profile:

```json
{
  "execution": {
    "mode": "assist",
    "max_retries": 1,
    "auto_repair": {
      "lowercase_fields": ["$.priority", "$.status"],
      "strip_markdown_fences": true
    }
  }
}
```

**Configuration Options:**

- `mode`: Execution mode (auto, enforce, assist, observe)
- `max_retries`: Maximum retry attempts on validation failure (default: 1)
- `auto_repair.lowercase_fields`: JSONPath fields to lowercase
- `auto_repair.strip_markdown_fences`: Remove code fence markers (default: true)

### Artifact Saving

Enable comprehensive artifact saving with `--save-io`:

```bash
prompt-contracts run \
  --pd pd.json --es es.json --ep ep.json \
  --save-io artifacts/
```

**Directory Structure:**
```
artifacts/
  <target-id>/
    <fixture-id>/
      input_final.txt      # Final prompt with augmentations
      output_raw.txt       # Raw model response
      output_norm.txt      # Normalized output after auto-repair
      run.json             # Complete execution metadata
```

**run.json Contents:**
```json
{
  "pcsl": "0.1.0",
  "target": "ollama:mistral",
  "params": { "temperature": 0 },
  "execution": {
    "mode": "assist",
    "effective_mode": "assist",
    "max_retries": 1
  },
  "latency_ms": 2314,
  "retries_used": 0,
  "status": "REPAIRED",
  "repaired_details": {
    "stripped_fences": true,
    "lowercased_fields": ["$.priority"]
  },
  "checks": [...],
  "prompt_hash": "a1b2c3...",
  "timestamp": "2025-10-07T12:34:56Z"
}
```

---

## PCSL Specification

### Conformance Levels

PCSL defines progressive conformance levels:

#### L1 - Structural Conformance
- JSON validity validation
- Required field presence checking
- Token budget enforcement
- Basic structural guarantees

#### L2 - Semantic Conformance
Includes L1 plus:
- Enum value validation with JSONPath
- Regex pattern assertions (presence/absence)
- Advanced field-level checks
- Semantic property validation

#### L3 - Differential Conformance
Includes L2 plus:
- Multi-target execution and comparison
- Pass-rate validation across models
- Latency budget enforcement (p95)
- Tolerance-based acceptance criteria

#### L4 - Security Conformance (Planned)
Includes L3 plus:
- Jailbreak escape-rate metrics
- PII leakage detection
- Adversarial robustness testing
- Security property validation

### Built-in Checks

#### pc.check.json_valid
Validates response is parseable JSON.

**Parameters:** None

```json
{ "type": "pc.check.json_valid" }
```

#### pc.check.json_required
Validates presence of required fields at root level.

**Parameters:**
- `fields` (array): Required field names

```json
{
  "type": "pc.check.json_required",
  "fields": ["category", "priority", "reason"]
}
```

#### pc.check.enum
Validates field value against allowed enumeration.

**Parameters:**
- `field` (string): JSONPath to field
- `allowed` (array): Allowed values
- `case_insensitive` (boolean, optional): Case-insensitive comparison

```json
{
  "type": "pc.check.enum",
  "field": "$.priority",
  "allowed": ["low", "medium", "high"],
  "case_insensitive": false
}
```

#### pc.check.regex_absent
Validates regex pattern is NOT present in response.

**Parameters:**
- `pattern` (string): Regex pattern

```json
{ "type": "pc.check.regex_absent", "pattern": "```" }
```

#### pc.check.token_budget
Validates response length stays within token budget.

**Parameters:**
- `max_out` (integer): Maximum output tokens

```json
{ "type": "pc.check.token_budget", "max_out": 200 }
```

**Note:** Current implementation approximates tokens by word count.

#### pc.check.latency_budget
Validates p95 latency across all fixtures.

**Parameters:**
- `p95_ms` (integer): p95 latency threshold in milliseconds

```json
{ "type": "pc.check.latency_budget", "p95_ms": 5000 }
```

---

## Adapters

### OpenAI Adapter

Uses OpenAI SDK with full schema enforcement support.

**Capabilities:**
- `schema_guided_json`: True
- `tool_calling`: True
- `function_call_json`: False

**Features:**
- Structured output via `response_format` with JSON Schema
- Enables `enforce` mode for guaranteed structure
- Parameter support: temperature, max_tokens

**Configuration:**
```json
{
  "type": "openai",
  "model": "gpt-4o-mini",
  "params": {
    "temperature": 0,
    "max_tokens": 500
  }
}
```

### Ollama Adapter

Supports local model execution via Ollama API.

**Capabilities:**
- `schema_guided_json`: False
- `tool_calling`: False
- `function_call_json`: False

**Features:**
- Local model execution
- HTTP API integration
- Falls back to `assist` mode in auto/enforce
- Parameter support: temperature

**Configuration:**
```json
{
  "type": "ollama",
  "model": "mistral",
  "params": {
    "temperature": 0
  }
}
```

### Custom Adapters

Implement custom adapters by subclassing `AbstractAdapter`:

```python
from promptcontracts.core.adapters import AbstractAdapter, Capability

class CustomAdapter(AbstractAdapter):
    def capabilities(self) -> Capability:
        return Capability(
            schema_guided_json=True,
            tool_calling=False,
            function_call_json=False
        )

    def generate(self, prompt: str, schema=None):
        # Implementation
        return response_text, latency_ms
```

---

## Reporters

### CLI Reporter

Rich-formatted terminal output with color coding and hierarchical structure.

**Usage:**
```bash
prompt-contracts run --report cli [--out output.txt]
```

**Features:**
- Color-coded status indicators
- Hierarchical fixture/check display
- Repair detail tracking
- Artifact path display
- Summary statistics

### JSON Reporter

Machine-readable JSON output for programmatic consumption.

**Usage:**
```bash
prompt-contracts run --report json [--out results.json]
```

**Features:**
- Complete result serialization
- Artifact path inclusion
- Metadata enrichment
- Timestamping

### JUnit Reporter

JUnit XML format for CI/CD integration.

**Usage:**
```bash
prompt-contracts run --report junit [--out junit.xml]
```

**Features:**
- Standard JUnit XML format
- Test case per check
- Failure detail capture
- CI/CD pipeline integration

---

## Architecture

### Project Structure

```
src/promptcontracts/
  cli.py                    # CLI entry points
  core/
    loader.py               # Artefact loading and schema validation
    validator.py            # Check registry and execution
    runner.py               # Contract orchestration
    checks/                 # Built-in check implementations
      json_valid.py
      json_required.py
      enum_value.py
      regex_absent.py
      token_budget.py
      latency_budget.py
    adapters/               # LLM provider adapters
      base.py
      openai_adapter.py
      ollama_adapter.py
    reporters/              # Output formatters
      cli_reporter.py
      json_reporter.py
      junit_reporter.py
  spec/                     # PCSL specification
    pcsl-v0.1.md
    schema/
      pcsl-pd.schema.json
      pcsl-es.schema.json
      pcsl-ep.schema.json
examples/                   # Example contracts
tests/                      # Test suite
```

### Dependencies

**Core:**
- `pyyaml`: YAML parsing
- `jsonschema`: Schema validation
- `jsonpath-ng`: JSONPath evaluation
- `httpx`: HTTP client for Ollama
- `numpy`: Statistical calculations

**Provider SDKs:**
- `openai`: OpenAI API integration

**CLI:**
- `rich`: Terminal formatting

---

## Testing

### Run Test Suite

```bash
# All tests
pytest tests/ -v

# Specific test module
pytest tests/test_enforcement.py -v

# With coverage
pytest tests/ --cov=promptcontracts --cov-report=html
```

### Test Categories

- **Loader Tests**: Schema validation, file parsing
- **Check Tests**: Individual check logic
- **Enforcement Tests**: Normalization, schema derivation, retries
- **Integration Tests**: End-to-end contract execution

### Current Coverage

- 17 tests passing
- Core functionality: 100%
- Enforcement features: 100%
- Edge cases: Ongoing

---

## Roadmap

### Completed (v0.1)
- PCSL specification v0.1 with JSON Schemas
- Execution modes (observe, assist, enforce, auto)
- Auto-repair and bounded retries
- Schema-guided JSON (OpenAI structured outputs)
- Artifact saving with full IO transparency
- OpenAI and Ollama adapters
- CLI, JSON, and JUnit reporters
- Conformance levels L1-L3 (scaffold)

### Planned (v0.2)
- L3 Differential runner enhancements
  - Statistical significance testing
  - Drift detection algorithms
  - A/B testing support
- HTML reporter with visualization
  - Trend charts
  - Diff views
  - Interactive filtering
- Additional check types
  - JSON Schema field validation
  - Numeric range checks
  - Cross-field dependencies
  - String length validation

### Planned (v0.3)
- L4 Security conformance
  - Jailbreak escape-rate metrics
  - PII leakage detection
  - Prompt injection testing
  - Adversarial robustness
- Additional adapters
  - Anthropic Claude
  - Google Gemini
  - Azure OpenAI
  - Hugging Face
- Observability integration
  - OpenTelemetry export
  - Prometheus metrics
  - Grafana dashboards

### Planned (Future)
- Multi-modal support (images, audio)
- GitHub Action and GitLab CI templates
- VS Code extension
- Pre-commit hooks
- Fine-tuning contract integration
- Production monitoring integration

---

## Contributing

### Spec Governance

The PCSL specification lives under `src/promptcontracts/spec/`. Changes to the specification follow an RFC process:

1. Open a GitHub Issue describing the proposed change
2. Label as `spec-rfc`
3. Community discussion and feedback
4. Approval by maintainers
5. Implementation and documentation

### Development Setup

```bash
# Clone repository
git clone https://github.com/promptcontracts/prompt-contracts.git
cd prompt-contracts

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest tests/ -v
```

### Contribution Guidelines

- Follow existing code style and patterns
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Write clear commit messages

### Versioning

PCSL and prompt-contracts follow Semantic Versioning:

- **Patch** (0.1.x): Bug fixes, clarifications
- **Minor** (0.x.0): New features, backward-compatible additions
- **Major** (x.0.0): Breaking changes to artefact structure or behavior

---

## License

**Code:** MIT License
**Documentation:** CC-BY 4.0

See LICENSE file for details.

---

## Support

- **Documentation:** See [QUICKSTART.md](QUICKSTART.md) for getting started guide
- **Best Practices:** Read [BEST_PRACTICES.md](BEST_PRACTICES.md) for production guidance
- **Troubleshooting:** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions
- **Specification:** Read `src/promptcontracts/spec/pcsl-v0.1.md` for detailed spec
- **Examples:** Explore [examples/](examples/) for real-world use cases
- **Issues:** Report bugs and request features via GitHub Issues
- **Discussions:** Join community discussions on GitHub Discussions

---

## Citation

If you use Prompt-Contracts in your research or production systems, please cite:

```bibtex
@software{promptcontracts2025,
  title = {Prompt-Contracts: Contract Testing for LLM Prompts},
  author = {Prompt-Contracts Contributors},
  year = {2025},
  url = {https://github.com/promptcontracts/prompt-contracts},
  version = {0.1.0}
}
```
