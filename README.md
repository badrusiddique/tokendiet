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

# 2. Convert
tokendiet convert report.pdf            # writes report.md + prints savings
tokendiet convert report.pdf --report json   # machine-readable report
tokendiet convert report.pdf --stdout --quiet > report.md
```

That's it. No GPU, no cloud API, no account.

## Benchmarks

Honest, reproducible, run on your own machine — **no borrowed marketing numbers.** Estimates use `tiktoken` as a proxy for Claude's tokenizer plus Anthropic's documented image-token heuristic.

| Document | Pages | Native PDF (tok) | Markdown (tok) | Saved | % |
|---|--:|--:|--:|--:|--:|
| Real research paper (arXiv 1706.03762) | 15 | 48,830 | 10,820 | 38,010 | **78%** |
| Prose (public-domain text) | 4 | 12,703 | 3,435 | 9,268 | **73%** |
| Report with table | 2 | 5,687 | 1,053 | 4,634 | **81%** |
| **Total** | **21** | **67,220** | **15,308** | **51,912** | **77%** |

Reproduce:

```bash
python benchmarks/make_corpus.py    # generates docs + downloads the real paper
python benchmarks/run.py            # writes benchmarks/RESULTS.md
```

The savings come **entirely from eliminating per-page image tokens** — the real mechanism, not an artifact. See [`benchmarks/RESULTS.md`](benchmarks/RESULTS.md) for the full method and caveats.

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

Claude then reads `your.md` instead of `your.pdf`, paying for text only.

## Use as a Claude skill

Tokendiet ships a [`SKILL.md`](SKILL.md). Once installed (see [docs/getting-started.md](docs/getting-started.md)), when you reference a PDF in Claude Code, Claude converts it with Tokendiet, reads the lean Markdown, and shows you the savings — instead of burning tokens on the native PDF.

> **A note on honesty:** a skill triggers on *intent*, not on a file-drop event. Tokendiet is **convert-on-reference**, not a magic upload interceptor. No false promises.

## When *not* to use it

Tokendiet is the wrong tool when the **visuals** are the point:

- Charts, diagrams, infographics, scanned documents, complex multi-column layouts, or math rendered as images — Markdown drops them. Let Claude read the PDF natively.
- Tokendiet detects image-only/scanned PDFs and **warns you** instead of silently producing empty Markdown.

## Comparison

| | Tokendiet | [MarkItDown](https://github.com/microsoft/markitdown) | Plain PDF→MD skills |
|---|---|---|---|
| PDF → Markdown | ✅ | ✅ | ✅ |
| **Measured token-$ savings report** | ✅ | ❌ | ❌ |
| Reproducible benchmark in-repo | ✅ | ❌ | ❌ |
| Scanned/visual-loss warnings | ✅ | partial | ❌ |
| Dependency-light (no GPU/cloud) | ✅ | ✅ | varies |

Tokendiet isn't trying to out-parse MarkItDown — it's the one that **shows you the win**.

## FAQ

**Does this really save tokens?** Yes, for text-heavy documents — by removing the per-page image tokens Claude pays on the native path. The benchmark numbers above are reproducible on your machine.

**Are the numbers exact?** They're labelled **estimates** (tiktoken proxy + documented image heuristic). For exact figures, validate against Anthropic's `count_tokens` API; the offline estimate is designed to be close and conservative.

**What about DOCX / HTML / PPTX?** Coming in later versions — but **only** formats our benchmark proves actually save token-$. Formats that don't will be documented as skipped, not shipped for show. See the [CHANGELOG](CHANGELOG.md).

**Roadmap?** PDF (v0.1) → HTML (v0.2, expected biggest win) → Office/images (v0.3, benchmark-gated).

## License

[MIT](LICENSE) © Badru Siddique
