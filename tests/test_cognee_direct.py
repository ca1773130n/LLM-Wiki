import asyncio

from llm_wiki.cognee_direct import CogneeDirectImporter


def test_cognee_direct_importer_adds_bundle_files_with_dataset_name(tmp_path):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "nodes.jsonl").write_text('{"text":"node"}\n', encoding="utf-8")
    (bundle / "edges.jsonl").write_text('{"relationship":"uses"}\n', encoding="utf-8")
    calls = []

    async def fake_add(data, dataset_name="main_dataset", user=None):
        calls.append({"data": data, "dataset_name": dataset_name, "user": user})

    result = asyncio.run(CogneeDirectImporter(add_func=fake_add).add_bundle(bundle, dataset_name="llm_wiki_test"))

    assert result == {"dataset_name": "llm_wiki_test", "files_added": 2, "cognified": False}
    assert calls == [{"data": [str(bundle / "nodes.jsonl"), str(bundle / "edges.jsonl")], "dataset_name": "llm_wiki_test", "user": None}]


def test_cognee_direct_importer_can_optionally_cognify(tmp_path):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "nodes.jsonl").write_text('{"text":"node"}\n', encoding="utf-8")
    (bundle / "edges.jsonl").write_text('{"relationship":"uses"}\n', encoding="utf-8")
    calls = []

    async def fake_add(data, dataset_name="main_dataset", user=None):
        calls.append(("add", dataset_name))

    async def fake_cognify(datasets=None, user=None):
        calls.append(("cognify", datasets))
        return ["ok"]

    result = asyncio.run(CogneeDirectImporter(add_func=fake_add, cognify_func=fake_cognify).add_bundle(bundle, dataset_name="llm_wiki_test", cognify=True))

    assert result["cognified"] is True
    assert calls == [("add", "llm_wiki_test"), ("cognify", ["llm_wiki_test"])]
