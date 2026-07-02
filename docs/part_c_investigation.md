# Part C – Investigation: Outdated or Irrelevant Answers

**Scenario:** Six months post-deployment, users report answers that are outdated or irrelevant even though source documents are correct and up to date.

---

## 1. Index staleness — reconciliation query

The most likely cause is the vector index lagging behind the monthly document refresh. I would run a reconciliation pass: compare each document's `last_modified` timestamp on the file system against the `indexed_at` field stored in chunk metadata at ingestion time. Any document where `indexed_at < last_modified` has stale embeddings. I would then inspect the batch job logs for the last three runs to confirm the job completed — a silent partial exit due to OOM or disk pressure is the most common culprit at this scale, and it leaves the index in a mixed-revision state with no visible error to the user.

## 2. Retrieval quality drift — Recall@k on a golden set

A shift in retrieval quality produces plausible-sounding but wrong answers even when the index is current. I would build a golden set of 20–30 query/passage pairs from known-correct answers at deployment time, then compute Recall@5 and NDCG@5 on the current index and compare against the baseline. If the metric dropped, I would check whether the embedding model binary or tokeniser changed since deployment — even a minor library upgrade can shift the embedding space enough to degrade retrieval without triggering any error.

## 3. Chunking or metadata filter mismatch — BM25 comparison

Relevant content may exist in the index but fail to surface due to chunk boundary errors or an overly restrictive metadata filter. I would run BM25 (via `rank-bm25`, no external dependencies) over the raw document text for the failing queries, then compare which passages rank highly against what the dense retriever returns. Passages that score well under BM25 but are absent from dense retrieval point to a chunking or embedding mismatch. I would also audit any department or date-range metadata filters applied at query time to confirm they are not inadvertently excluding valid documents.
