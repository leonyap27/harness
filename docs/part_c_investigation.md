# Part C – Investigation: Outdated or Irrelevant Answers

**Scenario:** Six months post-deployment, users report answers that are outdated or irrelevant even though source documents are correct and up to date.

---

## 1. Index freshness / version mismatch

The vector index may not reflect the latest document versions. I would run a reconciliation query comparing each document's `last_modified` timestamp in the source store against its `indexed_at` metadata field in the vector database (supported natively in Weaviate, Qdrant, and Pinecone). Any document where `indexed_at < last_modified` is stale. From there I would check the ingestion pipeline — specifically whether the scheduled re-embedding job is firing, succeeding, and committing. A silent failure in the pipeline (no alerting on non-zero exit) is the most common culprit.

## 2. Retrieval quality regression

The embedding model or its configuration may have drifted from the baseline. I would compute Recall@k and NDCG@k on a held-out golden set (query → relevant document pairs assembled at deployment time) and compare against the deployment-day baseline. If the metric has dropped, the next step is to diff the embedding model checkpoint and re-embed a sample corpus with the original model version to isolate whether the regression is in the model or in a preprocessing change (tokenisation, normalisation, truncation length).

## 3. Chunking or metadata filtering issue

Relevant content may exist in the index but not be retrieved due to chunk boundary problems or overly restrictive metadata filters. I would run BM25 (e.g., Elasticsearch or rank-bm25) over the raw documents for the same queries and compare which passages surface versus what the dense retriever returns. Passages that score high in BM25 but low in dense retrieval indicate a chunking or embedding mismatch. Separately, I would audit any department- or date-range metadata filters applied at query time to confirm they are not inadvertently excluding valid documents.
