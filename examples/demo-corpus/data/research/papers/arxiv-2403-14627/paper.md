---
type: Paper
arxiv: "2403.14627"
arxiv_url: https://arxiv.org/abs/2403.14627
title: "MVSplat: Efficient 3D Gaussian Splatting from Sparse Multi-View Images"
authors:
  - "Yuedong Chen"
  - "Haofei Xu"
  - "Chuanxia Zheng"
  - "Bohan Zhuang"
  - "Marc Pollefeys"
  - "Andreas Geiger"
  - "Tat-Jen Cham"
  - "Jianfei Cai"
date: 2024-03-21
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, FeedForward]
datasets: []
metrics: [FPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# MVSplat: Efficient 3D Gaussian Splatting from Sparse Multi-View Images

Chen et al. propose MVSplat, a FeedForward model that predicts 3D
GaussianSplatting parameters from a small set of input views in a single
network pass. The contribution that distinguishes MVSplat from
contemporaneous Gaussian predictors such as pixelSplat is its explicit use
of classical multi-view geometry as an inductive bias: the network builds a
plane-sweep cost volume that captures cross-view feature similarities and
uses those similarities, rather than learned attention alone, to localise
the centres of the predicted Gaussians.

The cost volume aggregates features across reference views at a discrete
set of depth hypotheses, with cross-view similarity scoring each
hypothesis at every reference pixel. This provides a strong geometric
prior on where Gaussians should be placed and, in the authors' analysis,
is the key reason the network generalises well across scenes and
datasets despite training only on photometric supervision. The remaining
Gaussian primitive parameters — opacity, anisotropic covariance, and
spherical-harmonic colour — are predicted jointly with the centres,
sharing intermediate features so that geometry and appearance estimates
are consistent.

On RealEstate10K and ACID, MVSplat matches or surpasses pixelSplat in
appearance and geometry quality while using roughly ten times fewer
parameters and inferring more than twice as fast, reaching 22 FPS at
benchmark resolution. Cross-dataset evaluations confirm stronger
generalisation than pixelSplat. The work has become a reference point for
the family of feed-forward Gaussian predictors that includes AGG, LGM, and
latentSplat, and is often cited for the observation that a small classical
geometry prior — a cost volume from plane sweeping — is worth a large
amount of model capacity and training data.
