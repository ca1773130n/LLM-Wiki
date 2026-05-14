---
type: Paper
arxiv: "2403.16292"
arxiv_url: https://arxiv.org/abs/2403.16292
title: "latentSplat: Autoencoding Variational Gaussians for Fast Generalizable 3D Reconstruction"
authors:
  - "Christopher Wewer"
  - "Kevin Raj"
  - "Eddy Ilg"
  - "Bernt Schiele"
  - "Jan Eric Lenssen"
date: 2024-03-24
sub_topic: 3D Gaussian Splatting
methods: [GaussianSplatting, Variational]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
---

# latentSplat: Autoencoding Variational Gaussians for Fast Generalizable 3D Reconstruction

Wewer et al. introduce latentSplat, a generalisable 3D reconstruction
method that fuses regression-based and generative paradigms by predicting
Variational 3D Gaussians in a latent space. Regression-based feed-forward
models (e.g. pixelSplat, MVSplat) reconstruct cleanly but interpolate
poorly under large view changes, while generative methods produce richer
extrapolations but are usually slow or limited to small scenes. latentSplat
keeps the inference speed of the regression-based line while inheriting
the extrapolation quality of generative decoders.

The core representation is a set of 3D feature Gaussians whose attributes
encode means and variances in a learned latent space rather than raw
colour. From this distribution, specific sample instances can be drawn,
splatted to the image plane via the standard differentiable rasteriser,
and decoded into pixels by a lightweight 2D generative decoder. The
variational structure means that uncertain regions — where the input
views are weak or absent — naturally pull samples toward a generative
prior learned from real video data, rather than collapsing to a single
underconstrained guess as a deterministic regressor would.

Training relies entirely on readily available real video data without
explicit 3D supervision, with the 2D decoder providing the generative
inductive bias and the multi-view consistency loss tying samples back to
the input frames. Experiments show that latentSplat outperforms previous
generalisable methods in reconstruction quality and in cross-dataset
behaviour while remaining fast and scalable to high-resolution data. The
paper is a useful counterpoint to the deterministic-prediction line of
feed-forward Gaussian work; its variational treatment foreshadows later
attempts to bring Diffusion-style sampling to feed-forward 3D
reconstruction.
