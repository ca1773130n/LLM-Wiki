---
type: Paper
arxiv: "2201.05989"
arxiv_url: https://arxiv.org/abs/2201.05989
title: "Instant Neural Graphics Primitives with a Multiresolution Hash Encoding"
authors:
  - "Thomas Müller"
  - "Alex Evans"
  - "Christoph Schied"
  - "Alexander Keller"
date: 2022-01-16
sub_topic: Neural Radiance Fields
license: "CC-BY-4.0 (Tesserae demo prose)"
methods: [HashEncoding]
datasets: []
metrics: [PSNR, SSIM, LPIPS]
oss_repo: NVlabs/instant-ngp
---

# Instant Neural Graphics Primitives with a Multiresolution Hash Encoding

Müller et al. present Instant Neural Graphics Primitives (Instant-NGP),
a coordinate-encoding scheme that lets a small MLP fit neural graphics
primitives — radiance fields, signed distance functions, gigapixel
images, neural volumes — orders of magnitude faster than prior work
without sacrificing quality. The contribution sits at the intersection
of the explicit-grid line (Plenoxels, DVGO) and the coordinate-MLP line
(NeRF, Mip-NeRF), and proved decisive enough to reset the practical
baseline for the entire radiance-field field.

The encoding is a multi-resolution hash table. A query 3D coordinate is
mapped, at L resolution levels (typically L=16, geometrically spaced),
to the eight nearest grid corners. At each level, those corners are
hashed into a fixed-size table of trainable feature vectors; the
features are trilinearly interpolated and concatenated across levels
into the input of a tiny MLP. There is no explicit collision resolution
— at coarse levels the table is large enough that there are no
collisions, at fine levels the table is undersized and collisions are
implicitly disambiguated by gradient updates that prefer to put visible
content where collisions are absent.

The system is implemented end-to-end in fully fused CUDA kernels with
careful attention to memory bandwidth, achieving training of a high-
quality radiance field in tens of seconds and rendering at 1080p in
tens of milliseconds — combined speedups of several orders of magnitude
over NeRF (Mildenhall et al., 2020) and Mip-NeRF (Barron et al., 2021)
on comparable hardware.

The hash encoding has been adopted by nearly every subsequent radiance-
field method that needs to train quickly: Magic3D (Lin et al., 2022)
uses it for text-to-3D, MonoSDF (Yu et al., 2022) uses it for surface
reconstruction, and the Nerfacto / Nerfstudio defaults wrap it. The
codebase at github.com/NVlabs/instant-ngp remains the reference
implementation.
