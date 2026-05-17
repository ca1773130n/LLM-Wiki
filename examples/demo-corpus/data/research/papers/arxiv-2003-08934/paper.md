---
type: Paper
arxiv: "2003.08934"
arxiv_url: https://arxiv.org/abs/2003.08934
title: "NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis"
authors:
  - "Ben Mildenhall"
  - "Pratul P. Srinivasan"
  - "Matthew Tancik"
  - "Jonathan T. Barron"
  - "Ravi Ramamoorthi"
  - "Ren Ng"
date: 2020-03-19
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [RadianceField, VolumeRendering, NovelViewSynthesis]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: bmild/nerf
---

# NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis

Mildenhall et al. introduce Neural Radiance Fields (NeRF), a scene
representation that encodes a continuous volumetric function with a
fully-connected coordinate-based MLP. The network takes a 5D input — a
3D spatial location and a 2D viewing direction — and produces a volume
density and a view-dependent emitted radiance. Novel views are synthesized
by querying many such 5D coordinates along camera rays and compositing
the predictions with classical volume rendering.

Two design choices made the approach work where prior coordinate-based
methods had stalled. First, the authors apply a sinusoidal positional
encoding to the input coordinates before the MLP, lifting them into a
higher-frequency space where the network can fit high-frequency scene
content. Second, they use a hierarchical coarse-to-fine sampling scheme:
a coarse network estimates where mass lies along each ray, and a fine
network then importance-samples around those locations. Because the
emission-absorption volume rendering integral is naturally differentiable,
the entire system trains from posed multi-view images by photometric
loss, with no explicit geometry supervision.

Quantitative results on synthetic and real datasets outperform contemporary
methods including LLFF, SRN, and NV in PSNR, SSIM, and LPIPS, while
producing visibly sharper specularities and thin structures. The result
established the paradigm that has dominated 3D reconstruction since:
implicit, coordinate-based, differentiable, optimized per-scene.

NeRF spawned a large family of follow-ups represented in this corpus —
Mip-NeRF (aliasing), NeRF-W (in-the-wild), Nerfies and HyperNeRF
(deformable), PlenOctrees and Plenoxels (fast rendering), Instant-NGP
(hash encoding), and the surface-reconstruction line UNISURF/NeuS/VolSDF.
The reference implementation at github.com/bmild/nerf remains the canonical
starting point.
