"""Rewrite markdown links targeting source-code files to GitHub blob URLs.

The compiled wiki only hosts content pages (markdown, generated HTML).
When source markdown documents reference code files via relative paths
(``[wiki_store.py](../tesserae/wiki_store.py)``), the rendered HTML preserves
those hrefs but the targets do not exist in the site tree.

This module identifies such links during compile and rewrites them to
absolute GitHub blob URLs so clicks land on real source on github.com
instead of 404s.

Activation: the rewriter is a no-op unless ``site.github_repo_url`` is set
in ``.tesserae/config.json`` (e.g. ``"https://github.com/ca1773130n/Tesserae"``).
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Optional


# Suffixes that signal "this is a code file, not a content page".
_CODE_SUFFIXES = frozenset(
    {
        ".py", ".pyi", ".pyx",
        ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
        ".go", ".rs", ".java", ".kt", ".swift", ".rb",
        ".c", ".cc", ".cpp", ".h", ".hpp",
        ".sh", ".bash", ".zsh", ".fish",
        ".toml", ".ini", ".cfg",
        ".yml", ".yaml",
        ".sql", ".graphql", ".proto",
    }
)


# Filenames that are not extension-prefixed but are always code/config.
_CODE_FILENAMES = frozenset(
    {
        "Dockerfile", "Makefile", "Containerfile",
        "Procfile", ".gitignore", ".dockerignore",
        "pyproject.toml", "setup.py", "setup.cfg",
        "package.json", "package-lock.json",
        "Cargo.toml", "Cargo.lock",
        "go.mod", "go.sum",
    }
)


_HREF_RE = re.compile(r'href="([^"]+)"')


def looks_like_code_file_target(href: str) -> bool:
    """Return ``True`` if ``href`` points at a source-code or config file.

    Inputs are markdown link targets (the raw text inside ``](...)``),
    not yet resolved against any base. Absolute URLs, anchor-only
    fragments, query strings, and content-page (``.html``) targets are
    explicitly excluded.
    """
    if not href:
        return False
    s = href.split("#", 1)[0].split("?", 1)[0].strip()
    if not s:
        return False
    if s.startswith(
        (
            "http://",
            "https://",
            "mailto:",
            "javascript:",
            "data:",
            "//",
        )
    ):
        return False
    filename = s.rsplit("/", 1)[-1]
    if filename in _CODE_FILENAMES:
        return True
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower()
        return ext in _CODE_SUFFIXES
    return False


def resolve_to_repo_relative(
    href: str, *, source_path: Optional[str] = None
) -> Optional[str]:
    """Resolve an href to a path relative to the repository root.

    ``source_path`` is the path (relative to the repo root) of the markdown
    file the link came from — needed to interpret ``../`` segments correctly.
    For example, ``[x](../tesserae/x.py)`` from ``docs/feature-map.md``
    resolves to ``tesserae/x.py``, while ``[x](../../tesserae/x.py)`` from
    ``docs/i18n/feature-map.zh.md`` resolves to the same ``tesserae/x.py``.
    """
    if not href:
        return None
    s = href.split("#", 1)[0].split("?", 1)[0].strip()
    if not s:
        return None
    if s.startswith(
        (
            "http://",
            "https://",
            "mailto:",
            "javascript:",
            "data:",
            "//",
            "/",
        )
    ):
        return None
    base_dir = PurePosixPath(source_path).parent if source_path else PurePosixPath("")
    joined = (base_dir / s) if str(base_dir) else PurePosixPath(s)
    parts: list[str] = []
    for seg in str(joined).split("/"):
        if seg == "..":
            if parts:
                parts.pop()
        elif seg and seg != ".":
            parts.append(seg)
    return "/".join(parts) if parts else None


def rewrite_code_links(
    html: str,
    *,
    source_path: Optional[str] = None,
    github_blob_base: Optional[str] = None,
) -> str:
    """Rewrite every code-file-targeted href in ``html`` to a GitHub blob URL.

    No-op when:
      - ``github_blob_base`` is None or empty (rewriter disabled),
      - the href doesn't look like a code file,
      - the href can't be resolved to a repo-relative path.

    ``github_blob_base`` should be a full URL prefix, e.g.
    ``"https://github.com/ca1773130n/Tesserae/blob/main"``.
    """
    if not github_blob_base:
        return html
    base = github_blob_base.rstrip("/")

    def replace(match: "re.Match[str]") -> str:
        href = match.group(1)
        if not looks_like_code_file_target(href):
            return match.group(0)
        repo_rel = resolve_to_repo_relative(href, source_path=source_path)
        if not repo_rel:
            return match.group(0)
        new_href = f"{base}/{repo_rel}"
        return f'href="{new_href}"'

    return _HREF_RE.sub(replace, html)


def derive_blob_base(
    *,
    github_repo_url: Optional[str] = None,
    github_blob_base: Optional[str] = None,
    default_ref: str = "main",
) -> Optional[str]:
    """Compute a ``…/blob/<ref>`` URL from config inputs.

    Returns ``None`` when neither input is set. Caller passes the result
    straight into :func:`rewrite_code_links`.
    """
    if github_blob_base:
        return github_blob_base.rstrip("/")
    if github_repo_url:
        return github_repo_url.rstrip("/") + f"/blob/{default_ref}"
    return None
