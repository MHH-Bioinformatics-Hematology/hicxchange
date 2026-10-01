# Python API

The functions of hic2cool 1.0.1 keep their names, positional arguments and
defaults, so code written for it keeps working once the import changes from
`hic2cool` to `hicxchange`. The one changed default is `nproc`, which is 0,
meaning every available CPU. Everything hicxchange adds is a keyword-only
argument, so a positional call can never reach it.

```python
from hicxchange import hic2cool_convert, cool2hic_convert

out = hic2cool_convert('matrix.hic', 'matrix.mcool')          # every resolution
out = hic2cool_convert('matrix.hic', 'matrix.cool', 10000)    # one resolution
cool2hic_convert(out, 'matrix.hic', hic_version=9)
```

`hic2cool_update`, `hic2cool_extractnorms`, `hic2cool_print_stderr` and
`hic2cool_force_exit` are available as before, as are the submodules
`hic2cool_config`, `hic2cool_updates` and `hic2cool_utils`.

## Signatures

```python
hic2cool_convert(infile, outfile, resolution=0, nproc=0, show_warnings=False,
                 silent=False, *, storage_mode='symmetric-upper')

hic2cool_extractnorms(infile, outfile, exclude_mt=False, show_warnings=False,
                      silent=False)

hic2cool_update(infile, outfile='', show_warnings=False, silent=False)

cool2hic_convert(infile, outfile, resolution=0, nproc=0, hic_version=9,
                 normalizations='auto', add_resolutions=None, cooler_weight=None,
                 genome=None, show_warnings=False, silent=False, *,
                 triangle='auto')
```

`hic2cool_convert` and `cool2hic_convert` return the path written.

## Messages and errors

Messages go to `sys.stdout` and `sys.stderr` as they do in hic2cool, so
redirecting those captures them. A condition that makes the command line tool
exit with status 1 raises `SystemExit` from the Python functions, as
`hic2cool_force_exit` does. The conversions release the GIL while they run.

## The command line in Python

`python -m hicxchange` takes the arguments of the `hicxchange` command:

```
python -m hicxchange hic2cool convert matrix.hic matrix.mcool
python -m hicxchange cool2hic matrix.mcool matrix.hic
```
