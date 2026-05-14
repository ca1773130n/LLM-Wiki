---
type: Paper
arxiv: "2310.08528"
arxiv_url: https://arxiv.org/abs/2310.08528
title: "4D Gaussian Splatting for Real-Time Dynamic Scene Rendering"
authors:
  - "Guanjun Wu"
  - "Taoran Yi"
  - "Jiemin Fang"
  - "Lingxi Xie"
  - "Xiaopeng Zhang"
  - "Wei Wei"
  - "Wenyu Liu"
  - "Qi Tian"
  - "Xinggang Wang"
date: 2023-10-12
sub_topic: Dynamic and 4D Reconstruction
methods: [GaussianSplatting, RealTimeRendering]
datasets: []
metrics: [FPS]
oss_repo: hustvl/4DGaussians
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# 4D Gaussian Splatting for Real-Time Dynamic Scene Rendering

Wu et al. extend 3D GaussianSplatting to time-varying scenes with 4D-GS, a
representation that pairs a canonical set of 3D Gaussians with a compact
spatio-temporal field that deforms them at each timestamp. A per-frame
3DGS would be wasteful — most of a typical video is locally static — so the
authors instead share Gaussians across time and predict deformations
conditioned on the temporal coordinate.

The deformation field is implemented as a decomposed neural voxel grid in
the style of HexPlane: three orthogonal planar projections and a small set
of feature planes encode the 4D function efficiently. Features fetched from
the grid are decoded by a lightweight MLP into per-Gaussian deformations of
position, rotation, and scale. Because the canonical Gaussians remain shared
and the deformation network is small, optimisation is tractable and the
runtime cost at rendering remains close to that of static 3DGS.

On dynamic scene benchmarks the method achieves competitive or better
reconstruction quality than prior dynamic NeRFs while sustaining 82 FPS at
800×800 on an RTX 3090 — a regime where ray-marched dynamic NeRFs cannot
operate. 4D-GS sits in a family of dynamic Gaussian methods that includes
4D-Rotor Gaussian Splatting, which represents motion through anisotropic
4D XYZT Gaussians sliced at each timestamp rather than through a separate
deformation MLP. Both lines of work establish that explicit primitives are a
viable substrate for RealTimeRendering of dynamic radiance fields, and the
released code remains a common reference implementation. Storage cost
benefits as well: because the canonical Gaussians are shared across all
frames, the per-scene memory footprint scales roughly with the size of
the deformation grid rather than linearly with sequence length, making
the method tractable on consumer GPUs even for multi-second captures.
