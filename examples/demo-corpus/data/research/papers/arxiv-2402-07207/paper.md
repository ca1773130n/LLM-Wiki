---
type: Paper
arxiv: "2402.07207"
arxiv_url: https://arxiv.org/abs/2402.07207
title: "GALA3D: Towards Text-to-3D Complex Scene Generation via Layout-guided Generative Gaussian Splatting"
authors:
  - "Xiaoyu Zhou"
  - "Xingjian Ran"
  - "Yajiao Xiong"
  - "Jinlin He"
  - "Zhiwei Lin"
  - "Yongtao Wang"
  - "Deqing Sun"
  - "Ming-Hsuan Yang"
date: 2024-02-11
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, TextTo3D]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# GALA3D: Towards Text-to-3D Complex Scene Generation via Layout-guided Generative Gaussian Splatting

Zhou et al. introduce GALA3D, a compositional TextTo3D pipeline that
targets multi-object scenes rather than the single-object outputs typical
of DreamFusion-era generators. The motivating observation is that most
SDS-based pipelines collapse when asked to generate scenes with several
distinct entities, because a single monolithic 3D field cannot easily
enforce separation, scale, and interaction constraints between objects
referred to in the prompt.

The pipeline begins by querying a large language model to translate a
free-form scene description into an explicit layout: a list of named
objects with approximate bounding boxes and qualitative relationships.
This LLM-generated layout serves as the prior for a layout-guided
GaussianSplatting representation, where Gaussians are organised into
per-object groups and the optimisation is constrained by per-object
geometric priors derived from the bounding boxes. Each object can be
optimised semi-independently while still influencing its neighbours
through the global rendering loss.

An instance-scene compositional optimisation mechanism, driven by a
conditioned diffusion prior, then refines the scene jointly. This stage
not only sharpens textures and shapes but also adjusts the initial
coarse layout that came from the LLM, so that scale, contact, and
relative positions become physically and semantically plausible. The
result is a compositional pipeline that supports both high-quality
scene-level generation and per-object controllable editing: the user can
move, resize, or swap objects in the layout and re-optimise. GALA3D is
a contemporary of LucidDreamer in the open-domain scene generation
literature; the two papers differ mainly in whether scene structure
comes from an inpainting-driven point cloud or from an LLM-emitted
layout.
