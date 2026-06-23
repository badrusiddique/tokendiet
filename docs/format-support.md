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

Full, reproducible numbers: [`../benchmarks/RESULTS.md`](../benchmarks/RESULTS.md).

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
