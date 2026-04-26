from llm_wiki.selective_extractor import SelectiveClaudeResearchExtractor
from llm_wiki.research_graph import ResearchGraph, ResearchNode, ResearchNodeType


class FakeExtractor:
    def __init__(self, label):
        self.label = label
        self.calls = []

    def extract_file(self, path, source_kind="SourceDocument"):
        self.calls.append(str(path))
        return ResearchGraph(nodes=[ResearchNode(id=f"Paper:{self.label}:test", name=self.label, type=ResearchNodeType.PAPER)], edges=[])


def test_selective_claude_extractor_uses_claude_only_for_matching_paths(tmp_path):
    deterministic = FakeExtractor("deterministic")
    claude = FakeExtractor("claude")
    selected = tmp_path / "important" / "paper.md"
    plain = tmp_path / "plain" / "paper.md"
    selected.parent.mkdir()
    plain.parent.mkdir()
    selected.write_text("# important", encoding="utf-8")
    plain.write_text("# plain", encoding="utf-8")

    extractor = SelectiveClaudeResearchExtractor(deterministic=deterministic, claude=claude, include_patterns=["*/important/*"])

    assert extractor.extract_file(selected, source_kind="Paper").nodes[0].name == "claude"
    assert extractor.extract_file(plain, source_kind="Paper").nodes[0].name == "deterministic"
    assert claude.calls == [str(selected)]
    assert deterministic.calls == [str(plain)]


def test_selective_claude_extractor_limit_falls_back_after_budget(tmp_path):
    deterministic = FakeExtractor("deterministic")
    claude = FakeExtractor("claude")
    first = tmp_path / "papers" / "a.md"
    second = tmp_path / "papers" / "b.md"
    first.parent.mkdir()
    first.write_text("# a", encoding="utf-8")
    second.write_text("# b", encoding="utf-8")

    extractor = SelectiveClaudeResearchExtractor(deterministic=deterministic, claude=claude, include_patterns=["*.md"], claude_limit=1)

    assert extractor.extract_file(first, source_kind="Paper").nodes[0].name == "claude"
    assert extractor.extract_file(second, source_kind="Paper").nodes[0].name == "deterministic"
