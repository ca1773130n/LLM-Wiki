---
type: Paper
arxiv: "2103.13415"
arxiv_url: https://arxiv.org/abs/2103.13415
title: "Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields"
authors:
  - "Jonathan T. Barron"
  - "Ben Mildenhall"
  - "Matthew Tancik"
  - "Peter Hedman"
  - "Ricardo Martin-Brualla"
  - "Pratul P. Srinivasan"
date: 2021-03-24
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [RadianceField, AntiAliasing]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: google/mipnerf
---

# Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields

Barron et al. identify a fundamental sampling problem in NeRF (Mildenhall
et al., 2020): each pixel is rendered by tracing a single infinitesimally
thin ray, so the network has no signal about the area or solid-angle
footprint that the pixel actually covers. When training and test images
view a scene at different resolutions, this produces aliasing — high-
frequency content reconstructed at low-resolution viewpoints and blur at
high-resolution viewpoints.

Mip-NeRF replaces the ray with a cone whose apex sits at the camera
center and whose footprint matches the pixel. Along the cone, the
representation is a sequence of conical frustums rather than point
samples. Each frustum is encoded by an integrated positional encoding
(IPE): the expectation of NeRF's sinusoidal positional encoding under a
multivariate Gaussian that approximates the frustum. The expectation has
a closed form, so IPE features are computable analytically and produce
features whose high-frequency components are damped in proportion to the
frustum's spatial extent — exactly the anti-aliased multi-scale behavior
of classical mipmapping.

Because the same MLP can now consume features at any scale, mip-NeRF
collapses the coarse and fine MLPs of vanilla NeRF into a single network,
making it 7% faster and half the size while reducing average error by
17% on the standard NeRF synthetic dataset and 60% on a new multiscale
variant the authors introduce. It also matches brute-force supersampled
NeRF at 22x lower cost.

Mip-NeRF became the standard NeRF backbone for downstream work that
needed to handle multi-scale capture, including its own follow-up Mip-NeRF
360 (Barron et al., 2021) for unbounded scenes and a long line of
anti-aliased radiance-field variants. Within this corpus the paper is
the canonical reference for the IPE construction.
