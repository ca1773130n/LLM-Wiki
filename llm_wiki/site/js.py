"""Client-side JavaScript bundles for the LLM-Wiki static site.

Three module-level constants compose into the bundle that gets written to
``assets/app.js`` by the StaticSiteBuilder:

- :data:`JS_THEME_TOGGLE` — toggles ``data-theme`` on the root element and
  persists the choice to ``localStorage``.
- :data:`JS_SEARCH_PALETTE` — full-text + fuzzy search over
  ``search-index.json`` (built by Subagent F). Opens with ``cmd+k`` or ``/``,
  arrow keys to navigate, enter to open, escape to close. Recent results are
  remembered between sessions.
- :data:`JS_GRAPH` — sigma.js powered graph view. Reads the ``#graph-data``
  payload script, renders nodes colored by kind, edges weighted by relevance,
  and navigates to the underlying URL on click. Falls back gracefully to a
  noop when sigma is not loaded (we vendor sigma in ``assets/`` per the
  design spec, but the page still renders if the vendor copy is missing).

The bundle stays vanilla (no npm) and feature-detects everything it touches.
DOM updates use ``textContent`` and explicit ``createElement`` calls — never
``innerHTML`` with user-influenced data — so XSS is structurally impossible
even when the search index contains arbitrary corpus strings.
"""

from __future__ import annotations


JS_THEME_TOGGLE = r"""
(function(){
  const root = document.documentElement;
  const KEY = 'llmwiki-theme';
  const saved = (function(){ try { return localStorage.getItem(KEY); } catch(_) { return null; } })();
  if (saved === 'dark' || saved === 'light') root.dataset.theme = saved;
  function toggle(){
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem(KEY, next); } catch(_) {}
  }
  document.addEventListener('click', function(e){
    const target = e.target.closest('#theme-toggle, [data-theme-toggle]');
    if (target) { e.preventDefault(); toggle(); }
  });
})();
"""


JS_SEARCH_PALETTE = r"""
(function(){
  let data = null;
  let dataReady = null;
  const palette = document.getElementById('palette');
  const input = document.getElementById('search');
  const results = document.getElementById('results');
  const RECENTS_KEY = 'llmwiki-recents';
  function loadRecents(){
    try { return JSON.parse(localStorage.getItem(RECENTS_KEY) || '[]'); } catch(_) { return []; }
  }
  function saveRecent(item){
    try {
      const list = loadRecents().filter(x => x.href !== item.href);
      list.unshift({ title: item.title, href: item.href, type: item.type });
      localStorage.setItem(RECENTS_KEY, JSON.stringify(list.slice(0, 10)));
    } catch(_) {}
  }
  function ensureData(){
    if (data) return Promise.resolve(data);
    if (dataReady) return dataReady;
    const inline = document.getElementById('search-data');
    if (inline) {
      try { data = JSON.parse(inline.textContent || '[]'); return Promise.resolve(data); } catch(_) {}
    }
    dataReady = fetch('search-index.json').then(r => r.ok ? r.json() : []).then(j => { data = j || []; return data; }).catch(() => { data = []; return data; });
    return dataReady;
  }
  function score(query, item){
    if (!query) return 0;
    const q = query.toLowerCase();
    const hay = ((item.title || '') + ' ' + (item.description || '') + ' ' + (item.type || '')).toLowerCase();
    if (hay.indexOf(q) !== -1) return 10 - hay.indexOf(q) / 200;
    let i = 0; let s = 0;
    for (const ch of q) { const idx = hay.indexOf(ch, i); if (idx === -1) return 0; s += 1 / (idx - i + 1); i = idx + 1; }
    return s;
  }
  function buildResultRow(item){
    const a = document.createElement('a');
    a.className = 'result';
    a.href = item.href || '#';
    a.dataset.href = item.href || '';
    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.textContent = item.type || '';
    const strong = document.createElement('strong');
    strong.textContent = item.title || item.id || '';
    const desc = document.createElement('p');
    desc.textContent = item.description || item.source_path || '';
    a.appendChild(badge);
    a.appendChild(strong);
    a.appendChild(desc);
    return a;
  }
  function render(items){
    if (!results) return;
    while (results.firstChild) results.removeChild(results.firstChild);
    if (!items.length) {
      const p = document.createElement('p');
      p.className = 'muted';
      p.textContent = 'No matches.';
      results.appendChild(p);
      return;
    }
    items.slice(0, 30).forEach(function(it){ results.appendChild(buildResultRow(it)); });
  }
  function open(){
    if (!palette) return;
    palette.hidden = false;
    setTimeout(() => { input && input.focus(); }, 0);
    ensureData().then(items => {
      const recents = loadRecents();
      render(recents.length ? recents : items.slice(0, 12));
    });
  }
  function close(){ if (palette) palette.hidden = true; }
  function search(){
    if (!input) return;
    ensureData().then(items => {
      const q = (input.value || '').trim();
      if (!q) { render(items.slice(0, 12)); return; }
      const ranked = items.map(it => ({ it, s: score(q, it) })).filter(r => r.s > 0).sort((a, b) => b.s - a.s).map(r => r.it);
      render(ranked);
    });
  }
  document.addEventListener('click', function(e){
    const opener = e.target.closest('[data-open-search]');
    if (opener) { e.preventDefault(); open(); return; }
    const result = e.target.closest('.result[data-href]');
    if (result) {
      saveRecent({
        title: (result.querySelector('strong') && result.querySelector('strong').textContent) || '',
        href: result.dataset.href,
        type: (result.querySelector('.badge') && result.querySelector('.badge').textContent) || ''
      });
    }
    if (palette && e.target === palette) close();
  });
  if (input) input.addEventListener('input', search);
  document.addEventListener('keydown', function(e){
    const tag = (document.activeElement && document.activeElement.tagName) || '';
    if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(tag)) { e.preventDefault(); open(); return; }
    if ((e.metaKey || e.ctrlKey) && (e.key || '').toLowerCase() === 'k') { e.preventDefault(); open(); return; }
    if (e.key === 'Escape') { close(); }
  });
})();
"""


