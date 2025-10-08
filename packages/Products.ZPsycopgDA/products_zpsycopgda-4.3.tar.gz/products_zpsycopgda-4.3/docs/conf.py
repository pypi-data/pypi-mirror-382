# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
import os

import pkginfo


parent = os.path.dirname(os.path.dirname(__file__))
parent_dir = os.path.abspath(parent)
pkg_info = pkginfo.Develop(parent_dir)
pkg_version = pkg_info.version or ''
year = datetime.datetime.now().year

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Products.ZPsycopgDA'
copyright = '2012-%i Federico Di Gregorio and Contributors' % year
author = 'Federico Di Gregorio and Contributors'

# The short X.Y version.
version = pkg_version.replace('.dev0', '')
# The full version, including alpha/beta/rc tags.
release = pkg_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
