"""Tests for the HTML -> Markdown conversion."""

from __future__ import annotations

from tokendiet.html import html_to_markdown


def test_strips_scripts_and_styles(html_text: str):
    md = html_to_markdown(html_text)
    assert "console.log" not in md
    assert "track(" not in md
    assert "font-family" not in md
    assert "display:none" not in md


def test_keeps_real_content(html_text: str):
    md = html_to_markdown(html_text)
    assert "real content" in md
    assert "Tokendiet Demo Article" in md


def test_produces_markdown_syntax(html_text: str):
    md = html_to_markdown(html_text)
    assert "# Tokendiet Demo Article" in md  # ATX heading
    assert "[the link](https://example.com)" in md  # link preserved as markdown


def test_collapses_blank_lines():
    md = html_to_markdown("<p>a</p><p>b</p>")
    assert "\n\n\n" not in md
    assert md.endswith("\n")


def test_empty_html():
    md = html_to_markdown("<html><head><script>x()</script></head><body></body></html>")
    assert md.strip() == ""
