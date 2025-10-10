# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "VCP CLI"
copyright = "2025, Chan Zuckerberg Initiative"
author = "Chan Zuckerberg Initiative"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_new_tab_link",
    "sphinx_click",
]

myst_heading_anchors = 5

myst_enable_extensions = [
    "colon_fence",
    "linkify",
]

suppress_warnings = ["myst.header", "myst.xref_missing"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "usage/models.md", "_schemas"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = False
html_favicon = "_static/favicon.ico"
