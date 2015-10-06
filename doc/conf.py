# General settings

source_suffix = [".rst"]
extensions = ["sphinx.ext.autodoc",
              "sphinx.ext.intersphinx",
              # "sphinx.ext.mathjax",
              "sphinx.ext.coverage",
              "sphinx.ext.viewcode",  # Or linkcode -> github?
              "sphinx.ext.napoleon"]

autodoc_default_flags = ["members", "undoc-members", "private-members",
                         "special-members"]
autodoc_member_order = "bysource"

intersphinx_mapping = {'python': ('https://docs.python.org/3.5', None),
                       'sqlalchemy': ('http://docs.sqlalchemy.org/en/rel_1_0', None)}

master_doc = "index"

exclude_patterns = ["org/*"]

default_role = "any"

nitpicky = True

# Project settings

project = "Lovett"

copyright = "2015, Aaron Ecay"

version = "0.0"

add_function_parentheses = False

add_module_names = False

trim_footnote_reference_space = True

# Skip stupid autodoc stuff


def maybe_skip_member(app, what, name, obj, skip, options):
    if name in ["__weakref__", "__module__", "__doc__",
                "__dict__", "__abstractmethods__"] or name.startswith("_abc_"):
        return True
    return False


def setup(app):
    app.connect('autodoc-skip-member', maybe_skip_member)
