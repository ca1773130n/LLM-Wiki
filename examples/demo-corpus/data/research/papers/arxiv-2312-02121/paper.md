---
type: Paper
arxiv: "2312.02121"
arxiv_url: https://arxiv.org/abs/2312.02121
title: "Mathematical Supplement for the gsplat Library"
authors:
  - "Vickie Ye"
  - "Angjoo Kanazawa"
date: 2023-12-04
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: nerfstudio-project/gsplat
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# Mathematical Supplement for the gsplat Library

Ye and Kanazawa publish a self-contained mathematical reference for gsplat,
the modular differentiable GaussianSplatting library hosted by the
nerfstudio project. The original 3DGS paper by Kerbl et al. introduces the
representation and the high-level rendering pipeline, but it does not
spell out every term of the forward and backward passes at the level of
detail needed for reimplementation or extension. gsplat's supplement fills
that gap.

The note walks through projection of 3D Gaussians into screen space under
a pinhole camera, including the local affine approximation of the
perspective transform and the propagation of covariance through it. It
covers tile-based rasterisation, front-to-back alpha compositing, and the
exact gradient flow back through opacity, colour, position, scale, and
rotation. Spherical-harmonic colour evaluation and its gradients are
documented alongside the choices of basis convention used by the library.
The text is intentionally implementation-aligned: each section maps to a
specific kernel or Python entry point in the library, so a reader can move
between equations and code without ambiguity.

The accompanying Python API exposes each component of the forward and
backward passes individually, making gsplat a common substrate for
research extensions of 3DGS — for example, surface-aware variants such as
SuGaR or 2D Gaussian Splatting, dynamic methods such as 4D Gaussian
Splatting, and SLAM systems such as Gaussian Splatting SLAM and GS-SLAM
have all reused or imitated gsplat's rasteriser interface. As a result,
the supplement is short but functions as the canonical low-level reference
for the GaussianSplatting ecosystem.
