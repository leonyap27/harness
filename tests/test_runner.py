"""Unit tests for the evaluation harness."""

from pathlib import Path

import pytest

from harness.loader import TestCase, load_test_cases
from harness.mock_endpoint import call_endpoint
from harness.runner import (
    CaseResult,
    RunSummary,
    format_summary,
    run_evaluation,
)
from harness.scorer import Score, exact_match, keyword_overlap


# ---------------------------------------------------------------------------
# scorer tests
# ---------------------------------------------------------------------------


class TestExactMatch:
    def test_identical_strings_pass(self):
        s = exact_match("14 days annual leave", "14 days annual leave")
        assert s.passed

    def test_case_insensitive(self):
        s = exact_match("Direct Manager", "direct manager")
        assert s.passed

    def test_whitespace_normalised(self):
        s = exact_match("  14  days  annual  leave  ", "14 days annual leave")
        assert s.passed

    def test_mismatch_fails(self):
        s = exact_match("30 days annual leave", "14 days annual leave")
        assert not s.passed
        assert s.score == 0.0


class TestKeywordOverlap:
    def test_full_overlap_passes(self):
        s = keyword_overlap("14 days annual leave", "14 days annual leave")
        assert s.passed
        assert s.score == 1.0

    def test_partial_overlap_above_threshold(self):
        s = keyword_overlap("You get 14 days of annual leave per year", "14 days annual leave", threshold=0.4)
        assert s.passed

    def test_no_overlap_fails(self):
        s = keyword_overlap("contact HR directly", "14 days annual leave")
        assert not s.passed

    def test_empty_expected_always_passes(self):
        s = keyword_overlap("anything", "")
        assert s.passed

    def test_threshold_boundary(self):
        # "cat dog" vs "cat" → union={cat,dog}, intersection={cat}, jaccard=0.5
        s = keyword_overlap("cat dog", "cat", threshold=0.5)
        assert s.passed
        s2 = keyword_overlap("cat dog", "cat", threshold=0.51)
        assert not s2.passed


# ---------------------------------------------------------------------------
# mock_endpoint tests
# ---------------------------------------------------------------------------


class TestMockEndpoint:
    def test_fixed_mode_returns_same_response(self):
        r1 = call_endpoint("any prompt", mode="fixed")
        r2 = call_endpoint("different prompt", mode="fixed")
        assert r1 == r2

    def test_echo_mode_returns_prompt(self):
        prompt = "What is the leave policy?"
        assert call_endpoint(prompt, mode="echo") == prompt

    def test_random_mode_with_seed_is_reproducible(self):
        r1 = call_endpoint("q", mode="random", seed=42)
        r2 = call_endpoint("q", mode="random", seed=42)
        assert r1 == r2

    def test_unknown_mode_raises_value_error(self):
        with pytest.raises(ValueError, match="unknown mode"):
            call_endpoint("q", mode="bogus")

    def test_fail_rate_1_always_raises(self):
        with pytest.raises(RuntimeError, match="simulated transient failure"):
            call_endpoint("q", fail_rate=1.0, seed=0)

    def test_fail_rate_0_never_raises(self):
        for _ in range(20):
            result = call_endpoint("q", mode="fixed", fail_rate=0.0)
            assert result


# ---------------------------------------------------------------------------
# load_test_cases tests
# ---------------------------------------------------------------------------


class TestLoadTestCases:
    def test_valid_jsonl(self, tmp_path: Path):
        f = tmp_path / "cases.jsonl"
        f.write_text(
            '{"id": "q1", "input": "hello", "expected": "world"}\n'
            '{"id": "q2", "input": "foo", "expected": "bar"}\n'
        )
        cases = load_test_cases(f)
        assert len(cases) == 2
        assert cases[0].id == "q1"

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_test_cases(tmp_path / "nonexistent.jsonl")

    def test_malformed_json_raises_value_error(self, tmp_path: Path):
        f = tmp_path / "bad.jsonl"
        f.write_text('{"id": "q1", broken\n')
        with pytest.raises(ValueError, match="invalid JSON"):
            load_test_cases(f)

    def test_missing_key_raises_value_error(self, tmp_path: Path):
        f = tmp_path / "missing.jsonl"
        f.write_text('{"id": "q1", "input": "hello"}\n')
        with pytest.raises(ValueError, match="missing required keys"):
            load_test_cases(f)

    def test_empty_file_raises_value_error(self, tmp_path: Path):
        f = tmp_path / "empty.jsonl"
        f.write_text("")
        with pytest.raises(ValueError, match="no test cases"):
            load_test_cases(f)

    def test_blank_lines_skipped(self, tmp_path: Path):
        f = tmp_path / "blanks.jsonl"
        f.write_text(
            '\n{"id": "q1", "input": "x", "expected": "y"}\n\n'
        )
        cases = load_test_cases(f)
        assert len(cases) == 1


# ---------------------------------------------------------------------------
# run_evaluation tests
# ---------------------------------------------------------------------------


class TestRunEvaluation:
    def _make_cases(self, n: int = 3) -> list[TestCase]:
        return [TestCase(id=f"q{i}", input=f"input {i}", expected=f"expected {i}") for i in range(n)]

    def test_all_pass_when_endpoint_echoes_expected(self):
        cases = self._make_cases()
        summary = run_evaluation(
            cases,
            endpoint=lambda p: cases[int(p.split()[-1])].expected,
            scorer=exact_match,
        )
        assert summary.passed == 3
        assert summary.errors == 0

    def test_endpoint_error_captured_not_raised(self):
        def bad_endpoint(prompt: str) -> str:
            raise ConnectionError("endpoint down")

        cases = self._make_cases(2)
        summary = run_evaluation(cases, endpoint=bad_endpoint)
        assert summary.errors == 2
        assert summary.passed == 0
        for r in summary.results:
            assert r.error is not None

    def test_run_continues_after_single_failure(self):
        call_count = 0

        def flaky_endpoint(prompt: str) -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("first call fails")
            return "some response"

        cases = self._make_cases(3)
        summary = run_evaluation(cases, endpoint=flaky_endpoint)
        assert call_count == 3  # all three were attempted despite first error
        assert summary.errors == 1

    def test_summary_totals_are_consistent(self):
        cases = self._make_cases(5)
        summary = run_evaluation(cases, endpoint=lambda p: "wrong answer")
        assert summary.total == 5
        assert summary.passed + summary.failed + summary.errors == 5


# ---------------------------------------------------------------------------
# format_summary tests
# ---------------------------------------------------------------------------


class TestFormatSummary:
    def test_includes_pass_rate(self):
        summary = RunSummary(total=4, passed=3, failed=1, errors=0)
        summary.results.append(
            CaseResult("q1", "i", "e", "r", Score(False, "kw", 0.2, "low overlap"), None)
        )
        text = format_summary(summary)
        assert "75.0%" in text

    def test_anomaly_all_errors_detected(self):
        summary = RunSummary(total=2, passed=0, failed=0, errors=2)
        summary.results.extend([
            CaseResult("q1", "i", "e", None, None, "err"),
            CaseResult("q2", "i", "e", None, None, "err"),
        ])
        text = format_summary(summary)
        assert "ANOMALIES" in text
        assert "all cases returned endpoint errors" in text
