**Size: L**

## TW-9 — Build scoring and summary report

### What changed

The evaluation harness can now run end-to-end. You provide a file of test questions with expected answers, and the tool automatically scores every response, flags problems, and saves a report you can inspect or share.

Before this change, there was no way to run the harness and get a result. After this change, a single command produces a complete scored summary.

---

### What operators / users can do now

| Capability | How to use it |
|------------|---------------|
| Run a scored evaluation | `python -m harness.main tests.jsonl` |
| Choose the scoring method | Add `--scorer exact_match` for strict matching, or omit (default is keyword overlap) |
| Simulate endpoint failures | Add `--fail-rate 0.1` to model 10% endpoint errors |
| Save a machine-readable report | Add `--output report.json` |
| Control the mock endpoint mode | Add `--mode fixed`, `--mode random`, or `--mode echo` |

---

### Before / after

| Aspect | Before | After |
|--------|--------|-------|
| Running the harness | Not possible — no entry point existed | `python -m harness.main <file>` |
| Scoring | No scoring logic | Two methods: exact match (strict) and keyword overlap (Jaccard, default) |
| Seeing failures | Not possible | Failures listed with score and reason in stdout summary |
| Endpoint errors | Not tracked | Counted separately; anomalies (high error rate, stuck responses) flagged automatically |
| Output format | None | Human-readable stdout summary + optional JSON report file |

---

### Caveats and known gaps

- The harness uses a **mock endpoint** — it does not call a real language model. The mock returns fixed, random, or echo responses. Results reflect how the scorer behaves, not a real model's quality.
- The keyword-overlap scorer passes a response if at least half the expected-answer tokens appear anywhere in the response. This is intentional: it tolerates natural phrasing variation while still catching clearly wrong answers.
- A pass rate of 20% on the included smoke-test data is expected — the mock endpoint returns a fixed stub answer that only matches one of five test cases.
