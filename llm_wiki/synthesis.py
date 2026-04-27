"""Stub for the synthesis projector. Filled in by Subagent B in Phase 1.

Generates the higher-order wiki layer: pulse, daily/weekly digests, topic and
comparison summaries, and field overviews. Deterministic baseline; LLM upgrade
is gated behind ``LLM_WIKI_SYNTHESIS_LLM=1``.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .research_graph import ResearchGraph
from .wiki_store import WikiPage, WikiPageStore


class SynthesisProjector:
    def __init__(self, wiki_store: WikiPageStore, manifest_path: Path | str | None = None) -> None:
        self.wiki_store = wiki_store
        self.manifest_path = Path(manifest_path) if manifest_path else None

    def project(self, graph: ResearchGraph) -> Tuple[ResearchGraph, List[WikiPage]]:
        """Add Synthesis nodes to ``graph`` and write wiki pages. Returns the
        updated graph and the list of pages that were (re)written.

        Phase-0 stub: no-op pass-through. Subagent B replaces this body.
        """
        return graph, []
