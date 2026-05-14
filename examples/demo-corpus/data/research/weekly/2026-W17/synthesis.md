---
type: Synthesis
period: weekly
iso_week: 2026-W17
covers_daily:
  - daily/2026-04-20
  - daily/2026-04-25
  - daily/2026-04-30
papers_anchored:
  - arxiv-2308-04079
  - arxiv-2311-12775
  - arxiv-2403-17888
  - arxiv-2312-00109
  - arxiv-2106-10689
  - arxiv-2106-12052
  - arxiv-2206-00665
  - arxiv-2311-11700
  - arxiv-2312-06741
  - arxiv-2403-14627
  - arxiv-2403-16292
  - arxiv-2108-10869
  - arxiv-2112-12130
  - arxiv-2404-06109
trend: "Gaussian Splatting is absorbing the implicit-surface and SLAM lines"
sub_topics: [3D Gaussian Splatting, Mesh and Surface Reconstruction, Visual SLAM and MVS]
---

# Weekly synthesis — 2026-W17

The thread running through this week's reading: 3D Gaussian Splatting is
no longer a standalone view-synthesis method. It's swallowing the two
adjacent sub-fields — implicit-surface reconstruction and visual SLAM —
that the NeRF era had treated as separate problems. Three years after
[3DGS](../../papers/arxiv-2308-04079/paper.md), the explicit-primitive
representation is doing most of what the implicit-field representation
used to.

## The surface absorption

The 2021 surface trilogy
([UNISURF](../../papers/arxiv-2104-10078/paper.md),
[NeuS](../../papers/arxiv-2106-10689/paper.md),
[VolSDF](../../papers/arxiv-2106-12052/paper.md)) settled on a
particular design: represent geometry as a signed distance function,
render it via volume rendering, train per-scene from photometric loss.
[MonoSDF](../../papers/arxiv-2206-00665/paper.md) added monocular cues
to make the training tractable on fewer views.

Two splatting papers from this week argue that you don't need any of
that machinery to get a mesh.
[SuGaR](../../papers/arxiv-2311-12775/paper.md) (Guédon et al., 2023)
regularises 3D Gaussians toward a manifold and then runs Poisson surface
reconstruction on the densely-sampled near-surface points.
[2D Gaussian Splatting](../../papers/arxiv-2403-17888/paper.md) (Huang
et al., 2024) goes further and collapses each primitive to a view-consistent
oriented disk, sidestepping the depth ambiguity that 3D Gaussians have when
you ask for geometry instead of radiance. The "surface story" for splatting
is no longer "bolt an SDF onto it" — it's "constrain the primitives to
behave like a surface in the first place".

This isn't strictly better than NeuS-line methods. The implicit-surface
reconstructions are still sharper on objects with thin structures and
self-occlusion. But splatting trains in minutes where NeuS takes hours,
and that ratio is what is winning over downstream users.

## The SLAM absorption

The neural-SLAM line — starting with
[NICE-SLAM](../../papers/arxiv-2112-12130/paper.md) (Zhu et al., 2021)
and continuing through [Point-SLAM](../../papers/arxiv-2304-04278/paper.md)
and [Co-SLAM](../../papers/arxiv-2304-14377/paper.md) — was built around
implicit feature grids or point-cloud feature stores, with NeRF-style
volume rendering as the photometric supervision signal. Tracking ran as
joint optimisation of pose and the implicit field. Quality was good;
speed never quite was.

[GS-SLAM](../../papers/arxiv-2311-11700/paper.md) and
[Gaussian Splatting SLAM / MonoGS](../../papers/arxiv-2312-06741/paper.md),
both from late 2023, do the obvious substitution: same online keyframe
management, same pose-and-map joint optimisation, but the map is now an
ever-growing pile of 3D Gaussians rasterised at frame rate. MonoGS
reports the highest-fidelity photometric reconstructions of any monocular
SLAM system in this corpus. Notably the classical-geometry baseline —
[DROID-SLAM](../../papers/arxiv-2108-10869/paper.md) — is still the
tracking-accuracy reference, because deep BA on learned features remains
the most robust pose engine. The Gaussian Splatting SLAM systems are
beating DROID-SLAM on the *map* but not on the *trajectory*.

This is the open question that runs across both absorptions: how do these
systems hold up under capture conditions that the splatting paradigm
implicitly assumes are benign? See
[multi-view-consistency](../questions/multi-view-consistency.md) for the
detailed version.

## Density, generalisation, and the sparse-view frontier

Two more arrivals worth flagging.
[Revising Densification](../../papers/arxiv-2404-06109/paper.md) (Bulò
et al., 2024) is a corrective on the original 3DGS recipe — the clone /
split / prune schedule was undertuned, and a more principled treatment
of the split criterion produces meaningfully better fidelity at the same
primitive count. This is the kind of paper the corpus has too few of:
nothing fancy, just careful re-examination. It complements
[Scaffold-GS](../../papers/arxiv-2312-00109/paper.md)'s argument that
the "free Gaussian soup" wastes capacity in low-frequency regions.

On the generalisation front,
[MVSplat](../../papers/arxiv-2403-14627/paper.md) (Chen et al., 2024)
and [latentSplat](../../papers/arxiv-2403-16292/paper.md) (Wewer et al.,
2024) both feed-forward predict Gaussian parameters from sparse-view
inputs, eliminating per-scene optimisation entirely. Splatting plus
learned priors — the next phase that next week's reading will pick up
in earnest.

## What to read next

Two threads to chase into W18: (1) the diffusion-into-3D line that
[DreamGaussian](../../papers/arxiv-2309-16653/paper.md) bridged into the
splatting representation, and (2) the large reconstruction model line
([LRM](../../papers/arxiv-2311-04400/paper.md) and successors) that asks
whether per-scene optimisation is necessary at all.
