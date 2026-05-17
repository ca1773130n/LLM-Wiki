"""Regression tests for the frontmatter-token entity-name filter (Bug C).

A live audit of the deployed demo site found the public entity / concept /
paper indexes polluted with YAML-shape names that had leaked through the
prose extractors:

  * ``type: Paper`` — the literal frontmatter token, mis-promoted as a
    Paper node because the title extractor scanned into the YAML block.
  * ``date: 2016-07-`` / ``methods: [PSNR]`` / ``sub_topic: Visual SLAM``
    — block-list items mis-parsed as Person names by the bibliographic
    ``Authors:`` extractor.

``looks_like_frontmatter_token`` recognizes these tokens; the post-merge
filter chain drops them before they hit the visual graph or any index.
``Person`` nodes (paper authors) are also kept private by default — they
stay in ``graph.json`` for MCP / Cognee consumers but never reach the
public ``/entities/`` index or get wiki pages of their own.
"""

from __future__ import annotations

from tesserae.research_graph import (
    ResearchEdge,
    ResearchGraph,
    ResearchNode,
    ResearchNodeType,
    filter_filename_shaped_concepts,
    is_public_research_node,
    looks_like_frontmatter_token,
)


# ---------------------------------------------------------------------------
# Predicate
# ---------------------------------------------------------------------------


def test_looks_like_frontmatter_token_recognizes_yaml_keys():
    assert looks_like_frontmatter_token("type: Paper") is True
    assert looks_like_frontmatter_token("type: Repository") is True
    assert looks_like_frontmatter_token("arxiv:") is True
    assert looks_like_frontmatter_token('arxiv: "2308.04079"') is True
    assert looks_like_frontmatter_token("authors:") is True
    assert looks_like_frontmatter_token("date: 2016-07-") is True
    assert looks_like_frontmatter_token("methods: [PSNR]") is True
    assert looks_like_frontmatter_token("sub_topic: Visual SLAM") is True
    assert looks_like_frontmatter_token("oss_repo: graphdeco-inria/gaussian-splatting") is True


def test_looks_like_frontmatter_token_keeps_real_concept_names():
    # Real concept tokens must survive even when they superficially carry
    # a colon (model checkpoints, dataset versions, namespaced terms).
    assert looks_like_frontmatter_token("Self-Supervised Learning") is False
    assert looks_like_frontmatter_token("GPT-4o") is False
    assert looks_like_frontmatter_token("4D Gaussian Splatting") is False
    assert looks_like_frontmatter_token("Llama 3.1") is False
    assert looks_like_frontmatter_token("RLHF") is False
    assert looks_like_frontmatter_token("Depth Map") is False
    # A model identifier like ``Whisper: large-v3`` happens to have a
    # colon but the leading token is not a YAML key — keep it.
    assert looks_like_frontmatter_token("Whisper: large-v3") is False


def test_looks_like_frontmatter_token_handles_empty_and_whitespace():
    assert looks_like_frontmatter_token("") is False
    assert looks_like_frontmatter_token("   ") is False
    assert looks_like_frontmatter_token(":") is False


# ---------------------------------------------------------------------------
# Public-output gating
# ---------------------------------------------------------------------------


def _make(node_type: ResearchNodeType, name: str, **meta) -> ResearchNode:
    return ResearchNode(
        id=f"{node_type.value}:{name}",
        name=name,
        type=node_type,
        aliases=tuple(),
        description="",
        source_path=None,
        metadata=meta,
    )


def test_person_nodes_are_not_public_research_nodes():
    """Person stays in the graph for MCP/Cognee but is hidden from public
    outputs by default — author noise should not dominate /entities/."""
    person = _make(ResearchNodeType.PERSON, "Bernhard Kerbl")
    assert is_public_research_node(person) is False


def test_frontmatter_token_named_paper_node_is_not_public():
    """A Paper node whose name accidentally became the literal YAML token
    ``type: Paper`` must never reach the public ``/papers/`` index — even
    if it survived earlier extraction stages."""
    bad = _make(ResearchNodeType.PAPER, "type: Paper", title_quality="paper_file")
    assert is_public_research_node(bad) is False


def test_valid_paper_node_is_still_public():
    good = _make(
        ResearchNodeType.PAPER,
        "3D Gaussian Splatting for Real-Time Radiance Field Rendering",
        title_quality="paper_file",
    )
    assert is_public_research_node(good) is True


def test_organization_named_after_frontmatter_token_is_not_public():
    bad = _make(ResearchNodeType.ORGANIZATION, "organizations: ['INRIA']")
    assert is_public_research_node(bad) is False


# ---------------------------------------------------------------------------
# Filter chain: dropping noise nodes + their edges
# ---------------------------------------------------------------------------


def test_filter_drops_frontmatter_token_person_node():
    nodes = [
        _make(ResearchNodeType.PAPER, "Real Paper Title", title_quality="paper_file"),
        _make(ResearchNodeType.PERSON, "date: 2016-07-"),
        _make(ResearchNodeType.PERSON, "Bernhard Kerbl"),  # legit author, still kept in graph.json
    ]
    edges = [
        ResearchEdge(source=nodes[0].id, target=nodes[1].id, type="authored_by"),
        ResearchEdge(source=nodes[0].id, target=nodes[2].id, type="authored_by"),
    ]
    filtered = filter_filename_shaped_concepts(ResearchGraph(nodes=nodes, edges=edges))
    surviving_names = {n.name for n in filtered.nodes}
    # The frontmatter-token Person was dropped from graph.json by the post-merge filter.
    assert "date: 2016-07-" not in surviving_names
    # The real author survives in graph.json (MCP/Cognee still see them) —
    # its public-index visibility is gated separately by is_public_research_node.
    assert "Bernhard Kerbl" in surviving_names
    # The Paper survives.
    assert "Real Paper Title" in surviving_names


def test_filter_drops_yaml_token_paper_node():
    nodes = [
        _make(ResearchNodeType.PAPER, "type: Paper", title_quality="paper_file"),
        _make(ResearchNodeType.PAPER, "Real Paper Title", title_quality="paper_file"),
    ]
    edges: list[ResearchEdge] = []
    filtered = filter_filename_shaped_concepts(ResearchGraph(nodes=nodes, edges=edges))
    surviving_names = {n.name for n in filtered.nodes}
    assert "type: Paper" not in surviving_names
    assert "Real Paper Title" in surviving_names
