"""Scoring logic for the evaluation harness.

Two scorers are provided and justified:

1. exact_match   — strict string equality after normalisation.
                   Appropriate when the expected answer is a canonical phrase
                   (e.g. "14 days annual leave"). Zero tolerance for paraphrase.

2. keyword_overlap — Jaccard similarity on lowercased token sets.
                   Appropriate for longer answers where word-for-word match is
                   unrealistic but key terms should appear (e.g. policy IDs,
                   names, numbers). Threshold default is 0.5 (at least half the
                   expected tokens appear in the response).

The harness uses keyword_overlap as the primary scorer because it is more robust
to trivial phrasing variation without requiring an LLM judge.
"""

import re
from typing import NamedTuple


class Score(NamedTuple):
    passed: bool
    method: str
    score: float
    reason: str


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _tokenise(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def exact_match(response: str, expected: str) -> Score:
    """Return Score based on case-insensitive, whitespace-normalised equality."""
    match = _normalise(response) == _normalise(expected)
    return Score(
        passed=match,
        method="exact_match",
        score=1.0 if match else 0.0,
        reason="exact match" if match else f"got {response!r}, expected {expected!r}",
    )


def keyword_overlap(response: str, expected: str, threshold: float = 0.5) -> Score:
    """Return Score based on Jaccard token overlap between response and expected.

    Jaccard = |intersection| / |union|.  Pass when score >= threshold.
    """
    resp_tokens = _tokenise(response)
    exp_tokens = _tokenise(expected)

    if not exp_tokens:
        return Score(passed=True, method="keyword_overlap", score=1.0, reason="expected is empty")

    union = resp_tokens | exp_tokens
    intersection = resp_tokens & exp_tokens
    jaccard = len(intersection) / len(union) if union else 0.0

    passed = jaccard >= threshold
    missing = exp_tokens - resp_tokens
    reason = (
        "keyword overlap sufficient"
        if passed
        else f"score {jaccard:.2f} < threshold {threshold:.2f}; missing tokens: {sorted(missing)}"
    )
    return Score(passed=passed, method="keyword_overlap", score=round(jaccard, 4), reason=reason)
