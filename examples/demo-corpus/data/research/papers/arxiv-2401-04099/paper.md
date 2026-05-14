---
type: Paper
arxiv: "2401.04099"
arxiv_url: https://arxiv.org/abs/2401.04099
title: "AGG: Amortized Generative 3D Gaussians for Single Image to 3D"
authors:
  - "Dejia Xu"
  - "Ye Yuan"
  - "Morteza Mardani"
  - "Sifei Liu"
  - "Jiaming Song"
  - "Zhangyang Wang"
  - "Arash Vahdat"
date: 2024-01-08
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, ImageTo3D]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# AGG: Amortized Generative 3D Gaussians for Single Image to 3D

Xu et al. propose AGG, an amortised ImageTo3D model that produces a 3D
GaussianSplatting representation from a single input image in a single
forward pass. Existing Gaussian-based 3D generators of the period — for
example DreamGaussian — relied on optimisation-based pipelines built
around ScoreDistillation, paying a per-instance compute cost on the order
of minutes. AGG eliminates this loop by training a neural network that
maps directly from an image to the parameters of a Gaussian set.

The architecture decomposes the generation problem along two axes. First,
AGG separates the prediction of Gaussian locations from the prediction of
the remaining appearance attributes (opacity, colour via spherical
harmonics, scale, rotation) and lets the two streams interact through a
hybrid intermediate representation. This decomposition stabilises
optimisation, since locating primitives near the true surface is a much
better-conditioned problem than jointly predicting all attributes at
once. Second, the pipeline is cascaded across resolution: a coarse 3D
Gaussian representation is produced first, and a downstream 3D Gaussian
super-resolution module then upsamples primitive count and refines local
detail.

In comparisons against optimisation-based Gaussian generators and against
amortised models built on alternative 3D representations such as NeRF, AGG
produces competitive quality while running several orders of magnitude
faster — the per-image generation cost drops from minutes to a fraction
of a second. AGG sits in a broader family of feed-forward Gaussian
predictors that includes LGM, MVSplat, and pixelSplat; together they
trace an arc from per-prompt optimisation toward learned amortised
inference for 3D content creation.
