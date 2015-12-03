import ipywidgets as widgets
from traitlets import Unicode, List, Int


class TreesView(widgets.DOMWidget):
    _view_name = Unicode("TreesView", sync=True)

    trees = List(Unicode, sync=True)
    index = Int(sync=True)
    # TODO: Is there a good way to say this is read-only (or more accurately
    # write-once)?
    maxindex = Int(sync=True)

    def __init__(self, trees):
        super().__init__()
        self.trees = trees
        self.index = 0
        self.maxindex = len(trees) - 1
