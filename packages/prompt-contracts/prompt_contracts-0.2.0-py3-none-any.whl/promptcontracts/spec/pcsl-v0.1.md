# PCSL v0.1 – Prompt Contract Specification Language

**Version:** 0.1.0  
**Status:** Draft  
**Last Updated:** October 2025

---

## 1. Introduction

### 1.1 Goals

The **Prompt Contract Specification Language (PCSL)** aims to bring structured, repeatable testing to LLM prompt interactions. Similar to how OpenAPI defines REST API contracts or JSON Schema defines data contracts, PCSL defines:

- **What** a prompt expects as input
- **How** the LLM should respond (structure, semantics, performance)
- **Where** these expectations should hold (which models, providers, parameters)

### 1.2 Scope

PCSL v0.1 covers:
- Text-based prompts with structured (JSON) or unstructured responses
- Structural validation (JSON validity, required fields)
- Semantic validation (enum values, regex patterns, JSONPath assertions)
- Performance budgets (token limits, latency)
- Differential testing (comparing models/versions with tolerance thresholds)

Out of scope for v0.1:
- Multi-modal prompts (images, audio)
- Fine-tuning contract integration
- Production monitoring/alerting

---

## 2. Core Concepts

### 2.1 Artefacts

PCSL defines three primary artefact types:

#### 2.1.1 Prompt Definition (PD)
Describes the canonical prompt, I/O channel, and metadata.

**Required fields:**
- `pcsl` (string): Semantic version of PCSL (e.g., `"0.1.0"`)
- `id` (string): Unique identifier for this prompt
- `io` (object):
  - `channel` (enum): `"text"` (future: `"multimodal"`)
  - `expects` (enum): `"structured/json"`, `"unstructured/text"`
- `prompt` (string): The canonical prompt template

**Optional fields:**
- `metadata`: author, description, tags, etc.

#### 2.1.2 Expectation Suite (ES)
Declares checks (properties) that must hold for responses.

**Required fields:**
- `pcsl` (string): Version
- `checks` (array): List of check objects

Each check has:
- `type` (string): Qualified check name (e.g., `pc.check.json_valid`)
- Additional parameters specific to the check type

#### 2.1.3 Evaluation Profile (EP)
Defines execution context: which models to test, with what inputs, and acceptable tolerances.

**Required fields:**
- `pcsl` (string): Version
- `targets` (array): Model/provider configurations
- `fixtures` (array): Test inputs

Each target:
- `type` (string): `"openai"`, `"ollama"`, etc.
- `model` (string): Model identifier
- `params` (object): Provider-specific parameters (temperature, max_tokens, etc.)

Each fixture:
- `id` (string): Fixture identifier
- `input` (string): Input text to append/inject into prompt

**Optional fields:**
- `tolerances` (object): Map check types to `{ "max_fail_rate": number }` (0.0 = 0%, 1.0 = 100%)
- `execution` (object): Execution configuration for enforcement and retries (see Section 2.2)

### 2.2 Execution Modes & Enforcement

PCSL v0.1 introduces **execution modes** to enable not just validation but also enforcement and auto-repair:

#### 2.2.1 Execution Modes

**`observe`** (Validation Only)
- No modifications to prompt or output
- Pure validation against ES checks
- Status: PASS or FAIL

**`assist`** (Prompt Augmentation)
- Automatically augments prompt with constraints derived from ES
- Example: enum check → "priority MUST be one of: low, medium, high"
- Bounded retries with auto-repair (strip markdown fences, lowercase fields)
- Status: PASS, REPAIRED, or FAIL

**`enforce`** (Schema-Guided JSON)
- Uses adapter capabilities for schema-guided generation (e.g., OpenAI structured outputs)
- Derives JSON Schema from ES (required fields, enum constraints)
- Falls back to `assist` if adapter doesn't support schema enforcement
- Status: PASS, REPAIRED, FAIL, or NONENFORCEABLE

**`auto`** (Adaptive)
- Tries `enforce` if adapter supports → falls back to `assist` → falls back to `observe`
- Default mode
- Maximizes enforcement while maintaining compatibility

#### 2.2.2 Capability Negotiation

Each adapter declares its capabilities:
- `schema_guided_json`: Supports JSON Schema-based structured output
- `tool_calling`: Supports function/tool calling
- `function_call_json`: Supports function call JSON mode

The runner selects the effective mode based on:
1. Requested mode from EP.execution.mode
2. Adapter capabilities
3. Fallback chain (enforce → assist → observe)

#### 2.2.3 Auto-Repair & Retries

**EP.execution** configuration:
```json
{
  "mode": "assist",
  "max_retries": 1,
  "auto_repair": {
    "strip_markdown_fences": true,
    "lowercase_fields": ["$.priority"]
  }
}
```

**Retry logic:**
1. Generate response
2. Validate against ES
3. If FAIL and retries remain:
   - Apply auto-repair (strip fences, lowercase fields)
   - Re-validate
   - If still FAIL: retry generation
4. Status: PASS (first attempt), REPAIRED (fixed by auto-repair), FAIL (exhausted retries)

**Auto-repair operations:**
- `strip_markdown_fences`: Remove ` ```json` and ` ``` ` markers
- `lowercase_fields`: Apply `.lower()` to specified JSONPath fields (e.g., enum values)

#### 2.2.4 Prompt Augmentation

