---
ticket: TW-8
type: business
tag: b
sprint: v0.1.0-TW-16
---

# TW-8 — Mock Endpoint and Evaluation Runner (Business)

## What this delivers

A working evaluation harness that can run a JSONL test suite against an LLM endpoint and produce a structured pass/fail report — with no external API key or cloud dependency required.

## User-facing outcome

A team member can now:

1. Write test cases in a simple text file (`id`, `input`, `expected` per line)
2. Run `harness data/test_cases.jsonl` to get a pass-rate summary, per-failure details, and anomaly flags
3. Reproduce the same run with `--seed 42` to compare results across model versions

## Why this matters for the assignment

The problem statement requires: runs each test case against the endpoint, scores responses, outputs a structured summary, and handles endpoint errors gracefully. All four requirements are now met.

## Scoring approach (business rationale)

The harness uses keyword overlap (Jaccard similarity) by default rather than exact string matching, because real LLM responses paraphrase — "You are entitled to 14 days of annual leave" should score as a pass against "14 days annual leave". This avoids false failures on correct but differently worded answers, which is the main source of noise in LLM eval results.

## What is not included

- No real HTTP endpoint is wired in (this is intentional per the assignment spec — a mock is sufficient)
- No semantic similarity scoring (would require an embedding model and dependencies)

## Status

READY TO DEPLOY. Tests pass. PR open for review at https://github.com/leonyap27/harness/pull/2.
