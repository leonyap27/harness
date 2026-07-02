# Part A – System Design: On-Prem RAG for Internal Document Q&A

> **Constraint summary:** on-prem only · no internet · GPU cluster shared across departments · ~2,000 docs, monthly refresh · 20 concurrent users · p95 latency target ≤ 3 s · small generalist team
>
> See [`assumptions.md`](assumptions.md) for all explicit assumptions.

---

## Architecture Overview

The system is a standard **Retrieval-Augmented Generation (RAG)** pipeline split into two paths: an offline batch ingestion path and an online query path.

```
┌─────────────────── OFFLINE (batch, monthly) ───────────────────┐
│                                                                  │
│  Document store ──► Parser ──► Chunker ──► Embedding model      │
│  (PDF/DOCX)         (text)    (512 tok    (CPU, on-prem)        │
│                               overlap 50) ──► Vector DB          │
│                                               (Chroma, local)    │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────── ONLINE (per query) ─────────────────────────┐
│                                                                  │
│  User ──► API Gateway ──► RAG Service                           │
│                           │                                      │
│                           ├── 1. Embed query (CPU, ~30 ms)      │
│                           ├── 2. Vector search top-K (Chroma)   │
│                           ├── 3. Build prompt                    │
│                           └── 4. Call LLM endpoint (GPU cluster) │
│                                  └──► Return answer to user      │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- **Document store** – shared network file system (NFS/SMB) holding the source files. No cloud storage — all data stays on-prem.
- **Parser** – extracts plain text from PDF/DOCX (PyMuPDF / python-docx). Runs on CPU in the batch job.
- **Chunker** – splits text into 512-token chunks with 50-token overlap. Preserves document ID and page number as metadata.
- **Embedding model** – a small bi-encoder (e.g., `all-MiniLM-L6-v2`) bundled and cached locally. No external API calls; the serving layer has no internet access. Runs on CPU; GPU not required for embedding at this scale.
- **Vector DB** – [Chroma](https://www.trychroma.com/) running as a persistent local server. Stores chunk embeddings plus metadata (source doc, page, last-updated timestamp).
- **RAG service** – a lightweight HTTP service (FastAPI) that handles the online query path: embed → retrieve → build prompt → call LLM → return.
- **LLM endpoint** – the existing GPU-cluster endpoint behind the API gateway. Not owned by this team.
- **Query cache** – optional in-memory LRU cache (or Redis if shared across RAG service replicas) keyed on query hash. Effective for FAQ-style repeated questions across departments.

---

## Key Decisions and Tradeoffs

### 1. Fixed-size chunking (chosen) vs. semantic / document-aware chunking

Fixed-size chunks (512 tokens, 50 overlap) are simple, fast, and predictable. Semantic chunking (split on paragraph or section boundaries, variable length) produces better retrieval quality for structured documents but requires per-format heuristics and significantly more ingestion complexity. Given monthly batch runs and a small team, simplicity wins for v1. The overlap mitigates the main failure mode (splitting a sentence across chunk boundaries).

### 2. Chroma (chosen) vs. Weaviate / Qdrant / pgvector

Chroma is deployable as a single process, requires minimal ops, and supports persistent local storage. Weaviate and Qdrant offer richer filtering, clustering, and horizontal scale — none of which are needed at 2,000 docs and 20 concurrent users. pgvector is viable if the team already runs PostgreSQL, but adds schema management overhead. For a no-dedicated-DevOps team, Chroma's operational simplicity is the deciding factor.

### 3. CPU embedding (chosen) vs. GPU embedding

Embedding a single 512-token query takes ~30–50 ms on a modern CPU. For 20 concurrent users this is well within the 3 s budget. Reserving GPU for the LLM keeps inference throughput high and avoids scheduling contention on the shared cluster. GPU embedding would only matter if query volume grew 10×+.

### 4. No fine-tuning (chosen not to do)

Fine-tuning the LLM on internal documents would improve factual grounding but requires GPU time, versioned training data, evaluation harness, and a promotion pipeline. RAG achieves the same grounding with lower cost and faster iteration: update the doc store, re-run ingestion, done. Fine-tuning is appropriate when the domain vocabulary is highly specialised and retrieval alone cannot bridge the gap.

### 5. No real-time indexing (chosen not to do)

A real-time pipeline (Kafka → index on doc upload) adds significant infrastructure complexity for marginal benefit when docs only change monthly. A scheduled batch job (e.g., nightly or triggered on upload) is sufficient.

### 6. No per-department ACL in v1 (chosen not to do)

Implementing document-level access control requires user identity propagation into the retrieval layer, which adds auth complexity. Assumption A10 treats departments as sharing a common corpus. If departments need isolation, the simplest path is separate Chroma collections per department, filtered at query time by a department ID in the API request.

---

## What I Would Monitor Post-Deployment

| Signal | Why | How |
|---|---|---|
| **Query latency (p50 / p95 / p99)** | Core SLA: "snappy" = p95 ≤ 3 s. Split by stage (embed / retrieve / LLM) to localise degradation. | Prometheus histogram on the RAG service |
| **LLM endpoint error rate and timeout rate** | The shared GPU endpoint is the highest-risk dependency. Timeouts will cascade to users. | HTTP client metrics + alerting |
| **Retrieval hit quality (top-K score distribution)** | Low cosine similarity scores indicate the query is out-of-distribution for the current index. | Log top-1 score per query; alert if median drops below threshold |
| **Vector DB index size** | Tracks ingestion health and catches runaway re-ingestion (duplicate chunks). | Chroma collection count metric |
| **Batch ingestion job success / duration** | Silent ingestion failures leave users querying stale data with no error signal. | Job exit code + duration logged to a file or a simple dashboard |
| **User feedback (thumbs up/down)** | The only ground-truth signal for answer quality. Even a simple binary rating surfaces systematic failures invisible to latency metrics. | In-app feedback button → append to a log file |

---

## One Failure Mode That Would Only Surface in Production

**Stale embeddings during partial re-ingestion**

During the monthly batch job, chunks are re-embedded and upserted into the vector DB incrementally — old chunks for unchanged documents are left in place, new/updated chunks are written. If the job fails halfway through (OOM, disk full, timeout), the index is left in a **mixed state**: some documents are at revision N+1, others are still at revision N.

A query that spans multiple documents will now retrieve chunks from different revision states, leading to contradictory answers (e.g., a policy doc says "14 days annual leave" while a superseded chunk says "12 days"). Neither the user nor the system will surface an error — the LLM will synthesise an answer from inconsistent context, often confidently.

This failure mode does not appear in development because the dev ingestion pipeline always runs to completion on a small fixture dataset. In production, large corpora and resource pressure make partial runs likely.

**Mitigation:** Treat each ingestion run as an atomic swap — write new chunks to a *staging* collection, validate chunk count and score distribution against the previous collection, then atomically rename/alias the collection. Expose the current collection version as a health endpoint so monitoring can detect a failed cutover.
