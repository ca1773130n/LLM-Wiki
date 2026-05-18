"""Tests for the SessionGraphExtractor orchestrator's caching layer.

Caching guarantees from the design:
1. Same content_hash + same project_root_hash → no LLM call.
2. Different content_hash → cache miss → new LLM call.
3. Different project_root_hash (cache file copied between projects) →
   cache rejected; re-extraction.
4. Stale cache files (sessions removed from disk) are pruned.
5. Schema-version mismatch → cache rejected.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional, Union

import pytest

from tesserae.harness_sessions import HarnessSession
from tesserae.research_graph import ResearchGraph, ResearchNode, ResearchNodeType
from tesserae.session_graph import (
    CACHE_SCHEMA_VERSION,
    SessionGraphExtractor,
    _project_root_hash,
    _session_content_hash,
)


class _ScriptedClient:
    """Tracks how many times complete_json was called."""

    def __init__(self, responses: List[Optional[Union[dict, list]]]):
        self._responses = list(responses)
        self.calls: int = 0

    def complete_json(self, **kwargs):
        self.calls += 1
        if not self._responses:
            return None
        return self._responses.pop(0)


def _session(*, id: str = "sess-1", title: str = "T", turns: int = 3) -> HarnessSession:
    return HarnessSession(
        id=id,
        slug=id,
        harness="claude-code",
        agent_label="Claude Code",
        project_name="test",
        project_root="/tmp/test",
        started_at="2026-05-19T10:00:00Z",
        title=title,
        metadata={
            "turns": [
                {"role": "user", "text": f"q{i}"} for i in range(turns)
            ],
        },
    )


def _doc_graph() -> ResearchGraph:
    return ResearchGraph(
        nodes=[
            ResearchNode(
                id="Paper:foo",
                name="Foo Paper",
                type=ResearchNodeType.PAPER,
                source_path="docs/foo.md",
            ),
        ],
        edges=[],
    )


def _scripted_finding_response():
    return {
        "findings": [
            {
                "kind": "insight",
                "body": "Cache hits skip the LLM call",
                "turn_ids": [1],
                "references": ["Paper:foo"],
            }
        ]
    }


def _make_extractor(
    tmp_path: Path,
    sessions: List[HarnessSession],
    *,
    client: Optional[_ScriptedClient] = None,
    project_root: Optional[Path] = None,
) -> SessionGraphExtractor:
    root = project_root or (tmp_path / "project")
    root.mkdir(parents=True, exist_ok=True)
    # Make each test session's project_root match `root` so the
    # session_matches_project filter accepts it.
    fixed_sessions = [
        HarnessSession.from_dict({**s.to_dict(), "project_root": str(root.resolve())})
        for s in sessions
    ]
    cache_dir = root / ".tesserae" / "session_findings"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return SessionGraphExtractor(
        project_root=root.resolve(),
        cache_dir=cache_dir,
        doc_graph=_doc_graph(),
        sessions=fixed_sessions,
        json_client=client,
    )


def test_cache_hit_skips_llm_call(tmp_path: Path):
    session = _session()
    client = _ScriptedClient([_scripted_finding_response()])
    extractor = _make_extractor(tmp_path, [session], client=client)

    # First call → miss → LLM hit.
    extractor.extract()
    assert client.calls == 1

    # Second call (fresh extractor instance, same client) → cache hit.
    client2 = _ScriptedClient([_scripted_finding_response()])
    extractor2 = _make_extractor(
        tmp_path, [session], client=client2,
        project_root=extractor.project_root,
    )
    extractor2.extract()
    assert client2.calls == 0, "second extract should hit the cache, not call LLM"


def test_content_hash_change_invalidates_cache(tmp_path: Path):
    session = _session()
    client = _ScriptedClient([_scripted_finding_response()])
    extractor = _make_extractor(tmp_path, [session], client=client)
    extractor.extract()
    assert client.calls == 1

    # Change the session's content (different title, different metadata hash).
    changed = HarnessSession.from_dict({**session.to_dict(), "title": "T2"})
    client2 = _ScriptedClient([_scripted_finding_response()])
    extractor2 = _make_extractor(
        tmp_path, [changed], client=client2,
        project_root=extractor.project_root,
    )
    extractor2.extract()
    assert client2.calls == 1, "changed content_hash must invalidate the cache"


def test_project_root_hash_mismatch_rejects_cache(tmp_path: Path):
    """Cache file copied from another project must not be replayed."""
    session = _session()
    project_a = tmp_path / "project-a"
    project_b = tmp_path / "project-b"

    client_a = _ScriptedClient([_scripted_finding_response()])
    extractor_a = _make_extractor(
        tmp_path, [session], client=client_a, project_root=project_a
    )
    extractor_a.extract()
    assert client_a.calls == 1

    # Simulate someone copying project-a's cache file into project-b's
    # cache dir (e.g. by `cp -R` of the .tesserae/ dir between projects).
    cache_file = next((project_a / ".tesserae/session_findings").glob("*.findings.json"))
    target_cache = project_b / ".tesserae/session_findings"
    target_cache.mkdir(parents=True, exist_ok=True)
    (target_cache / cache_file.name).write_bytes(cache_file.read_bytes())

    # Now run extractor in project-b. The cached project_root_hash points
    # at project-a, so we must reject the cache and re-extract.
    client_b = _ScriptedClient([_scripted_finding_response()])
    extractor_b = _make_extractor(
        tmp_path, [session], client=client_b, project_root=project_b
    )
    extractor_b.extract()
    assert client_b.calls == 1, (
        "cache from a different project_root must be rejected (no replay)"
    )


def test_stale_cache_pruned_on_extract(tmp_path: Path):
    """Cache files for sessions that no longer exist on disk are removed."""
    session = _session(id="sess-current")
    extractor = _make_extractor(tmp_path, [session], client=_ScriptedClient([]))

    # Plant a stale cache file from a long-gone session id.
    stale_path = extractor.cache_dir / "sess-old.findings.json"
    stale_path.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    assert stale_path.exists()

    extractor.extract()
    assert not stale_path.exists(), "stale cache file should be pruned"


def test_no_client_returns_structural_only(tmp_path: Path):
    """With json_client=None, only the structural slice survives."""
    session = _session()
    extractor = _make_extractor(tmp_path, [session], client=None)
    graph = extractor.extract()
    # Structural pass mints one Session node (no decisions in this fixture).
    session_nodes = [n for n in graph.nodes if n.type == ResearchNodeType.SESSION]
    finding_nodes = [
        n for n in graph.nodes
        if n.type.value.startswith("Session") and n.type != ResearchNodeType.SESSION
    ]
    assert len(session_nodes) == 1
    assert finding_nodes == [], "no LLM client → no finding nodes"


def test_session_content_hash_includes_all_fields(tmp_path: Path):
    """Two sessions identical except for `title` must produce different hashes."""
    a = _session(title="T1")
    b = _session(title="T2")
    assert _session_content_hash(a) != _session_content_hash(b)


def test_project_root_hash_is_resolve_stable(tmp_path: Path):
    """Project root hashes are normalized through Path.resolve()."""
    project = tmp_path / "p"
    project.mkdir()
    # `project` and `project/.` resolve to the same path.
    assert _project_root_hash(project) == _project_root_hash(project / ".")
