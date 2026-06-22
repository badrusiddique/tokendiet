---
name: tokendiet
description: >-
  Convert PDFs to lean Markdown before reading them, to save Claude tokens and money.
  Use when the user references, attaches, uploads, or asks to read / analyze / summarize /
  extract from a PDF file (or mentions a .pdf path), and the goal is the document's TEXT
  rather than its visual layout. Also use when the user asks how many tokens a PDF will
  cost, or how to reduce token usage from documents. Do NOT use when the user needs Claude
  to SEE the visuals (charts, diagrams, scans, complex layouts) — read those natively.
---

# Tokendiet — read PDFs cheaply

Claude pays for a PDF twice: the extracted **text** *and* a rendered **image of every
page**. For text-heavy documents those page images are wasted tokens. Tokendiet converts
the PDF to Markdown so you read the text-only version, and reports what was saved.

## When to use vs. not

- **Use it** when the user wants the document's *content/text* (read, summarize, extract,
  Q&A over a report, paper, contract, manual).
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

2. **Convert, asking for a JSON report:**
   ```bash
   tokendiet convert "<path/to/file.pdf>" --report json
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
