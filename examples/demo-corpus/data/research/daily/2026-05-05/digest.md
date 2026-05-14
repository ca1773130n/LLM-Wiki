---
type: ResearchDigest
date: 2026-05-05
period: daily
papers_covered:
  - arxiv-2209-14988
  - arxiv-2211-10440
  - arxiv-2303-11328
  - arxiv-2305-16213
  - arxiv-2306-17843
  - arxiv-2309-16653
sub_topics: [Diffusion-based 3D Generation, 3D Gaussian Splatting]
---

# Daily digest — 2026-05-05

Diffusion-into-3D day. The thread: how Score Distillation Sampling (SDS)
evolved from a clever trick into a default and is now being partially
displaced.

[DreamFusion](../../papers/arxiv-2209-14988/paper.md) (Poole et al., 2022)
is the SDS paper. A 2D text-to-image diffusion model is used as a critic
that backpropagates a per-view rendering of a NeRF toward "looks like the
prompt". No 3D training data; the prior comes entirely from the 2D
diffusion model. The
[ashawkey/stable-dreamfusion](../../repos/ashawkey-stable-dreamfusion/about.md)
reimplementation is what most people actually ran, since the original used
proprietary Imagen weights.

[Magic3D](../../papers/arxiv-2211-10440/paper.md) (Lin et al., 2022) is the
coarse-to-fine, mesh-export version: low-resolution NeRF first, then a
high-resolution textured-mesh refinement stage. The two-stage pattern
becomes standard.

[Zero-1-to-3](../../papers/arxiv-2303-11328/paper.md) (Liu et al., 2023) is
a different lever: fine-tune Stable Diffusion to condition on camera pose
relative to a reference image. Now your prior is geometric, not just
appearance-level. [cvlab-columbia/zero123](../../repos/cvlab-columbia-zero123/about.md)
became the default novel-view prior for downstream image-to-3D.
[Magic123](../../papers/arxiv-2306-17843/paper.md) (Qian et al., 2023)
combines a 2D Stable Diffusion SDS loss with a 3D Zero-1-to-3 SDS loss —
get the appearance richness of 2D priors plus the geometric consistency of
3D ones.

[ProlificDreamer](../../papers/arxiv-2305-16213/paper.md) (Wang et al.,
2023) reframes SDS as a particle-based variational approximation
(Variational Score Distillation). The mode-collapse problem of vanilla
SDS — overly smooth, oversaturated geometry — largely goes away. Best
SDS-line read in the corpus.

The pivot is [DreamGaussian](../../papers/arxiv-2309-16653/paper.md) (Tang
et al., 2023): replace the NeRF backbone with 3D Gaussians for SDS.
~2 minutes instead of ~hours per asset, because rasterisation is faster
than ray marching. The [dreamgaussian/dreamgaussian](../../repos/dreamgaussian-dreamgaussian/about.md)
release is small and readable; it's where I'd start anyone learning this
sub-field today.

Six papers, ~55 min. Next week: pull these threads together.
