# LLM Evaluation Harness

A lightweight CLI tool for running structured test cases against an LLM endpoint, scoring responses, and producing a structured summary report.

Built for the Q Team take-home assignment (Part B, Option 1).

---

## What it does

- Loads test cases from a JSONL file (one JSON object per line: `id`, `input`, `expected`)
- Runs each test case against a configurable LLM endpoint (or a built-in mock that returns deterministic/random strings)
- Scores each response using a pluggable scoring strategy (exact match, keyword overlap, or fuzzy similarity)
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
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Requires Python 3.11+. No external API key needed — the mock endpoint is built in.

---

## How to run

```bash
# Run the harness against the built-in mock endpoint
harness run sample_data/normal_policy.jsonl

# Run against a real endpoint
harness run sample_data/normal_policy.jsonl --endpoint http://your-llm-host/v1/chat

# Specify scoring strategy (default: keyword_overlap)
harness run sample_data/normal_policy.jsonl --scorer exact_match

# Run tests
pytest tests/ -v
```

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

## What I'd add with more time

- **Semantic scoring** via sentence embeddings (cosine similarity) — avoids penalising correct paraphrases
- **Async runner** to parallelise requests against the endpoint for large test suites
- **CI integration** (GitHub Actions) to gate on pass-rate thresholds before deployment
- **HTML report** output as an alternative to the structured JSON summary
- **Retry logic** with exponential backoff for transient endpoint errors
