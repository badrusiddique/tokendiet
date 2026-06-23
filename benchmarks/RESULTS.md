# Benchmark results

_Generated 2026-06-23 by `python benchmarks/run.py`. Numbers are **estimates** (tiktoken proxy + documented image-token heuristic); regenerate locally to reproduce._

| Document | Pages | Native (tok) | Markdown (tok) | Saved | % saved | $ saved/call (Opus) |
|---|--:|--:|--:|--:|--:|--:|
| article.html | 0 | 6,643 | 1,897 | 4,746 | 71% | $0.0237 |
| paper-attention.pdf | 15 | 48,830 | 10,820 | 38,010 | 78% | $0.1900 |
| prose.pdf | 4 | 12,703 | 3,435 | 9,268 | 73% | $0.0463 |
| report.pdf | 2 | 5,687 | 1,053 | 4,634 | 81% | $0.0232 |
| wikipedia-markdown.html | 0 | 64,229 | 9,513 | 54,716 | 85% | $0.2736 |
| **Total** | | **138,092** | **26,718** | **111,374** | **81%** | **$0.5569** |

## Method

- **PDF native tokens** = extracted text tokens + per-page image tokens. Claude renders each page to an image (capped at 1568px longest edge) and tokenizes it via `tokens ≈ (w·h)/750`, *on top of* the text. The win is the eliminated image tokens.
- **HTML native tokens** = tokens of the raw markup you'd otherwise feed Claude (tags, attributes, inline scripts and styles). The win is shedding that markup.
- **Markdown tokens** = tokens of the converted Markdown (text only).
- **Text counting** uses `tiktoken` `cl100k_base` as a proxy for Claude's tokenizer (within ~10-20% for English prose).

## Caveats

- Figures, charts, and equation images are **lost** in Markdown. For documents where Claude must *see* the visuals, the native PDF is the right choice and these savings do not apply.
- Scanned/image-only PDFs have little text to extract; Tokendiet warns and recommends native or OCR.
- HTML conversion strips scripts/styles/head but keeps structural content, so it never silently drops real text.
- Generated docs (`prose.pdf`, `report.pdf`, `article.html`) are reproducible; `paper-attention.pdf` and `wikipedia-markdown.html` are downloaded at runtime and not redistributed.
