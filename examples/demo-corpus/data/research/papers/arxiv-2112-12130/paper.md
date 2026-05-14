---
type: Paper
arxiv: "2112.12130"
arxiv_url: https://arxiv.org/abs/2112.12130
title: "NICE-SLAM: Neural Implicit Scalable Encoding for SLAM"
authors:
  - "Zihan Zhu"
  - "Songyou Peng"
  - "Viktor Larsson"
  - "Weiwei Xu"
  - "Hujun Bao"
  - "Zhaopeng Cui"
  - "Martin R. Oswald"
  - "Marc Pollefeys"
date: 2021-12-22
sub_topic: Visual SLAM and MVS
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [NeuralImplicitSurface, SLAM]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# NICE-SLAM: Neural Implicit Scalable Encoding for SLAM

Zhu et al. present NICE-SLAM, a dense online SLAM system that
reconstructs an implicit neural scene representation while
simultaneously tracking the camera. It targets a gap left by iMAP, the
first neural-implicit SLAM system: a single shared MLP over the entire
scene is convenient for small rooms but cannot scale to larger spaces
because every observation perturbs every parameter, producing
over-smoothing and forgetting.

NICE-SLAM replaces the monolithic MLP with a hierarchical feature grid.
Three voxel grids at coarse, mid, and fine resolutions store local
geometric features, and a small shared decoder MLP turns trilinearly
interpolated features into occupancy and color. Because each
observation only updates the small subset of grid cells visible from
the current camera pose, the system avoids the global forgetting of
iMAP and scales to multi-room indoor environments while keeping runtime
roughly constant in scene size. Pre-trained geometric priors on the
decoder MLPs let the model fill in unobserved regions plausibly,
yielding completed reconstructions even from sparse views.

The mapping and tracking threads are decoupled and run alternately:
mapping fixes the camera pose and updates the scene grids on a sliding
window of keyframes; tracking fixes the scene and refines the latest
camera pose by minimizing the same RGB-D photometric and geometric
losses. On five challenging datasets including Replica, ScanNet, and
TUM-RGBD the system achieves competitive mapping and tracking accuracy
versus iMAP and classical TSDF-fusion baselines, while producing
significantly more detailed reconstructions on large scenes.

NICE-SLAM became the reference architecture for the wave of neural-
implicit SLAM follow-ups (Vox-Fusion, Co-SLAM, Point-SLAM) and is the
counterpart to DROID-SLAM (Teed and Deng, 2021) within this corpus —
both attack online SLAM with neural representations but from opposite
ends of the explicit-implicit spectrum.
