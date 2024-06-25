# Corrosiff-Python

A hybrid `Python` and `Rust` package that wraps the
`corrosiff` library for reading .siff files and
presents a `Python` API.

TODOS:

-   As always, more documentation.
-   Test suite that does not rely on my local files!

Installation with a package manager
----------------------------------

I'm starting to host things on PyPI and a private
`conda` channel (`maimon-forge` on the Rockefeller
server). Watch this space for updates....

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

lifetime, intensity, _ = siffio.get_frames_flim(frames = list(range(200)))

```

Testing
----------

Testing in this module, right now, is intended mostly to test that
the `C++` and `Rust` implementations agree on all files. As such
the tests are all built around loading the same file with
`corrosiffpy` and `siffreadermodule` and ensuring they return the same
results. The benchmarks are concentrated around comparing how each
implementation differs in terms of speed when calling exactly the same function.

Tests can be run with `pytest`. From the main repository directory:

```
pytest compatibility_tests
```

To test new features in `corrosiff`, use the `corrosiff` test suite in `Rust`. As
I start to develop new features selectively in `corrosiff`, I will also start making
tests that are specific to the `corrosiffpy` module and actually test functionality
instead of just comparing the `C++` backend. Note that these tests require
`pytest` and `siffpy`, so you'll need to install the `test` optional dependencies.