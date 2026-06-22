"""Command-line interface: ``tokendiet convert <file>``.

This is the entry point the Claude skill shells out to. It converts a document
to Markdown, writes the ``.md`` next to it (or to ``--out``), and prints the
savings report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .convert import (
    EncryptedPDFError,
    UnsupportedFormatError,
    convert,
    supported_formats,
)
from .report import build_savings, format_report


def _cmd_convert(args: argparse.Namespace) -> int:
    src = Path(args.file)
    try:
        result = convert(src)
    except FileNotFoundError:
        print(f"error: file not found: {src}", file=sys.stderr)
        return 2
    except (UnsupportedFormatError, EncryptedPDFError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out_path = Path(args.out) if args.out else src.with_suffix(".md")
    savings = build_savings(
        source=str(src),
        markdown=result.markdown,
        page_dims=result.page_dims,
        warnings=result.warnings,
    )

    if args.stdout:
        sys.stdout.write(result.markdown)
    else:
        out_path.write_text(result.markdown, encoding="utf-8")

    if args.report == "json":
        payload = savings.to_dict()
        payload["output"] = None if args.stdout else str(out_path)
        print(json.dumps(payload, indent=2))
    elif not args.quiet:
        if not args.stdout:
            print(f"Wrote {out_path}", file=sys.stderr)
        print(format_report(savings), file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tokendiet",
        description="Convert documents to lean Markdown and report the token-$ saved.",
    )
    parser.add_argument("--version", action="version", version=f"tokendiet {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    conv = sub.add_parser(
        "convert",
        help=f"Convert a document to Markdown (supported: {', '.join(supported_formats())})",
    )
    conv.add_argument("file", help="Path to the document to convert")
    conv.add_argument("--out", help="Output .md path (default: alongside the source)")
    conv.add_argument(
        "--report",
        choices=["text", "json"],
        default="text",
        help="Report format (default: text on stderr; json on stdout)",
    )
    conv.add_argument("--stdout", action="store_true", help="Write Markdown to stdout, not a file")
    conv.add_argument("--quiet", action="store_true", help="Suppress the text report")
    conv.set_defaults(func=_cmd_convert)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
