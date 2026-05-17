---
type: Paper
arxiv: "2209.14988"
arxiv_url: https://arxiv.org/abs/2209.14988
title: "DreamFusion: Text-to-3D using 2D Diffusion"
authors:
  - "Ben Poole"
  - "Ajay Jain"
  - "Jonathan T. Barron"
  - "Ben Mildenhall"
date: 2022-09-29
sub_topic: Diffusion-based 3D Generation
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [RadianceField, Diffusion, TextTo3D]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: ashawkey/stable-dreamfusion
---

# DreamFusion: Text-to-3D using 2D Diffusion

Poole et al. propose DreamFusion, the first method to generate 3D
content from natural-language prompts using only a pretrained 2D
text-to-image diffusion model — no 3D training data, no modifications
to the diffusion model itself. The result reframes text-to-3D from a
data problem (which has no large-scale ground-truth corpus) to an
optimization problem against an existing image prior.

The core technical contribution is Score Distillation Sampling (SDS).
Given a text prompt, the method initializes a Neural Radiance Field
(Mildenhall et al., 2020) with random weights and iteratively refines
it as follows: at each step, a random camera is sampled, the NeRF is
rendered to produce a 2D image, the image is noised with a Gaussian
perturbation, and the diffusion model's predicted denoising direction
is treated as a gradient signal that pushes the rendered image toward
"things the diffusion model considers likely under this prompt." Unlike
sampling from the diffusion model, SDS skips the score-Jacobian term,
yielding a stable per-step update that can be backpropagated through
the differentiable NeRF renderer.

The resulting 3D representation is view-consistent because every
training step renders a different camera, all of them constrained
toward the same prompt-conditioned image distribution. The output NeRF
can be relit, composited, or further edited; the authors demonstrate a
broad range of generations including animals, objects, and stylized
scenes.

DreamFusion seeded the entire text-to-3D literature represented in this
corpus by Magic3D (Lin et al., 2022), Fantasia3D, ProlificDreamer, and
the single-image methods such as Zero-1-to-3 (Liu et al., 2023). SDS
itself has been refined into Variational SDS and other low-variance
estimators, but the core idea — use a 2D image prior to supervise 3D
optimization — remains the foundational primitive for diffusion-based
3D generation.
