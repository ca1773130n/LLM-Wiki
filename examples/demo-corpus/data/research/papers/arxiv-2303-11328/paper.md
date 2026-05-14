---
type: Paper
arxiv: "2303.11328"
arxiv_url: https://arxiv.org/abs/2303.11328
title: "Zero-1-to-3: Zero-shot One Image to 3D Object"
authors:
  - "Ruoshi Liu"
  - "Rundi Wu"
  - "Basile Van Hoorick"
  - "Pavel Tokmakov"
  - "Sergey Zakharov"
  - "Carl Vondrick"
date: 2023-03-20
sub_topic: Diffusion-based 3D Generation
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [Diffusion, ImageTo3D, NovelViewSynthesis]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: cvlab-columbia/zero123
---

# Zero-1-to-3: Zero-shot One Image to 3D Object

Liu et al. introduce Zero-1-to-3, a framework that generates new views
of an object from a single RGB image by re-purposing the geometric
priors latent in a large-scale pretrained text-to-image diffusion
model. The single-view-to-3D problem is severely under-constrained —
infinite 3D shapes project to the same image — and prior work either
required category-specific training data or simply hallucinated
plausible-but-inconsistent novel views.

The approach fine-tunes a Stable-Diffusion-style 2D diffusion model to
become viewpoint-conditional: the model is trained to denoise the
target image of an object given the input image and a relative camera
transformation expressed as elevation, azimuth, and radius. Training
data comes from rendering the Objaverse synthetic 3D dataset at
randomized viewpoints, yielding triplets of (source view, relative
pose, target view) that the model fits with a standard latent diffusion
objective. Despite being trained only on synthetic data, the model
inherits the broad object prior of the underlying Stable Diffusion
backbone and generalizes zero-shot to in-the-wild photos, sketches, and
impressionist paintings.

Two downstream uses are demonstrated. First, sampling new viewpoints
directly: a single image becomes a controllable rotation around the
object. Second, single-view 3D reconstruction: the viewpoint-
conditional diffusion model is used as a Score Distillation Sampling
prior (Poole et al., 2022, DreamFusion) to optimize a NeRF from a
single input view, producing a full 3D model that is significantly
more accurate than prior single-view 3D methods.

Zero-1-to-3 connected the text-to-3D line (DreamFusion, Magic3D) to the
single-image-to-3D line and seeded a productive sub-area; follow-ups
including SyncDreamer, Wonder3D, and One-2-3-45 all build on its
viewpoint-conditional diffusion-model formulation. The code at
github.com/cvlab-columbia/zero123 is the reference implementation.
