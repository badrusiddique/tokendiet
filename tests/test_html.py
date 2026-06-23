"""Tests for HTML -> Markdown: the main-content path and the fallback path."""

from __future__ import annotations

from tokendiet.html import _full_document_markdown, html_to_markdown

# A realistic article: substantial body, plus distinctive boilerplate to drop.
_ARTICLE = (
    "<!DOCTYPE html><html><head><title>T</title>"
    "<style>.x{color:red}</style><script>track()</script></head><body>"
    "<nav>UNIQUENAVTOKEN home about contact menu</nav>"
    "<article><h1>The Real Article</h1>"
    + ("<p>" + ("Tokendiet keeps the body and drops the surrounding chrome. " * 8) + "</p>")
    * 6
    + "</article>"
    "<footer>UNIQUEFOOTERTOKEN copyright 2026 boilerplate links</footer>"
    "</body></html>"
)


# --- Main-content extraction path (trafilatura, the default) ---
def test_main_content_keeps_body_drops_boilerplate():
    md = html_to_markdown(_ARTICLE)
    assert "Real Article" in md  # body survives
    assert "UNIQUENAVTOKEN" not in md  # nav dropped
    assert "UNIQUEFOOTERTOKEN" not in md  # footer dropped
    assert "track()" not in md  # script never leaks


def test_main_content_nonempty():
    assert html_to_markdown(_ARTICLE).strip()


# --- Fallback path (markdownify on the whole document) ---
def test_fallback_strips_scripts_and_styles(html_text: str):
    md = _full_document_markdown(html_text)
    assert "console.log" not in md
    assert "track(" not in md
    assert "font-family" not in md
    assert "display:none" not in md


def test_fallback_keeps_content_and_markdown_syntax(html_text: str):
    md = _full_document_markdown(html_text)
    assert "real content" in md
    assert "# Tokendiet Demo Article" in md  # ATX heading
    assert "[the link](https://example.com)" in md  # link preserved as markdown


def test_fallback_collapses_blank_lines():
    md = _full_document_markdown("<p>a</p><p>b</p>")
    assert "\n\n\n" not in md
    assert md.endswith("\n")


def test_fallback_empty_html():
    md = _full_document_markdown("<html><head><script>x()</script></head><body></body></html>")
    assert md.strip() == ""
