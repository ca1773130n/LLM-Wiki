---
type: Paper
arxiv: "2106.13228"
arxiv_url: https://arxiv.org/abs/2106.13228
title: "HyperNeRF: A Higher-Dimensional Representation for Topologically Varying Neural Radiance Fields"
authors:
  - "Keunhong Park"
  - "Utkarsh Sinha"
  - "Peter Hedman"
  - "Jonathan T. Barron"
  - "Sofien Bouaziz"
  - "Dan B Goldman"
  - "Ricardo Martin-Brualla"
  - "Steven M. Seitz"
date: 2021-06-24
sub_topic: Dynamic and 4D Reconstruction
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RadianceField, DeformationField, NovelViewSynthesis]
datasets: []
metrics: [LPIPS]
---

# HyperNeRF: A Higher-Dimensional Representation for Topologically Varying Neural Radiance Fields

Park et al. extend their earlier Nerfies (Park et al., 2020) deformable
radiance-field model to scenes with topological change — an opening
mouth, a fist that unclenches, a knife slicing fruit. The Nerfies-style
deformation field maps each observed point into a single canonical
template; this works for elastic deformation but fails when the topology
itself changes, because a continuous deformation field cannot represent
a discontinuity (an opening or closing of a connected component).

HyperNeRF resolves the discontinuity by lifting the canonical template
into a higher-dimensional ambient space. Each input frame is associated
with an ambient coordinate; the radiance field is then defined over the
joint (3D position, ambient code) space, and the per-frame appearance is
recovered by slicing the higher-dimensional field at the frame's ambient
location. The construction is inspired by level-set methods in classical
geometry, where evolving surfaces are modeled as slices of a higher-
dimensional implicit function.

The deformation field is retained from Nerfies — the network first warps
observed points into the canonical 3D coordinates, then performs the
ambient slice — and the elastic regularization and coarse-to-fine
positional encoding of that earlier work are reused. On a benchmark of
casually captured topology-changing clips, HyperNeRF reduces LPIPS error
by 4.1% for moment-interpolation and 8.6% for novel-view synthesis
compared to Nerfies, and renders cleanly across topology transitions.

The higher-dimensional canonical-space construction has been adopted by
subsequent monocular dynamic methods that struggle with topology, and
the Nerfies / HyperNeRF pair remains the canonical pre-Gaussian
reference for deformable radiance fields. Both works appear together in
the dynamic-3D portion of the corpus mapped here.
