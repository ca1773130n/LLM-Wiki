from llm_wiki.research_graph import ResearchCorpusAnalyzer, ResearchGraphExtractor, ResearchNodeType


PAPER_DAY_1 = """
# 논문 분석: 2604.00538

> - arxiv: https://arxiv.org/abs/2604.00538
> - 분석일: 2026-04-25

TRiGS: Temporal Rigid-Body Motion for Scalable 4D Gaussian Splatting | Cool Papers - 몰입형 논문 탐색

## 2604.00538

최근 4D Gaussian Splatting, 즉 4DGS 방법들은 동적 장면 재구성에서 인상적인 성능을 달성했다.
TRiGS는 표준 벤치마크에서 높은 충실도의 렌더링을 달성한다.
"""

PAPER_DAY_2 = """
# 논문 분석: 2601.17835

> - arxiv: https://arxiv.org/abs/2601.17835
> - 분석일: 2026-04-26

Geometry-Grounded Gaussian Splatting | Cool Papers - 몰입형 논문 탐색

Gaussian Splatting은 novel view synthesis와 shape reconstruction에서 중요한 방법론이다.
본 논문은 stochastic solid를 사용해 depth map을 개선한다.
"""


def test_extract_title_prefers_real_paper_title_over_analysis_heading_and_arxiv_id():
    graph = ResearchGraphExtractor().extract_text(
        PAPER_DAY_1,
        source_path="data/research/daily/2026-04-25/papers/2604.00538/paper.md",
        source_kind="Paper",
    )

    papers = [node for node in graph.nodes if node.type == ResearchNodeType.PAPER]
    assert len(papers) == 1
    assert papers[0].name == "TRiGS: Temporal Rigid-Body Motion for Scalable 4D Gaussian Splatting"
    assert papers[0].metadata["arxiv_id"] == "2604.00538"
    assert papers[0].metadata["analysis_date"] == "2026-04-25"


def test_corpus_analyzer_creates_trend_nodes_for_repeated_concepts_across_dates():
    extractor = ResearchGraphExtractor()
    graphs = [
        extractor.extract_text(
            PAPER_DAY_1,
            source_path="data/research/daily/2026-04-25/papers/2604.00538/paper.md",
            source_kind="Paper",
        ),
        extractor.extract_text(
            PAPER_DAY_2,
            source_path="data/research/daily/2026-04-26/papers/2601.17835/paper.md",
            source_kind="Paper",
        ),
    ]

    corpus = ResearchCorpusAnalyzer().summarize_trends(graphs, min_sources=2)

    trend_nodes = [node for node in corpus.nodes if node.type == ResearchNodeType.TREND]
    assert any(node.name == "Trend: Gaussian Splatting" for node in trend_nodes)

    gaussian = next(node for node in corpus.nodes if node.name == "Gaussian Splatting")
    trend = next(node for node in trend_nodes if node.name == "Trend: Gaussian Splatting")
    assert any(edge.source == gaussian.id and edge.target == trend.id and edge.type == "rising_in" for edge in corpus.edges)
    assert trend.metadata["source_count"] == 2
    assert trend.metadata["first_seen"] == "2026-04-25"
    assert trend.metadata["last_seen"] == "2026-04-26"
