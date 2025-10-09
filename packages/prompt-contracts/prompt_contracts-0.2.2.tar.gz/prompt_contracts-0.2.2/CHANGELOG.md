# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2025-01-08

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

## [0.2.1] - 2025-01-07

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
