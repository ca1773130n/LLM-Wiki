---
type: ResearchDigest
date: 2026-04-25
period: daily
papers_covered:
  - arxiv-2308-04079
  - arxiv-2311-12775
  - arxiv-2403-17888
  - arxiv-2312-00109
  - arxiv-2312-02121
sub_topics: [3D Gaussian Splatting, Mesh and Surface Reconstruction]
---

# Daily digest — 2026-04-25

Gaussian Splatting day. The plan was: read the original paper, then read
its three most-cited follow-ons, then figure out where the surface story is.

The anchor is [3D Gaussian Splatting](../../papers/arxiv-2308-04079/paper.md)
(Kerbl et al., 2023). Compared to
[Instant-NGP](../../papers/arxiv-2201-05989/paper.md), splatting trades
implicit-volume ray marching for explicit anisotropic primitives rasterised
front-to-back. The headline number — real-time at training-time quality on
Mip-NeRF 360 — is what reshaped the field. The
[graphdeco-inria/gaussian-splatting](../../repos/graphdeco-inria-gaussian-splatting/about.md)
reference is non-commercial, which has been awkward for downstream products;
the [nerfstudio-project/gsplat](../../repos/nerfstudio-project-gsplat/about.md)
Apache-2.0 reimplementation is what almost everyone is actually running.
The [gsplat math supplement](../../papers/arxiv-2312-02121/paper.md) is
worth reading alongside the original paper — the projection math is more
subtle than the rasteriser code makes it look.

[SuGaR](../../papers/arxiv-2311-12775/paper.md) (Guédon et al., 2023) is
the surface story for splatting: regularise Gaussians toward a manifold,
then extract a mesh via Poisson reconstruction on the resulting near-surface
distribution. It's the closest splatting analogue to
[NeuS](../../papers/arxiv-2106-10689/paper.md), and the comparison is
worth doing — SuGaR is faster but more capture-sensitive.

[2D Gaussian Splatting](../../papers/arxiv-2403-17888/paper.md) (Huang et al.,
2024) collapses each primitive to a view-consistent oriented disk. The
geometry is cleaner because the depth ambiguity inherent in volumetric
3D Gaussians goes away — at a small cost in view-synthesis fidelity. The
right move when you actually want a mesh.

[Scaffold-GS](../../papers/arxiv-2312-00109/paper.md) (Lu et al., 2023)
replaces the "free Gaussian soup" with anchor points that emit
view-conditioned offsets, which prunes redundant primitives in low-frequency
regions. Worth contrasting with the densification revisit later this week.

Five papers, ~50 min. Tomorrow I want to see what happens when you push
splatting into SLAM territory.
