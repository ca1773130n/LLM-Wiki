import json

from llm_wiki.canonicalization import ReviewItem, ReviewQueue
from llm_wiki.review_workflow import ReviewQueueExporter


def sample_queue():
    return ReviewQueue([
        ReviewItem(
            id="review:similar_name:test",
            left_node_id="MethodologicalConcept:gs:test",
            right_node_id="MethodologicalConcept:4dgs:test",
            left_name="Gaussian Splatting",
            right_name="4D Gaussian Splatting",
            node_type="MethodologicalConcept",
            reason="similar_name",
            score=0.9,
        )
    ])


def test_review_queue_exporter_renders_markdown_jsonl_and_decision_template():
    exporter = ReviewQueueExporter()
    queue = sample_queue()

    markdown = exporter.render_markdown(queue)
    jsonl = exporter.render_jsonl(queue)
    template = exporter.render_decision_template(queue)

    assert "# Research Graph Review Queue" in markdown
    assert "Gaussian Splatting ↔ 4D Gaussian Splatting" in markdown
    assert "canonical_node_id" in markdown
    assert json.loads(jsonl.strip())["item_id"] == "review:similar_name:test"
    payload = json.loads(template)
    assert payload["decisions"][0]["item_id"] == "review:similar_name:test"
    assert payload["decisions"][0]["action"] == "TODO: merge|keep_separate"


def test_review_queue_exporter_writes_requested_files(tmp_path):
    exporter = ReviewQueueExporter()
    queue = sample_queue()

    markdown_path = tmp_path / "review.md"
    jsonl_path = tmp_path / "review.jsonl"
    template_path = tmp_path / "decisions.template.json"
    exporter.write_files(queue, markdown_path=markdown_path, jsonl_path=jsonl_path, decision_template_path=template_path)

    assert markdown_path.read_text(encoding="utf-8").startswith("# Research Graph Review Queue")
    assert jsonl_path.read_text(encoding="utf-8").count("\n") == 1
    assert json.loads(template_path.read_text(encoding="utf-8"))["decisions"]
