"""CLI entry point for the LLM evaluation harness."""

import argparse
import json
import logging
import sys
from pathlib import Path

from harness.loader import load_test_cases
from harness.mock_endpoint import call_endpoint
from harness.runner import format_summary, run_evaluation
from harness.scorer import exact_match, keyword_overlap


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="harness",
        description="Run JSONL test cases against an LLM endpoint and score the results.",
    )
    parser.add_argument(
        "test_file",
        type=Path,
        help="Path to a .jsonl file with test cases (fields: id, input, expected).",
    )
    parser.add_argument(
        "--scorer",
        choices=["keyword_overlap", "exact_match"],
        default="keyword_overlap",
        help="Scoring method (default: keyword_overlap).",
    )
    parser.add_argument(
        "--mode",
        choices=["random", "fixed", "echo"],
        default="random",
        help="Mock endpoint response mode (default: random).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for the mock endpoint -- makes runs reproducible.",
    )
    parser.add_argument(
        "--fail-rate",
        type=float,
        default=0.0,
        metavar="RATE",
        help="Probability [0-1] that each endpoint call fails (simulates errors).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write full results as JSON to this file (optional).",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="WARNING",
        help="Logging verbosity (default: WARNING).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
    )

    try:
        cases = load_test_cases(args.test_file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    scorer_fn = exact_match if args.scorer == "exact_match" else keyword_overlap

    def endpoint(prompt: str) -> str:
        return call_endpoint(prompt, mode=args.mode, seed=args.seed, fail_rate=args.fail_rate)

    summary = run_evaluation(cases, endpoint, scorer=scorer_fn)

    print(format_summary(summary))

    if args.output:
        payload = {
            "total": summary.total,
            "passed": summary.passed,
            "failed": summary.failed,
            "errors": summary.errors,
            "pass_rate": round(summary.pass_rate, 4),
            "results": [
                {
                    "id": r.case_id,
                    "input": r.input,
                    "expected": r.expected,
                    "response": r.response,
                    "passed": r.passed,
                    "score": r.score.score if r.score else None,
                    "method": r.score.method if r.score else None,
                    "reason": r.score.reason if r.score else None,
                    "error": r.error,
                }
                for r in summary.results
            ],
        }
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nFull results written to {args.output}", file=sys.stderr)

    return 0 if summary.errors == 0 and summary.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
