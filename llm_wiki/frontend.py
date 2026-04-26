"""Dependency-light static frontend for compiled LLM-Wiki graphs.

Inspired by Pratiyush/llm-wiki's stdlib-first static site approach: precompute a
search index and graph JSON, then ship a single no-build HTML page with inline
CSS/JS for browsing research and development knowledge together.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .research_graph import ResearchGraph, ResearchNode, ResearchNodeType

RESEARCH_TYPES = {
    ResearchNodeType.PAPER.value,
    ResearchNodeType.RESEARCH_FIELD.value,
    ResearchNodeType.RESEARCH_TOPIC.value,
    ResearchNodeType.APPROACH_FAMILY.value,
    ResearchNodeType.CLAIM.value,
    ResearchNodeType.CONTRIBUTION_CLAIM.value,
    ResearchNodeType.PERFORMANCE_CLAIM.value,
    ResearchNodeType.EVIDENCE_SPAN.value,
}
DEVELOPMENT_TYPES = {
    ResearchNodeType.CODE_PROJECT.value,
    ResearchNodeType.SOURCE_FILE.value,
    ResearchNodeType.CODE_MODULE.value,
    ResearchNodeType.CODE_CLASS.value,
    ResearchNodeType.CODE_FUNCTION.value,
    ResearchNodeType.DEPENDENCY.value,
    ResearchNodeType.REPOSITORY.value,
    ResearchNodeType.PROJECT.value,
}


@dataclass(frozen=True)
class StaticSiteBuilder:
    site_title: str = "LLM-Wiki"

    def write_site(self, graph: ResearchGraph, output_dir: str | Path) -> Dict[str, object]:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        graph_payload = graph.model_dump()
        search_index = build_search_index(graph)
        (out / "graph.json").write_text(json.dumps(graph_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (out / "search-index.json").write_text(json.dumps(search_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (out / "llms.txt").write_text(render_llms_txt(self.site_title, graph), encoding="utf-8")
        (out / "index.html").write_text(render_index_html(self.site_title, graph, search_index), encoding="utf-8")
        return {"site_path": str(out), "nodes": len(graph.nodes), "edges": len(graph.edges), "search_entries": len(search_index)}


def build_search_index(graph: ResearchGraph) -> List[Dict[str, object]]:
    entries = []
    for node in graph.nodes:
        entries.append({
            "id": node.id,
            "title": node.name,
            "type": node.type.value,
            "description": node.description,
            "source_path": node.source_path,
            "text": " ".join([node.name, node.type.value, node.description or "", str(node.metadata)]),
        })
    return entries


def render_llms_txt(title: str, graph: ResearchGraph) -> str:
    lines = [f"# {title}", "", "Compiled LLM-Wiki graph for AI agents.", "", "## Entry points", "", "- graph.json — authoritative graph", "- search-index.json — client-side search index", "", "## Top nodes", ""]
    for node in graph.nodes[:50]:
        lines.append(f"- {node.name} ({node.type.value})")
    return "\n".join(lines) + "\n"


def render_index_html(title: str, graph: ResearchGraph, search_index: List[Dict[str, object]]) -> str:
    type_counts = count_types(graph)
    research_nodes = [node for node in graph.nodes if node.type.value in RESEARCH_TYPES or node.type.value not in DEVELOPMENT_TYPES]
    dev_nodes = [node for node in graph.nodes if node.type.value in DEVELOPMENT_TYPES]
    return f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <header class="nav"><strong>{html.escape(title)}</strong><input id="search" aria-label="Search graph" placeholder="Search research + development graph…"></header>
  <main class="container">
    <section class="hero">
      <p class="eyebrow">Karpathy-style compiled knowledge</p>
      <h1>Research + Development LLM-Wiki</h1>
      <p>Research papers, claims, code files, symbols, dependencies, temporal facts, and agent harnesses share one validated graph pipeline.</p>
    </section>
    <section class="stats">{render_stats(type_counts, len(graph.nodes), len(graph.edges))}</section>
    <section class="grid">
      <article class="card"><h2>Research</h2>{render_node_list(research_nodes[:20])}</article>
      <article class="card"><h2>Development</h2>{render_node_list(dev_nodes[:20])}</article>
    </section>
    <section class="card"><h2>Search results</h2><div id="results"></div></section>
  </main>
  <script id="search-data" type="application/json">{safe_json_for_script(search_index)}</script>
  <script>{JS}</script>
</body>
</html>
"""


