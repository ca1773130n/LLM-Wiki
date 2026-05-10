"""Managed RAG-Anything refresh runner for LLM-Wiki.

Discovers non-code sources, parses them via RAG-Anything (MinerU/Docling/PaddleOCR),
and writes `.llm-wiki/external/raganything/manifest.json` plus `meta.json` so the
adapter has a stable artifact to import during compile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


RAGA_ROOT = Path(".llm-wiki/external/raganything")
MANIFEST_NAME = "manifest.json"
META_NAME = "meta.json"


def _git_head(project: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project,
            text=True,
            capture_output=True,
            timeout=20,
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _stored_commit(project: Path) -> str | None:
    meta_path = project / RAGA_ROOT / META_NAME
    if not meta_path.exists():
        return None
    try:
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    for key in ("gitCommitHash", "commit", "head"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _artifact_is_current(project: Path) -> bool:
    manifest = project / RAGA_ROOT / MANIFEST_NAME
    if not manifest.exists():
        return False
    head = _git_head(project)
    if not head:
        return True
    stored = _stored_commit(project)
    return stored == head


_SUPPORTED_EXT = {
    ".md", ".markdown", ".txt", ".rst",
    ".pdf",
    ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp",
}

_EXCLUDED_DIRS = {".git", ".venv", "node_modules", ".llm-wiki", ".understand-anything", ".pytest_cache", "__pycache__", "output", "dist", "build"}


def discover_sources(project: Path, *, roots: Iterable[str] | None = None) -> list[Path]:
    """Return all non-code files under the given roots that RAG-Anything can parse."""
    project = Path(project).resolve()
    candidates: list[Path] = []
    search_roots = [project / r for r in (roots or ["."]) if (project / r).exists()]
    for root in search_roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in _EXCLUDED_DIRS for part in path.relative_to(project).parts):
                continue
            if path.suffix.lower() in _SUPPORTED_EXT:
                candidates.append(path)
    return sorted(candidates)


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_manifest(
    project: Path,
    *,
    documents: Sequence[dict],
    parser: str,
    parser_version: str = "",
    git_commit: str | None = None,
) -> Path:
    project = Path(project).resolve()
    out_dir = project / RAGA_ROOT
    out_dir.mkdir(parents=True, exist_ok=True)

    serialized: list[dict] = []
    for doc in documents:
        path = Path(doc["path"]).resolve()
        rel = str(path.relative_to(project)).replace("\\", "/") if path.is_relative_to(project) else str(path)
        sha = _sha256_path(path)
        serialized.append({
            "id": f"doc-{sha[:16]}",
            "path": rel,
            "sha256": sha,
            "parsed_dir": str((out_dir / "parsed" / sha).relative_to(project)).replace("\\", "/"),
            "content_list": list(doc.get("content_list") or []),
        })

    manifest = {
        "version": 1,
        "project": {"name": project.name, "root": "."},
        "parser": parser,
        "parser_version": parser_version,
        "git_commit": git_commit or "",
        "documents": serialized,
    }
    manifest_path = out_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    meta = {
        "gitCommitHash": git_commit or "",
        "parser": parser,
        "parser_version": parser_version,
        "document_count": len(serialized),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / META_NAME).write_text(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def parse_documents(
    project: Path,
    *,
    sources: Sequence[Path],
    parser: str,
    parse_method: str = "auto",
    working_dir: Path | None = None,
    llm_funcs: dict | None = None,
) -> list[dict]:
    """Parse the given source files with RAG-Anything and return per-doc content lists.

    Imported lazily so the refresh module can be loaded without `raganything` installed.
    """
    try:
        import asyncio
        from raganything import RAGAnything, RAGAnythingConfig
    except Exception as exc:  # pragma: no cover - depends on env
        raise RuntimeError(
            "raganything is not installed. Run `pip install 'raganything[all]'` or use --install-raganything."
        ) from exc

    working_dir = Path(working_dir or (project / RAGA_ROOT / "working_dir")).resolve()
    working_dir.mkdir(parents=True, exist_ok=True)
    parsed_root = (project / RAGA_ROOT / "parsed").resolve()
    parsed_root.mkdir(parents=True, exist_ok=True)

    config = RAGAnythingConfig(working_dir=str(working_dir), parser=parser, parse_method=parse_method)
    funcs = llm_funcs or {}
    rag = RAGAnything(
        config=config,
        llm_model_func=funcs.get("llm_model_func"),
        vision_model_func=funcs.get("vision_model_func"),
        embedding_func=funcs.get("embedding_func"),
    )

    async def run() -> list[dict]:
        results: list[dict] = []
        for src in sources:
            sha = _sha256_path(src)
            out_dir = parsed_root / sha
            out_dir.mkdir(parents=True, exist_ok=True)
            try:
                await rag.process_document_complete(
                    file_path=str(src),
                    output_dir=str(out_dir),
                    parse_method=parse_method,
                    parser=parser,
                )
            except Exception as exc:  # noqa: BLE001
                print(f"raganything: failed to parse {src}: {exc}", file=sys.stderr)
                continue
            content_list_path = out_dir / "content_list.json"
            content_list = []
            if content_list_path.exists():
                try:
                    content_list = json.loads(content_list_path.read_text(encoding="utf-8"))
                except Exception:
                    content_list = []
            results.append({"path": src, "content_list": content_list})
        return results

    return asyncio.run(run())


def refresh_raganything(
    project: str | Path,
    *,
    parser: str = "mineru",
    parse_method: str = "auto",
    roots: Sequence[str] | None = None,
    force: bool = False,
    full: bool = False,
    llm_funcs: dict | None = None,
) -> int:
    root = Path(project).resolve()
    if not root.exists() or not root.is_dir():
        print(f"RAG-Anything refresh failed: project directory does not exist: {root}", file=sys.stderr)
        return 2

    if not force and not full and _artifact_is_current(root):
        print("RAG-Anything manifest is already current; skipping refresh.")
        return 0

    if full:
        for sub in ("parsed", "working_dir"):
            target = root / RAGA_ROOT / sub
            if target.exists():
                import shutil as _shutil
                _shutil.rmtree(target)

    sources = discover_sources(root, roots=roots)
    if not sources:
        print("RAG-Anything: no parseable sources found; writing empty manifest.")
        write_manifest(root, documents=[], parser=parser, git_commit=_git_head(root))
        return 0

    try:
        documents = parse_documents(
            root,
            sources=sources,
            parser=parser,
            parse_method=parse_method,
            working_dir=None,
            llm_funcs=llm_funcs,
        )
    except RuntimeError as exc:
        print(f"RAG-Anything: {exc}", file=sys.stderr)
        return 4

    write_manifest(
        root,
        documents=documents,
        parser=parser,
        git_commit=_git_head(root) or "",
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser_ = argparse.ArgumentParser(description="Refresh RAG-Anything for an LLM-Wiki project.")
    parser_.add_argument("--project", default=".", help="Project root")
    parser_.add_argument("--parser", default="mineru", choices=["mineru", "docling", "paddleocr"])
    parser_.add_argument("--parse-method", default="auto", choices=["auto", "ocr", "txt"])
    parser_.add_argument("--root", action="append", dest="roots", help="Restrict discovery to this root (repeatable)")
    parser_.add_argument("--force", action="store_true")
    parser_.add_argument("--full", action="store_true", help="Purge parsed/ and working_dir/ before refresh")
    args = parser_.parse_args(list(argv) if argv is not None else None)
    return refresh_raganything(
        args.project,
        parser=args.parser,
        parse_method=args.parse_method,
        roots=args.roots,
        force=args.force,
        full=args.full,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
