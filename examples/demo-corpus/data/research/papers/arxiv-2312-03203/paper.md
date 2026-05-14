---
type: Paper
arxiv: "2312.03203"
arxiv_url: https://arxiv.org/abs/2312.03203
title: "Feature 3DGS: Supercharging 3D Gaussian Splatting to Enable Distilled Feature Fields"
authors:
  - "Shijie Zhou"
  - "Haoran Chang"
  - "Sicheng Jiang"
  - "Zhiwen Fan"
  - "Zehao Zhu"
  - "Dejia Xu"
  - "Pradyumna Chari"
  - "Suya You"
  - "Zhangyang Wang"
  - "Achuta Kadambi"
date: 2023-12-06
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, RadianceField, FeatureField, NovelViewSynthesis, RealTimeRendering]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# Feature 3DGS: Supercharging 3D Gaussian Splatting to Enable Distilled Feature Fields

Zhou et al. extend 3D GaussianSplatting beyond colour rendering to
arbitrary-channel FeatureField distillation, taking inspiration from earlier
NeRF-based feature distillation work that lifted 2D foundation models such
as CLIP-LSeg and SAM into a 3D RadianceField. Those earlier methods inherit
the slow rendering of implicit volumes and suffer from continuity
artefacts where the implicit field cannot match the spatial resolution of
the 2D foundation maps. Feature 3DGS keeps the RealTimeRendering of 3DGS
while adding distilled semantic features as a first-class output of the
splatting renderer.

A naive port — attaching a high-dimensional feature vector to every
Gaussian and rasterising it like colour — fails for two reasons: feature
maps from 2D foundation models live at a coarser spatial resolution than
RGB, and their channel statistics differ markedly. The authors propose
architectural and training adjustments that separate the colour and
feature branches of the renderer, adapt the loss to the resolution
mismatch, and stabilise high-dimensional feature optimisation. The result
is a Gaussian field that simultaneously renders photorealistic novel views
and projects consistent semantic features from any viewpoint.

Distilling SAM produces a Gaussian field that can be prompted by point or
bounding-box clicks at render time, enabling 3D-consistent segmentation
through the 2D SAM API — to the authors' knowledge, the first method to
support point and box prompting for radiance field manipulation. Distilling
CLIP-LSeg yields a language-queryable scene that supports open-vocabulary
NovelViewSynthesis editing and semantic segmentation. Across experiments
the system matches or beats prior NeRF-based feature distillation at a
fraction of the training and inference cost, helping establish the
Gaussian field as a general substrate for 3D-aware foundation-model
applications.
