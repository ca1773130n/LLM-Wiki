---
type: Paper
arxiv: "2311.12775"
arxiv_url: https://arxiv.org/abs/2311.12775
title: "SuGaR: Surface-Aligned Gaussian Splatting for Efficient 3D Mesh Reconstruction and High-Quality Mesh Rendering"
authors:
  - "Antoine Guédon"
  - "Vincent Lepetit"
date: 2023-11-21
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: Anttwo/SuGaR
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# SuGaR: Surface-Aligned Gaussian Splatting for Efficient 3D Mesh Reconstruction and High-Quality Mesh Rendering

Guédon and Lepetit tackle a practical gap in 3D GaussianSplatting: while
3DGS renders well, its optimised primitive cloud is unstructured and
extracting a mesh from it is not straightforward. Marching Cubes, the
default for Neural SDFs, does not apply directly because Gaussians do not
implicitly define a level set. SuGaR closes this gap with a regularisation
term that encourages Gaussians to align with the underlying scene surface
and a downstream mesh extraction procedure tailored to that alignment.

The regulariser penalises Gaussians whose elongation deviates from the
local tangent plane suggested by their neighbours, biasing the
optimisation toward thin, surface-conforming primitives. Once trained, the
authors run Poisson reconstruction on the oriented Gaussian centres to
produce a clean, watertight triangle mesh in minutes. Poisson
reconstruction scales gracefully and preserves detail better than
Marching Cubes applied to noisy implicit fields, which is the standard
fallback for NeRF-style methods.

A final, optional refinement stage binds Gaussians to the surface of the
extracted mesh, parameterising each primitive by a barycentric coordinate
on a face. The mesh and the bound Gaussians are then jointly optimised
through the splatting renderer, so the mesh provides edit handles while
the Gaussians provide rendering quality. This enables sculpting, rigging,
animation, and relighting through conventional graphics tools acting on
the mesh, with the Gaussians automatically following along.

SuGaR sits alongside 2D Gaussian Splatting as one of the two main lines
of work on extracting accurate geometry from a Gaussian field, and the
released code is a common reference for editable Gaussian assets.
