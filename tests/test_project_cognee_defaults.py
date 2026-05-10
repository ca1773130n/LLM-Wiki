import json

from llm_wiki.cli import main
from llm_wiki.project import ProjectWiki, cognify_options_from_config
from llm_wiki.project_setup import build_setup_plan, apply_setup_plan


def test_setup_enables_cognee_backend_by_default(tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "README.md").write_text("# Demo\n", encoding="utf-8")

    plan = build_setup_plan(project)
    result = apply_setup_plan(plan)

    cfg = json.loads(result.config_path.read_text(encoding="utf-8"))
    cognee = cfg["memory_backends"]["cognee"]
    assert cognee["enabled"] is True
    assert cognee["mode"] == "codex_cognify"
    assert cognee["auto_cognify"] is False
    assert cognee["dataset"] == "demo_memory"
    assert cognee["system_root"] == ".llm-wiki/cognee_system"
    assert cognee["data_root"] == ".llm-wiki/cognee_data"
    assert cognee["fail_fast"] is False


def test_compile_uses_configured_cognee_when_auto_cognify_enabled(tmp_path, monkeypatch):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "README.md").write_text("# Demo\nGaussian Splatting supports novel view synthesis.\n", encoding="utf-8")
    wiki = ProjectWiki.init(project, name="demo", source_kind="Repository", sources=["README.md"])
    cfg = wiki.config()
    cfg["memory_backends"] = {
        "cognee": {
            "enabled": True,
            "mode": "add",
            "auto_cognify": True,
            "dataset": "demo_memory",
            "system_root": ".llm-wiki/cognee_system",
            "data_root": ".llm-wiki/cognee_data",
        }
    }
    wiki.paths.config.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    calls = []
    monkeypatch.setattr(ProjectWiki, "_run_cognify", lambda self, options: calls.append(options))

    assert main(["project", "compile", "--project", str(project), "--limit", "1"]) == 0

    assert calls
    assert calls[0].mode == "add"
    assert calls[0].dataset == "demo_memory"
    assert calls[0].system_root == ".llm-wiki/cognee_system"
    assert calls[0].data_root == ".llm-wiki/cognee_data"


def test_compile_cli_cognee_flags_override_config(tmp_path, monkeypatch):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "README.md").write_text("# Demo\nGaussian Splatting supports novel view synthesis.\n", encoding="utf-8")
    wiki = ProjectWiki.init(project, name="demo", source_kind="Repository", sources=["README.md"])
    cfg = wiki.config()
    cfg["memory_backends"] = {"cognee": {"enabled": True, "mode": "add", "auto_cognify": False, "dataset": "configured"}}
    wiki.paths.config.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    calls = []
    monkeypatch.setattr(ProjectWiki, "_run_cognify", lambda self, options: calls.append(options))

    assert main([
        "project", "compile", "--project", str(project), "--limit", "1",
        "--cognee-codex-cognify", "--cognee-dataset", "override_memory",
    ]) == 0

    assert calls
    assert calls[0].mode == "codex_cognify"
    assert calls[0].dataset == "override_memory"


def test_cognify_options_from_config_ignores_disabled_or_manual_cognee(tmp_path):
    cfg = {"memory_backends": {"cognee": {"enabled": True, "auto_cognify": False, "mode": "codex_cognify"}}}
    assert cognify_options_from_config(cfg) is None
    cfg["memory_backends"]["cognee"]["auto_cognify"] = True
    cfg["memory_backends"]["cognee"]["enabled"] = False
    assert cognify_options_from_config(cfg) is None


def test_legacy_project_config_gets_default_cognee_backend():
    from llm_wiki.project import cognee_backend_config

    cognee = cognee_backend_config({"name": "legacy_demo"})

    assert cognee["enabled"] is True
    assert cognee["dataset"] == "legacy_demo_memory"
    assert cognee["auto_cognify"] is False


def test_configured_cognee_failure_warns_and_compile_continues(tmp_path, monkeypatch, capsys):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "README.md").write_text("# Demo\nGaussian Splatting supports novel view synthesis.\n", encoding="utf-8")
    wiki = ProjectWiki.init(project, name="demo", source_kind="Repository", sources=["README.md"])
    cfg = wiki.config()
    cfg["memory_backends"]["cognee"]["auto_cognify"] = True
    cfg["memory_backends"]["cognee"]["fail_fast"] = False
    wiki.paths.config.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    def fail_cognee(self, options):
        raise RuntimeError("cognee missing")

    monkeypatch.setattr(ProjectWiki, "_run_cognify", fail_cognee)

    assert main(["project", "compile", "--project", str(project), "--limit", "1"]) == 0

    out = capsys.readouterr().out
    assert "Cognee cognify warning" in out
    assert "Compiled project wiki" in out


def test_project_ask_uses_configured_cognee_backend(tmp_path, monkeypatch, capsys):
    project = tmp_path / "demo"
    project.mkdir()
    wiki = ProjectWiki.init(project, name="demo", sources=[])
    cfg = wiki.config()
    cfg["memory_backends"] = {"cognee": {"enabled": True, "dataset": "demo_memory"}}
    wiki.paths.config.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    monkeypatch.setattr(
        "llm_wiki.cognee_query.search_cognee",
        lambda question, dataset=None, search_type="INSIGHTS", top_k=8: [f"answer for {question} in {dataset}"],
    )

    assert main(["project", "ask", "What renders Mermaid?", "--project", str(project)]) == 0
    out = capsys.readouterr().out
    assert "Cognee answer" in out
    assert "answer for What renders Mermaid? in demo_memory" in out
