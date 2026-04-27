"""Stub for the wiki page store. Filled in by Subagent A in Phase 1.

The store owns the markdown layer that lives at ``.llm-wiki/wiki/`` — the
Karpathy "Layer 2" between the validated graph and the rendered static site.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class WikiPage:
    kind: str
    slug: str
    title: str
    body: str
    path: Path
    frontmatter: Dict[str, object] = field(default_factory=dict)


class WikiPageStore:
    """Filesystem-backed store for wiki markdown pages (one folder per kind).

    Subagent A fills in the methods. Phase-0 stub keeps imports stable.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def path_for(self, kind: str, slug: str) -> Path:
        return self.root / kind / f"{slug}.md"

    def slug_for(self, name: str) -> str:
        raise NotImplementedError

    def write_page(self, page: WikiPage) -> bool:
        raise NotImplementedError

    def read_page(self, path: str | Path) -> WikiPage:
        raise NotImplementedError

    def list_pages(self, kind: str) -> List[WikiPage]:
        raise NotImplementedError
