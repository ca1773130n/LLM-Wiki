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
