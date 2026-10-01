# hicxchange #

Converting Hi-C contact matrices between the Juicer .hic format and the cooler .cool and .mcool formats, in both directions. One command with two subtools:

```
$ hicxchange hic2cool convert matrix.hic matrix.mcool     # .hic to cool/mcool
$ hicxchange cool2hic matrix.mcool matrix.hic             # cool/mcool to .hic
```

**hicxchange is a fork of [hic2cool](https://github.com/4dn-dcic/hic2cool)**, written by Carl Vitzthum, Nezar Abdennur, Soo Lee and Peter Kerpedjiev at the 4DN Data Coordination and Integration Center (Park lab and Gehlenborg lab, Harvard Medical School DBMI; Mirny lab, MIT), released under the MIT licence. The fork keeps that licence ([LICENSE.txt](LICENSE.txt)) and the arguments and Python functions of hic2cool 1.0.1, and replaces the implementation with multi-threaded C++. The commands became subtools of `hicxchange`, and the Python package is imported as `hicxchange`, so that hicxchange and hic2cool can be installed side by side:

* **.hic versions 6 to 9.** hic2cool 1.0.1 reads versions 6 to 8; a version 9 file (Juicer tools 2) stops with a `UnicodeDecodeError`.
* **All cores by default.** `-p/--nproc` and `nproc` default to 0, every CPU the process may use. The output does not depend on the number of threads.
* **The same files.** On the test files of both projects, `hic2cool convert`, `extract-norms` and `update` write the groups, datasets, dtypes, chunk shapes, filters, attributes and values hic2cool 1.0.1 writes, and print the same messages ([docs/DEVIATIONS.md](docs/DEVIATIONS.md) lists the exceptions).
* **cool2hic**, the opposite conversion: .cool and .mcool files to .hic version 8 or 9.

The original hic parsing code was based on the [straw project](https://github.com/theaidenlab/straw) by Neva C. Durand and Yue Wu, and the hdf5-based structure used for cooler file writing on the [cooler repository](https://github.com/open2c/cooler). The C++ implementation reads and writes .hic files with hiccpp (see [Building](#building)), which follows hicstraw and Juicer tools.

## Converting .hic to cool

```
$ hicxchange hic2cool convert <infile> <outfile> -r <resolution> -p <nproc>
```

**infile** is a .hic input file, version 6, 7, 8 or 9.

**outfile** is a .cool output file.

**-r**, or --resolution, is an integer bp resolution supported by the hic file. *Please note* that only resolutions contained within the original hic file can be used. If 0 is given, will use all resolutions to build a multi-resolution file. Default is 0.

**-p**, or --nproc, is the number of threads to use. Default 0: all available CPUs.

**-w**, or --warnings, causes warnings to be explicitly printed to the console. This is false by default, though there are a few cases in which hic2cool will exit with an error based on the input hic file.

**-s**, or --silent, run in silent mode and hide console output from the program. Default false.

**-v**, or --version, print out hic2cool package version and exit.

**-h**, or --help, print out help about the package/specific run mode and exit.

Running the subtool from the command line will cause some helpful information about the hic file to be printed to stdout unless the `-s` flag is used.

## Converting cool to .hic

```
$ hicxchange cool2hic <infile> <outfile> [-r RESOLUTION] [-a ADD_RESOLUTIONS] [-p NPROC]
                      [--hic-version {8,9}] [-n NORMALIZATIONS] [--cooler-weight NAME]
                      [-g GENOME] [--triangle {auto,upper,lower}] [-s] [-w]
```

**infile** is a .cool or .mcool file, or a cooler URI such as `matrix.mcool::/resolutions/10000`.

**outfile** is the .hic output file.

**-r**, or --resolution: the resolution of the cooler file to write; 0 (default) writes every resolution of the file.

**-a**, or --add-resolutions: comma separated coarser resolutions to add, each a multiple of the finest resolution written, binned from it (for example `2500000,1000000,500000,250000,100000,50000,25000` for a 5 kb cooler, Juicer's usual zoom levels).

**--hic-version**: 9 (default, as Juicer tools 2 writes) or 8 (Juicer tools 1.22).

**-n**, or --normalizations: `auto` (default) writes the normalization vectors kept in the bins table, as hic2cool stores them, so that a .hic file converted to cool and back keeps its vectors; when the table has none, VC, VC_SQRT, KR and SCALE are computed as Juicer tools does. `none` writes none; a list such as `KR,SCALE` computes those.

**--cooler-weight NAME** also writes cooler's balancing weights (the `weight` column from `cooler balance`) as the normalization vector NAME, inverted, since hic normalization vectors divide and cooler weights multiply.

**-g**, or --genome: the genome id of the .hic header; default the cooler file's genome-assembly attribute.

**-p**, **-s** and **-w** work as for `hicxchange hic2cool convert`.

A .hic file converted with `hicxchange hic2cool convert` and back with `hicxchange cool2hic` has the same pixels, normalization vectors and expected values as the original (bit for bit on the test files; version 9 stores vectors as float32).

## Using the Python package

```
$ pip install .
```

Once the package is installed, the main method is hic2cool_convert. It takes the same parameters as `hicxchange hic2cool convert`, and the same positional arguments and defaults as hic2cool 1.0.1, except nproc, which defaults to every available CPU. Everything hicxchange adds is a keyword only argument, so calls written for hic2cool keep working once the import is changed. Example usage in a Python script is shown below or in test.py.
```
from hicxchange import hic2cool_convert, cool2hic_convert
hic2cool_convert(<infile>, <outfile>, <resolution (optional)>, <nproc (optional)>, <warnings (optional)>, <silent (optional)>)
cool2hic_convert('my_cool.mcool', 'my_hic.hic', hic_version=9, normalizations='auto')
```

The command line is the `hicxchange` executable; the Python package is the library interface. `hic2cool_update`, `hic2cool_extractnorms`, `hic2cool_print_stderr` and `hic2cool_force_exit` are available as before, as are the submodules `hic2cool_config`, `hic2cool_updates` and `hic2cool_utils`. Messages go to `sys.stdout` and `sys.stderr`, so redirecting those captures them; the conversions release the GIL.

## Building

Dependencies: a C++20 compiler (GCC 12 or newer, Clang 16 or newer), CMake 3.21
or newer, the HDF5 C library, zlib, hiccpp 0.4 or newer, which reads and
writes the .hic files, and coolercpp 0.4 or newer, which reads, writes and edits
the cool files. hic2cool contains no HDF5 code of its own. The Python package also needs Python 3.8 or newer,
pybind11 and scikit-build-core.

Conda provides all of them:

```
conda create -n hicxchange-build -c conda-forge python=3.12 cxx-compiler cmake \
      hdf5 zlib pybind11 scikit-build-core pytest h5py numpy cooler
conda activate hic2cool-build
```

### The command line tools

`hiccpp` and `coolercpp` are each found in one of three ways: as an installed
CMake package (`find_package(hiccpp 0.4)`), as a source tree
(`-DHICXCHANGE_HICCPP_SOURCE_DIR=/path/to/hiccpp`), or fetched during the
configure step (`-DHICXCHANGE_HICCPP_GIT_REPOSITORY=<url>`, with
`-DHICXCHANGE_HICCPP_GIT_TAG=<tag>`). The variables of `coolercpp` are named
`HICXCHANGE_COOLERCPP_SOURCE_DIR`, `HICXCHANGE_COOLERCPP_GIT_REPOSITORY` and
`HICXCHANGE_COOLERCPP_GIT_TAG`.

```
cmake -S . -B build -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" \
      -DHICXCHANGE_HICCPP_SOURCE_DIR=/path/to/hiccpp \
      -DHICXCHANGE_COOLERCPP_SOURCE_DIR=/path/to/coolercpp
cmake --build build -j
```

This writes `build/hicxchange`. To install it:

```
cmake --install build --prefix "$HOME/.local"
hicxchange --version
hicxchange cool2hic --help
```

### The Python package

```
pip install . --config-settings=cmake.define.HIC2COOL_HICCPP_SOURCE_DIR=/path/to/hiccpp \
      --config-settings=cmake.define.HIC2COOL_COOLERCPP_SOURCE_DIR=/path/to/coolercpp
```

This builds the extension module and installs the `hicxchange` command
alongside it. To build the module in the source tree instead, for
example to run the tests against it, configure with `-DHICXCHANGE_BUILD_PYTHON=ON`
and point `Python_EXECUTABLE` and `pybind11_DIR` at the interpreter to build
for:

```
cmake -S . -B build -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" \
      -DHICXCHANGE_HICCPP_SOURCE_DIR=/path/to/hiccpp \
      -DHICXCHANGE_BUILD_PYTHON=ON \
      -DPython_EXECUTABLE="$(which python)" \
      -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"
cmake --build build -j
```

### The tests

The tests need the Python module (`-DHICXCHANGE_BUILD_PYTHON=ON` above) and a
Python with pytest, h5py, numpy and cooler; `cooler` must be on `PATH`, since
one test calls `cooler dump`. They run the original hic2cool test suite and the
fork's own tests against a copy of the package in the build tree:

```
ctest --test-dir build --output-on-failure
```

## Performance

Measured on a 32-core machine (Linux, local NVMe disk) with the 40 GB `GSE63525_GM12878_insitu_primary+replicate_combined_30.hic` (GEO GSE63525, version 7): converting its 25 kb matrix (898,978,865 pixels) to cool, and that cool back to .hic version 9 with its seven normalization vectors.

| Conversion | Threads | Wall time | Peak memory |
|---|---|---|---|
| `hic2cool convert -r 25000`, hic2cool 1.0.1 (Python) | 1 | 1,951 s | 5.25 GB |
| `hicxchange hic2cool convert -r 25000` | 1 | 162 s | 0.48 GB |
| `hicxchange hic2cool convert -r 25000` | 8 | 46 s | 0.76 GB |
| `hicxchange hic2cool convert -r 25000` | 32 | 34 s | 1.44 GB |
| `hicxchange cool2hic` (cool to .hic v9, vectors carried) | 32 | 56 s | 3.19 GB |

The cool files written with 1, 16 and 32 threads hold the same data in the same layout; they differ only in their timestamps. Converting the .hic file written by `cool2hic` back to cool returns all 898,978,865 pixels unchanged and the normalization vectors equal at float32 precision. Memory grows with the thread count because every thread decodes a .hic block at a time; `-p` bounds it.

## Output file structure
If you elect to use all resolutions, a multi-resolution .mcool file will be produced. This changes the hdf5 structure of the file from a typical .cool file. Namely, all of the information needed for a complete cooler file is stored in separate hdf5 groups named by the individual resolutions. The hdf5 hierarchy is organized as such:

File --> 'resolutions' --> '###' (where ### is the resolution in bp).
For example, see the code below that generates a multi-res file and then accesses the specific resolution of 10000 bp.

```
from hicxchange import hic2cool_convert
import cooler
### using 0 triggers a multi-res output
hic2cool_convert('my_hic.hic', 'my_cool.cool', 0)
### will give you the cooler object with resolution = 10000 bp
my_cooler = cooler.Cooler('my_cool.cool::resolutions/10000')
```

When using only one resolution, the .cool file produced stores all the necessary information at the top level. Thus, organization in the multi-res format is not needed. The code below produces a file with one resolution, 10000 bp, and opens it with a cooler object.

```
from hicxchange import hic2cool_convert
import cooler
### giving a specific resolution below (e.g. 10000) triggers a single-res output
hic2cool_convert('my_hic.hic', 'my_cool.cool', 10000)
h5file = h5py.File('my_cool.cool', 'r')
### will give you the cooler object with resolution = 10000 bp
my_cooler = cooler.Cooler(h5file)
```


## higlass
Multi-resolution coolers produced by hi2cool can be visualized using [higlass](http://higlass.io/). Please note that single resolution coolers are NOT higlass compatible (created when using a non-zero value for `-r`). If you created a cooler before hic2cool version 0.5.0 that you want to view in higlass, it is highly recommended that you upgrade it before viewing on higlass to ensure correct normalization behavior.

To apply the hic normalization transformations in higlass, right click on the tileset and do the following:

`"<name of tileset>" --> "Configure Series" --> "Transforms" --> "<norm>"`

![higlass img](https://raw.githubusercontent.com/4dn-dcic/hic2cool/master/test_data/higlass_apply_transform.png)


## Updating hic2cool coolers
As of hic2cool version 0.5.0, there was a critical change in how hic normalization vectors are handled in the resulting cooler files. Prior to 0.5.0, hic normalization vectors were inverted by hic2cool. The rationale for doing this is that hic uses divisive normalization values, whereas cooler uses multiplicative values. However, higlass and the 4DN analysis pipelines specifically handled the divisive normalization values, so hic2cool now handles them the same way.

In the near future, there will be a `cooler` package release to correctly handle divisive hic normalization values when balancing.

To update a hic2cool cooler, simply run:
```
hicxchange hic2cool update <infile> -o <outfile (optional)>
```

If you only provide the `infile` argument, then the cooler will be updated directly. If you provide an optional `outfile` file path, then a new cooler updated cooler file will be created and the original file will remain unchanged.


## Extracting hic normalization values
As of hic2cool 0.5.0, you can easily extract hic normalization vectors to an existing cooler file. This will only work if the specified cooler file shares the resolutions found in the hic file. To do this, simply run:
```
hicxchange hic2cool extract-norms <hic file> <cooler file>
```

You may also provide the optional `-e` flag, which will cause the mitchondrial chromosome to automatically be omitted from the extraction. This is found by name; the code specifically looks for one of `['M', 'MT', 'chrM', 'chrMT']` (in a case-insensitive way). Just like with `hicxchange hic2cool convert`, you can also provide `-s` and `-w` [arguments](#arguments-for-hic2cool-convert).


## Changelog
### 2.0.0
* Fork of hic2cool 1.0.1 with the conversions in multi-threaded C++; command line and Python API unchanged
* Reads .hic version 9 (Juicer tools 2) besides versions 6 to 8
* `-p/--nproc` defaults to 0, all available CPUs; the output does not depend on the number of threads
* New `cool2hic` command and `cool2hic_convert`: cool and mcool files to .hic version 8 or 9, keeping or computing normalization vectors
* `generated-by` is `hic2cool-2.0.0`; build with CMake or scikit-build-core instead of Poetry
### 1.0.1
* Restore command line usage, adds missing README update
### 1.0.0
*  Switch to poetry, upgraded `python`, `numpy`, `cooler` versions, h5file I/O clean up, replace `multiprocessing` with `multiprocess'
### 0.8.3
* Partial fix for zlib decompression issue.
### 0.8.2
* loosened version for `numpy`, `scipy` and `pandas`.
### 0.8.1
* `setup.py` takes dependencies directly from `requirements.txt` (`requirements.txt` updated to match `setup.py`)
### 0.8.0
* multiprocessing support for convert
* change in usage of convert API due to the addition of the `nproc` option
* Python 2.7 is deprecated.
### 0.7.3
* Pinned `pandas==0.24.2` since newer versions deprecate python 2
### 0.7.2
* Warning from `hic2cool_utils.parse_hic` will now output chromsome names, not indices
### 0.7.1
* Add `format` and `format-version` to `/` collection for multi-resolution coolers written by hic2cool
* Run `hic2cool_update` to add these attributes to mcool files generated with previous hic2cool versions
* Fixed issue where datetime-derived metadata was written as bytestring when using python 2
### 0.7.0
* Fixed package issues associated with python 2
* Fixed issue where some cooler metadata was written as non-unicode when using python 2
### 0.6.1
* Fixed input issue with `hic2cool update` when using python 2
### 0.6.0
* Added `format-version` and `storage-type` to attributes of output cooler to get up-to-date with cooler schema v3
* Run `hic2cool update` to add these attributes to files generated with previous hic2cool versions
### 0.5.1
Fixed packaging issue by adding MANIFEST.in and made some documentation/pypi edits
### 0.5.0
Large release that changes how hic2cool is run
* hic2cool is now executed with `hic2cool <mode>`, where mode is one of: `[convert, update, extract-norms]`
* Added two new modes: `update` (update coolers made by hic2cool based on version) and `extract-norms` (extract hic normalization vectors to pre-existing cooler file)
* Removed old hic2cool_extractnorms script (this is now run with `hic2cool extract-norms`)
* hic normalization vectors are NO LONGER INVERTED when added to output cooler for consistency with the 4DN omics processing pipeline and higlass
* Missing hic normalization vectors are now represented by vectors of `NaN` (used to be vectors of zeros)
* Improvement of help messages when running hic2cool and change around arguments for running the program
* Test updates
### 0.4.2
* Fixed issue where hic files could not be converted if they were missing normalization vectors
### 0.4.1
* Fixed error in reading counts from hic files of version 6
* Chromosome names are now directly taken from hic file (with exception of 'all')
### 0.4.0
Large patch, should fix most memory issues and improve runtimes:
* Changed run parameters. Removed -n and -e; added -v (--version) and -w (--warnings)
* Improved memory usage
* Improved runtime (many thanks to Nezar Abdennur)
* hic2cool now does a 'direct' conversion of files and does not fail on missing chr-chr contacts or missing normalization vectors. Finding these issues will cause warnings to be printed (controlled by -w flag)
* No longer uses the 'weights' column, which is reserved for cooler
* No longer takes a normalization type argument. All normalization vectors from the hic file are automatically added to the bins table in the output .cool
* Many other minor bug fixes/code improvement
### 0.3.7
Fixed issue with bin1_offset not containing final entry (should be length nbins + 1).
### 0.3.6
Simple release to fix pip execution.
### 0.3.5
README updates, switched cooler syntax in test, and added helpful printing of hic file header info when using the command line tool.
### 0.3.4
Fixed issue where chromosome name was not getting properly set for 'All' vs 'all'.
### 0.3.3
Removed rounding fix. For now, allow py2 and py3 weights to have different number of significant figures (they're very close).
### 0.3.2
Changed output file structure for single resolution file. Resolved an issue where rounding for weights was different between python 2 and 3.
### 0.3.1
Added .travis.yml for automated testing. Changed command line running scheme. Python3 fix in hic2cool_utils.
### 0.3.0
Added multi-resolution format to output cool files. Setup argparse. Improved speed. Added tests for new resolutions format.

## Contributors
hic2cool was written by Carl Vitzthum (1), Nezar Abdennur (2), Soo Lee (1), and Peter Kerpedjiev (3).

The C++ fork (version 2) was written by Joachim Wolff.

(1) Park lab, Harvard Medical School DBMI

(2) Mirny lab, MIT

(3) Gehlenborg lab, Harvard Medical School DBMI

Originally published 1/26/17.
