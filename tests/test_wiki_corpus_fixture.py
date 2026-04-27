"""Smoke test for the wiki_sample_graph fixture."""
from __future__ import annotations

from llm_wiki.research_graph import ResearchNodeType


def test_wiki_sample_graph_has_minimum_size(wiki_sample_graph) -> None:
    assert len(wiki_sample_graph.nodes) >= 10


def test_wiki_sample_graph_covers_paper_repo_and_source(wiki_sample_graph) -> None:
    types = {node.type for node in wiki_sample_graph.nodes}
    assert ResearchNodeType.PAPER in types
    assert ResearchNodeType.REPOSITORY in types
    assert ResearchNodeType.SOURCE_DOCUMENT in types


def test_wiki_sample_graph_node_ids_are_unique(wiki_sample_graph) -> None:
    ids = [node.id for node in wiki_sample_graph.nodes]
    assert len(ids) == len(set(ids))
