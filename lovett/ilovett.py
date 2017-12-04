"""Functions for use in the IPython notebook interface."""

from IPython.display import display, HTML
from IPython.core.magic import (Magics, magics_class, cell_magic)
import pkg_resources
import keyword


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


def initialize():
    global injected
    injected = True
    try:
        ip = get_ipython()
        ip.register_magics(LovettMagics)
    except:
        pass
    return display(HTML("""<script>$("head").append($("<style type='text/css' />").text('%s'));</script>""" %
                        open(pkg_resources.resource_filename("lovett", "css/ipython.css")).read().replace("\n", "\\n") +
                        "<script>%s</script>" % open(pkg_resources.resource_filename("lovett", "js/widget.js")).read()))


# TODO: a widget that allows the editing of a single tree annotald-style in
# the ipython window.  (Or pops up another window to do it?).  Will allow
# R-like fix() function
