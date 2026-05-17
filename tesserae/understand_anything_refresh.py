"""Managed Understand Anything refresh runner for Tesserae.

This module gives Tesserae a stable shell entrypoint so users do not need to
know where Understand Anything is installed or how its slash command is exposed
by each coding-agent CLI.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def _git_head(project: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project,
            text=True,
            capture_output=True,
            timeout=20,
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _stored_commit(project: Path) -> str | None:
    meta_path = project / ".understand-anything" / "meta.json"
    if not meta_path.exists():
        return None
    try:
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    for key in ("gitCommitHash", "commit", "head"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _artifact_is_current(project: Path) -> bool:
    artifact = project / ".understand-anything" / "knowledge-graph.json"
    if not artifact.exists():
        return False
    head = _git_head(project)
    if not head:
        return True
    stored = _stored_commit(project)
    return stored == head


def _prompt(project: Path, *, full: bool) -> str:
    flag = " --full" if full else ""
    return (
        f"/understand{flag} {project}\n\n"
        "Run Understand Anything for this project and finish only after "
        ".understand-anything/knowledge-graph.json has been written."
    )


def build_agent_command(platform: str, project: Path, *, full: bool) -> list[str]:
    platform = platform.lower().strip()
    prompt = _prompt(project, full=full)
    if platform == "codex":
        binary = shutil.which("codex")
        if not binary:
            raise RuntimeError("Codex CLI not found on PATH; install Codex or choose another Understand Anything platform.")
        return [binary, "exec", "--full-auto", prompt]
    if platform == "opencode":
        binary = shutil.which("opencode")
        if not binary:
            raise RuntimeError("OpenCode CLI not found on PATH; install OpenCode or choose another Understand Anything platform.")
        return [binary, "run", prompt]
    if platform == "claude":
        binary = shutil.which("claude")
        if not binary:
            raise RuntimeError("Claude Code CLI not found on PATH; install Claude Code or choose another Understand Anything platform.")
        return [binary, "-p", prompt, "--max-turns", "40"]
    raise RuntimeError(f"Unsupported Understand Anything platform: {platform}")


def refresh_understand_anything(
    project: str | Path,
    *,
    platform: str = "codex",
    full: bool = False,
    force: bool = False,
    timeout: int | None = None,
) -> int:
    root = Path(project).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Understand Anything refresh failed: project directory does not exist: {root}", file=sys.stderr)
        return 2

    if not force and not full and _artifact_is_current(root):
        print("Understand Anything graph is already current; skipping refresh.")
        return 0

    command = build_agent_command(platform, root, full=full or force)
    print(f"Refreshing Understand Anything via {platform}...")
    completed = subprocess.run(command, cwd=root, text=True, timeout=timeout)
    if completed.returncode != 0:
        return completed.returncode

    artifact = root / ".understand-anything" / "knowledge-graph.json"
    if not artifact.exists():
        print(
            "Understand Anything command completed but did not write .understand-anything/knowledge-graph.json",
            file=sys.stderr,
        )
        return 3
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh Understand Anything for an Tesserae project.")
    parser.add_argument("--project", default=".", help="Project root to analyze")
    parser.add_argument("--platform", default="codex", help="Agent platform to run: codex, opencode, or claude")
    parser.add_argument("--full", action="store_true", help="Force /understand --full")
    parser.add_argument("--force", action="store_true", help="Run even if the existing graph appears current")
    parser.add_argument("--timeout", type=int, help="Optional timeout in seconds")
    args = parser.parse_args(list(argv) if argv is not None else None)
    return refresh_understand_anything(
        args.project,
        platform=args.platform,
        full=args.full,
        force=args.force,
        timeout=args.timeout,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
