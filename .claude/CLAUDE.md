# Project: harness

Inherits user-global rules from `~/.claude/CLAUDE.md` (team rulebook, memory policy, generic workflows).

## Context
Take-home assignment — LLM/ML AI R&D Team, Q Team.
Building an LLM evaluation harness (Part B, Option 1) with a mock/dummy endpoint.

## Stack
- Language: Python 3
- Framework: CLI tool / small service
- LLM endpoint: mock/dummy (returns fixed or randomised string)
- Input format: JSONL test cases

## JIRA
- Project key: TW
- Instance: https://leonyap27.atlassian.net
- Auth method: rest-api — credentials in `.env` as `jira_api`
- Do NOT use MCP Atlassian tools for this project; use REST API v3 with Basic auth.
- Use TW-### issues for development work

## Git
- Remote: origin (no remote configured yet — add when repo is published)
- Default branch: `dev`
- Feature branches: `feat/TW-XXX-<slug>` or `fix/TW-XXX-<slug>`
- PR base: `dev`

## AgenticOps skill chain

JIRA skill chain (`/jira-plan`, `/jira-review`, `/jira-impl`, `/jira-test`, `/dfsl`), hooks, release
tooling, and usage tracking live in the **AgenticOps** plugin at `~/my_project/AgenticOps/`.

Run `AgenticOps/install.sh` to make all skills globally available and wire hooks.
Profile: `~/.claude-usage/leonyap27/rag_simulator/project.json`

## Project-specific notes

- This is an interview take-home: prioritise clarity, test coverage, and documented assumptions.
- Part A (system design) and Part C (opinion) are written answers; Part B is the implementation.
- Mock endpoint should return deterministic or randomised strings — no real LLM API key required.
- README must cover: what it does, how to run, what you'd add with more time.
