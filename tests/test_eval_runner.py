"""Smoke tests for TW-8 acceptance criteria.

AC1 -- each test case is sent to the endpoint
AC2 -- endpoint failure is handled gracefully (no crash)
AC3 -- run continues even if one case fails
"""

from harness.loader import TestCase
from harness.mock_endpoint import call_endpoint
from harness.runner import run_evaluation


def _cases(n: int = 3) -> list[TestCase]:
    return [TestCase(id=f"q{i}", input=f"input {i}", expected=f"expected {i}") for i in range(n)]


def test_all_cases_sent_to_endpoint():
    """AC1 -- every case is dispatched to the endpoint callable."""
    calls: list[str] = []

    def recording_endpoint(prompt: str) -> str:
        calls.append(prompt)
        return "some response"

    cases = _cases(4)
    run_evaluation(cases, endpoint=recording_endpoint)
    assert len(calls) == 4
    assert calls == [c.input for c in cases]


def test_endpoint_failure_does_not_raise():
    """AC2 -- endpoint errors are captured; the harness does not crash."""
    def always_fails(prompt: str) -> str:
        raise ConnectionError("endpoint down")

    summary = run_evaluation(_cases(2), endpoint=always_fails)
    assert summary.errors == 2
    for r in summary.results:
        assert r.error is not None
        assert r.response is None


def test_run_continues_after_one_failure():
    """AC3 -- remaining cases are still executed after a single failure."""
    call_count = 0

    def flaky(prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("first call fails")
        return "some response"

    cases = _cases(3)
    summary = run_evaluation(cases, endpoint=flaky)
    assert call_count == 3, "all cases must be attempted despite one error"
    assert summary.errors == 1


def test_mock_endpoint_returns_non_empty_string():
    """Basic smoke -- mock endpoint always returns a string."""
    result = call_endpoint("What is the leave policy?", mode="fixed")
    assert isinstance(result, str) and result
