# LLM Evaluation Harness

A lightweight CLI tool for running structured test cases against an LLM endpoint, scoring responses, and producing a structured summary report.

Built for the Q Team take-home assignment.

---

## Submission overview

| Part | Format | Location |
|---|---|---|
| **Part A** — On-prem RAG system design | Written | [docs/part_a_system_design.md](docs/part_a_system_design.md) |
| **Part B** — LLM evaluation harness | Code + CLI | This README |
| **Part C** — Investigation: outdated/irrelevant answers | Written | [docs/part_c_investigation.md](docs/part_c_investigation.md) |

---

## What it does (Part B)

- Loads test cases from a JSONL file (one JSON object per line: `id`, `input`, `expected`)
- Runs each test case against a configurable LLM endpoint (or a built-in mock that returns deterministic/random strings)
- Scores each response using a pluggable scoring strategy (exact match or keyword overlap — see [How scoring works](#how-scoring-works))
- Outputs a structured summary: pass rate, per-case results, failures with reasons, and any anomalies
- Handles endpoint errors (timeouts, HTTP errors, malformed responses) gracefully

---

## Project layout

```
.
├── harness/              # Core package
│   ├── main.py           # CLI entry point
│   ├── loader.py         # JSONL test case loader and validation
│   ├── runner.py         # Runs test cases against the endpoint
│   ├── scorer.py         # Scoring strategies
│   └── mock_endpoint.py  # Built-in mock endpoint (no API key needed)
├── tests/                # Pytest test suite
│   ├── conftest.py       # Shared fixtures and paths
│   ├── test_loader.py    # Loader unit tests
│   └── test_runner.py    # Runner and scorer tests
├── fixtures/             # Test fixture JSONL files (used by pytest)
├── sample_data/          # Ready-to-use JSONL test files for manual runs
│   ├── normal_policy.jsonl
│   ├── normal_travel.jsonl
│   ├── edge_long_prompt.jsonl
│   └── edge_empty_expected.jsonl
├── outputs/              # Evaluation run outputs (committed, not gitignored)
├── docs/                 # System design and assumptions (Part A)
├── pyproject.toml        # Package metadata and entry point
└── requirements.txt      # Pinned dev dependencies
```

---

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install the package and dev dependencies
pip install -e ".[dev]"

# 3. Confirm everything works
pytest tests/ -v            # expect: 43 passed
harness --help              # confirm the CLI is on your PATH
```

Requires Python 3.11+. No external API key needed — the mock endpoint is built in.

---

## End-to-end walkthrough

This is the fastest path from install to a real evaluation run.

**1. Pick a test file.** The repo ships with two sets:

| File | Purpose |
|---|---|
| `sample_data/normal_policy.jsonl` | Happy-path policy questions |
| `sample_data/normal_travel.jsonl` | Travel-claim questions |
| `sample_data/edge_long_prompt.jsonl` | Long inputs — stress-tests truncation |
| `sample_data/edge_empty_expected.jsonl` | Empty expected field — always scores pass |
| `data/test_cases.jsonl` | Full five-question HR policy suite |

**2. Run the harness.**

```bash
harness data/test_cases.jsonl
```

**3. Read the summary** (see [How to read the output](#how-to-read-the-output) below).

**4. Save full results for inspection.**

```bash
harness data/test_cases.jsonl --output my_run.json
```

**5. Try different scorers and modes** — see [How to run](#how-to-run) for all flags.

---

## How to run

```bash
# Run the harness against the built-in mock endpoint (random mode)
harness sample_data/normal_policy.jsonl

# Use exact-match scoring instead of the default keyword overlap
harness sample_data/normal_policy.jsonl --scorer exact_match

# Fixed response mode with a seed for reproducible runs
harness sample_data/normal_policy.jsonl --mode fixed --seed 42

# Simulate 20% endpoint failure rate (tests error handling)
harness sample_data/normal_policy.jsonl --fail-rate 0.2

# Write full JSON results to a file
harness sample_data/normal_policy.jsonl --output results.json

# Run tests
pytest tests/ -v
```

All options:

| Flag | Default | Description |
|---|---|---|
| `test_file` | *(required)* | Path to a `.jsonl` file |
| `--scorer` | `keyword_overlap` | `keyword_overlap` or `exact_match` |
| `--mode` | `random` | Mock response mode: `random`, `fixed`, or `echo` |
| `--seed` | `None` | RNG seed for reproducible random runs |
| `--fail-rate` | `0.0` | Probability `[0–1]` that a call raises a simulated error |
| `--output` | `None` | Write full JSON results to this path |
| `--log-level` | `WARNING` | `DEBUG`, `INFO`, `WARNING`, or `ERROR` |

---

## Sample test case format

Each line in a JSONL file is one test case:

```json
{"id": "q1", "input": "What is the leave policy?", "expected": "14 days annual leave"}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier for the test case |
| `input` | string | Prompt sent to the LLM endpoint |
| `expected` | string | Expected response (used for scoring) |

See [`sample_data/`](sample_data/) for ready-to-use examples.

---

## How to read the output

A typical run prints:

```
============================================================
EVAL SUMMARY  total=5  passed=1  failed=4  errors=0  pass_rate=20.0%
============================================================

FAILURES / ERRORS:
  [q2] score=0.0000  score 0.00 < threshold 0.50; missing tokens: ['direct', 'manager']
           input:    'Who approves travel claims?'
           expected: 'Direct manager'
           got:      'Medical certificates must be submitted within 3 working days'

ANOMALIES:
  all responses identical ('14 days annual leave') — endpoint may be returning a fixed stub
```

| Section | What it means |
|---|---|
| `total / passed / failed / errors` | `errors` = endpoint threw an exception; `failed` = ran but scored below threshold |
| `score=0.00 < threshold 0.50` | Jaccard overlap between response and expected tokens — 0 = no shared words, 1 = exact |
| `missing tokens: [...]` | Words in the expected answer that are absent from the response |
| `ANOMALIES` | Automatic sanity checks: all-errors (endpoint down?), all-identical (stuck stub?) |

With `--output results.json` you get the same data as machine-readable JSON, one object per case, plus `pass_rate` at the top level. Useful for CI thresholds or post-run analysis.

Exit codes: `0` = all passed · `1` = at least one failure or error · `2` = bad input file.

---

## How to add custom evaluation

### A. Custom test cases (no code needed)

Create any `.jsonl` file with three fields per line and pass it directly:

```jsonl
{"id": "leave-01", "input": "How many days of annual leave do I get?", "expected": "14 days annual leave"}
{"id": "travel-01", "input": "Who approves my travel claim?", "expected": "Direct manager"}
```

```bash
harness my_cases.jsonl
```

### B. Custom endpoint (point at a real LLM)

The `call_endpoint` function in `harness/mock_endpoint.py` is the only place the harness talks to a model. Swap it out in `main.py`, or call `run_evaluation()` directly from your own script:

```python
import requests
from harness.loader import load_test_cases
from harness.runner import run_evaluation, format_summary

def my_endpoint(prompt: str) -> str:
    resp = requests.post(
        "http://your-llm-host/v1/chat",
        json={"prompt": prompt},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["response"]

cases = load_test_cases("my_cases.jsonl")
summary = run_evaluation(cases, endpoint=my_endpoint)
print(format_summary(summary))
```

### C. Custom scorer

Implement a function with the signature `(response: str, expected: str) -> Score` and pass it to `run_evaluation()`:

```python
from harness.scorer import Score
from harness.runner import run_evaluation

def semantic_match(response: str, expected: str) -> Score:
    # e.g. cosine similarity via sentence-transformers
    score = my_embedding_similarity(response, expected)
    passed = score >= 0.7
    return Score(passed=passed, method="semantic", score=score,
                 reason="semantic similarity" if passed else f"similarity {score:.2f} < 0.70")

summary = run_evaluation(cases, endpoint=my_endpoint, scorer=semantic_match)
```

The built-in scorers in `harness/scorer.py` follow the same pattern and are good reference implementations.

---

## How scoring works

Two built-in scorers are available. Both normalise text (lowercase, collapsed whitespace) before comparing.

**`keyword_overlap`** (default) — Jaccard similarity on token sets.

```
score = |tokens(response) ∩ tokens(expected)| / |tokens(response) ∪ tokens(expected)|
```

A case passes when `score >= 0.5`. Appropriate for policy-style answers where word-for-word match is unrealistic but key terms (numbers, names, IDs) should appear.

**`exact_match`** — case-insensitive, whitespace-normalised string equality. Score is `1.0` (pass) or `0.0` (fail). Use when the expected answer is a short canonical phrase and paraphrase is unacceptable.

Select with `--scorer exact_match`. To add a custom scorer, implement `(response: str, expected: str) -> Score` and pass it directly to `run_evaluation()`.

---

## How errors are handled

The harness treats every failure as a data point rather than a crash:

- **Malformed JSONL** — the loader raises `ValueError` with the line number and field name before any cases run. The CLI prints the error and exits with code `2`.
- **Missing file** — `FileNotFoundError` is raised immediately on load. Same exit path.
- **Endpoint error** (any exception during a call) — the case is recorded as an error (`response=None`, `error=<message>`). The remaining cases continue to run.
- **Anomaly detection** — after the run, the summary flags: all-cases-errored (endpoint likely down) and all-responses-identical (endpoint may be returning a fixed stub).

Exit codes: `0` = all passed, `1` = at least one failure or error, `2` = input error (bad file, bad JSON).

---

## What I'd add with more time

- **Semantic scoring** via sentence embeddings (cosine similarity) — avoids penalising correct paraphrases
- **Async runner** to parallelise requests against the endpoint for large test suites
- **CI integration** (GitHub Actions) to gate on pass-rate thresholds before deployment
- **HTML report** output as an alternative to the structured JSON summary
- **Retry logic** with exponential backoff for transient endpoint errors
