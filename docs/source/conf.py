""" Configuration file for the Sphinx documentation builder. """
#import importlib.util
import pathlib
import sys
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
#spec = importlib.util.spec_from_file_location("Version", "../../LogP.py")
#foo = importlib.util.module_from_spec(spec)
#sys.modules["Version"] = foo
#spec.loader.exec_module(foo)
#Version = foo.Version
from LogP import Version

project = 'pcs_log'
copyright = '2022, Ing. Rainer Pietsch'
author = 'Ing. Rainer Pietsch'
release = '.'.join(Version.split('.')[:2])
#release = '1.6'
version = Version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'alabaster'
#html_theme = 'classic'
html_theme = 'sphinx_rtd_theme'
#html_theme = 'furo'
html_static_path = ['_static']

# EPUB options
epub_show_urls = 'footnote'
