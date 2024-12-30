# Corrosiff-Python

![GitHub CI](https://github.com/MaimonLab/corrosiff-python/actions/workflows/maturin-CI.yaml/badge.svg)

A hybrid `Python` and `Rust` package that wraps the
`corrosiff` library for reading .siff files and
presents a `Python` API.

# Installation

Installation with a package manager
----------------------------------

I'm starting to host things on PyPI and a private
`conda` channel (`maimon-forge` on the Rockefeller
server). Watch this space for updates...

```
pip install corrosiffpy
```

Installation from source
--------------------------

Everyone has a bunch of different `Python`
installations and different solutions for
managing them. Because this package relies on
`Rust`, if you're installing from source
you need a `Rust` compiler. The main way to manage
`Rust` and its dependencies is [`cargo`](https://doc.rust-lang.org/cargo/getting-started/installation.html).
Once you have `cargo` you can install with `pip` or
`maturin`.

## Install to a local environment

### pip

You can use your interpreter's `pip` with
the `pyproject.toml` location in `corrosiff-python`.

```sh
(venv) cd path/to/corrosiff-python
(venv) pip install .
```

### Maturin

This can be installed using `maturin`, the
current preferred `PyO3` installation tool. It's
a `Python` package that can be installed from `PyPI`
with `pip`.

`pip install maturin`

To use maturin, you can navigate to the `corrosiff-python`
directly and then execute

```
maturin develop --release
```

in the command line, which will use the system `Python`
distribution to install this library.

Example use
------------

```python

import corrosiffpy

siffio : 'corrosiffpy.SiffIO' = corrosiffpy.open_file(
    'path_to_my_file'
)

frames = siffio.get_frames(frames=list(range(200)))

print(frames.shape, frame.dtype)

>>> ((200, 256, 256), np.uint16)

lifetime, intensity, _ = siffio.flim_map(frames = list(range(200)))

print(lifetime.shape, lifetime.dtype, intensity.shape, intensity.dtype)

>>> ((200,256,256), np.float64, (200,256,256), np.uint16)

masks = np.ones((4, 256, 256), dtype= bool)
masks[:,:128,:] = False

masked_rois = siffio.sum_rois(masks, frames = list(range(200)))

print(masked_rois.shape, masked_rois.dtype)

>> ((4, 200), np.uint64)

```

# Python API

The module contains only a few functions:

- `siff_to_tiff`
    A currently-unimplemented function to convert `.siff` files
    to `.tiff` data, sacrificing the arrival time information

- `open_file`
    A function that returns the `SiffIO` class, the primary `Python`
    interface to the `corrosiff` library.

`SiffIO`
---------

The `SiffIO` class wraps the methods of the `SiffReader` struct in `Rust`,
returning `Python` versions of the various arrays, strings, and metadata.
Most functions read frames from the file stream, so you never have to actually
load the file into memory (which can be good -- many resonant scanning imaging
files are very large), and return `numpy` arrays.


Testing
----------

There are two classes of tests: internal consistency, and consistency
with the `C++` implementation.

To test that different methods (e.g. separate mask function calls vs.
all-together versions) return the same results, the core tests suite
is implemented purely using the `corrosiff-python` library with no
comparisons or calls to `siffpy`. These tests can be run with `pytest`
from the main repository directory, and testing across various
`Python` versions can be run with `tox`

```
pytest tests
```
or

```
tox
```

It is these internal consistency tests that are also run by the 
continuous integration tools that `GitHub` will run on new version uploads.

Compatibility tests are all built around loading the same file with
`corrosiffpy` and `siffreadermodule` and ensuring they return the same
results. The benchmarks are concentrated around comparing how each
implementation differs in terms of speed when calling exactly the same function.

These tests can be run with `pytest`. From the main repository directory:

```
pytest compatibility
```

To test new features in `corrosiff`, use the `corrosiff` test suite in `Rust`. As
I start to develop new features selectively in `corrosiff`, I will also start making
tests that are specific to the `corrosiffpy` module and actually test functionality
instead of just comparing the `C++` backend. Note that these tests require
`pytest` and `siffpy`, so you'll need to install the `test` optional dependencies.

They are far from exhaustive and do not test every possible error condition, nor
do they test corrupt files (yet).