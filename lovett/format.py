import abc
import json

import lovett.util


# https://stackoverflow.com/a/5656097
def intersperse(iterable, delimiter):
    it = iter(iterable)
    yield from next(it)
    for x in it:
        yield delimiter
        yield from x


def _index_string_for_metadata(metadata):
    idx = metadata.index
    idxconn = "=" if metadata.idx_type == lovett.util.IDX_GAP else "-"
    if idx:
        return idxconn + str(idx)
    return ""


# TODO: make these class methods, as the class never needs to be instantiated
class Format(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def leaf(cls, node, indent=0):
        pass

    @classmethod
    @abc.abstractmethod
    def tree(cls, node, indent=0):
        pass

    @classmethod
    @abc.abstractmethod
    def corpus(cls, corpus):
        pass


class Bracketed(Format):
    # TODO: can move up to Format class
    @classmethod
    def _do_format(cls, node, indent):
        if lovett.util.is_leaf(node):
            yield from cls.leaf(node, indent)
        else:
            yield from cls.tree(node, indent)

    @classmethod
    def _do_format_root(cls, tree):
        yield "( "
        yield from cls._do_format(tree, 2)
        if "ID" in tree.metadata:
            yield "\n  (ID %s)" % tree.metadata.id
        yield ")"


class Penn(Bracketed):
    @classmethod
    def leaf(cls, node, indent=0):
        idxstr = _index_string_for_metadata(node.metadata)
        if lovett.util.is_trace(node):
            fmtstr = "({label} {text}{index})"
        else:
            fmtstr = "({label}{index} {text})"
        yield fmtstr.format(label=node.label,
                            text=node.text,
                            index=idxstr)

    @classmethod
    def tree(cls, node, indent=0):
        pre = "(" + node.label + _index_string_for_metadata(node.metadata) + " "
        newindent = len(pre) + indent
        yield pre
        yield from intersperse((cls._do_format(child, newindent) for child in node.children), "\n" + " " * newindent)
        yield ")"

    @classmethod
    def corpus(cls, corpus):
        yield from intersperse((cls._do_format_root(tree) for tree in corpus), "\n\n")


class Deep(Bracketed):
    @classmethod
    def _metadata(cls, metadata, indent):
        yield from intersperse(("({key} {value})".format(key=key, value=value) for (key, value) in metadata.items()),
                               "\n" + " " * (6 + indent))

    @classmethod
    def leaf(cls, node, indent=0):
        yield "({label} (ORTHO {text})".format(label=node.label, text=node.text)
        if len(node.metadata) > 0:
            newindent = (indent + len(node.label) + 2)
            yield "\n{pad}(META ".format(pad=" " * newindent)
            yield from cls._metadata(node.metadata, newindent)
            yield ")"
        yield ")"

    @classmethod
    def tree(cls, node, indent=0):
        yield "(" + node.label + " "
        newindent = (indent + len(node.label) + 2)
        if len(node.metadata) > 0:
            yield "\n{pad}(META ".format(pad=" " * newindent)
            yield from cls._metadata(node.metadata, newindent)
            yield ")"
        yield from intersperse((cls._do_format(child, newindent) for child in node.children),
                               "\n" + " " * newindent)
        yield ")"


class Json(Format):
    @classmethod
    def _return(cls, obj):
        yield json.dumps(obj, indent=4)

    @classmethod
    def _format(cls, node):
        if lovett.util.is_leaf(node):
            return cls._leaf(node)
        else:
            return cls._tree(node)

    @classmethod
    def _leaf(cls, node):
        m = dict(node.metadata)
        return {"label": node.label,
                "text": node.text,
                "metadata": m}

    @classmethod
    def leaf(cls, node, _indent=0):
        yield from cls._return(cls._leaf(node))

    @classmethod
    def _tree(cls, node, _indent=0):
        return {"label": node.label,
                "metadata": dict(node.metadata),
                "children": [cls._format(c) for c in node.children]}

    @classmethod
    def tree(cls, node, _indent=0):
        yield from cls._return(cls._tree(node))

    @classmethod
    def corpus(cls, corpus):
        yield from cls._return([cls._format(tree) for tree in corpus])
