"""Tests for the hexagonal ports defining input/output adapters."""

from __future__ import annotations

from typing import Iterator
from uuid import UUID

from llm_wiki.ports import GraphStore, Source, SourceLoader
from llm_wiki.research_graph import ResearchEdge, ResearchGraph, ResearchNode


def test_source_constructs_with_required_fields() -> None:
    src = Source(id="src-1", path="file:///tmp/x.md", content="hello world")
    assert src.id == "src-1"
    assert src.path == "file:///tmp/x.md"
    assert src.content == "hello world"


def test_source_metadata_defaults_to_empty_dict() -> None:
    src = Source(id="src-2", path=None, content="body")
    assert src.metadata == {}


def test_source_loader_protocol_runtime_checkable() -> None:
    class GoodLoader:
        def discover(self) -> Iterator[Source]:
            yield Source(id="a", path=None, content="x")

        def fetch(self, source_id: str) -> Source:
            return Source(id=source_id, path=None, content="x")

    class BadLoader:
        def discover(self) -> Iterator[Source]:
            yield Source(id="a", path=None, content="x")
        # missing fetch

    assert isinstance(GoodLoader(), SourceLoader)
    assert not isinstance(BadLoader(), SourceLoader)


def test_graph_store_protocol_runtime_checkable() -> None:
    class GoodStore:
        def upsert_node(self, node: ResearchNode) -> str:
            return "id"

        def upsert_edge(self, edge: ResearchEdge) -> None:
            return None

        def get_node(self, node_id: str) -> ResearchNode | None:
            return None

        def iterate_nodes(
            self,
            type: str | None = None,
            owner_user_id: str | UUID | None = None,
        ) -> Iterator[ResearchNode]:
            return iter(())

        def query_subgraph(self, seeds: list[str], depth: int = 1) -> ResearchGraph:
            return ResearchGraph()

        def find_canonical(self, name: str, type: str) -> ResearchNode | None:
            return None

    class BadStore:
        def upsert_node(self, node: ResearchNode) -> str:
            return "id"
        # missing the other 5 methods

    assert isinstance(GoodStore(), GraphStore)
    assert not isinstance(BadStore(), GraphStore)
