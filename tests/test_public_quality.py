import json
import re

from tesserae.research_graph import ResearchEdge, ResearchGraph, ResearchNode, ResearchNodeType, stable_id
from tesserae.synthesis import SynthesisProjector
from tesserae.wiki_projector import WikiLayerProjector
from tesserae.wiki_store import WikiPageStore


def _node(name, node_type, **kwargs):
    return ResearchNode(
        id=kwargs.pop("id", stable_id(node_type.value, name)),
        name=name,
        type=node_type,
        aliases=kwargs.pop("aliases", []),
        source_path=kwargs.pop("source_path", None),
        metadata=kwargs.pop("metadata", {}),
        description=kwargs.pop("description", ""),
    )


def test_public_wiki_projection_skips_social_feed_sources_and_unverified_feed_papers(tmp_path):
    feed = _node(
        "RT Someone: tweet content with TL;DR and @handle",
        ResearchNodeType.SOURCE_DOCUMENT,
        source_path="data/research/daily/2026-04-07/feeds/20260406122914.md",
    )
    feed_paper = _node(
        "Tweet body pretending to be a paper title @author",
        ResearchNodeType.PAPER,
        source_path="data/research/daily/2026-04-07/feeds/20260406122914.md",
        aliases=["arXiv:2604.02996"],
        metadata={"arxiv_id": "2604.02996", "title_quality": "reference_context"},
    )
    real_paper = _node(
        "Geometry-Grounded Gaussian Splatting",
        ResearchNodeType.PAPER,
        source_path="data/research/daily/2026-04-15/papers/2601.17835/paper.md",
        aliases=["arXiv:2601.17835"],
        metadata={"arxiv_id": "2601.17835", "title_quality": "paper_file"},
    )
    graph = ResearchGraph(nodes=[feed, feed_paper, real_paper], edges=[])

    written = WikiLayerProjector(WikiPageStore(tmp_path)).project(graph)
    titles = {page.title for page in written}

    assert "RT Someone: tweet content with TL;DR and @handle" not in titles
    assert "Tweet body pretending to be a paper title @author" not in titles
    assert "Geometry-Grounded Gaussian Splatting" in titles


def test_daily_synthesis_lists_verified_research_artifacts_not_tweet_sources(tmp_path):
    feed = _node(
        "Learning 3D Reconstruction with Priors @adaveiitm tl;dr: tweet text",
        ResearchNodeType.SOURCE_DOCUMENT,
        source_path="data/research/daily/2026-04-08/feeds/20260407235725.md",
    )
    unverified = _node(
        "arXiv:2604.04158",
        ResearchNodeType.PAPER,
        source_path="data/research/daily/2026-04-08/digest.md",
        aliases=["arXiv:2604.04158"],
        metadata={"arxiv_id": "2604.04158", "title_quality": "arxiv_only"},
    )
    real_paper = _node(
        "WorldCompass: Reinforcement Learning for Long-Horizon World Models",
        ResearchNodeType.PAPER,
        source_path="data/research/daily/2026-04-08/papers/2602.09022/paper.md",
        aliases=["arXiv:2602.09022"],
        metadata={"arxiv_id": "2602.09022", "title_quality": "paper_file"},
    )
    graph = ResearchGraph(nodes=[feed, unverified, real_paper], edges=[])

    projected, _ = SynthesisProjector(WikiPageStore(tmp_path)).project(graph)
    daily = next(n for n in projected.nodes if n.name == "Daily Digest — 2026-04-08")
    page = (tmp_path / "syntheses" / "daily-2026-04-08.md").read_text()

    assert "WorldCompass: Reinforcement Learning for Long-Horizon World Models" in page
    assert "Learning 3D Reconstruction with Priors" not in page
    assert "tl;dr" not in page.lower()
    assert "arXiv:2604.04158" not in page


def test_public_paper_page_hides_internal_claim_and_evidence_scaffold(tmp_path):
    paper = _node(
        "RoMo: Robust Motion Segmentation Improves Structure from Motion",
        ResearchNodeType.PAPER,
        source_path="data/research/daily/2026-04-08/papers/2411.18650/paper.md",
        metadata={"arxiv_id": "2411.18650", "title_quality": "paper_file"},
    )
    claim = _node(
        "Performance claim: # 논문 분석: 2411.18650 > - arxiv: https://arxiv.org/abs/2411.18650 Designed by kexue.fm",
        ResearchNodeType.PERFORMANCE_CLAIM,
        source_path=paper.source_path,
    )
    evidence = _node(
        "Evidence: # 논문 분석: 2411.18650 > - papers.cool: https://papers.cool/arxiv/2411.18650",
        ResearchNodeType.EVIDENCE_SPAN,
        source_path=paper.source_path,
    )
    graph = ResearchGraph(
        nodes=[paper, claim, evidence],
        edges=[
            ResearchEdge(source=paper.id, target=claim.id, type="supports_claim"),
            ResearchEdge(source=claim.id, target=evidence.id, type="evidenced_by"),
        ],
    )

    WikiLayerProjector(WikiPageStore(tmp_path)).project(graph)
    page = next((tmp_path / "papers").glob("*.md")).read_text()

    assert "RoMo: Robust Motion Segmentation" in page
    assert "논문 분석" not in page
    assert "Designed by" not in page
    assert "Evidence:" not in page
