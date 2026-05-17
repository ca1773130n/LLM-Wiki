"""Direct Cognee ingestion helper for Tesserae export bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Dict, Optional

CogneeAdd = Callable[..., Awaitable[object]]
CogneeCognify = Callable[..., Awaitable[object]]
CogneeConfigure = Callable[..., None]


class CogneeDirectImporter:
    """Add a generated Cognee JSONL bundle to Cognee.

    `cognify` is optional because it may invoke configured LLM/embedding providers.
    For cost-aware operation, the default is add-only ingestion of the explicit
    Tesserae JSONL records.
    """

    def __init__(self, add_func: Optional[CogneeAdd] = None, cognify_func: Optional[CogneeCognify] = None, configure_func: Optional[CogneeConfigure] = None) -> None:
        self.add_func = add_func
        self.cognify_func = cognify_func
        self.configure_func = configure_func

    async def add_bundle(self, bundle_dir: str | Path, dataset_name: str = "tesserae_research_graph", cognify: bool = False, system_root: str | Path | None = None, data_root: str | Path | None = None) -> Dict[str, object]:
        root = Path(bundle_dir)
        files = [root / "nodes.jsonl", root / "edges.jsonl"]
        missing = [str(path) for path in files if not path.exists()]
        if missing:
            raise FileNotFoundError(f"Cognee bundle missing required files: {missing}")
        if system_root or data_root:
            configure_func = self.configure_func or configure_cognee_roots
            configure_func(system_root=system_root, data_root=data_root)
        add_func = self.add_func or import_cognee_add()
        await add_func([str(path) for path in files], dataset_name=dataset_name)
        cognify_result = None
        if cognify:
            cognify_func = self.cognify_func or import_cognee_cognify()
            cognify_result = await cognify_func(datasets=[dataset_name])
        result = {
            "dataset_name": dataset_name,
            "files_added": len(files),
            "cognified": bool(cognify),
        }
        if cognify:
            result["cognify_result"] = cognify_result
        return result


def configure_cognee_roots(system_root: str | Path | None = None, data_root: str | Path | None = None) -> None:
    try:
        import cognee
    except ImportError as exc:
        raise RuntimeError("cognee is not installed. Install it with: python3 -m pip install --user cognee") from exc
    if system_root:
        cognee.config.system_root_directory(str(Path(system_root)))
    if data_root:
        cognee.config.data_root_directory(str(Path(data_root)))


def import_cognee_add():
    try:
        import cognee
    except ImportError as exc:
        raise RuntimeError("cognee is not installed. Install it with: python3 -m pip install --user cognee") from exc
    return cognee.add


def import_cognee_cognify():
    try:
        import cognee
    except ImportError as exc:
        raise RuntimeError("cognee is not installed. Install it with: python3 -m pip install --user cognee") from exc
    return cognee.cognify
