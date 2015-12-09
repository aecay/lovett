import ipywidgets
from traitlets import Unicode, Int

# TODO: why does running a cell with a ResultsView result twice advance the
# tree viewer?


def get_tree(widget, content, buffers):
    if "action" in content and content["action"] == "get-tree":
        widget.html = widget.trees[content["index"]]._repr_html_()


class TreesView(ipywidgets.DOMWidget):
    _view_name = Unicode("TreesView", sync=True)

    index = Int(sync=True)
    # TODO: Is there a good way to say this is read-only (or more accurately
    # write-once)?
    maxindex = Int(sync=True)
    html = Unicode("", sync=True)

    def __init__(self, trees):
        super().__init__()
        self.trees = trees
        self.index = 0
        self.maxindex = len(trees) - 1
        self.begin()

    def begin(self):
        self.on_msg(get_tree)


def get_tree_resultsview(widget, content, buffers):
    if "action" in content and content["action"] == "get-tree":
        tree = widget.trees[content["index"]]
        widget._query.colorize_tree(tree)
        widget.html = tree._repr_html_()


class ResultsView(TreesView):
    _view_name = Unicode("ResultsView", sync=True)
    query_html = Unicode(sync=True)

    def __init__(self, trees, query):
        # TODO: should we make a copy of the query here?
        self._query = query
        self._query.colorize()
        self.query_html = self._query._repr_html_()
        super().__init__(trees)

    def begin(self):
        self.on_msg(get_tree_resultsview)
