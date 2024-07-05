# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pkg_resources
import re
import commonmark

py_attr_re = re.compile(r"\:py\:\w+\:(``[^:`]+``)")

def docstring(app, what, name, obj, options, lines):
    md  = '\n'.join(lines)
    ast = commonmark.Parser().parse(md)
    rst = commonmark.ReStructuredTextRenderer().render(ast)
    lines.clear()
    lines += rst.splitlines()

    for i, line in enumerate(lines):
        while True:
            match = py_attr_re.search(line)
            if match is None:
                break 

            start, end = match.span(1)
            line_start = line[:start]
            line_end = line[end:]
            line_modify = line[start:end]
            line = line_start + line_modify[1:-1] + line_end
        lines[i] = line

def setup(app):
    app.connect('autodoc-process-docstring', docstring)
sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Corrosiff-Python'
copyright = '2023-2024, Stephen Thornquist'
author = 'Stephen Thornquist'

# The full version, including alpha/beta/rc tags
release = pkg_resources.get_distribution('corrosiffpy').version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'nbsphinx',
    'sphinx.ext.autodoc',
#    'autodoc2',
    'sphinx_rtd_theme',
    'myst_parser',
    #'myst_nb',
]

# autodoc2_packages = [
#     {
#         "path" : "../../python/corrosiffpy",

#     }
# ]

# autodoc2_render_plugin = "myst"

#html_extra_path = ['_static/corrosiff']

source_suffix = [".rst", ".md"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store','**.ipynb_checkpoints']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']
