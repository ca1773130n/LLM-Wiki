---
type: ResearchDigest
date: 2026-04-10
period: daily
papers_covered:
  - arxiv-2003-08934
  - arxiv-2008-02268
  - arxiv-2011-12948
  - arxiv-1607-02565
  - arxiv-1812-04605
sub_topics: [Neural Radiance Fields, Visual SLAM and MVS, Dynamic and 4D Reconstruction]
---

# Daily digest — 2026-04-10

A foundations day. Before re-engaging with the 2023–2024 splatting and
generative papers, I went back to the work the field is still standing on.

The anchor was the original [NeRF paper](../../papers/arxiv-2003-08934/paper.md)
by Mildenhall et al. Two ideas still feel under-credited five years later:
the sinusoidal positional encoding (which is what made coordinate MLPs fit
high frequencies at all), and the coarse-to-fine importance sampling along
each ray. Every "fast NeRF" paper since has chipped away at one of these,
not invented something orthogonal.

[NeRF in the Wild](../../papers/arxiv-2008-02268/paper.md) is the one I
always forget to cite. Martin-Brualla et al. layer per-image appearance
and transient embeddings on top of NeRF so it can swallow unconstrained
photo collections — variable lighting, moving tourists, occluders. The
trick is small but the framing matters: you can decouple the scene from
the capture conditions if you give the model a per-frame latent.

[Nerfies](../../papers/arxiv-2011-12948/paper.md) by Park et al. is the
deformable-NeRF entry point. A per-observation deformation field warps
the canonical radiance field, so a casually-captured selfie video becomes
a 4D reconstruction. It still per-scene-optimises and still bakes ~hours
of training per clip — both costs the corpus's 2023+ papers will revisit.

On the classical-geometry side, I re-read
[Direct Sparse Odometry](../../papers/arxiv-1607-02565/paper.md) (Engel
et al., 2016) and [DeepV2D](../../papers/arxiv-1812-04605/paper.md) (Teed
& Deng, 2018) to remember why differentiable SfM mattered. DSO is the
last great non-learned visual odometry baseline; DeepV2D is the first
serious attempt at a learned, differentiable bundle adjustment, and it
seeds the [DROID-SLAM](../../papers/arxiv-2108-10869/paper.md) line I'll
get to later this month.

Five papers, ~45 min. The thread for the coming weeks: every 2023+ paper
is a reaction to a constraint one of these set.
