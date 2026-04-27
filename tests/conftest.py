"""Shared pytest fixtures for the LLM-Wiki test suite."""
from __future__ import annotations

from pathlib import Path

import pytest

from llm_wiki.project import merge_graphs
from llm_wiki.research_graph import ResearchGraph, ResearchGraphExtractor


WIKI_CORPUS_ROOT = Path(__file__).parent / "fixtures" / "wiki_corpus"


def _source_kind_for(path: Path) -> str:
    """Pick the right ResearchGraphExtractor source_kind for a fixture file."""
    parts = path.parts
    name = path.name
    if "papers" in parts and name == "paper.md":
        return "Paper"
    if "papers" in parts and name == "repo.md":
        return "Repository"
    if "repos" in parts:
        return "Repository"
    return "SourceDocument"


@pytest.fixture
def wiki_sample_graph() -> ResearchGraph:
    """Build a ResearchGraph from tests/fixtures/wiki_corpus/.

    Walks the data/research/ and docs/ trees, classifies each markdown file
    via the same path heuristic the production pipeline uses (Paper for
    papers/*/paper.md, Repository for *repo.md and repos/*.md, SourceDocument
    otherwise), runs ResearchGraphExtractor.extract_file on each, and merges
    the resulting per-file graphs via project.merge_graphs.
    """
    extractor = ResearchGraphExtractor()
    roots = [
        WIKI_CORPUS_ROOT / "data" / "research",
        WIKI_CORPUS_ROOT / "docs",
    ]
    graphs = []
    for root in roots:
        if not root.exists():
            continue
        for md_path in sorted(root.rglob("*.md")):
            graphs.append(extractor.extract_file(md_path, source_kind=_source_kind_for(md_path)))
    return merge_graphs(graphs)
