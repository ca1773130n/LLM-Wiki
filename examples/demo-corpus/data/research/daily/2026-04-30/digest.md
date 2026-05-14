---
type: ResearchDigest
date: 2026-04-30
period: daily
papers_covered:
  - arxiv-2108-10869
  - arxiv-2112-12130
  - arxiv-2304-04278
  - arxiv-2304-14377
  - arxiv-2311-11700
  - arxiv-2312-06741
sub_topics: [Visual SLAM and MVS, 3D Gaussian Splatting]
---

# Daily digest — 2026-04-30

SLAM day. The thread I wanted to chase: how the neural-field representations
absorbed the SLAM pipeline, and what's still classical underneath.

[DROID-SLAM](../../papers/arxiv-2108-10869/paper.md) (Teed & Deng, 2021) is
the deep-learning end-to-end SLAM baseline. The trick is a recurrent update
operator that jointly refines depth and pose via a differentiable bundle
adjustment layer. The
[princeton-vl/DROID-SLAM](../../repos/princeton-vl-droid-slam/about.md)
release is still the cleanest "deep SLAM that actually runs in real time"
reference codebase. Notable that the underlying BA is conceptually the
same as in [DSO](../../papers/arxiv-1607-02565/paper.md) — what changed
is that the feature extractor and the update rule are now learned.

The neural-implicit SLAM line starts with
[NICE-SLAM](../../papers/arxiv-2112-12130/paper.md) (Zhu et al., 2021):
a hierarchical voxel grid of features, optimised online for both mapping
and tracking. [Point-SLAM](../../papers/arxiv-2304-04278/paper.md)
(Sandström et al., 2023) trades the grid for a neural point cloud —
adaptive resolution where the scene needs it. [Co-SLAM](../../papers/arxiv-2304-14377/paper.md)
(Wang et al., 2023) re-introduces a sparse parametric encoding for speed,
the same trade-off [Instant-NGP](../../papers/arxiv-2201-05989/paper.md)
made for offline NeRF.

The new arrivals are the Gaussian-Splatting SLAM systems.
[GS-SLAM](../../papers/arxiv-2311-11700/paper.md) (Yan et al., 2023) and
[Gaussian Splatting SLAM / MonoGS](../../papers/arxiv-2312-06741/paper.md)
(Matsuki et al., 2023) both swap the implicit volume for explicit 3D
Gaussians, retain the differentiable rasteriser from the
[base 3DGS paper](../../papers/arxiv-2308-04079/paper.md), and add online
keyframe management. MonoGS in particular reports the highest-quality
photometric reconstructions of any monocular SLAM system in the corpus.

The open question — what happens when the camera moves fast — is what I
want to write up next week. None of these systems benchmarks aggressively
on motion-blurred or fast-pan captures.

Six papers, ~55 min. Heavy day. Diffusion-based generation tomorrow.
