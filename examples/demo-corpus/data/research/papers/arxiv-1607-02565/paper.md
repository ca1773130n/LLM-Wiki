---
type: Paper
arxiv: "1607.02565"
arxiv_url: https://arxiv.org/abs/1607.02565
title: "Direct Sparse Odometry"
authors:
  - "Jakob Engel"
  - "Vladlen Koltun"
  - "Daniel Cremers"
date: 2016-07-09
sub_topic: Visual SLAM and MVS
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RealTimeRendering]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# Direct Sparse Odometry

Engel et al. present Direct Sparse Odometry (DSO), a visual odometry system
that merges the direct image-formation model of LSD-SLAM with the sparse
keyframe windowed optimization of indirect feature-based pipelines. The
formulation minimizes a photometric error directly over pixel intensities
rather than reprojected feature locations, and jointly optimizes inverse
depth, camera intrinsics, and a full photometric calibration covering
exposure time, lens vignetting, and the camera response function.

In contrast to dense direct methods such as DTAM, DSO drops the
total-variation smoothness prior on depth and instead samples a fixed
budget of pixels uniformly across regions of non-zero intensity gradient.
The sampling deliberately spans edges, weakly textured walls, and high-
gradient interiors, which lets the optimizer extract signal from surfaces
that classical keypoint pipelines would discard. Joint windowed bundle
adjustment over keyframes refines pose and inverse-depth simultaneously,
keeping the operation real-time on a single CPU.

The authors evaluate on three datasets — the TUM-monoVO benchmark, the EuRoC
MAV sequences, and an in-house high-frame-rate corpus — totaling several
hours of video. DSO outperforms both ORB-SLAM-style indirect baselines and
prior direct methods (LSD-SLAM) on tracking accuracy and robustness,
particularly under rolling shutter, motion blur, and exposure changes
where photometric calibration is decisive.

DSO became a reference baseline for subsequent direct monocular systems
and was extended in follow-up work to stereo, RGB-D, and inertial inputs.
It is also a recurring comparison point for learned SLAM systems such as
DROID-SLAM and DeepV2D, which inherit the dense-photometric residual but
replace the hand-engineered front end with a recurrent network. Within
the LLM-Wiki demo corpus, DSO sits at the classical end of the
SLAM-to-radiance-field continuum: explicit residuals, sparse geometry,
real-time on commodity hardware.