def render_stats(type_counts: Dict[str, int], nodes: int, edges: int) -> str:
    cards = [f"<div class='stat'><b>{nodes}</b><span>Nodes</span></div>", f"<div class='stat'><b>{edges}</b><span>Edges</span></div>"]
    for key, value in sorted(type_counts.items())[:8]:
        cards.append(f"<div class='stat'><b>{value}</b><span>{html.escape(key)}</span></div>")
    return "".join(cards)


def safe_json_for_script(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def render_node_list(nodes: List[ResearchNode]) -> str:
    if not nodes:
        return "<p class='muted'>No nodes yet.</p>"
    items = []
    for node in nodes:
        desc = node.description or node.source_path or node.id
        items.append(f"<li><span class='badge'>{html.escape(node.type.value)}</span> <strong>{html.escape(node.name)}</strong><p>{html.escape(str(desc))}</p></li>")
    return "<ul class='nodes'>" + "".join(items) + "</ul>"


def count_types(graph: ResearchGraph) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for node in graph.nodes:
        counts[node.type.value] = counts.get(node.type.value, 0) + 1
    return counts


CSS = """
:root{--bg:#0c0a1d;--card:#16142d;--text:#e2e8f0;--muted:#94a3b8;--border:#2d2b4a;--accent:#a78bfa;--accent-bg:#1e1a3a;--font:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;--mono:'JetBrains Mono',monospace}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);line-height:1.6}.nav{position:sticky;top:0;z-index:10;display:flex;gap:16px;align-items:center;justify-content:space-between;padding:14px 24px;background:rgba(12,10,29,.92);border-bottom:1px solid var(--border);backdrop-filter:blur(16px)}input{width:min(520px,55vw);padding:10px 12px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text)}.container{max-width:1120px;margin:0 auto;padding:28px 24px}.hero{padding:34px 0}.eyebrow{color:var(--accent);text-transform:uppercase;font-size:.78rem;letter-spacing:.12em;font-weight:700}.hero h1{font-size:2.4rem;margin:.2rem 0}.hero p{color:var(--muted);max-width:760px}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin:20px 0}.stat,.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px;box-shadow:0 12px 30px rgba(0,0,0,.25)}.stat b{display:block;font-size:1.6rem}.stat span,.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}.nodes{list-style:none;padding:0;margin:0}.nodes li{border-top:1px solid var(--border);padding:12px 0}.nodes li:first-child{border-top:0}.nodes p{margin:4px 0 0;color:var(--muted);font-size:.9rem}.badge{display:inline-block;font:700 .7rem var(--mono);padding:2px 6px;border-radius:999px;background:var(--accent-bg);color:var(--accent);margin-right:6px}mark{background:var(--accent);color:#0c0a1d;border-radius:3px;padding:0 2px}
"""

JS = """
const data = JSON.parse(document.getElementById('search-data').textContent || '[]');
const input = document.getElementById('search');
const results = document.getElementById('results');
function render(items){results.innerHTML = '<ul class="nodes">' + items.slice(0,30).map(x => `<li><span class="badge">${x.type}</span> <strong>${x.title}</strong><p>${x.description || x.source_path || x.id}</p></li>`).join('') + '</ul>';}
function search(){const q=input.value.toLowerCase().trim(); if(!q){render(data.slice(0,10)); return;} render(data.filter(x => (x.text || '').toLowerCase().includes(q)));}
input.addEventListener('input', search); render(data.slice(0,10));
"""
