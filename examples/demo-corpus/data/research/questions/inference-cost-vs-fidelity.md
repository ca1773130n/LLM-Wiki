---
type: OpenQuestion
title: "Feed-forward reconstruction vs per-scene optimisation: where does each win?"
sub_topics: [Generative 3D Representations, 3D Gaussian Splatting, Diffusion-based 3D Generation]
papers_surfaced_in:
  - arxiv-2311-04400
  - arxiv-2311-06214
  - arxiv-2402-05054
  - arxiv-2403-02151
  - arxiv-2308-04079
  - arxiv-2309-16653
  - arxiv-2201-05989
status: open
asked: 2026-05-05
---

# Feed-forward reconstruction vs per-scene optimisation: where does each win?

The corpus contains two opposed bets on the right architecture for
single- or sparse-view 3D reconstruction.

The per-scene optimisation bet is the dominant one historically.
[3D Gaussian Splatting](../../papers/arxiv-2308-04079/paper.md) optimises a
primitive cloud against the photometric loss for each scene;
[Instant-NGP](../../papers/arxiv-2201-05989/paper.md) optimises a hash grid;
[DreamGaussian](../../papers/arxiv-2309-16653/paper.md) optimises Gaussians
against an SDS critic. Time per asset has dropped from hours to minutes,
but the per-scene loop is still there.

The feed-forward bet is more recent.
[LRM](../../papers/arxiv-2311-04400/paper.md) (Hong et al., 2023) trains
a large transformer on Objaverse to produce a triplane radiance field from
a single image in ~5 seconds with no per-scene loop at all.
[Instant3D](../../papers/arxiv-2311-06214/paper.md) chains a multi-view
diffusion stage in front of an LRM-style backbone.
[LGM](../../papers/arxiv-2402-05054/paper.md) ports the architecture onto
the splatting representation, and
[TripoSR](../../papers/arxiv-2403-02151/paper.md) is the open production-quality
release in this line.

The question — and the gap in the corpus — is: on the *same prompt or
input image*, how does feed-forward output compare to per-scene
optimisation in fidelity, geometric correctness, and downstream usability?
The published comparisons are mostly self-reported and choose inputs that
favour the proposing method. The qualitative impression is that
feed-forward gives you a coherent-but-blurry result in seconds, while
per-scene SDS-on-Gaussians gives you a sharper-but-occasionally-broken
result in minutes. But "qualitative impression" isn't a benchmark.

The economics matter beyond aesthetics. Feed-forward methods amortise
training cost across all future inferences; per-scene methods pay the cost
once per asset. The break-even point depends on the asset volume, which
is exactly the variable a serious benchmark would parameterise.

What would resolve this: a head-to-head evaluation suite that takes a fixed
set of input images, runs all four feed-forward methods and at least two
per-scene SDS-on-splats methods, and reports (a) reconstruction fidelity
on held-out views, (b) geometric error against ground truth where
available, (c) wall-clock inference time, (d) GPU-hour amortised cost
per asset across a realistic asset-volume range. None of the papers in
this corpus provides that decomposition. Until they do, "feed-forward
is the future" and "SDS-on-splats is the future" can both be defended
without evidence.
