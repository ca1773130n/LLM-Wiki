"""Client-side JavaScript bundles for the LLM-Wiki static site.

Three module-level constants compose into the bundle that gets written to
``assets/app.js`` by the StaticSiteBuilder:

- :data:`JS_THEME_TOGGLE` — toggles ``data-theme`` on the root element and
  persists the choice to ``localStorage``.
- :data:`JS_SEARCH_PALETTE` — full-text + fuzzy search over
  ``search-index.json`` (built by Subagent F). Opens with ``cmd+k`` or ``/``,
  arrow keys to navigate, enter to open, escape to close. Recent results are
  remembered between sessions.
- :data:`JS_GRAPH` — interactive 3D force-directed graph view powered by
  ``3d-force-graph`` (with ``three`` as a peer dependency) loaded as ES
  modules from esm.sh. Reads the ``#graph-data`` payload script, renders
  nodes colored by group, edges thickness-coded, with hover-highlight,
  hover-tooltip on edges, info panel, search, type-legend, 2D/3D toggle,
  and keyboard shortcuts (``f`` fit, ``r`` reset, ``2``/``3`` toggle,
  ``/`` focus search, ``Esc`` clear). Falls back to an inline SVG layout
  + error banner if the CDN is blocked. Respects ``prefers-reduced-motion``.

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
  // ----- Color map (terracotta family, harmonised with palette tokens) -----
  const GROUP_COLORS = {
    sources:   '#5b574f',
    papers:    '#be185d',
    repos:     '#2563eb',
    concepts:  '#0891b2',
    entities:  '#7c3aed',
    topics:    '#b3502b',
    syntheses: '#2a6f4f',
    questions: '#c08a1a',
    other:     '#64748b'
  };
  const EDGE_COLOR_LIGHT = 'rgba(91,87,79,0.35)';
  const EDGE_COLOR_DIM   = 'rgba(91,87,79,0.06)';
  const EDGE_COLOR_HOT   = 'rgba(179,80,43,0.95)';

  function ready(fn){
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else { fn(); }
  }

  ready(function(){
    const dataNode  = document.getElementById('graph-data');
    const container = document.getElementById('graph-canvas');
    if (!dataNode || !container) return;

    // ---- payload -------------------------------------------------------
    let payload = { nodes: [], links: [] };
    try { payload = JSON.parse(dataNode.textContent || '{}') || payload; } catch(_) {}
    if (!Array.isArray(payload.nodes)) payload.nodes = [];
    if (!Array.isArray(payload.links)) payload.links = (payload.edges || []);

    // Decorate nodes for fast neighbour lookup; build adjacency.
    const byId = new Map();
    payload.nodes.forEach(function(n){
      n.color = n.color || GROUP_COLORS[n.group || 'other'] || GROUP_COLORS.other;
      n.neighbors = new Set();
      n.edges = [];
      n.degree = 0;
      byId.set(n.id, n);
    });
    payload.links.forEach(function(l){
      const a = byId.get(typeof l.source === 'object' ? l.source.id : l.source);
      const b = byId.get(typeof l.target === 'object' ? l.target.id : l.target);
      if (!a || !b) return;
      a.neighbors.add(b); b.neighbors.add(a);
      a.edges.push(l); b.edges.push(l);
      a.degree += 1; b.degree += 1;
    });

    // ---- DOM slots -----------------------------------------------------
    const infoPanel = document.getElementById('graph-info-panel');
    const tooltip   = document.getElementById('graph-tooltip');
    const legendEl  = document.getElementById('graph-legend');
    const searchEl  = document.getElementById('graph-search-input');
    const banner    = document.getElementById('graph-error-banner');
    const btn2D     = document.querySelector('[data-graph-mode="2d"]');
    const btn3D     = document.querySelector('[data-graph-mode="3d"]');
    const btnFit    = document.querySelector('[data-graph-action="fit"]');
    const btnReset  = document.querySelector('[data-graph-action="reset"]');

    const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ---- Build legend (color swatches with counts; click toggles type) -
    const typeCounts = {};
    payload.nodes.forEach(function(n){
      const g = n.group || 'other';
      typeCounts[g] = (typeCounts[g] || 0) + 1;
    });
    const hiddenGroups = new Set();
    if (legendEl) {
      while (legendEl.firstChild) legendEl.removeChild(legendEl.firstChild);
      Object.keys(typeCounts).sort().forEach(function(group){
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'graph-legend-chip';
        chip.dataset.group = group;
        const dot = document.createElement('span');
        dot.className = 'graph-legend-dot';
        dot.style.background = GROUP_COLORS[group] || GROUP_COLORS.other;
        const label = document.createElement('span');
        label.className = 'graph-legend-label';
        label.textContent = group;
        const count = document.createElement('span');
        count.className = 'graph-legend-count';
        count.textContent = String(typeCounts[group]);
        chip.appendChild(dot); chip.appendChild(label); chip.appendChild(count);
        chip.addEventListener('click', function(){
          if (hiddenGroups.has(group)) hiddenGroups.delete(group);
          else hiddenGroups.add(group);
          chip.classList.toggle('is-off', hiddenGroups.has(group));
          if (Graph) refreshVisibility();
        });
        legendEl.appendChild(chip);
      });
    }

    // ---- Highlight + info-panel state ---------------------------------
    let highlightNodes = new Set();
    let highlightLinks = new Set();
    let hoverNode = null;
    let pinnedNode = null;
    let Graph = null;        // current renderer instance
    let mode = '3d';
    let searchQuery = '';

    function showInfoPanel(node){
      if (!infoPanel) return;
      while (infoPanel.firstChild) infoPanel.removeChild(infoPanel.firstChild);
      if (!node) { infoPanel.classList.remove('is-visible'); return; }
      const h = document.createElement('h3');
      h.className = 'graph-info-title';
      h.textContent = node.name || node.id || '';
      infoPanel.appendChild(h);
      const meta = document.createElement('p');
      meta.className = 'graph-info-meta';
      const t = document.createElement('span');
      t.className = 'graph-info-badge';
      t.style.background = GROUP_COLORS[node.group || 'other'] || GROUP_COLORS.other;
      t.textContent = node.group || node.kind || '';
      meta.appendChild(t);
      const typeSpan = document.createElement('span');
      typeSpan.textContent = ' ' + (node.type || '');
      meta.appendChild(typeSpan);
      const degSpan = document.createElement('span');
      degSpan.className = 'graph-info-degree';
      degSpan.textContent = ' · degree ' + (node.degree || 0);
      meta.appendChild(degSpan);
      infoPanel.appendChild(meta);
      if (node.description) {
        const desc = document.createElement('p');
        desc.className = 'graph-info-desc';
        const text = String(node.description);
        desc.textContent = text.length > 200 ? text.slice(0, 197) + '…' : text;
        infoPanel.appendChild(desc);
      }
      if (node.href) {
        const a = document.createElement('a');
        a.className = 'graph-info-link';
        a.href = node.href;
        a.textContent = 'Open page →';
        infoPanel.appendChild(a);
      }
      infoPanel.classList.add('is-visible');
    }

    function showTooltip(text, x, y){
      if (!tooltip) return;
      tooltip.textContent = text;
      tooltip.style.left = (x + 12) + 'px';
      tooltip.style.top  = (y + 12) + 'px';
      tooltip.classList.add('is-visible');
    }
    function hideTooltip(){ if (tooltip) tooltip.classList.remove('is-visible'); }

    function applyHighlight(node){
      highlightNodes.clear();
      highlightLinks.clear();
      if (node) {
        highlightNodes.add(node);
        node.neighbors.forEach(function(nb){ highlightNodes.add(nb); });
        node.edges.forEach(function(e){ highlightLinks.add(e); });
      }
      if (Graph && Graph.refresh) {
        try { Graph.refresh(); } catch(_) {}
      }
      if (Graph && Graph.nodeColor) {
        // Kick a re-render in 2D builds
        Graph.nodeColor(Graph.nodeColor());
      }
    }

    function isVisible(node){
      if (!node) return false;
      const g = node.group || 'other';
      if (hiddenGroups.has(g)) return false;
      if (searchQuery && !(node.name || '').toLowerCase().includes(searchQuery)) return false;
      return true;
    }

    function refreshVisibility(){
      if (!Graph) return;
      // Force a repaint by re-applying accessors.
      try { Graph.nodeVisibility(function(n){ return isVisible(n); }); } catch(_) {}
      try { Graph.linkVisibility(function(l){
        const s = typeof l.source === 'object' ? l.source : byId.get(l.source);
        const t = typeof l.target === 'object' ? l.target : byId.get(l.target);
        return isVisible(s) && isVisible(t);
      }); } catch(_) {}
    }

    // ---- 2D-fallback (SVG) renderer for CDN-blocked environments ------
    function renderFallback(message){
      if (banner) {
        banner.textContent = message || 'Interactive 3D renderer unavailable — showing static fallback.';
        banner.classList.add('is-visible');
      }
      const NS = 'http://www.w3.org/2000/svg';
      while (container.firstChild) container.removeChild(container.firstChild);
      const svg = document.createElementNS(NS, 'svg');
      const w = container.clientWidth || 800;
      const h = container.clientHeight || 480;
      svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
      svg.setAttribute('width', '100%');
      svg.setAttribute('height', '100%');
      svg.setAttribute('role', 'img');
      svg.setAttribute('aria-label', 'Knowledge graph (static fallback)');
      const cx = w / 2, cy = h / 2, r = Math.min(w, h) * 0.42;
      const positions = {};
      const visible = payload.nodes.filter(isVisible);
      visible.forEach(function(n, i){
        const angle = (i / Math.max(visible.length, 1)) * Math.PI * 2;
        positions[n.id] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
      });
      payload.links.forEach(function(e){
        const sId = typeof e.source === 'object' ? e.source.id : e.source;
        const tId = typeof e.target === 'object' ? e.target.id : e.target;
        const a = positions[sId]; const b = positions[tId];
        if (!a || !b) return;
        const line = document.createElementNS(NS, 'line');
        line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
        line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
        line.setAttribute('stroke', EDGE_COLOR_LIGHT);
        line.setAttribute('stroke-width', '1');
        svg.appendChild(line);
      });
      visible.forEach(function(n){
        const p = positions[n.id]; if (!p) return;
        const link = document.createElementNS(NS, 'a');
        link.setAttribute('href', n.href || '#');
        const circle = document.createElementNS(NS, 'circle');
        circle.setAttribute('cx', p.x); circle.setAttribute('cy', p.y);
        circle.setAttribute('r', String(3 + Math.min(8, Math.sqrt(n.val || 1))));
        circle.setAttribute('fill', n.color);
        const title = document.createElementNS(NS, 'title');
        title.textContent = (n.name || '') + ' — ' + (n.type || '');
        circle.appendChild(title);
        link.appendChild(circle);
        svg.appendChild(link);
      });
      container.appendChild(svg);
    }

    // ---- Build interactive renderer (3D by default) -------------------
    function buildGraph(initialMode){
      mode = initialMode || '3d';
      // Clear container
      while (container.firstChild) container.removeChild(container.firstChild);
      const ctor = (mode === '2d') ? window.ForceGraph : window.ForceGraph3D;
      if (!ctor) { renderFallback('Renderer constructor missing.'); return; }
      const inst = ctor()(container)
        .graphData({ nodes: payload.nodes, links: payload.links })
        .backgroundColor('rgba(0,0,0,0)')
        .nodeId('id')
        .nodeLabel(function(n){ return ''; }) // we handle our own info panel
        .nodeVal(function(n){ return Math.max(1, n.val || 1); })
        .nodeColor(function(n){
          if (highlightNodes.size && !highlightNodes.has(n)) return 'rgba(120,116,108,0.18)';
          return n.color;
        })
        .nodeOpacity(0.95)
        .linkColor(function(l){
          if (highlightLinks.size === 0) return EDGE_COLOR_LIGHT;
          return highlightLinks.has(l) ? EDGE_COLOR_HOT : EDGE_COLOR_DIM;
        })
        .linkWidth(function(l){ return highlightLinks.has(l) ? 1.6 : 0.4; })
        .linkDirectionalParticles(function(l){ return highlightLinks.has(l) ? 2 : 0; })
        .linkDirectionalParticleWidth(1.8)
        .onNodeHover(function(node){
          hoverNode = node || null;
          container.style.cursor = node ? 'pointer' : 'default';
          if (!pinnedNode) {
            applyHighlight(node);
            showInfoPanel(node);
          }
        })
        .onLinkHover(function(link){
          if (!link) { hideTooltip(); return; }
          const s = typeof link.source === 'object' ? link.source : byId.get(link.source);
          const t = typeof link.target === 'object' ? link.target : byId.get(link.target);
          const sName = (s && s.name) || '';
          const tName = (t && t.name) || '';
          const label = link.label || link.type || 'related';
          showTooltip(sName + ' → ' + label + ' → ' + tName, lastMouseX, lastMouseY);
        })
        .onNodeClick(function(node, evt){
          if (!node) return;
          if (evt && (evt.metaKey || evt.ctrlKey)) {
            // Cmd/Ctrl-click: focus camera on node, lock selection.
            pinnedNode = node;
            applyHighlight(node);
            showInfoPanel(node);
            focusOnNode(node);
            return;
          }
          if (node.href) window.location.href = node.href;
        })
        .onBackgroundClick(function(){
          pinnedNode = null;
          applyHighlight(null);
          showInfoPanel(null);
        });

      // 3D-specific tuning
      if (mode === '3d' && inst.nodeThreeObjectExtend) {
        // (default sphere is fine — we keep it lightweight)
      }
      // Force tuning
      try {
        if (inst.d3Force) {
          const charge = inst.d3Force('charge'); if (charge && charge.strength) charge.strength(-120);
          const link = inst.d3Force('link'); if (link && link.distance) link.distance(40);
        }
      } catch(_) {}
      try { inst.cooldownTicks(120); } catch(_) {}

      // Auto-fit once the simulation cools.
      let didFit = false;
      try {
        inst.onEngineStop(function(){
          if (didFit) return;
          didFit = true;
          if (reduceMotion) return;
          setTimeout(function(){
            try { inst.zoomToFit(600, 60); } catch(_) {}
          }, 600);
        });
      } catch(_) {}

      Graph = inst;
      refreshVisibility();
      return inst;
    }

    // Track mouse position for edge tooltip placement.
    let lastMouseX = 0, lastMouseY = 0;
    container.addEventListener('mousemove', function(e){
      const rect = container.getBoundingClientRect();
      lastMouseX = e.clientX - rect.left;
      lastMouseY = e.clientY - rect.top;
      if (tooltip && tooltip.classList.contains('is-visible')) {
        tooltip.style.left = (lastMouseX + 12) + 'px';
        tooltip.style.top  = (lastMouseY + 12) + 'px';
      }
    });
    container.addEventListener('mouseleave', hideTooltip);

    function focusOnNode(node){
      if (!Graph) return;
      if (mode === '3d' && Graph.cameraPosition && node && node.x !== undefined) {
        const distance = 120;
        const distRatio = 1 + distance / Math.hypot(node.x || 1, node.y || 1, node.z || 1);
        try {
          Graph.cameraPosition(
            { x: (node.x || 0) * distRatio, y: (node.y || 0) * distRatio, z: (node.z || 0) * distRatio },
            node,
            reduceMotion ? 0 : 600
          );
        } catch(_) {}
      } else if (mode === '2d' && Graph.centerAt && node) {
        try { Graph.centerAt(node.x || 0, node.y || 0, reduceMotion ? 0 : 600); Graph.zoom(4, reduceMotion ? 0 : 600); } catch(_) {}
      }
    }

    function setMode(next){
      if (next === mode) return;
      buildGraph(next);
      if (btn2D) btn2D.classList.toggle('is-active', next === '2d');
      if (btn3D) btn3D.classList.toggle('is-active', next === '3d');
    }

    // ---- Toolbar wiring -----------------------------------------------
    if (btn2D) btn2D.addEventListener('click', function(){ setMode('2d'); });
    if (btn3D) btn3D.addEventListener('click', function(){ setMode('3d'); });
    if (btnFit) btnFit.addEventListener('click', function(){
      if (Graph && Graph.zoomToFit) try { Graph.zoomToFit(400, 60); } catch(_) {}
    });
    if (btnReset) btnReset.addEventListener('click', function(){
      pinnedNode = null;
      applyHighlight(null);
      showInfoPanel(null);
      if (Graph && Graph.cameraPosition && mode === '3d') {
        try { Graph.cameraPosition({ x: 0, y: 0, z: 400 }, { x: 0, y: 0, z: 0 }, reduceMotion ? 0 : 600); } catch(_) {}
      } else if (Graph && Graph.centerAt) {
        try { Graph.centerAt(0, 0, reduceMotion ? 0 : 600); Graph.zoom(1, reduceMotion ? 0 : 600); } catch(_) {}
      }
    });
    if (searchEl) {
      searchEl.addEventListener('input', function(){
        searchQuery = (searchEl.value || '').trim().toLowerCase();
        refreshVisibility();
      });
      searchEl.addEventListener('keydown', function(e){
        if (e.key === 'Enter') {
          e.preventDefault();
          const match = payload.nodes.find(function(n){
            return (n.name || '').toLowerCase().includes(searchQuery);
          });
          if (match) {
            pinnedNode = match;
            applyHighlight(match);
            showInfoPanel(match);
            focusOnNode(match);
          }
        }
      });
    }

    // ---- Keyboard shortcuts -------------------------------------------
    document.addEventListener('keydown', function(e){
      const tag = (document.activeElement && document.activeElement.tagName) || '';
      const inField = tag === 'INPUT' || tag === 'TEXTAREA';
      if (e.key === '/' && !inField) { e.preventDefault(); searchEl && searchEl.focus(); return; }
      if (inField) return;
      if (e.key === 'f') { if (Graph && Graph.zoomToFit) try { Graph.zoomToFit(400, 60); } catch(_) {} }
      if (e.key === 'r') { if (btnReset) btnReset.click(); }
      if (e.key === '2') setMode('2d');
      if (e.key === '3') setMode('3d');
      if (e.key === 'Escape') {
        pinnedNode = null;
        applyHighlight(null);
        showInfoPanel(null);
        if (searchEl) { searchEl.value = ''; searchQuery = ''; refreshVisibility(); }
      }
    });

    // ---- CDN load detection. The <script type="module"> on the page
    //      sets window.__graphLibsReady = true once 3d-force-graph and
    //      ForceGraph (2D) have been attached to window. We poll briefly.
    let waited = 0;
    const interval = setInterval(function(){
      waited += 100;
      if (window.ForceGraph3D && window.ForceGraph) {
        clearInterval(interval);
        try {
          buildGraph('3d');
          if (btn3D) btn3D.classList.add('is-active');
        } catch (err) {
          console.error('graph: init failed', err);
          renderFallback('Graph init failed: ' + (err && err.message ? err.message : err));
        }
      } else if (waited > 6000) {
        clearInterval(interval);
        renderFallback('Could not load 3d-force-graph from the CDN. Showing static fallback.');
      }
    }, 100);
  });
})();
"""


JS_BUNDLE = JS_THEME_TOGGLE + "\n" + JS_SEARCH_PALETTE + "\n" + JS_GRAPH


__all__ = ["JS_THEME_TOGGLE", "JS_SEARCH_PALETTE", "JS_GRAPH", "JS_BUNDLE"]
