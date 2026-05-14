---
type: Paper
arxiv: "2403.02151"
arxiv_url: https://arxiv.org/abs/2403.02151
title: "TripoSR: Fast 3D Object Reconstruction from a Single Image"
authors:
  - "Dmitry Tochilkin"
  - "David Pankratz"
  - "Zexiang Liu"
  - "Zixuan Huang"
  - "Adam Letts"
  - "Yangguang Li"
  - "Ding Liang"
  - "Christian Laforte"
  - "Varun Jampani"
  - "Yan-Pei Cao"
date: 2024-03-04
sub_topic: Generative 3D Representations
methods: [TransformerArchitecture, LargeReconstructionModel, FeedForward]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: VAST-AI-Research/TripoSR
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# TripoSR: Fast 3D Object Reconstruction from a Single Image

Tochilkin et al. release TripoSR, a FeedForward single-image 3D
reconstruction model that takes the TransformerArchitecture introduced by
LRM and pushes it on data, training, and engineering. The headline
contribution is throughput: TripoSR returns a mesh from a single image
in under half a second, compared to the roughly five-second inference of
LRM, while improving quantitative and qualitative reconstruction quality
on standard benchmarks.

The architecture preserves LRM's LargeReconstructionModel template — an
image encoder followed by a cross-attention transformer that predicts a
triplane-parameterised volumetric representation — but tightens it on
several axes. The training corpus is expanded and cleaned with
quality-aware filtering so that low-quality multi-view supervision is
de-emphasised; new data augmentations expose the model to a wider range
of object scales, orientations, and lighting conditions; and the training
objective is adjusted to balance silhouette, photometric, and geometric
terms in a way that the report finds more stable than the original LRM
recipe. Inference is further accelerated by careful kernel scheduling and
mixed-precision execution.

The technical report deliberately stays close to LRM in headline
architecture; its contribution is the careful tuning that converts an
academic prototype into a robust, fast, openly licensed model. TripoSR is
released under MIT and has become a popular base for downstream
single-image-to-3D work, including pipelines that pair it with multi-view
diffusion in the style of Instant3D and pipelines that swap its implicit
output for a GaussianSplatting head similar to LGM. The report is brief
because the abstract claims are deliberately narrow — the value is in the
released artefact and the engineering recipe rather than a new theoretical
result.
