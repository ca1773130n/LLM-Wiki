"""Development-code graph extraction for project-local LLM-Wiki workspaces.

Research notes and code projects share the same validated ResearchGraph pipeline,
but code gets a separate ontology slice: project → source files → symbols →
dependencies. This follows Karpathy's wiki philosophy by treating source files as
immutable raw evidence and generated graph/markdown/site artifacts as projections.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Iterable, List, Optional

from .research_graph import ResearchGraph, ResearchGraphBuilder, ResearchNode, ResearchNodeType

CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".swift", ".c", ".h", ".cpp", ".hpp", ".cs", ".rb", ".php", ".sh", ".zsh", ".bash", ".sql"}
SKIP_PARTS = {".git", ".llm-wiki", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".next", ".cache", ".pytest_cache", "target"}


class CodeGraphExtractor:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()

    def extract_paths(self, paths: Iterable[str | Path]) -> ResearchGraph:
        builder = ResearchGraphBuilder()
        project = builder.add_node(
            self.project_root.name,
            ResearchNodeType.CODE_PROJECT,
            description=f"Development code project at {self.project_root}",
            source_path=str(self.project_root),
            metadata={"layer": "project", "source_kind": "CodeProject"},
        )
        for file_path in self.iter_code_files(paths):
            self._extract_file(builder, project, file_path)
        return builder.build()

    def iter_code_files(self, paths: Iterable[str | Path]) -> List[Path]:
        files: List[Path] = []
        for raw in paths:
            path = Path(raw)
            if not path.is_absolute():
                path = self.project_root / path
            if path.is_file() and is_code_file(path) and not should_skip(path):
                files.append(path)
            elif path.is_dir():
                for child in sorted(path.rglob("*")):
                    if child.is_file() and is_code_file(child) and not should_skip(child):
                        files.append(child)
        return sorted(dict.fromkeys(files))

    def _extract_file(self, builder: ResearchGraphBuilder, project: ResearchNode, path: Path) -> None:
        rel = safe_relative(path, self.project_root)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        file_node = builder.add_node(
            rel,
            ResearchNodeType.SOURCE_FILE,
            description=first_nonempty_line(text) or f"Source file {rel}",
            source_path=str(path),
            metadata={"layer": "raw-code", "language": language_for(path), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "bytes": len(text.encode("utf-8"))},
        )
        builder.add_edge(project, "contains", file_node, evidence=f"{rel} is inside {self.project_root.name}")
        if path.suffix == ".py":
            self._extract_python(builder, file_node, text)
        else:
            self._extract_text_symbols(builder, file_node, text)

    def _extract_python(self, builder: ResearchGraphBuilder, file_node: ResearchNode, text: str) -> None:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            self._extract_text_symbols(builder, file_node, text)
            return
        class_stack: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for dep in dependencies_from_import(node):
                    dep_node = builder.add_node(dep, ResearchNodeType.DEPENDENCY, metadata={"layer": "dependency"})
                    builder.add_edge(file_node, "imports", dep_node, evidence=f"{file_node.name} imports {dep}")
            elif isinstance(node, ast.ClassDef):
                class_node = builder.add_node(node.name, ResearchNodeType.CODE_CLASS, source_path=file_node.source_path, metadata={"layer": "symbol", "line": node.lineno})
                builder.add_edge(file_node, "defines", class_node, evidence=f"class {node.name} defined in {file_node.name}")
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fn = f"{node.name}.{child.name}"
                        fn_node = builder.add_node(fn, ResearchNodeType.CODE_FUNCTION, source_path=file_node.source_path, metadata={"layer": "symbol", "line": child.lineno, "parent_class": node.name})
                        builder.add_edge(class_node, "contains", fn_node, evidence=f"{fn} is a method on {node.name}")
                        builder.add_edge(file_node, "defines", fn_node, evidence=f"method {fn} defined in {file_node.name}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not class_stack:
                # ast.walk does not expose parents; skip methods already emitted via ClassDef body.
                if "." not in node.name:
                    fn_node = builder.add_node(node.name, ResearchNodeType.CODE_FUNCTION, source_path=file_node.source_path, metadata={"layer": "symbol", "line": node.lineno})
                    builder.add_edge(file_node, "defines", fn_node, evidence=f"function {node.name} defined in {file_node.name}")

    def _extract_text_symbols(self, builder: ResearchGraphBuilder, file_node: ResearchNode, text: str) -> None:
        for name in simple_symbol_names(text):
            fn_node = builder.add_node(name, ResearchNodeType.CODE_FUNCTION, source_path=file_node.source_path, metadata={"layer": "symbol"})
            builder.add_edge(file_node, "defines", fn_node, evidence=f"symbol {name} found in {file_node.name}")


def dependencies_from_import(node: ast.AST) -> List[str]:
    if isinstance(node, ast.Import):
        return sorted({alias.name.split(".")[0] for alias in node.names})
    if isinstance(node, ast.ImportFrom):
        return [node.module.split(".")[0]] if node.module else []
    return []


def is_code_file(path: Path) -> bool:
    return path.suffix.lower() in CODE_SUFFIXES


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def safe_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def language_for(path: Path) -> str:
    return {".py": "python", ".js": "javascript", ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript", ".rs": "rust", ".go": "go"}.get(path.suffix.lower(), path.suffix.lower().lstrip(".") or "text")


def first_nonempty_line(text: str) -> Optional[str]:
    for line in text.splitlines():
        stripped = line.strip().lstrip("#/")
        if stripped:
            return stripped[:160]
    return None


def simple_symbol_names(text: str) -> List[str]:
    import re
    names = []
    for pattern in [r"function\s+([A-Za-z_][A-Za-z0-9_]*)", r"class\s+([A-Za-z_][A-Za-z0-9_]*)", r"def\s+([A-Za-z_][A-Za-z0-9_]*)"]:
        names.extend(re.findall(pattern, text))
    return sorted(set(names))
