# Roadmap & improvement backlog

Every item here is **benchmark-gated**: it ships only if it measurably saves token-$ (or
makes the savings verifiable). Numbers below are measured on our own corpus unless marked
"est." Inspiration drawn from MarkItDown, Docling, Marker, trafilatura, Jina ReaderLM, and
Anthropic's own docs.

## Shipped

- **v0.1** PDF → Markdown + savings report
- **v0.2** HTML files + URLs
- **v0.3** Office investigated & excluded with data ([format-support.md](format-support.md))
- **v0.4** Main-content extraction for HTML (trafilatura) + ground-truth tool + this roadmap

## Shipped in v0.4

### 1. Main-content extraction for HTML (trafilatura) — **+11 points on Wikipedia** ✅
The HTML path now extracts just the article body via [trafilatura](https://trafilatura.readthedocs.io),
dropping nav/sidebar/footer, with a safe fallback to the full strip-and-convert when no main
content is found (so content is never silently dropped):

| Page | before (v0.3) | **after (v0.4)** |
|---|--:|--:|
| Live Wikipedia article | 74% | **85%** |
| Bloated synthetic article | 64% | **71%** |

Links are kept (`include_links=True`), which costs some tokens but preserves information —
dropping links would reach ~92% but loses content, so we don't. Pure-Python, CPU-only.

### 2. Ground-truth token counting (`benchmarks/ground_truth.py`) ✅
Validates the with-vs-without saving against Anthropic's real `count_tokens` tokenizer
instead of the tiktoken estimate. Run with `ANTHROPIC_API_KEY` set. Removes all guesswork
from the headline numbers.

## P0 — next

### 3. Strip base64 data-URI images from output — est. 2–8% on image-heavy docs
`![..](data:image/png;base64,...)` blobs bloat Markdown and render nowhere useful. Drop them
(or replace with a short placeholder). ~10 lines, no risk.

## P1 — medium impact / effort

### 4. PDF cross-page header/footer dedup + whitespace collapse — est. 2–5%
"Page X of Y" and running heads repeat on every page. Detect lines recurring on >80% of pages
and drop them; collapse redundant blank lines (we already do this for HTML).

### 5. Prompt-caching guidance (docs, not code)
For repeated queries over the same document, Anthropic [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
cuts repeat input cost ~90%. Tokendiet + caching compound. Document the pattern; no code needed.

### 6. Optional Marker backend for table-heavy PDFs (`--engine marker`) — est. 5–10% fidelity
[Marker](https://github.com/datalab-to/marker) handles complex tables better than
pymupdf4llm, at a heavier install. Keep pymupdf4llm the default; offer Marker as opt-in.

## P2 — situational

### 7. Images (PNG/JPG/scans) → Markdown via OCR
The one remaining format that fits the thesis: an image costs image tokens like a PDF page, so
OCR'd text eliminates them. Needs a local OCR engine (tesseract via `pytesseract`, or
`rapidocr-onnxruntime` — onnxruntime is already pulled in transitively). Benchmark-gate before shipping.

### 8. Optional Jina ReaderLM backend for HTML — est. +5–10% quality over trafilatura
ML-based HTML→Markdown; higher fidelity but ~100× slower and heavier. Opt-in only.

## P3 — explore later

- **LLMLingua-style prompt compression** as an opt-in `--compress` pass (20–40% est., but lossy
  — must be opt-in and clearly labelled, never default).
- **RAG chunking** output mode (`--chunk-for-rag`) if users ask for it.

## Ruled out

- **DOCX / XLSX / PPTX** — measured, no real savings. See [format-support.md](format-support.md).
