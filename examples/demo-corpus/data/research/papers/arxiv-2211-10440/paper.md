---
type: Paper
arxiv: "2211.10440"
arxiv_url: https://arxiv.org/abs/2211.10440
title: "Magic3D: High-Resolution Text-to-3D Content Creation"
authors:
  - "Chen-Hsuan Lin"
  - "Jun Gao"
  - "Luming Tang"
  - "Towaki Takikawa"
  - "Xiaohui Zeng"
  - "Xun Huang"
  - "Karsten Kreis"
  - "Sanja Fidler"
  - "Ming-Yu Liu"
  - "Tsung-Yi Lin"
date: 2022-11-18
sub_topic: Diffusion-based 3D Generation
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RadianceField, Diffusion, HashEncoding, TextTo3D]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# Magic3D: High-Resolution Text-to-3D Content Creation

Lin et al. present Magic3D, a follow-up to DreamFusion (Poole et al.,
2022) that addresses two limitations of the original Score Distillation
Sampling pipeline: it is slow (1-2 hours per prompt) and its
supervision happens at low spatial resolution because the diffusion
model used as a prior operates at low resolution. Both limitations
prevent the production-quality, high-resolution geometry that
downstream creative applications need.

Magic3D introduces a two-stage coarse-to-fine pipeline. Stage one
inherits DreamFusion's SDS objective but replaces the slow vanilla NeRF
with a hash-grid-accelerated radiance field built on Instant-NGP
(Müller et al., 2022), letting the coarse stage converge to a plausible
3D shape in minutes. Stage two extracts a triangle mesh from the coarse
NeRF via marching cubes, re-parameterizes the scene as a textured mesh
with deformable vertex positions, and continues SDS optimization
against a high-resolution latent diffusion model rendered through a
differentiable rasterizer. The rasterizer is fast enough to render at
the latent diffusion model's full operating resolution, providing
substantially crisper supervision than the original implicit-volume
renderer.

End-to-end, Magic3D produces a high-quality textured 3D mesh in roughly
40 minutes — about 2x faster than DreamFusion despite operating at
higher resolution — and a human user study reports 61.7% preference for
its outputs over DreamFusion. The mesh-based stage two also enables
image-conditioned generation, where a reference image steers texture
and style while the prompt steers content.

Magic3D established the coarse-to-fine NeRF-then-mesh recipe that
recurs throughout the subsequent text-to-3D literature and is the
direct ancestor of higher-fidelity methods that combine SDS with
explicit Gaussian-Splatting or mesh-based renderers.
