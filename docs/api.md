# C++ API

The conversions are callable from C++ as well; the library target is
`hicxchange::core`.

```cpp
#include <hicxchange/hicxchange.hpp>

const std::string written = hicxchange::hic2cool_convert("matrix.hic", "matrix.mcool");

hicxchange::Cool2hicOptions options;
options.hic_version = 9;
hicxchange::cool2hic_convert(written, "back.hic", options);
```

Messages and prompts go through a `Console`, which the command line fills with
the process streams and the Python module with `sys.stdout`, `sys.stderr` and
`input`.

## A complete program

`examples/convert.cpp`, which converts a `.hic` file to a multi-resolution cool
file and back, with its own console and its own error handling:

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
