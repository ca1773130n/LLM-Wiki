import json

from tesserae.understand_anything_refresh import refresh_understand_anything


def test_managed_refresh_skips_when_existing_graph_matches_git_head(tmp_path, monkeypatch, capsys):
    project = tmp_path / "demo"
    project.mkdir()
    ua = project / ".understand-anything"
    ua.mkdir()
    (ua / "knowledge-graph.json").write_text('{"nodes": [], "edges": []}\n', encoding="utf-8")
    (ua / "meta.json").write_text(json.dumps({"gitCommitHash": "abc123"}), encoding="utf-8")

    monkeypatch.setattr("tesserae.understand_anything_refresh._git_head", lambda root: "abc123")

    assert refresh_understand_anything(project, platform="codex") == 0
    assert "already current" in capsys.readouterr().out


def test_managed_refresh_runs_agent_cli_and_requires_artifact(tmp_path, monkeypatch):
    project = tmp_path / "demo"
    project.mkdir()
    calls = []

    def fake_build(platform, root, *, full):
        assert platform == "codex"
        assert root == project.resolve()
        assert full is True
        return ["fake-codex", "exec"]

    class Completed:
        returncode = 0

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        ua = project / ".understand-anything"
        ua.mkdir()
        (ua / "knowledge-graph.json").write_text('{"nodes": [], "edges": []}\n', encoding="utf-8")
        return Completed()

    monkeypatch.setattr("tesserae.understand_anything_refresh.build_agent_command", fake_build)
    monkeypatch.setattr("tesserae.understand_anything_refresh.subprocess.run", fake_run)

    assert refresh_understand_anything(project, platform="codex", full=True) == 0
    assert calls and calls[0][0] == ["fake-codex", "exec"]
    assert calls[0][1]["cwd"] == project.resolve()
