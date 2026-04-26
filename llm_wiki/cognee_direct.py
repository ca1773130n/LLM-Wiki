"""Direct Cognee ingestion helper for LLM-Wiki export bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Dict, Optional

CogneeAdd = Callable[..., Awaitable[object]]
CogneeCognify = Callable[..., Awaitable[object]]


class CogneeDirectImporter:
    """Add a generated Cognee JSONL bundle to Cognee.

    `cognify` is optional because it may invoke configured LLM/embedding providers.
    For cost-aware operation, the default is add-only ingestion of the explicit
    LLM-Wiki JSONL records.
    """

    def __init__(self, add_func: Optional[CogneeAdd] = None, cognify_func: Optional[CogneeCognify] = None) -> None:
        self.add_func = add_func
        self.cognify_func = cognify_func

    async def add_bundle(self, bundle_dir: str | Path, dataset_name: str = "llm_wiki_research_graph", cognify: bool = False) -> Dict[str, object]:
        root = Path(bundle_dir)
        files = [root / "nodes.jsonl", root / "edges.jsonl"]
        missing = [str(path) for path in files if not path.exists()]
        if missing:
            raise FileNotFoundError(f"Cognee bundle missing required files: {missing}")
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
