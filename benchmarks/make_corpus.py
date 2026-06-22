"""Build the benchmark corpus.

Two kinds of documents, so the benchmark is both reproducible *and* realistic:

* **Generated** (offline, deterministic) — multi-page prose and a structured
  report built from public-domain text. Anyone can regenerate them byte-for-byte.
* **Remote** (downloaded at runtime, not committed) — real-world PDFs under open
  terms, to confirm the generated numbers aren't an artifact of generation.

Run: ``python benchmarks/make_corpus.py``  (add ``--no-remote`` to skip downloads)
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import pymupdf

CORPUS = Path(__file__).parent / "corpus"

# Public-domain text: Jane Austen, *Pride and Prejudice* (1813).
_PD_PROSE = """It is a truth universally acknowledged, that a single man in possession
of a good fortune, must be in want of a wife. However little known the feelings or views
of such a man may be on his first entering a neighbourhood, this truth is so well fixed in
the minds of the surrounding families, that he is considered the rightful property of some
one or other of their daughters. "My dear Mr. Bennet," said his lady to him one day, "have
you heard that Netherfield Park is let at last?" Mr. Bennet replied that he had not. "But it
is," returned she; "for Mrs. Long has just been here, and she told me all about it." Mr.
Bennet made no answer. "Do you not want to know who has taken it?" cried his wife
impatiently. "You want to tell me, and I have no objection to hearing it." This was
invitation enough."""

# Remote, real-world PDFs. Downloaded at runtime; NOT redistributed in this repo.
REMOTE = {
    "paper-attention.pdf": (
        "https://arxiv.org/pdf/1706.03762",
        "Vaswani et al., 'Attention Is All You Need' (arXiv:1706.03762).",
    ),
}


def _flow_html_to_pdf(path: Path, html: str) -> None:
    """Flow arbitrary HTML across as many A4 pages as needed."""
    story = pymupdf.Story(html=html)
    writer = pymupdf.DocumentWriter(str(path))
    mediabox = pymupdf.paper_rect("a4")
    where = mediabox + (50, 50, -50, -50)
    more = 1
    while more:
        dev = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
    writer.close()


def make_prose() -> Path:
    """~6 pages of pure public-domain prose — the text-heavy best case."""
    paras = "".join(f"<p>{_PD_PROSE}</p>" for _ in range(18))
    html = f"<h1>Pride and Prejudice (excerpt)</h1>{paras}"
    path = CORPUS / "prose.pdf"
    _flow_html_to_pdf(path, html)
    return path


def make_report() -> Path:
    """A structured business-style report: headings, paragraphs, and a table."""
    rows = "".join(
        f"<tr><td>Q{i}</td><td>{1000 * i}</td><td>{i * 7}%</td><td>{_PD_PROSE[:80]}</td></tr>"
        for i in range(1, 9)
    )
    html = f"""
    <h1>Quarterly Operations Report</h1>
    <h2>Summary</h2><p>{_PD_PROSE}</p>
    <h2>Detail</h2><p>{_PD_PROSE}</p>
    <h2>Metrics</h2>
    <table border="1" cellpadding="4">
      <tr><th>Quarter</th><th>Units</th><th>Growth</th><th>Notes</th></tr>{rows}
    </table>
    <h2>Outlook</h2><p>{_PD_PROSE}</p><p>{_PD_PROSE}</p>
    """
    path = CORPUS / "report.pdf"
    _flow_html_to_pdf(path, html)
    return path


def fetch_remote() -> list[Path]:
    out: list[Path] = []
    for name, (url, note) in REMOTE.items():
        dest = CORPUS / name
        if dest.exists():
            out.append(dest)
            continue
        try:
            print(f"  downloading {name} <- {url}  ({note})")
            req = urllib.request.Request(url, headers={"User-Agent": "tokendiet-benchmark"})
            with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
                dest.write_bytes(r.read())
            out.append(dest)
        except Exception as exc:  # network optional
            print(f"  ! skipped {name}: {exc}", file=sys.stderr)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Tokendiet benchmark corpus")
    parser.add_argument("--no-remote", action="store_true", help="Skip remote downloads")
    args = parser.parse_args(argv)

    CORPUS.mkdir(parents=True, exist_ok=True)
    print("Generating reproducible PDFs:")
    for fn in (make_prose, make_report):
        p = fn()
        print(f"  wrote {p.relative_to(CORPUS.parent)}")
    if not args.no_remote:
        print("Fetching real-world PDFs (not committed):")
        fetch_remote()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
