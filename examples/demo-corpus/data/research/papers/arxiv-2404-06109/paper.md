---
type: Paper
arxiv: "2404.06109"
arxiv_url: https://arxiv.org/abs/2404.06109
title: "Revising Densification in Gaussian Splatting"
authors:
  - "Samuel Rota Bulò"
  - "Lorenzo Porzi"
  - "Peter Kontschieder"
date: 2024-04-09
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, NovelViewSynthesis]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# Revising Densification in Gaussian Splatting

Rota Bulò et al. revisit the Adaptive Density Control (ADC) heuristic
introduced with the original 3D GaussianSplatting paper by Kerbl et al.
ADC governs when primitives are cloned, split, or pruned during training,
using positional-gradient magnitudes as its trigger. The authors argue
that this criterion is only a proxy for the quantity that actually matters
— per-pixel reconstruction error — and that the proxy is biased in ways
that cause well-known artefacts: floating Gaussians, missing structure in
under-densified regions, and runaway primitive counts in scenes with many
high-frequency details.

The paper proposes a more principled, pixel-error-driven formulation for
density control in 3DGS. The trigger for densification becomes an
auxiliary per-pixel error function computed during training, and
primitives are cloned or split in proportion to where they actually
explain the rendered output poorly rather than where their positional
gradients happen to be large. A complementary mechanism caps the total
number of primitives generated per scene, which gives the user a direct
handle on the speed/quality trade-off and prevents the long-tail
explosions that ADC sometimes produces.

The authors also identify and correct a bias in ADC's opacity handling
during cloning operations, where the existing implementation
inadvertently doubles effective opacity contributions and skews the
optimisation. With both fixes in place the method produces consistent
quality improvements across standard NovelViewSynthesis benchmarks
without sacrificing the efficiency of 3DGS. The work is part of a small
but important literature on the optimisation side of GaussianSplatting,
complementing structural variants such as Scaffold-GS, SuGaR, and 2D
Gaussian Splatting that change the primitive itself rather than the
densification schedule.
