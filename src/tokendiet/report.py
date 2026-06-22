"""Savings report: how many tokens (and dollars) converting to Markdown saves.

The report compares two ways of giving the same document to Claude:

* **Before** — the native path. Claude extracts the page text *and* renders
  each page to an image, paying for both.
* **After** — the Markdown path. Claude reads plain text only.

``method`` records how the numbers were produced: ``"estimate"`` (offline,
tiktoken + the documented image-token heuristic) or ``"ground-truth"``
(Anthropic ``count_tokens`` API). Estimates are always labelled in output.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .tokens import (
    DEFAULT_PRICES,
    ModelPrice,
    count_text_tokens,
    dollars_for_tokens,
)

if TYPE_CHECKING:
    from .convert import ConversionResult


@dataclass
class TokenSavings:
    """The measured/estimated savings for a single converted document."""

    source: str
    pages: int
    before_text_tokens: int
    before_image_tokens: int
    after_tokens: int
    method: str = "estimate"
    warnings: list[str] = field(default_factory=list)

    @property
    def before_total(self) -> int:
        return self.before_text_tokens + self.before_image_tokens

    @property
    def saved_tokens(self) -> int:
        return max(0, self.before_total - self.after_tokens)

    @property
    def pct_saved(self) -> float:
        if self.before_total <= 0:
            return 0.0
        return self.saved_tokens / self.before_total * 100.0

    def dollar_savings(
        self, prices: Sequence[ModelPrice] = DEFAULT_PRICES
    ) -> list[tuple[str, float]]:
        """USD saved per model for this single document."""
        return [(p.name, dollars_for_tokens(self.saved_tokens, p)) for p in prices]

    def to_dict(self, prices: Sequence[ModelPrice] = DEFAULT_PRICES) -> dict:
        return {
            "source": self.source,
            "pages": self.pages,
            "method": self.method,
            "before": {
                "text_tokens": self.before_text_tokens,
                "image_tokens": self.before_image_tokens,
                "total_tokens": self.before_total,
            },
            "after": {"total_tokens": self.after_tokens},
            "saved_tokens": self.saved_tokens,
            "pct_saved": round(self.pct_saved, 1),
            "dollar_savings": {name: round(usd, 6) for name, usd in self.dollar_savings(prices)},
            "warnings": self.warnings,
        }


def build_savings(result: ConversionResult, method: str = "estimate") -> TokenSavings:
    """Assemble a savings report from a :class:`~tokendiet.convert.ConversionResult`.

    The backend has already computed the native cost (text + image tokens); here
    we count the Markdown ("after") and combine. The mechanism is honest: PDF
    savings come from eliminating page-image tokens, HTML savings from shedding
    markup.
    """
    after = count_text_tokens(result.markdown)
    return TokenSavings(
        source=result.source,
        pages=result.pages,
        before_text_tokens=result.before_text_tokens,
        before_image_tokens=result.before_image_tokens,
        after_tokens=after,
        method=method,
        warnings=list(result.warnings),
    )


def format_report(savings: TokenSavings, prices: Sequence[ModelPrice] = DEFAULT_PRICES) -> str:
    """Render a human-readable report block."""
    note = " (estimate)" if savings.method == "estimate" else " (ground truth)"
    if savings.before_image_tokens > 0:
        native = (
            f"  Native{note}: {savings.before_total:,} tokens "
            f"({savings.before_text_tokens:,} text + {savings.before_image_tokens:,} image)"
        )
    else:
        native = f"  Native{note}: {savings.before_total:,} tokens (raw markup)"
    lines = [
        f"Tokendiet — {savings.source}",
        f"  Pages: {savings.pages}" if savings.pages else "  HTML",
        native,
        f"  Markdown{note}:   {savings.after_tokens:,} tokens",
        f"  Saved: {savings.saved_tokens:,} tokens ({savings.pct_saved:.0f}%)",
    ]
    dollars = savings.dollar_savings(prices)
    if savings.saved_tokens > 0:
        per_model = ", ".join(f"{name}: ${usd:.4f}" for name, usd in dollars)
        lines.append(f"  Saved per call: {per_model}")
    for w in savings.warnings:
        lines.append(f"  ! {w}")
    return "\n".join(lines)
