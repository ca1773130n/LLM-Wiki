"""Cognee-facing export adapter for ResearchGraph.

The adapter is intentionally dependency-free: it writes a stable JSONL bundle that
can be consumed by a future Cognee ingestion script without weakening the
controlled ResearchGraph schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .research_graph import ResearchGraph


class CogneeResearchGraphAdapter:
    """Export ResearchGraph nodes and relationships in a Cognee-friendly bundle."""

    def write_bundle(self, graph: ResearchGraph, output_dir: str | Path) -> Dict[str, object]:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        nodes_path = out / "nodes.jsonl"
        edges_path = out / "edges.jsonl"

        with nodes_path.open("w", encoding="utf-8") as handle:
            for node in graph.nodes:
                handle.write(json.dumps(self.node_record(node), ensure_ascii=False, sort_keys=True) + "\n")
        with edges_path.open("w", encoding="utf-8") as handle:
            for edge in graph.edges:
                handle.write(json.dumps(self.edge_record(edge), ensure_ascii=False, sort_keys=True) + "\n")

        manifest = {
            "format": "tesserae-cognee-jsonl-v1",
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
            "files": {"nodes": "nodes.jsonl", "edges": "edges.jsonl"},
            "notes": "Import these JSONL files into Cognee while preserving research_node_type and controlled relationship labels.",
        }
        (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out / "README.md").write_text(self.readme(manifest), encoding="utf-8")
        return manifest

    def node_record(self, node) -> Dict[str, object]:
        return {
            "cognee_id": node.id,
            "text": node.description or node.name,
            "name": node.name,
            "metadata": {
                "research_node_type": node.type.value,
                "aliases": node.aliases,
                "source_path": node.source_path,
                **node.metadata,
            },
        }

    def edge_record(self, edge) -> Dict[str, object]:
        return {
            "source_id": edge.source,
            "target_id": edge.target,
            "relationship": edge.type,
            "evidence": edge.evidence,
            "metadata": edge.metadata,
        }

    def readme(self, manifest: Dict[str, object]) -> str:
        return "\n".join(
            [
                "# Cognee Export Bundle",
                "",
                "This directory contains a dependency-free JSONL export of the validated Tesserae ResearchGraph.",
                "",
                f"- nodes: {manifest['nodes']}",
                f"- edges: {manifest['edges']}",
                "- node file: `nodes.jsonl`",
                "- edge file: `edges.jsonl`",
                "",
                "Keep `metadata.research_node_type` and `relationship` as controlled ontology labels during Cognee ingestion.",
                "",
            ]
        )
