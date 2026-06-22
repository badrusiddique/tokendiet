"""Document -> Markdown conversion engine.

v0.1 supports PDF via PyMuPDF (``pymupdf4llm``). The backend interface is kept
deliberately small so later versions can register HTML / DOCX / etc. backends
without touching callers: a backend is a function
``(Path) -> ConversionResult``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

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


@dataclass
class ConversionResult:
    """Everything downstream (reporter, CLI) needs about one conversion."""

    source: Path
    markdown: str
    page_dims: list[tuple[float, float]]  # (width_pt, height_pt) per page
    warnings: list[str] = field(default_factory=list)


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
    return ConversionResult(source=path, markdown=markdown, page_dims=page_dims, warnings=warnings)


# Backend registry: extension -> converter function.
_BACKENDS: dict[str, Callable[[Path], ConversionResult]] = {
    ".pdf": _convert_pdf,
}


def supported_formats() -> list[str]:
    return sorted(_BACKENDS)


def convert(path: str | Path) -> ConversionResult:
    """Convert a supported document to Markdown.

    Raises :class:`UnsupportedFormatError` for unknown extensions and
    :class:`EncryptedPDFError` for locked PDFs.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    backend = _BACKENDS.get(path.suffix.lower())
    if backend is None:
        raise UnsupportedFormatError(
            f"No backend for '{path.suffix}'. Supported: {', '.join(supported_formats())}"
        )
    return backend(path)
