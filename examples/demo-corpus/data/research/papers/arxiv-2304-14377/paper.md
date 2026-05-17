---
type: Paper
arxiv: "2304.14377"
arxiv_url: https://arxiv.org/abs/2304.14377
title: "Co-SLAM: Joint Coordinate and Sparse Parametric Encodings for Neural Real-Time SLAM"
authors:
  - "Hengyi Wang"
  - "Jingwen Wang"
  - "Lourdes Agapito"
date: 2023-04-27
sub_topic: Visual SLAM and MVS
methods: [SLAM, StructureFromMotion, BundleAdjustment, RealTimeRendering]
datasets: [ScanNet, Replica]
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (Tesserae demo prose)"
---

# Co-SLAM: Joint Coordinate and Sparse Parametric Encodings for Neural Real-Time SLAM

Wang et al. introduce Co-SLAM, a real-time neural RGB-D SLAM system designed
around a hybrid scene encoding that combines a multi-resolution hash grid
with a coordinate-based one-blob encoding. The hash grid contributes fast
convergence and high-frequency detail, while the smooth coordinate encoding
encourages surface coherence in regions that the camera has not yet
observed — a known weakness of purely parametric grids, which tend to leave
unobserved space noisy.

The hybrid representation feeds a shallow MLP that predicts signed
distance and colour for queried 3D points. Camera tracking is performed by
inverting this rendering through a photometric and depth loss; the system
then folds tracking and mapping into a global BundleAdjustment over all
keyframes rather than the small active-keyframe window used in iMAP and
NICE-SLAM. A ray sampling strategy tuned to the hybrid representation keeps
the bundle adjustment tractable at interactive rates.

On Replica, ScanNet, and TUM-RGBD the system runs at 10–17 Hz and matches
or exceeds prior neural SLAM methods in reconstruction quality (PSNR, SSIM,
LPIPS) and tracking accuracy. The global BundleAdjustment is shown to be
essential in long sequences where local-window optimisation alone allows
drift to accumulate, while the smoothness contribution of the one-blob
encoding keeps unobserved regions plausible rather than empty. Co-SLAM is
part of a wave of neural SLAM systems that culminated in
GaussianSplatting-based variants such as GS-SLAM and Gaussian Splatting
SLAM, but it remains a strong baseline for hybrid implicit
representations and for studying how surface-completion priors interact
with high-frequency parametric encodings in incremental reconstruction.
