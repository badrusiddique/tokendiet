# Getting started

Tokendiet is two things in one repo:

1. a **CLI** (`tokendiet`) that converts documents to Markdown and reports token-$ saved, and
2. a **Claude skill** (`SKILL.md`) that tells Claude to use that CLI automatically.

## 1. Install the CLI

You need Python 3.9+ and one of `uv`, `pipx`, or `pip`.

```bash
git clone https://github.com/badrusiddique/tokendiet
cd tokendiet

# pick one:
uv tool install .        # recommended — isolated, on your PATH
pipx install .           # also isolated
pip install .            # into the current environment
```

Verify:

```bash
tokendiet --version
tokendiet convert --help
```

Convert something:

```bash
tokendiet convert ~/Downloads/report.pdf
# -> writes report.md and prints the savings report
```

## 2. Install the Claude skill (Claude Code)

Claude Code discovers skills under `~/.claude/skills/<name>/SKILL.md`. Symlink this repo's
skill so updates flow through automatically:

```bash
mkdir -p ~/.claude/skills/tokendiet
ln -sf "$(pwd)/SKILL.md" ~/.claude/skills/tokendiet/SKILL.md
```

(Or copy it if you prefer a snapshot: `cp SKILL.md ~/.claude/skills/tokendiet/`.)

Now, in Claude Code, when you reference a PDF and want its text, Claude will convert it with
Tokendiet, read the Markdown, and tell you what you saved. Make sure the `tokendiet` CLI from
step 1 is on the same PATH Claude Code uses.

### Quick check

In Claude Code: *"Summarize ~/Downloads/report.pdf"* → Claude should run
`tokendiet convert ... --report json`, read the `.md`, and mention the tokens saved.

## 3. claude.ai

The skill format also works on claude.ai, but the conversion CLI must be runnable in that
environment. First-class claude.ai packaging is on the roadmap — for now, Tokendiet targets
the Claude Code workflow where files live on your machine.

## Troubleshooting

- **`tokendiet: command not found`** — the install location isn't on your PATH. With `uv tool
  install`, run `uv tool update-shell` (or add `~/.local/bin` to PATH) and restart your shell.
- **"looks like a scanned/image-only PDF"** — there's no text layer to extract. Read it
  natively, or OCR it first (`ocrmypdf in.pdf out.pdf`).
- **Encrypted PDF** — remove the password first, then convert.
