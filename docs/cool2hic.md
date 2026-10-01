# hicxchange cool2hic

cool and mcool to `.hic` version 8 or 9.

```
$ hicxchange cool2hic <infile> <outfile> [-r RESOLUTION] [-a ADD_RESOLUTIONS]
                      [-p NPROC] [--hic-version {8,9}] [-n NORMALIZATIONS]
                      [--cooler-weight NAME] [-g GENOME]
                      [--triangle {auto,upper,lower}] [-s] [-w]
```

`infile` is a `.cool` or `.mcool` file, or a URI such as
`matrix.mcool::/resolutions/10000`. With `-r 0`, the default, every resolution of
the file is written.

`--hic-version` is 9 by default, as Juicer 2 writes; 8 is the format Juicer tools
1.22 writes and older Juicebox builds read.

`-a` adds coarser resolutions, each a multiple of the finest resolution written
and binned from it, for example `-a 2500000,1000000,500000,250000,100000,50000,25000`
for a 5 kb cooler, which gives Juicer's usual zoom levels.

## Normalization vectors

`-n auto`, the default, writes back the vectors stored in the bins table, so a
`.hic` file converted to cool and back keeps them. When the table holds none, VC,
VC_SQRT, KR and SCALE are computed as Juicer tools does. `-n none` writes none,
and a list such as `-n KR,SCALE` computes those.

`--cooler-weight NAME` writes cooler's balancing weights, the `weight` column, as
the normalization vector NAME. The values are inverted, since hic vectors divide
and cooler weights multiply.

## Square coolers

A `.hic` file stores one triangle. A square cooler is therefore checked for
symmetry, and an asymmetric one is refused unless `--triangle upper` or
`--triangle lower` says which half to write.
