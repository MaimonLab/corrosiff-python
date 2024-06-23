# Corrosiff-Py

A hybrid `Python` and `Rust` package that wraps the
`corrosiff` library for reading .siff files and
presents a `Python` API.

Installation from source
--------------------------

Everyone has a bunch of different `Python`
installations and different solutions for
managing them.

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

```