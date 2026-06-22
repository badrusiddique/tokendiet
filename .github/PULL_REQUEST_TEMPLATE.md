# Summary

<!-- What does this PR do and why? -->

## Checklist

- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass
- [ ] `uv run pytest` passes
- [ ] Benchmark still runs: `python benchmarks/make_corpus.py --no-remote && python benchmarks/run.py`
- [ ] If this adds/changes a format: the benchmark shows it **actually saves token-$** (or it's documented as skipped)
- [ ] Any savings claims are honest, measured, and reproducible
- [ ] `CHANGELOG.md` updated
