"""``llm_wiki.site`` package.

Phase 0 shim: re-exports the legacy ``StaticSiteBuilder`` from ``llm_wiki.frontend``
so existing imports keep working while Phase 2 subagents (D/E/F/G) build the
real package out underneath.
"""

from __future__ import annotations

from ..frontend import StaticSiteBuilder  # noqa: F401

__all__ = ["StaticSiteBuilder"]
