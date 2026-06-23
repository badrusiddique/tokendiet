"""Tests for image -> Markdown via OCR (the optional 'ocr' extra)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from tokendiet.convert import OCRNotInstalledError, convert, supported_formats

# `tokendiet.convert` the attribute is shadowed by the convert() function in
# the package __init__, so grab the real module object explicitly.
convert_mod = importlib.import_module("tokendiet.convert")


def test_image_extensions_registered():
    fmts = supported_formats()
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        assert ext in fmts


def test_image_without_ocr_raises(monkeypatch, png_image: Path):
    """When the OCR extra isn't installed, we fail with a clear, actionable error."""
    monkeypatch.setattr(convert_mod, "_ocr_engine", None)
    monkeypatch.setitem(sys.modules, "rapidocr_onnxruntime", None)  # makes import fail
    with pytest.raises(OCRNotInstalledError):
        convert(png_image)


def test_ocr_warning_no_text():
    w = convert_mod._ocr_quality_warnings("\n", [0.99])
    assert w and "No text detected" in w[0]


def test_ocr_warning_low_confidence():
    w = convert_mod._ocr_quality_warnings("Some recovered text here", [0.3, 0.4, 0.5])
    assert w and "Low OCR confidence" in w[0]


def test_ocr_no_warning_when_confident():
    assert convert_mod._ocr_quality_warnings("Some recovered text here", [0.95, 0.97]) == []


def test_image_ocr_extracts_text(png_image: Path):
    """With OCR available, an image of text converts to lean Markdown with real savings."""
    pytest.importorskip("rapidocr_onnxruntime")
    convert_mod._ocr_engine = None  # reset cache in case another test nulled it
    result = convert(png_image)
    assert result.pages == 1
    assert result.before_image_tokens > 0  # native cost = seeing the image
    assert result.before_text_tokens == 0
    assert result.markdown.strip()
    assert "Tokendiet" in result.markdown  # OCR recovered the rendered text
