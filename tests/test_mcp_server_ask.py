"""Tests for the MCP `ask` tool that mirrors the CLI ``project ask`` dispatcher."""
import json
from pathlib import Path

import pytest


def _write_minimal_project(project: Path, *, raganything_enabled: bool = True, cognee_enabled: bool = False) -> None:
    """Create a minimal .tesserae layout with a graph.json so the MCP registry accepts it."""
    cfg_dir = project / ".tesserae"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg = {
        "name": "demo",
        "sources": ["README.md"],
        "external_tools": [],
        "memory_backends": {
            "raganything": {
                "enabled": raganything_enabled,
                "working_dir": "wd",
                "parser": "docling",
                "query_mode": "hybrid",
            },
            "cognee": {"enabled": cognee_enabled},
        },
    }
    (cfg_dir / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    # Empty but valid graph.json so register_project accepts the path.
    (cfg_dir / "graph.json").write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")
    (project / "README.md").write_text("# demo", encoding="utf-8")


def test_mcp_lists_ask_tool():
    from tesserae.mcp_server import LLMWikiMCPServer

    tools = LLMWikiMCPServer().list_tools()
    by_name = {tool["name"]: tool for tool in tools}
    assert "ask" in by_name
    schema = by_name["ask"]["inputSchema"]
    assert "question" in schema["properties"]
    assert "backend" in schema["properties"]
    assert set(schema["properties"]["backend"]["enum"]) == {"auto", "raganything", "cognee", "wiki"}
    assert "question" in schema["required"]


def test_mcp_ask_routes_to_raganything(tmp_path, monkeypatch):
    from tesserae.mcp_server import LLMWikiMCPServer

    project = tmp_path / "demo"
    _write_minimal_project(project, raganything_enabled=True)

    captured = {}

    def fake_query(question, *, backend_config):
        captured["question"] = question
        captured["backend_config"] = backend_config
        return f"answered:{question}"

    import tesserae.raganything_query as rq
    monkeypatch.setattr(rq, "query", fake_query)

    server = LLMWikiMCPServer(registry_path=tmp_path / "registry.json")
    server.registry.register(str(project), name="demo")

    result = server.call_tool("ask", {"question": "hello?", "backend": "raganything", "project": "demo"})
    assert result["backend"] == "raganything"
    assert result["question"] == "hello?"
    assert result["answer"] == "answered:hello?"
    # working_dir resolved relative to the project
    assert str(project.resolve()) in captured["backend_config"]["working_dir"]


def test_mcp_ask_requires_question(tmp_path):
    from tesserae.mcp_server import LLMWikiMCPServer

    server = LLMWikiMCPServer(registry_path=tmp_path / "registry.json")
    with pytest.raises(ValueError, match="ask requires 'question'"):
        server.call_tool("ask", {"question": "  "})


def test_mcp_ask_falls_through_to_wiki_when_raganything_returns_none(tmp_path, monkeypatch):
    """auto mode + raganything returning None should fall through; cognee disabled means wiki search runs."""
    from tesserae.mcp_server import LLMWikiMCPServer

    project = tmp_path / "demo"
    _write_minimal_project(project, raganything_enabled=True, cognee_enabled=False)

    import tesserae.raganything_query as rq
    monkeypatch.setattr(rq, "query", lambda q, *, backend_config: None)

    server = LLMWikiMCPServer(registry_path=tmp_path / "registry.json")
    server.registry.register(str(project), name="demo")

    result = server.call_tool("ask", {"question": "anything", "backend": "auto", "project": "demo"})
    # Wiki fallback path returned a structured QueryResult-shaped dict, with backend=wiki.
    assert result["backend"] == "wiki"
    assert result["question"] == "anything"


def test_mcp_ask_explicit_raganything_returns_note_when_no_answer(tmp_path, monkeypatch):
    from tesserae.mcp_server import LLMWikiMCPServer

    project = tmp_path / "demo"
    _write_minimal_project(project, raganything_enabled=True)

    import tesserae.raganything_query as rq
    monkeypatch.setattr(rq, "query", lambda q, *, backend_config: None)

    server = LLMWikiMCPServer(registry_path=tmp_path / "registry.json")
    server.registry.register(str(project), name="demo")

    result = server.call_tool("ask", {"question": "q", "backend": "raganything", "project": "demo"})
    assert result["backend"] == "raganything"
    assert result["answer"] is None
    assert "no answer" in result.get("note", "")
