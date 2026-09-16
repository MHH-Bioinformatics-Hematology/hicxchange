#!/usr/bin/env python
"""Compares two hicstraw dumps (tests/straw_dump.py) of .hic files.

    python tests/compare_hic.py EXPECTED.npz ACTUAL.npz [--norm-tolerance REL] [--oe-tolerance REL]

Chromosomes, resolutions and pixels must be identical. Normalization vectors
must exist for the same chromosomes and agree within the chromosome's bins to
the relative tolerance (default 0: bit for bit, NaN equal to NaN);
observed/expected records must be the same records with values within
--oe-tolerance (default 1e-6). Exit status 0 when the files agree.
"""
import argparse
import math
import sys

import numpy as np


def relative(a, b):
    nan = np.isnan(a) | np.isnan(b)
    if not np.array_equal(np.isnan(a), np.isnan(b)):
        return math.inf
    a, b = a[~nan], b[~nan]
    if len(a) == 0:
        return 0.0
    scale = np.maximum(np.abs(a), np.abs(b))
    diff = np.abs(a - b)
    with np.errstate(invalid="ignore", divide="ignore"):
        rel = np.where(scale > 0, diff / scale, 0.0)
    return float(rel.max())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("expected")
    parser.add_argument("actual")
    parser.add_argument("--norm-tolerance", type=float, default=0.0)
    parser.add_argument("--oe-tolerance", type=float, default=1e-6)
    args = parser.parse_args()
    e, a = np.load(args.expected), np.load(args.actual)
    problems = []
    if list(e["chroms"]) != list(a["chroms"]) or list(e["lengths"]) != list(a["lengths"]):
        problems.append("chromosomes differ")
    lengths = e["lengths"]
    ke, ka = set(e.files), set(a.files)
    for kind in ("pixels", "norm", "oe"):
        only_e = sorted(k for k in ke - ka if k.startswith(kind + "/"))
        only_a = sorted(k for k in ka - ke if k.startswith(kind + "/"))
        if only_e or only_a:
            problems.append(f"{kind}: only expected {only_e[:5]} ({len(only_e)}), only actual {only_a[:5]} ({len(only_a)})")
    worst_norm = 0.0
    worst_oe = 0.0
    for key in sorted(ke & ka):
        if key.startswith("pixels/"):
            pe = e[key][np.lexsort(e[key][:, ::-1].T)]
            pa = a[key][np.lexsort(a[key][:, ::-1].T)]
            if not np.array_equal(pe, pa):
                problems.append(f"{key}: {len(pe)} vs {len(pa)} records, not identical")
        elif key.startswith("norm/"):
            _, res, _, chrom = key.split("/")
            bins = math.ceil(lengths[int(chrom) - 1] / int(res))
            r = relative(e[key][:bins], a[key][:bins])
            worst_norm = max(worst_norm, r)
            if r > args.norm_tolerance:
                problems.append(f"{key}: relative difference {r:.3g}")
        elif key.startswith("oe/"):
            oe_e = e[key][np.lexsort(e[key][:, 1::-1].T)]
            oe_a = a[key][np.lexsort(a[key][:, 1::-1].T)]
            if oe_e.shape != oe_a.shape or not np.array_equal(oe_e[:, :2], oe_a[:, :2]):
                problems.append(f"{key}: different records")
                continue
            r = relative(oe_e[:, 2], oe_a[:, 2])
            worst_oe = max(worst_oe, r)
            if r > args.oe_tolerance:
                problems.append(f"{key}: relative difference {r:.3g}")
    for p in problems[:30]:
        print("DIFF", p)
    n_pixels = sum(len(e[k]) for k in ke if k.startswith("pixels/"))
    print(f"{'identical' if not problems else 'DIFFERENT'}: {n_pixels} pixels, "
          f"{sum(k.startswith('norm/') for k in ke)} vectors (worst relative {worst_norm:.3g}), "
          f"{sum(k.startswith('oe/') for k in ke)} o/e matrices (worst relative {worst_oe:.3g})")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
