# Changelog

All notable changes to Tokendiet are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- **v0.3.0** — DOCX / PPTX / XLSX / image-OCR, **only** for formats the benchmark proves save token-$. Skipped formats will be documented, not shipped for show.

## [0.2.0] — 2026-06-22

HTML support.

### Added
- **HTML → Markdown** for local `.html`/`.htm` files **and** `http(s)://` URLs
  (`tokendiet convert https://…`). Strips scripts/styles/head and converts the rest, keeping
  structural content so no real text is silently dropped.
- Format-aware savings: HTML's native baseline is the raw markup tokens (no page images),
  while PDF's remains text + page-image tokens — each backend computes its own native cost.
- Benchmark corpus extended with a generated bloated article and a live Wikipedia page.
  **HTML reduction: 74% on a real Wikipedia article**; new aggregate **75%** across 5 docs.

### Changed
- `build_savings()` now takes a `ConversionResult` (internal API; pre-1.0).
- `ConversionResult` carries `before_text_tokens` / `before_image_tokens` / `pages`.

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

[Unreleased]: https://github.com/badrusiddique/tokendiet/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/badrusiddique/tokendiet/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/badrusiddique/tokendiet/releases/tag/v0.1.0
