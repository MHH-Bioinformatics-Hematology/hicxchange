#!/usr/bin/env python3
"""Converting in both directions from Python.

The functions are those of hic2cool 1.0.1 under the name hicxchange, so a
script written for hic2cool keeps working once the import changes.

    python convert.py matrix.hic matrix.mcool back.hic
"""

import sys

from hicxchange import cool2hic_convert, hic2cool_convert


def main(argv):
    if len(argv) != 4:
        print("usage: convert.py <in.hic> <out.mcool> <roundtrip.hic>", file=sys.stderr)
        return 2

    hic_path, cool_path, back_path = argv[1], argv[2], argv[3]

    # resolution 0, the default, writes every resolution of the file as one
    # mcool file; any other value writes that one resolution as a cool file.
    # nproc 0, also the default, uses every available CPU.
    written = hic2cool_convert(hic_path, cool_path, 0, 0)

    # The other direction. normalizations 'auto' carries over the vectors the
    # cool file has and computes VC, VC_SQRT, KR and SCALE when it has none.
    back = cool2hic_convert(written, back_path, hic_version=9, normalizations="auto")

    print(f"wrote {written} and {back}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
