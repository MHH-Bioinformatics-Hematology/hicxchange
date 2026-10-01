# Examples

The program below is `examples/convert.cpp` in the repository. It is complete:
the console, the resolutions and the options it passes are defined in the code,
and a top-level build compiles it, so an example that stops compiling fails the
build.

It is built with the library and left in the build tree:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
./build/examples/convert matrix.hic matrix.mcool back.hic
```

## Converting in both directions

`convert` fills a `Console`, converts a `.hic` file to a multi-resolution cool
file, converts that back to a `.hic` file of version 9, and handles the
condition the command line exits with status 1 on.

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

## From Python

`convert.py` does the same through the Python functions, which keep the names,
positional arguments and defaults of hic2cool 1.0.1.

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
