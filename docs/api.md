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

```cpp
--8<-- "include/hicxchange/hicxchange.hpp"
```
