"""Tests for the Obsidian-vault projection layer's handling of session findings.

Phase 6 contract:
* Each Session<Kind> node gets its own page (one file per node).
* Pages live under ``sessions/<session-id-slug>/`` per-session subdirectory.
* The existing user-notes survival contract still holds: notes written
  between USER_NOTES_START/END survive a recompile.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tesserae.markdown_projection import (
    GraphMarkdownProjector,
    USER_NOTES_END,
    USER_NOTES_START,
    directory_for_node,
)
from tesserae.research_graph import (
    ResearchEdge,
    ResearchGraph,
    ResearchNode,
    ResearchNodeType,
)


def _finding(
    *, id: str, kind: ResearchNodeType, body: str, session_id: str = "sess-1"
) -> ResearchNode:
    return ResearchNode(
        id=id,
        name=body,
        type=kind,
        metadata={"session_id": session_id},
    )


def _session_node(session_id: str = "sess-1") -> ResearchNode:
    return ResearchNode(
        id=f"Session:{session_id}",
        name=f"Session — {session_id}",
        type=ResearchNodeType.SESSION,
        metadata={"session_id": session_id, "started_at": "2026-05-19T10:00:00Z"},
    )


def test_directory_for_finding_groups_by_session():
    a = _finding(
        id="SessionInsight:a",
        kind=ResearchNodeType.SESSION_INSIGHT,
        body="A",
        session_id="sess-A",
    )
    b = _finding(
        id="SessionDecision:b",
        kind=ResearchNodeType.SESSION_DECISION,
        body="B",
        session_id="sess-B",
    )
    assert directory_for_node(a) == "sessions/sess-a"
    assert directory_for_node(b) == "sessions/sess-b"


def test_directory_for_finding_without_session_metadata_falls_back():
    """Defensive: a finding missing session_id metadata still lands somewhere."""
    n = ResearchNode(
        id="SessionInsight:orphan",
        name="Orphan finding",
        type=ResearchNodeType.SESSION_INSIGHT,
    )
    assert directory_for_node(n) == "sessions"


def test_session_findings_produce_one_file_per_node(tmp_path: Path):
    """Phase 6 invariant: bundled-files plan v1 abandoned in favour of
    one-page-per-finding to preserve the user-notes survival contract."""
    graph = ResearchGraph(
        nodes=[
            _session_node("sess-1"),
            _finding(
                id="SessionInsight:i1",
                kind=ResearchNodeType.SESSION_INSIGHT,
                body="Path index needs basename fallback suppression",
            ),
            _finding(
                id="SessionDecision:d1",
                kind=ResearchNodeType.SESSION_DECISION,
                body="Cache findings by content hash",
            ),
            _finding(
                id="SessionInsight:i2",
                kind=ResearchNodeType.SESSION_INSIGHT,
                body="Another insight",
            ),
        ],
        edges=[],
    )

    projector = GraphMarkdownProjector()
    projector.write_projection(graph, tmp_path)

    sessions_dir = tmp_path / "sessions" / "sess-1"
    assert sessions_dir.exists(), "per-session subdirectory should be created"

    files = sorted(p.name for p in sessions_dir.glob("*.md"))
    assert len(files) == 3, (
        f"expected one .md file per finding (2 insights + 1 decision); got {files}"
    )


def test_user_notes_survive_recompile_in_finding_page(tmp_path: Path):
    """A user can add notes to a finding page; the next projection
    must preserve them. This is the projection layer's contract — Phase
    6 must not break it for the new Session<Kind> pages."""
    graph = ResearchGraph(
        nodes=[
            _session_node("sess-notes"),
            _finding(
                id="SessionInsight:i1",
                kind=ResearchNodeType.SESSION_INSIGHT,
                body="Insight body",
                session_id="sess-notes",
            ),
        ],
        edges=[],
    )

    projector = GraphMarkdownProjector()
    projector.write_projection(graph, tmp_path)

    # Find the finding's file and inject a user-notes block.
    insight_files = list((tmp_path / "sessions" / "sess-notes").glob("*.md"))
    assert len(insight_files) == 1
    insight_file = insight_files[0]
    body = insight_file.read_text(encoding="utf-8")
    user_note = "\nThis is my personal annotation about this insight.\n"
    new_body = body.replace(
        f"{USER_NOTES_START}\n",
        f"{USER_NOTES_START}\n{user_note}",
        1,
    )
    # Sanity: replacement must have happened.
    assert USER_NOTES_START in new_body
    assert user_note in new_body
    insight_file.write_text(new_body, encoding="utf-8")

    # Re-project; the user note must survive.
    projector.write_projection(graph, tmp_path)
    after = insight_file.read_text(encoding="utf-8")
    assert user_note in after, "user notes inside the user-notes block must survive"
