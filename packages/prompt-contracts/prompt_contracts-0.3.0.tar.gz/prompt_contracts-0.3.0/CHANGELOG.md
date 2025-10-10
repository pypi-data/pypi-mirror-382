# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-09

### Added

#### Core Features
- **Probabilistic Sampling**: N-sampling with configurable aggregation policies (majority, all, any, first)
- **Bootstrap Confidence Intervals**: Statistical confidence bounds for pass rates
- **Formal Capability Negotiation**: μ(Acap, Mreq) -> Mactual mapping with detailed logs
- **Enhanced Parsing**: json_loose() for fault-tolerant JSON extraction, regex_extract() utilities
- **Repair Policy Framework**: Structured repair_policy with allowed steps and max_steps
- **Metrics Module**: Comprehensive metrics including validation_success, task_accuracy, repair_rate, latency_ms, overhead_pct, provider_consistency

#### Semantic Checks
- **pc.check.contains_all**: Verify all required substrings present
- **pc.check.contains_any**: Verify at least one option present
- **pc.check.regex_present**: Pattern matching with flags support
- **pc.check.similarity**: Semantic similarity using embeddings (requires sentence-transformers)
- **pc.check.judge**: LLM-as-judge for subjective quality evaluation

#### Adapters
- **embeddings_local.py**: Local embedding adapter using sentence-transformers MiniLM
- **judge_openai.py**: OpenAI-based LLM-as-judge adapter
- Enhanced OpenAI/Ollama adapters with seed, top_p support

#### CLI Enhancements
- **--n**: Override sampling count per fixture
- **--seed**: Set random seed for reproducibility
- **--temperature**: Override generation temperature
- **--top-p**: Override top-p sampling parameter
- **--baseline**: Experimental baseline comparison mode

#### Documentation
- **COMPLIANCE.md**: Mapping to ISO/IEC/IEEE 29119, EU AI Act, NIST AI RMF
- **MIGRATION_0.2_to_0.3.md**: Comprehensive migration guide
- Dockerfile for reproducible environments
- Makefile targets: setup, eval-small, eval-full, docker-build

#### Examples
- extraction: Contact info extraction with probabilistic sampling
- summarization: Article summarization with semantic checks

#### Testing
- Unit tests for sampling.py (aggregation policies, bootstrap CI)
- Unit tests for parser.py (json_loose, regex_extract)
- Unit tests for semantic checks

### Changed

- **Runner Architecture**: Completely rewritten to integrate sampling, parsing, and repair
- **Execution Results**: Enhanced with sampling_metadata, repair_ledger, negotiation_log
- **Reporters**: Updated CLI/JSON/JUnit to display sampling info, confidence intervals, repair ledgers
- **Status Values**: Simplified to PASS/FAIL (REPAIRED deprecated, tracked in repair_ledger)
- **CheckRegistry**: Extended with new semantic and judge check types

### Deprecated

- **max_retries**: Use sampling.n instead (still works for backward compatibility)
- **REPAIRED status**: Repairs now tracked in repair_ledger, status is PASS or FAIL

### Fixed

- Improved JSON parsing resilience with json_loose()
- Better error messages in capability negotiation
- More robust repair tracking with structured ledger

### Technical Details

#### API Changes
- ContractRunner accepts optional embedding_adapter and judge_adapter
- SamplingConfig dataclass for N-sampling configuration
- ProviderCapabilities with extended fields (supports_seed, supports_temperature, supports_top_p)

#### Performance
- Parallel sample execution (when n > 1)
- Bootstrap CI computed only when bootstrap_samples > 0
- Optimized JSON schema derivation

### Compliance

This release enables compliance with:
- ISO/IEC/IEEE 29119 (Software Testing Standards)
- EU AI Act Articles 9, 10, 12, 13, 14, 15
- IEEE 730 (Software Quality Assurance)
- NIST AI Risk Management Framework

See docs/COMPLIANCE.md for detailed mapping.

## [Unreleased]

## [0.2.3] - 2025-10-09

### Fixed
- strict_enforce semantics now properly returns NONENFORCEABLE status instead of silent fallback when schema enforcement is requested but unavailable
- Absolute artifact paths now included in JSON reporter and run.json under "artifact_paths" field
- Enum case-insensitive comparison now works consistently without mutating payload

### Changed
- CLI help text enhanced with examples and usage patterns
- Exit codes clarified and documented (0=success, 1=failure/nonenforceable, 2=validation error, 3=runtime error)
- effective_mode now logged in CLI output and included in all run.json files
- Verbose mode added with -v/--verbose flag for detailed output
- Improved error messages with better categorization (validation vs runtime errors)

