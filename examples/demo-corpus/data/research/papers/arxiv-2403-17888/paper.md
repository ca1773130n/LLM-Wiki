---
type: Paper
arxiv: "2403.17888"
arxiv_url: https://arxiv.org/abs/2403.17888
title: "2D Gaussian Splatting for Geometrically Accurate Radiance Fields"
authors:
  - "Binbin Huang"
  - "Zehao Yu"
  - "Anpei Chen"
  - "Andreas Geiger"
  - "Shenghua Gao"
date: 2024-03-26
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, RadianceField, NovelViewSynthesis, RealTimeRendering]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: hbb1/2d-gaussian-splatting
license: "CC-BY-4.0 (Tesserae demo prose)"
---

# 2D Gaussian Splatting for Geometrically Accurate Radiance Fields

Huang et al. observe that 3D GaussianSplatting (3DGS), while excellent for
NovelViewSynthesis, is a poor representation when accurate geometry is
required. Each 3D Gaussian is a volumetric primitive: its silhouette
changes shape from one camera angle to another, so the surface inferred
from a 3DGS field is not view-consistent. The authors propose 2D Gaussian
Splatting (2DGS), which collapses each 3D volumetric primitive to a flat,
oriented Gaussian disk in 3D space, intrinsically representing a tangent
plane to the underlying surface.

A 2D disk has a single normal and a well-defined location in 3D, which
makes the geometry it represents view-consistent: every camera sees the
same plane. Recovering radiance from a set of such disks requires a
perspective-correct splatting process, derived through explicit ray-splat
intersection rather than the screen-space affine approximation that 3DGS
uses. The authors implement this perspective-correct rasterisation
efficiently on the GPU so that the runtime cost remains close to that of
3DGS.

Two regularisers strengthen the geometric output further: a depth
distortion term encourages the depth distribution along each ray to be
sharply peaked on a single disk, and a normal consistency term encourages
the disks' normals to agree with the gradient of the rendered depth map.
Together these produce noise-free meshes and clean surface normals that
are competitive with NeuralImplicitSurface methods, while retaining 3DGS-
style training speed and real-time rendering. 2DGS sits alongside SuGaR as
one of the two main lines of work bridging the gap between fast
Gaussian-based radiance fields and accurate geometry, and the released
code has become a common baseline for surface-aware Gaussian methods.
