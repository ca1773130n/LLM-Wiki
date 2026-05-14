---
type: Paper
arxiv: "1812.04605"
arxiv_url: https://arxiv.org/abs/1812.04605
title: "DeepV2D: Video to Depth with Differentiable Structure from Motion"
authors:
  - "Zachary Teed"
  - "Jia Deng"
date: 2018-12-11
sub_topic: Visual SLAM and MVS
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [StructureFromMotion, DepthEstimation]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# DeepV2D: Video to Depth with Differentiable Structure from Motion

Teed and Deng introduce DeepV2D, a video-to-depth architecture that
embeds classical structure-from-motion as a sequence of differentiable
modules inside a deep network. The pipeline interleaves two stages: a
motion module that estimates inter-frame camera pose given current depth,
and a depth module that estimates per-pixel depth given current pose.
The two are alternated to convergence at inference time, mimicking the
iterative refinement of bundle adjustment but with all components
end-to-end trainable.

The contribution is methodological: rather than learn a black-box depth
regressor, DeepV2D unrolls the geometric structure-from-motion problem
into modules — feature extraction, plane-sweep cost volume, dense pose
optimization — that each respect epipolar constraints. Gradients flow
across both stages, so supervision on depth simultaneously trains the
pose head and vice versa. This contrasts with concurrent monocular depth
networks that ignore multi-view geometry entirely.

DeepV2D is the conceptual predecessor of DROID-SLAM by the same first
author: both rely on iteratively refining pose and depth through a
differentiable optimization layer, but DROID-SLAM generalizes the design
to full SLAM with a Dense Bundle Adjustment layer over a growing keyframe
graph. DeepV2D is the offline two-view-to-multi-view analog and
demonstrates that the differentiable-SfM pattern is sufficient for
accurate depth alone.

The code release at github.com/princeton-vl/DeepV2D became a starting
point for follow-up work on learned multi-view stereo and recurrent
optical flow (RAFT), which share the iterative refinement primitive. In
the broader 3D reconstruction landscape mapped by this corpus, DeepV2D
marks the transition from hand-engineered MVS pipelines to architectures
where the geometric solver itself is learned.
