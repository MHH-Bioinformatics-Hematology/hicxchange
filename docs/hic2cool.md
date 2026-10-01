# hicxchange hic2cool

`.hic` to cool, with the three modes of hic2cool 1.0.1 and the same arguments.

## convert

```
$ hicxchange hic2cool convert <infile> <outfile> [-r RESOLUTION] [-p NPROC]
                              [--storage-mode {symmetric-upper,square}] [-s] [-w]
```

`infile` is a `.hic` file of version 6, 7, 8 or 9. With `-r 0`, the default,
every base pair resolution of the file is written as a multi-resolution `.mcool`
file; a single resolution gives a `.cool` file. As in hic2cool, the output name
is adjusted to `.cool` or `.mcool` to match.

`-p` is the number of threads, 0 by default, which uses every CPU the process
may run on. The pixels, indexes and attributes written do not depend on it.

`--storage-mode square` writes both triangles, cooler's layout for asymmetric
matrices, instead of the upper triangle.

## update

```
$ hicxchange hic2cool update <infile> [-o OUTFILE] [-s] [-w]
```

Upgrades a cool or mcool file written by an older hic2cool, as
`hic2cool update` does, in place or into a new file.

## extract-norms

```
$ hicxchange hic2cool extract-norms <hic file> <cooler file> [-e] [-s] [-w]
```

Adds the normalization vectors of a `.hic` file to the bins tables of the cooler
groups whose resolution that file has. `-e` leaves out the mitochondrial
chromosome.

## Normalization vectors

The vectors are stored as the `.hic` file holds them, which is divisive, in bins
table columns named after the normalization (`KR`, `VC`, `VC_SQRT`, `SCALE`, and
the genome-wide and inter-chromosomal variants when present). cooler applies
them with `divisive_weights`, and so do tools that read the `generated-by`
attribute to recognise a file of this origin.
