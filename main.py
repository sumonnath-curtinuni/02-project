"""Entry point for AssessmentFlow."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from assessmentflow.cli import print_summary, run
from assessmentflow.storage import load_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AssessmentFlow - personal assessment sprint planner"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(os.environ.get("ASSESSMENTFLOW_DATA", "data/assessmentflow.json")),
        help="Path to the JSON data file (default: data/assessmentflow.json)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print the assessment list, focus recommendation and weekly insights, then exit.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.summary:
        try:
            data = load_data(args.data)
        except (ValueError, OSError) as exc:
            raise SystemExit(f"Could not load data: {exc}")
        print_summary(data)
        return
    run(args.data)


if __name__ == "__main__":
    main()
