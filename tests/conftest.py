"""Shared fixtures: generate small PDFs on the fly so tests need no binary assets."""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest

_LOREM = (
    "Tokendiet converts documents to lean Markdown so language models read the "
    "cheap text version instead of paying to render every page as an image. "
    "This paragraph exists purely to give the extractor real words to work with. "
)


@pytest.fixture
def text_pdf(tmp_path: Path) -> Path:
    """A normal 2-page text PDF."""
    path = tmp_path / "text.pdf"
    doc = pymupdf.open()
    for i in range(2):
        page = doc.new_page()  # default A4 (595 x 842 pt)
        rect = pymupdf.Rect(72, 72, 523, 770)
        page.insert_textbox(rect, f"Page {i + 1}\n\n" + _LOREM * 4, fontsize=11)
    doc.save(path)
    doc.close()
    return path


@pytest.fixture
def scanned_pdf(tmp_path: Path) -> Path:
    """An image-only PDF with no real text layer (simulates a scan)."""
    path = tmp_path / "scanned.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.draw_rect(pymupdf.Rect(50, 50, 545, 750), fill=(0.9, 0.9, 0.9))
    doc.save(path)
    doc.close()
    return path


_HTML = """<!DOCTYPE html>
<html><head><title>Demo</title>
<style>body{font-family:sans-serif;color:#333;margin:0}.ad{display:none}</style>
<script>console.log('analytics');for(var i=0;i<100;i++){track(i);}</script>
</head>
<body>
<nav>Home About Contact</nav>
<h1>Tokendiet Demo Article</h1>
<p>This paragraph is the <strong>real content</strong> a reader wants.</p>
<p>See <a href="https://example.com">the link</a> for more.</p>
<footer>Copyright 2026</footer>
</body></html>"""


@pytest.fixture
def html_file(tmp_path: Path) -> Path:
    path = tmp_path / "page.html"
    path.write_text(_HTML, encoding="utf-8")
    return path


@pytest.fixture
def html_text() -> str:
    return _HTML


@pytest.fixture
def encrypted_pdf(tmp_path: Path) -> Path:
    """A password-protected PDF."""
    path = tmp_path / "locked.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 100), "secret", fontsize=11)
    doc.save(
        path,
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="owner",
        user_pw="user",
    )
    doc.close()
    return path
