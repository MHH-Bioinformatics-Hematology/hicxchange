# Installing and building

## Conda

```
conda install -c bioconda hicxchange
```

## Pip

```
pip install hicxchange
```

A source install compiles the extension, so it needs a C++20 compiler, CMake
3.21 or newer, the HDF5 C library, zlib, hiccpp and coolercpp.

## From source

```
conda create -n hicxchange-build -c conda-forge python=3.12 cxx-compiler cmake \
      hdf5 zlib pybind11 scikit-build-core pytest h5py numpy cooler
conda activate hicxchange-build

cmake -S . -B build -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" \
      -DHICXCHANGE_HICCPP_SOURCE_DIR=/path/to/hiccpp \
      -DHICXCHANGE_COOLERCPP_SOURCE_DIR=/path/to/coolercpp
cmake --build build -j
cmake --install build --prefix "$HOME/.local"
```

Both libraries are found as installed CMake packages, as source trees with the
options above, or fetched with `HICXCHANGE_HICCPP_GIT_REPOSITORY` and
`HICXCHANGE_COOLERCPP_GIT_REPOSITORY`.

The tests need the Python module and a Python with pytest, h5py, numpy and
cooler, with `cooler` on `PATH`:

```
cmake -S . -B build -DHICXCHANGE_BUILD_PYTHON=ON ...
cmake --build build -j
ctest --test-dir build --output-on-failure
```
