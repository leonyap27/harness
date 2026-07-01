from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FIELDS = ("id", "input", "expected")


@dataclass(frozen=True)
class TestCase:
    id: str
    input: str
    expected: str


def load_test_cases(path: str | Path) -> list[TestCase]:
    """Load and validate test cases from a JSONL file.

    Args:
        path: Path to the JSONL file. Each line must be a JSON object with
              fields ``id``, ``input``, and ``expected``.

    Returns:
        List of validated TestCase objects.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If any line contains malformed JSON or is missing a
                    required field. The message names the line number and
                    the specific problem.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Test file not found: {path}")

    cases: list[TestCase] = []
    with path.open(encoding="utf-8") as fh:
        for line_num, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue

            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Line {line_num}: malformed JSON — {exc.msg} "
                    f"(col {exc.colno}): {raw!r}"
                ) from exc

            for field in REQUIRED_FIELDS:
                if field not in record:
                    raise ValueError(
                        f"Line {line_num}: missing required field '{field}' "
                        f"in record {record!r}"
                    )

            cases.append(
                TestCase(
                    id=str(record["id"]),
                    input=str(record["input"]),
                    expected=str(record["expected"]),
                )
            )

    return cases
