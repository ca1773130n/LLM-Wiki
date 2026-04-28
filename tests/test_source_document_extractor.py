from llm_wiki.research_graph import ResearchGraphExtractor, ResearchNodeType


def test_repository_document_extraction_uses_source_and_heading_nodes_not_research_claims():
    text = """# Feature Map

This document mentions Gaussian Splatting as an example string, not as a paper claim.

## Volumetric Rendering

A concept-shaped heading that survives the filter.

## Frontend

Static HTML site generation.
"""

    graph = ResearchGraphExtractor().extract_text(text, source_path="docs/feature-map.md", source_kind="SourceDocument")
    types = {node.type for node in graph.nodes}
    names = {node.name for node in graph.nodes}

    assert ResearchNodeType.SOURCE_DOCUMENT in types
    assert "Feature Map" in names
    # Concept-shaped headings (whitelist match) survive as Concept nodes.
    assert "Volumetric Rendering" in names
    # Generic single-word section markers like "Frontend" are intentionally
    # NOT promoted to Concept nodes after the heading-classifier fix.
    assert "Frontend" not in names
    assert ResearchNodeType.CLAIM not in types
    assert ResearchNodeType.EVIDENCE_SPAN not in types
    assert ResearchNodeType.METHODOLOGICAL_CONCEPT not in types
