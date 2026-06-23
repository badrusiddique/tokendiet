"""Ground-truth with-vs-without benchmark using Anthropic's real tokenizer.

Tokendiet's normal numbers are *estimates* (tiktoken proxy + the documented image
heuristic). This script removes the guesswork: for every document in the corpus it
asks Anthropic's `count_tokens` API for the real token count of

  * WITHOUT Tokendiet — the native document (PDF as a document block; HTML as raw text)
  * WITH Tokendiet    — the converted Markdown as text

and reports the true saving, plus how close our offline estimate was.

Requires an API key and the anthropic extra:
    pip install -e ".[anthropic]"
    export ANTHROPIC_API_KEY=sk-ant-...
    python benchmarks/ground_truth.py

It is intentionally NOT part of CI (needs a key + network).
"""

from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

from tokendiet import build_savings, convert

CORPUS = Path(__file__).parent / "corpus"
MODEL = os.environ.get("TOKENDIET_MODEL", "claude-opus-4-8")


def _count(client, content) -> int:
    resp = client.messages.count_tokens(
        model=MODEL, messages=[{"role": "user", "content": content}]
    )
    return resp.input_tokens


def _native_content(path: Path):
    """The 'without Tokendiet' payload: how you'd hand the file to Claude as-is."""
    if path.suffix.lower() == ".pdf":
        data = base64.standard_b64encode(path.read_bytes()).decode()
        return [
            {
                "type": "document",
                "source": {"type": "base64", "media_type": "application/pdf", "data": data},
            }
        ]
    # HTML (and anything text-like): the raw markup you'd otherwise paste.
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY not set. This script needs a key to call count_tokens.\n"
            "  pip install -e '.[anthropic]' && export ANTHROPIC_API_KEY=sk-ant-... ",
            file=sys.stderr,
        )
        return 2
    try:
        import anthropic
    except ImportError:
        print("Install the anthropic extra: pip install -e '.[anthropic]'", file=sys.stderr)
        return 2

    client = anthropic.Anthropic()
    docs = sorted(p for pat in ("*.pdf", "*.html", "*.htm") for p in CORPUS.glob(pat))
    if not docs:
        print("No corpus. Run: python benchmarks/make_corpus.py", file=sys.stderr)
        return 1

    print(f"Ground truth via {MODEL} count_tokens API\n")
    print(f"{'document':26} {'without':>9} {'with':>8} {'saved':>6}  {'est.':>5}  est.err")
    tot_without = tot_with = 0
    for path in docs:
        result = convert(path)
        without = _count(client, _native_content(path))
        with_md = _count(client, result.markdown)
        est = build_savings(result)
        real_pct = (without - with_md) / without * 100 if without else 0
        est_err = real_pct - est.pct_saved  # how far our estimate was, in points
        tot_without += without
        tot_with += with_md
        print(
            f"{path.name:26} {without:>9,} {with_md:>8,} {real_pct:>5.0f}% "
            f"{est.pct_saved:>4.0f}%  {est_err:+.0f}pp"
        )

    saved = tot_without - tot_with
    pct = saved / tot_without * 100 if tot_without else 0
    print(f"\nTOTAL (ground truth): {tot_without:,} -> {tot_with:,}  ({pct:.0f}% saved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
