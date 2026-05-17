---
type: Paper
arxiv: "2311.11700"
arxiv_url: https://arxiv.org/abs/2311.11700
title: "GS-SLAM: Dense Visual SLAM with 3D Gaussian Splatting"
authors:
  - "Chi Yan"
  - "Delin Qu"
  - "Dan Xu"
  - "Bin Zhao"
  - "Zhigang Wang"
  - "Dong Wang"
  - "Xuelong Li"
date: 2023-11-20
sub_topic: Visual SLAM and MVS
methods: [GaussianSplatting, NeuralImplicitSurface, SLAM, RealTimeRendering]
datasets: [Replica, TUM-RGBD]
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (Tesserae demo prose)"
---

# GS-SLAM: Dense Visual SLAM with 3D Gaussian Splatting

Yan et al. present GS-SLAM, one of the first systems to adopt 3D
GaussianSplatting as the underlying scene representation for dense RGB-D
SLAM. Earlier neural SLAM methods, such as Point-SLAM and Co-SLAM, rely on
implicit features anchored in points or hash grids and reconstruct geometry
via NeuralImplicitSurface rendering. Those representations couple ray
sampling to MLP queries and impose a substantial cost per pixel, which
limits incremental update rates. GS-SLAM instead uses Gaussians and a
differentiable splatting rasteriser, exploiting the same speed advantage
that 3DGS brings to offline reconstruction.

The system runs a two-track loop. Tracking estimates the new camera pose
by minimising a photometric-and-depth re-rendering loss against the current
Gaussian map. A coarse-to-fine selection of reliable Gaussians focuses pose
optimisation on confidently observed regions, suppressing the influence of
recently spawned or noisy primitives. Mapping, in turn, runs an adaptive
expansion strategy that adds new Gaussians where the current map fails to
explain incoming pixels and prunes Gaussians that drift away from the
surface. This combination is essential for extending 3DGS — originally a
batch reconstruction method — to incremental, scene-scale capture.

A practical advantage of the explicit primitive is that the system can
visualise the current map at any time without an extra rendering pass
through a separate decoder, which simplifies debugging and live
monitoring of large captures. On Replica and TUM-RGBD, GS-SLAM achieves
competitive tracking accuracy and
state-of-the-art rendering quality among RealTimeRendering SLAM methods. It
is contemporary with Gaussian Splatting SLAM by Matsuki et al., which
tackles the harder monocular setting; together the two papers established
explicit Gaussian primitives as a serious option for live dense SLAM and
seeded a follow-on literature on Gaussian-based incremental reconstruction.
