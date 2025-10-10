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

### Option 1: Install from PyPI (Recommended)

```bash
pip install prompt-contracts
```

This is the easiest way to get started. The package and all dependencies will be installed automatically.

### Option 2: Install from Source (For Development)

```bash
git clone https://github.com/philippmelikidis/prompt-contracts.git
cd prompt-contracts
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

## Understanding Execution Modes

Prompt-Contracts offers four execution modes that use different strategies to ensure LLM output quality. Choosing the right mode depends on your use case.

### Mode Comparison

| Mode | Prompt Changes | Auto-Repair | Retry | Schema Enforcement | Use Case |
|------|----------------|-------------|-------|-------------------|----------|
| **observe** | ❌ None | ❌ No | ❌ No | ❌ No | Testing, Monitoring |
| **assist** | ✅ Add constraints | ✅ Yes | ✅ Yes | ❌ No | Production (all providers) |
| **enforce** | ✅ Schema injection | ✅ Yes | ✅ Yes | ✅ Yes (if supported) | Maximum structure guarantee |
| **auto** | 🔄 Adaptive | ✅ Yes | ✅ Yes | 🔄 When available | Default (recommended) |

### Mode 1: observe (Validation Only)

**When to use:**
- Baseline measurements
- Production system monitoring
- A/B tests without interventions
- Regression testing

**How it works:**
1. Prompt is sent unchanged to the model
2. Response is validated directly
3. No auto-repair, no retries
4. Only PASS or FAIL status

**Example configuration:**
```json
{
  "execution": {
    "mode": "observe",
    "max_retries": 0
  }
}
```

**Run:**
```bash
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_observe.json \
  --report cli
```

**Typical output:**
```
TARGET ollama:mistral
  mode: observe

Fixture: business_email (latency: 1847ms, status: FAIL, retries: 0)
  PASS | pc.check.json_valid
  PASS | pc.check.json_required
  FAIL | pc.check.enum
         Value 'Medium' not in allowed values ['low', 'medium', 'high']

Summary: 5/6 checks passed — status: RED
```

### Mode 2: assist (Prompt Augmentation)

**When to use:**
- Production systems
- Providers without schema enforcement (Ollama, local models)
- When you want control over prompt augmentation
- Standard for robust systems

**How it works:**
1. Automatically derives constraints from Expectation Suite
2. Adds CONSTRAINTS block to prompt
3. On validation failure: Attempt auto-repair
4. On failure after repair: Retry with same prompt
5. Status: PASS, REPAIRED, or FAIL

**Constraint Generation:**

**Expectation Suite:**
```json
{
  "checks": [
    { "type": "pc.check.json_valid" },
    { "type": "pc.check.json_required", "fields": ["category", "priority"] },
    { "type": "pc.check.enum", "field": "$.priority", "allowed": ["low", "medium", "high"] }
  ]
}
```

**Generated Constraint Block:**
```
CONSTRAINTS:
- Response MUST be valid JSON
- Required fields: category, priority
- Field "priority" MUST be one of: low, medium, high
```

**Auto-Repair Capabilities:**
```json
{
  "auto_repair": {
    "strip_markdown_fences": true,        // ```json ... ``` → ...
    "lowercase_fields": ["$.priority"]    // "High" → "high"
  }
}
```

**Example configuration:**
```json
{
  "execution": {
    "mode": "assist",
    "max_retries": 2,
    "auto_repair": {
      "lowercase_fields": ["$.priority", "$.category", "$.sentiment"],
      "strip_markdown_fences": true
    }
  }
}
```

**Run:**
```bash
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_assist.json \
  --save-io artifacts/
```

**Typical output:**
```
TARGET ollama:mistral
  mode: assist

Fixture: business_email (latency: 2134ms, status: REPAIRED, retries: 0)
  Repairs applied: lowercased $.priority, stripped markdown fences
  PASS | pc.check.json_valid
  PASS | pc.check.json_required
  PASS | pc.check.enum
  PASS | pc.check.regex_absent
  PASS | pc.check.token_budget

Summary: 5/5 checks passed (1 REPAIRED) — status: YELLOW
```

**Artifacts saved to:**
```
artifacts/ollama:mistral/business_email/
  input_final.txt      # Prompt with CONSTRAINTS block
  output_raw.txt       # ```json\n{"priority": "High", ...}\n```
  output_norm.txt      # {"priority": "high", ...}
  run.json            # Complete metadata
```

### Mode 3: enforce (Schema-Guided JSON)

**When to use:**
- OpenAI API (GPT-4, GPT-3.5, etc.)
- Maximum structure guarantee required
- Critical production systems
- When JSON Schema enforcement is available

**How it works:**
1. Automatically generates JSON Schema from Expectation Suite
2. Uses provider's native schema enforcement (e.g., OpenAI `response_format`)
3. If not supported: Fallback to `assist` (or NONENFORCEABLE if `strict_enforce=true`)
4. Auto-repair and retry available
5. Status: PASS, REPAIRED, FAIL, or NONENFORCEABLE

**JSON Schema Generation:**

**Expectation Suite:**
```json
{
  "checks": [
    { "type": "pc.check.json_required", "fields": ["category", "urgency", "sentiment"] },
    { "type": "pc.check.enum", "field": "$.category", "allowed": ["business", "personal", "spam"] },
    { "type": "pc.check.enum", "field": "$.urgency", "allowed": ["low", "medium", "high"] }
  ]
}
```

**Generated JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["business", "personal", "spam"]
    },
    "urgency": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    },
    "sentiment": {
      "type": "string"
    }
  },
  "required": ["category", "urgency", "sentiment"],
  "additionalProperties": false
}
```

