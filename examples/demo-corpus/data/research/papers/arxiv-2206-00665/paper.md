---
type: Paper
arxiv: "2206.00665"
arxiv_url: https://arxiv.org/abs/2206.00665
title: "MonoSDF: Exploring Monocular Geometric Cues for Neural Implicit Surface Reconstruction"
authors:
  - "Zehao Yu"
  - "Songyou Peng"
  - "Michael Niemeyer"
  - "Torsten Sattler"
  - "Andreas Geiger"
date: 2022-06-01
sub_topic: Mesh and Surface Reconstruction
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [NeuralImplicitSurface, MultiViewStereo]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# MonoSDF: Exploring Monocular Geometric Cues for Neural Implicit Surface Reconstruction

Yu et al. address a failure mode shared by NeuS (Wang et al., 2021),
VolSDF (Yariv et al., 2021), and UNISURF (Oechsle et al., 2021):
multi-view neural implicit surface methods produce excellent results on
small, well-observed objects but degrade rapidly on large, textureless,
or sparsely captured scenes. The diagnosis is that the photometric RGB
loss alone is too weak a constraint in regions of low texture or low
multi-view overlap.

MonoSDF augments the standard signed-distance-function plus volume-
rendering pipeline with two monocular geometric cues, both produced by
general-purpose off-the-shelf predictors that were never trained on the
target scenes. A monocular depth predictor produces a per-pixel relative
depth estimate, which is converted into a scale-and-shift-invariant
depth-consistency loss against the rendered depth of the SDF. A
monocular surface-normal predictor produces a per-pixel normal estimate,
which is matched against the rendered surface normal (the analytic
gradient of the SDF). Both losses are robust to the noise inherent in
single-image predictions but provide dense supervision on every pixel.

The authors also conduct a systematic study of representation choice:
monolithic MLPs versus single-resolution voxel grids versus the multi-
resolution hash grids of Instant-NGP (Müller et al., 2022). The
monocular cues improve every backbone, with the hash-grid variant
producing the best speed-quality trade-off. On ScanNet, Replica, and
Tanks-and-Temples the method substantially improves over NeuS and VolSDF
on both small-scene and room-scale benchmarks.

MonoSDF crystallized the recipe — SDF backbone, volume rendering,
hash-grid encoding, monocular priors — that subsequent indoor and
outdoor surface-reconstruction work has largely converged on, including
the Gaussian-Splatting surface variants that postdate this corpus.
