# LLM Evaluation Harness

A lightweight CLI tool for running a test suite against an LLM endpoint and scoring the responses.

Built for Part B (Option 1) of the Deployment Team take-home assignment. A mock endpoint is included so no API key is required.

## What it does

1. Reads test cases from a JSONL file (`id`, `input`, `expected` fields)
2. Sends each `input` to the mock LLM endpoint
3. Scores the response against `expected` using Jaccard keyword overlap (or exact match)
4. Outputs a structured summary: pass rate, failures with reasons, anomaly detection
5. Optionally writes full results to a JSON file

## How to run

**Prerequisites:** Python 3.11+

```bash
# Install (editable)
pip install -e .

# Run against the sample test cases
harness data/test_cases.jsonl

# Reproducible run with a fixed seed
harness data/test_cases.jsonl --seed 42

# Exact-match scoring
harness data/test_cases.jsonl --scorer exact_match

# Simulate 20% endpoint failure rate
harness data/test_cases.jsonl --fail-rate 0.2

# Write full results to JSON
harness data/test_cases.jsonl --output results.json
```

**Run tests:**

```bash
pip install pytest
pytest
```

## Scoring approach

Two scorers are available:

| Scorer | Method | When to use |
|---|---|---|
| `keyword_overlap` (default) | Jaccard similarity on token sets | Responses may paraphrase but should contain key terms |
| `exact_match` | Case-insensitive, whitespace-normalised equality | Expected answer is a canonical phrase |

Jaccard threshold defaults to 0.5 (at least half the expected tokens present). This tolerates natural phrasing variation without requiring an LLM-as-judge, which keeps the harness dependency-free.

## Project structure

```
harness/
  __init__.py
  loader.py          -- JSONL loader and TestCase dataclass
  mock_endpoint.py   -- mock LLM (fixed/random/echo modes, configurable fail_rate)
  runner.py          -- run_evaluation() loop with per-case error isolation
  scorer.py          -- exact_match and keyword_overlap scorers
  main.py            -- CLI (argparse)
data/
  test_cases.jsonl   -- sample test cases
tests/
  test_loader.py     -- tests for JSONL loading and validation
  test_eval_runner.py -- tests for AC1/AC2/AC3 of the runner
fixtures/
  valid.jsonl / bad_json.jsonl / missing_field.jsonl
```

## What I would add with more time

- **Real endpoint adapter**: an `http_endpoint(url, headers)` factory so the same harness works against a live API, not just the mock.
- **Semantic similarity scorer**: cosine similarity of sentence embeddings for answers where keyword overlap is too coarse (e.g. "I need 2 weeks off" vs "14 days annual leave").
- **Parallel execution**: `asyncio`/`ThreadPoolExecutor` so endpoint calls run concurrently -- matters when testing hundreds of cases against a slow endpoint.
- **Retry logic**: exponential backoff on transient errors before marking a case as failed.
- **HTML/CSV report**: human-readable output for non-technical stakeholders.
