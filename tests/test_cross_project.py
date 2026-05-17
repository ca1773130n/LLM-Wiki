"""Tests for the cross-project ``wiki://`` URI resolver.

Bet B2 — the registry is a graph substrate. Source markdown in one
Tesserae project can reference a node in a sibling registered project by
stable URI; this module is the resolver layer those bridges depend on.
"""

from __future__ import annotations

import json
from pathlib import Path


def test_parse_wiki_uri_accepts_standard_form():
    from tesserae.cross_project import parse_wiki_uri

    assert parse_wiki_uri("wiki://research/concepts/rlhf") == (
        "research", "concepts", "rlhf",
    )
    assert parse_wiki_uri("wiki://my-vault/papers/arxiv-2510-12323") == (
        "my-vault", "papers", "arxiv-2510-12323",
    )
    # Unicode slugs (Korean) — localized docs round-trip through the
    # canonical slug builder, so the URI scheme must accept them too.
    assert parse_wiki_uri("wiki://x/concepts/한국어-slug") == (
        "x", "concepts", "한국어-slug",
    )


def test_parse_wiki_uri_strips_trailing_html_extension():
    from tesserae.cross_project import parse_wiki_uri

    assert parse_wiki_uri("wiki://research/concepts/rlhf.html") == (
        "research", "concepts", "rlhf",
    )


def test_parse_wiki_uri_rejects_garbage():
    from tesserae.cross_project import parse_wiki_uri

    assert parse_wiki_uri("http://example.com") is None
    assert parse_wiki_uri("wiki://") is None
    assert parse_wiki_uri("wiki://a/b") is None  # missing slug segment
    assert parse_wiki_uri("") is None
    assert parse_wiki_uri("not even close") is None


def test_cross_project_resolve_unregistered_alias_returns_tombstone(tmp_path):
    """Tombstone path: the alias is not in the registry."""
    from tesserae.cross_project import cross_project_resolve
    from tesserae.mcp_server import ProjectRegistry

    registry = ProjectRegistry(path=tmp_path / "registry.json")
    ref = cross_project_resolve(
        "wiki://nope/concepts/foo",
        registry=registry,
    )
    assert ref.alias == "nope"
    assert ref.kind == "concepts"
    assert ref.slug == "foo"
    assert ref.is_resolvable is False
    assert ref.is_built is False
    assert ref.project_root is None
    assert ref.page_path is None


def test_cross_project_resolve_registered_and_built(tmp_path):
    """Happy path: alias registered, page exists on disk."""
    from tesserae.cross_project import cross_project_resolve
    from tesserae.mcp_server import ProjectRegistry

    sibling = tmp_path / "sibling"
    sibling.mkdir()
    page_dir = sibling / ".tesserae" / "site" / "concepts"
    page_dir.mkdir(parents=True)
    (page_dir / "rlhf.html").write_text("<html>...</html>", encoding="utf-8")
    # ProjectRegistry.register() expects ``.tesserae/graph.json`` so the
    # discovery path picks the root up.
    (sibling / ".tesserae" / "graph.json").write_text("{}", encoding="utf-8")

    registry = ProjectRegistry(path=tmp_path / "registry.json")
    registry.register(str(sibling), name="sibling")

    ref = cross_project_resolve(
        "wiki://sibling/concepts/rlhf",
        registry=registry,
    )
    assert ref.is_resolvable
    assert ref.is_built
    assert ref.page_path is not None
    assert ref.page_path.name == "rlhf.html"


def test_cross_project_resolve_registered_but_unbuilt(tmp_path):
    """Registered but page not built yet — returns is_built=False."""
    from tesserae.cross_project import cross_project_resolve
    from tesserae.mcp_server import ProjectRegistry

    sibling = tmp_path / "sibling"
    sibling.mkdir()
    (sibling / ".tesserae").mkdir()
    (sibling / ".tesserae" / "graph.json").write_text("{}", encoding="utf-8")

    registry = ProjectRegistry(path=tmp_path / "registry.json")
    registry.register(str(sibling), name="sibling")

    ref = cross_project_resolve(
        "wiki://sibling/concepts/never-built",
        registry=registry,
    )
    assert ref.is_resolvable
    assert ref.is_built is False
    assert ref.page_path is None


def test_cross_project_resolve_invalid_uri_raises():
    from tesserae.cross_project import cross_project_resolve

    import pytest

    with pytest.raises(ValueError):
        cross_project_resolve("not a wiki uri")


def test_cross_project_resolve_never_raises_on_corrupt_registry(tmp_path, monkeypatch):
    """Registry corruption must NOT crash compile or serve."""
    from tesserae.cross_project import cross_project_resolve
    from tesserae.mcp_server import ProjectRegistry

    registry_path = tmp_path / "registry.json"
    registry_path.write_text("{not valid json", encoding="utf-8")
    registry = ProjectRegistry(path=registry_path)
    ref = cross_project_resolve(
        "wiki://anything/concepts/foo",
        registry=registry,
    )
    assert ref.is_resolvable is False


def test_render_cross_project_link_emits_tombstone_when_unregistered(tmp_path, monkeypatch):
    """Tombstone styling kicks in when the alias is unregistered."""
    from tesserae.cross_project import render_cross_project_link
    import tesserae.cross_project as cp
    from tesserae.mcp_server import ProjectRegistry

    monkeypatch.setattr(
        cp,
        "ProjectRegistry",
        lambda: ProjectRegistry(path=tmp_path / "registry.json"),
    )

    out = render_cross_project_link("wiki://missing/concepts/x", label="X")
    assert "wiki-link-tombstone" in out
    assert "X" in out


