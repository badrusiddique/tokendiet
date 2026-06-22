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

# 2. Convert — PDF, HTML, or a URL
tokendiet convert report.pdf                       # writes report.md + prints savings
tokendiet convert page.html --report json          # machine-readable report
tokendiet convert https://en.wikipedia.org/wiki/Markdown   # fetch + convert a web page
tokendiet convert report.pdf --stdout --quiet > report.md
```

That's it. No GPU, no cloud API, no account.

## Benchmarks

Honest, reproducible, run on your own machine — **no borrowed marketing numbers.** Estimates use `tiktoken` as a proxy for Claude's tokenizer plus Anthropic's documented image-token heuristic.

| Document | Type | Native (tok) | Markdown (tok) | Saved | % |
|---|---|--:|--:|--:|--:|
| Real research paper (arXiv 1706.03762) | PDF, 15p | 48,830 | 10,820 | 38,010 | **78%** |
| Real Wikipedia article (live HTML) | HTML | 64,229 | 16,431 | 47,798 | **74%** |
| Prose (public-domain text) | PDF, 4p | 12,703 | 3,435 | 9,268 | **73%** |
| Bloated article (inline CSS/JS) | HTML | 6,643 | 2,407 | 4,236 | **64%** |
| Report with table | PDF, 2p | 5,687 | 1,053 | 4,634 | **81%** |
| **Total** | | **138,092** | **34,146** | **103,946** | **75%** |

Reproduce:

```bash
python benchmarks/make_corpus.py    # generates docs + downloads the real paper & web page
python benchmarks/run.py            # writes benchmarks/RESULTS.md
```

For **PDF** the savings come from eliminating per-page image tokens; for **HTML** from shedding markup (tags, attributes, inline scripts/styles). Both are the real mechanism, not an artifact. See [`benchmarks/RESULTS.md`](benchmarks/RESULTS.md) for the full method and caveats.

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

Claude then reads `your.md` instead of `your.pdf`, paying for text only. **HTML files and URLs** follow the same path: Tokendiet strips scripts/styles/markup and emits clean Markdown (the native baseline there is the raw markup, not page images).

## Use as a Claude skill

Tokendiet ships a [`SKILL.md`](SKILL.md). Once installed (see [docs/getting-started.md](docs/getting-started.md)), when you reference a PDF or web page in Claude Code, Claude converts it with Tokendiet, reads the lean Markdown, and shows you the savings — instead of burning tokens on the native document.

> **A note on honesty:** a skill triggers on *intent*, not on a file-drop event. Tokendiet is **convert-on-reference**, not a magic upload interceptor. No false promises.

## When *not* to use it

Tokendiet is the wrong tool when the **visuals** are the point:

- Charts, diagrams, infographics, scanned documents, complex multi-column layouts, or math rendered as images — Markdown drops them. Let Claude read the PDF natively.
- Tokendiet detects image-only/scanned PDFs and **warns you** instead of silently producing empty Markdown.

## Comparison

| | Tokendiet | [MarkItDown](https://github.com/microsoft/markitdown) | Plain PDF→MD skills |
|---|---|---|---|
| PDF / HTML / URL → Markdown | ✅ | ✅ / ✅ / ❌ | PDF only |
| **Measured token-$ savings report** | ✅ | ❌ | ❌ |
| Reproducible benchmark in-repo | ✅ | ❌ | ❌ |
| Scanned/visual-loss warnings | ✅ | partial | ❌ |
| Dependency-light (no GPU/cloud) | ✅ | ✅ | varies |

Tokendiet isn't trying to out-parse MarkItDown — it's the one that **shows you the win**.

## FAQ

**Does this really save tokens?** Yes, for text-heavy documents — by removing the per-page image tokens Claude pays on the native path. The benchmark numbers above are reproducible on your machine.

**Are the numbers exact?** They're labelled **estimates** (tiktoken proxy + documented image heuristic). For exact figures, validate against Anthropic's `count_tokens` API; the offline estimate is designed to be close and conservative.

**What about DOCX / PPTX / XLSX?** Coming in later versions — but **only** formats our benchmark proves actually save token-$. Formats that don't will be documented as skipped, not shipped for show. See the [CHANGELOG](CHANGELOG.md).

**Roadmap?** PDF (v0.1 ✓) → HTML + URLs (v0.2 ✓, 74% on a live Wikipedia page) → Office/images (v0.3, benchmark-gated).

## License

[MIT](LICENSE) © Badru Siddique
