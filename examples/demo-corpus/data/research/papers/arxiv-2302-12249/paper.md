---
type: Paper
arxiv: "2302.12249"
arxiv_url: https://arxiv.org/abs/2302.12249
title: "MERF: Memory-Efficient Radiance Fields for Real-time View Synthesis in Unbounded Scenes"
authors:
  - "Christian Reiser"
  - "Richard Szeliski"
  - "Dor Verbin"
  - "Pratul P. Srinivasan"
  - "Ben Mildenhall"
  - "Andreas Geiger"
  - "Jonathan T. Barron"
  - "Peter Hedman"
date: 2023-02-23
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [RadianceField, NovelViewSynthesis, RealTimeRendering]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# MERF: Memory-Efficient Radiance Fields for Real-time View Synthesis in Unbounded Scenes

Reiser et al. present MERF, a baked radiance-field representation that
delivers real-time browser rendering of unbounded scenes while staying
within the memory budget of consumer GPUs. The work occupies a specific
gap: PlenOctrees (Yu et al., 2021) and SNeRG showed that NeRF can be
baked for real-time rendering of bounded objects, but neither scales to
the large-scale 360-degree captures that Mip-NeRF 360 (Barron et al.,
2021) made tractable to reconstruct.

MERF's representation is a hybrid of two complementary explicit
structures. A coarse sparse 3D feature grid stores volumetric content
near surfaces, with empty space pruned. Three high-resolution 2D
feature planes (axis-aligned, one per coordinate pair) supplement the
grid with fine detail at near-zero additional memory cost. A small MLP
decodes the combined features into density and view-dependent color.
The decomposition mirrors the TensoRF / K-Planes factorization but is
geared specifically for low-memory baking rather than fast training.

To handle the unbounded nature of the target scenes, the authors
introduce a contraction function that maps world coordinates into a
bounded volume but, unlike Mip-NeRF 360's parameterization, is designed
to preserve efficient ray-box intersection — a hard requirement for the
fast ray traversal that real-time rendering needs. The training
pipeline is lossless: the parameterization used during optimization is
identical to the one used at render time, so the baked model has the
same quality as the trained model.

End-to-end, MERF renders large-scale unbounded scenes at interactive
frame rates inside a browser with quality close to a fully trained
Mip-NeRF 360. It is a key reference for "shippable" radiance-field
formats and a precursor of the production baking pipelines that
3D-Gaussian-Splatting variants would later inherit.
