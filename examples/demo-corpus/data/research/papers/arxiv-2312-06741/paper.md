---
type: Paper
arxiv: "2312.06741"
arxiv_url: https://arxiv.org/abs/2312.06741
title: "Gaussian Splatting SLAM"
authors:
  - "Hidenobu Matsuki"
  - "Riku Murai"
  - "Paul H. J. Kelly"
  - "Andrew J. Davison"
date: 2023-12-11
sub_topic: Visual SLAM and MVS
methods: [GaussianSplatting, SLAM, StructureFromMotion, NovelViewSynthesis]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: muskie82/MonoGS
license: "CC-BY-4.0 (Tesserae demo prose)"
---

# Gaussian Splatting SLAM

Matsuki et al. present MonoGS, the first SLAM system to use 3D
GaussianSplatting as its sole scene representation in the difficult
monocular setting. Vanilla 3DGS requires accurate per-image camera poses
from an offline StructureFromMotion stage; in a SLAM context those poses
have to be estimated online from a live monocular stream, with no depth
sensor. The paper shows that camera tracking can be done directly against
the Gaussian map by differentiating the splat rendering with respect to
camera parameters, and that this yields a wide basin of convergence and
robust tracking at roughly 3 FPS.

The system is unified: the same Gaussian field supports tracking, mapping,
and high-quality NovelViewSynthesis. Tracking minimises a photometric loss
between the current frame and a render of the current map from the
candidate pose. Mapping grows new Gaussians where the map fails to
explain incoming pixels and updates existing ones via the usual splatting
optimisation. The authors introduce explicit geometric verification and
regularisation steps that exploit the primitive nature of Gaussians to
suppress the ambiguities (floaters, sliding surfaces, scale drift) that
plague incremental monocular reconstruction. When an RGB-D sensor is
available, the same machinery accepts depth as an additional supervision
signal without architectural change.

Because primitives are explicit and tied to image evidence, the system is
able to reconstruct tiny and even transparent objects that are hard for
implicit neural SLAM methods. The paper is broadly contemporary with
GS-SLAM by Yan et al., which focuses on RGB-D; together they establish
Gaussian-based incremental SLAM as a practical direction and serve as
direct successors to Point-SLAM and Co-SLAM. The released MonoGS code is a
common reference implementation for monocular Gaussian SLAM.
