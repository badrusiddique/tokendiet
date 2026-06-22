"""Token accounting for Tokendiet.

This module is deliberately conservative and explicit about what is *measured*
versus *estimated*, because the whole value proposition of Tokendiet rests on
the savings numbers being honest.

Two quantities matter:

1. **Text tokens** — counted with ``tiktoken``'s ``cl100k_base`` encoding as a
   proxy. Claude's exact tokenizer is not public; for English prose cl100k is
   within roughly 10-20% of Claude's count. For published claims, prefer the
   Anthropic ``count_tokens`` ground truth (see :mod:`tokendiet.report`).

2. **Image tokens** — when Claude ingests a PDF natively it *also renders each
   page to an image* and tokenizes it, on top of the extracted text. Image
   cost follows Anthropic's documented heuristic ``tokens ≈ (w*h)/750`` after
   the image is resized so its longest edge is at most 1568px.
   Ref: https://platform.claude.com/docs/en/build-with-claude/vision

Every offline number produced here is an ESTIMATE and is labelled as such by
the reporter. The image-token term in particular assumes Claude renders each
page up to the vision size cap (longest edge = 1568px), which is the dominant
real-world case for A4/Letter pages but is an assumption, not a fact.
"""

from __future__ import annotations

import functools
import math
from dataclasses import dataclass

# --- Anthropic vision constants (documented heuristic) ---------------------
MAX_EDGE_PX = 1568
PX_PER_TOKEN = 750


@functools.lru_cache(maxsize=1)
def _encoder():
    import tiktoken

    return tiktoken.get_encoding("cl100k_base")


def count_text_tokens(text: str) -> int:
    """Estimate the number of tokens in ``text`` using the cl100k proxy."""
    if not text:
        return 0
    return len(_encoder().encode(text))


def _scale_longest_edge(width: float, height: float, edge: float) -> tuple[float, float]:
    """Scale (width, height) so the longest edge equals ``edge`` px."""
    longest = max(width, height)
    if longest <= 0:
        return 0.0, 0.0
    scale = edge / longest
    return width * scale, height * scale


def image_tokens(width_px: float, height_px: float) -> int:
    """Image token cost for an image of the given pixel size, after capping.

    Implements Anthropic's documented heuristic: resize so the longest edge is
    at most ``MAX_EDGE_PX``, then ``tokens = ceil(w*h / 750)``.
    """
    if width_px <= 0 or height_px <= 0:
        return 0
    if max(width_px, height_px) > MAX_EDGE_PX:
        width_px, height_px = _scale_longest_edge(width_px, height_px, MAX_EDGE_PX)
    return math.ceil((width_px * height_px) / PX_PER_TOKEN)


def page_image_tokens(width_pt: float, height_pt: float) -> int:
    """Estimated image tokens for a PDF page when ingested natively.

    A PDF page's size is given in points (1/72 inch). We assume Claude renders
    the page up to the vision size cap (longest edge = ``MAX_EDGE_PX`` px),
    which is the conservative dominant case for standard document pages.
    """
    w, h = _scale_longest_edge(width_pt, height_pt, MAX_EDGE_PX)
    return image_tokens(w, h)


# --- Pricing ----------------------------------------------------------------
@dataclass(frozen=True)
class ModelPrice:
    """Input price for a model, USD per million tokens."""

    name: str
    input_per_mtok: float


# Input prices in USD per million tokens, as researched June 2026. Pricing
# changes over time — override via the CLI/API. These are illustrative.
DEFAULT_PRICES: tuple[ModelPrice, ...] = (
    ModelPrice("Claude Opus 4.8", 5.0),
    ModelPrice("Claude Sonnet 4.6", 3.0),
    ModelPrice("Claude Haiku 4.5", 1.0),
)


def dollars_for_tokens(tokens: int, price: ModelPrice) -> float:
    """USD cost of ``tokens`` input tokens at ``price``."""
    return tokens / 1_000_000 * price.input_per_mtok
