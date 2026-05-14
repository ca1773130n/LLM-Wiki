---
type: Paper
arxiv: "2308.04079"
arxiv_url: https://arxiv.org/abs/2308.04079
title: "3D Gaussian Splatting for Real-Time Radiance Field Rendering"
authors:
  - "Bernhard Kerbl"
  - "Georgios Kopanas"
  - "Thomas Leimkühler"
  - "George Drettakis"
date: 2023-08-08
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, RadianceField, NovelViewSynthesis, RealTimeRendering]
datasets: []
metrics: [FPS]
oss_repo: graphdeco-inria/gaussian-splatting
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# 3D Gaussian Splatting for Real-Time Radiance Field Rendering

Kerbl et al. introduce 3D GaussianSplatting, a primitive-based representation
for novel-view synthesis that recovers a scene as a collection of anisotropic
3D Gaussians and renders them by differentiable rasterisation. Each Gaussian
carries a position, a full 3×3 covariance, an opacity, and a view-dependent
colour encoded as spherical harmonics. Compared to NeRF-style methods that
ray-march through an implicit volume, splatting factorises the rendering
equation into a tile-based, front-to-back sort of projected Gaussians,
sidestepping costly sampling along empty regions of the ray.

Three design choices make the representation practical at 1080p in real time.
First, the optimisation is seeded from the sparse PointCloud produced by a
standard StructureFromMotion pass, anchoring the Gaussians near the true
surface from the outset. Second, an interleaved densification and pruning
schedule clones, splits, and removes primitives during training, with
anisotropic covariance adapting each Gaussian to local geometry. Third, the
authors implement a fast visibility-aware tile rasteriser whose backward
pass is closed-form and GPU-friendly, accelerating both training and
inference.

The pipeline reaches state-of-the-art quality on standard benchmarks while
sustaining >= 30 FPS rendering at 1080p on unbounded scenes — a regime where
prior RadianceField methods had to compromise. The paper triggered a wave of
follow-on work: SuGaR aligns Gaussians to surfaces for mesh extraction,
2D Gaussian Splatting collapses primitives to view-consistent disks for
better geometry, Scaffold-GS replaces a free Gaussian soup with anchor-based
structure, and Gaussian Splatting SLAM extends the representation to live
camera tracking. Together with the open INRIA reference implementation, the
paper has become the de-facto baseline for explicit-primitive
NovelViewSynthesis.
