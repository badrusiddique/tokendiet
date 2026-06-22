"""Tests for the savings report arithmetic and serialization."""

from __future__ import annotations

from tokendiet.convert import ConversionResult
from tokendiet.report import TokenSavings, build_savings, format_report
from tokendiet.tokens import count_text_tokens


def _sample() -> TokenSavings:
    return TokenSavings(
        source="doc.pdf",
        pages=2,
        before_text_tokens=1000,
        before_image_tokens=4000,
        after_tokens=1000,
        method="estimate",
    )


def test_before_total_and_saved():
    s = _sample()
    assert s.before_total == 5000
    assert s.saved_tokens == 4000  # image tokens eliminated
    assert round(s.pct_saved, 1) == 80.0


def test_saved_never_negative():
    s = TokenSavings("d", 1, 100, 0, 999999, method="estimate")
    assert s.saved_tokens == 0
    assert s.pct_saved >= 0.0


def test_pct_saved_zero_when_no_before():
    s = TokenSavings("d", 0, 0, 0, 0, method="estimate")
    assert s.pct_saved == 0.0


def test_dollar_savings_positive_and_ordered_by_price():
    s = _sample()
    dollars = dict(s.dollar_savings())
    # Opus ($5) should save more than Haiku ($1) for the same tokens.
    opus = next(v for k, v in dollars.items() if "Opus" in k)
    haiku = next(v for k, v in dollars.items() if "Haiku" in k)
    assert opus > haiku > 0


def test_to_dict_shape():
    d = _sample().to_dict()
    assert d["saved_tokens"] == 4000
    assert d["before"]["total_tokens"] == 5000
    assert d["after"]["total_tokens"] == 1000
    assert "dollar_savings" in d and d["dollar_savings"]


def test_build_savings_from_pdf_result():
    md = "# Title\n\n" + ("word " * 200)
    text_tokens = count_text_tokens(md)
    result = ConversionResult(
        source="x.pdf",
        markdown=md,
        before_text_tokens=text_tokens,
        before_image_tokens=2317,
        pages=1,
        warnings=["w"],
    )
    s = build_savings(result)
    assert s.pages == 1
    assert s.before_image_tokens == 2317
    assert s.after_tokens == text_tokens
    # For PDF, before_text == after, so the whole win is the image tokens.
    assert s.saved_tokens == 2317
    assert "w" in s.warnings


def test_build_savings_from_html_result():
    md = "# Title\n\nclean body\n"
    result = ConversionResult(
        source="page.html",
        markdown=md,
        before_text_tokens=5000,  # raw HTML markup
        before_image_tokens=0,
        pages=0,
    )
    s = build_savings(result)
    assert s.before_image_tokens == 0
    assert s.saved_tokens == 5000 - s.after_tokens
    assert s.pct_saved > 0


def test_format_report_contains_key_facts():
    out = format_report(_sample())
    assert "doc.pdf" in out
    assert "80%" in out
    assert "estimate" in out
