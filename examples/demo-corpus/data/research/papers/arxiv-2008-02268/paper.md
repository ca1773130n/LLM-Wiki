---
type: Paper
arxiv: "2008.02268"
arxiv_url: https://arxiv.org/abs/2008.02268
title: "NeRF in the Wild: Neural Radiance Fields for Unconstrained Photo Collections"
authors:
  - "Ricardo Martin-Brualla"
  - "Noha Radwan"
  - "Mehdi S. M. Sajjadi"
  - "Jonathan T. Barron"
  - "Alexey Dosovitskiy"
  - "Daniel Duckworth"
date: 2020-08-05
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RadianceField]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# NeRF in the Wild: Neural Radiance Fields for Unconstrained Photo Collections

Martin-Brualla et al. extend NeRF (Mildenhall et al., 2020) to the
"in-the-wild" setting: tourist photo collections of famous landmarks
where images differ in time of day, weather, exposure, and frequently
contain transient occluders such as people and vehicles. Vanilla NeRF
assumes a static scene with consistent appearance, and produces severe
artifacts under either kind of variation.

NeRF-W introduces two extensions. A per-image appearance embedding is
concatenated to the radiance MLP input, letting the network model
photometric variation across captures as a low-dimensional latent code
while keeping geometry shared. A separate transient head, also conditioned
on a per-image embedding, predicts a transient density and color along
with an uncertainty field; the loss is downweighted in pixels where the
transient head asserts high uncertainty, automatically masking out
photo-bombers, tourists, and scaffolding without per-image annotation.

The two components together let NeRF-W reconstruct landmarks such as
Trevi Fountain, the Brandenburg Gate, and Sacre Coeur from in-the-wild
Flickr image collections, producing temporally consistent free-viewpoint
renderings with controllable illumination conditions. Compared to NRW and
Neural Rerendering in the Wild, NeRF-W substantially improves PSNR and
perceptual metrics on the Phototourism benchmark.

The appearance-embedding trick became standard in subsequent radiance-
field methods that needed to absorb capture-time variation, including
Block-NeRF for city-scale scenes and Mega-NeRF for aerial captures. The
transient-uncertainty idea reappears in robust NeRF training, where it
is used to ignore other forms of inconsistent observation. Within this
corpus, NeRF-W is the first work to push NeRF beyond the controlled
laboratory capture into raw consumer imagery.
