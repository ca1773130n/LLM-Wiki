---
type: Paper
arxiv: "2106.12052"
arxiv_url: https://arxiv.org/abs/2106.12052
title: "Volume Rendering of Neural Implicit Surfaces"
authors:
  - "Lior Yariv"
  - "Jiatao Gu"
  - "Yoni Kasten"
  - "Yaron Lipman"
date: 2021-06-22
sub_topic: Mesh and Surface Reconstruction
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [VolumeRendering, NeuralImplicitSurface]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# Volume Rendering of Neural Implicit Surfaces

Yariv et al. introduce VolSDF, a volume-rendering framework in which
the volume density is derived from a signed distance function rather
than predicted by an independent MLP head as in NeRF (Mildenhall et al.,
2020). Concretely, the density is the Laplace cumulative distribution
function applied to the negative SDF, producing a thin shell of high
density concentrated around the zero level set whose sharpness is
controlled by a learnable bandwidth parameter.

The formulation has three consequences. First, the geometry inherits the
inductive bias of an SDF — smooth, well-defined surfaces with usable
normals — instead of NeRF's noisy density cloud. Second, the authors
derive an explicit bound on the opacity-approximation error along a ray
in terms of the bandwidth, enabling an importance sampler that places
samples where they matter without redundant evaluations near empty
space. Third, because shape (the SDF) and appearance (the radiance MLP)
are now disentangled in the representation, scenes can be composed by
swapping the geometry of one capture with the appearance of another.

On standard multi-view benchmarks VolSDF outperforms IDR (which requires
masks) and matches or exceeds NeRF on view synthesis quality while
producing reconstructions with substantially less geometric noise. The
work builds on Implicit Geometric Regularization (Gropp et al., 2020),
whose Eikonal loss is used to keep the SDF metric, and was published
within days of NeuS (Wang et al., 2021), which solves the same problem
with a different opacity construction.

VolSDF and NeuS are the foundational references for downstream SDF-from-
multi-view methods in this corpus: MonoSDF, NeuralWarp, Voxurf, and the
Gaussian-Splatting surface variants all inherit the Laplace-CDF density
or one of its close cousins.
