# C++ API

The conversions are callable from C++ as well; the library target is
`hicxchange::core`.

`hic2cool_convert`, `hic2cool_convert_mcool`, `hic2cool_extractnorms`,
`hic2cool_update` and `cool2hic_convert` take the arguments of the Python
functions and return the path written. Messages and prompts go through a
`Console`, which the command line fills with the process streams and the Python
module with `sys.stdout`, `sys.stderr` and `input`. A condition that makes the
command line exit with status 1 throws `ExitError`.

```cpp title="examples/convert.cpp"
--8<-- "examples/convert.cpp"
```

```
$ convert SRR1791297_30.v8.hic matrix.mcool back.hic
[convert] ### Header info from cool
[convert] ... Resolutions:  [1000000, 250000, 50000, 10000]
[convert] ... Normalizations carried:  ['KR', 'SCALE', 'VC', 'VC_SQRT']
[convert] ... Genome:  sacCer3.chrom.sizes
[convert] ... hic version:  9
[convert] ### Converting
[convert] ### Finished! Output written to: back.hic
wrote matrix.mcool and back.hic on 32 threads
```

## Headers

```cpp
--8<-- "include/hicxchange/hicxchange.hpp"
```
