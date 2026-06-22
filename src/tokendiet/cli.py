"""Command-line interface: ``tokendiet convert <file-or-url>``.

This is the entry point the Claude skill shells out to. It converts a document
(PDF or HTML file, or an http(s) URL) to Markdown, writes the ``.md``, and
prints the savings report.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from . import __version__
from .convert import (
    EncryptedPDFError,
    FetchError,
    UnsupportedFormatError,
    convert,
    supported_formats,
)
from .report import build_savings, format_report


def _is_url(arg: str) -> bool:
    return arg.startswith(("http://", "https://"))


def _default_out(src_arg: str) -> Path:
    """Where to write the Markdown when ``--out`` is not given."""
    if _is_url(src_arg):
        parsed = urlparse(src_arg)
        name = parsed.path.rstrip("/").split("/")[-1] or parsed.netloc or "page"
        stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", name).strip("-.") or "page"
        return Path.cwd() / (Path(stem).stem + ".md")
    return Path(src_arg).with_suffix(".md")


def _cmd_convert(args: argparse.Namespace) -> int:
    src_arg = args.file
    try:
        result = convert(src_arg)
    except FileNotFoundError:
        print(f"error: file not found: {src_arg}", file=sys.stderr)
        return 2
    except (UnsupportedFormatError, EncryptedPDFError, FetchError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    savings = build_savings(result)
    out_path = Path(args.out) if args.out else _default_out(src_arg)

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
        help=f"Convert a document or URL to Markdown (supported: {', '.join(supported_formats())})",
    )
    conv.add_argument("file", help="Path to a document, or an http(s):// URL")
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
