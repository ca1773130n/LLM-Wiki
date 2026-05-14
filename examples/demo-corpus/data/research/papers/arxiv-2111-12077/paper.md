---
type: Paper
arxiv: "2111.12077"
arxiv_url: https://arxiv.org/abs/2111.12077
title: "Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields"
authors:
  - "Jonathan T. Barron"
  - "Ben Mildenhall"
  - "Dor Verbin"
  - "Pratul P. Srinivasan"
  - "Peter Hedman"
date: 2021-11-23
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RadianceField, AntiAliasing, NovelViewSynthesis]
datasets: [Mip-NeRF360]
metrics: [PSNR, SSIM, LPIPS]
---

# Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields

Barron et al. extend Mip-NeRF (Barron et al., 2021) from object-centric
capture to unbounded 360-degree scenes — outdoor environments and large
indoor spaces where the camera rotates around a point and the scene
content extends to arbitrary depths. Three problems prevent vanilla
Mip-NeRF from handling this setting: distant background content cannot
be parameterized by a uniformly sampled bounded volume; the optimization
is slow on large scenes; and unbounded captures admit floaters and
shape-radiance ambiguities that produce visually disturbing artifacts.

The paper introduces three contributions. A non-linear scene
parameterization contracts unbounded 3D coordinates into a bounded
domain, with a piecewise rule that keeps the near-field nearly linear
and compresses the far-field smoothly toward infinity — extending the
classical NDC trick to non-forward-facing captures. An online
distillation scheme uses a small proposal MLP to predict where mass
lies along a ray, supervised by a larger radiance MLP, which makes
hierarchical sampling far more efficient and lets the radiance network
focus capacity on visible content. A distortion-based regularizer
penalizes radiance contributions that are smeared along the ray rather
than concentrated, which suppresses the floaters and background haze
that plague large-scene NeRFs.

The combination reduces mean-squared error by 57% relative to Mip-NeRF
on the new 360-degree benchmark that the authors introduce with the
paper, and produces clean depth maps for highly intricate real-world
captures. The "mipnerf360" dataset itself has become a standard
evaluation suite for unbounded radiance-field methods, used by every
subsequent system in this corpus that targets the same regime including
3D Gaussian Splatting, MERF, and Zip-NeRF.

The non-linear contraction and proposal-network architecture are now
ubiquitous components of any modern radiance-field codebase.
