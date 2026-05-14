---
type: Paper
arxiv: "2311.04400"
arxiv_url: https://arxiv.org/abs/2311.04400
title: "LRM: Large Reconstruction Model for Single Image to 3D"
authors:
  - "Yicong Hong"
  - "Kai Zhang"
  - "Jiuxiang Gu"
  - "Sai Bi"
  - "Yang Zhou"
  - "Difan Liu"
  - "Feng Liu"
  - "Kalyan Sunkavalli"
  - "Trung Bui"
  - "Hao Tan"
date: 2023-11-08
sub_topic: Generative 3D Representations
methods: [RadianceField, ImageTo3D, TransformerArchitecture, LargeReconstructionModel]
datasets: [ShapeNet, Objaverse]
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# LRM: Large Reconstruction Model for Single Image to 3D

Hong et al. propose the Large Reconstruction Model (LRM), the first
attempt to apply foundation-model scaling laws directly to single-image 3D
reconstruction. Where contemporaneous ImageTo3D systems either depended on
slow ScoreDistillation optimisation or were trained per-category on small
sets like ShapeNet, LRM treats reconstruction as a feed-forward learning
problem: a single forward pass of a 500-million-parameter Transformer maps
the input image to the parameters of a NeRF-style RadianceField.

The architecture takes encoder features from the input image and uses a
deep cross-attention TransformerArchitecture to predict a triplane
representation that parameterises the output radiance field. The model is
trained end-to-end against multi-view supervision on roughly one million
objects, combining synthetic renders from Objaverse with real captures from
MVImgNet. The breadth of the training corpus and the model capacity together
give the network strong generalisation to in-the-wild images, including
those produced by 2D generative models, well beyond the closed-vocabulary
behaviour of earlier category-specific reconstructors.

Inference takes about five seconds per object — orders of magnitude faster
than per-instance SDS pipelines such as Magic123 and DreamFusion — while
still producing meshes detailed enough for downstream use. The LRM
architecture has become a foundation for a family of feed-forward
generators: Instant3D feeds it the four-view output of a multi-view
diffusion model, TripoSR rebuilds it with improved data and training, and
LGM swaps the implicit radiance field for a multi-view Gaussian
representation. The paper is widely credited with shifting 3D reconstruction
research from per-scene optimisation to amortised inference.
