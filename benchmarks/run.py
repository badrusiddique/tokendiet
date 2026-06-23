"""Run the benchmark over every PDF in ``benchmarks/corpus`` and write RESULTS.md.

Numbers are produced by Tokendiet's offline estimator (tiktoken proxy for text +
the documented image-token heuristic). They are labelled ESTIMATE. To validate
against Anthropic's tokenizer, see ``--ground-truth`` notes in the README.

Run: ``python benchmarks/run.py``  (after ``python benchmarks/make_corpus.py``)
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

from tokendiet import build_savings, convert
from tokendiet.convert import TokendietError
from tokendiet.tokens import DEFAULT_PRICES, dollars_for_tokens

CORPUS = Path(__file__).parent / "corpus"
RESULTS = Path(__file__).parent / "RESULTS.md"
OPUS = DEFAULT_PRICES[0]  # headline $ uses the most expensive model


SUPPORTED = ("*.pdf", "*.html", "*.htm")


def _run_one(path: Path):
    result = convert(path)
    s = build_savings(result)
    s.source = path.name  # display the bare filename in the table
    return s


def main(argv: list[str] | None = None) -> int:
    generated_at = argv[0] if argv else datetime.now(UTC).strftime("%Y-%m-%d")
    docs = sorted(p for pat in SUPPORTED for p in CORPUS.glob(pat))
    if not docs:
        print("No documents in corpus/. Run: python benchmarks/make_corpus.py", file=sys.stderr)
        return 1

    rows = []
    tot_before = tot_after = 0
    for doc in docs:
        try:
            s = _run_one(doc)
        except TokendietError as exc:
            print(f"! {doc.name}: {exc}", file=sys.stderr)
            continue
        tot_before += s.before_total
        tot_after += s.after_tokens
        rows.append(s)
        print(
            f"{doc.name:26} pages={s.pages:>3}  native={s.before_total:>7,}  "
            f"md={s.after_tokens:>6,}  saved={s.pct_saved:>4.0f}%"
        )

    saved = tot_before - tot_after
    pct = saved / tot_before * 100 if tot_before else 0

    lines = [
        "# Benchmark results",
        "",
        f"_Generated {generated_at} by `python benchmarks/run.py`. "
        "Numbers are **estimates** (tiktoken proxy + documented image-token heuristic); "
        "regenerate locally to reproduce._",
        "",
        "| Document | Pages | Native (tok) | Markdown (tok) | Saved | % saved | "
        "$ saved/call (Opus) |",
        "|---|--:|--:|--:|--:|--:|--:|",
    ]
    for s in rows:
        usd = dollars_for_tokens(s.saved_tokens, OPUS)
        lines.append(
            f"| {s.source} | {s.pages} | {s.before_total:,} | {s.after_tokens:,} "
            f"| {s.saved_tokens:,} | {s.pct_saved:.0f}% | ${usd:.4f} |"
        )
    total_usd = dollars_for_tokens(saved, OPUS)
    lines.append(
        f"| **Total** | | **{tot_before:,}** | **{tot_after:,}** | **{saved:,}** "
        f"| **{pct:.0f}%** | **${total_usd:.4f}** |"
    )
    lines += [
        "",
        "## Method",
        "",
        "- **PDF native tokens** = extracted text tokens + per-page image tokens. Claude "
        "renders each page to an image (capped at 1568px longest edge) and tokenizes it via "
        "`tokens ≈ (w·h)/750`, *on top of* the text. The win is the eliminated image tokens.",
        "- **HTML native tokens** = tokens of the raw markup you'd otherwise feed Claude "
        "(tags, attributes, inline scripts and styles). The win is shedding that markup.",
        "- **Markdown tokens** = tokens of the converted Markdown (text only).",
        "- **Text counting** uses `tiktoken` `cl100k_base` as a proxy for Claude's tokenizer "
        "(within ~10-20% for English prose).",
        "",
        "## Caveats",
        "",
        "- Figures, charts, and equation images are **lost** in Markdown. For documents where "
        "Claude must *see* the visuals, the native PDF is the right choice and these savings "
        "do not apply.",
        "- Scanned/image-only PDFs have little text to extract; Tokendiet warns and recommends "
        "native or OCR.",
        "- HTML conversion strips scripts/styles/head but keeps structural content, so it never "
        "silently drops real text.",
        "- Generated docs (`prose.pdf`, `report.pdf`, `article.html`) are reproducible; "
        "`paper-attention.pdf` and `wikipedia-markdown.html` are downloaded at runtime and not "
        "redistributed.",
    ]
    RESULTS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nTOTAL: {tot_before:,} -> {tot_after:,} tokens  ({pct:.0f}% saved)")
    print(f"Wrote {RESULTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
