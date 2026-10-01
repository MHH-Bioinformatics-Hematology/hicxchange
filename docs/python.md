# Python API

The commands are the C++ executable `hicxchange`; this page is the library
interface, importable from Python.

The functions of hic2cool 1.0.1 keep their names, positional arguments and
defaults, so code written for it keeps working once the import changes from
`hic2cool` to `hicxchange`. The one changed default is `nproc`, which is 0,
meaning every available CPU. Everything hicxchange adds is a keyword-only
argument, so a positional call can never reach it.

```python title="examples/convert.py"
--8<-- "examples/convert.py"
```

```
$ python convert.py SRR1791297_30.v8.hic matrix.mcool back.hic
### Header info from cool
... Resolutions:  [1000000, 250000, 50000, 10000]
... Normalizations carried:  ['KR', 'SCALE', 'VC', 'VC_SQRT']
... hic version:  9
### Converting
### Finished! Output written to: back.hic
wrote matrix.mcool and back.hic
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
