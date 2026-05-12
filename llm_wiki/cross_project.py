"""Cross-project link resolution for LLM-Wiki's multi-vault registry.

Bet **B2** in the competitive-positioning research: the registry
(``~/.llm-wiki/registry.json``) is a *graph substrate*, not just a CLI
convenience. Source markdown in one registered project can reference a
node in another registered project via a stable URI scheme:

    ``wiki://<project-alias>/<kind>/<slug>``

Examples:

    * ``wiki://research/concepts/rlhf``                 — concept page in ``research``
    * ``wiki://other-vault/papers/arxiv-2510-12323``    — paper in ``other-vault``
    * ``wiki://x/concepts/한국어-slug``                 — Unicode slug

This module is the **resolver layer**. It never touches the network and
never throws on a missing sibling project; it returns a
:class:`CrossProjectRef` whose ``is_resolvable`` / ``is_built`` booleans
let the caller decide whether to render the link as a live ``<a>``, a
tombstone, or a broken-link placeholder. Compile-time
(``site/pages.build_graph_payload`` -> bridge nodes) and runtime
(MCP ``ask`` / CLI ``ask --scope`` aggregation) both call into here.

See also:

    * ``docs/superpowers/specs/2026-05-13-competitive-positioning-research.md``
      section 4.B2 — the bet spec.
    * :class:`llm_wiki.mcp_server.ProjectRegistry` — the file-backed
      registry this resolver reads.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .mcp_server import ProjectRegistry


# Wiki kinds the registry-side static site lays out under
# ``.llm-wiki/site/<kind>/<slug>.html``. We don't restrict the regex to
# this set — unknown kinds resolve to ``is_resolvable=True`` (alias is
# registered) but ``is_built=False`` (file doesn't exist), which is the
# correct tombstone behavior for typos / non-existent kinds.
_KNOWN_WIKI_KINDS: frozenset[str] = frozenset(
    {"concepts", "papers", "repos", "entities", "topics", "syntheses", "questions", "sources"}
)


# ``wiki://<alias>/<kind>/<slug>`` where:
#   * alias: ASCII alphanumeric + ``-`` / ``_`` (matches
#     :func:`ProjectRegistry._sanitize_project_name`'s output).
#   * kind: ASCII alphanumeric + ``-`` / ``_`` (intentionally loose so a
#     future schema-evolution bet can add new kinds without touching the
#     regex).
#   * slug: alphanumeric + ``-`` ``_`` ``.`` plus a Unicode range so
#     localized slugs (Korean / Chinese / Japanese / etc.) round-trip
#     unmodified through ``_canonical_slug``. Trailing ``.html`` is
#     stripped so the URI can be written either way.
_WIKI_URI_RE = re.compile(
    r"^wiki://(?P<alias>[A-Za-z0-9_\-]+)/(?P<kind>[A-Za-z0-9_\-]+)/(?P<slug>[A-Za-z0-9_\-\.À-￿]+?)(?:\.html)?$"
)


@dataclass(frozen=True)
class CrossProjectRef:
    """Result of resolving a ``wiki://`` URI against the registry.

    A ``CrossProjectRef`` always carries the parsed ``alias`` / ``kind``
    / ``slug`` (so callers can render a tombstone even when the alias is
    unregistered). ``project_root`` is ``None`` when the alias is not in
    the registry; ``page_path`` is ``None`` when the registered project
    exists on disk but the page has not been built yet.
    """

    alias: str
    kind: str
    slug: str
    project_root: Optional[Path]
    page_path: Optional[Path]

    @property
    def is_resolvable(self) -> bool:
        """The alias is in the registry and we know where to look for it."""
        return self.project_root is not None

    @property
    def is_built(self) -> bool:
        """The target page actually exists on disk in the sibling project."""
        return self.page_path is not None and self.page_path.exists()

    @property
    def uri(self) -> str:
        return f"wiki://{self.alias}/{self.kind}/{self.slug}"


def parse_wiki_uri(uri: str) -> Optional[tuple[str, str, str]]:
    """Return ``(alias, kind, slug)`` for a valid ``wiki://`` URI or ``None``.

    Whitespace around the URI is stripped. Returns ``None`` for any
    string that does not match the strict three-segment form — callers
    use this to short-circuit on garbage input without raising.
    """
    if not isinstance(uri, str):
        return None
    match = _WIKI_URI_RE.match(uri.strip())
    if not match:
        return None
    return match.group("alias"), match.group("kind"), match.group("slug")


def cross_project_resolve(uri: str, *, registry: Optional[ProjectRegistry] = None) -> CrossProjectRef:
    """Resolve a ``wiki://`` URI against the registry without raising.

    Raises :class:`ValueError` *only* when ``uri`` isn't a syntactically
    valid ``wiki://`` URI. For semantic failures — alias not registered,
    project root missing, page not yet built — the returned
    :class:`CrossProjectRef` carries ``is_resolvable=False`` or
    ``is_built=False`` so the caller can decide between tombstone,
    placeholder, or live link rendering.
    """
    parsed = parse_wiki_uri(uri)
    if not parsed:
        raise ValueError(f"Not a wiki:// URI: {uri!r}")
    alias, kind, slug = parsed
    reg = registry or ProjectRegistry()
    try:
        data = reg.load()
    except Exception:
        # Corrupt / missing registry must NOT crash the compile or
        # serve loop — return an unresolvable ref instead.
        return CrossProjectRef(alias=alias, kind=kind, slug=slug, project_root=None, page_path=None)
    entry = (data.get("projects") or {}).get(alias)
    if not entry or not entry.get("root"):
        return CrossProjectRef(alias=alias, kind=kind, slug=slug, project_root=None, page_path=None)
    root_str = entry["root"]
    try:
        root = Path(root_str).expanduser().resolve()
    except Exception:
        root = Path(root_str)
    # Canonical static-site layout: ``<root>/.llm-wiki/site/<kind>/<slug>.html``.
    page = root / ".llm-wiki" / "site" / kind / f"{slug}.html"
    page_path: Optional[Path] = page if page.exists() else None
    return CrossProjectRef(
        alias=alias,
        kind=kind,
        slug=slug,
        project_root=root,
        page_path=page_path,
    )


def render_cross_project_link(uri: str, *, label: Optional[str] = None) -> str:
    """Render a ``wiki://`` URI as an HTML fragment for in-body links.

    Three failure modes degrade gracefully:

    * **Syntactically broken** URI → ``<span class="wiki-link-broken">``.
    * **Unregistered alias** → ``<span class="wiki-link-tombstone">``
      with a ``title`` explaining the alias is missing.
    * **Registered but not built** → ``<span class="wiki-link-unbuilt">``
      with a ``title`` explaining the page has not been compiled yet.

    On success returns ``<a class="wiki-link-cross" ...>`` pointing at
    the local file path. The calling template can rewrite ``href`` to a
    served URL via `data-cross-project="<alias>"` if it proxies the
    sibling project — the resolver itself stays filesystem-local.
    """
    try:
        ref = cross_project_resolve(uri)
    except ValueError:
        safe = _escape_html(label or uri)
        return f'<span class="wiki-link-broken">{safe}</span>'
    text = _escape_html(label or f"{ref.alias}/{ref.kind}/{ref.slug}")
    if not ref.is_resolvable:
        title = _escape_html(f"Project {ref.alias!r} is not registered")
        return f'<span class="wiki-link-tombstone" title="{title}">{text}</span>'
    if not ref.is_built:
        title = _escape_html(f"Page not yet built in {ref.alias}")
        return (
            f'<span class="wiki-link-unbuilt" title="{title}" '
            f'data-cross-project="{_escape_html(ref.alias)}">{text}</span>'
        )
    href = f"file://{ref.page_path}"
    return (
        f'<a href="{_escape_html(href)}" class="wiki-link-cross" '
        f'data-cross-project="{_escape_html(ref.alias)}">{text}</a>'
    )


def find_wiki_uris_in_text(body: str) -> list[str]:
    """Return every ``wiki://...`` URI mentioned in ``body``, in order, deduped.

    Used at compile time by :func:`llm_wiki.site.pages.build_graph_payload`
    to discover bridge edges from source markdown without re-parsing
    every Markdown link form. The matcher is greedy enough to cover
    bare URIs, ``[label](wiki://...)`` Markdown links, and ``[[wiki://...]]``
    wikilinks; trailing punctuation (``).,;:!?>"'``) is trimmed.
    """
    if not body:
        return []
    # The body-side regex is intentionally a *superset* of
    # ``_WIKI_URI_RE`` — we accept anything that looks like a wiki:// URI
    # and let :func:`parse_wiki_uri` reject malformed candidates. That
    # keeps the body scanner simple and lets the canonical regex evolve
    # without re-syncing.
    candidates = re.findall(r"wiki://[^\s\)\]\}<>\"']+", body)
    seen: dict[str, None] = {}
    for raw in candidates:
        trimmed = raw.rstrip(".,;:!?>\"'`)")
        if parse_wiki_uri(trimmed) is None:
            continue
        if trimmed not in seen:
            seen[trimmed] = None
    return list(seen.keys())


def _escape_html(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


__all__ = [
    "CrossProjectRef",
    "cross_project_resolve",
    "find_wiki_uris_in_text",
    "parse_wiki_uri",
    "render_cross_project_link",
]