def test_render_cross_project_link_emits_anchor_when_built(tmp_path, monkeypatch):
    """Live link styling when the sibling has built the target page."""
    from tesserae.cross_project import render_cross_project_link
    import tesserae.cross_project as cp
    from tesserae.mcp_server import ProjectRegistry

    sibling = tmp_path / "sibling"
    page_dir = sibling / ".tesserae" / "site" / "concepts"
    page_dir.mkdir(parents=True)
    (page_dir / "rlhf.html").write_text("<html>x</html>", encoding="utf-8")
    (sibling / ".tesserae" / "graph.json").write_text("{}", encoding="utf-8")

    registry = ProjectRegistry(path=tmp_path / "registry.json")
    registry.register(str(sibling), name="sibling")

    monkeypatch.setattr(
        cp,
        "ProjectRegistry",
        lambda: ProjectRegistry(path=tmp_path / "registry.json"),
    )

    out = render_cross_project_link("wiki://sibling/concepts/rlhf", label="RLHF")
    assert "wiki-link-cross" in out
    assert 'data-cross-project="sibling"' in out
    assert "RLHF" in out


def test_render_cross_project_link_emits_broken_for_bad_uri():
    from tesserae.cross_project import render_cross_project_link

    out = render_cross_project_link("not a uri", label="X")
    assert "wiki-link-broken" in out


def test_find_wiki_uris_in_text_handles_markdown_and_bare():
    from tesserae.cross_project import find_wiki_uris_in_text

    body = (
        "See [RLHF](wiki://research/concepts/rlhf) for details. "
        "Bare reference: wiki://other/papers/arxiv-1234. "
        "Wikilink [[wiki://research/concepts/rlhf]]. "
        "Trailing punctuation wiki://x/topics/foo. "
        "Not a uri: wiki:/single-slash."
    )
    found = find_wiki_uris_in_text(body)
    # Dedup keeps the first occurrence of duplicate URIs.
    assert "wiki://research/concepts/rlhf" in found
    assert "wiki://other/papers/arxiv-1234" in found
    assert "wiki://x/topics/foo" in found
    # Garbage candidates must not slip through.
    assert all("wiki://" in u and "/" in u[7:] for u in found)


def test_find_wiki_uris_in_text_empty_body_returns_empty():
    from tesserae.cross_project import find_wiki_uris_in_text
    assert find_wiki_uris_in_text("") == []
    assert find_wiki_uris_in_text("nothing here") == []


def test_build_graph_payload_emits_bridge_node_and_edge(tmp_path, monkeypatch):
    """End-to-end: source markdown with wiki:// URI -> bridge node + edge in payload."""
    from tesserae.mcp_server import ProjectRegistry
    from tesserae.research_graph import ResearchGraph, ResearchNode, ResearchNodeType
    from tesserae.site.pages import SiteContext, build_graph_payload
    import tesserae.cross_project as cp

    # Sibling project: register so the bridge node resolves to is_built=True.
    sibling = tmp_path / "sibling"
    page_dir = sibling / ".tesserae" / "site" / "concepts"
    page_dir.mkdir(parents=True)
    (page_dir / "rlhf.html").write_text("<html>x</html>", encoding="utf-8")
    (sibling / ".tesserae" / "graph.json").write_text("{}", encoding="utf-8")

    registry_path = tmp_path / "registry.json"
    registry = ProjectRegistry(path=registry_path)
    registry.register(str(sibling), name="sibling")
    monkeypatch.setattr(
        cp,
        "ProjectRegistry",
        lambda: ProjectRegistry(path=registry_path),
    )

    # Local project with a SourceDocument and a Concept; the SourceDocument
    # body mentions the wiki:// URI.
    src = ResearchNode(
        id="src-1",
        name="Notes",
        type=ResearchNodeType.SOURCE_DOCUMENT,
        source_path="notes.md",
    )
    cpt = ResearchNode(
        id="cpt-1",
        name="Attention",
        type=ResearchNodeType.CONCEPT,
        source_path="notes.md",
    )
    graph = ResearchGraph(nodes=[src, cpt], edges=[])

    # show_sources=True so the SourceDocument stays in the visual payload
    # — bridges are only emitted for visible local nodes.
    ctx = SiteContext.build(
        graph=graph,
        wiki_pages_by_kind={},
        site_title="x",
        show_sources=True,
    )
    # Inject the body that the SiteContext.build path would have read
    # from disk. ``source_body_by_path`` is the field
    # ``_build_cross_project_bridges`` scans.
    object.__setattr__(
        ctx,
        "source_body_by_path",
        {"notes.md": "see [rlhf](wiki://sibling/concepts/rlhf) here"},
    )

    payload = build_graph_payload(ctx)
    node_ids = {n["id"] for n in payload["nodes"]}
    assert "bridge:sibling:concepts:rlhf" in node_ids
    bridge = next(
        n for n in payload["nodes"] if n["id"] == "bridge:sibling:concepts:rlhf"
    )
    assert bridge["group"] == "external"
    assert bridge["metadata"]["external_project"] == "sibling"
    assert bridge["metadata"]["external_uri"] == "wiki://sibling/concepts/rlhf"

    bridge_edges = [
        e for e in payload["links"]
        if e["target"] == "bridge:sibling:concepts:rlhf"
    ]
    assert bridge_edges, "expected at least one bridge edge"
    assert bridge_edges[0]["cross_project"] is True