### Documentation
- README updated with CLI syntax and exit code table
- TROUBLESHOOTING.md added with common issues and solutions
- All documentation synchronized with actual implementation behavior
- Examples section expanded with real output snippets

## [0.2.2] - 2025-10-08

### Added
- **BEST_PRACTICES.md**: Comprehensive production guide covering:
  - Contract design principles
  - Execution mode selection strategies
  - Writing effective prompts
  - Designing expectation suites
  - Fixture strategies
  - Auto-repair configuration
  - Tolerance tuning
  - Production deployment patterns
  - Testing & CI/CD integration
  - Monitoring & observability
  - Common pitfalls and solutions
  - 3 real-world examples (content moderation, financial transactions, sentiment analysis)
- New comprehensive examples:
  - `email_classification/`: All 4 execution modes with sentiment analysis
  - `product_recommendation/`: Personalized product recommendations
- Enhanced documentation:
  - Detailed execution modes explanation in README.md
  - Comprehensive mode comparison in QUICKSTART.md
  - Complete examples overview in examples/README.md
  - All documentation translated to English

### Changed
- Improved README.md structure with Examples section
- Enhanced QUICKSTART.md with detailed mode guides, decision trees, and production recommendations
- Updated Table of Contents to include Best Practices guide

### Documentation
- All documentation now in English for international audience
- Professional production-ready guidance
- Real-world use case examples

## [0.2.1] - 2025-10-08

### Added
- Public Python API: `run_contract()` and `validate_artifact()`
- Execution modes: `observe`, `assist`, `enforce`, `auto` with capability negotiation
- Auto-repair utilities: markdown fence stripping, JSONPath field lowercasing
- Retry logic with exponential backoff
- Comprehensive error classes: `SpecValidationError`, `AdapterError`, `ExecutionError`, `CheckFailure`
- Artifact saving with `--save-io` flag (input_final.txt, output_raw.txt, output_norm.txt, run.json)
- Status codes: `PASS`, `REPAIRED`, `FAIL`, `NONENFORCEABLE`
- Case-insensitive enum checks
- GitHub issue templates (bug report, feature request, release checklist)
- Pull request template
- Contributing guidelines (CONTRIBUTING.md)
- Code owners configuration (CODEOWNERS)
- CI/CD pipeline (GitHub Actions)
- Pre-commit hooks configuration
- EditorConfig for consistent code style
- Comprehensive utility modules (errors, normalization, retry, hashing, timestamps)

### Changed
- Version bumped to 0.2.1
- Refactored package structure with `utils/` module
- Enhanced EP schema to support `execution` configuration
- Improved adapter interface with `capabilities()` method
- Updated documentation with professional structure

### Fixed
- Module import issues with Python 3.13 editable installs

## [0.1.0] - 2025-10-08

### Added
- Initial release of prompt-contracts
- PCSL (Prompt Contract Specification Language) v0.1
- Core artifacts: Prompt Definition (PD), Expectation Suite (ES), Evaluation Profile (EP)
- JSON Schema validation for all artifacts
- Built-in checks:
  - `pc.check.json_valid` - JSON validity
  - `pc.check.json_required` - Required fields
  - `pc.check.enum` - Enum value validation
  - `pc.check.regex_absent` - Regex pattern absence
  - `pc.check.token_budget` - Token budget enforcement
  - `pc.check.latency_budget` - Latency budget enforcement
- LLM adapters:
  - OpenAI adapter (gpt-4o-mini, gpt-3.5-turbo)
  - Ollama adapter (local models)
- Reporters:
  - CLI reporter (human-readable output)
  - JSON reporter (machine-readable)
  - JUnit reporter (CI integration)
- CLI with `validate` and `run` subcommands
- Conformance levels: L1 (Structural), L2 (Semantic), L3 (Differential)
- Example contracts for support ticket classification
- Basic test suite
- README and QUICKSTART documentation

### Technical Details
- Python 3.10+ support
- YAML and JSON artifact support
- JSONPath-based field extraction
- Tolerance-based pass/fail gates

---

## Release Tags

- [Unreleased]: https://github.com/PhilipposMelikidis/prompt-contracts/compare/v0.1.0...HEAD
- [0.1.0]: https://github.com/PhilipposMelikidis/prompt-contracts/releases/tag/v0.1.0
