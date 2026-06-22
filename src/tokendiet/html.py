"""HTML -> Markdown conversion.

Raw HTML is mostly markup the model pays for but never needs: tags, attributes,
and — the big ones — inline ``<script>`` and ``<style>`` blocks. We strip the
*definite* noise (scripts, styles, head metadata, embedded SVG/iframes) and let
``markdownify`` turn the rest into Markdown. We deliberately keep structural
content elements (including ``nav``/``header``/``footer``) so we never silently
drop real text — the savings come from shedding markup, not guessing at layout.
"""

from __future__ import annotations

from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as _to_md

# Elements whose *content* is pure noise for a model reading for text.
_DROP = ["script", "style", "noscript", "template", "svg", "iframe", "head"]


def html_to_markdown(raw_html: str) -> str:
    """Convert an HTML string to clean Markdown."""
    soup = BeautifulSoup(raw_html, "html.parser")

    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()
    for tag in soup(_DROP):
        tag.decompose()

    md = _to_md(str(soup), heading_style="ATX")
    return _collapse_blank_lines(md)


def _collapse_blank_lines(text: str) -> str:
    """Trim trailing whitespace and collapse runs of blank lines to one."""
    out: list[str] = []
    blanks = 0
    for line in text.splitlines():
        line = line.rstrip()
        if line:
            blanks = 0
            out.append(line)
        else:
            blanks += 1
            if blanks == 1:
                out.append("")
    return "\n".join(out).strip() + "\n"
