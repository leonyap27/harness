from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from harness.loader import TestCase, load_test_cases


FIXTURES = Path(__file__).parent.parent / "fixtures"


# ---------------------------------------------------------------------------
# AC1 — Valid JSONL loads successfully
# ---------------------------------------------------------------------------

def test_valid_jsonl_returns_all_cases():
    cases = load_test_cases(FIXTURES / "valid.jsonl")

    assert len(cases) == 2
    assert all(isinstance(c, TestCase) for c in cases)


def test_valid_jsonl_preserves_field_values():
    cases = load_test_cases(FIXTURES / "valid.jsonl")

    assert cases[0].id == "q1"
    assert cases[0].input == "What is the leave policy?"
    assert cases[0].expected == "14 days annual leave"

    assert cases[1].id == "q2"
    assert cases[1].input == "Who approves travel claims?"
    assert cases[1].expected == "Direct manager"


def test_empty_lines_are_skipped(tmp_path: Path):
    f = tmp_path / "with_blanks.jsonl"
    f.write_text(
        '\n{"id": "q1", "input": "hi", "expected": "hello"}\n\n',
        encoding="utf-8",
    )
    cases = load_test_cases(f)
    assert len(cases) == 1


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError, match="no_such_file.jsonl"):
        load_test_cases("no_such_file.jsonl")


# ---------------------------------------------------------------------------
# AC2 — Bad JSONL gives useful error
# ---------------------------------------------------------------------------

def test_bad_json_raises_value_error():
    with pytest.raises(ValueError):
        load_test_cases(FIXTURES / "bad_json.jsonl")


def test_bad_json_error_includes_line_number():
    with pytest.raises(ValueError, match=r"Line 2"):
        load_test_cases(FIXTURES / "bad_json.jsonl")


def test_bad_json_error_mentions_malformed(tmp_path: Path):
    f = tmp_path / "bad.jsonl"
    f.write_text('{"id":"1","input":"x","expected":"y"}\nnot json at all\n')
    with pytest.raises(ValueError, match="malformed JSON"):
        load_test_cases(f)


# ---------------------------------------------------------------------------
# AC3 — Missing field gives useful error
# ---------------------------------------------------------------------------

def test_missing_field_raises_value_error():
    with pytest.raises(ValueError):
        load_test_cases(FIXTURES / "missing_field.jsonl")


def test_missing_field_error_includes_field_name():
    with pytest.raises(ValueError, match="'expected'"):
        load_test_cases(FIXTURES / "missing_field.jsonl")


def test_missing_field_error_includes_line_number():
    with pytest.raises(ValueError, match=r"Line 2"):
        load_test_cases(FIXTURES / "missing_field.jsonl")


def test_missing_id_field(tmp_path: Path):
    f = tmp_path / "no_id.jsonl"
    f.write_text('{"input": "q", "expected": "a"}\n')
    with pytest.raises(ValueError, match="'id'"):
        load_test_cases(f)


def test_missing_input_field(tmp_path: Path):
    f = tmp_path / "no_input.jsonl"
    f.write_text('{"id": "1", "expected": "a"}\n')
    with pytest.raises(ValueError, match="'input'"):
        load_test_cases(f)
