# Assumptions – Part A System Design

These assumptions fill gaps in the brief. They are stated explicitly so that any mis-alignment with the real environment can be corrected before design decisions are locked in.

## Environment

| # | Assumption | Basis |
|---|---|---|
| A1 | The serving layer has **no internet access**. External APIs (OpenAI, Pinecone, HuggingFace Hub downloads) are unavailable at inference time. All models and dependencies must be bundled on-prem. | Brief states: *"no cloud or internet access from the serving layer."* |
| A2 | There is a **GPU cluster** reachable via an internal API gateway. The LLM is already deployed and accessible as an HTTP endpoint. We do not manage the LLM itself. | Brief states: *"GPU cluster behind an API gateway."* |
| A3 | The cluster has enough spare CPU capacity to run a small embedding model (e.g., `all-MiniLM-L6-v2`) offline during batch ingestion. GPU is reserved for the shared LLM endpoint. | Inference embedding on CPU is feasible for a batch of ≤2,000 docs; real-time embedding of a single query (~512 tokens) takes <50 ms on modern CPU. |

## Documents

| # | Assumption | Basis |
|---|---|---|
| A4 | Documents are in **PDF or DOCX format**. A text extraction step is needed before chunking. | Typical internal document formats; no format specified in the brief. |
| A5 | Documents are **single-language (English)**. No multilingual retrieval or translation is required. | Not specified; noting the assumption in case this is wrong. |
| A6 | The **~2,000 document** count refers to distinct files, not pages. Total corpus size is estimated at 5–50 million tokens (average 10–25 pages per document). | Conservative estimate for a government department's knowledge base. |
| A7 | Documents are **updated in batch, roughly monthly**. There is no real-time document stream. A scheduled re-ingestion job is acceptable. | Brief states: *"roughly 2,000 documents updated monthly."* |

## Users and Latency

| # | Assumption | Basis |
|---|---|---|
| A8 | **"Snappy"** is defined as **p95 end-to-end latency ≤ 3 seconds** for a typical query (retrieval + LLM generation). | Industry convention for conversational UX. Stated explicitly to make it measurable. |
| A9 | Peak load of **20 concurrent users** implies roughly 20–60 queries per minute at peak (assuming 1–3 queries per user per minute). | Conservative load estimate; small team deployment. |
| A10 | **Multi-department sharing** is assumed to be at the document level, not user-isolated. All departments share the same document index (one vector DB collection). If departments have separate document sets requiring access control, each gets its own collection — but that is a v2 concern. | Brief states: *"multiple departments share the same endpoint"*; no ACL requirement mentioned. |

## Team and Operations

| # | Assumption | Basis |
|---|---|---|
| A11 | The team will **own and operate** the RAG service, embedding pipeline, and vector database — not just the LLM. The team is small and generalist, so operational simplicity outweighs feature richness. | Brief states: *"engineers own what they build."* |
| A12 | **No dedicated CI/CD or container orchestration** (e.g., Kubernetes) is assumed. Docker Compose or a simple systemd service is the deployment target. | Follows from the no-dedicated-DevOps constraint. |
