**Size: M**

## TW-7 — Build JSONL test loader

**One-line summary:** Added `harness/loader.py` — a validated JSONL test-case loader with a typed `TestCase` dataclass and clear error messages for malformed input.

---

### Problem being solved

The evaluation harness had no mechanism to ingest test cases. Before this ticket, there was no way to supply structured inputs to the mock endpoint or validate that those inputs were well-formed. All three core acceptance criteria (valid load, bad JSON error, missing field error) were unimplemented.

---

### Architecture / Before and After

| Aspect | Before | After |
|--------|--------|-------|
| Test-case ingestion | Not present | `load_test_cases(path)` reads a JSONL file line-by-line |
| Input validation | Not present | Required fields (`id`, `input`, `expected`) checked on every record |
| Error reporting on bad JSON | Not present | `ValueError` raised with line number and raw line content |
| Error reporting on missing field | Not present | `ValueError` raised naming the missing field and the offending record ID |
| Data contract | None | `TestCase` dataclass enforces typed fields (`id: str`, `input: str`, `expected: str`) |

_Diagram omitted: single linear flow with no branching or actors — `load_test_cases()` reads a file, validates each line, and returns a list._

---

### File changes

| File | Change | Notes |
|------|--------|-------|
| `harness/__init__.py` | New | Package init — exposes `TestCase` and `load_test_cases` |
| `harness/loader.py` | New | Core loader: `TestCase` dataclass, `load_test_cases()`, field validation |
| `tests/__init__.py` | New | Test package init |
| `tests/test_loader.py` | New | 12 pytest cases covering all 3 acceptance criteria |
| `fixtures/valid.jsonl` | New | Valid test fixture — 3 well-formed records |
| `fixtures/bad_json.jsonl` | New | Malformed JSON fixture — triggers parse-error path |
| `fixtures/missing_field.jsonl` | New | Record missing `expected` field — triggers field-validation path |

---

### Risk and rollback

**Risk:** Low. This is a new module with no side-effects on existing code. No existing files were modified.

**Rollback:** Delete `harness/loader.py`, `harness/__init__.py`, and the `tests/` and `fixtures/` directories. No migration or data cleanup required.

---

### Test evidence

12/12 pytest cases pass on Python 3.14.2. Coverage spans:

- Happy path: valid JSONL file loads and returns a list of `TestCase` objects with correct field values.
- Bad JSON path: a file containing a malformed JSON line raises `ValueError` with a message that includes the line number.
- Missing field path: a record lacking the `expected` key raises `ValueError` that names the missing field.

Commit `20ba112` on branch `feat/TW-7-jsonl-loader`. PR #1 open as draft against `dev`.
