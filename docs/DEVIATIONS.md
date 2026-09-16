# Differences from hic2cool 1.0.1

hic2cool 2.x keeps the command line and the Python API of hic2cool 1.0.1 and
writes the same files: the same groups, datasets, dtypes, chunk shapes,
filters, attributes and values, and prints the same messages. This page lists
where it differs, on purpose or because the original's behaviour depends on
the environment it runs in.

## Intended changes

| Area | hic2cool 1.0.1 | hic2cool 2.x |
|---|---|---|
| .hic versions | 6 to 8; version 9 files stop with `UnicodeDecodeError` | 6 to 9 |
| `nproc` / `-p` default | 1 | 0, meaning every CPU the process may run on (its affinity mask, which taskset, cgroups and batch schedulers set) |
| parallelism | `multiprocess` pool over block ranges | threads: blocks are decoded and HDF5 chunks compressed on all threads; the output does not depend on the number of threads |
| cool to .hic | not available | `cool2hic` command and `cool2hic_convert` |
| `generated-by` attribute | `hic2cool-0.8.3` (the 1.0.1 package reports 0.8.3 as its version) | `hic2cool-2.0.0` |
| file size | chunks are rewritten as the pixel datasets grow, which leaves unused space in the file (190 kB in `test_hic.hic`'s mcool) | every chunk is written once; the stored data is the same, the file smaller. `test.py` compares stored dataset bytes instead of the file size |
| a missing chromosome pair at a resolution the pair's matrix does not have | reads the block list of the wrong resolution | treated like a missing pair: skipped, with the `-w` warning |

## Output that depends on the Python environment

| Message | hic2cool 1.0.1 | hic2cool 2.x |
|---|---|---|
| `extract-norms`: `... {500000: '/resolutions/500000', ...}` | numpy 2 prints the resolutions as `np.int64(500000)`, numpy 1 as `500000` | `500000` |
| `extract-norms`: pandas `FutureWarning` about `observed=False` | printed by pandas 2.1 and newer | not printed |
| `extract-norms`: the bins table preview | pandas `DataFrame.to_string` | the same layout, reimplemented (display precision 6, fixed or scientific notation as pandas chooses) |
| `update`: a `creation-date` without fractional seconds | `strptime` raises `ValueError` (isoformat leaves out a zero fraction) | accepted |
| a missing input file | Python `FileNotFoundError` traceback | the Python API raises the same exception; the command line prints `[Errno 2] No such file or directory: <path>` and exits with status 1 |
| errors inside hicstraw-level parsing (a truncated or corrupt .hic file) | a Python traceback (`struct.error`, `zlib.error`) | `!!! ERROR. <reason>` and exit status 1 |

## Kept although odd

These reproduce hic2cool 1.0.1 exactly, because files and scripts may depend
on them:

- `### Converting` is printed even with `-s`; so are `### No updates found!`
  and the progress lines of `update`.
- Pixel counts are stored as int32: non-integer counts of a .hic file are
  truncated, as numpy truncates a float stored into an int32 array.
- `extract-norms -e` prints both `Excluding chromosome ...` and
  `No chromosome found when attempting to exclude MT.` when it finds exactly
  one mitochondrial chromosome.
- `convert` never prints `Warnings were found in this run`: in 1.0.1 the
  flag it tests is only ever set in a local variable.
- Normalization vectors are stored divisive, as in the .hic file (hic2cool
  0.5.0 and later); `cooler` applies them with `divisive_weights`.

## cool2hic

`cool2hic` has no counterpart in hic2cool 1.0.1. Its choices:

- The .hic file is laid out as Juicer tools `pre` lays it out (version 8 as
  1.22.01, version 9 as 2.x), through hicfilecpp. Normalizations it computes
  are those of Juicer tools `addNorm`; on the test data they are bit for bit
  those Juicer tools 2.20.00 `addNorm` writes into the same file.
- `--normalizations auto` (the default) writes back the normalization columns
  of the bins table: for a file written by hic2cool every float column but
  `weight`, for any other cooler the columns named as Juicer's
  normalizations (VC, VC_SQRT, KR, SCALE, GW_*, INTER_*). A chromosome whose
  column holds only NaN, hic2cool's mark for a missing vector, gets no
  vector. Without such columns, VC, VC_SQRT, KR and SCALE are computed.
- Header attributes that hic2cool copied from the .hic file into the cooler
  attributes are written back into the .hic header; `software` names
  cool2hic.
- Pixels with a count of 0 are left out; pixels with a count that is not
  finite are left out with a warning. The lower triangle of a `square`
  cooler is left out, as .hic stores the upper triangle.
- Coolers with variable bin sizes are refused: .hic needs fixed bins.
- A .hic file round-tripped through `hic2cool convert` and `cool2hic` returns
  the same pixels and normalization vectors; version 9 stores vectors as
  float32, so a cooler's float64 vectors are rounded when written to it.
