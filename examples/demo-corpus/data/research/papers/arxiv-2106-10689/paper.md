---
type: Paper
arxiv: "2106.10689"
arxiv_url: https://arxiv.org/abs/2106.10689
title: "NeuS: Learning Neural Implicit Surfaces by Volume Rendering for Multi-view Reconstruction"
authors:
  - "Peng Wang"
  - "Lingjie Liu"
  - "Yuan Liu"
  - "Christian Theobalt"
  - "Taku Komura"
  - "Wenping Wang"
date: 2021-06-20
sub_topic: Mesh and Surface Reconstruction
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RadianceField, VolumeRendering, NeuralImplicitSurface, NovelViewSynthesis]
datasets: [DTU, BlendedMVS]
metrics: [PSNR, SSIM, LPIPS]
oss_repo: Totoro97/NeuS
---

# NeuS: Learning Neural Implicit Surfaces by Volume Rendering for Multi-view Reconstruction

Wang et al. present NeuS, a mask-free neural surface reconstruction
method that represents geometry as the zero-level set of a signed
distance function (SDF) and renders it with a volume-rendering integral
adapted from NeRF (Mildenhall et al., 2020). The motivation is to
inherit NeRF's robust gradient-based optimization while obtaining the
clean, mesh-extractable geometry that IDR and DVR-style surface methods
provide — but without requiring per-pixel foreground masks as those
methods do.

The technical contribution is a new opacity formulation for SDF-driven
volume rendering. The authors show that the obvious approach — turning
the SDF into a density with a logistic function and rendering as in NeRF
— introduces a first-order bias in the rendered surface location, so
that the recovered zero level set systematically drifts from where the
photometric residual is minimized. NeuS proposes an alternative opacity
function constructed from the cumulative distribution of a logistic
density that is unbiased to first order in the approximation, and
provides a derivation showing its consistency with classical volume
rendering.

Experiments on DTU and BlendedMVS show that NeuS produces noticeably
sharper and more complete reconstructions than UNISURF and IDR on
objects with thin structures and self-occlusion, all without input
masks. The released codebase at github.com/Totoro97/NeuS is the
reference implementation that downstream work — MonoSDF, Voxurf, NeuS2,
and several Gaussian-Splatting surface variants — extends.

NeuS, alongside VolSDF (Yariv et al., 2021) published days later, defined
the SDF-via-volume-rendering paradigm that has since displaced both
classical MVS and original NeRF for high-fidelity multi-view surface
reconstruction.
