---
type: Paper
arxiv: "2002.10099"
arxiv_url: https://arxiv.org/abs/2002.10099
title: "Implicit Geometric Regularization for Learning Shapes"
authors:
  - "Amos Gropp"
  - "Lior Yariv"
  - "Niv Haim"
  - "Matan Atzmon"
  - "Yaron Lipman"
date: 2020-02-24
sub_topic: Mesh and Surface Reconstruction
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [PointCloud]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# Implicit Geometric Regularization for Learning Shapes

Gropp et al. propose Implicit Geometric Regularization (IGR), a training
objective for fitting neural signed distance functions directly to raw
point clouds without supervised ground-truth occupancy. The loss has two
terms: a zero-set term encouraging the network to vanish on input points
(optionally with surface normals), and an Eikonal regularizer encouraging
the gradient of the network to have unit norm everywhere in the ambient
space.

The Eikonal term is the methodological core. Because the loss is non-zero
almost everywhere in space, the optimizer cannot collapse to the
degenerate solution where the network is zero outside the support of the
point cloud. The authors prove, in the linear regime, that the regularizer
biases the network toward smooth zero level sets — the kind of clean,
manifold surfaces practitioners want — rather than the noisy, fragmented
implicit surfaces produced by direct chamfer-style fitting.

Empirically, IGR recovers high-fidelity surfaces from sparse oriented
points and unoriented points alike, outperforming DeepSDF-style methods
that require pre-computed ground-truth SDF samples and Occupancy Networks
that need explicit inside/outside labels. The method became a building
block for IDR, NeuS, VolSDF, and MonoSDF: any neural-implicit-surface
method that backs a radiance field with an SDF inherits IGR's Eikonal
regularizer to keep the distance field well-behaved.

The contribution is a clear example of how a carefully chosen
regularization term, applied to coordinate-based networks, can replace
expensive pre-processing pipelines that produce explicit supervision.
Within the 3D reconstruction corpus this paper is the bridge between
classical level-set methods and the volume-rendering era surface
reconstruction lineage led by NeuS and VolSDF.
