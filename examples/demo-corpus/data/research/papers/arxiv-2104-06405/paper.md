---
type: Paper
arxiv: "2104.06405"
arxiv_url: https://arxiv.org/abs/2104.06405
title: "BARF: Bundle-Adjusting Neural Radiance Fields"
authors:
  - "Chen-Hsuan Lin"
  - "Wei-Chiu Ma"
  - "Antonio Torralba"
  - "Simon Lucey"
date: 2021-04-13
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [RadianceField, SLAM, BundleAdjustment, NovelViewSynthesis]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# BARF: Bundle-Adjusting Neural Radiance Fields

Lin et al. attack a practical limitation of NeRF (Mildenhall et al.,
2020): it assumes accurate camera poses from an upstream
structure-from-motion pipeline such as COLMAP. BARF removes this
requirement by jointly optimizing scene representation and camera poses
within the same gradient-descent loop, framing the problem as a
synthesis-based bundle adjustment.

The authors first establish a theoretical link to classical image
alignment: synthesizing a NeRF pixel and matching it to an observation
is, up to first order, an alignment problem on the photometric residual,
and is therefore subject to the same coarse-to-fine wisdom that has made
Lucas-Kanade alignment robust for decades. They show that NeRF's
high-frequency sinusoidal positional encoding interferes with this
process — the gradient landscape with respect to camera pose becomes
spiky and bundle adjustment falls into local minima.

The proposed fix is a coarse-to-fine annealing schedule on the
positional-encoding frequencies: the high-frequency bands of the encoding
are masked out early in training and progressively re-enabled. The
low-frequency NeRF gives smooth pose-gradients, the optimizer finds the
correct camera registration globally, and then the high-frequency
content is reintroduced to capture fine detail. The same trick had
appeared concurrently in Nerfies (Park et al., 2020) for deformation
fields; BARF applies it to extrinsic pose.

Experiments on synthetic Blender scenes and real forward-facing scenes
show that BARF recovers reasonable poses and reconstructions even from
heavily perturbed or completely uninitialized cameras, enabling pose-free
NeRF training. The result connects the radiance-field literature to
visual SLAM and dense reconstruction, and is a regular reference for
subsequent pose-refining NeRF and Gaussian-splatting systems.
