Installation
=============

Installation with a package manager
----------------------------------

This will hopefully be available in a local
``conda`` channel soon, but for now you can use
the latest stable version from ``PyPI``.

```
pip install corrosiffpy
```

Installation from source
--------------------------

Everyone has a bunch of different ``Python``
installations and different solutions for
managing them. Because this package relies on
``Rust``, if you're installing from source
you need a ``Rust`` compiler. The main way to manage
``Rust`` and its dependencies is `cargo <https://doc.rust-lang.org/cargo/getting-started/installation.html>`_.
Once you have ``cargo`` you can install with ``pip`` or
``maturin``.

## Install to a local environment

### pip

You can use your interpreter's ``pip`` with
the ``pyproject.toml`` location in ``corrosiff-python``.

```sh
(venv) cd path/to/corrosiff-python
(venv) pip install .
```

### Maturin

This can be installed using ``maturin``, the
current preferred ``PyO3`` installation tool. It's
a ``Python`` package that can be installed from ``PyPI``
with ``pip``.

``pip install maturin``

To use maturin, you can navigate to the ``corrosiff-python``
directly and then execute

```
maturin develop --release
```

in the command line, which will use the system ``Python``
distribution to install this library.