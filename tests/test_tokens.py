"""Unit tests for the token accounting math — the honest core of the tool."""

from __future__ import annotations

import math

from tokendiet.tokens import (
    DEFAULT_PRICES,
    MAX_EDGE_PX,
    PX_PER_TOKEN,
    ModelPrice,
    count_text_tokens,
    dollars_for_tokens,
    image_tokens,
    page_image_tokens,
)


def test_count_text_tokens_empty():
    assert count_text_tokens("") == 0


def test_count_text_tokens_monotonic():
    assert count_text_tokens("hello world") < count_text_tokens("hello world " * 50)


def test_image_tokens_small_image_uses_raw_area():
    # 300x300 is under the cap, so tokens = ceil(90000/750) = 120
    assert image_tokens(300, 300) == math.ceil(300 * 300 / PX_PER_TOKEN)


def test_image_tokens_caps_longest_edge():
    # A huge square is scaled so the longest edge == MAX_EDGE_PX.
    tokens = image_tokens(5000, 5000)
    expected = math.ceil(MAX_EDGE_PX * MAX_EDGE_PX / PX_PER_TOKEN)
    assert tokens == expected


def test_image_tokens_zero_dims():
    assert image_tokens(0, 100) == 0
    assert image_tokens(100, 0) == 0


def test_page_image_tokens_scales_up_to_cap():
    # An A4 page (595x842 pt) is rendered up to the cap; long edge -> 1568.
    tokens = page_image_tokens(595, 842)
    short = MAX_EDGE_PX * (595 / 842)
    expected = math.ceil(MAX_EDGE_PX * short / PX_PER_TOKEN)
    assert tokens == expected
    # And it lands in the documented per-page ballpark.
    assert 1500 <= tokens <= 2600


def test_dollars_for_tokens():
    price = ModelPrice("Test", 5.0)  # $5 / 1e6 tokens
    assert dollars_for_tokens(1_000_000, price) == 5.0
    assert dollars_for_tokens(0, price) == 0.0


def test_default_prices_present():
    names = {p.name for p in DEFAULT_PRICES}
    assert any("Opus" in n for n in names)
    assert all(p.input_per_mtok > 0 for p in DEFAULT_PRICES)
