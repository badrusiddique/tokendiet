<h1 align="center">Tokendiet</h1>

<p align="center">
  <b>Convert PDFs to lean Markdown so Claude reads the cheap version — and see exactly how many tokens (and dollars) you saved.</b>
</p>

<p align="center">
  <a href="#quickstart">Quickstart</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#benchmarks">Benchmarks</a> ·
  <a href="#use-as-a-claude-skill">Claude skill</a> ·
  <a href="#faq">FAQ</a>
</p>

---

## Why

When you hand Claude a PDF, it doesn't just read the text — it **also renders every page to an image and tokenizes that image**, on top of the extracted text. For a text-heavy document, those page images are pure cost: the same words as clean Markdown, at a multiple of the tokens.

**Tokendiet** converts the document to Markdown first, so Claude reads the text-only version. Then — and this is the part other converters skip — it **reports the measured token-$ you saved**, so the win is visible, not hand-waved.

```
$ tokendiet convert paper.pdf
Wrote paper.md
Tokendiet — paper.pdf
  Pages: 15
  Native PDF (estimate): 48,830 tokens (10,820 text + 38,010 image)
  Markdown (estimate):   10,820 tokens
  Saved: 38,010 tokens (78%)
  Saved per call: Claude Opus 4.8: $0.1900, Claude Sonnet 4.6: $0.1140, Claude Haiku 4.5: $0.0380
```

## Quickstart

```bash
# 1. Install (from source for now; PyPI release coming)
git clone https://github.com/badrusiddique/tokendiet
cd tokendiet
uv tool install .          # or: pipx install .   /   pip install .

# 2. Convert — PDF, HTML, a URL, or an image
tokendiet convert report.pdf                       # writes report.md + prints savings
tokendiet convert page.html --report json          # machine-readable report
tokendiet convert https://en.wikipedia.org/wiki/Markdown   # fetch + convert a web page
tokendiet convert scan.png                         # OCR an image (needs the ocr extra)
tokendiet convert report.pdf --stdout --quiet > report.md
```

For image OCR, install the optional engine: `pip install 'tokendiet[ocr]'` (CPU-only, models bundled). Otherwise — no GPU, no cloud API, no account.

## Benchmarks

Honest, reproducible, run on your own machine — **no borrowed marketing numbers.** Estimates use `tiktoken` as a proxy for Claude's tokenizer plus Anthropic's documented image-token heuristic.

| Document | Type | Native (tok) | Markdown (tok) | Saved | % |
|---|---|--:|--:|--:|--:|
| Real research paper (arXiv 1706.03762) | PDF, 15p | 48,830 | 10,820 | 38,010 | **78%** |
| Real Wikipedia article (live HTML)† | HTML | ~64,200 | ~9,500 | ~54,700 | **~85%** |
| Prose (public-domain text) | PDF, 4p | 12,703 | 3,435 | 9,268 | **73%** |
| Bloated article (inline CSS/JS) | HTML | 6,643 | 1,897 | 4,746 | **71%** |
| Report with table | PDF, 2p | 5,687 | 1,053 | 4,634 | **81%** |
| **Total** | | **~138,100** | **~26,700** | **~111,400** | **~81%** |

<sub>† The Wikipedia row is a **live** fetch, so its exact tokens (and the totals) drift a little between runs — shown rounded. The deterministic rows are exact. Run `python benchmarks/run.py` for current numbers.</sub>

Reproduce:

```bash
python benchmarks/make_corpus.py    # generates docs + downloads the real paper & web page
python benchmarks/run.py            # writes benchmarks/RESULTS.md
```

For **PDF** the savings come from eliminating per-page image tokens; for **HTML** from shedding markup (tags, attributes, inline scripts/styles). Both are the real mechanism, not an artifact. See [`benchmarks/RESULTS.md`](benchmarks/RESULTS.md) for the full method and caveats.

**Images** (with the `ocr` extra): sending a page as an image costs ~2,317 tokens; OCR'd Markdown is ~665 — **~71% saved**, verified with a real OCR engine. **Why Markdown and not base64/LaTeX/plain text?** We measured — base64 is 7–360× *worse*; Markdown is the right container. Details: [docs/format-support.md](docs/format-support.md#why-markdown-not-base64-binary-latex-).

## How it works

