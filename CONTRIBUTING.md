# Contributing to Tokendiet

Thanks for your interest! Tokendiet has one hard rule that shapes everything:

> **Every savings claim must be honest, measured, and reproducible.** No borrowed marketing
> numbers, no fake before/after, no silently dropping a format's downsides.

## Dev setup

```bash
git clone https://github.com/badrusiddique/tokendiet
cd tokendiet
uv sync --extra anthropic        # creates .venv and installs deps + dev tools
```

## Before opening a PR

```bash
uv run ruff check .              # lint
uv run ruff format --check .     # format
uv run pytest                    # all tests must pass
uv run python benchmarks/make_corpus.py --no-remote && uv run python benchmarks/run.py
```

CI runs the same. PRs must be green.

## Adding a new format (the bar)

A new format ships **only if the benchmark proves it saves token-$.** To add one:

1. Implement a backend in `src/tokendiet/convert.py` and register it in `_BACKENDS`.
2. Add a representative sample to the benchmark corpus (`benchmarks/make_corpus.py`).
3. Add tests (golden conversion + edge cases) mirroring the PDF ones.
4. Run the benchmark. If the format **doesn't** save meaningfully, document it as a skipped
   format in the README/CHANGELOG instead of shipping it.

## Releasing (maintainers)

Tokendiet uses [SemVer](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/).
A version is tagged **only after** the full suite and benchmark are green:

1. Update `CHANGELOG.md` and the version in `pyproject.toml` / `__init__.py`.
2. `uv run pytest && uv run ruff check .`
3. Regenerate benchmarks and confirm README numbers still match.
4. Tag `vX.Y.Z` and push.
