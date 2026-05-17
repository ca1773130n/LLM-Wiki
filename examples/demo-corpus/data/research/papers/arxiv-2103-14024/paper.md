---
type: Paper
arxiv: "2103.14024"
arxiv_url: https://arxiv.org/abs/2103.14024
title: "PlenOctrees for Real-time Rendering of Neural Radiance Fields"
authors:
  - "Alex Yu"
  - "Ruilong Li"
  - "Matthew Tancik"
  - "Hao Li"
  - "Ren Ng"
  - "Angjoo Kanazawa"
date: 2021-03-25
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [RadianceField, Octree, RealTimeRendering]
datasets: []
metrics: [FPS]
---

# PlenOctrees for Real-time Rendering of Neural Radiance Fields

Yu et al. introduce PlenOctrees, a sparse octree-based representation
that accelerates NeRF (Mildenhall et al., 2020) inference by more than
three orders of magnitude — rendering 800x800 frames at over 150 FPS on
a single GPU. The key observation is that a trained NeRF's MLP can be
evaluated densely on a 3D grid and discarded; what is needed at render
time is a lookup table indexed by spatial location, plus a compact
description of view-dependent appearance.

To remove the viewing-direction input from the MLP without losing
specularities, the authors retrain the radiance head to output the
coefficients of a spherical-harmonic expansion of view-dependent color.
A specular highlight then becomes a fixed set of SH coefficients per
voxel, evaluated at render time by an inexpensive direction-dependent
dot product. The pre-tabulated MLP outputs are pruned and stored in a
sparse octree, the PlenOctree, that skips empty space and concentrates
resolution near scene surfaces.

The PlenOctree itself is differentiable: after baking, the octree leaf
coefficients can be fine-tuned directly against the photometric loss,
typically improving on the source NeRF rather than just matching it.
This decoupling also shortens training: full NeRF convergence is no
longer required before baking and fine-tuning.

PlenOctrees enabled in-browser interactive viewing of NeRF scenes and is
the immediate predecessor of Plenoxels (Yu et al., 2021), which removes
the neural network entirely and trains a sparse-voxel SH grid from
scratch. The factorization into "occupancy octree plus SH appearance"
recurs in subsequent baking pipelines such as MERF and SNeRG, all
represented elsewhere in this corpus.
