# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from pathlib import Path

from avoca.qa_class import generate_classes_doc
from avoca.utils import flags_doc

this_path = Path(__file__).parent
generate_classes_doc.main(this_path)
flags_doc.main(this_path)

project = "@voc@"
copyright = "2024, Lionel Constantin, Empa"
author = "Lionel Constantin, Empa"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",
    # "myst_parser",
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
