"""Functions for use in the IPython notebook interface."""

from IPython.core.magic import (Magics, magics_class, cell_magic)

import ipywidgets as widgets
from traitlets import Unicode, List, Int

injected = False


@magics_class
class LovettMagics(Magics):
    @cell_magic
    def tree(self, line, cell):
        # TODO: are we sure we like this method of assigning the tree to a
        # variable?
        import lovett.tree as tree
        t = tree.parse(cell)
        if line is not None and line.isidentifier() and not keyword.iskeyword(line):
            self.shell.user_ns[line] = t
        return t

# TODO: is it correct to do this unconditionally?  Should we do it in a
# notebook extension callback or something?
try:
    ip = get_ipython()
    ip.register_magics(LovettMagics)
except:
    pass

class TreeWidget(widgets.DOMWidget):
    _view_name = Unicode("LovettTree").tag(sync=True)
    _view_module = Unicode("lovett").tag(sync=True)

    # TODO: let this be a Tree object instead, and wire up custom
    # de/serializers
    tree = Unicode("").tag(sync=True)

    def __init__(self, json, **kwargs):
        super().__init__(**kwargs)
        self.tree = json


# TODO: a widget that allows the editing of a single tree annotald-style in
# the ipython window.  (Or pops up another window to do it?).  Will allow
# R-like fix() function
