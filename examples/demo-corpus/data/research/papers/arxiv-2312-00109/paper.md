---
type: Paper
arxiv: "2312.00109"
arxiv_url: https://arxiv.org/abs/2312.00109
title: "Scaffold-GS: Structured 3D Gaussians for View-Adaptive Rendering"
authors:
  - "Tao Lu"
  - "Mulin Yu"
  - "Linning Xu"
  - "Yuanbo Xiangli"
  - "Limin Wang"
  - "Dahua Lin"
  - "Bo Dai"
date: 2023-11-30
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (Tesserae demo prose)"
---

# Scaffold-GS: Structured 3D Gaussians for View-Adaptive Rendering

Lu et al. address one of the more practical failure modes of vanilla
3D GaussianSplatting: the optimiser tends to spawn many redundant primitives
that overfit individual training views, ignoring the underlying scene
geometry. This bloat makes the representation brittle to large viewpoint
changes, to texture-less regions, and to view-dependent lighting effects,
because there is no shared structure across views that the renderer can lean
on.

Scaffold-GS replaces the unstructured Gaussian soup with a two-tier
representation. A sparse set of anchor points — placed near scene geometry —
forms the scaffold. Each anchor owns a small bundle of neural Gaussians
whose attributes (position offset, opacity, colour, scale) are predicted
on-the-fly by a shared MLP that receives the viewing direction and the
distance from camera to anchor. This view-conditioned prediction lets the
same anchor produce different splat patterns from different angles,
naturally handling view-dependent appearance with far fewer primitives than
a fixed-attribute baseline.

The anchor set itself is grown and pruned during training by a procedure
that scores how much each anchor contributes to rendering quality, growing
into under-covered regions and pruning anchors whose neural Gaussians never
fire. The net effect is a substantial reduction in primitive count at
equal rendering quality, plus improved robustness on level-of-detail and
view-extrapolation scenarios. Scaffold-GS has become a common starting
point for follow-on work on structured Gaussian representations, including
later extensions that vary anchor density with scene complexity and that
adapt the per-anchor MLP for editing and compression.
