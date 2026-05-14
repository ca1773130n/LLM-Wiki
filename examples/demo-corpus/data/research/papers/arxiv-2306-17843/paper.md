---
type: Paper
arxiv: "2306.17843"
arxiv_url: https://arxiv.org/abs/2306.17843
title: "Magic123: One Image to High-Quality 3D Object Generation Using Both 2D and 3D Diffusion Priors"
authors:
  - "Guocheng Qian"
  - "Jinjie Mai"
  - "Abdullah Hamdi"
  - "Jian Ren"
  - "Aliaksandr Siarohin"
  - "Bing Li"
  - "Hsin-Ying Lee"
  - "Ivan Skorokhodov"
  - "Peter Wonka"
  - "Sergey Tulyakov"
  - "Bernard Ghanem"
date: 2023-06-30
sub_topic: Diffusion-based 3D Generation
methods: [RadianceField, Diffusion, ImageTo3D, DepthEstimation]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# Magic123: One Image to High-Quality 3D Object Generation Using Both 2D and 3D Diffusion Priors

Qian et al. propose Magic123, a coarse-to-fine ImageTo3D pipeline that
recovers a textured 3D mesh from a single unposed photograph by combining
two complementary Diffusion priors. The first stage optimises a neural
RadianceField using reference-view supervision and novel-view guidance,
producing rough geometry and rough appearance. The second stage swaps the
volumetric NeRF for a memory-efficient differentiable mesh representation
and continues optimisation at higher resolution, producing a detailed
textured surface suitable for downstream graphics use.

The defining design choice is the joint use of a 2D text-to-image prior
(for stylistic and detail richness) and a 3D-aware diffusion prior
(for geometric consistency across novel views). A single scalar trade-off
parameter modulates between the two: leaning on the 2D prior produces
more imaginative novel views at the cost of geometric drift, while
leaning on the 3D prior keeps the object faithful to the input image but
risks blandness. Textual inversion captures the reference image's identity
in a token that can be reused by the diffusion guidance, and a monocular
DepthEstimation regulariser prevents the radiance field from collapsing
to degenerate flat or hollow solutions.

The two-stage design and the explicit 2D/3D prior interpolation became
common reference points for subsequent single-image-to-3D work. Magic123
predates feed-forward methods such as LRM, Instant3D, and TripoSR, but its
coarse-to-fine recipe and use of multiple diffusion priors continue to
inform optimisation-based pipelines aimed at high fidelity rather than raw
speed. Released code, models, and pre-generated assets accompany the
paper, which also helped establish in-the-wild image inputs — rather than
synthetic ShapeNet renders — as the appropriate evaluation regime for
single-image 3D generation.
