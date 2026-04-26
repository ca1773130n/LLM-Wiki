from llm_wiki.canonicalization import GraphCanonicalizer, ReviewDecision, ReviewQueue
from llm_wiki.research_graph import ResearchEdge, ResearchGraph, ResearchNode, ResearchNodeType


def test_canonicalizer_merges_alias_nodes_and_rewires_edges():
    paper = ResearchNode(id="Paper:p:test", name="Paper A", type=ResearchNodeType.PAPER)
    canonical = ResearchNode(
        id="MethodologicalConcept:gaussian-splatting:canonical",
        name="Gaussian Splatting",
        type=ResearchNodeType.METHODOLOGICAL_CONCEPT,
        aliases=["3DGS", "3D Gaussian Splatting"],
    )
    alias = ResearchNode(id="MethodologicalConcept:3dgs:alias", name="3DGS", type=ResearchNodeType.METHODOLOGICAL_CONCEPT)
    task = ResearchNode(id="Task:novel-view-synthesis:test", name="Novel View Synthesis", type=ResearchNodeType.TASK)
    graph = ResearchGraph(
        nodes=[paper, canonical, alias, task],
        edges=[
            ResearchEdge(source=paper.id, target=alias.id, type="uses"),
            ResearchEdge(source=alias.id, target=task.id, type="addresses"),
        ],
    )

    result = GraphCanonicalizer().canonicalize(graph)

    names = [node.name for node in result.graph.nodes]
    assert names.count("Gaussian Splatting") == 1
    assert "3DGS" not in names
    gaussian = next(node for node in result.graph.nodes if node.name == "Gaussian Splatting")
    assert set(gaussian.aliases) >= {"3DGS", "3D Gaussian Splatting"}
    assert any(edge.source == paper.id and edge.target == gaussian.id and edge.type == "uses" for edge in result.graph.edges)
    assert any(edge.source == gaussian.id and edge.target == task.id and edge.type == "addresses" for edge in result.graph.edges)
    assert result.merged_nodes == {alias.id: gaussian.id}


def test_canonicalizer_creates_review_candidates_for_similar_unmerged_concepts():
    graph = ResearchGraph(
        nodes=[
            ResearchNode(id="MethodologicalConcept:gs:test", name="Gaussian Splatting", type=ResearchNodeType.METHODOLOGICAL_CONCEPT),
            ResearchNode(id="MethodologicalConcept:3d-gaussian-splatting:test", name="3D Gaussian Splatting", type=ResearchNodeType.METHODOLOGICAL_CONCEPT),
            ResearchNode(id="Task:nvs:test", name="Novel View Synthesis", type=ResearchNodeType.TASK),
        ],
        edges=[],
    )

    result = GraphCanonicalizer().canonicalize(graph)

    assert result.review_items
    item = result.review_items[0]
    assert item.left_name == "Gaussian Splatting"
    assert item.right_name == "3D Gaussian Splatting"
    assert item.reason == "similar_name"
    assert 0 < item.score <= 1


def test_review_queue_serializes_and_applies_merge_decisions():
    graph = ResearchGraph(
        nodes=[
            ResearchNode(id="MethodologicalConcept:gs:test", name="Gaussian Splatting", type=ResearchNodeType.METHODOLOGICAL_CONCEPT),
            ResearchNode(id="MethodologicalConcept:3d-gaussian-splatting:test", name="3D Gaussian Splatting", type=ResearchNodeType.METHODOLOGICAL_CONCEPT),
        ],
        edges=[ResearchEdge(source="MethodologicalConcept:3d-gaussian-splatting:test", target="MethodologicalConcept:gs:test", type="shares_concept_with")],
    )
    result = GraphCanonicalizer().canonicalize(graph)
    queue = ReviewQueue(result.review_items)
    payload = queue.model_dump()

    assert payload["items"][0]["status"] == "pending"
    decisions = [ReviewDecision(item_id=payload["items"][0]["id"], action="merge", canonical_node_id="MethodologicalConcept:gs:test")]
    merged = queue.apply_decisions(graph, decisions)

    assert [node.name for node in merged.nodes] == ["Gaussian Splatting"]
    assert merged.edges == []
