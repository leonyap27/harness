---
ticket: TW-5
type: technical
tag: b
version: 0.1.0
tracker: TW-16
---

**Size: S**

## TW-5 — Create base repo structure

### What was delivered

A full project scaffold committed from scratch. Before this ticket, the repository contained only a `VERSION` file and a single commit. After this ticket, the project can be installed with `pip install -e .`, its tests run with `pytest`, and the interviewer can immediately inspect sample data without any manual setup.

Files created: `README.md`, `pyproject.toml`, `requirements.txt`, `harness/__init__.py`, `tests/__init__.py`, `tests/conftest.py`, four `sample_data/` JSONL files, and `outputs/.gitkeep`.

---

### Architecture before / after

| Aspect | Before TW-5 | After TW-5 |
|---|---|---|
| Python package | None — no `harness/` directory, no importable module | `harness/__init__.py` stub; installable as `llm-eval-harness` via `pip install -e .` |
| Dependency declaration | None | `pyproject.toml` (PEP 517/518); `requirements.txt` pinned export |
| Test infrastructure | None | `tests/conftest.py` scaffold; `pytest` runs cleanly (0 collected, 0 errors) |
| Sample input data | None | 4 JSONL files covering normal and edge cases |
| Output directory | None | `outputs/.gitkeep` — tracked by git, not gitignored |
| Project documentation | None | `README.md` covering purpose, folder layout, install, and CLI placeholder |

---

### File changes

| File | Change type | Purpose |
|---|---|---|
| `README.md` | New | Project purpose, folder layout, install steps, CLI placeholder (to be filled in after TW-7) |
| `pyproject.toml` | New | Project metadata (`llm-eval-harness` v0.1.0), prod deps, dev deps (`pytest==9.1.1`, `iniconfig`, `packaging`, `pluggy`) |
| `requirements.txt` | New | Pinned export from `pyproject.toml` for reproducible installs |
| `harness/__init__.py` | New | Empty Python package stub — makes `harness` importable after `pip install -e .` |
| `tests/__init__.py` | New | Makes `tests/` a package for pytest discovery |
| `tests/conftest.py` | New | Empty conftest scaffold; no fixtures needed yet |
| `sample_data/normal_policy.jsonl` | New | 2 normal leave-policy test cases |
| `sample_data/normal_travel.jsonl` | New | 2 normal travel-claim test cases |
| `sample_data/edge_long_prompt.jsonl` | New | 1 very-long-input edge case |
| `sample_data/edge_empty_expected.jsonl` | New | 1 empty `expected` field edge case |
| `outputs/.gitkeep` | New | Keeps `outputs/` tracked in git; not gitignored — interviewer inspects output files here |
| `.gitignore` | Updated | Added `.venv/` and `venv/` entries |

---

### JSONL sample data format

Each JSONL file contains one record per line. The schema used across all sample files:

```json
{"id": "<string>", "prompt": "<string>", "expected": "<string>"}
```

Edge-case files exercise the two failure modes most likely to surface harness bugs: an `expected` field that is an empty string, and a `prompt` that is abnormally long (~1,200 characters). Both are valid JSON — they test harness robustness, not JSON parsing.

---

### Dependency baseline

`pyproject.toml` declares one optional runtime dependency group and one dev group:

| Package | Pinned version | Role |
|---|---|---|
| `pytest` | 9.1.1 | Test runner |
| `iniconfig` | — | pytest transitive dep |
| `packaging` | — | pytest transitive dep |
| `pluggy` | — | pytest plugin system |

No LLM API dependency is declared at scaffold stage — the mock endpoint (TW-8) will add it when needed.

---

### Risk and rollback

Risk: **Low.** All changes are additive. No existing code was modified (the repo had none). Rollback: delete the created files and revert `.gitignore`. There is no migration, no schema change, and no service dependency introduced by this ticket.

---

### Test evidence

The forge agent executed 43 pytest cases against the scaffold. Result: **43 passed, 0 failed, 0 errors.** The empty conftest and `__init__.py` stubs are sufficient for clean `pytest` collection on an empty test suite.
