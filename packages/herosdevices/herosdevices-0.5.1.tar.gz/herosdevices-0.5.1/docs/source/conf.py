"""Documentation configuration file for sphinx."""  # noqa:INP001

import datetime
import subprocess
import sys
from pathlib import Path

import tomllib
from sphinx.util import logging

log = logging.getLogger(__name__)

# Add the project's src directory to sys.path
sys.path.insert(0, str(Path("../../src").resolve()))

# -- Project information -----------------------------------------------------
pyproject_path = Path(__file__).parents[2] / "pyproject.toml"

with pyproject_path.open("rb") as f:
    pyproject_data = tomllib.load(f)

project = pyproject_data["project"]["name"]


def get_version() -> str:
    """Get version from dynamic versioning."""
    try:
        result = subprocess.run(
            ["hatch", "version"],  # noqa: S607
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        log.exception("Failed to get version from hatch: %s")
        return "unknown"


release = get_version()

version = release

# Extract author names
authors = [author["name"] for author in pyproject_data["project"]["authors"]]

# Build copyright
project = "Heros Devices"
year = datetime.datetime.now(tz=datetime.UTC).year
authors_str = ", ".join(authors)
copyright = f"{year}, {authors_str}"  # noqa: A001
author = authors_str

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.inheritance_diagram",
    "autoapi.extension",
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.mathjax",  # Enable MathJax for LaTeX-style math
    "sphinx.ext.todo",  # Enable todo lists
    "sphinx_autodoc_typehints",  # Handle type hints in documentation
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["../_static"]
# Furo theme options
html_theme_options = {
    "light_logo": "logo.svg",
    "dark_logo": "logo.svg",
    "sidebar_hide_name": False,
}

# Autodoc settings
autoclass_content = "both"
autodoc_default_options = {
    "members": None,
    "member-order": "bysource",
    "show-inheritance": None,
    "private-members": None,
    "inherited-members": None,
}
autodoc_mock_imports = ["serial", "ids_peak", "toptica", "picosdk", "dcamsdk4"]
# -- AutoAPI configuration ---------------------------------------------------
autoapi_options = ["members", "undoc-members", "show-inheritance", "inherited-members"]
autoapi_type = "python"
autoapi_dirs = ["../../src"]  # Path to your source code
autoapi_add_toctree_entry = True  # Avoid duplicate toctree entries
autoapi_keep_files = False  # Keep intermediate reStructuredText files
# todo conf
todo_include_todos = True

intersphinx_mapping = {
    "herostools": ("https://herostools-0faae3.gitlab.io/", None),
    "boss": ("https://boss-eb4966.gitlab.io/", None),
    "heros": ("https://heros-761c0f.gitlab.io/", None),
    "atomiq": ("https://atomiq-atomiq-project-515d34b8ff1a5c74fcf04862421f6d74a00d9de1b.gitlab.io/", None),
}
