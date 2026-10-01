# hicxchange

Converting Hi-C contact matrices between the Juicer `.hic` format and the cooler
`.cool` and `.mcool` formats, in both directions. One command with two subtools:

```
$ hicxchange hic2cool convert matrix.hic matrix.mcool     # .hic to cool or mcool
$ hicxchange cool2hic matrix.mcool matrix.hic             # cool or mcool to .hic
```

hicxchange is a fork of [hic2cool](https://github.com/4dn-dcic/hic2cool), written
by Carl Vitzthum, Nezar Abdennur, Soo Lee and Peter Kerpedjiev, and keeps its MIT
licence, its command arguments and its Python functions. What it adds:

- **`.hic` versions 6 to 9.** hic2cool 1.0.1 reads 6 to 8 and stops on version 9
  files, which Juicer 2 writes.
- **All cores by default**, with output that does not depend on the thread count.
- **The same files.** The cool files it writes are hic2cool's, dataset by
  dataset, down to the chunk shapes and attributes.
- **cool2hic**, the conversion in the other direction, to `.hic` version 8 or 9.

It reads and writes `.hic` files with [hiccpp](https://hiccpp.readthedocs.io) and
cool files with [coolercpp](https://coolercpp.readthedocs.io).

```{toctree}
:maxdepth: 2
:caption: Guide

install
hic2cool
cool2hic
python
performance
```

```{toctree}
:maxdepth: 2
:caption: Reference

api
DEVIATIONS
```
