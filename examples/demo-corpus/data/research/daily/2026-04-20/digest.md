---
type: ResearchDigest
date: 2026-04-20
period: daily
papers_covered:
  - arxiv-2002-10099
  - arxiv-2104-10078
  - arxiv-2106-10689
  - arxiv-2106-12052
  - arxiv-2206-00665
  - arxiv-2104-06405
sub_topics: [Mesh and Surface Reconstruction, Neural Radiance Fields]
---

# Daily digest — 2026-04-20

Surfaces day. Radiance fields are excellent at view synthesis and bad at
giving you a mesh; the surface-reconstruction line is the field's answer.

[Implicit Geometric Regularization](../../papers/arxiv-2002-10099/paper.md)
(Gropp et al., 2020) is the unsexy prerequisite: a loss that encourages a
learned implicit function to behave like a signed distance function, via an
Eikonal term on its gradients. Almost every later SDF-based paper in this
corpus cites it as the regulariser that made unconstrained shape learning
stable.

The 2021 surface trilogy is where it gets interesting.
[UNISURF](../../papers/arxiv-2104-10078/paper.md) (Oechsle et al.) was first
out: unify implicit surfaces and radiance fields by replacing density with
an occupancy function. Then [NeuS](../../papers/arxiv-2106-10689/paper.md)
(Wang et al.) and [VolSDF](../../papers/arxiv-2106-12052/paper.md) (Yariv
et al.) — published days apart — both argued that occupancy biases the
surface estimate and proposed unbiased SDF-to-density conversions. NeuS's
derivation is the cleaner read. The [Totoro97/NeuS](../../repos/totoro97-neus/about.md)
implementation has become the de-facto baseline in the surface-reconstruction
benchmarks.

[MonoSDF](../../papers/arxiv-2206-00665/paper.md) (Yu et al., 2022) is the
practical follow-on: feed an off-the-shelf monocular depth and normal
predictor into the surface optimiser as additional cues, so the SDF
training converges with far fewer views and on indoor scenes where the
purely-multi-view methods struggle.

The detour was [BARF](../../papers/arxiv-2104-06405/paper.md) (Lin et al.,
2021) on bundle-adjusting NeRF — optimising camera poses jointly with the
field via a coarse-to-fine positional encoding schedule. Not strictly a
surface paper, but it answers the "what if SfM poses are bad?" question
that every surface method ducks. Same trick reappears in the SLAM literature
later.

Six papers, ~50 min. The surface line and the splatting line are about to
collide; that's next week's reading.
