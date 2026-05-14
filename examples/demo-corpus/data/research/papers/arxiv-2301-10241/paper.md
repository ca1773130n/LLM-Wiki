---
type: Paper
arxiv: "2301.10241"
arxiv_url: https://arxiv.org/abs/2301.10241
title: "K-Planes: Explicit Radiance Fields in Space, Time, and Appearance"
authors:
  - "Sara Fridovich-Keil"
  - "Giacomo Meanti"
  - "Frederik Warburg"
  - "Benjamin Recht"
  - "Angjoo Kanazawa"
date: 2023-01-24
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RadianceField]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: sarafridov/K-Planes
---

# K-Planes: Explicit Radiance Fields in Space, Time, and Appearance

Fridovich-Keil et al. introduce K-Planes, a factorized explicit
representation for radiance fields that generalizes seamlessly from
static 3D scenes to dynamic 4D scenes and to scenes with varying
appearance. The construction generalizes the planar factorization of
TensoRF and its predecessors: a d-dimensional scene is represented by
"d choose 2" feature planes, one per pair of axes. For a static 3D
scene that is three planes (xy, xz, yz); for a dynamic 4D scene it is
six planes (xy, xz, yz, xt, yt, zt).

At a query point, features are bilinearly sampled from each plane and
combined by element-wise multiplication into a single feature vector,
which is then decoded into density and color. The decoder can be a
small MLP, as in prior factorized methods, but the authors show that a
linear decoder with a learned global color basis achieves comparable
quality, making the entire pipeline a white-box that is easy to inspect
and regularize.

The factorization makes adding dimension-specific priors mechanically
simple. Temporal smoothness becomes a TV penalty on the time-axis
planes; multi-scale spatial detail becomes a multi-resolution stack of
spatial planes; static-dynamic decomposition is induced by initializing
the time-involving planes to the identity, so the model represents only
genuinely time-varying content in those planes. The result is a roughly
1000x memory compression versus a dense 4D grid.

K-Planes outperforms or matches state-of-the-art static and dynamic
radiance-field methods across synthetic and real benchmarks while
training quickly in pure PyTorch — no custom CUDA. Within this corpus
it pairs with Plenoxels (Yu et al., 2021) and Instant-NGP (Müller et
al., 2022) as part of the explicit-representation lineage, and with
Nerfies/HyperNeRF as part of the dynamic-radiance-field lineage.
