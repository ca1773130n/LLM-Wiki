---
type: Paper
arxiv: "2105.06468"
arxiv_url: https://arxiv.org/abs/2105.06468
title: "Dynamic View Synthesis from Dynamic Monocular Video"
authors:
  - "Chen Gao"
  - "Ayush Saraf"
  - "Johannes Kopf"
  - "Jia-Bin Huang"
date: 2021-05-13
sub_topic: Dynamic and 4D Reconstruction
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RadianceField, NeuralImplicitSurface, NovelViewSynthesis]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# Dynamic View Synthesis from Dynamic Monocular Video

Gao et al. tackle space-time novel view synthesis from a single
monocular video of a dynamic scene — a setting in which conventional
NeRF (Mildenhall et al., 2020) fails because there are not enough
simultaneous viewpoints to disambiguate motion from parallax. The
method represents the scene as a pair of cooperating neural radiance
fields: a static NeRF that captures time-invariant geometry and
appearance, and a dynamic NeRF that is additionally conditioned on a
time embedding and captures the time-varying components.

At each query point the renderer composites contributions from the
static and dynamic fields using an unsupervised blending weight, also
predicted by the dynamic network. This decomposition is important
because in a monocular setting most of any given frame is static
background; forcing the entire scene through a 4D MLP wastes capacity
and over-smooths the static regions. The decomposition lets the static
NeRF benefit from multi-frame parallax while the dynamic NeRF is
constrained only on regions where motion actually occurs.

Because the problem admits infinitely many solutions that explain the
input video, the authors add a battery of regularizers to bias the
optimization toward a physically plausible reconstruction: 3D scene
flow consistency between adjacent frames, a depth-order constraint
derived from monocular depth predictions, and a 2D optical-flow loss
that ties dynamic-field motion to off-the-shelf flow estimates.

Quantitative results on casually captured monocular videos demonstrate
plausible space-time interpolation, and the work seeded a wave of
follow-ups including DyNeRF, NSFF, and HyperNeRF (Park et al., 2021)
which is also represented in this corpus. The static/dynamic split it
introduces remains the standard architectural recipe for monocular
dynamic radiance fields.
