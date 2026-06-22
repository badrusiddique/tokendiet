"""Tests for the savings report arithmetic and serialization."""

from __future__ import annotations

from tokendiet.report import TokenSavings, build_savings, format_report


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


def test_build_savings_from_markdown():
    md = "# Title\n\n" + ("word " * 200)
    s = build_savings("x.pdf", md, page_dims=[(595, 842)], warnings=["w"])
    assert s.pages == 1
    assert s.before_image_tokens > 0
    assert s.after_tokens > 0
    # The whole win is the eliminated image tokens, so savings == image tokens.
    assert s.saved_tokens == s.before_image_tokens
    assert "w" in s.warnings


def test_format_report_contains_key_facts():
    out = format_report(_sample())
    assert "doc.pdf" in out
    assert "80%" in out
    assert "estimate" in out
