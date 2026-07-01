from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


_REQUIRED_KEYS = {"id", "input", "expected"}


@dataclass(frozen=True)
class TestCase:
    id: str
    input: str
    expected: str


def load_test_cases(path: str | Path) -> list[TestCase]:
    """Load test cases from a JSONL file.

    Args:
        path: Path to the JSONL file. Each non-blank line must be a JSON object
              with keys ``id``, ``input``, and ``expected``.

    Returns:
        Non-empty list of TestCase objects.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If any line contains invalid JSON, is missing required keys,
                    or the file contains no test cases after filtering blank lines.
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
                    f"Line {line_num}: invalid JSON at col {exc.colno}: {raw!r}"
                ) from exc

            missing = _REQUIRED_KEYS - record.keys()
            if missing:
                raise ValueError(
                    f"Line {line_num}: missing required keys {sorted(missing)!r} "
                    f"in record {record!r}"
                )

            cases.append(
                TestCase(
                    id=str(record["id"]),
                    input=str(record["input"]),
                    expected=str(record["expected"]),
                )
            )

    if not cases:
        raise ValueError(f"no test cases found in {path}")

    return cases
