# Benchmark results

_Generated 2026-06-22 by `python benchmarks/run.py`. Numbers are **estimates** (tiktoken proxy + documented image-token heuristic); regenerate locally to reproduce._

| Document | Pages | Native PDF (tok) | Markdown (tok) | Saved | % saved | $ saved/call (Opus) |
|---|--:|--:|--:|--:|--:|--:|
| paper-attention.pdf | 15 | 48,830 | 10,820 | 38,010 | 78% | $0.1900 |
| prose.pdf | 4 | 12,703 | 3,435 | 9,268 | 73% | $0.0463 |
| report.pdf | 2 | 5,687 | 1,053 | 4,634 | 81% | $0.0232 |
| **Total** | | **67,220** | **15,308** | **51,912** | **77%** | **$0.2596** |

## Method

- **Native PDF tokens** = extracted text tokens + per-page image tokens. Claude renders each page to an image (capped at 1568px longest edge) and tokenizes it via `tokens ≈ (w·h)/750`, *on top of* the text.
- **Markdown tokens** = tokens of the converted Markdown (text only).
- **Text counting** uses `tiktoken` `cl100k_base` as a proxy for Claude's tokenizer (within ~10-20% for English prose).
- The savings come entirely from eliminating the per-page image tokens — the real, honest mechanism.

## Caveats

- Figures, charts, and equation images are **lost** in Markdown. For documents where Claude must *see* the visuals, the native PDF is the right choice and these savings do not apply.
- Scanned/image-only PDFs have little text to extract; Tokendiet warns and recommends native or OCR.
- Generated docs (`prose.pdf`, `report.pdf`) are reproducible; `paper-attention.pdf` is downloaded at runtime and not redistributed.
