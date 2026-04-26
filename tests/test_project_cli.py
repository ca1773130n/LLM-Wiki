import json
import subprocess
import sys

from llm_wiki.cli import main
from llm_wiki.project import ProjectWiki


def test_project_init_creates_llm_wiki_workspace(tmp_path):
    project = tmp_path / "demo-project"
    project.mkdir()

    wiki = ProjectWiki.init(project, name="demo_wiki", source_kind="Repository")

    assert wiki.root == project / ".llm-wiki"
    assert (wiki.root / "config.json").exists()
    assert (wiki.root / "graph.json").exists()
    assert (wiki.root / "manifest.json").exists()
    assert (wiki.root / "markdown_projection").is_dir()
    assert (wiki.root / "cognee_bundle").is_dir()
    config = json.loads((wiki.root / "config.json").read_text(encoding="utf-8"))
    assert config["name"] == "demo_wiki"
    assert config["project_root"] == str(project.resolve())
    assert config["source_kind"] == "Repository"
    assert config["graph_path"] == ".llm-wiki/graph.json"


def test_project_mcp_config_renders_absolute_hermes_snippet(tmp_path):
    project = tmp_path / "demo-project"
    project.mkdir()
    wiki = ProjectWiki.init(project, name="demo_wiki")

    snippet = wiki.render_mcp_config(server_name="demo_project_wiki", pythonpath="/opt/llm-wiki")

    assert "mcp_servers:" in snippet
    assert "demo_project_wiki:" in snippet
    assert 'command: "python3"' in snippet
    assert "llm_wiki.mcp_server" in snippet
    assert str((project / ".llm-wiki" / "graph.json").resolve()) in snippet
    assert 'PYTHONPATH: "/opt/llm-wiki"' in snippet


def test_project_ingest_updates_standard_artifacts(tmp_path):
    project = tmp_path / "demo-project"
    project.mkdir()
    docs = project / "docs"
    docs.mkdir()
    (docs / "paper.md").write_text("# Demo Paper\nGaussian Splatting supports novel view synthesis.", encoding="utf-8")
    wiki = ProjectWiki.init(project, source_kind="Paper")

    result = wiki.ingest([docs], trends=False)

    assert result["node_count"] > 0
    assert result["edge_count"] > 0
    graph = json.loads((project / ".llm-wiki" / "graph.json").read_text(encoding="utf-8"))
    assert any(node["name"] == "Demo Paper" for node in graph["nodes"])
    assert (project / ".llm-wiki" / "sqlite.db").exists()
    assert (project / ".llm-wiki" / "markdown_projection" / "index.md").exists()
    assert (project / ".llm-wiki" / "cognee_bundle" / "nodes.jsonl").exists()


def test_cli_project_init_ingest_and_mcp_config_from_working_directory(tmp_path, capsys):
    project = tmp_path / "demo-project"
    project.mkdir()
    note = project / "note.md"
    note.write_text("# Project Note\nGaussian Splatting supports novel view synthesis.", encoding="utf-8")

    assert main(["project", "init", "--project", str(project), "--name", "demo_wiki", "--source-kind", "Paper"]) == 0
    assert main(["project", "ingest", "--project", str(project), "note.md"]) == 0
    assert main(["project", "mcp-config", "--project", str(project), "--server-name", "demo_wiki"]) == 0

    captured = capsys.readouterr().out
    assert "Initialized project wiki" in captured
    assert "Ingested project wiki" in captured
    assert "mcp_servers:" in captured
    assert "demo_wiki:" in captured
    assert (project / ".llm-wiki" / "graph.json").exists()


def test_cli_module_can_init_from_current_working_directory(tmp_path):
    project = tmp_path / "cwd-project"
    project.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "llm_wiki.cli", "project", "init", "--name", "cwd_wiki"],
        cwd=project,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PYTHONPATH": "/Users/neo/Developer/Projects/LLM-Wiki"},
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert (project / ".llm-wiki" / "config.json").exists()
    assert "Initialized project wiki" in result.stdout
