---
ticket: TW-8
type: technical
tag: b
sprint: v0.1.0-TW-16
---

# TW-8 — Mock Endpoint and Evaluation Runner (Technical)

## What changed

Added four new modules that together form the core of the LLM evaluation harness:

| File | Role |
|---|---|
| `harness/mock_endpoint.py` | Mock LLM endpoint — returns seeded-random or fixed canned responses; supports configurable `fail_rate` for error-path testing |
| `harness/scorer.py` | Two scorers: `exact_match` (normalised string equality) and `keyword_overlap` (Jaccard similarity on token sets, threshold 0.5) |
| `harness/runner.py` | `run_evaluation()` — iterates test cases, wraps each endpoint call in `try/except`, accumulates `CaseResult` objects; `format_summary()` with anomaly detection |
| `harness/main.py` | `argparse` CLI entry point registered as the `harness` console script |

Also adds `data/test_cases.jsonl` (5 sample HR-policy cases), `pyproject.toml`, and `README.md`.

Builds on TW-7's `harness/loader.py`; `runner.py` imports `TestCase` from `harness.loader`.

## Architecture notes

### Mock endpoint (`mock_endpoint.py`)

```python
call_endpoint(prompt, mode="random", seed=None, fail_rate=0.0)
```

- `mode="random"` + `seed` → deterministic output per seed (reproducible test runs)
- `mode="fixed"` → always returns the first canned response (useful for baseline scoring)
- `mode="echo"` → returns the prompt verbatim (useful for exact-match tests)
- `fail_rate` → probability [0, 1] of raising `RuntimeError` to simulate endpoint errors

### Scorer choice rationale

`keyword_overlap` (Jaccard) is the default because:
- HR-policy answers paraphrase: "You are entitled to 14 days" ≠ "14 days annual leave" under exact_match but shares enough tokens
- Threshold 0.5 means at least half the expected tokens must appear — loose enough for natural variation, strict enough to catch hallucinations
- Zero external dependencies; fast enough for hundreds of cases per second

`exact_match` is available via `--scorer exact_match` for canonical short answers.

### Error isolation in `run_evaluation()`

Each case runs in an independent `try/except`. On exception:
- `CaseResult.error` is set to the exception message
- `CaseResult.response = None`, `CaseResult.score = None`
- `RunSummary.errors += 1`
- Loop continues to the next case

This satisfies AC2 (graceful handling) and AC3 (run continues).

### Anomaly detection

`_detect_anomalies()` flags:
- All cases errored → "endpoint may be down"
- Error rate > 50% → "check endpoint stability"
- All responses identical → "endpoint may be returning a fixed stub"

## Test coverage

```
pytest tests/test_eval_runner.py -v
4 passed — AC1, AC2, AC3, basic mock smoke
```

Full suite: 16 passed (4 new + 12 from TW-7 loader).

## CLI usage

```bash
pip install -e .
harness data/test_cases.jsonl --seed 42
harness data/test_cases.jsonl --scorer exact_match
harness data/test_cases.jsonl --fail-rate 0.2 --log-level DEBUG
harness data/test_cases.jsonl --output results.json
```

Exit code 0 = all cases passed; 1 = failures or errors present; 2 = input error.

## PR

[DFSL] TW-8 build mock endpoint and evaluation runner — https://github.com/leonyap27/harness/pull/2
