import json
from pathlib import Path

import pytest


def test_artifact_is_current_returns_false_when_manifest_missing(tmp_path):
    from llm_wiki.raganything_refresh import _artifact_is_current
    assert _artifact_is_current(tmp_path) is False


def test_artifact_is_current_returns_true_when_meta_matches_head(tmp_path, monkeypatch):
    import llm_wiki.raganything_refresh as mod
    base = tmp_path / ".llm-wiki" / "external" / "raganything"
    base.mkdir(parents=True)
    (base / "manifest.json").write_text("{}", encoding="utf-8")
    (base / "meta.json").write_text(json.dumps({"gitCommitHash": "abc"}), encoding="utf-8")
    monkeypatch.setattr(mod, "_git_head", lambda p: "abc")
    assert mod._artifact_is_current(tmp_path) is True


def test_artifact_is_current_returns_false_when_meta_differs(tmp_path, monkeypatch):
    import llm_wiki.raganything_refresh as mod
    base = tmp_path / ".llm-wiki" / "external" / "raganything"
    base.mkdir(parents=True)
    (base / "manifest.json").write_text("{}", encoding="utf-8")
    (base / "meta.json").write_text(json.dumps({"gitCommitHash": "old"}), encoding="utf-8")
    monkeypatch.setattr(mod, "_git_head", lambda p: "new")
    assert mod._artifact_is_current(tmp_path) is False


def test_discover_sources_returns_non_code_files_only(tmp_path):
    from llm_wiki.raganything_refresh import discover_sources
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("# code")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "spec.md").write_text("# spec")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "paper.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "data" / "img.png").write_bytes(b"\x89PNG\r\n")
    (tmp_path / "data" / "notes.docx").write_bytes(b"PK\x03\x04")
    (tmp_path / ".llm-wiki").mkdir()
    (tmp_path / ".llm-wiki" / "scratch.md").write_text("# excluded")

    sources = sorted(str(p.relative_to(tmp_path)) for p in discover_sources(tmp_path, roots=["docs", "data"]))
    assert sources == ["data/img.png", "data/notes.docx", "data/paper.pdf", "docs/spec.md"]
