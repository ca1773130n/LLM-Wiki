import json

import pytest

from llm_wiki.graphiti_adapter import GraphitiResearchGraphAdapter, GraphitiSyncUnavailableError
from llm_wiki.research_graph import ResearchEdge, ResearchGraph, ResearchNode, ResearchNodeType


def graphiti_sample_graph():
    paper = ResearchNode(
        id="Paper:demo",
        name="Demo Paper",
        type=ResearchNodeType.PAPER,
        source_path="papers/demo.md",
        metadata={"analysis_date": "2026-04-27"},
    )
    method = ResearchNode(
        id="Method:gs",
        name="Gaussian Splatting",
        type=ResearchNodeType.METHODOLOGICAL_CONCEPT,
        description="A point-based rendering method.",
    )
    return ResearchGraph(
        nodes=[paper, method],
        edges=[ResearchEdge(source=paper.id, target=method.id, type="uses", evidence="Demo Paper uses Gaussian Splatting.")],
    )


def test_graphiti_adapter_exports_temporal_facts_as_episode_jsonl(tmp_path):
    output = tmp_path / "graphiti_episodes.jsonl"

    episodes = GraphitiResearchGraphAdapter(group_id="demo_project").write_episodes(graphiti_sample_graph(), output)

    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == len(episodes) == 1
    assert rows[0]["group_id"] == "demo_project"
    assert rows[0]["source"] == "llm_wiki"
    assert rows[0]["source_description"] == "LLM-Wiki controlled research graph temporal fact"
    assert rows[0]["reference_time"] == "2026-04-27"
    assert "Demo Paper --uses--> Gaussian Splatting" in rows[0]["content"]
    assert "Demo Paper uses Gaussian Splatting." in rows[0]["content"]
    assert rows[0]["metadata"]["subject_type"] == "Paper"
    assert rows[0]["metadata"]["object_type"] == "MethodologicalConcept"


def test_graphiti_sync_fails_helpfully_when_optional_dependency_missing(monkeypatch):
    monkeypatch.setattr("llm_wiki.graphiti_adapter.find_spec", lambda name: None if name == "graphiti_core" else object())

    with pytest.raises(GraphitiSyncUnavailableError) as exc:
        GraphitiResearchGraphAdapter().sync(graphiti_sample_graph(), neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="password")

    assert "graphiti_core" in str(exc.value)
    assert "pip install" in str(exc.value)
