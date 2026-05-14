---
type: ResearchDigest
date: 2026-04-15
period: daily
papers_covered:
  - arxiv-2103-13415
  - arxiv-2103-14024
  - arxiv-2112-05131
  - arxiv-2201-05989
  - arxiv-2111-12077
sub_topics: [Neural Radiance Fields]
---

# Daily digest — 2026-04-15

Today was the "fast NeRF" arc. After yesterday's foundations re-read, the
question was: how did the field get from hours-per-scene to minutes-per-scene
between 2021 and 2022, and which of those tricks survived the splatting era?

[Mip-NeRF](../../papers/arxiv-2103-13415/paper.md) (Barron et al., 2021)
is the aliasing-aware revision of NeRF: rays become cones, point samples
become integrated positional encodings over conical frustums. Useful on
multiscale captures. [Mip-NeRF 360](../../papers/arxiv-2111-12077/paper.md)
extends it to unbounded scenes via a non-linear contraction of space and a
proposal-network sampler. The 360 benchmark this paper introduced is still
the splatting community's default scene set.

[PlenOctrees](../../papers/arxiv-2103-14024/paper.md) (Yu et al., 2021) bakes
a trained NeRF into a sparse octree of spherical-harmonic coefficients for
real-time rendering. It traded training-time flexibility for inference speed
— a pattern Plenoxels then pushed further by skipping the MLP entirely.
[Plenoxels](../../papers/arxiv-2112-05131/paper.md) is a remarkable paper to
read in 2026 because everything it argues — "you don't need an MLP, you need
positional features and a good optimisation prior" — became conventional
wisdom. The [svox2](../../repos/sxyu-svox2/about.md) reference implementation
is still the cleanest place to read that argument as code.

The cleanest synthesis of these ideas is
[Instant-NGP](../../papers/arxiv-2201-05989/paper.md) (Müller et al., 2022):
a multiresolution hash grid plus a tiny MLP, trained from scratch in seconds
on a single GPU. The [NVlabs/instant-ngp](../../repos/nvlabs-instant-ngp/about.md)
reference codebase has been ported into more downstream systems than any
other in this corpus. Instant-NGP is what 3D Gaussian Splatting had to beat
on quality-at-FPS — and what it then did beat, on training-time fidelity at
1080p.

Five papers, ~40 min. Tomorrow: surfaces.
