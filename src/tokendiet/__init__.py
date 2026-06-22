"""Tokendiet — convert documents to lean Markdown so Claude reads the cheap version.

Public API:

    from tokendiet import convert, build_savings, format_report

    result = convert("paper.pdf")
    savings = build_savings(result.source.name, result.markdown, result.page_dims)
    print(format_report(savings))
"""

from __future__ import annotations

__version__ = "0.1.0"

from .convert import (
    ConversionResult,
    EncryptedPDFError,
    TokendietError,
    UnsupportedFormatError,
    convert,
    supported_formats,
)
from .report import TokenSavings, build_savings, format_report

__all__ = [
    "__version__",
    "convert",
    "supported_formats",
    "ConversionResult",
    "TokendietError",
    "UnsupportedFormatError",
    "EncryptedPDFError",
    "build_savings",
    "format_report",
    "TokenSavings",
]
