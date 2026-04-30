"""Project graph nodes into the markdown wiki layer.

The synthesis projector handles higher-order pages (pulse, daily, weekly,
topic, comparison, field). This projector handles the leaf kinds that mirror
graph nodes one-to-one: sources, concepts, entities, papers, repos, topics,
questions. Together they populate ``.llm-wiki/wiki/`` so the static site
renders detail pages for every wiki-layer node.

Idempotent: a page is only rewritten when its body hash would change.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .research_graph import ResearchEdge, ResearchGraph, ResearchNode, ResearchNodeType, is_public_research_node
from .wiki_store import WikiPage, WikiPageStore


# --- Node-type → wiki kind --------------------------------------------------

_KIND_FOR_TYPE: Mapping[ResearchNodeType, str] = {
    ResearchNodeType.SOURCE_DOCUMENT: "sources",
    ResearchNodeType.PAPER: "papers",
    ResearchNodeType.REPOSITORY: "repos",
    ResearchNodeType.PROJECT: "repos",
    ResearchNodeType.CODE_PROJECT: "repos",
    ResearchNodeType.CONCEPT: "concepts",
    ResearchNodeType.TECHNICAL_TERM: "concepts",
    ResearchNodeType.MATHEMATICAL_CONCEPT: "concepts",
    ResearchNodeType.METHODOLOGICAL_CONCEPT: "concepts",
    ResearchNodeType.ALGORITHM: "concepts",
    ResearchNodeType.OBJECTIVE_FUNCTION: "concepts",
    ResearchNodeType.ARCHITECTURE_PATTERN: "concepts",
    ResearchNodeType.TRAINING_PARADIGM: "concepts",
    ResearchNodeType.INFERENCE_STRATEGY: "concepts",
    ResearchNodeType.EVALUATION_PROTOCOL: "concepts",
    ResearchNodeType.TASK: "concepts",
    ResearchNodeType.CAPABILITY: "concepts",
    ResearchNodeType.MODEL: "entities",
    ResearchNodeType.DATASET: "entities",
    ResearchNodeType.BENCHMARK: "entities",
    ResearchNodeType.METRIC: "entities",
    ResearchNodeType.ORGANIZATION: "entities",
    ResearchNodeType.PERSON: "entities",
    ResearchNodeType.RESEARCH_FIELD: "topics",
    ResearchNodeType.RESEARCH_TOPIC: "topics",
    ResearchNodeType.PROBLEM_AREA: "topics",
    ResearchNodeType.APPROACH_FAMILY: "topics",
    ResearchNodeType.TREND: "topics",
    ResearchNodeType.OPEN_QUESTION: "questions",
}


@dataclass(frozen=True)
class _Adjacency:
    out: Dict[str, List[ResearchEdge]] = field(default_factory=lambda: defaultdict(list))
    inn: Dict[str, List[ResearchEdge]] = field(default_factory=lambda: defaultdict(list))


def _build_adjacency(graph: ResearchGraph) -> _Adjacency:
    adj = _Adjacency()
    for edge in graph.edges:
        adj.out[edge.source].append(edge)
        adj.inn[edge.target].append(edge)
    return adj


def _format_relation_block(title: str, items: Sequence[Tuple[str, str, str]]) -> str:
    if not items:
        return ""
    lines = [f"## {title}", ""]
    for label, name, kind in items[:25]:
        lines.append(f"- **{label}** → {name} _({kind})_")
    lines.append("")
    return "\n".join(lines)


class WikiLayerProjector:
    """Materialize wiki/<kind>/<slug>.md files for every wiki-layer graph node."""

    def __init__(self, wiki_store: WikiPageStore) -> None:
        self.wiki_store = wiki_store

    def project(self, graph: ResearchGraph) -> List[WikiPage]:
        adj = _build_adjacency(graph)
        nodes_by_id = {node.id: node for node in graph.nodes}
        written: List[WikiPage] = []
        for node in graph.nodes:
            if not is_public_research_node(node):
                continue
            kind = _KIND_FOR_TYPE.get(node.type)
            if kind is None:
                continue
            page = self._page_for_node(node, kind, adj, nodes_by_id)
            if self.wiki_store.write_page(page):
                written.append(page)
        return written

    def _page_for_node(
        self,
        node: ResearchNode,
        kind: str,
        adj: _Adjacency,
        nodes_by_id: Mapping[str, ResearchNode],
    ) -> WikiPage:
        slug = self.wiki_store.slug_for(node.name) if hasattr(self.wiki_store, "slug_for") else _local_slug(node.name)
        try:
            slug = self.wiki_store.slug_for(node.name)
        except NotImplementedError:
            slug = _local_slug(node.name)
        title = node.name
        outgoing = [
            (edge.type, nodes_by_id[edge.target].name, nodes_by_id[edge.target].type.value)
            for edge in adj.out.get(node.id, [])
            if edge.target in nodes_by_id
            and is_public_research_node(nodes_by_id[edge.target])
            and _KIND_FOR_TYPE.get(nodes_by_id[edge.target].type) is not None
        ]
        incoming = [
            (edge.type, nodes_by_id[edge.source].name, nodes_by_id[edge.source].type.value)
            for edge in adj.inn.get(node.id, [])
            if edge.source in nodes_by_id
            and is_public_research_node(nodes_by_id[edge.source])
            and _KIND_FOR_TYPE.get(nodes_by_id[edge.source].type) is not None
        ]
        outgoing.sort()
        incoming.sort()
        type_mix = Counter(item[2] for item in outgoing + incoming)
        body_lines = [
            f"# {title}",
            "",
            f"_Type: **{node.type.value}**_",
            "",
        ]
        if node.description:
            body_lines.extend([node.description, ""])
        if node.aliases:
            body_lines.append("**Aliases:** " + ", ".join(sorted(node.aliases)))
            body_lines.append("")
        if node.source_path:
            body_lines.append(f"**Source:** `{node.source_path}`")
            body_lines.append("")
        if outgoing:
            body_lines.append(_format_relation_block("Outgoing relations", outgoing))
        if incoming:
            body_lines.append(_format_relation_block("Incoming relations", incoming))
        if type_mix:
            body_lines.append("## Connected node types")
            body_lines.append("")
            for kind_name, count in sorted(type_mix.items(), key=lambda item: (-item[1], item[0])):
                body_lines.append(f"- {kind_name}: {count}")
            body_lines.append("")
        body = "\n".join(body_lines).rstrip() + "\n"
        frontmatter = {
            "title": title,
            "kind": kind,
            "node_id": node.id,
            "node_type": node.type.value,
            "source_path": node.source_path or "",
        }
        path = self.wiki_store.path_for(kind, slug)
        return WikiPage(kind=kind, slug=slug, title=title, body=body, path=path, frontmatter=frontmatter)


def _local_slug(value: str) -> str:
    import hashlib
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    if not safe:
        safe = hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]
    return safe[:80]
