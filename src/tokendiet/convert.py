"""Document -> Markdown conversion engine.

v0.1 added PDF (PyMuPDF); v0.2 adds HTML (local files and URLs).

A backend is a function ``(Path) -> ConversionResult`` registered by extension.
Each backend is responsible for computing its own *native cost* — the tokens
Claude would spend without conversion — because that cost is format-specific:

* **PDF**: extracted text tokens **plus** a rendered image of every page.
* **HTML**: the raw markup tokens (tags, attributes, scripts, styles). No images.

The reporter just assembles these into a savings report.
"""

from __future__ import annotations

import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .tokens import count_text_tokens, page_image_tokens

try:  # PyMuPDF exposes both names depending on version
    import pymupdf  # type: ignore
except ImportError:  # pragma: no cover - fallback for older PyMuPDF
    import fitz as pymupdf  # type: ignore


class TokendietError(Exception):
    """Base class for Tokendiet errors."""


class UnsupportedFormatError(TokendietError):
    """The file extension has no registered backend."""


class EncryptedPDFError(TokendietError):
    """The PDF is password-protected and cannot be read."""


class FetchError(TokendietError):
    """A URL could not be fetched."""


@dataclass
class ConversionResult:
    """Everything downstream (reporter, CLI) needs about one conversion.

    ``before_text_tokens`` + ``before_image_tokens`` are the native cost; the
    Markdown's own token count (the "after") is computed by the reporter.
    """

    source: str
    markdown: str
    before_text_tokens: int
    before_image_tokens: int
    pages: int = 0
    warnings: list[str] = field(default_factory=list)


# --- PDF --------------------------------------------------------------------
def _convert_pdf(path: Path) -> ConversionResult:
    import pymupdf4llm

    try:
        doc = pymupdf.open(path)
    except Exception as exc:  # corrupt / unreadable
        raise TokendietError(f"Could not open PDF: {exc}") from exc

    try:
        if getattr(doc, "needs_pass", False):
            raise EncryptedPDFError(
                f"{path.name} is password-protected; convert it after removing the password, "
                "or let Claude read it natively."
            )
        page_dims = [(p.rect.width, p.rect.height) for p in doc]
        raw_chars = sum(len(p.get_text().strip()) for p in doc)
        markdown = pymupdf4llm.to_markdown(doc, show_progress=False)
    finally:
        doc.close()

    warnings: list[str] = []
    if page_dims and raw_chars < 50 * len(page_dims):
        warnings.append(
            "Very little text extracted — this looks like a scanned/image-only PDF. "
            "Markdown will lose its content; let Claude read it natively, or OCR it first."
        )
    # Native PDF cost: extracted text (≈ the Markdown's words) + a rendered
    # image per page. The win is the eliminated per-page image tokens.
    before_text = count_text_tokens(markdown)
    before_image = sum(page_image_tokens(w, h) for (w, h) in page_dims)
    return ConversionResult(
        source=str(path),
        markdown=markdown,
        before_text_tokens=before_text,
        before_image_tokens=before_image,
        pages=len(page_dims),
        warnings=warnings,
    )


# --- HTML -------------------------------------------------------------------
def _build_html_result(source: str, raw_html: str) -> ConversionResult:
    from .html import html_to_markdown

    markdown = html_to_markdown(raw_html)
    warnings: list[str] = []
    if not markdown.strip():
        warnings.append("No textual content found in the HTML.")
    # Native HTML cost: the raw markup you'd otherwise feed Claude. No images.
    return ConversionResult(
        source=source,
        markdown=markdown,
        before_text_tokens=count_text_tokens(raw_html),
        before_image_tokens=0,
        pages=0,
        warnings=warnings,
    )


def _convert_html_file(path: Path) -> ConversionResult:
    raw = path.read_text(encoding="utf-8", errors="replace")
    return _build_html_result(str(path), raw)


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "tokendiet"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - user-supplied URL
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def _convert_url(url: str) -> ConversionResult:
    try:
        raw = _fetch(url)
    except Exception as exc:
        raise FetchError(f"Could not fetch {url}: {exc}") from exc
    return _build_html_result(url, raw)


# --- Registry / entry point -------------------------------------------------
_BACKENDS: dict[str, Callable[[Path], ConversionResult]] = {
    ".pdf": _convert_pdf,
    ".html": _convert_html_file,
    ".htm": _convert_html_file,
}


def supported_formats() -> list[str]:
    return sorted(_BACKENDS) + ["http(s):// URLs"]


def convert(path_or_url: str | Path) -> ConversionResult:
    """Convert a supported document (or URL) to Markdown.

    Accepts a file path or an ``http(s)://`` URL. Raises
    :class:`UnsupportedFormatError` for unknown extensions,
    :class:`EncryptedPDFError` for locked PDFs, and :class:`FetchError` for
    unreachable URLs.
    """
    text = str(path_or_url)
    if text.startswith(("http://", "https://")):
        return _convert_url(text)

    path = Path(path_or_url)
    if not path.exists():
        raise FileNotFoundError(path)
    backend = _BACKENDS.get(path.suffix.lower())
    if backend is None:
        raise UnsupportedFormatError(
            f"No backend for '{path.suffix}'. Supported: {', '.join(supported_formats())}"
        )
    return backend(path)
