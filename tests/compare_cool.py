#!/usr/bin/env python
"""Compares two cool or mcool files dataset by dataset.

    python tests/compare_cool.py EXPECTED ACTUAL [--ignore-attr NAME ...] [--data-only]

Every group, dataset and attribute must exist in both files with the same
dtype, shape, maxshape, chunk shape, compression, compression level and
shuffle flag, and the same values (NaN equal to NaN). The attributes
creation-date, update-date and generated-by differ between runs and
implementations and are not compared. --data-only compares names, dtypes,
shapes and values only. Exit status 0 when the files agree, 1 otherwise.
"""

import argparse
import sys

import h5py
import numpy as np

SKIPPED = {"creation-date", "update-date", "generated-by"}


def attrs_of(obj, ignore):
    return {k: obj.attrs[k] for k in obj.attrs if k not in ignore}


def same_value(a, b):
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.array_equal(np.asarray(a), np.asarray(b))
    if isinstance(a, bytes):
        a = a.decode()
    if isinstance(b, bytes):
        b = b.decode()
    return type(a) is type(b) and a == b if not isinstance(a, (np.generic,)) else (
        np.dtype(type(a)) == np.dtype(type(b)) and a == b)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("expected")
    parser.add_argument("actual")
    parser.add_argument("--ignore-attr", action="append", default=[])
    parser.add_argument("--data-only", action="store_true")
    args = parser.parse_args()
    ignore = SKIPPED | set(args.ignore_attr)
    problems = []

    with h5py.File(args.expected, "r") as e, h5py.File(args.actual, "r") as a:
        names_e, names_a = [], []
        e.visit(names_e.append)
        a.visit(names_a.append)
        if sorted(names_e) != sorted(names_a):
            problems.append(f"objects differ: only expected {sorted(set(names_e) - set(names_a))[:10]}, "
                            f"only actual {sorted(set(names_a) - set(names_e))[:10]}")
        for name in ["/"] + sorted(set(names_e) & set(names_a)):
            oe, oa = e[name], a[name]
            if type(oe) is not type(oa):
                problems.append(f"{name}: group/dataset mismatch")
                continue
            ae, aa = attrs_of(oe, ignore), attrs_of(oa, ignore)
            if sorted(ae) != sorted(aa):
                problems.append(f"{name}: attribute names {sorted(ae)} != {sorted(aa)}")
            for key in sorted(set(ae) & set(aa)):
                if not same_value(ae[key], aa[key]):
                    problems.append(f"{name}@{key}: {ae[key]!r} != {aa[key]!r}")
                if not args.data_only:
                    te = oe.attrs.get_id(key).dtype
                    ta = oa.attrs.get_id(key).dtype
                    if te != ta:
                        problems.append(f"{name}@{key}: attribute dtype {te} != {ta}")
            if isinstance(oe, h5py.Dataset):
                if oe.dtype != oa.dtype:
                    problems.append(f"{name}: dtype {oe.dtype} != {oa.dtype}")
                if h5py.check_enum_dtype(oe.dtype) != h5py.check_enum_dtype(oa.dtype):
                    problems.append(f"{name}: enum {h5py.check_enum_dtype(oe.dtype)} != "
                                    f"{h5py.check_enum_dtype(oa.dtype)}")
                if oe.shape != oa.shape:
                    problems.append(f"{name}: shape {oe.shape} != {oa.shape}")
                    continue
                if not args.data_only:
                    for prop in ("maxshape", "chunks", "compression", "compression_opts", "shuffle", "fletcher32"):
                        if getattr(oe, prop) != getattr(oa, prop):
                            problems.append(f"{name}: {prop} {getattr(oe, prop)} != {getattr(oa, prop)}")
                step = 1 << 24
                for lo in range(0, oe.shape[0] if oe.shape else 1, step):
                    ve = oe[lo:lo + step] if oe.shape else oe[()]
                    va = oa[lo:lo + step] if oa.shape else oa[()]
                    if ve.dtype.kind == "f":
                        equal = np.array_equal(ve, va, equal_nan=True)
                    else:
                        equal = np.array_equal(ve, va)
                    if not equal:
                        diff = np.flatnonzero(~((ve == va) | (np.isnan(ve) & np.isnan(va)))) if ve.dtype.kind == "f" \
                            else np.flatnonzero(ve != va)
                        problems.append(f"{name}: values differ at {len(diff)} rows from row {lo + diff[0]}: "
                                        f"{ve[diff[0]]!r} != {va[diff[0]]!r}")
                        break

    for p in problems[:40]:
        print("DIFF", p)
    print(f"{'identical' if not problems else 'DIFFERENT'}: {args.expected} vs {args.actual} "
          f"({len(problems)} differences)")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
