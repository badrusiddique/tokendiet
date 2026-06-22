"""End-to-end CLI tests."""

from __future__ import annotations

import json
from pathlib import Path

from tokendiet.cli import main


def test_cli_convert_writes_markdown_and_report(text_pdf: Path, capsys):
    rc = main(["convert", str(text_pdf), "--report", "json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["pages"] == 2
    assert out["saved_tokens"] > 0
    assert out["output"].endswith(".md")
    assert Path(out["output"]).exists()


def test_cli_convert_custom_out(text_pdf: Path, tmp_path: Path):
    dest = tmp_path / "custom.md"
    rc = main(["convert", str(text_pdf), "--out", str(dest), "--quiet"])
    assert rc == 0
    assert dest.exists() and dest.read_text().strip()


def test_cli_convert_stdout(text_pdf: Path, capsys):
    rc = main(["convert", str(text_pdf), "--stdout", "--quiet"])
    assert rc == 0
    assert capsys.readouterr().out.strip()


def test_cli_convert_html(html_file: Path, capsys):
    rc = main(["convert", str(html_file), "--report", "json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["pages"] == 0
    assert out["saved_tokens"] > 0
    assert Path(out["output"]).exists()


def test_cli_unsupported_returns_2(tmp_path: Path):
    f = tmp_path / "x.xyz"
    f.write_text("hi")
    rc = main(["convert", str(f)])
    assert rc == 2


def test_cli_missing_file_returns_2(tmp_path: Path):
    rc = main(["convert", str(tmp_path / "nope.pdf")])
    assert rc == 2
