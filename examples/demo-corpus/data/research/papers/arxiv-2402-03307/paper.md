---
type: Paper
arxiv: "2402.03307"
arxiv_url: https://arxiv.org/abs/2402.03307
title: "4D-Rotor Gaussian Splatting: Towards Efficient Novel View Synthesis for Dynamic Scenes"
authors:
  - "Yuanxing Duan"
  - "Fangyin Wei"
  - "Qiyu Dai"
  - "Yuhang He"
  - "Wenzheng Chen"
  - "Baoquan Chen"
date: 2024-02-05
sub_topic: Dynamic and 4D Reconstruction
methods: [GaussianSplatting, DeformationField, RotorRepresentation, NovelViewSynthesis, RealTimeRendering]
datasets: []
metrics: [FPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# 4D-Rotor Gaussian Splatting: Towards Efficient Novel View Synthesis for Dynamic Scenes

Duan et al. introduce 4D-Rotor GaussianSplatting (4DRotorGS), a dynamic
extension of 3D Gaussian Splatting that represents a time-varying scene
with anisotropic 4D Gaussians defined over the joint XYZT domain. Prior
dynamic NeRF and dynamic-Gaussian work generally encodes motion via a
canonical 3D representation plus an implicit or explicit DeformationField
that maps each timestamp back to canonical coordinates. Such canonical
formulations struggle with abrupt motions, topological changes, and
emerging or disappearing content, because the deformation network must
absorb discontinuities that violate its smoothness assumptions.

4DRotorGS avoids the canonical-plus-deformation factorisation entirely.
Each primitive is a full 4D Gaussian with an orientation parameterised by
a RotorRepresentation drawn from geometric algebra, which generalises the
quaternion approach used for 3D rotations to four dimensions while
remaining numerically stable. At any rendering time t the authors take a
temporal slice through the 4D field, producing a set of effective 3D
Gaussians for that frame that can be splatted with the standard
differentiable rasteriser. This temporal slicing naturally handles abrupt
motion: parts of the scene that appear or disappear are represented by
4D Gaussians with narrow temporal extent, rather than by a smooth
deformation of a persistent canonical primitive.

The authors implement temporal slicing and splatting in a CUDA pipeline
optimised alongside the existing 3DGS kernels, achieving 277 FPS at the
benchmark resolution on an RTX 3090 and 583 FPS on an RTX 4090.
RealTimeRendering performance and reconstruction quality are competitive
with or better than prior dynamic methods, including the contemporary
4D Gaussian Splatting (4D-GS) line of work that uses a HexPlane-style
deformation field instead.
