"""CLI entrypoint for the B2B lead generation pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from leadseek.config import AppConfig, ConfigError
from leadseek.pipeline import PipelineRunError, process_leads


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="leadseek",
        description="Diagnose product-management job descriptions into consulting leads.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    process = subparsers.add_parser(
        "process-leads",
        help="Fetch live job postings, diagnose them with Gemini, and append CSV rows.",
    )
    process.add_argument(
        "--roles",
        required=True,
        help='Comma-separated target roles, e.g. "VP Product, Head of Product".',
    )
    process.add_argument(
        "--locations",
        required=True,
        help='Comma-separated locations, e.g. "US, Canada, Mexico".',
    )
    process.add_argument(
        "--output",
        required=True,
        type=Path,
        help="CSV file to append diagnosed leads into.",
    )
    process.add_argument(
        "--model",
        default=None,
        help="Gemini model override. Defaults to GEMINI_MODEL or gemini-2.5-flash.",
    )
    process.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of job descriptions to process.",
    )
    process.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on the first failed job description instead of continuing.",
    )

    return parser


def _split_csv_arg(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "process-leads":
        try:
            config = AppConfig.from_env(model_override=args.model)
            summary = process_leads(
                roles=_split_csv_arg(args.roles),
                locations=_split_csv_arg(args.locations),
                output_path=args.output,
                config=config,
                limit=args.limit,
                fail_fast=args.fail_fast,
            )
        except (ConfigError, PipelineRunError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        print(
            f"Processed {summary.succeeded}/{summary.total} job descriptions. "
            f"Appended {summary.succeeded} rows to {args.output}."
        )
        if summary.failed:
            print(f"Skipped {summary.failed} failed job posting(s):", file=sys.stderr)
            for failure in summary.failures:
                print(f"- {failure.job_url}: {failure.error}", file=sys.stderr)
            return 2
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
