---
type: Paper
arxiv: "2108.10869"
arxiv_url: https://arxiv.org/abs/2108.10869
title: "DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras"
authors:
  - "Zachary Teed"
  - "Jia Deng"
date: 2021-08-24
sub_topic: Visual SLAM and MVS
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [SLAM, StructureFromMotion, BundleAdjustment]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: princeton-vl/DROID-SLAM
---

# DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras

Teed and Deng introduce DROID-SLAM, a deep visual SLAM system that
replaces the hand-engineered front end of classical pipelines (ORB-SLAM,
DSO) with a recurrent neural network and embeds a differentiable Dense
Bundle Adjustment (DBA) layer at the core of the optimizer. The system
is trained end-to-end on monocular video but, at test time, transparently
ingests stereo or RGB-D streams to improve accuracy.

The architecture builds on the iterative-refinement idea introduced by
the same first author's earlier DeepV2D (Teed and Deng, 2018) and RAFT
optical-flow networks. A ConvGRU update operator inspects a 4D
correlation volume between every pair of frames in a growing co-
visibility graph and emits revisions to per-pixel depth and per-frame
camera pose. The DBA layer then solves a Gauss-Newton step that
projects these revisions onto the manifold of geometrically consistent
solutions; the entire iteration is differentiable, so the gradient of
the photometric residual flows back through the bundle-adjustment
Jacobian and supervises the update network.

The result is a SLAM system that is markedly more accurate than prior
deep approaches (e.g., DeepFactors, TANDEM, DeepFusion) and substantially
more robust than classical baselines — DROID-SLAM rarely suffers the
catastrophic tracking failures that affect ORB-SLAM and DSO on the
challenging EuRoC, TUM-RGBD, TartanAir, and ETH3D benchmarks. The same
trained model handles indoor, outdoor, and aerial sequences without
domain-specific tuning.

Code at github.com/princeton-vl/DROID-SLAM became the de-facto baseline
for deep SLAM and the front end for several radiance-field-based mapping
systems (e.g., NICE-SLAM and its successors). Within this corpus
DROID-SLAM is the modern counterpoint to Engel et al.'s Direct Sparse
Odometry.
