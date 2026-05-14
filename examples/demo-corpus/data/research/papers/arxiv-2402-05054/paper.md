---
type: Paper
arxiv: "2402.05054"
arxiv_url: https://arxiv.org/abs/2402.05054
title: "LGM: Large Multi-View Gaussian Model for High-Resolution 3D Content Creation"
authors:
  - "Jiaxiang Tang"
  - "Zhaoxi Chen"
  - "Xiaokang Chen"
  - "Tengfei Wang"
  - "Gang Zeng"
  - "Ziwei Liu"
date: 2024-02-07
sub_topic: Generative 3D Representations
methods: [Diffusion, FeedForward]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: 3DTopia/LGM
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# LGM: Large Multi-View Gaussian Model for High-Resolution 3D Content Creation

Tang et al. propose the Large Multi-View Gaussian Model (LGM), a
FeedForward 3D generator that produces high-resolution 3D content from
either a text prompt or a single input image. By the time of writing, both
optimisation-based generators (DreamFusion, ProlificDreamer, Magic123,
DreamGaussian) and feed-forward NeRF-style generators (LRM, Instant3D,
TripoSR) had matured, but the latter group's training-time compute scaled
poorly with output resolution because predicting an entire NeRF or
implicit field at high resolution is memory-heavy. LGM addresses the
resolution bottleneck by changing the 3D representation.

The pipeline factorises 3D generation into two stages. A multi-view
Diffusion model first produces a small set of consistent views of the
target object from the prompt or input image. An asymmetric U-Net then
operates on the multi-view image stack and predicts per-pixel Gaussian
features that, fused across views via differentiable rendering, form the
final 3D Gaussian field. Two design choices make this practical at high
resolution: the multi-view Gaussian features are predicted in image space
rather than as an abstract volumetric grid, which keeps memory cost
linear in pixel count; and the U-Net's asymmetry allows the decoder to
spend more compute at higher resolutions without inflating the encoder.

End to end, LGM generates 3D content at 512-pixel training resolution
within five seconds of inference, a resolution-throughput combination
that prior feed-forward methods of comparable speed could not match. The
paper is a key data point in the shift from implicit to explicit
Gaussian representations for amortised 3D generation, and sits alongside
AGG, MVSplat, and pixelSplat in the Gaussian-prediction line of work.
