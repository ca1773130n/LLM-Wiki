"""Research-domain literature intelligence graph primitives.

This module is intentionally independent from Cognee/Graphiti. It defines the
controlled research ontology and a deterministic baseline extractor that can be
used in tests and as a guardrail around future Claude/Cognee extraction.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


class ResearchNodeType(str, Enum):
    # Field / taxonomy layer
    RESEARCH_FIELD = "ResearchField"
    RESEARCH_TOPIC = "ResearchTopic"
    PROBLEM_AREA = "ProblemArea"
    APPROACH_FAMILY = "ApproachFamily"
    TREND = "Trend"

    # Source / artifact layer
    SOURCE_DOCUMENT = "SourceDocument"
    PAPER = "Paper"
    REPOSITORY = "Repository"
    PROJECT = "Project"
    MODEL = "Model"
    DATASET = "Dataset"
    BENCHMARK = "Benchmark"
    METRIC = "Metric"
    RESULT = "Result"
    ORGANIZATION = "Organization"
    PERSON = "Person"
    CODE_PROJECT = "CodeProject"
    SOURCE_FILE = "SourceFile"
    CODE_MODULE = "CodeModule"
    CODE_CLASS = "CodeClass"
    CODE_FUNCTION = "CodeFunction"
    DEPENDENCY = "Dependency"

    # Concept layer
    CONCEPT = "Concept"
    TECHNICAL_TERM = "TechnicalTerm"
    MATHEMATICAL_CONCEPT = "MathematicalConcept"
    METHODOLOGICAL_CONCEPT = "MethodologicalConcept"
    ALGORITHM = "Algorithm"
    OBJECTIVE_FUNCTION = "ObjectiveFunction"
    ARCHITECTURE_PATTERN = "ArchitecturePattern"
    TRAINING_PARADIGM = "TrainingParadigm"
    INFERENCE_STRATEGY = "InferenceStrategy"
    EVALUATION_PROTOCOL = "EvaluationProtocol"
    TASK = "Task"
    CAPABILITY = "Capability"

    # Assertion layer
    CLAIM = "Claim"
    CONTRIBUTION_CLAIM = "ContributionClaim"
    PERFORMANCE_CLAIM = "PerformanceClaim"
    COMPARISON_CLAIM = "ComparisonClaim"
    LIMITATION_CLAIM = "LimitationClaim"
    CAUSAL_CLAIM = "CausalClaim"
    OPEN_QUESTION = "OpenQuestion"
    EVIDENCE_SPAN = "EvidenceSpan"

    # Synthesis layer (higher-order, generated)
    SYNTHESIS = "Synthesis"


ALLOWED_NODE_TYPES: Set[str] = {item.value for item in ResearchNodeType}

ALLOWED_EDGE_TYPES: Set[str] = {
    "is_a",
    "part_of",
    "subfield_of",
    "introduces",
    "uses",
    "extends",
    "improves_on",
    "compares_against",
    "criticizes",
    "addresses",
    "optimizes_for",
    "uses_dataset",
    "evaluated_on",
    "uses_metric",
    "reports_result",
    "achieves_score",
    "belongs_to_approach_family",
    "shares_concept_with",
    "derived_from",
    "supports_claim",
    "contradicts_claim",
    "attributes_improvement_to",
    "has_limitation",
    "evidenced_by",
    "mentioned_in",
    "authored_by",
    "released_by",
    "implemented_in",
    "rising_in",
    "declining_in",
    "emerged_after",
    "contains",
    "defines",
    "imports",
    "calls",
    "documents",
    "synthesizes",
    "summarizes",
}


@dataclass(frozen=True)
class ResearchNode:
    id: str
    name: str
    type: ResearchNodeType
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    source_path: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)

    def model_dump(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["type"] = self.type.value
        return payload


@dataclass(frozen=True)
class ResearchEdge:
    source: str
    target: str
    type: str
    evidence: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in ALLOWED_EDGE_TYPES:
            raise ValueError(f"Unsupported research edge type: {self.type}")

    def model_dump(self) -> Dict[str, object]:
        return asdict(self)


def is_arxiv_placeholder_name(name: str) -> bool:
    return re.fullmatch(r"arXiv:\d{4}\.\d{4,6}", name.strip(), flags=re.IGNORECASE) is not None


def prefer_research_node(existing: ResearchNode, incoming: ResearchNode) -> ResearchNode:
    """Merge duplicate nodes while preferring verified paper titles.

    Digest/source-document pages can discover papers as ``arXiv:<id>`` or weak
    context titles. When the real per-paper raw document is also ingested, keep
    the same stable node id but upgrade the display name to the paper title.
    """
    quality_rank = {"arxiv_only": 0, "reference_context": 1, "paper_file": 3, "verified": 4}
    existing_quality = str(existing.metadata.get("title_quality") or "")
    incoming_quality = str(incoming.metadata.get("title_quality") or "")
    existing_placeholder = is_arxiv_placeholder_name(existing.name)
    incoming_placeholder = is_arxiv_placeholder_name(incoming.name)
    if quality_rank.get(incoming_quality, 2) > quality_rank.get(existing_quality, 2):
        chosen = incoming
    elif existing_placeholder and not incoming_placeholder:
        chosen = incoming
    else:
        chosen = existing
    other = existing if chosen is incoming else incoming
    aliases = set(existing.aliases) | set(incoming.aliases)
    if other.name != chosen.name:
        aliases.add(other.name)
    aliases.discard(chosen.name)
    metadata = {**other.metadata, **chosen.metadata}
    return ResearchNode(
        id=chosen.id,
        name=chosen.name,
        type=chosen.type,
        aliases=sorted(aliases),
        description=chosen.description or other.description,
        source_path=chosen.source_path or other.source_path,
        metadata=metadata,
    )


@dataclass
class ResearchGraph:
    nodes: List[ResearchNode] = field(default_factory=list)
    edges: List[ResearchEdge] = field(default_factory=list)

    def model_dump(self) -> Dict[str, object]:
        return {
            "nodes": [node.model_dump() for node in self.nodes],
            "edges": [edge.model_dump() for edge in self.edges],
        }

    def to_json(self, **kwargs: object) -> str:
        return json.dumps(self.model_dump(), ensure_ascii=False, **kwargs)

    def has_edge_type(self, edge_type: str) -> bool:
        return any(edge.type == edge_type for edge in self.edges)


class ResearchGraphBuilder:
    def __init__(self) -> None:
        self._nodes: Dict[str, ResearchNode] = {}
        self._edges: Dict[Tuple[str, str, str], ResearchEdge] = {}

    def add_node(
        self,
        name: str,
        node_type: ResearchNodeType,
        aliases: Optional[Sequence[str]] = None,
        description: str = "",
        source_path: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
        id_seed: Optional[str] = None,
    ) -> ResearchNode:
        canonical_name = normalize_display_name(name)
        # ``id_seed`` lets callers (e.g. Paper extraction) decouple the stable
        # node id from the human-readable display name. We use this so the
        # arxiv id pins the node identity while the title can still be the
        # nice title pulled from the paper file.
        node_id = stable_id(node_type.value, id_seed or canonical_name)
        existing = self._nodes.get(node_id)
        if existing:
            incoming = ResearchNode(
                id=existing.id,
                name=canonical_name,
                type=node_type,
                aliases=list(aliases or []),
                description=description,
                source_path=source_path,
                metadata=metadata or {},
            )
            node = prefer_research_node(existing, incoming)
            self._nodes[node_id] = node
            return node
        node = ResearchNode(
            id=node_id,
            name=canonical_name,
            type=node_type,
            aliases=list(aliases or []),
            description=description,
            source_path=source_path,
            metadata=metadata or {},
        )
        self._nodes[node_id] = node
        return node

    def add_edge(
        self,
        source: ResearchNode,
        edge_type: str,
        target: ResearchNode,
        evidence: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> ResearchEdge:
        edge = ResearchEdge(source=source.id, target=target.id, type=edge_type, evidence=evidence, metadata=metadata or {})
        self._edges[(edge.source, edge.type, edge.target)] = edge
        return edge

    def build(self) -> ResearchGraph:
        # Keep source artifacts last so convenience maps keyed by display name
        # prefer the concrete Paper/Repository over an identically named
        # ApproachFamily candidate.
        source_types = {ResearchNodeType.PAPER, ResearchNodeType.REPOSITORY, ResearchNodeType.SOURCE_DOCUMENT}
        nodes = sorted(self._nodes.values(), key=lambda node: node.type in source_types)
        return ResearchGraph(nodes=nodes, edges=list(self._edges.values()))


@dataclass(frozen=True)
class TermRule:
    canonical_name: str
    node_type: ResearchNodeType
    aliases: Tuple[str, ...] = ()
    approach_family: Optional[str] = None

    def patterns(self) -> Tuple[str, ...]:
        return (self.canonical_name, *self.aliases)


DEFAULT_TERM_RULES: Tuple[TermRule, ...] = (
    TermRule("Gaussian Splatting", ResearchNodeType.METHODOLOGICAL_CONCEPT, ("3D Gaussian Splatting", "3DGS", "GS"), "Gaussian Splatting Reconstruction"),
    TermRule("Geometry-Grounded Gaussian Splatting", ResearchNodeType.APPROACH_FAMILY, ("Geometry-Grounded GS",), "Geometry-Grounded Gaussian Splatting"),
    TermRule("Novel View Synthesis", ResearchNodeType.TASK, ("new view synthesis",)),
    TermRule("Shape Reconstruction", ResearchNodeType.TASK, ("형상 재구성", "geometry extraction", "기하 추출")),
    TermRule("Stochastic Solid", ResearchNodeType.MATHEMATICAL_CONCEPT, ("stochastic solid",)),
    TermRule("Volumetric Rendering", ResearchNodeType.METHODOLOGICAL_CONCEPT, ("volumetric 특성", "volumetric")),
    TermRule("Depth Map", ResearchNodeType.TECHNICAL_TERM, ("depth map", "depth maps")),
    TermRule("Multi-View Consistency", ResearchNodeType.EVALUATION_PROTOCOL, ("multi-view consistency",)),
    TermRule("Floaters", ResearchNodeType.LIMITATION_CLAIM, ("floaters",)),
    TermRule("4D Gaussian Splatting", ResearchNodeType.METHODOLOGICAL_CONCEPT, ("4DGS", "4D Gaussian Splatting"), "Dynamic Gaussian Splatting"),
    TermRule("Video Diffusion", ResearchNodeType.METHODOLOGICAL_CONCEPT, ("video diffusion",)),
    TermRule("Point Cloud", ResearchNodeType.TECHNICAL_TERM, ("point cloud", "4D point cloud")),
    TermRule("Image-to-3D", ResearchNodeType.TASK, ("image-to-3D",)),
    TermRule("World Model", ResearchNodeType.RESEARCH_TOPIC, ("world model", "world models")),
    TermRule("Pseudo-Mask", ResearchNodeType.TECHNICAL_TERM, ("pseudo-mask", "pseudo mask")),
    TermRule("Object-Level Prior", ResearchNodeType.METHODOLOGICAL_CONCEPT, ("object-level prior", "object-level pseudo-mask")),
    TermRule("Visual SLAM", ResearchNodeType.RESEARCH_TOPIC, ("Visual SLAM", "SLAM")),
    TermRule("Multi-Robot Cooperative Mapping", ResearchNodeType.TASK, ("multi-robot cooperative mapping",)),
)


class ResearchGraphExtractor:
    """Deterministic baseline extractor for research-literature intelligence graphs.

    The long-term extractor should be LLM-backed, but this baseline enforces the
    domain ontology and provides stable tests/evaluation fixtures.
    """

    def __init__(self, term_rules: Sequence[TermRule] = DEFAULT_TERM_RULES) -> None:
        self.term_rules = tuple(term_rules)

    def extract_file(self, path: str | Path, source_kind: str = "SourceDocument") -> ResearchGraph:
        file_path = Path(path)
        return self.extract_text(file_path.read_text(encoding="utf-8", errors="replace"), str(file_path), source_kind)

    def extract_text(
        self,
        text: str,
        source_path: Optional[str] = None,
        source_kind: str = "SourceDocument",
    ) -> ResearchGraph:
        builder = ResearchGraphBuilder()
        title = extract_title(text, source_path)
        source_type = source_kind_to_node_type(source_kind, source_path)
        source_metadata = extract_source_metadata(text, source_path)
        if source_type == ResearchNodeType.SOURCE_DOCUMENT and is_social_feed_source_path(source_path):
            return builder.build()
        # Pre-compute heading-derived candidate paper titles so we can attach
        # them to the source-document metadata up-front (ResearchNode is frozen).
        candidate_paper_titles, surviving_concept_headings = self._classify_document_headings(text)
        paper_metadata: Dict[str, object] = {"source_kind": source_kind, **source_metadata}
        if source_type == ResearchNodeType.PAPER:
            paper_metadata["title_quality"] = "paper_file" if is_verified_paper_title(title, source_metadata) else "arxiv_only"

        # When the path identifies a Paper subfolder we want all references
        # (digest mentions, per-paper file ingest) to collapse onto the same
        # node id. We achieve that by seeding stable_id with ``arXiv:<id>``
        # while keeping the human-readable title as the display name, with
        # the arxiv id captured as an alias for cross-reference search.
        arxiv_id = str(source_metadata.get("arxiv_id", ""))
        if source_type == ResearchNodeType.PAPER and arxiv_id:
            display_name = title if is_verified_paper_title(title, source_metadata) else f"arXiv:{arxiv_id}"
            aliases: List[str] = [f"arXiv:{arxiv_id}"]
            paper = builder.add_node(
                display_name,
                source_type,
                aliases=aliases,
                source_path=source_path,
                metadata=paper_metadata,
                id_seed=f"arXiv:{arxiv_id}",
            )
        else:
            if candidate_paper_titles:
                paper_metadata["candidate_paper_titles"] = candidate_paper_titles
            paper = builder.add_node(title, source_type, source_path=source_path, metadata=paper_metadata)

        if source_type in {ResearchNodeType.SOURCE_DOCUMENT, ResearchNodeType.REPOSITORY, ResearchNodeType.PROJECT}:
            self._add_document_structure(builder, paper, surviving_concept_headings, source_path)
            self._extract_paper_references(builder, paper, text, source_path)
            return builder.build()

        field = builder.add_node(infer_research_field(text), ResearchNodeType.RESEARCH_FIELD)
        builder.add_edge(paper, "part_of", field)
        research_text = strip_non_research_scaffold(text)

        matched_terms: List[ResearchNode] = []
        for rule in self.term_rules:
            evidence = find_evidence(research_text, rule.patterns())
            if not evidence:
                continue
            node = builder.add_node(
                rule.canonical_name,
                rule.node_type,
                aliases=list(rule.aliases),
                source_path=source_path,
            )
            matched_terms.append(node)
            relation = relation_for_node_type(rule.node_type)
            builder.add_edge(paper, relation, node, evidence=evidence)

            span = self._add_evidence(builder, paper, evidence, source_path)
            claim = self._add_claim_for_term(builder, paper, node, evidence, source_path)
            builder.add_edge(claim, "evidenced_by", span, evidence=evidence)
            builder.add_edge(claim, "mentioned_in", paper, evidence=evidence)

            if rule.approach_family:
                family = builder.add_node(rule.approach_family, ResearchNodeType.APPROACH_FAMILY)
                builder.add_edge(paper, "belongs_to_approach_family", family, evidence=evidence)
                if node.type != ResearchNodeType.APPROACH_FAMILY:
                    builder.add_edge(family, "uses", node, evidence=evidence)

        self._add_comparative_claims(builder, paper, research_text, source_path)
        self._connect_related_terms(builder, matched_terms, research_text)
        return builder.build()

    def _classify_document_headings(self, text: str) -> Tuple[List[str], List[str]]:
        """Sort markdown headings into (paper-title candidates, concept-shaped)."""
        candidate_paper_titles: List[str] = []
        concept_headings: List[str] = []
        whitelist_terms = {rule.canonical_name.lower() for rule in self.term_rules}
        whitelist_terms |= {alias.lower() for rule in self.term_rules for alias in rule.aliases}
        for raw in extract_markdown_headings(text):
            cleaned = _strip_heading_numbering(raw)
            if not cleaned:
                continue
            if _is_generic_section_heading(cleaned):
                continue
            if _looks_like_paper_title_heading(raw, cleaned):
                candidate_paper_titles.append(cleaned)
                continue
            if _is_concept_shaped_heading(cleaned, whitelist_terms):
                concept_headings.append(cleaned)
        # Cap heading-derived concepts at 6 per file to limit pollution.
        return candidate_paper_titles, concept_headings[:6]

    def _add_document_structure(
        self,
        builder: ResearchGraphBuilder,
        document: ResearchNode,
        concept_headings: Sequence[str],
        source_path: Optional[str],
    ) -> None:
        for heading in concept_headings:
            if heading.lower() == document.name.lower():
                continue
            concept = builder.add_node(
                heading,
                ResearchNodeType.CONCEPT,
                description=f"Section heading in {document.name}",
                source_path=source_path,
                metadata={"source_kind": "document_heading"},
            )
            builder.add_edge(document, "documents", concept)

    def _extract_paper_references(
        self,
        builder: ResearchGraphBuilder,
        document: ResearchNode,
        text: str,
        source_path: Optional[str],
    ) -> None:
        """Promote arxiv links inside research-corpus digest/feed bodies to Paper refs."""
        normalized_source_path = source_path.replace("\\", "/") if source_path else ""
        if not normalized_source_path or "data/research/" not in normalized_source_path:
            return
        seen: Set[str] = set()
        # arxiv URLs (http/https, abs|pdf), bare ``arXiv:NNNN.NNNNN``, and
        # relative paths to ``papers/<id>/paper.md``.
        patterns = (
            re.compile(r"https?://arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,6})", re.IGNORECASE),
            re.compile(r"\barxiv\s*:\s*(\d{4}\.\d{4,6})", re.IGNORECASE),
            re.compile(r"papers/(\d{4}\.\d{4,6})/(?:paper|main|abstract)\.md", re.IGNORECASE),
        )
        for pattern in patterns:
            for match in pattern.finditer(text):
                arxiv_id = match.group(1)
                if arxiv_id in seen:
                    continue
                seen.add(arxiv_id)
                display_name = f"arXiv:{arxiv_id}"
                title_quality = "arxiv_only"
                paper = builder.add_node(
                    display_name,
                    ResearchNodeType.PAPER,
                    aliases=[f"arXiv:{arxiv_id}"],
                    source_path=source_path,
                    metadata={
                        "source_kind": "Paper",
                        "arxiv_id": arxiv_id,
                        "title_quality": title_quality,
                        "discovered_in": document.source_path or source_path,
                    },
                    id_seed=f"arXiv:{arxiv_id}",
                )
                builder.add_edge(document, "mentioned_in", paper)

    def _add_evidence(self, builder: ResearchGraphBuilder, paper: ResearchNode, evidence: str, source_path: Optional[str]) -> ResearchNode:
        name = "Evidence: " + truncate(evidence, 72)
        span = builder.add_node(name, ResearchNodeType.EVIDENCE_SPAN, description=evidence, source_path=source_path)
        builder.add_edge(span, "part_of", paper, evidence=evidence)
        return span

    def _add_claim_for_term(
        self,
        builder: ResearchGraphBuilder,
        paper: ResearchNode,
        term: ResearchNode,
        evidence: str,
        source_path: Optional[str],
    ) -> ResearchNode:
        claim_type = classify_claim_type(evidence)
        claim = builder.add_node(
            "Claim: " + truncate(evidence, 96),
            claim_type,
            description=evidence,
            source_path=source_path,
        )
        builder.add_edge(paper, "supports_claim", claim, evidence=evidence)
        builder.add_edge(claim, "uses" if term.type not in {ResearchNodeType.TASK, ResearchNodeType.CAPABILITY} else "addresses", term, evidence=evidence)
        return claim

    def _add_comparative_claims(
        self, builder: ResearchGraphBuilder, paper: ResearchNode, text: str, source_path: Optional[str]
    ) -> None:
        sentences = split_sentences(text)
        for sentence in sentences:
            if any(marker in sentence.lower() for marker in ["우수", "outperform", "better", "improve", "성능"]):
                claim = builder.add_node(
                    "Performance claim: " + truncate(sentence, 96),
                    ResearchNodeType.PERFORMANCE_CLAIM,
                    description=sentence,
                    source_path=source_path,
                )
                span = self._add_evidence(builder, paper, sentence, source_path)
                builder.add_edge(paper, "supports_claim", claim, evidence=sentence)
                builder.add_edge(claim, "evidenced_by", span, evidence=sentence)
                if "dataset" in sentence.lower() or "데이터셋" in sentence:
                    dataset = builder.add_node("Public Datasets", ResearchNodeType.DATASET)
                    builder.add_edge(claim, "evaluated_on", dataset, evidence=sentence)

    def _connect_related_terms(self, builder: ResearchGraphBuilder, terms: Sequence[ResearchNode], text: str) -> None:
        names = {term.name: term for term in terms}
        if "Stochastic Solid" in names and "Gaussian Splatting" in names:
            builder.add_edge(names["Geometry-Grounded Gaussian Splatting"] if "Geometry-Grounded Gaussian Splatting" in names else names["Gaussian Splatting"], "uses", names["Stochastic Solid"])
        if "Depth Map" in names and "Shape Reconstruction" in names:
            builder.add_edge(names["Depth Map"], "addresses", names["Shape Reconstruction"])


class ResearchCorpusAnalyzer:
    """Corpus-level projections over already validated ResearchGraph objects.

    This deliberately consumes typed graphs instead of raw text so trend creation
    stays downstream from the controlled ontology and cannot introduce arbitrary
    node/edge types.
    """

    TREND_ELIGIBLE_TYPES = {
        ResearchNodeType.RESEARCH_TOPIC,
        ResearchNodeType.PROBLEM_AREA,
        ResearchNodeType.APPROACH_FAMILY,
        ResearchNodeType.MATHEMATICAL_CONCEPT,
        ResearchNodeType.METHODOLOGICAL_CONCEPT,
        ResearchNodeType.ALGORITHM,
        ResearchNodeType.OBJECTIVE_FUNCTION,
        ResearchNodeType.ARCHITECTURE_PATTERN,
        ResearchNodeType.TRAINING_PARADIGM,
        ResearchNodeType.INFERENCE_STRATEGY,
        ResearchNodeType.EVALUATION_PROTOCOL,
        ResearchNodeType.TASK,
        ResearchNodeType.CAPABILITY,
        ResearchNodeType.TECHNICAL_TERM,
    }

    def summarize_trends(self, graphs: Sequence[ResearchGraph], min_sources: int = 2) -> ResearchGraph:
        builder = ResearchGraphBuilder()
        occurrences: Dict[str, Dict[str, object]] = {}

        for graph in graphs:
            for node in graph.nodes:
                builder.add_node(
                    node.name,
                    node.type,
                    aliases=node.aliases,
                    description=node.description,
                    source_path=node.source_path,
                    metadata=node.metadata,
                )
            nodes_by_id = {node.id: node for node in graph.nodes}
            for edge in graph.edges:
                source = nodes_by_id.get(edge.source)
                target = nodes_by_id.get(edge.target)
                if source and target:
                    merged_source = builder.add_node(source.name, source.type, aliases=source.aliases, description=source.description, source_path=source.source_path, metadata=source.metadata)
                    merged_target = builder.add_node(target.name, target.type, aliases=target.aliases, description=target.description, source_path=target.source_path, metadata=target.metadata)
                    builder.add_edge(merged_source, edge.type, merged_target, evidence=edge.evidence, metadata=edge.metadata)

            source_dates = sorted({node.metadata.get("analysis_date") for node in graph.nodes if node.metadata.get("analysis_date")})
            graph_date = str(source_dates[0]) if source_dates else None
            source_paths = sorted({node.source_path for node in graph.nodes if node.source_path})
            graph_source = source_paths[0] if source_paths else None

            for node in graph.nodes:
                if node.type not in self.TREND_ELIGIBLE_TYPES:
                    continue
                bucket = occurrences.setdefault(node.id, {"node": node, "dates": set(), "sources": set()})
                if graph_date:
                    bucket["dates"].add(graph_date)  # type: ignore[union-attr]
                if graph_source:
                    bucket["sources"].add(graph_source)  # type: ignore[union-attr]

        for bucket in occurrences.values():
            node = bucket["node"]
            dates = sorted(bucket["dates"])
            sources = sorted(bucket["sources"])
            if len(sources) < min_sources:
                continue
            trend = builder.add_node(
                f"Trend: {node.name}",
                ResearchNodeType.TREND,
                description=f"{node.name} appears across {len(sources)} research sources.",
                metadata={
                    "concept_id": node.id,
                    "source_count": len(sources),
                    "sources": sources,
                    "first_seen": dates[0] if dates else None,
                    "last_seen": dates[-1] if dates else None,
                },
            )
            merged_node = builder.add_node(node.name, node.type, aliases=node.aliases, description=node.description, source_path=node.source_path, metadata=node.metadata)
            builder.add_edge(merged_node, "rising_in", trend)

        return builder.build()


def extract_markdown_headings(text: str) -> List[str]:
    headings: List[str] = []
    for line in text.splitlines():
        match = re.match(r"^#{1,4}\s+(.+?)\s*$", line.strip())
        if not match:
            continue
        heading = re.sub(r"\s+#*$", "", match.group(1)).strip()
        if heading and heading not in headings:
            headings.append(heading)
    return headings


# Regexes for daily-digest path classification. They match anywhere inside a
# normalised forward-slash path so `data/research/<anything>/papers/<id>/...`
# windows-style or absolute prefixes both classify correctly.
_PAPER_SUBFOLDER_RE = re.compile(
    r"data/research/.+?/papers/(\d{4}\.\d{4,6})/(?:paper|main|abstract)\.md$",
    re.IGNORECASE,
)
_PAPER_REPO_FILE_RE = re.compile(
    r"data/research/.+?/papers/(\d{4}\.\d{4,6})/repo\.md$",
    re.IGNORECASE,
)
_DAILY_REPOS_RE = re.compile(r"data/research/.+?/repos/.+?\.md$", re.IGNORECASE)
_DAILY_FEEDS_RE = re.compile(r"data/research/.+?/feeds/.+?\.md$", re.IGNORECASE)


VERIFIED_PAPER_TITLE_QUALITIES = {"paper_file", "verified"}


def is_social_feed_source_path(source_path: Optional[str]) -> bool:
    if not source_path:
        return False
    return _DAILY_FEEDS_RE.search(source_path.replace("\\", "/")) is not None


def is_public_research_node(node: ResearchNode) -> bool:
    """Return whether a node should appear in the public wiki/site projection.

    Social feed captures are noisy evidence inputs, not durable wiki entities.
    Likewise, arXiv mentions that have not been resolved from a real paper file
    must not become public paper pages.
    """
    if is_social_feed_source_path(node.source_path):
        return False
    if node.type == ResearchNodeType.PAPER:
        quality = str(node.metadata.get("title_quality") or "")
        if quality and quality not in VERIFIED_PAPER_TITLE_QUALITIES:
            return False
    return True


def infer_arxiv_reference_title(text: str, arxiv_match_start: int) -> Optional[str]:
    """Infer a paper title from local feed context before an arXiv URL.

    Twitter/RSS feed captures often store entries as:
    ``Title<br><br>Authors<br>https://arxiv.org/abs/...``. In that case the
    arXiv id alone is a poor display name, and the nearby title is already in
    the raw document.
    """
    window = text[max(0, arxiv_match_start - 800) : arxiv_match_start]
    window = html.unescape(window)
    window = window.replace("\\n", "\n")
    window = re.sub(r"<br\s*/?>", "\n", window, flags=re.IGNORECASE)
    window = re.sub(r"<[^>]+>", " ", window)
    segments = [segment.strip(" \t#>-*") for segment in re.split(r"\n{2,}|\r\n{2,}", window)]
    for segment in reversed([segment for segment in segments if segment.strip()]):
        lines = [line.strip(" \t#>-*") for line in segment.splitlines() if line.strip()]
        if not lines:
            continue
        candidate = lines[0]
        candidate = re.sub(r"https?://\S+", "", candidate).strip()
        candidate = strip_trailing_authors(candidate)
        candidate = normalize_display_name(candidate)
        if _is_plausible_arxiv_context_title(candidate):
            return candidate
    return None


def strip_trailing_authors(candidate: str) -> str:
    if "," not in candidate:
        return candidate
    prefix = candidate.split(",", 1)[0].strip()
    match = re.match(r"^(?P<title>.+?)\s+[A-Z][A-Za-z'\-]+\s+[A-Z][A-Za-z'\-]+$", prefix)
    if match and len(match.group("title")) >= 12:
        return match.group("title").strip()
    return candidate


def _is_plausible_arxiv_context_title(candidate: str) -> bool:
    if not candidate:
        return False
    lowered = candidate.lower()
    if lowered in {"arxiv", "본문", "feed"} or "arxiv.org" in lowered:
        return False
    if lowered.startswith(("url", "date", "author", "작성자", "논문 분석", "rt ", "tl;dr", "extract ", "📄", "논문:")):
        return False
    if any(marker in lowered for marker in ("released #", "we just released", "join our discord", "goated things", "what's the right representation")):
        return False
    if re.fullmatch(r"\d{4}\.\d{4,6}", candidate):
        return False
    if len(candidate) < 8 or len(candidate) > 220:
        return False
    if "," in candidate and not re.search(r"\b(of|for|with|in|and|to|from|via|towards?|using|learning|neural|model|models|graph|image|video|3d|4d)\b", candidate, re.IGNORECASE):
        return False
    tokens = re.findall(r"[A-Za-z][A-Za-z'-]*", candidate)
    if 1 <= len(tokens) <= 3 and all(token[:1].isupper() and token[1:].islower() for token in tokens):
        return False
    return True


def strip_non_research_scaffold(text: str) -> str:
    """Remove scraper/UI/provenance scaffolding before extracting claims.

    The raw paper note remains immutable; this only affects graph claim/evidence
    extraction so headings like ``# 논문 분석`` and papers.cool chrome do not
    become claims or evidence spans.
    """
    cleaned: List[str] = []
    skip_exact = {
        "search", "filter", "highlight", "export", "save", "copy", "rel",
        "include or:", "exclude:", "stared paper(s):", "magic token:",
        "english", "中文", "desc language:", "kimi language:",
    }
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            cleaned.append("")
            continue
        lowered = line.lower().strip(" -*_`#")
        if line.startswith("# 논문 분석") or re.fullmatch(r"#{1,6}\s*\d{4}\.\d{4,6}", line):
            continue
        if line.startswith("> - arxiv:") or line.startswith("> - papers.cool:") or line.startswith("> - 분석일:"):
            continue
        if re.fullmatch(r"#{1,6}\s*#?\d+", line):
            continue
        if lowered in skip_exact:
            continue
        if lowered.startswith(("designed by", "powered by", "bug report", "github:", "publish:", "subject:", "authors:", "저자:", "주제:", "게시:")):
            continue
        if lowered.startswith(("제공하신", "제공된 원문", "의미 있는 내용을", "`paper_prompt.txt`", "paper_prompt.txt", "중국어 분석")):
            continue
        cleaned.append(raw_line)
    return "\n".join(cleaned)


def source_kind_to_node_type(source_kind: str, source_path: Optional[str]) -> ResearchNodeType:
    lowered = (source_kind or "").lower()
    path = (source_path or "").replace("\\", "/")
    path_lower = path.lower()
    # Path-precise matches win over the looser keyword fallbacks below: a daily
    # feed snippet must stay a SourceDocument even though the corpus root
    # contains the substring "papers".
    if _PAPER_SUBFOLDER_RE.search(path):
        return ResearchNodeType.PAPER
    if _PAPER_REPO_FILE_RE.search(path) or _DAILY_REPOS_RE.search(path):
        return ResearchNodeType.REPOSITORY
    if _DAILY_FEEDS_RE.search(path):
        return ResearchNodeType.SOURCE_DOCUMENT
    if "paper" in lowered or "/papers/" in path_lower or path_lower.endswith("paper.md") or "arxiv" in path_lower:
        return ResearchNodeType.PAPER
    if "repo" in lowered or "repo" in path_lower or "github" in path_lower:
        return ResearchNodeType.REPOSITORY
    return ResearchNodeType.SOURCE_DOCUMENT


def extract_arxiv_id_from_path(source_path: Optional[str]) -> Optional[str]:
    """Return the arxiv id from a daily-digest paper subfolder path, if any."""
    if not source_path:
        return None
    path = source_path.replace("\\", "/")
    match = _PAPER_SUBFOLDER_RE.search(path) or _PAPER_REPO_FILE_RE.search(path)
    if match:
        return match.group(1)
    return None


# Heading-classification helpers ---------------------------------------------

# Whitelist tokens that signal a heading is a real research concept rather
# than a paper title or section marker. Keep this list short and additive.
_CONCEPT_WHITELIST_TOKENS: Tuple[str, ...] = (
    "model",
    "diffusion",
    "splatting",
    "transformer",
    "graph",
    "rendering",
    "encoder",
    "decoder",
    "embedding",
    "attention",
    "reconstruction",
    "synthesis",
    "segmentation",
    "estimation",
    "depth",
    "slam",
    "convolution",
    "kernel",
    "loss",
    "regularization",
    "tokenization",
    "agent",
    "policy",
    "reward",
    "alignment",
)

_GENERIC_SECTION_NAMES: Set[str] = {
    "intro",
    "introduction",
    "summary",
    "abstract",
    "method",
    "methods",
    "results",
    "discussion",
    "conclusion",
    "conclusions",
    "references",
    "background",
    "related work",
    "experiments",
    "evaluation",
    "limitations",
    "appendix",
    "overview",
    "highlights",
    "본문",
    "개요",
    "요약",
    "결론",
    "참고",
    "실험",
    "한계",
    "방법",
}


def _strip_heading_numbering(heading: str) -> str:
    """Strip leading numbering ("1. ", "1) ", "I. ") and trailing whitespace."""
    text = re.sub(r"\s+", " ", heading.strip())
    # 1. , 1) , 12. , 12) — Arabic numbering
    text = re.sub(r"^\d{1,3}\s*[.)]\s+", "", text)
    # I. , II) , IV. — Roman numbering (simple form)
    text = re.sub(r"^[IVXLCM]{1,4}\s*[.)]\s+", "", text)
    return text.strip()


def _is_generic_section_heading(cleaned: str) -> bool:
    return cleaned.strip().lower().rstrip(":") in _GENERIC_SECTION_NAMES


def _looks_like_paper_title_heading(raw: str, cleaned: str) -> bool:
    """True if the heading looks like a paper title / digest entry, not a concept.

    Triggers on:
      - explicit numeric section prefix in the raw heading (``### 1. …``)
      - Korean sentence-ending punctuation (``다.``, ``.`` after Hangul)
      - too many commas / em-dashes (>5) — classic Korean digest prose form
    """
    raw_stripped = raw.strip()
    # Heading started with "### 1." style numbering — that is an enumerated
    # digest entry, never a concept.
    if re.match(r"^\d{1,3}\s*[.)]\s+", raw_stripped):
        return True
    # Korean conclusion clauses or trailing periods usually mark a sentence.
    if re.search(r"[가-힣]\.\s*$", cleaned):
        return True
    if cleaned.endswith("다.") or cleaned.endswith("이다") or cleaned.endswith("했다"):
        return True
    # Comma / em-dash density implies prose, not a single concept.
    punctuation = sum(cleaned.count(ch) for ch in (",", "—", "·"))
    if punctuation > 5:
        return True
    return False


def _is_concept_shaped_heading(cleaned: str, whitelist_terms: Set[str]) -> bool:
    """True iff ``cleaned`` is short enough and looks like a concept noun phrase.

    A heading qualifies as a Concept only if it is short (< 6 words),
    free of sentence-style punctuation, and either contains a whitelisted
    technical token or matches an existing TermRule canonical name/alias.
    """
    if not cleaned:
        return False
    if ":" in cleaned:
        return False
    # Reject anything with sentence-ending punctuation or too many commas.
    if cleaned.count(",") > 0:
        return False
    if re.search(r"[!?。]", cleaned):
        return False
    word_count = len(cleaned.split())
    if word_count == 0 or word_count > 5:
        return False
    lowered = cleaned.lower()
    # Direct match against term-rule whitelist (e.g. "Volumetric Rendering").
    if lowered in whitelist_terms:
        return True
    # Whitelist-token match — any concept-flavored noun.
    for token in _CONCEPT_WHITELIST_TOKENS:
        if re.search(rf"\b{re.escape(token)}\b", lowered):
            return True
    return False


def relation_for_node_type(node_type: ResearchNodeType) -> str:
    if node_type in {ResearchNodeType.TASK, ResearchNodeType.CAPABILITY, ResearchNodeType.PROBLEM_AREA, ResearchNodeType.RESEARCH_TOPIC}:
        return "addresses"
    if node_type in {ResearchNodeType.DATASET}:
        return "uses_dataset"
    if node_type in {ResearchNodeType.BENCHMARK}:
        return "evaluated_on"
    if node_type in {ResearchNodeType.METRIC}:
        return "uses_metric"
    if node_type in {ResearchNodeType.LIMITATION_CLAIM}:
        return "has_limitation"
    if node_type in {ResearchNodeType.APPROACH_FAMILY}:
        return "belongs_to_approach_family"
    return "uses"


def classify_claim_type(sentence: str) -> ResearchNodeType:
    lowered = sentence.lower()
    if any(marker in lowered for marker in ["outperform", "better", "improve", "성능", "우수", "달성"]):
        return ResearchNodeType.PERFORMANCE_CLAIM
    if any(marker in lowered for marker in ["문제", "limitation", "however", "그러나", "민감"]):
        return ResearchNodeType.LIMITATION_CLAIM
    if any(marker in lowered for marker in ["활용", "because", "통해", "by "]):
        return ResearchNodeType.CAUSAL_CLAIM
    return ResearchNodeType.CLAIM


def extract_title(text: str, source_path: Optional[str]) -> str:
    """Extract the human paper title, not scraper scaffolding headings.

    The papers.cool notes often start with ``# 논문 분석: <arxiv_id>`` and then
    ``## <arxiv_id>`` before the real title. Those are metadata headings, not the
    research artifact title.
    """
    metadata = extract_source_metadata(text, source_path)
    arxiv_id = str(metadata.get("arxiv_id", ""))
    candidates: List[str] = []
    for line in text.splitlines():
        stripped = line.strip().strip("# ").strip()
        if not stripped or stripped.startswith(">"):
            continue
        if stripped.startswith("논문 분석:"):
            continue
        if arxiv_id and stripped == arxiv_id:
            continue
        if re.fullmatch(r"\d+", stripped):
            continue
        if stripped in {"총계: 1", "Total: 1", "검색", "필터", "하이라이트", "내보내기", "저장"}:
            continue
        # papers.cool can render result headings as ``### #1 Title``. Keep the
        # title, not the rank marker. Do this before title validation so valid
        # headings like ``# WorldCompass: ...`` and ``### #1 FullCircle: ...``
        # both converge to the paper title.
        stripped = re.sub(r"^(?:#?\d+|#\d+)\s+(?=\S)", "", stripped).strip()
        if " | Cool Papers" in stripped:
            stripped = stripped.split(" | Cool Papers", 1)[0].strip()
        if stripped.endswith("  "):
            stripped = stripped.rstrip()
        if looks_like_research_title(stripped):
            candidates.append(stripped)
    if candidates:
        return candidates[0]
    if source_path:
        return Path(source_path).stem
    return "Untitled Source"


def looks_like_research_title(text: str) -> bool:
    if len(text) < 3 or len(text) > 220:
        return False
    lowered = text.lower()
    if any(skip in lowered for skip in ["designed by", "powered by", "github:", "disclaimer"]):
        return False
    if lowered.startswith((
        "extract ",
        "rt ",
        "tl;dr",
        "📄",
        "논문:",
        "관련 링크:",
        "본 연구",
        "제공하신",
        "제공된 원문",
        "`paper_prompt.txt`",
        "paper_prompt.txt",
        "의미 있는 내용을",
        "중국어 분석",
        "희소 뷰",
        "authors:",
        "저자:",
        "subject:",
        "publish:",
    )):
        return False
    if "[paper](" in lowered or "[논문 분석](" in lowered:
        return False
    return bool(re.search(r"[A-Za-z가-힣]", text))


def is_verified_paper_title(title: str, metadata: Dict[str, object]) -> bool:
    if not looks_like_research_title(title):
        return False
    arxiv_id = str(metadata.get("arxiv_id") or "")
    if title in {"paper", "main", "abstract"} or (arxiv_id and title == arxiv_id):
        return False
    return True


def extract_source_metadata(text: str, source_path: Optional[str]) -> Dict[str, object]:
    metadata: Dict[str, object] = {}
    arxiv_id = extract_arxiv_id_from_path(source_path)
    if not arxiv_id:
        arxiv_match = re.search(r"arxiv(?:\.org/abs/|:\s*)(\d{4}\.\d{4,6})", text, flags=re.IGNORECASE)
        if not arxiv_match and source_path:
            arxiv_match = re.search(r"(\d{4}\.\d{4,6})", source_path)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
    if arxiv_id:
        metadata["arxiv_id"] = arxiv_id
    date_match = re.search(r"분석일:\s*(\d{4}-\d{2}-\d{2})", text)
    if not date_match and source_path:
        date_match = re.search(r"daily/(\d{4}-\d{2}-\d{2})/", source_path)
    if date_match:
        metadata["analysis_date"] = date_match.group(1)
    return metadata


def infer_research_field(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["gaussian", "splatting", "novel view", "3d", "4d", "slam"]):
        return "3D/4D Vision and Reconstruction"
    if any(term in lowered for term in ["llm", "reasoning", "language model"]):
        return "LLM Reasoning"
    return "Research Literature"


def find_evidence(text: str, patterns: Iterable[str]) -> Optional[str]:
    lowered = text.lower()
    for pattern in patterns:
        if pattern.lower() in lowered:
            for sentence in split_sentences(text):
                if pattern.lower() in sentence.lower():
                    return sentence.strip()
            return pattern
    return None


def split_sentences(text: str) -> List[str]:
    cleaned = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return []
    # Korean/English mixed notes usually separate claims with periods.
    parts = re.split(r"(?<=[.!?。])\s+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def normalize_display_name(name: str) -> str:
    text = re.sub(r"\s+", " ", name.strip())
    if not text:
        return "Unnamed"
    # Preserve common all-caps acronyms; otherwise title-case only all-lower labels.
    if text.islower() and " " in text and re.fullmatch(r"[a-z0-9 ]+", text):
        return text.title()
    return text


def stable_id(node_type: str, name: str) -> str:
    digest = hashlib.sha1(f"{node_type}:{name.lower()}".encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:48] or "node"
    return f"{node_type}:{slug}:{digest}"


def truncate(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"
