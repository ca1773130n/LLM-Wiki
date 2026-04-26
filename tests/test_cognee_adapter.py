import json
from pathlib import Path

from llm_wiki.cognee_adapter import CogneeResearchGraphAdapter
from llm_wiki.research_graph import ResearchEdge, ResearchGraph, ResearchNode, ResearchNodeType


def sample_graph():
    paper = ResearchNode(id="Paper:p:test", name="Paper A", type=ResearchNodeType.PAPER, source_path="paper.md")
    concept = ResearchNode(id="MethodologicalConcept:gs:test", name="Gaussian Splatting", type=ResearchNodeType.METHODOLOGICAL_CONCEPT)
    return ResearchGraph(nodes=[paper, concept], edges=[ResearchEdge(source=paper.id, target=concept.id, type="uses", evidence="uses GS")])


def test_cognee_adapter_exports_jsonl_bundle(tmp_path):
    output_dir = tmp_path / "cognee"

    manifest = CogneeResearchGraphAdapter().write_bundle(sample_graph(), output_dir)

    assert manifest["nodes"] == 2
    assert manifest["edges"] == 1
    assert (output_dir / "nodes.jsonl").exists()
    assert (output_dir / "edges.jsonl").exists()
    assert (output_dir / "manifest.json").exists()
    node = json.loads((output_dir / "nodes.jsonl").read_text(encoding="utf-8").splitlines()[0])
    edge = json.loads((output_dir / "edges.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert node["cognee_id"] == "Paper:p:test"
    assert node["metadata"]["research_node_type"] == "Paper"
    assert edge["relationship"] == "uses"
    assert edge["source_id"] == "Paper:p:test"
