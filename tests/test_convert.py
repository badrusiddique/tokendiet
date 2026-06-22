"""Tests for the conversion engine and its edge cases."""

from __future__ import annotations

from pathlib import Path

import pytest

from tokendiet.convert import (
    EncryptedPDFError,
    UnsupportedFormatError,
    convert,
    supported_formats,
)


def test_supported_formats_includes_pdf_and_html():
    fmts = supported_formats()
    assert ".pdf" in fmts
    assert ".html" in fmts


def test_convert_text_pdf(text_pdf: Path):
    result = convert(text_pdf)
    assert result.markdown.strip()
    assert result.pages == 2
    assert result.before_image_tokens > 0  # native PDF renders page images
    assert result.before_text_tokens > 0
    assert "Tokendiet" in result.markdown
    assert not result.warnings


def test_convert_html_file(html_file: Path):
    result = convert(html_file)
    assert result.pages == 0
    assert result.before_image_tokens == 0  # HTML has no page images
    # Real content survives; scripts/styles are stripped.
    assert "real content" in result.markdown
    assert "console.log" not in result.markdown
    assert "font-family" not in result.markdown
    # Markdown is leaner than the raw HTML it came from.
    from tokendiet.tokens import count_text_tokens

    assert count_text_tokens(result.markdown) < result.before_text_tokens


def test_convert_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        convert(tmp_path / "nope.pdf")


def test_convert_unsupported_format(tmp_path: Path):
    f = tmp_path / "data.xyz"
    f.write_text("hello")
    with pytest.raises(UnsupportedFormatError):
        convert(f)


def test_convert_encrypted_pdf(encrypted_pdf: Path):
    with pytest.raises(EncryptedPDFError):
        convert(encrypted_pdf)


def test_convert_scanned_pdf_warns(scanned_pdf: Path):
    result = convert(scanned_pdf)
    assert any("scanned" in w.lower() for w in result.warnings)


def test_accepts_str_path(text_pdf: Path):
    result = convert(str(text_pdf))
    assert result.markdown.strip()
