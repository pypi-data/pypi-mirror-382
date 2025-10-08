"""Command line entry points for the divelogpy package."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .sensor_report import ReportGenerationError, generate_sensor_report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="divelogpy", description="Dive log analysis utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report = subparsers.add_parser(
        "sensor-report",
        help="Generate the sensor dashboard PDF report.",
    )
    report.add_argument("database", help="Path to the .db file or directory containing Shearwater exports.")
    report.add_argument(
        "-o",
        "--output",
        help="Destination PDF path. Defaults to <database>/sensor-report.pdf.",
    )
    report.add_argument("--dive-id", help="Explicit dive id to render.")
    report.add_argument(
        "--dive-index",
        type=int,
        default=-1,
        help="Select the Nth most recent CCR dive when no dive id is given (default: -1).",
    )

    report.add_argument("--start", help="Override the report start date (YYYY-MM-DD).")
    report.add_argument("--end", help="Override the report end date (YYYY-MM-DD).")
    report.add_argument(
        "--image-scale",
        type=float,
        default=1.0,
        help="Scale factor applied when rasterising Plotly figures (default: 1.0).",
    )
    report.add_argument(
        "--pdf-dpi",
        type=int,
        default=50,
        help="DPI to use for embedding plot images into the PDF (default: 150).",
    )

    return parser


def _run_sensor_report(args: argparse.Namespace) -> int:
    try:
        result = generate_sensor_report(
            args.database,
            output=args.output,
            dive_id=args.dive_id,
            dive_index=args.dive_index,
            start=args.start,
            end=args.end,
            image_scale=args.image_scale,
            pdf_dpi=args.pdf_dpi,
        )
    except (FileNotFoundError, ReportGenerationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Report written to {result.output_path}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "sensor-report":
        return _run_sensor_report(args)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
