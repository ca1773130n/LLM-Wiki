from pathlib import Path

from tesserae.research_graph import (
    ALLOWED_EDGE_TYPES,
    ALLOWED_NODE_TYPES,
    ResearchGraphExtractor,
    ResearchNodeType,
)


SAMPLE = """
# Geometry-Grounded Gaussian Splatting

Gaussian Splatting, GS는 novel view synthesis에서 인상적인 품질과 효율성을 보여주었다.
그러나 Gaussian primitive로부터 형상을 추출하는 문제는 여전히 미해결 과제이다.
본 논문에서는 Gaussian primitive를 특정한 유형의 stochastic solid로 정립하는 엄밀한 이론적 유도를 제시한다.
stochastic solid의 volumetric 특성을 활용하여, 우리 방법은 세밀한 기하 추출을 위한 고품질 depth map을 효율적으로 렌더링한다.
실험 결과, 우리 방법은 공개 데이터셋에서 모든 Gaussian Splatting 기반 방법 가운데 가장 우수한 형상 재구성 성능을 달성하였다.
"""


def test_research_extractor_uses_controlled_node_and_edge_types():
    graph = ResearchGraphExtractor().extract_text(
        SAMPLE,
        source_path="papers/2601.17835/paper.md",
        source_kind="Paper",
    )

    assert graph.nodes
    assert graph.edges
    assert {node.type for node in graph.nodes}.issubset(ALLOWED_NODE_TYPES)
    assert {edge.type for edge in graph.edges}.issubset(ALLOWED_EDGE_TYPES)
    forbidden_types = {"software", "technique", "domain", "topic", "technology", "feature", "entity"}
    assert not ({node.type.lower() for node in graph.nodes} & forbidden_types)


def test_research_extractor_models_paper_concepts_claims_and_evidence():
    graph = ResearchGraphExtractor().extract_text(
        SAMPLE,
        source_path="papers/2601.17835/paper.md",
        source_kind="Paper",
    )

    by_name = {node.name: node for node in graph.nodes}
    assert by_name["Geometry-Grounded Gaussian Splatting"].type == ResearchNodeType.PAPER
    assert by_name["Gaussian Splatting"].type == ResearchNodeType.METHODOLOGICAL_CONCEPT
    assert by_name["Novel View Synthesis"].type == ResearchNodeType.TASK
    assert by_name["Stochastic Solid"].type == ResearchNodeType.MATHEMATICAL_CONCEPT
    assert by_name["Depth Map"].type == ResearchNodeType.TECHNICAL_TERM
    assert by_name["Shape Reconstruction"].type == ResearchNodeType.TASK

    claim_nodes = [node for node in graph.nodes if node.type == ResearchNodeType.PERFORMANCE_CLAIM]
    evidence_nodes = [node for node in graph.nodes if node.type == ResearchNodeType.EVIDENCE_SPAN]
    assert claim_nodes, "performance/result claim should be represented explicitly"
    assert evidence_nodes, "claims must be grounded in EvidenceSpan nodes"
    assert graph.has_edge_type("evidenced_by")
    assert graph.has_edge_type("uses")
    assert graph.has_edge_type("addresses")


def test_research_extractor_assigns_approach_family_for_similar_papers():
    graph = ResearchGraphExtractor().extract_text(
        SAMPLE,
        source_path="papers/2601.17835/paper.md",
        source_kind="Paper",
    )

    # The extractor identifies "Geometry-Grounded Gaussian Splatting" as both
    # a Paper and an ApproachFamily. ResearchGraphBuilder.build() collapses
    # them into the canonical Paper (Paper outranks ApproachFamily in
    # _CROSS_TYPE_MERGE_PRIORITY) and records the secondary type in
    # metadata['merged_types'] so the extractor's signal is preserved.
    match = [n for n in graph.nodes if n.name == "Geometry-Grounded Gaussian Splatting"]
    assert match, "the canonical Geometry-Grounded Gaussian Splatting node must exist"
    canonical = match[0]
    assert canonical.type == ResearchNodeType.PAPER
    merged = canonical.metadata.get("merged_types") or []
    assert ResearchNodeType.APPROACH_FAMILY.value in merged, (
        "extractor must mark this paper as also being an approach family "
        "via metadata.merged_types"
    )
    assert graph.has_edge_type("belongs_to_approach_family")


def test_graph_serializes_to_json_compatible_dict():
    graph = ResearchGraphExtractor().extract_text(SAMPLE, source_path="paper.md")
    payload = graph.model_dump()

    assert payload["nodes"]
    assert payload["edges"]
    assert payload["nodes"][0]["type"] in ALLOWED_NODE_TYPES
