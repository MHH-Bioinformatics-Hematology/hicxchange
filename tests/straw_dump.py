#!/usr/bin/env python
"""Dumps a .hic file through hicstraw into an .npz archive: for every base pair
resolution, the observed records of every chromosome pair (chromosome
indexes, bins, counts) and every normalization vector of every chromosome.

    python tests/straw_dump.py FILE.hic OUT.npz [NORM,...]

NORM,... lists the normalizations to read (default VC,VC_SQRT,KR,SCALE); list
only ones the file has: hicstraw reads a vector from an uninitialized file
position when asked for one it does not have.

Runs in an environment with hicstraw and numpy.
"""
import sys

import hicstraw
import numpy as np


def main():
    hic = hicstraw.HiCFile(sys.argv[1])
    chroms = [c for c in hic.getChromosomes() if c.name.lower() != "all"]
    out = {"chroms": np.array([c.name for c in chroms]), "lengths": np.array([c.length for c in chroms])}
    for res in hic.getResolutions():
        rows = []
        for i, a in enumerate(chroms):
            for b in chroms[i:]:
                mzd = hic.getMatrixZoomData(a.name, b.name, "observed", "NONE", "BP", res)
                for r in mzd.getRecords(0, a.length, 0, b.length):
                    rows.append((a.index, b.index, r.binX // res, r.binY // res, r.counts))
        out[f"pixels/{res}"] = np.array(rows, dtype=np.float64).reshape(-1, 5)
        wanted = sys.argv[3].split(",") if len(sys.argv) > 3 else ["VC", "VC_SQRT", "KR", "SCALE"]
        for norm in [n for n in wanted if n]:
            for c in chroms:
                try:
                    mzd = hic.getMatrixZoomData(c.name, c.name, "observed", norm, "BP", res)
                    v = np.asarray(mzd.getNormVector(c.index), dtype=np.float64)
                except Exception:
                    continue
                if len(v):
                    out[f"norm/{res}/{norm}/{c.index}"] = v
                    # observed / expected of the chromosome: exercises the
                    # normalized expected values
                    oe = hic.getMatrixZoomData(c.name, c.name, "oe", norm, "BP", res)
                    rows = [(r.binX // res, r.binY // res, r.counts) for r in oe.getRecords(0, c.length, 0, c.length)]
                    out[f"oe/{res}/{norm}/{c.index}"] = np.array(rows, dtype=np.float64).reshape(-1, 3)
    for res in hic.getResolutions():
        for c in chroms:
            oe = hic.getMatrixZoomData(c.name, c.name, "oe", "NONE", "BP", res)
            rows = [(r.binX // res, r.binY // res, r.counts) for r in oe.getRecords(0, c.length, 0, c.length)]
            out[f"oe/{res}/NONE/{c.index}"] = np.array(rows, dtype=np.float64).reshape(-1, 3)
    np.savez(sys.argv[2], **out)


if __name__ == "__main__":
    main()