```
                 ┌──────────────────────────────────────────┐
   your.pdf  ──▶ │  tokendiet convert                        │ ──▶  your.md
                 │  • PyMuPDF extracts structured text        │      (text only)
                 │  • emits clean Markdown                     │
                 │  • estimates native tokens (text + image)  │ ──▶  savings report
                 │  • estimates Markdown tokens               │      (tokens + $)
                 └──────────────────────────────────────────┘
```

Claude then reads `your.md` instead of `your.pdf`, paying for text only. **HTML files and URLs** follow the same path: Tokendiet extracts the main content (via `trafilatura`, falling back to a full strip-and-convert when no article body is found) and emits clean Markdown — shedding nav, sidebars, footers, scripts, and styles. The native baseline there is the raw markup, not page images. **Images** (with the `ocr` extra) are OCR'd to text — replacing the image tokens Claude would pay to *see* the page. Different input, same destination: lean Markdown.

## Use as a Claude skill

Tokendiet ships a [`SKILL.md`](SKILL.md). Once installed (see [docs/getting-started.md](docs/getting-started.md)), when you reference a PDF or web page in Claude Code, Claude converts it with Tokendiet, reads the lean Markdown, and shows you the savings — instead of burning tokens on the native document.

> **A note on honesty:** a skill triggers on *intent*, not on a file-drop event. Tokendiet is **convert-on-reference**, not a magic upload interceptor. No false promises.

## When *not* to use it

Tokendiet is the wrong tool when the **visuals** are the point:

- Charts, diagrams, infographics, scanned documents, complex multi-column layouts, or math rendered as images — Markdown drops them. Let Claude read the PDF natively.
- Tokendiet detects image-only/scanned PDFs, no-text images, and **low-confidence OCR**, and **warns you** instead of silently producing empty or wrong Markdown.

**Does it lose your content?** We measure it ([`benchmarks/fidelity_check.py`](benchmarks/fidelity_check.py)): PDF keeps **95–98%** of the text (tables included), HTML keeps the full article body (only chrome is dropped), image OCR recovers **~90–95%** (weaker on small text/numbers — hence the warning). Body *text* is never silently dropped; only genuinely-visual content can't survive a text conversion. Full breakdown: [docs/format-support.md](docs/format-support.md#fidelity--whats-preserved-whats-lost).

## Comparison

| | Tokendiet | [MarkItDown](https://github.com/microsoft/markitdown) | Plain PDF→MD skills |
|---|---|---|---|
| PDF / HTML / URL / image → Markdown | ✅ | ✅ / ✅ / ❌ / ✅ | PDF only |
| **Measured token-$ savings report** | ✅ | ❌ | ❌ |
| Reproducible benchmark in-repo | ✅ | ❌ | ❌ |
| Scanned/visual-loss warnings | ✅ | partial | ❌ |
| Dependency-light (no GPU/cloud) | ✅ | ✅ | varies |

Tokendiet isn't trying to out-parse MarkItDown — it's the one that **shows you the win**.

## FAQ

**Does this really save tokens?** Yes, for text-heavy documents — by removing the per-page image tokens Claude pays on the native path. The benchmark numbers above are reproducible on your machine.

**Are the numbers exact?** They're labelled **estimates** (tiktoken proxy + documented image heuristic). For exact figures, validate against Anthropic's `count_tokens` API; the offline estimate is designed to be close and conservative.

**What about DOCX / PPTX / XLSX?** **Deliberately not supported** — we measured, and they don't save tokens. Office files have no expensive native form (Claude doesn't image them like PDFs, and their text extraction is already Markdown-sized), so converting them is equal or *larger*. We won't ship a feature that doesn't deliver on the promise. Full data and the reproducible probe: [docs/format-support.md](docs/format-support.md). For convenience conversion, use [MarkItDown](https://github.com/microsoft/markitdown).

**Roadmap?** PDF (v0.1 ✓) → HTML + URLs (v0.2 ✓) → Office investigated & excluded with data (v0.3 ✓) → main-content extraction, 85% on Wikipedia (v0.4 ✓) → images via OCR, 71% verified (v0.5 ✓) → video → transcript (the 567× win, needs ASR). See [docs/ROADMAP.md](docs/ROADMAP.md).

## License

[MIT](LICENSE) © Badru Siddique
