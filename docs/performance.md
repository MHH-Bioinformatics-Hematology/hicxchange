# Performance

Measured on the in situ Hi-C matrix of GM12878 (GEO GSE63525), a 40 GB `.hic`
file in version 7, converting its 25 kb matrix of 898,978,865 pixels on an AMD
Ryzen 9 7950X with 16 cores and 32 threads, 128 GB of memory and a local NVMe
disk. Each tool ran on its own with its own defaults, hictk with 32 threads
requested.

| Conversion | Tool | Time (s) | Memory (GB) |
|---|---|---|---|
| `.hic` to cool | hic2cool 1.0.1 | 1951 | 5.25 |
| | hictk 2.2.0 | 166 | 0.77 |
| | hicxchange, 1 thread | 162 | 0.48 |
| | hicxchange, 8 threads | 46 | 0.76 |
| | hicxchange, 32 threads | 34 | 1.44 |
| cool to `.hic` | hictk 2.2.0 | 997 | 9.84 |
| | hicxchange, 32 threads | 56 | 3.19 |

Memory grows with the thread count, since every thread holds one decoded block,
so `-p` bounds it.

## What the output was checked against

- On the test files of hic2cool and on `.hic` versions 6, 7 and 8, the cool and
  mcool files are identical to hic2cool's in their groups, datasets, dtypes,
  chunk shapes, filters, attributes and values, and the messages printed are the
  same.
- For version 9 files, which hic2cool cannot read, the pixels agree with those of
  the version 8 file Juicer wrote from the same contacts.
- Taking the 898,978,865 pixel matrix to `.hic` version 9 and back returns every
  pixel unchanged, with the normalization vectors equal at the float32 precision
  version 9 stores.
- The vectors `cool2hic` computes are bit-identical to those Juicer tools 2.20.00
  `addNorm` writes into the same file.
- Against hictk, the pixels and normalization columns of the cool files agree, and
  hicxchange reads the `.hic` files hictk writes.
