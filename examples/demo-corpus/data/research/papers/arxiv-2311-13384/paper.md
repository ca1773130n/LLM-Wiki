---
type: Paper
arxiv: "2311.13384"
arxiv_url: https://arxiv.org/abs/2311.13384
title: "LucidDreamer: Domain-free Generation of 3D Gaussian Splatting Scenes"
authors:
  - "Jaeyoung Chung"
  - "Suyoung Lee"
  - "Hyeongjin Nam"
  - "Jaerin Lee"
  - "Kyoung Mu Lee"
date: 2023-11-22
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, PointCloud]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# LucidDreamer: Domain-free Generation of 3D Gaussian Splatting Scenes

Chung et al. propose LucidDreamer, a pipeline that generates large 3D
scenes — not just isolated objects — using only off-the-shelf 2D diffusion
priors and no scene-scale 3D training data. Prior scene-generation methods
typically constrain themselves to a domain (e.g. indoor rooms scanned by
3D capture rigs) because they depend on 3D supervision; LucidDreamer
avoids this by lifting outputs of a general-purpose image diffusion model
into a 3D PointCloud and converting that point cloud into a GaussianSplatting
scene.

The pipeline alternates between two operations the authors call Dreaming
and Alignment. In Dreaming, the current point cloud is projected to a new
target view; the rendered (partial, masked) image is fed back into the
diffusion model as an inpainting prompt, producing a coherent novel-view
image. The new image is then lifted to 3D by combining a monocular depth
estimate with the known camera pose, yielding a fresh chunk of points.
Alignment merges this new chunk into the accumulated cloud by smoothing
inconsistencies across overlapping observations so that subsequent
renders remain coherent.

Once the iterative Dream/Align loop has populated the scene, the
aggregated point cloud is used to initialise a 3D Gaussian Splatting
optimisation, which refines colour and density to produce a final
explicit representation that can be rendered in real time. Because the
2D diffusion model is unrestricted in subject, the pipeline inherits its
generality: indoor, outdoor, stylised, and photo-realistic scenes can be
produced with the same machinery, and the only data requirement is the
pre-trained image model. The work sits alongside scene-level methods such
as GALA3D as part of an emerging literature on Gaussian-based open-domain
3D content creation.
