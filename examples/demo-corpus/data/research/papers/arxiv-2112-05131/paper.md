---
type: Paper
arxiv: "2112.05131"
arxiv_url: https://arxiv.org/abs/2112.05131
title: "Plenoxels: Radiance Fields without Neural Networks"
authors:
  - "Alex Yu"
  - "Sara Fridovich-Keil"
  - "Matthew Tancik"
  - "Qinhong Chen"
  - "Benjamin Recht"
  - "Angjoo Kanazawa"
date: 2021-12-09
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [RadianceField, Plenoxels, NovelViewSynthesis]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: sxyu/svox2
---

# Plenoxels: Radiance Fields without Neural Networks

Yu, Fridovich-Keil et al. demonstrate that a radiance field can match
NeRF-quality view synthesis with no neural network at all. Plenoxels
(plenoptic voxels) represents a scene as a sparse 3D voxel grid where
each occupied voxel stores a scalar density and a set of spherical-
harmonic coefficients describing view-dependent color. Rendering is the
same emission-absorption volume rendering integral as NeRF (Mildenhall
et al., 2020), but the queried density and color values come from
trilinearly interpolating the voxel grid instead of evaluating an MLP.

Because the representation is fully explicit, training reduces to a
direct gradient-based optimization of the voxel coefficients against
the photometric loss. There is no autodiff through a deep network and
no positional encoding; the regularization that the MLP implicitly
provided in NeRF is replaced by explicit total-variation and sparsity
priors on the voxel values. Empty space is pruned aggressively after a
few iterations, leaving only a thin shell of voxels around the visible
scene surface.

The empirical claim is striking: on the standard NeRF synthetic and
forward-facing benchmarks, Plenoxels matches NeRF's PSNR, SSIM, and
LPIPS while training in roughly 11 minutes per scene on a single GPU
versus 1-2 days for NeRF — two orders of magnitude faster, with no loss
of quality. The result decoupled two ideas that had been conflated in
the early NeRF literature: that the scene representation needs to be
implicit, and that volume rendering needs the smoothing of a neural
network.

Plenoxels is the immediate methodological descendant of PlenOctrees (Yu
et al., 2021) by some of the same authors, and the direct ancestor of
Instant-NGP (Müller et al., 2022), DVGO, and TensoRF. Within this corpus
it is the canonical reference for grid-based radiance fields and is the
strongest argument that explicit representations deserve a first-class
place alongside coordinate-based MLPs.
