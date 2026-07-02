**Size: S**

## TW-10 — Add unit tests for scorer, runner, and mock endpoint

### Summary

Added 27 unit tests covering `harness.scorer`, `harness.mock_endpoint`, and `harness.runner`. Combined with the 12 pre-existing tests in `tests/test_loader.py`, the suite now contains 39 tests and all pass under pytest.

### File changes

| File | Change |
|---|---|
| `tests/test_runner.py` | New — 27 tests across scorer, mock endpoint, and runner modules |

### What was covered

**`harness.scorer`**
- `exact_match`: correct on identical strings, false on case mismatch
- `keyword_overlap`: threshold boundary (at-threshold passes, below fails), empty expected list edge case

**`harness.mock_endpoint`**
- `call_endpoint` in `fixed` mode: returns configured static string
- `call_endpoint` in `echo` mode: returns the prompt unchanged
- `call_endpoint` in `random` mode: returns a non-empty string
- `call_endpoint` with `bogus` mode: raises or returns error sentinel
- `fail_rate` simulation: endpoint failure is captured without crashing the runner

**`harness.runner`**
- `run_evaluation` all-pass scenario: correct summary totals
- `run_evaluation` with endpoint error: error captured in result, evaluation continues for remaining cases
- `run_evaluation` run-continues-after-failure: no early exit on a single failed case
- `format_summary`: pass rate calculation, anomaly detection flag present in output

_Diagram omitted: single linear flow with no branching or actors._

### Risk and rollback

Low risk — tests are additive and do not alter production code paths. To roll back, delete `tests/test_runner.py`; all other behaviour is unchanged.
