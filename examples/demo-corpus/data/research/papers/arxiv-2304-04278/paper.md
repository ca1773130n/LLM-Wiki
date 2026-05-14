---
type: Paper
arxiv: "2304.04278"
arxiv_url: https://arxiv.org/abs/2304.04278
title: "Point-SLAM: Dense Neural Point Cloud-based SLAM"
authors:
  - "Erik Sandström"
  - "Yue Li"
  - "Luc Van Gool"
  - "Martin R. Oswald"
date: 2023-04-09
sub_topic: Visual SLAM and MVS
methods: [SLAM, PointCloud]
datasets: [ScanNet, Replica, TUM-RGBD]
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# Point-SLAM: Dense Neural Point Cloud-based SLAM

Sandström and colleagues present a dense neural SLAM system that anchors the
features of a neural scene representation in a PointCloud rather than the
sparse voxel or hash grids favoured by contemporaneous neural SLAM work. The
point set is grown incrementally as new RGBD frames arrive, with anchor
density adapted to the local information density of the input — flat walls
receive few points, while textured or geometrically complex regions are
densified.

Both the mapping and tracking stages share the same point-based field. The
authors minimise an RGBD-based re-rendering loss that compares synthesised
colour and depth against the incoming sensor stream; the same loss drives
gradient updates to the per-point feature vectors and to the current camera
pose. Because anchors are sparse where they need to be sparse, the system
spends less compute on empty space than grid-bound competitors and is able
to allocate finer detail near surfaces.

Experiments on Replica, TUM-RGBD, and ScanNet report tracking accuracy and
rendering quality (PSNR, SSIM, LPIPS) on par with or better than prior dense
neural SLAM methods. The data-driven anchor placement also reduces memory
relative to fixed-resolution grid encodings such as those used by iMAP and
NICE-SLAM, making the approach a useful reference point for later
GaussianSplatting-based SLAM efforts (Gaussian Splatting SLAM, GS-SLAM)
that retain the explicit-primitive philosophy but swap point anchors for
anisotropic Gaussian primitives. A reliability check on new candidate
points prevents the cloud from absorbing every transient observation,
keeping the active point set bounded even under repeated revisits, which
is one of the more practical contributions of the work to incremental
neural mapping. Source code is released and the design remains a common
citation for input-adaptive neural map representations in real-time SLAM.
