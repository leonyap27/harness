**Size: M**

## TW-11 — Write README and Part C answer

### What changed

This ticket made the project submittable and reviewer-friendly. It fixed a bug that was silently preventing the tool from running, corrected the documentation so a reviewer can actually follow the instructions, and added a written answer demonstrating how to diagnose failures in a real retrieval-augmented generation system.

---

### Why it matters

A reviewer picking up this project for the first time relies entirely on the README to understand what the tool does and how to run it. Before this change, following the documented commands would have produced an error — the CLI entry point was broken at the import level, and the example commands referenced flags that do not exist. This would have made the project appear non-functional even though the underlying evaluation logic was complete and tested.

After this change:

- The tool runs as documented with a single command.
- The README explains scoring, error handling, and all available options without requiring the reader to read source code.
- The written investigation answer (Part C) demonstrates structured technical thinking about a real-world RAG failure scenario.

---

### Before / after

| Aspect | Before | After |
|--------|--------|-------|
| Running the CLI | Failed immediately with an import error | Works: `python3 -m harness.main <file>` |
| README accuracy | Contained non-existent subcommand and flag | All examples verified correct |
| Scoring explanation | Not documented | Jaccard formula and pass threshold explained |
| Error handling | Not documented | Exit codes, per-case error capture, and anomaly detection explained |
| Part C answer | File did not exist | `docs/part_c_investigation.md` written (~270 words, three specific methods) |

---

### What a reviewer can now do

- Clone the repo and run the tool successfully on the first attempt using only the README.
- Understand how the scorer decides pass/fail without reading source code.
- Read a concrete, method-specific answer to the "how would you investigate a RAG failure" question — covering index freshness, retrieval quality metrics, and chunking issues with named tools and metrics.

---

### Caveats

- The tool uses a mock endpoint, not a real language model — this is by design for the take-home assignment. The README makes this explicit.
- The Part C answer is intentionally scoped to the first three investigation steps; a real incident would involve additional layers (re-ranker tuning, query reformulation, etc.).
