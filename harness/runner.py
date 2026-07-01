"""Evaluation runner — runs loaded test cases against an endpoint and scores results."""

import logging
from dataclasses import dataclass, field
from typing import Callable, Optional

from harness.loader import TestCase
from harness.scorer import Score, keyword_overlap

logger = logging.getLogger(__name__)


@dataclass
class CaseResult:
    case_id: str
    input: str
    expected: str
    response: Optional[str]
    score: Optional[Score]
    error: Optional[str]

    @property
    def passed(self) -> bool:
        return self.score is not None and self.score.passed


@dataclass
class RunSummary:
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    results: list[CaseResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


def run_evaluation(
    cases: list[TestCase],
    endpoint: Callable[[str], str],
    scorer: Callable[[str, str], Score] = keyword_overlap,
) -> RunSummary:
    """Run all test cases against the endpoint.

    Each case is attempted independently — a failure or endpoint error does not
    stop the run. All results are captured and returned.

    Args:
        cases: List of TestCase objects.
        endpoint: Callable that takes a prompt string and returns a response string.
                  May raise any exception to signal an endpoint error.
        scorer: Callable(response, expected) → Score. Defaults to keyword_overlap.

    Returns:
        RunSummary with per-case results and aggregate statistics.
    """
    summary = RunSummary(total=len(cases))

    for case in cases:
        logger.debug("running case %s", case.id)
        try:
            response = endpoint(case.input)
            score = scorer(response, case.expected)
            result = CaseResult(
                case_id=case.id,
                input=case.input,
                expected=case.expected,
                response=response,
                score=score,
                error=None,
            )
            if score.passed:
                summary.passed += 1
            else:
                summary.failed += 1
                logger.warning("case %s FAILED: %s", case.id, score.reason)
        except Exception as exc:
            logger.error("case %s ERROR: %s", case.id, exc)
            result = CaseResult(
                case_id=case.id,
                input=case.input,
                expected=case.expected,
                response=None,
                score=None,
                error=str(exc),
            )
            summary.errors += 1

        summary.results.append(result)

    return summary


def format_summary(summary: RunSummary) -> str:
    """Render a human-readable summary string from a RunSummary."""
    lines: list[str] = [
        "=" * 60,
        f"EVAL SUMMARY  total={summary.total}  passed={summary.passed}  "
        f"failed={summary.failed}  errors={summary.errors}  "
        f"pass_rate={summary.pass_rate:.1%}",
        "=" * 60,
    ]

    failures = [r for r in summary.results if not r.passed]
    if failures:
        lines.append("\nFAILURES / ERRORS:")
        for r in failures:
            if r.error:
                lines.append(f"  [{r.case_id}] ENDPOINT ERROR: {r.error}")
            else:
                lines.append(
                    f"  [{r.case_id}] score={r.score.score:.4f}  {r.score.reason}"
                )
                lines.append(f"           input:    {r.input!r}")
                lines.append(f"           expected: {r.expected!r}")
                lines.append(f"           got:      {r.response!r}")

    anomalies = _detect_anomalies(summary)
    if anomalies:
        lines.append("\nANOMALIES:")
        for a in anomalies:
            lines.append(f"  {a}")

    return "\n".join(lines)


def _detect_anomalies(summary: RunSummary) -> list[str]:
    """Flag unusual patterns in the run results."""
    anomalies: list[str] = []

    if summary.errors == summary.total:
        anomalies.append("all cases returned endpoint errors — endpoint may be down")
    elif summary.errors > summary.total * 0.5:
        anomalies.append(
            f"high error rate ({summary.errors}/{summary.total}) — check endpoint stability"
        )

    responses = [r.response for r in summary.results if r.response is not None]
    if len(set(responses)) == 1 and len(responses) > 1:
        anomalies.append(
            f"all responses identical ({responses[0]!r}) — endpoint may be returning a fixed stub"
        )

    return anomalies
