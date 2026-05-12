"""Regression tests for the filename-shaped concept filter (Bug A).

The LLM extractor occasionally emits ``Concept``-typed nodes whose names are
literally filenames or path strings (``feature-map.md``, ``pyproject.toml``,
``tests/test_x.py``). Those duplicate the ``SourceDocument`` nodes that
already represent the same files with proper titles and pollute the
concept layer of the visual graph. ``looks_like_filename_or_path`` +
``filter_filename_shaped_concepts`` strip them.

These tests pin the predicate so we never silently regress into either
dropping real concepts ("GPT-4o", "Llama 3.1") or admitting filename
noise.
"""

from __future__ import annotations

from llm_wiki.research_graph import (
    ResearchEdge,
    ResearchGraph,
    ResearchNode,
    ResearchNodeType,
    filter_filename_shaped_concepts,
    looks_like_filename_or_path,
)


# ---------------------------------------------------------------------------
# predicate
# ---------------------------------------------------------------------------


def test_looks_like_filename_or_path_recognizes_common_filenames():
    assert looks_like_filename_or_path("feature-map.md") is True
    assert looks_like_filename_or_path("pyproject.toml") is True
    assert looks_like_filename_or_path("__init__.py") is True
    assert looks_like_filename_or_path("tests/test_x.py") is True
    assert looks_like_filename_or_path("docs/integrations/rag-anything.md") is True
    assert looks_like_filename_or_path("package.json") is True
    assert looks_like_filename_or_path(".gitignore") is True
    assert looks_like_filename_or_path("Makefile") is True
    assert looks_like_filename_or_path("Dockerfile") is True
    assert looks_like_filename_or_path("LICENSE") is True


def test_looks_like_filename_or_path_keeps_real_concepts():
    # These are real research-domain concept tokens. They must survive even
    # though some of them superficially resemble dotted filenames.
    assert looks_like_filename_or_path("GaussianFlow SLAM") is False
    assert looks_like_filename_or_path("Self-Supervised Learning") is False
    assert looks_like_filename_or_path("Depth Map") is False
    assert looks_like_filename_or_path("4D Gaussian Splatting") is False
    assert looks_like_filename_or_path("GPT-4o") is False
    assert looks_like_filename_or_path("Llama 3.1") is False
    assert looks_like_filename_or_path("128-D vector") is False
    assert looks_like_filename_or_path("A. M. Turing") is False


def test_looks_like_filename_or_path_handles_empty_and_whitespace():
    assert looks_like_filename_or_path("") is False
    assert looks_like_filename_or_path("   ") is False
    # Whitespace-padded filename still gets caught.
    assert looks_like_filename_or_path("  foo.md  ") is True


def test_looks_like_filename_or_path_windows_path_separator():
    assert looks_like_filename_or_path(r"tests\test_x.py") is True


# ---------------------------------------------------------------------------
# graph-level filter
# ---------------------------------------------------------------------------


def test_filename_concept_filter_drops_nodes_and_incident_edges():
    """End-to-end: a tiny graph with a filename-named Concept comes out with
    neither the offending node nor its incident edges."""
    graph = ResearchGraph(
        nodes=[
            ResearchNode(
                id="c1",
                name="feature-map.md",
                type=ResearchNodeType.CONCEPT,
                description="",
            ),
            ResearchNode(
                id="c2",
                name="Depth Map",
                type=ResearchNodeType.CONCEPT,
                description="",
            ),
            ResearchNode(
                id="s1",
                name="Architecture",
                type=ResearchNodeType.SOURCE_DOCUMENT,
                description="",
            ),
        ],
        edges=[
            ResearchEdge(source="s1", target="c1", type="defines"),
            ResearchEdge(source="s1", target="c2", type="defines"),
        ],
    )
    cleaned = filter_filename_shaped_concepts(graph)
    names = {n.name for n in cleaned.nodes}
    assert "feature-map.md" not in names
    assert "Depth Map" in names
    assert "Architecture" in names
    # The edge anchored to the dropped node is also gone.
    targets = {e.target for e in cleaned.edges}
    assert "c1" not in targets
    assert "c2" in targets


def test_filename_concept_filter_preserves_source_document_with_filename_shape():
    """A SourceDocument legitimately named ``README.md`` must survive — the
    filter only targets concept-layer types."""
    graph = ResearchGraph(
        nodes=[
            ResearchNode(
                id="src1",
                name="README.md",
                type=ResearchNodeType.SOURCE_DOCUMENT,
                description="",
            ),
        ],
        edges=[],
    )
    cleaned = filter_filename_shaped_concepts(graph)
    assert {n.name for n in cleaned.nodes} == {"README.md"}


def test_filename_concept_filter_no_op_when_no_offenders():
    """Hot-path: graphs without any filename-shaped concepts must come back
    unchanged (same object identity is fine; we just need byte-equivalence)."""
    graph = ResearchGraph(
        nodes=[
            ResearchNode(
                id="c1",
                name="Self-Supervised Learning",
                type=ResearchNodeType.CONCEPT,
                description="",
            ),
        ],
        edges=[],
    )
    cleaned = filter_filename_shaped_concepts(graph)
    assert [n.name for n in cleaned.nodes] == ["Self-Supervised Learning"]


def test_filename_concept_filter_covers_all_conceptish_types():
    """The filter targets every concept-layer node type, not just CONCEPT."""
    conceptish_types = [
        ResearchNodeType.CONCEPT,
        ResearchNodeType.TECHNICAL_TERM,
        ResearchNodeType.METHODOLOGICAL_CONCEPT,
        ResearchNodeType.MATHEMATICAL_CONCEPT,
        ResearchNodeType.ALGORITHM,
        ResearchNodeType.CAPABILITY,
        ResearchNodeType.TASK,
        ResearchNodeType.APPROACH_FAMILY,
        ResearchNodeType.RESEARCH_TOPIC,
        ResearchNodeType.INFERENCE_STRATEGY,
        ResearchNodeType.EVALUATION_PROTOCOL,
        ResearchNodeType.TRAINING_PARADIGM,
        ResearchNodeType.OBJECTIVE_FUNCTION,
        ResearchNodeType.ARCHITECTURE_PATTERN,
    ]
    graph = ResearchGraph(
        nodes=[
            ResearchNode(
                id=f"n{i}",
                name="bogus.py",
                type=t,
                description="",
            )
            for i, t in enumerate(conceptish_types)
        ],
        edges=[],
    )
    cleaned = filter_filename_shaped_concepts(graph)
    assert cleaned.nodes == []