In `assist` and `enforce` modes, the runner appends a `[CONSTRAINTS]` block to the prompt:

**Example augmentation from ES:**
```
[CONSTRAINTS]
- Output MUST be strict JSON.
- Required fields: category, priority, reason.
- `priority` MUST be exactly one of: low, medium, high (lowercase).
- Do NOT include markdown code fences (```).
- Keep response under 200 tokens/words.
```

Augmentation is deterministic and ordered by check type.

#### 2.2.5 Artifact Saving

With `--save-io <dir>`, the runner saves per-fixture artifacts:

**Directory structure:**
```
<dir>/
  <target_id>/
    <fixture_id>/
      input_final.txt      # Final prompt (with constraints if applicable)
      output_raw.txt       # Raw model output
      output_norm.txt      # After auto-repair (if any)
      run.json             # Metadata (status, retries, checks, timestamp, etc.)
```

**run.json format:**
```json
{
  "pcsl": "0.1.0",
  "target": "ollama:mistral",
  "params": {...},
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
  "prompt_hash": "<sha256>",
  "timestamp": "2025-10-07T12:34:56Z"
}
```

#### 2.2.6 Status Codes

**Per-fixture status:**
- **PASS**: Validation passed on first attempt
- **REPAIRED**: Validation passed after auto-repair
- **FAIL**: Validation failed after exhausting retries
- **NONENFORCEABLE**: Requested `enforce` mode but adapter doesn't support schema guidance

**Per-target status:**
- **GREEN**: All fixtures PASS
- **YELLOW**: Some fixtures REPAIRED or NONENFORCEABLE
- **RED**: Any fixture FAIL

---

## 3. Conformance Levels

PCSL defines progressive conformance levels:

### L1 – Structural Conformance
- JSON validity (`pc.check.json_valid`)
- Required field presence (`pc.check.json_required`)
- Token budget checks (`pc.check.token_budget`)

### L2 – Semantic Conformance
Includes L1 plus:
- Enum value validation (`pc.check.enum`)
- Regex pattern assertions (`pc.check.regex_absent`, `pc.check.regex_present`)
- JSONPath-based field checks

### L3 – Differential Conformance
Includes L2 plus:
- Multi-target execution with tolerance enforcement
- Pass-rate comparison across models/versions
- Latency budget validation (`pc.check.latency_budget`)

### L4 – Security Conformance (Planned)
Includes L3 plus:
- Jailbreak escape-rate metrics
- PII leakage detection
- Adversarial robustness checks

---

## 4. Built-in Check Types

### 4.1 `pc.check.json_valid`
Validates that the response is parseable JSON.

**Parameters:** None

**Example:**
```json
{ "type": "pc.check.json_valid" }
```

### 4.2 `pc.check.json_required`
Validates presence of required fields at the root level.

**Parameters:**
- `fields` (array of strings): Required field names

**Example:**
```json
{ "type": "pc.check.json_required", "fields": ["category", "priority"] }
```

### 4.3 `pc.check.enum`
Validates that a field (selected via JSONPath) has a value from an allowed set.

**Parameters:**
- `field` (string): JSONPath expression
- `allowed` (array): Allowed values

**Example:**
```json
{ "type": "pc.check.enum", "field": "$.priority", "allowed": ["low", "medium", "high"] }
```

### 4.4 `pc.check.regex_absent`
Fails if a regex pattern is found in the raw response.

**Parameters:**
- `pattern` (string): Regex pattern

**Example:**
```json
{ "type": "pc.check.regex_absent", "pattern": "```" }
```

### 4.5 `pc.check.token_budget`
Validates that the response does not exceed a token limit (approximated by word count in v0.1).

**Parameters:**
- `max_out` (integer): Maximum output tokens

**Example:**
```json
{ "type": "pc.check.token_budget", "max_out": 200 }
```

### 4.6 `pc.check.latency_budget`
Validates that the p95 latency across all fixtures stays within a threshold.

**Parameters:**
- `p95_ms` (integer): p95 latency in milliseconds

**Example:**
```json
{ "type": "pc.check.latency_budget", "p95_ms": 2000 }
```

---

## 5. Schema References

PCSL artefacts are validated using JSON Schema:

- **Prompt Definition:** `pcsl-pd.schema.json`
- **Expectation Suite:** `pcsl-es.schema.json`
- **Evaluation Profile:** `pcsl-ep.schema.json`

Each artefact SHOULD include a `$schema` field pointing to the canonical schema URL (or local file).

---

## 6. Versioning

PCSL follows Semantic Versioning (SemVer):
- **Patch** (0.1.x): Clarifications, non-breaking additions
- **Minor** (0.x.0): New check types, new fields (backward-compatible)
- **Major** (x.0.0): Breaking changes to artefact structure

The `pcsl` field in each artefact declares the spec version it targets.

---

## 7. Extensibility

Custom checks can be registered via the validator registry. Check types MUST use a namespaced identifier (e.g., `com.mycompany.check.custom_logic`).

---

## 8. Future Directions

- Multi-modal support (image, audio prompts)
- Advanced JSONPath/JSONLogic-based assertions
- Differential drift gates with statistical significance
- Integration with CI/CD (GitHub Actions, GitLab CI templates)
- Observability integration (OpenTelemetry export)

---

**End of PCSL v0.1 Specification**

