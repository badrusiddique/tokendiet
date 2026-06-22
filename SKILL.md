---
name: tokendiet
description: >-
  Convert PDFs, HTML files, and web-page URLs to lean Markdown before reading them, to save
  Claude tokens and money. Use when the user references, attaches, uploads, or asks to read /
  analyze / summarize / extract from a PDF or HTML file (or a .pdf/.html path), or gives a
  web-page URL to read, and the goal is the TEXT rather than the visual layout. Also use when
  the user asks how many tokens a document will cost, or how to reduce token usage from
  documents/web pages. Do NOT use when the user needs Claude to SEE the visuals (charts,
  diagrams, scans, complex layouts) — read those natively.
---

# Tokendiet — read documents cheaply

Claude pays for a PDF twice: the extracted **text** *and* a rendered **image of every
page**. Web pages are worse — raw HTML is mostly markup (tags, scripts, styles). For
text-heavy content those extra tokens are waste. Tokendiet converts to Markdown so you read
the lean text-only version, and reports what was saved. Supports **PDF, HTML files, and URLs**.

## When to use vs. not

- **Use it** when the user wants the *content/text* of a PDF, HTML file, or web page (read,
  summarize, extract, Q&A over a report, paper, contract, manual, or article).
- **Skip it** when the user needs the *visuals* — charts, diagrams, infographics, scanned
  pages, math-as-images, complex multi-column layout. Read those natively. Tokendiet also
  warns when a PDF looks scanned/image-only.

## How to use it

1. **Check the CLI is available** (once per session):
   ```bash
   tokendiet --version
   ```
   If it's missing, tell the user to install it (see the repo's `docs/getting-started.md`)
   and stop — do not fall back to reading the PDF natively without telling them.

2. **Convert, asking for a JSON report** (works for a PDF, an `.html` file, or a URL):
   ```bash
   tokendiet convert "<path/to/file.pdf>" --report json
   tokendiet convert "https://example.com/article" --report json
   ```
   The JSON includes `output` (the `.md` path), `saved_tokens`, `pct_saved`, and
   `dollar_savings`. If `warnings` mentions a scanned/image-only PDF, **stop and tell the
   user** — the Markdown will be near-empty; offer to read the PDF natively instead.

3. **Read the Markdown, not the PDF.** Open the `.md` from `output` with your normal file
   read. Do this instead of reading the original `.pdf`.

4. **Surface the savings** to the user in one short line, e.g.:
   > Converted with Tokendiet — ~38,010 tokens saved (78%), ≈ $0.19/call on Opus.

## Notes

- Numbers are **estimates** (clearly labelled). They're conservative and close; for exact
  counts, Anthropic's `count_tokens` API is authoritative.
- Tokendiet is **convert-on-reference**: it acts when you reference a PDF, not via a
  magic upload hook. Be honest about that with users.
- Supported formats grow by version (PDF in v0.1). Run `tokendiet convert --help` to see
  what the installed version supports.
