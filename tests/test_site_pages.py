"""Structural tests for the site page renderers in :mod:`llm_wiki.site.pages`.

The tests build a small ``SiteContext`` from the ``wiki_sample_graph`` fixture
(see ``tests/conftest.py``) and synthesize a couple of ``WikiPage`` objects so
every detail renderer has something concrete to render. Assertions stay
structural — full document, semantic landmarks, breadcrumb labels, AI
siblings footer — so they keep passing as Subagent D's components and
Subagent F's search index land on top of this module.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from llm_wiki.research_graph import ResearchGraph, ResearchNodeType
from llm_wiki.site.js import JS_BUNDLE, JS_GRAPH, JS_SEARCH_PALETTE, JS_THEME_TOGGLE
from llm_wiki.site.pages import (
    SiteContext,
    page_href,
    render_about,
    render_concept_detail,
    render_concepts_index,
    render_entities_index,
    render_entity_detail,
    render_graph_view,
    render_home,
    render_paper_detail,
    render_papers_index,
    render_question_detail,
    render_questions_index,
    render_repo_detail,
    render_repos_index,
    render_source_detail,
    render_sources_index,
    render_synthesis_detail,
    render_syntheses_index,
    render_timeline,
    render_topic_detail,
    render_topics_index,
)
from llm_wiki.wiki_store import WikiPage


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


def _wiki_pages_for(graph: ResearchGraph) -> dict[str, list[WikiPage]]:
    """Synthesize a minimal WikiPage per kind so detail renderers have input."""
    pages: dict[str, list[WikiPage]] = {
        "sources": [],
        "concepts": [],
        "entities": [],
        "papers": [],
        "repos": [],
        "topics": [],
        "syntheses": [],
        "questions": [],
    }

    def _make(kind: str, slug: str, title: str, body: str, frontmatter: dict | None = None) -> WikiPage:
        return WikiPage(
            kind=kind,
            slug=slug,
            title=title,
            body=body,
            path=Path(f"wiki/{kind}/{slug}.md"),
            frontmatter=frontmatter or {},
        )

    # Pull one node per public kind from the fixture graph if available.
    by_type: dict[str, list] = {}
    for n in graph.nodes:
        by_type.setdefault(n.type.value, []).append(n)

    src = next(iter(by_type.get(ResearchNodeType.SOURCE_DOCUMENT.value, [])), None)
    if src:
        pages["sources"].append(
            _make(
                "sources",
                "sample-source",
                src.name,
                "# Sample source\n\nLead paragraph.\n\n## Section\n\nA bullet:\n\n- one\n- two\n",
                {"node_id": src.id, "source_path": src.source_path or "", "generated_at": "2026-04-27"},
            )
        )

    paper = next(iter(by_type.get(ResearchNodeType.PAPER.value, [])), None)
    if paper:
        pages["papers"].append(
            _make(
                "papers",
                "sample-paper",
                paper.name,
                "# Sample paper\n\nAbstract excerpt for the paper page.\n",
                {"node_id": paper.id, "generated_at": "2026-04-27"},
            )
        )

    repo = next(iter(by_type.get(ResearchNodeType.REPOSITORY.value, [])), None)
    if repo:
        pages["repos"].append(
            _make(
                "repos",
                "sample-repo",
                repo.name,
                "# Sample repo\n\nReadme excerpt.\n",
                {"node_id": repo.id},
            )
        )

    concept = next(iter(by_type.get(ResearchNodeType.CONCEPT.value, [])), None)
    if concept:
        pages["concepts"].append(
            _make(
                "concepts",
                "sample-concept",
                concept.name,
                "# Sample concept\n\nA short definition with a [link](https://example.com).\n",
                {"node_id": concept.id},
            )
        )

    field = next(iter(by_type.get(ResearchNodeType.RESEARCH_FIELD.value, [])), None)
    if field:
        pages["topics"].append(
            _make(
                "topics",
                "sample-topic",
                field.name,
                "# Sample topic\n\nField overview.\n",
                {"node_id": field.id},
            )
        )

    # Synthetic entries for kinds the fixture doesn't naturally produce.
    pages["entities"].append(
        _make("entities", "sample-entity", "Sample Model", "# Sample entity\n\nModel page.\n")
    )
    pages["syntheses"].append(
        _make(
            "syntheses",
            "pulse",
            "Project pulse",
            "# Pulse\n\n- Three new papers this week.\n- One concept emerged.\n- Activity up 12%.\n",
            {"synthesis_kind": "pulse", "generated_at": "2026-04-27T12:00:00Z"},
        )
    )
    pages["syntheses"].append(
        _make(
            "syntheses",
            "weekly-2026-w17",
            "Weekly digest 2026-W17",
            "# Weekly\n\nWeekly summary.\n",
            {"synthesis_kind": "weekly", "generated_at": "2026-04-27T12:00:00Z"},
        )
    )
    pages["questions"].append(
        _make("questions", "sample-question", "Why does it work?", "# Open question\n\nWhy does it work?\n")
    )

    # Overview seed (used by render_home for the tagline).
    pages["overview"] = [
        _make("overview", "overview", "Overview", "A self-indexing knowledge base for the dogfood corpus.\n")
    ]

    return pages


@pytest.fixture
def site_ctx(wiki_sample_graph: ResearchGraph) -> SiteContext:
    return SiteContext.build(
        graph=wiki_sample_graph,
        wiki_pages_by_kind=_wiki_pages_for(wiki_sample_graph),
        site_title="LLM-Wiki",
    )


# ---------------------------------------------------------------------------
# shared assertions
# ---------------------------------------------------------------------------


def _assert_doc_shape(html: str) -> None:
    assert html.lstrip().lower().startswith("<!doctype html>"), "must begin with <!doctype html>"
    assert html.rstrip().endswith("</html>"), "must end with </html>"
    assert "<main" in html, "needs <main> landmark"
    assert "<nav" in html, "needs <nav> landmark"


def _assert_breadcrumb_contains(html: str, label: str) -> None:
    bc = re.search(r'<nav class="breadcrumbs"[^>]*>(.*?)</nav>', html, flags=re.DOTALL)
    assert bc, "page must contain a breadcrumbs <nav class='breadcrumbs'>"
    assert label in bc.group(1), f"breadcrumbs missing label {label!r}: {bc.group(1)[:200]}"


def _assert_ai_siblings(html: str) -> None:
    assert 'class="ai-siblings"' in html or "ai-siblings" in html, "page must include AI siblings footer"


# ---------------------------------------------------------------------------
# index renderers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "renderer,active_label",
    [
        (render_sources_index, "Sources"),
        (render_concepts_index, "Concepts"),
        (render_entities_index, "Entities"),
        (render_papers_index, "Papers"),
        (render_repos_index, "Repos"),
        (render_topics_index, "Topics"),
        (render_syntheses_index, "Syntheses"),
        (render_questions_index, "Open questions"),
    ],
)
def test_index_routes_render_full_html(site_ctx: SiteContext, renderer, active_label: str) -> None:
    out = renderer(site_ctx)
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, active_label)


# ---------------------------------------------------------------------------
# detail renderers
# ---------------------------------------------------------------------------


def test_render_source_detail(site_ctx: SiteContext) -> None:
    pages = site_ctx.wiki_pages_by_kind["sources"]
    if not pages:
        pytest.skip("fixture has no source page")
    out = render_source_detail(site_ctx, pages[0])
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Sources")
    _assert_ai_siblings(out)


def test_render_concept_detail(site_ctx: SiteContext) -> None:
    pages = site_ctx.wiki_pages_by_kind["concepts"]
    if not pages:
        pytest.skip("fixture has no concept page")
    out = render_concept_detail(site_ctx, pages[0])
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Concepts")
    _assert_ai_siblings(out)


def test_render_entity_detail(site_ctx: SiteContext) -> None:
    pages = site_ctx.wiki_pages_by_kind["entities"]
    out = render_entity_detail(site_ctx, pages[0])
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Entities")
    _assert_ai_siblings(out)


def test_render_paper_detail(site_ctx: SiteContext) -> None:
    pages = site_ctx.wiki_pages_by_kind["papers"]
    if not pages:
        pytest.skip("fixture has no paper page")
    out = render_paper_detail(site_ctx, pages[0])
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Papers")
    _assert_ai_siblings(out)
    assert "Mentions in the corpus" in out
    assert "Related" in out
    assert "Source provenance" in out
    assert "Activity" in out


def test_render_repo_detail(site_ctx: SiteContext) -> None:
    pages = site_ctx.wiki_pages_by_kind["repos"]
    if not pages:
        pytest.skip("fixture has no repo page")
    out = render_repo_detail(site_ctx, pages[0])
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Repos")


def test_render_topic_detail(site_ctx: SiteContext) -> None:
    pages = site_ctx.wiki_pages_by_kind["topics"]
    if not pages:
        pytest.skip("fixture has no topic page")
    out = render_topic_detail(site_ctx, pages[0])
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Topics")


def test_render_synthesis_detail(site_ctx: SiteContext) -> None:
    pages = site_ctx.wiki_pages_by_kind["syntheses"]
    out = render_synthesis_detail(site_ctx, pages[0])
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Syntheses")


def test_render_question_detail(site_ctx: SiteContext) -> None:
    pages = site_ctx.wiki_pages_by_kind["questions"]
    out = render_question_detail(site_ctx, pages[0])
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Open questions")


# ---------------------------------------------------------------------------
# special pages
# ---------------------------------------------------------------------------


def test_render_home_has_hero_pulse_stats_and_heatmap(site_ctx: SiteContext) -> None:
    out = render_home(site_ctx)
    _assert_doc_shape(out)
    assert 'class="hero"' in out, "home must include hero markers"
    assert "Sources" in out and "Concepts" in out and "Papers" in out and "Open questions" in out
    # stat row
    assert 'class="stat"' in out, "home must include stat row entries"
    # 26-week heatmap
    assert 'class="heatmap"' in out, "home must include the activity heatmap SVG"
    # tagline pulled from overview
    assert "self-indexing knowledge base" in out


def test_render_timeline_renders_full_doc(site_ctx: SiteContext) -> None:
    out = render_timeline(site_ctx)
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Timeline")


def test_render_graph_view_includes_payload_script(site_ctx: SiteContext) -> None:
    out = render_graph_view(site_ctx)
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "Graph view")
    # Payload script tag present with the documented id.
    m = re.search(r'<script id="graph-data" type="application/json">(.+?)</script>', out, flags=re.DOTALL)
    assert m, "render_graph_view must emit a <script id='graph-data'> payload"
    payload = json.loads(m.group(1).replace("<\\/", "</"))
    # The interactive 3D layout uses ``links`` (3d-force-graph convention);
    # the legacy 2D sigma renderer used ``edges``. Accept either to keep the
    # contract loose enough that future renderer swaps don't break this test.
    assert "nodes" in payload
    assert "links" in payload or "edges" in payload
    # No code-class nodes leak into the graph view payload.
    leaked = [n for n in payload["nodes"] if n.get("type") in {"CodeClass", "CodeFunction", "CodeModule"}]
    assert not leaked, f"graph view leaked code-layer nodes: {leaked!r}"


def test_render_about_renders_full_doc(site_ctx: SiteContext) -> None:
    out = render_about(site_ctx)
    _assert_doc_shape(out)
    _assert_breadcrumb_contains(out, "About")


# ---------------------------------------------------------------------------
# routing rules: no detail page for code-layer types
# ---------------------------------------------------------------------------


def test_no_public_renderer_for_code_layer_types() -> None:
    """``pages.py`` exports no renderer for CodeClass/CodeFunction/etc."""
    import llm_wiki.site.pages as pages_module

    for forbidden in ("render_codeclass_detail", "render_codefunction_detail",
                      "render_codemodule_detail", "render_evidence_span",
                      "render_claim_detail"):
        assert not hasattr(pages_module, forbidden), f"unexpected exposed renderer: {forbidden}"


def test_page_href_kinds_are_wiki_layer_only() -> None:
    """page_href must refuse to mint URLs for code-layer kinds."""
    from llm_wiki.site.pages import ROUTE_FOR_KIND

    forbidden = {"codeclass", "codefunction", "codemodule", "evidence", "claim"}
    overlap = forbidden & set(ROUTE_FOR_KIND)
    assert not overlap, f"ROUTE_FOR_KIND must not include code-layer kinds: {overlap}"

    # Spot check a wiki-layer slug.
    assert page_href("papers", "abc") == "papers/abc.html"


# ---------------------------------------------------------------------------
# JS bundle smoke
# ---------------------------------------------------------------------------


def test_js_bundle_concatenates_three_modules() -> None:
    assert JS_THEME_TOGGLE in JS_BUNDLE
    assert JS_SEARCH_PALETTE in JS_BUNDLE
    assert JS_GRAPH in JS_BUNDLE
    assert "data-theme" in JS_THEME_TOGGLE
    assert "search-data" in JS_SEARCH_PALETTE or "search-index.json" in JS_SEARCH_PALETTE
    assert "graph-data" in JS_GRAPH
