**Size: M**

## TW-7 — Build JSONL test loader

### What changed

The evaluation harness can now read test cases from a file. Before this release, there was no way to supply questions and expected answers to the tool — it had no input mechanism at all. Now, operators prepare a plain-text file where each line is one test case, and the harness loads it automatically before running evaluations.

---

### What operators can do now

- **Supply test cases in a standard format.** Each line in the input file contains a question ID, the question text, and the expected answer. The harness reads the file and validates every record before any evaluation runs.
- **Receive clear error messages when the file is wrong.** If a line cannot be parsed (e.g. truncated or corrupted), the harness reports exactly which line failed. If a record is missing a required field, the harness names the field and the record — no silent failures.
- **Run a reliable test suite.** The loader is covered by 12 automated tests. Valid input loads cleanly; bad input is caught before any evaluation work is done.

---

### Before/after

| Capability | Before | After |
|-----------|--------|-------|
| Load test cases from a file | Not possible | Supported — JSONL format, one record per line |
| Validate input before evaluation | Not possible | All three required fields checked on every record |
| Error feedback on bad input | None | Clear message with line number or missing field name |

---

### Caveats / known gaps

The loader reads the file in full before returning. Very large input files (tens of thousands of records) will hold all records in memory simultaneously. This is acceptable for the current take-home scope but would need attention before production use.
