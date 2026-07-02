---
ticket: TW-6
type: business
tag: a
version: 0.1.0
tracker: TW-16
---

**Size: M**

## TW-6 — System Design Locked Down Before Build Begins

### What was delivered

The architecture and explicit assumptions for the on-premises document question-answering system are now written down and reviewed. Two documents were produced:

- **`docs/part_a_system_design.md`** — describes how the system is structured, why each major technology was chosen, what was deliberately left out of scope, what will be monitored in production, and the one failure mode that only emerges at production scale
- **`docs/assumptions.md`** — 12 numbered assumptions about the environment, documents, users, and team that fill gaps in the original brief

Both documents passed a full review pass against all acceptance criteria with no gaps found.

---

### Why this matters

Without an agreed design and explicit assumptions, the implementation sprint risks building the wrong thing — or building the right thing against wrong constraints (e.g., expecting internet access, expecting a dedicated DevOps team, or expecting real-time document updates when monthly batch is sufficient).

Locking down the design now means:

- The implementation team has a single reference document that answers "why did we choose X over Y" without reconstructing reasoning mid-sprint
- Any stakeholder disagreement about constraints (e.g., whether departments need separate access control) is surfaced before code is written, not after
- The monitoring plan is agreed upfront, so instrumentation is built in rather than retrofitted

---

### Scope boundary — what was deliberately left out

Three things were explicitly documented as out of scope for v1:

| Item | Why deferred |
|---|---|
| Fine-tuning the language model on internal documents | High cost in GPU time, training data curation, and evaluation infrastructure; RAG achieves equivalent grounding at lower cost |
| Real-time document indexing | Documents change monthly; the infrastructure complexity of a real-time pipeline is not justified by that frequency |
| Per-department access control | Not required in the brief; if departments need isolation in future, the design already names the lowest-complexity path (separate Chroma collections filtered by department ID) |

---

### Constraints the design is built around

The system is designed to work entirely on-premises with no internet access. It uses the existing GPU cluster only for language model inference (via an internal API gateway already in place). Everything else — document parsing, text chunking, embedding, and the retrieval service — runs on CPU and is operated by the same small team building it. The target response time is under 3 seconds at the 95th percentile for a corpus of roughly 2,000 documents and up to 20 simultaneous users.

---

### Status

Design and assumptions documents are complete and reviewed. The team is ready to begin implementation (Part B).
