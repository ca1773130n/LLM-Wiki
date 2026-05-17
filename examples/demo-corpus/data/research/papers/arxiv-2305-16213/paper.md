---
type: Paper
arxiv: "2305.16213"
arxiv_url: https://arxiv.org/abs/2305.16213
title: "ProlificDreamer: High-Fidelity and Diverse Text-to-3D Generation with Variational Score Distillation"
authors:
  - "Zhengyi Wang"
  - "Cheng Lu"
  - "Yikai Wang"
  - "Fan Bao"
  - "Chongxuan Li"
  - "Hang Su"
  - "Jun Zhu"
date: 2023-05-25
sub_topic: Diffusion-based 3D Generation
methods: [RadianceField, Diffusion, ScoreDistillation, TextTo3D, Variational]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
license: "CC-BY-4.0 (Tesserae demo prose)"
---

# ProlificDreamer: High-Fidelity and Diverse Text-to-3D Generation with Variational Score Distillation

Wang et al. revisit Score Distillation Sampling (SDS), the workhorse
behind DreamFusion and its successors, and identify the source of its
well-known pathologies: over-saturation, over-smoothing, and a collapse to
low-diversity modes. The diagnosis is that SDS treats the 3D parameters
as a single point estimate optimised against a frozen text-to-image
Diffusion prior. The authors reformulate the problem as posterior
inference over a distribution of 3D scenes and derive Variational Score
Distillation (VSD), a particle-based variational framework that updates a
small ensemble of 3D parameterisations using a learned "variational"
score network alongside the pretrained prior.

The authors show that SDS is recoverable as a single-particle limit of
VSD with a delta posterior and that the corresponding score is biased
toward the prior mean — explaining the saturation and mode collapse. VSD
behaves well across a wide range of classifier-free-guidance weights and,
at the standard CFG of 7.5, produces samples that are simultaneously
diverse and detailed. Companion design choices — a slow-to-fast
distillation time schedule and a careful density initialisation — give
further gains and are reusable by other TextTo3D methods.

The full pipeline, ProlificDreamer, generates 512×512 NeRF renders with
fine structure and difficult effects like smoke and translucency, and a
follow-on mesh fine-tuning stage produces editable assets. Across rendered
samples, the diversity gains are most visible on prompts where SDS would
otherwise lock onto a single canonical interpretation, demonstrating that
the saturation problem is genuinely a posterior-shape issue rather than
a hyperparameter accident. The paper has become a foundational reference
for principled score distillation; later work such as DreamGaussian and
Instant3D inherits its analysis even when substituting alternative 3D
representations.
