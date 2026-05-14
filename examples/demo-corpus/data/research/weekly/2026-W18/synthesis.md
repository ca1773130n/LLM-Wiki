---
type: Synthesis
period: weekly
iso_week: 2026-W18
covers_daily:
  - daily/2026-04-30
  - daily/2026-05-05
papers_anchored:
  - arxiv-2209-14988
  - arxiv-2211-10440
  - arxiv-2303-11328
  - arxiv-2305-16213
  - arxiv-2306-17843
  - arxiv-2309-16653
  - arxiv-2311-13384
  - arxiv-2401-04099
  - arxiv-2402-07207
  - arxiv-2312-03203
  - arxiv-2311-04400
  - arxiv-2311-06214
  - arxiv-2402-05054
  - arxiv-2403-02151
  - arxiv-2310-08528
  - arxiv-2402-03307
  - arxiv-2106-13228
  - arxiv-2105-06468
  - arxiv-2301-10241
  - arxiv-2302-12249
trend: "Per-scene SDS distillation is being replaced by feed-forward reconstruction"
sub_topics: [Diffusion-based 3D Generation, Generative 3D Representations, Dynamic and 4D Reconstruction]
---

# Weekly synthesis — 2026-W18

The thread this week: the SDS distillation paradigm that
[DreamFusion](../../papers/arxiv-2209-14988/paper.md) launched in 2022 is
quietly being deprecated. Two replacements are competing for the slot:
splatting-native SDS variants that make distillation cheap enough to live
with, and feed-forward Large Reconstruction Models that skip per-scene
optimisation entirely.

## Where SDS got to

The SDS line is well-traced in this corpus.
[DreamFusion](../../papers/arxiv-2209-14988/paper.md) was the first paper
to backpropagate a 2D diffusion model's score into a per-scene 3D
representation; it produced cartoonish geometry and took hours per asset.
[Magic3D](../../papers/arxiv-2211-10440/paper.md) added a coarse-to-fine
schedule with a mesh-export second stage.
[Zero-1-to-3](../../papers/arxiv-2303-11328/paper.md) reconditioned a
diffusion model on camera pose, so the prior had geometric structure
rather than only appearance-level structure;
[Magic123](../../papers/arxiv-2306-17843/paper.md) combined the two priors.
[ProlificDreamer](../../papers/arxiv-2305-16213/paper.md) is the most
intellectually satisfying of the line — it reframed SDS as a variational
problem (Variational Score Distillation) and made the mode-collapse
disappear.

Then [DreamGaussian](../../papers/arxiv-2309-16653/paper.md) swapped the
backbone for 3D Gaussians, and the per-asset cost dropped from hours to
minutes. The same paradigm now applies, but cheaply.
[LucidDreamer](../../papers/arxiv-2311-13384/paper.md) is the
text-to-Gaussian-scene generalisation;
[GALA3D](../../papers/arxiv-2402-07207/paper.md) extends to layout-guided
compositional scenes;
[AGG](../../papers/arxiv-2401-04099/paper.md) is the amortised single-image
variant.

## Where it's going

The more disruptive move is feed-forward.
[LRM](../../papers/arxiv-2311-04400/paper.md) (Hong et al., 2023) trains a
giant transformer on Objaverse to produce a triplane radiance field from a
single image in ~5 seconds — no per-scene optimisation, no SDS loop.
[Instant3D](../../papers/arxiv-2311-06214/paper.md) chains a multi-view
diffusion model into an LRM to make the input less ambiguous.
[LGM](../../papers/arxiv-2402-05054/paper.md) ports the same idea onto the
splatting representation: feed-forward predict Gaussians from sparse
multi-view inputs. [TripoSR](../../papers/arxiv-2403-02151/paper.md) is the
production-quality open release in this line.

Two ways to read this: either feed-forward will absorb SDS the way
splatting absorbed the NeRF backbone, or the two will stratify by use
case — feed-forward for low-effort consumer image-to-3D, SDS-on-splats
for high-fidelity asset creation. The corpus doesn't have head-to-head
benchmarks across both regimes; that's the gap
[inference-cost-vs-fidelity](../questions/inference-cost-vs-fidelity.md)
tries to articulate.

A note on [Feature 3DGS](../../papers/arxiv-2312-03203/paper.md): the
"distil a 2D foundation feature into the 3D Gaussian primitives" trick is
orthogonal to both axes. It's worth flagging because it predicts a third
direction — splatting representations as the substrate for 3D-aware
foundation features generally, not just for view synthesis.

## The dynamic side

The other half of this week was the dynamic / 4D line.
[Nerfies](../../papers/arxiv-2011-12948/paper.md) (Park et al., 2020)
and [HyperNeRF](../../papers/arxiv-2106-13228/paper.md) (Park et al.,
2021) are the deformable-NeRF parents — per-observation warps of a
canonical field. [Dynamic View Synthesis from Dynamic Monocular Video](../../papers/arxiv-2105-06468/paper.md)
(Gao et al., 2021) is the monocular companion.
[K-Planes](../../papers/arxiv-2301-10241/paper.md) (Fridovich-Keil et al.,
2023) factorises 4D into six explicit feature planes — a tractable
alternative to a 4D MLP. [MERF](../../papers/arxiv-2302-12249/paper.md)
(Reiser et al., 2023) is the memory-efficient variant for unbounded scenes
(it's strictly static, but its tri-plane plus sparse 3D grid structure is
what K-Planes generalises to time).

[4D Gaussian Splatting](../../papers/arxiv-2310-08528/paper.md) (Wu et al.,
2023) and [4D-Rotor Gaussian Splatting](../../papers/arxiv-2402-03307/paper.md)
(Duan et al., 2024) are the splatting analogues — the same "explicit primitives,
cheap rasterisation" trade-off applied to the dynamic case. Neither paper
benchmarks at the scale or scene complexity that monocular dynamic capture
in the wild would demand. That gap is the
[dynamic-reconstruction-scale](../questions/dynamic-reconstruction-scale.md)
question.

## What to read next

Two follow-ups: (1) anything that benchmarks feed-forward (LRM/LGM/TripoSR)
against SDS-on-splats head to head on the same prompts and (2) anything
that pushes 4D Gaussian Splatting past short clips into minute-scale
dynamic capture. Neither sub-area is solved.
