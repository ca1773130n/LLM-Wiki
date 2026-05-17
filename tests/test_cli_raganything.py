from pathlib import Path
from types import SimpleNamespace


def test_cli_setup_passes_raganything_flags_to_plan(tmp_path, monkeypatch):
    from tesserae import cli

    captured = {}

    def fake_build(root, **kwargs):
        captured["root"] = root
        captured.update(kwargs)
        from tesserae.project_setup import SetupPlan
        return SetupPlan(project_root=Path(root), name="demo", sources=["README.md"])

    def fake_apply(plan):
        return SimpleNamespace(
            wiki=SimpleNamespace(root=plan.project_root),
            config_path=plan.project_root / ".tesserae" / "config.json",
            ran_tools=[],
        )

    monkeypatch.setattr(cli, "build_setup_plan", fake_build)
    monkeypatch.setattr(cli, "apply_setup_plan", fake_apply)

    rc = cli.main([
        "project", "setup", "--yes",
        "--project", str(tmp_path),
        "--with-raganything", "--install-raganything",
        "--raganything-parser", "docling",
        "--raganything-extras", "all",
        "--run-raganything",
    ])
    assert rc == 0
    assert captured["include_raganything"] is True
    assert captured["install_raganything"] is True
    assert captured["raganything_parser"] == "docling"
    assert captured["raganything_extras"] == "all"
    assert captured["run_raganything"] is True


def test_cli_with_raganything_alone_passes_none_for_install(tmp_path, monkeypatch):
    from tesserae import cli

    captured = {}

    def fake_build(root, **kwargs):
        captured.update(kwargs)
        from tesserae.project_setup import SetupPlan
        from pathlib import Path
        return SetupPlan(project_root=Path(root), name="demo", sources=["README.md"])

    monkeypatch.setattr(cli, "build_setup_plan", fake_build)
    monkeypatch.setattr(cli, "apply_setup_plan", lambda *a, **kw: SimpleNamespace(
        wiki=SimpleNamespace(root=Path(str(tmp_path))),
        config_path=Path(str(tmp_path)) / ".tesserae" / "config.json",
        ran_tools=[],
    ))

    rc = cli.main([
        "project", "setup", "--yes",
        "--with-raganything",
        "--project", str(tmp_path),
    ])
    assert rc == 0
    # When neither --install-raganything nor --skip-install-raganything is passed,
    # CLI should forward None so build_setup_plan can decide.
    assert captured["install_raganything"] is None


def test_cli_ask_routes_raganything_when_backend_explicit(tmp_path, monkeypatch, capsys):
    """--backend raganything calls raganything_query.query directly."""
    from tesserae import cli
    import json as _json

    # Set up a minimal project on disk
    cfg_dir = tmp_path / ".tesserae"
    cfg_dir.mkdir()
    cfg = {
        "name": "demo",
        "sources": ["README.md"],
        "external_tools": [],
        "memory_backends": {
            "raganything": {
                "enabled": True,
                "working_dir": ".tesserae/external/raganything/working_dir",
                "parser": "docling",
                "query_mode": "hybrid",
            }
        },
    }
    (cfg_dir / "config.json").write_text(_json.dumps(cfg), encoding="utf-8")
    (tmp_path / "README.md").write_text("# demo", encoding="utf-8")

    captured = {}

    def fake_query(question, *, backend_config):
        captured["question"] = question
        captured["backend_config"] = backend_config
        return "raganything-answer"

    import tesserae.raganything_query as rq
    monkeypatch.setattr(rq, "query", fake_query)
    # The CLI imports `query` symbolically; patch the cli reference too if it's bound at call time.
    monkeypatch.setattr(cli, "_raganything_refresh_main", lambda argv: 0, raising=False)

    rc = cli.main([
        "project", "ask", "What does the demo say?",
        "--backend", "raganything",
        "--project", str(tmp_path),
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "RAG-Anything answer:" in out
    assert "raganything-answer" in out
    assert captured["question"] == "What does the demo say?"
    # working_dir should be resolved relative to the project root
    assert str(tmp_path) in captured["backend_config"]["working_dir"]


def test_cli_ask_falls_through_when_raganything_returns_none(tmp_path, monkeypatch, capsys):
    """auto mode: raganything returning None falls through to cognee/wiki."""
    from tesserae import cli
    import json as _json

    cfg_dir = tmp_path / ".tesserae"
    cfg_dir.mkdir()
    cfg = {
        "name": "demo",
        "sources": ["README.md"],
        "external_tools": [],
        "memory_backends": {
            "raganything": {"enabled": True, "working_dir": "wd", "parser": "docling"},
            "cognee": {"enabled": False},  # force fallback to wiki
        },
    }
    (cfg_dir / "config.json").write_text(_json.dumps(cfg), encoding="utf-8")
    (tmp_path / "README.md").write_text("# demo\n\nSome content.", encoding="utf-8")

    import tesserae.raganything_query as rq
    monkeypatch.setattr(rq, "query", lambda q, *, backend_config: None)

    # The wiki fallback must run; it should not crash even with minimal corpus.
    rc = cli.main([
        "project", "ask", "anything",
        "--backend", "auto",
        "--project", str(tmp_path),
    ])
    # rc may be 0 regardless of whether the wiki path returns hits — accept 0 or 2.
    assert rc in (0, 2)
    err = capsys.readouterr().err
    # No "RAG-Anything ask failed" since raganything just returned None silently.
    assert "RAG-Anything ask failed" not in err


def test_cli_refresh_raganything_invokes_refresh_main(monkeypatch):
    from tesserae import cli
    captured = {}

    def fake_refresh_main(argv):
        captured["argv"] = list(argv)
        return 0

    monkeypatch.setattr(cli, "_raganything_refresh_main", fake_refresh_main)
    rc = cli.main(["project", "refresh-raganything", "--parser", "mineru", "--full"])
    assert rc == 0
    assert "--parser" in captured["argv"]
    assert "mineru" in captured["argv"]
    assert "--full" in captured["argv"]
