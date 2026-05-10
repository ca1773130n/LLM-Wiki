import json
from pathlib import Path

import pytest

from llm_wiki.research_graph import ResearchGraph, ResearchNode, ResearchNodeType


def _payload():
    return {
        "version": 1,
        "project": {"name": "demo"},
        "parser": "mineru",
        "documents": [
            {
                "id": "doc-abc123",
                "path": "docs/whitepaper.pdf",
                "sha256": "abc123",
                "parsed_dir": ".llm-wiki/external/raganything/parsed/abc123",
                "content_list": [
                    {"type": "text", "page_idx": 0, "text": "Mermaid rendering is described here."},
                    {"type": "image", "page_idx": 1, "img_path": "p1.png", "img_caption": ["Mermaid pipeline"]},
                    {"type": "table", "page_idx": 2, "table_body": "| a | b |\n| - | - |\n| 1 | 2 |", "table_caption": ["Performance"]},
                    {"type": "equation", "page_idx": 3, "latex": "E = mc^2", "equation_caption": ["Energy"]},
                ],
            }
        ],
    }


def test_import_payload_creates_source_file_with_multimodal_blocks(tmp_path):
    from llm_wiki.raganything_adapter import RagAnythingGraphAdapter

    adapter = RagAnythingGraphAdapter(tmp_path)
    graph, manifest = adapter.import_payload(
        _payload(),
        artifact_rel=".llm-wiki/external/raganything/manifest.json",
        artifact_sha256="deadbeef",
    )
    sources = [n for n in graph.nodes if n.type == ResearchNodeType.SOURCE_FILE]
    assert len(sources) == 1
    src = sources[0]
    assert src.metadata["parser"] == "raganything"
    assert src.source_path == "docs/whitepaper.pdf"
    blocks = src.metadata["multimodal_blocks"]
    types = sorted({b["type"] for b in blocks})
    assert types == ["equation", "image", "table"]
    refs = src.metadata["external_refs"]
    assert refs[0]["system"] == "rag-anything"
    assert refs[0]["id"] == "doc-abc123"
    assert manifest["artifact_sha256"] == "deadbeef"
    assert manifest["imported_documents"]["doc-abc123"] == src.id
