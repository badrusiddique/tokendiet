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


def test_supported_formats_includes_pdf():
    assert ".pdf" in supported_formats()


def test_convert_text_pdf(text_pdf: Path):
    result = convert(text_pdf)
    assert result.markdown.strip()
    assert len(result.page_dims) == 2
    assert all(w > 0 and h > 0 for (w, h) in result.page_dims)
    assert "Tokendiet" in result.markdown
    assert not result.warnings


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
