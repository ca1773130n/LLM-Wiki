---
type: OpenQuestion
title: "Does dynamic reconstruction work at minute-scale capture in the wild?"
sub_topics: [Dynamic and 4D Reconstruction, 3D Gaussian Splatting]
papers_surfaced_in:
  - arxiv-2011-12948
  - arxiv-2106-13228
  - arxiv-2105-06468
  - arxiv-2310-08528
  - arxiv-2402-03307
  - arxiv-2301-10241
status: open
asked: 2026-05-05
---

# Does dynamic reconstruction work at minute-scale capture in the wild?

The dynamic-reconstruction line in this corpus reports almost all of its
quantitative results on short clips of a single deformable subject in
relatively controlled conditions. [Nerfies](../../papers/arxiv-2011-12948/paper.md)
(Park et al., 2020) is the canonical example: ~10–20 second selfie videos,
indoor lighting, one moving subject. [HyperNeRF](../../papers/arxiv-2106-13228/paper.md)
(Park et al., 2021) extends the deformation field to handle topological
change but still operates on the same scale of input.
[Dynamic View Synthesis from Dynamic Monocular Video](../../papers/arxiv-2105-06468/paper.md)
(Gao et al., 2021) is similar.

The 2023–2024 splatting analogues — [4D Gaussian Splatting](../../papers/arxiv-2310-08528/paper.md)
(Wu et al., 2023) and [4D-Rotor Gaussian Splatting](../../papers/arxiv-2402-03307/paper.md)
(Duan et al., 2024) — solve the rendering-cost half of the problem
convincingly. Both report real-time playback of dynamic novel views, and
both use the same explicit-primitive trick that
[3DGS](../../papers/arxiv-2308-04079/paper.md) used to displace NeRF in the
static case. But the captures they evaluate on are still short.
[K-Planes](../../papers/arxiv-2301-10241/paper.md) (Fridovich-Keil et al.,
2023) is the most aggressive on duration — its planar factorisation makes
the memory growth linear in time rather than quadratic — but its public
results are still on minutes-or-less captures.

What "in the wild" means here is concrete: a hand-held monocular phone
video, several minutes long, of a scene with multiple moving subjects and
non-trivial illumination change (a busy street, a marketplace). None of
the papers in this corpus benchmarks on that regime. The likely failure
modes are easy to enumerate: the deformation MLP's capacity is fixed at
training time; the canonical-frame assumption breaks when no single
canonical state covers the whole capture; the per-Gaussian temporal
trajectories in 4DGS-class methods grow linearly in primitive count,
which the densification schedule wasn't designed for.

What would resolve this: a benchmark dataset of multi-minute monocular
dynamic captures with calibrated ground-truth, plus a head-to-head
evaluation of K-Planes, 4DGS, 4D-Rotor-GS, HyperNeRF, and Nerfies on it.
Bonus points for ablating capture length explicitly so the failure modes
have a name. Until that exists, the field is publishing real-time 4D
rendering on captures that are short enough for the failure modes to
hide.
