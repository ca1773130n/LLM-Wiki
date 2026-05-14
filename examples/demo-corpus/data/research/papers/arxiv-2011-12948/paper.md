---
type: Paper
arxiv: "2011.12948"
arxiv_url: https://arxiv.org/abs/2011.12948
title: "Nerfies: Deformable Neural Radiance Fields"
authors:
  - "Keunhong Park"
  - "Utkarsh Sinha"
  - "Jonathan T. Barron"
  - "Sofien Bouaziz"
  - "Dan B Goldman"
  - "Steven M. Seitz"
  - "Ricardo Martin-Brualla"
date: 2020-11-25
sub_topic: Dynamic and 4D Reconstruction
license: "CC-BY-4.0 (LLM-Wiki demo prose)"
methods: [RadianceField, DeformationField]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
---

# Nerfies: Deformable Neural Radiance Fields

Park et al. introduce Nerfies, the first NeRF variant that handles
non-rigidly deforming subjects captured casually with a handheld phone.
The key extension is a continuous volumetric deformation field that maps
each observed 5D coordinate into a canonical template space, where a
standard NeRF (Mildenhall et al., 2020) is fit. The radiance MLP and the
deformation MLP are optimized jointly from monocular video with no
explicit motion supervision.

Two regularizers stabilize the otherwise ill-posed optimization. A
coarse-to-fine annealing schedule on the positional-encoding frequencies
of the deformation network avoids the local minima that high-frequency
encodings induce — the optimizer first learns low-frequency, near-rigid
motion and progressively introduces fine deformation. An elastic energy
regularizer, borrowed from physical-simulation literature, penalizes
non-rigid distortion of the Jacobian, encouraging the deformation to
behave like a soft-body deformation rather than an arbitrary warp.

The authors capture training and evaluation data with a two-phone rig:
one phone records the training video while the second phone records
time-synchronized validation frames from a different viewpoint, giving
held-out novel views of an actively deforming subject. On this benchmark
Nerfies produces photorealistic free-viewpoint renderings of selfies and
expressive motions where vanilla NeRF and D-NeRF baselines blur or
hallucinate.

Nerfies established the canonical-template-plus-deformation-field
formulation that HyperNeRF (its direct follow-up by the same team) later
generalized to topologically varying scenes. The elastic regularizer and
coarse-to-fine encoding schedule recur across the dynamic-NeRF literature
in this corpus, and the "casually captured deformable capture" framing
seeded a strand of work on monocular dynamic view synthesis.
