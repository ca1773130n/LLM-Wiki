# Research Graph Extraction Prompt

Use this prompt with Claude/Cognee extraction. The deterministic `llm_wiki.research_graph` module is the schema authority.

You are extracting a literature intelligence graph for a user's research field.
Do **not** create arbitrary node types. Every node type MUST be one of:

- ResearchField, ResearchTopic, ProblemArea, ApproachFamily, Trend
- SourceDocument, Paper, Repository, Project, Model, Dataset, Benchmark, Metric, Result, Organization, Person
- Concept, TechnicalTerm, MathematicalConcept, MethodologicalConcept, Algorithm, ObjectiveFunction, ArchitecturePattern, TrainingParadigm, InferenceStrategy, EvaluationProtocol, Task, Capability
- Claim, ContributionClaim, PerformanceClaim, ComparisonClaim, LimitationClaim, CausalClaim, OpenQuestion, EvidenceSpan

Never use generic types like `Entity`, `software`, `technique`, `domain`, `topic`, `technology`, `feature`.
Map them instead:

- software -> Repository / Project / Tool-like Project / ArchitecturePattern
- technique -> MethodologicalConcept / Algorithm / InferenceStrategy / TrainingParadigm
- domain -> ResearchField / ResearchTopic / ProblemArea / Task
- feature -> Capability
- topic -> ResearchTopic / Concept

Every factual claim must be represented as a Claim subtype and grounded with an EvidenceSpan.
Papers and repositories are sources/artifacts; concepts/methods/tasks/benchmarks are reusable canonical nodes.

Prefer relations from this set only:

is_a, part_of, subfield_of, introduces, uses, extends, improves_on, compares_against, criticizes, addresses, optimizes_for, uses_dataset, evaluated_on, uses_metric, reports_result, achieves_score, belongs_to_approach_family, shares_concept_with, derived_from, supports_claim, contradicts_claim, attributes_improvement_to, has_limitation, evidenced_by, mentioned_in, authored_by, released_by, implemented_in, rising_in, declining_in, emerged_after.

Extraction priorities:

1. Identify the Paper/Repository/SourceDocument.
2. Extract reusable concepts, mathematical concepts, methods, algorithms, tasks, datasets, benchmarks, metrics.
3. Extract contribution/performance/comparison/limitation/causal claims.
4. Ground each claim in an EvidenceSpan copied from the source.
5. Assign candidate ApproachFamily nodes only when the paper clearly shares a method pattern with other papers.
6. Avoid over-extraction: do not create nodes for generic adjectives or one-off phrases unless they are reusable research concepts.
