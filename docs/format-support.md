# Format support — and what we deliberately skip

Tokendiet has one job: **save tokens by replacing an expensive native form with lean
Markdown.** A format earns support only if it *genuinely* saves token-$ against a
**realistic** baseline. We benchmark before we ship, and we say no when the numbers say no.

## Supported

| Format | Native cost (what you'd otherwise pay) | Typical saving |
|---|---|---|
| **PDF** | Extracted text **+ a rendered image of every page** | ~73–81% |
| **HTML file** | Raw markup: tags, attributes, inline scripts/styles | ~71% |
| **URL (web page)** | Same as HTML, fetched live | ~85% (real Wikipedia article, main-content extraction) |
| **Image** (PNG/JPG/…) | The image tokens Claude pays to *see* it | ~71% (verified, OCR; needs `pip install 'tokendiet[ocr]'`) |

Full, reproducible numbers: [`../benchmarks/RESULTS.md`](../benchmarks/RESULTS.md).

## Why Markdown (not base64, binary, LaTeX, …)?

We measured every plausible target encoding across inputs (`benchmarks/format_compare.py`):

| Encoding | vs Markdown | Verdict |
|---|---|---|
| **Markdown** | 1× | **Right container** — near-minimal *and* keeps structure/links |
| Plain text | ~0.9–1.0× (prose); 0.5× on link-heavy HTML | Marginal, and only cheaper by *dropping* links/tables. Optional. |
| base64 / binary | **7×–360× worse** | Encoding bytes as text *inflates* tokens and the model can't read it. Hard no. |
| LaTeX | more than Markdown for prose | Only compact for **math**; belongs *inside* Markdown, not as the container. |
| HTML / JSON | more than Markdown | More markup per unit of content. |

**Conclusion:** Markdown is the right target. The real savings come from the **per-input
extractor** (text layer for PDF, main-content for HTML, OCR for images, transcript for video) —
all producing Markdown. LaTeX (math) and CSV (tables) are *embeddings within* Markdown, not
replacements. Reproduce: `python benchmarks/format_compare.py`.

## Deliberately **not** supported: DOCX, XLSX, PPTX

Office files look like obvious candidates — but they fail the test. They have **no
expensive native form**:

- Claude does **not** render them as page images (unlike PDF).
- Their realistic text extraction is **already Markdown-sized** — there's no markup bloat to
  shed (unlike HTML).

Converting them to Markdown saves nothing against a realistic baseline. In fact Markdown is
marginally **larger**, because it adds heading/table syntax. Measured with
`benchmarks/office_probe.py`:

| Format | Raw OOXML dump | Clean text (realistic) | Markdown |
|---|--:|--:|--:|
| DOCX | ~2,100 | ~1,100 | ~1,420 |
| XLSX | ~19,200 | ~5,800 | ~5,840 |
| PPTX | ~5,200 | ~1,100 | ~1,310 |

The only "savings" appear against the **Raw OOXML dump** column — i.e. unzipping the file and
pasting its internal XML. Nobody does that; any sane DOCX/XLSX/PPTX reader extracts the text
directly, which is what the **Clean text** column shows. Headlining the OOXML baseline would
be a strawman, so we don't.

> If you need DOCX/XLSX/PPTX → Markdown for *convenience* (not token savings), use
> [MarkItDown](https://github.com/microsoft/markitdown) — it's excellent at exactly that.

### Reproduce it yourself

```bash
uv sync --group probe
python benchmarks/office_probe.py
```

## On the roadmap (benchmark-gated)

- **Images (PNG/JPG/scans) → Markdown via OCR.** This *does* fit the thesis: an image costs
  image tokens just like a PDF page, so OCR'd Markdown eliminates them. Pending a decision on
  a local OCR engine. It will ship only if the benchmark confirms the saving in practice.

Any future format follows the same rule: **prove the saving, or document why we skipped it.**
