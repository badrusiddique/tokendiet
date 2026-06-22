# Changelog

All notable changes to Tokendiet are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- **v0.2.0** — HTML → Markdown (expected the biggest token win; benchmark-gated before any claim).
- **v0.3.0** — DOCX / PPTX / XLSX / image-OCR, **only** for formats the benchmark proves save token-$. Skipped formats will be documented, not shipped for show.

## [0.1.0] — 2026-06-22

First release. PDF core.

### Added
- `tokendiet convert <file.pdf>` CLI — converts PDF to clean Markdown via PyMuPDF.
- **Token-$ savings report** (text + JSON): tokens before/after, % saved, and $ saved
  per model — the project's differentiator.
- Honest token model: text via `tiktoken` proxy, per-page image tokens via Anthropic's
  documented heuristic; savings come from eliminating page-image tokens. All numbers
  labelled as estimates.
- Edge-case handling: encrypted PDFs raise a clear error; scanned/image-only PDFs warn
  instead of producing empty Markdown; unsupported formats are reported.
- Reproducible benchmark harness (`benchmarks/make_corpus.py`, `benchmarks/run.py`) and
  published `RESULTS.md` (77% aggregate reduction across a real arXiv paper, prose, and a
  report-with-table).
- `SKILL.md` for use as a Claude skill (convert-on-reference).
- Full test suite (token math, reporter, conversion edge cases, CLI) and CI.

[Unreleased]: https://github.com/badrusiddique/tokendiet/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/badrusiddique/tokendiet/releases/tag/v0.1.0