**Provider Support:**
- ✅ **OpenAI**: Full support via `response_format={"type": "json_schema", ...}`
- ❌ **Ollama**: No native support → Fallback to `assist`
- ❌ **Others**: Provider-dependent

**Example configuration:**
```json
{
  "targets": [
    {
      "type": "openai",
      "model": "gpt-4o-mini",
      "params": { "temperature": 0 }
    }
  ],
  "execution": {
    "mode": "enforce",
    "max_retries": 1,
    "strict_enforce": false
  }
}
```

**strict_enforce Flag:**
- `false` (default): Silent fallback to `assist` when schema enforcement not available
- `true`: Returns NONENFORCEABLE status instead of fallback

**Run:**
```bash
# With OpenAI (requires OPENAI_API_KEY)
export OPENAI_API_KEY="sk-..."
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_enforce.json
```

**Typical output (OpenAI):**
```
TARGET openai:gpt-4o-mini
  mode: enforce
  schema_guided: true

Fixture: business_email (latency: 876ms, status: PASS, retries: 0)
  PASS | pc.check.json_valid
  PASS | pc.check.json_required
  PASS | pc.check.enum

Summary: 5/5 checks passed — status: GREEN
```

**Typical output (Ollama with fallback):**
```
TARGET ollama:mistral
  mode: enforce → assist (fallback)
  schema_guided: false

Fixture: business_email (latency: 2013ms, status: REPAIRED, retries: 0)
  ...
```

### Mode 4: auto (Adaptive)

**When to use:**
- Default mode for most use cases
- Multi-provider setups
- Maximum compatibility required
- No specific mode preferences

**How it works:**
1. Checks adapter capabilities at runtime
2. Selects the best available mode:
   - If `schema_guided_json=true` → uses `enforce`
   - Otherwise → uses `assist`
   - On errors → fallback to `observe`
3. Different effective mode can be chosen per target

**Fallback Logic:**
```
auto
  ├─ Check: adapter.capabilities().schema_guided_json?
  │   ├─ YES  → enforce
  │   └─ NO   → assist
  └─ On error → observe
```

**Example configuration (Multi-Provider):**
```json
{
  "targets": [
    { "type": "openai", "model": "gpt-4o-mini" },
    { "type": "ollama", "model": "mistral" }
  ],
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

**Run:**
```bash
prompt-contracts run \
  --pd examples/email_classification/pd.json \
  --es examples/email_classification/es.json \
  --ep examples/email_classification/ep_auto.json \
  --report cli
```

**Typical output:**
```
TARGET openai:gpt-4o-mini
  mode: auto → enforce
  schema_guided: true

Fixture: business_email (latency: 892ms, status: PASS, retries: 0)
  PASS | All checks

Summary: 5/5 checks passed — status: GREEN

---

TARGET ollama:mistral
  mode: auto → assist
  schema_guided: false

Fixture: business_email (latency: 2156ms, status: REPAIRED, retries: 0)
  Repairs applied: lowercased $.priority
  PASS | All checks after repair

Summary: 5/5 checks passed (1 REPAIRED) — status: YELLOW
```

### Retry and Auto-Repair Flow

**Flow for assist/enforce mode:**

```
1. Execute Prompt
   ↓
2. Validate Response
   ├─ PASS → ✅ Done
   └─ FAIL → Try Auto-Repair
      ├─ Strip markdown fences (```json ... ```)
      ├─ Lowercase configured fields
      └─ Re-validate
         ├─ PASS → ✅ Status: REPAIRED
         └─ FAIL → Retry?
            ├─ retries_left > 0 → Execute Prompt again
            └─ retries_left = 0 → ❌ Status: FAIL
```

**Example run.json (after repair):**
```json
{
  "status": "REPAIRED",
  "retries_used": 0,
  "repaired_details": {
    "stripped_fences": true,
    "lowercased_fields": ["$.priority", "$.category"]
  },
  "output_raw": "```json\n{\"priority\": \"High\", \"category\": \"Business\"}```",
  "output_normalized": "{\"priority\": \"high\", \"category\": \"business\"}"
}
```

### Choosing the Right Mode

**Decision Tree:**

```
Do you need monitoring only without interventions?
├─ YES  → observe
└─ NO
   └─ Using OpenAI and need guaranteed structure?
      ├─ YES  → enforce
      └─ NO
         └─ Using multiple providers or uncertain?
            ├─ Multiple providers → auto
            └─ Single provider → assist
```

**Production Recommendations:**

| Scenario | Recommended Mode | Rationale |
|----------|------------------|-----------|
| OpenAI Production | `enforce` | Native schema support |
| Ollama/Local Models | `assist` | Robust prompt augmentation |
| Multi-Provider | `auto` | Automatic adaptation |
| CI/CD Testing | `observe` | No modifications |
| Development | `assist` | Good debugging |

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

If installed from PyPI:
```bash
pip install --upgrade prompt-contracts
```

If installed from source:
```bash
cd prompt-contracts
pip install -e .
```

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
