# -*- coding: utf-8 -*-

import os
import AnniesLasso as tc

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "breathe",
]
intersphinx_mapping = {
#    'python': ('https://docs.python.org/3/', None),
#    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
#    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
#    'astropy': ('http://docs.astropy.org/en/stable/', None),
#    'emcee': ('http://dan.iel.fm/emcee/current/', None)
}

breathe_projects = {"celerite": "xml"}
breathe_default_project = "celerite"

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

# General information about the project.
project = "The Cannon"
author = " & contributors"
copyright = "2016, 2017, " + author

version = tc.__version__
release = tc.__version__

exclude_patterns = ["_build"]
pygments_style = "sphinx"

# Readthedocs.
on_rtd = os.environ.get("READTHEDOCS", None) == "True"
if on_rtd:
    import subprocess
    subprocess.call("doxygen Doxyfile", shell=True)
else:
    import sphinx_rtd_theme
    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_context = dict(
    display_github=True,
    github_user="andycasey",
    github_repo="AnniesLasso",
    github_version="refactor",
    conf_py_path="/docs/",
)
html_static_path = ["_static"]
html_show_sourcelink = False
