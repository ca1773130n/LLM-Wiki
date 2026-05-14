---
type: Paper
arxiv: "2311.06214"
arxiv_url: https://arxiv.org/abs/2311.06214
title: "Instant3D: Fast Text-to-3D with Sparse-View Generation and Large Reconstruction Model"
authors:
  - "Jiahao Li"
  - "Hao Tan"
  - "Kai Zhang"
  - "Zexiang Xu"
  - "Fujun Luan"
  - "Yinghao Xu"
  - "Yicong Hong"
  - "Kalyan Sunkavalli"
  - "Greg Shakhnarovich"
  - "Sai Bi"
date: 2023-11-10
sub_topic: Generative 3D Representations
methods: [RadianceField, Diffusion, ScoreDistillation, TextTo3D, TransformerArchitecture, LargeReconstructionModel]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# Instant3D: Fast Text-to-3D with Sparse-View Generation and Large Reconstruction Model

Li et al. propose Instant3D, a feed-forward TextTo3D pipeline that
sidesteps the slow per-prompt optimisation of ScoreDistillation methods
while avoiding the low-quality outputs typical of earlier direct-prediction
networks. The system splits the problem in two: first, generate a sparse
set of consistent views of the desired object; second, regress a 3D
RadianceField directly from those views.

The first stage fine-tunes a 2D text-to-image Diffusion model to emit
four structured, view-consistent images of an object in one shot. The
spatial layout of the four views is canonicalised so that downstream
regression can rely on known relative camera poses. The second stage uses
a TransformerArchitecture sparse-view reconstructor — a LargeReconstructionModel
in the style of LRM, but conditioned on the sparse multi-view input rather
than a single image — to predict the radiance field in one forward pass.
This decouples the appearance/diversity problem from the geometric
reconstruction problem and avoids the multi-view inconsistency ("Janus")
artefacts that plague single-image optimisation methods.

End-to-end Instant3D generates a 3D asset in roughly twenty seconds, two
orders of magnitude faster than per-prompt SDS systems such as
DreamFusion, Magic123, or ProlificDreamer, and the diversity benefits from
the diffusion sampler propagate to the 3D output. Because the multi-view
generator is reusable across prompts and the reconstructor is amortised,
batched generation across many prompts is straightforward, which the
authors highlight as a practical advantage for asset-creation workflows.
The paper is part of an emerging consensus that feed-forward reconstruction
conditioned on multi-view diffusion outputs is the right factorisation for
fast TextTo3D; later work (LGM, TripoSR) follows the same template, often
substituting GaussianSplatting or improved transformer backbones for the
radiance field predictor.
