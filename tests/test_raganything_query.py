import pytest


def test_query_returns_string_via_aquery_when_backend_available(monkeypatch, tmp_path):
    import llm_wiki.raganything_query as mod

    captured = {}

    class FakeRag:
        def __init__(self, **kwargs):
            captured["init"] = kwargs

        async def aquery(self, question, mode="hybrid", vlm_enhanced=False):
            captured["question"] = question
            captured["mode"] = mode
            return "answer-text"

    monkeypatch.setattr(mod, "_load_raganything", lambda cfg: FakeRag(working_dir=cfg["working_dir"]))

    answer = mod.query(
        "What does the paper say?",
        backend_config={
            "enabled": True,
            "working_dir": str(tmp_path),
            "query_mode": "hybrid",
            "vlm_enhanced": True,
        },
    )
    assert answer == "answer-text"
    assert captured["question"] == "What does the paper say?"
    assert captured["mode"] == "hybrid"


def test_query_returns_none_when_disabled(tmp_path):
    from llm_wiki.raganything_query import query
    assert query("q", backend_config={"enabled": False, "working_dir": str(tmp_path)}) is None


def test_query_returns_none_when_module_missing(monkeypatch, tmp_path):
    import llm_wiki.raganything_query as mod

    def boom(cfg):
        raise RuntimeError("raganything not installed")

    monkeypatch.setattr(mod, "_load_raganything", boom)
    assert mod.query("q", backend_config={"enabled": True, "working_dir": str(tmp_path)}) is None