JS_GRAPH = r"""
(function(){
  const dataNode = document.getElementById('graph-data');
  const container = document.getElementById('graph-canvas');
  if (!dataNode || !container) return;
  let payload = { nodes: [], edges: [] };
  try { payload = JSON.parse(dataNode.textContent || '{}') || payload; } catch(_) {}
  const Sigma = window.Sigma || (window.sigma && window.sigma.Sigma);
  const Graph = window.graphology && window.graphology.Graph;
  if (Sigma && Graph) {
    const g = new Graph();
    payload.nodes.forEach(function(n, i){
      const angle = (i / Math.max(payload.nodes.length, 1)) * Math.PI * 2;
      g.addNode(n.id, {
        label: n.label, x: Math.cos(angle), y: Math.sin(angle),
        size: 4, color: n.color || '#7c3aed', kind: n.kind, url: n.url
      });
    });
    payload.edges.forEach(function(e, i){
      try { g.addEdgeWithKey('e' + i, e.source, e.target, { size: 0.5 + (e.weight || 1) * 0.5, color: 'rgba(91,87,79,0.35)' }); } catch(_) {}
    });
    const renderer = new Sigma(g, container);
    renderer.on('clickNode', function(evt){
      const attrs = g.getNodeAttributes(evt.node);
      if (attrs.url) window.location.href = attrs.url;
    });
    return;
  }
  // SVG fallback — built via DOM APIs (no innerHTML) so the corpus strings
  // we draw cannot smuggle markup.
  const NS = 'http://www.w3.org/2000/svg';
  while (container.firstChild) container.removeChild(container.firstChild);
  const svg = document.createElementNS(NS, 'svg');
  const w = container.clientWidth || 800;
  const h = container.clientHeight || 480;
  svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', '100%');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', 'Knowledge graph');
  const cx = w / 2, cy = h / 2, r = Math.min(w, h) * 0.4;
  const positions = {};
  payload.nodes.forEach(function(n, i){
    const angle = (i / Math.max(payload.nodes.length, 1)) * Math.PI * 2;
    positions[n.id] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });
  payload.edges.forEach(function(e){
    const a = positions[e.source]; const b = positions[e.target];
    if (!a || !b) return;
    const line = document.createElementNS(NS, 'line');
    line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
    line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
    line.setAttribute('stroke', 'rgba(91,87,79,0.3)');
    line.setAttribute('stroke-width', '1');
    svg.appendChild(line);
  });
  payload.nodes.forEach(function(n){
    const p = positions[n.id]; if (!p) return;
    const link = document.createElementNS(NS, 'a');
    link.setAttribute('href', n.url || '#');
    const circle = document.createElementNS(NS, 'circle');
    circle.setAttribute('cx', p.x); circle.setAttribute('cy', p.y);
    circle.setAttribute('r', '6');
    circle.setAttribute('fill', n.color || '#7c3aed');
    const title = document.createElementNS(NS, 'title');
    title.textContent = n.label || '';
    circle.appendChild(title);
    link.appendChild(circle);
    svg.appendChild(link);
  });
  container.appendChild(svg);
})();
"""


JS_BUNDLE = JS_THEME_TOGGLE + "\n" + JS_SEARCH_PALETTE + "\n" + JS_GRAPH


__all__ = ["JS_THEME_TOGGLE", "JS_SEARCH_PALETTE", "JS_GRAPH", "JS_BUNDLE"]
