---
type: Paper
arxiv: "2309.16653"
arxiv_url: https://arxiv.org/abs/2309.16653
title: "DreamGaussian: Generative Gaussian Splatting for Efficient 3D Content Creation"
authors:
  - "Jiaxiang Tang"
  - "Jiawei Ren"
  - "Hang Zhou"
  - "Ziwei Liu"
  - "Gang Zeng"
date: 2023-09-28
sub_topic: Diffusion-based 3D Generation
methods: [GaussianSplatting, RadianceField, Diffusion, ScoreDistillation]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: dreamgaussian/dreamgaussian
license: "CC-BY-4.0 (Tesserae demo prose)"
---

# DreamGaussian: Generative Gaussian Splatting for Efficient 3D Content Creation

Tang et al. show that swapping the implicit RadianceField backbone of
ScoreDistillation-based 3D generation for an explicit GaussianSplatting
representation produces a dramatic speed-up without sacrificing fidelity.
Earlier optimisation-based methods such as DreamFusion and Magic123 spend
most of their time querying a NeRF MLP across many sampled points per ray;
DreamGaussian instead distils the Diffusion prior directly into a growing
set of 3D Gaussians, exploiting the fact that explicit primitives can be
densified, pruned, and rendered far more cheaply than implicit volumes.

The pipeline has two stages. In the first, a set of 3D Gaussians is
initialised sparsely and grown by progressive densification while a 2D
diffusion prior supplies novel-view score gradients via SDS. The authors
observe that, unlike NeRF where empty-space pruning is expensive, Gaussian
densification naturally biases capacity toward populated regions, which
converges in a fraction of the iterations needed for implicit fields. The
second stage converts the Gaussian set into a textured mesh by exporting
geometry through a Marching-Cubes-style step and refining the UV-space
texture against the diffusion prior, yielding an asset compatible with
standard graphics pipelines.

End to end, DreamGaussian produces a textured mesh from a single image in
roughly two minutes, about an order of magnitude faster than implicit
SDS-based methods of the period. The paper helped establish 3DGS as a
serious backbone for generative 3D and motivated later feed-forward
Gaussian-based generators such as AGG, LGM, and Instant3D, which trade
the per-instance optimisation loop for a learned amortised mapping.
