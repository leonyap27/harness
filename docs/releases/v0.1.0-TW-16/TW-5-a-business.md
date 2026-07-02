---
ticket: TW-5
type: business
tag: a
version: 0.1.0
tracker: TW-16
---

**Size: S**

## TW-5 — Project can now be installed and explored

### What changed

Before this ticket, the repository was an empty shell with no installable code, no test setup, and no sample data. After this ticket, anyone who clones the repo can install the project with a single command and immediately begin exploring it — without needing to hunt for sample inputs or figure out the folder structure.

---

### What operators can do now

| Capability | Before TW-5 | After TW-5 |
|---|---|---|
| Install the project | Not possible — no `pyproject.toml` | `pip install -e .` installs cleanly with pinned dependencies |
| Run the test suite | Not possible — no `tests/` directory | `pytest` runs without errors |
| Inspect sample inputs | Not possible — no sample data | 4 ready-to-use JSONL files in `sample_data/` covering typical and edge-case prompts |
| Inspect output files | Not possible — no `outputs/` directory | `outputs/` folder is tracked in git and ready to receive results |
| Understand project structure | Not possible — no README | `README.md` covers purpose, folder layout, install, and run instructions |

---

### What the sample data covers

Four JSONL input files are included so the project can be exercised immediately after install:

| File | Contents |
|---|---|
| `sample_data/normal_policy.jsonl` | 2 standard leave-policy questions with expected answers |
| `sample_data/normal_travel.jsonl` | 2 standard travel-claim questions with expected answers |
| `sample_data/edge_long_prompt.jsonl` | 1 very long prompt — tests harness behaviour with large inputs |
| `sample_data/edge_empty_expected.jsonl` | 1 case with an empty expected field — tests harness handling of missing ground truth |

---

### Caveats

The CLI entry point is a placeholder and will be filled in once TW-7 (CLI implementation) is complete. The `README.md` notes this explicitly. All other install and test steps work end-to-end as of this ticket.
