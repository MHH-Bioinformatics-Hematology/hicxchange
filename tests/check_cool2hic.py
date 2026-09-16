#!/usr/bin/env python
"""Checks a .hic file written by cool2hic against the cooler file it came from.

    python tests/check_cool2hic.py COOLER_URI_OR_FILE DUMP.npz [--added RES,...] [--carried NAME,...]
                                   [--weight-name NAME]

DUMP.npz is tests/straw_dump.py of the .hic file. For every cooler
resolution, the .hic pixels must be the cooler's upper triangle pixels with
non-zero counts; an added resolution must hold the finest cooler resolution's
pixels summed into its bins; a carried normalization column must come back as
stored (float32 rounding allowed for version 9); --weight-name compares 1 /
weight. Runs in an environment with cooler, h5py and numpy.
"""
import argparse
import sys

import cooler
import numpy as np


def upper_pixels(clr, factor=1):
    px = clr.pixels()[:]
    bins = clr.bins()[["chrom", "start"]][:]
    names = list(clr.chromnames)
    chrom = bins["chrom"].map({n: i for i, n in enumerate(names)}).to_numpy() + 1
    start = bins["start"].to_numpy()
    b1, b2 = px["bin1_id"].to_numpy(), px["bin2_id"].to_numpy()
    c1, c2 = chrom[b1], chrom[b2]
    keep = (c1 < c2) | ((c1 == c2) & (b1 <= b2))
    keep &= px["count"].to_numpy() != 0
    res = clr.binsize * factor
    rows = np.stack([c1[keep], c2[keep], start[b1[keep]] // res, start[b2[keep]] // res,
                     px["count"].to_numpy()[keep].astype(np.float32)], axis=1).astype(np.float64)
    if factor > 1:
        keys, inverse = np.unique(rows[:, :4], axis=0, return_inverse=True)
        sums = np.zeros(len(keys), dtype=np.float32)
        np.add.at(sums, inverse.ravel(), rows[:, 4].astype(np.float32))
        rows = np.concatenate([keys, sums[:, None].astype(np.float64)], axis=1)
    return rows[np.lexsort(rows[:, ::-1].T)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cool")
    parser.add_argument("dump")
    parser.add_argument("--added", default="")
    parser.add_argument("--carried", default="")
    parser.add_argument("--weight-name", default="")
    args = parser.parse_args()
    if "::" in args.cool:
        uris = [args.cool]
    else:
        uris = [args.cool + "::" + g for g in cooler.fileops.list_coolers(args.cool)]
    coolers = {cooler.Cooler(u).binsize: cooler.Cooler(u) for u in uris}
    z = np.load(args.dump)
    problems = []
    checked = 0
    finest = min(coolers)
    targets = [(res, clr, 1) for res, clr in coolers.items()]
    targets += [(int(r), coolers[finest], int(r) // finest) for r in args.added.split(",") if r]
    for res, clr, factor in targets:
        key = f"pixels/{res}"
        if key not in z.files:
            problems.append(f"resolution {res} missing from the .hic file")
            continue
        mine = z[key][np.lexsort(z[key][:, ::-1].T)]
        theirs = upper_pixels(clr, factor)
        checked += len(theirs)
        if mine.shape != theirs.shape or not np.array_equal(mine, theirs):
            problems.append(f"{res}: {len(theirs)} cooler pixels vs {len(mine)} .hic pixels, not identical")
        if factor != 1:
            continue
        offsets = clr._load_dset("indexes/chrom_offset")
        columns = [c for c in args.carried.split(",") if c]
        if args.weight_name:
            columns.append("weight")
        for column in columns:
            if column not in clr.bins().columns:
                continue
            values = clr.bins()[column][:].to_numpy()
            name = args.weight_name if column == "weight" else column
            if column == "weight":
                values = 1.0 / values
            for ci in range(len(offsets) - 1):
                seg = values[offsets[ci]:offsets[ci + 1]]
                key = f"norm/{res}/{name}/{ci + 1}"
                if key not in z.files:
                    if not np.all(np.isnan(seg)) and f"pixels/{res}" in z.files and \
                            np.any((z[f"pixels/{res}"][:, 0] == ci + 1) & (z[f"pixels/{res}"][:, 1] == ci + 1)):
                        problems.append(f"{key} missing")
                    continue
                v = z[key][:len(seg)]
                if not np.array_equal(np.isnan(v), np.isnan(seg)):
                    problems.append(f"{key}: NaN positions differ")
                    continue
                m = ~np.isnan(v)
                if m.any() and not np.allclose(v[m], seg[m].astype(np.float32) if np.all(v[m] == v[m].astype(np.float32)) and not np.array_equal(v[m], seg[m]) else seg[m], rtol=0, atol=0):
                    problems.append(f"{key}: values differ, max {np.max(np.abs(v[m] - seg[m]))}")
    for p in problems[:30]:
        print("DIFF", p)
    print(f"{'identical' if not problems else 'DIFFERENT'}: {checked} pixels over {len(targets)} resolutions")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
