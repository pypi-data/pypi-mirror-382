# Quick Start Guide

Get up and running with Prompt-Contracts in 5 minutes.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup Local Model](#setup-local-model)
- [Running Your First Contract](#running-your-first-contract)
- [Understanding the Output](#understanding-the-output)
- [Using OpenAI Instead](#using-openai-instead)
- [Creating Custom Contracts](#creating-custom-contracts)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Prerequisites

**Required:**
- Python 3.10 or higher
- pip package manager

**Optional:**
- Ollama (for local models)
- OpenAI API key (for OpenAI models)

---

## Installation

### Step 1: Install Dependencies

```bash
cd /Users/PhilipposMelikidis/Desktop/prompt-contracts
pip install -r requirements.txt
```

### Step 2: Install Package

```bash
pip install -e .
```

This makes the `prompt-contracts` command available globally.

### Step 3: Verify Installation

```bash
prompt-contracts --help
```

Expected output:
```
usage: prompt-contracts [-h] {validate,run} ...

prompt-contracts: Test your LLM prompts like code

positional arguments:
  {validate,run}  Command to run
    validate      Validate a PCSL artefact
    run           Run a contract
...
```

---

## Setup Local Model

### Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai

### Start Ollama Server

Open a separate terminal and run:
```bash
ollama serve
```

Leave this running in the background.

### Pull Mistral Model

```bash
ollama pull mistral
```

This downloads the Mistral 7B model (approximately 4GB).

---

## Running Your First Contract

### Validate Artefacts

First, validate the example contracts against PCSL schemas:

```bash
prompt-contracts validate pd examples/support_ticket/pd.json
prompt-contracts validate es examples/support_ticket/es.json
prompt-contracts validate ep examples/support_ticket/ep.json
```

Expected output for each:
```
Valid Prompt Definition: examples/support_ticket/pd.json
  PCSL version: 0.1.0
  ID: support.ticket.classify.v1
```

### Run the Contract

Execute the complete contract:

```bash
prompt-contracts run \
  --pd examples/support_ticket/pd.json \
  --es examples/support_ticket/es.json \
  --ep examples/support_ticket/ep.json \
  --report cli
```

This will:
1. Load the prompt definition, expectation suite, and evaluation profile
2. Run 2 test fixtures through Mistral
3. Validate each response against 6 checks
4. Display a formatted CLI report

---

## Understanding the Output

### Sample Output

```
Loading artefacts...
Valid Prompt Definition: examples/support_ticket/pd.json
Valid Expectation Suite: examples/support_ticket/es.json
Valid Evaluation Profile: examples/support_ticket/ep.json

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
  PASS | pc.check.regex_absent
         Pattern '```' not found (as expected)
  PASS | pc.check.token_budget
         Token count ~45 <= 200

Fixture: billing (latency: 2113ms, status: REPAIRED, retries: 0)
  ...

============================================================
Summary: 11/11 checks passed (0 PASS, 2 REPAIRED) — status: YELLOW
============================================================
```

### Status Interpretation

**Per-Fixture Status:**
- **PASS**: Response validated successfully on first attempt
- **REPAIRED**: Response validated after auto-repair (e.g., lowercased field)
- **FAIL**: Response failed validation after all retries
- **NONENFORCEABLE**: Enforcement mode requested but not supported

**Overall Status:**
- **GREEN**: All fixtures passed without repairs
- **YELLOW**: Some fixtures required repairs or marked nonenforceable
- **RED**: One or more fixtures failed

---

## Using OpenAI Instead

### Set API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Modify Evaluation Profile

Edit `examples/support_ticket/ep.json` and change the target:

```json
{
  "targets": [
    {
      "type": "openai",
      "model": "gpt-4o-mini",
      "params": {
        "temperature": 0
      }
    }
  ]
}
```

### Run with OpenAI

```bash
prompt-contracts run \
  --pd examples/support_ticket/pd.json \
  --es examples/support_ticket/es.json \
  --ep examples/support_ticket/ep.json \
  --report cli
```

OpenAI adapter will use schema-guided JSON (enforce mode) for guaranteed structure.

---

## Creating Custom Contracts

### Step 1: Create Prompt Definition

Create `my-contract/pd.json`:

```json
{
  "pcsl": "0.1.0",
  "id": "my.custom.prompt",
  "io": {
    "channel": "text",
    "expects": "structured/json"
  },
  "prompt": "Classify the following text into categories: positive, negative, neutral. Return JSON with fields: sentiment, confidence."
}
```

### Step 2: Create Expectation Suite

Create `my-contract/es.json`:

```json
{
  "pcsl": "0.1.0",
  "checks": [
    { "type": "pc.check.json_valid" },
    { 
      "type": "pc.check.json_required", 
      "fields": ["sentiment", "confidence"] 
    },
    {
      "type": "pc.check.enum",
      "field": "$.sentiment",
      "allowed": ["positive", "negative", "neutral"]
    },
    { "type": "pc.check.token_budget", "max_out": 50 }
  ]
}
```

### Step 3: Create Evaluation Profile

Create `my-contract/ep.json`:

```json
{
  "pcsl": "0.1.0",
  "targets": [
    { "type": "ollama", "model": "mistral", "params": {} }
  ],
  "fixtures": [
    { "id": "test1", "input": "This product is amazing!" },
    { "id": "test2", "input": "Worst experience ever." },
    { "id": "test3", "input": "It's okay, nothing special." }
  ],
  "execution": {
    "mode": "assist",
    "max_retries": 1,
    "auto_repair": {
      "lowercase_fields": ["$.sentiment"],
      "strip_markdown_fences": true
    }
  }
}
```

### Step 4: Run Your Contract

```bash
prompt-contracts run \
  --pd my-contract/pd.json \
  --es my-contract/es.json \
  --ep my-contract/ep.json \
  --report cli
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Module

```bash
pytest tests/test_enforcement.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=promptcontracts --cov-report=html
```

View coverage report: `open htmlcov/index.html`

---

## Troubleshooting

### Error: "Module not found: promptcontracts"

**Solution:**
```bash
pip install -e .
```

Ensure you're running from the project root directory.

### Error: "Connection refused" with Ollama

**Symptoms:**
```
Failed to get LLM response: Connection refused
```

**Solutions:**
1. Ensure Ollama is running: `ollama serve`
2. Check if port 11434 is available: `lsof -i :11434`
3. Restart Ollama service

### Error: "Model not found"

**Symptoms:**
```
Failed to get LLM response: model 'mistral' not found
```

**Solution:**
```bash
ollama pull mistral
```

List available models: `ollama list`

### Error: Invalid JSON response

**Symptoms:**
```
FAIL | pc.check.json_valid
       Response is not valid JSON
```

**Solutions:**
1. Enable auto-repair in EP:
   ```json
   "auto_repair": {
     "strip_markdown_fences": true
   }
   ```
2. Use `enforce` mode with OpenAI for guaranteed JSON
3. Improve prompt with explicit JSON formatting instructions

### Validation fails with wrong enum casing

**Symptoms:**
```
FAIL | pc.check.enum
       Value 'High' not in allowed values ['low', 'medium', 'high']
```

**Solutions:**
1. Enable auto-repair lowercase:
   ```json
   "auto_repair": {
     "lowercase_fields": ["$.priority"]
   }
   ```
2. Or use case-insensitive check:
   ```json
   {
     "type": "pc.check.enum",
     "field": "$.priority",
     "allowed": ["low", "medium", "high"],
     "case_insensitive": true
   }
   ```

---

## Next Steps

### Explore Features

**Save Artifacts:**
```bash
prompt-contracts run \
  --pd pd.json --es es.json --ep ep.json \
  --save-io artifacts/
```

View saved artifacts in `artifacts/<target>/<fixture>/`

**Try Different Execution Modes:**

Edit `ep.json` to try different modes:
```json
{
  "execution": {
    "mode": "observe"  // observe, assist, enforce, or auto
  }
}
```

**Generate Different Report Formats:**
```bash
# JSON report
prompt-contracts run --report json --out results.json

# JUnit XML for CI
prompt-contracts run --report junit --out junit.xml
```

### Read Documentation

- **Full README:** `README.md` - Complete feature documentation
- **PCSL Specification:** `src/promptcontracts/spec/pcsl-v0.1.md` - Formal specification
- **Examples:** Explore `examples/` directory for more contract examples

### Customize

- **Create custom checks:** Extend `CheckRegistry` in `validator.py`
- **Add custom adapters:** Subclass `AbstractAdapter`
- **Build custom reporters:** Implement reporter interface

### Integrate

- **CI/CD:** Use JUnit reporter for pipeline integration
- **Monitoring:** Save artifacts for ongoing validation
- **Testing:** Add contracts to your test suite

---

## Getting Help

**Documentation:**
- Main README: `README.md`
- PCSL Spec: `src/promptcontracts/spec/pcsl-v0.1.md`

**Community:**
- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share use cases

**Examples:**
- Basic: `examples/simple_yaml/`
- Advanced: `examples/support_ticket/`

---

## Summary

You've learned how to:
- Install and setup Prompt-Contracts
- Configure Ollama for local model execution
- Run pre-built contract examples
- Understand output and status codes
- Create custom contracts from scratch
- Troubleshoot common issues

For advanced features like schema enforcement, multi-target testing, and artifact analysis, see the main README.
