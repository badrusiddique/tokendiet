# Changelog

All notable changes to Tokendiet are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- **Video → transcript (Markdown)** — the largest saving measured (~567×: frames→text); needs a Whisper-class ASR engine. Opt-in, benchmark-gated, **fidelity to be measured before shipping**. See [docs/ROADMAP.md](docs/ROADMAP.md).

## [0.6.0] — 2026-06-23

Fidelity hardening — proof that savings don't cost content.

### Added
- `benchmarks/fidelity_check.py` — measures how much source **text survives** each conversion
  and shows what's dropped. Results: PDF **95–98%** (tables kept), HTML keeps the article body
  (only chrome dropped), image OCR **~90–95%** (weaker on small text/numbers).
- **Low-confidence OCR warning** — image conversion now warns (`~NN%`) when mean OCR confidence
  is below 0.6, advising verification of numbers/symbols or native reading.
- "Fidelity — what's preserved, what's lost" section in
  [docs/format-support.md](docs/format-support.md#fidelity--whats-preserved-whats-lost).

### Notes
- Reaffirms the boundary: body **text** is never silently dropped; genuinely **visual** content
  (charts, diagrams, photos, math-as-image) can't survive a text conversion — and the tool warns.

## [0.5.0] — 2026-06-23

Images, and proof that Markdown is the right target.

### Added
- **Image → Markdown via OCR** for `.png/.jpg/.jpeg/.webp/.bmp/.tif/.tiff`, behind the optional
  `ocr` extra (`pip install 'tokendiet[ocr]'`) — `rapidocr-onnxruntime`, CPU-only, models
  bundled, no GPU. Verified **~71% saving** (a text page as an image is ~2,317 tokens; OCR'd
  Markdown ~665). Warns when no text is found (likely a photo, not a document).
- `benchmarks/format_compare.py` — evidence that **Markdown is the right target format**:
  base64/binary are **7×–360× worse**; plain text only beats Markdown by dropping links;
  the real wins are per-input extraction (OCR, transcript). Documented in
  [docs/format-support.md](docs/format-support.md#why-markdown-not-base64-binary-latex-).

### Notes
- OCR is an opt-in extra, so the core install and CI stay light (no OCR models in CI).

## [0.4.0] — 2026-06-23

Deeper HTML savings + verifiable numbers.

### Added
- **Main-content extraction for HTML/URLs** via `trafilatura` (default), with a safe fallback
  to the previous full strip-and-convert when no article body is found — so content is never
  silently dropped. Drops nav/sidebar/footer clutter.
- `benchmarks/ground_truth.py` — validates the with-vs-without saving against Anthropic's real
  `count_tokens` API (run with `ANTHROPIC_API_KEY`), not just the offline estimate.
- `docs/ROADMAP.md` — prioritized, benchmark-gated improvement backlog.

### Changed
- HTML savings improved: live Wikipedia article **74% → 85%**, synthetic article **64% → 71%**;
  new aggregate **81%** (was 75%) across the 5-doc corpus. Links are preserved (`include_links`),
  trading a few tokens for fidelity.
- New runtime dependency: `trafilatura` (pure-Python, CPU-only).
- **Minimum Python is now 3.11** (was 3.9). `trafilatura` needs ≥3.10, and `onnxruntime`
  (pulled in by `pymupdf4llm`'s layout engine) ships no Linux wheel below cp311. Python 3.9/3.10
  are at or near end-of-life. CI runs 3.11 / 3.12 / 3.13.

## [0.3.0] — 2026-06-23

Format scope finalized. **Office formats investigated and deliberately excluded** — with data.

### Added
- `docs/format-support.md` — what Tokendiet supports (PDF, HTML, URLs) and **why DOCX/XLSX/PPTX
  are intentionally not supported**: they have no expensive native form, so Markdown saves
  nothing (it's marginally larger than realistic text extraction).
- `benchmarks/office_probe.py` — reproducible evidence for the above (run with `uv sync --group probe`).

### Changed
- README FAQ now answers DOCX/PPTX/XLSX definitively with measured data instead of "coming soon".
- Office-probe dependencies isolated in a `probe` dependency group (not installed by default or in CI).

### Notes
- No new conversion formats this release — by design. Per the project's rule, a format ships
  only if it genuinely saves token-$; Office files don't.

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

[Unreleased]: https://github.com/badrusiddique/tokendiet/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/badrusiddique/tokendiet/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/badrusiddique/tokendiet/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/badrusiddique/tokendiet/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/badrusiddique/tokendiet/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/badrusiddique/tokendiet/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/badrusiddique/tokendiet/releases/tag/v0.1.0
