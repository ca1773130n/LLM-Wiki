---
type: Paper
arxiv: "2104.10078"
arxiv_url: https://arxiv.org/abs/2104.10078
title: "UNISURF: Unifying Neural Implicit Surfaces and Radiance Fields for Multi-View Reconstruction"
authors:
  - "Michael Oechsle"
  - "Songyou Peng"
  - "Andreas Geiger"
date: 2021-04-20
sub_topic: Mesh and Surface Reconstruction
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [RadianceField, VolumeRendering, NeuralImplicitSurface, NovelViewSynthesis]
datasets: [DTU, BlendedMVS]
metrics: [PSNR, SSIM, LPIPS]
---

# UNISURF: Unifying Neural Implicit Surfaces and Radiance Fields for Multi-View Reconstruction

Oechsle et al. propose UNISURF, the first method to unify implicit-surface
reconstruction (DVR, IDR) and radiance-field volume rendering (NeRF) under
a single formulation. The motivating tension is that DVR/IDR-style surface
methods reconstruct clean geometry but require accurate per-pixel object
masks as supervision, while NeRF requires no masks but produces a fuzzy
volume density that does not admit a clean surface.

The unifying observation is that surface rendering and volume rendering
differ only in how opacity is distributed along a ray. UNISURF
parameterizes the scene as an occupancy field (binary inside/outside,
relaxed to a probability) and lets a single training pipeline interpolate
between the two regimes: early in training the model behaves like a soft
volume renderer, so gradients flow through entire rays and bad
initializations recover; late in training the opacity sharpens around
the occupancy boundary and the renderer collapses to surface rendering,
yielding crisp, mask-free reconstructions.

Experiments on DTU, BlendedMVS, and an internal synthetic indoor dataset
show that UNISURF outperforms NeRF on reconstruction quality while
matching IDR (Yariv et al., 2020) without using foreground masks. The
unification also enables more efficient ray sampling: once the model has
learned where the surface lies, the sampler can concentrate points around
the occupancy boundary rather than uniformly along the ray.

UNISURF is a foundational reference for the surface-from-volume lineage
that includes NeuS (Wang et al., 2021) and VolSDF (Yariv et al., 2021),
both of which substitute a signed distance function for UNISURF's
occupancy field and refine the bias analysis. Together these three
papers established the multi-view surface-reconstruction paradigm that
dominates the area today.
