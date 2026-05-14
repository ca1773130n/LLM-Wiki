---
type: OpenQuestion
title: "How robust is multi-view consistency under fast camera motion?"
sub_topics: [3D Gaussian Splatting, Visual SLAM and MVS]
papers_surfaced_in:
  - arxiv-2308-04079
  - arxiv-2108-10869
  - arxiv-2312-06741
  - arxiv-2311-11700
status: open
asked: 2026-04-30
---

# How robust is multi-view consistency under fast camera motion?

[3D Gaussian Splatting](../../papers/arxiv-2308-04079/paper.md) and its SLAM
descendants assume reasonably smooth camera trajectories. The
[base 3DGS paper](../../papers/arxiv-2308-04079/paper.md) reports its
30+ FPS results on Mip-NeRF 360 captures, where image overlap is high and
motion is essentially quasi-static. The capture protocol in the Mip-NeRF 360
dataset is a tripod-paced orbit; nothing in the published results addresses
what the representation does when the camera moves fast, accumulates motion
blur, or covers a scene with sub-second pans.

The question becomes pointed once you push splatting into the SLAM regime.
[GS-SLAM](../../papers/arxiv-2311-11700/paper.md) and
[Gaussian Splatting SLAM / MonoGS](../../papers/arxiv-2312-06741/paper.md)
both report tracking accuracy on the Replica and TUM-RGBD benchmarks — but
those benchmarks have well-behaved trajectories. Compare against
[DROID-SLAM](../../papers/arxiv-2108-10869/paper.md) (Teed & Deng, 2021)
on EuRoC or TartanAir, where aggressive motion is part of the protocol and
deep BA on learned features is the only thing keeping the tracker locked
on. The splatting-SLAM systems haven't published numbers on those harder
benchmarks, and the few qualitative results suggest the photometric loss
struggles when the same Gaussian is seen at radically different scale and
exposure across adjacent frames.

The mechanism is plausible. A 3D Gaussian's anisotropic covariance is
optimised to match a particular *projected* footprint in screen space.
Fast motion changes that footprint between consecutive frames; motion blur
spreads radiance across pixels that weren't part of the primitive's
original support. The cumulative effect is that the densification schedule
clones primitives to cover the blur, which then have to be pruned when the
camera slows down. That dynamic is exactly the kind of thing that the
[revising-densification](../../papers/arxiv-2404-06109/paper.md) line has
started to question even in the static case.

What would resolve this: a benchmark that pairs (a) a high-frame-rate
capture with known ground-truth poses, (b) a deliberately fast trajectory
(sub-second 360° pans, hand-held running motion), and (c) a head-to-head
comparison across DROID-SLAM, MonoGS, GS-SLAM, and a NICE-SLAM baseline,
on both trajectory accuracy and reconstruction quality. The corpus
currently has none of those numbers in any single paper. Until that exists,
"splatting SLAM has overtaken classical SLAM" is the kind of claim that
only holds inside the easy half of the operating envelope.
