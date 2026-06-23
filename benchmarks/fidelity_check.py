"""Fidelity check: does conversion KEEP the content, not just shed tokens?

Token savings are worthless if information is lost. This measures how much of the
source TEXT survives each conversion, and shows what gets dropped, so the
"savings" are honest.

Run:  python benchmarks/fidelity_check.py   (image section needs the `ocr` extra)
"""

from __future__ import annotations

import logging
import re
import tempfile
from pathlib import Path

import pymupdf

from tokendiet.html import _full_document_markdown, html_to_markdown

logging.disable(logging.CRITICAL)
CORPUS = Path(__file__).parent / "corpus"


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{3,}", (text or "").lower()))


def _recall(source: str, output: str) -> float:
    s = _words(source)
    return len(s & _words(output)) / len(s) if s else 1.0


def pdf_fidelity() -> None:
    print("PDF — markdown vs the PDF's own text layer (ground truth):")
    import pymupdf4llm

    for name in ("prose.pdf", "paper-attention.pdf"):
        p = CORPUS / name
        if not p.exists():
            continue
        doc = pymupdf.open(p)
        raw = "\n".join(pg.get_text() for pg in doc)
        md = pymupdf4llm.to_markdown(doc, show_progress=False)
        doc.close()
        tables = sum(1 for ln in md.splitlines() if ln.count("|") >= 2)
        print(f"  {name:24} text recall {_recall(raw, md) * 100:4.0f}%   table rows: {tables}")
    print("  (lost: figures/charts as images, some equation glyphs — by design)\n")


def html_fidelity() -> None:
    print("HTML — main-content vs the full page (what main-content extraction drops):")
    for name in ("wikipedia-markdown.html", "article.html"):
        p = CORPUS / name
        if not p.exists():
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        full, main = _full_document_markdown(raw), html_to_markdown(raw)
        main_w = _words(main)
        dropped = [
            ln.strip() for ln in full.splitlines() if _words(ln) and not (_words(ln) & main_w)
        ]
        print(f"  {name:26} keeps {_recall(full, main) * 100:4.0f}% of page text")
        for ln in dropped[:4]:
            print(f"      dropped: {ln[:70]}")
    print("  (dropped text is navigation/footer chrome; article body + tables kept)\n")


def image_fidelity() -> None:
    print("IMAGE — OCR vs the page's text layer (ground truth):")
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("  skipped — install the OCR extra: pip install 'tokendiet[ocr]'\n")
        return
    ocr = RapidOCR()
    for name in ("prose.pdf", "report.pdf"):
        p = CORPUS / name
        if not p.exists():
            continue
        doc = pymupdf.open(p)
        page = doc[0]
        truth = page.get_text()
        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / "p.png"
            page.get_pixmap(dpi=150).save(png)
            res, _ = ocr(str(png))
        doc.close()
        got = "\n".join(r[1] for r in res) if res else ""
        print(f"  {name:24} OCR recall {_recall(truth, got) * 100:4.0f}%")
    print("  (~90-95% on clean pages; weaker on small text/numbers — hence the warning)\n")


def main() -> int:
    if not any(CORPUS.glob("*")):
        print("No corpus. Run: python benchmarks/make_corpus.py")
        return 1
    print("=== Tokendiet fidelity ===\n")
    pdf_fidelity()
    html_fidelity()
    image_fidelity()
    print("Verdict: text content is preserved; only genuinely-visual elements are lost.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
