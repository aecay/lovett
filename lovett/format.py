import abc
import json

import lovett.tree
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


def _postprocess_parsed(l):
    metadata = {}
    if not isinstance(l[0], str):
        # Root node
        tree = None
        id = None
        try:
            while True:
                v = l.pop()
                if v[0] == 'ID':
                    id = v[1]
                elif v[0] == "METADATA":
                    for key, val in v[1:]:
                        metadata[key] = val
                else:
                    if tree:
                        raise ParseError("Too many children of root node (or label-less node)")
                    tree = v
        except IndexError:
            pass
        try:
            r = _postprocess_parsed(tree)
            # TODO: We should instead insert a hash-based id.
            # TODO: think about the differece between id and fingerprint (for
            # backwards compatibility: fingerprint is the hash-based one,
            # which is better)
            for key, val in metadata.items():
                r.metadata[key] = val
            r.metadata.id = id or "MISSING_ID"
            return r
        except ParseError as e:
            print("error in id: %s" % id)
            raise e
    if len(l) < 2:
        raise ParseError("malformed tree: node has too few children: %s" % l)
    if isinstance(l[1], str):
        # Simple leaf
        if len(l) != 2:
            raise ParseError("malformed tree: leaf has too many children: %s" % l)
        label = l[0]
        text = l[1]
        if lovett.util.is_trace_string(l[1]):
            text, idx_type, index = lovett.util.label_and_index(text)
            if index is not None:
                metadata['INDEX'] = index
                metadata['IDX-TYPE'] = idx_type
        else:
            label, idx_type, index = lovett.util.label_and_index(label)
            if index is not None:
                metadata['INDEX'] = index
                metadata['IDX-TYPE'] = idx_type
        return lovett.tree.Leaf(label, text, metadata)
    # Regular node
    label, idx_type, index = lovett.util.label_and_index(l[0])
    if index is not None:
        metadata['INDEX'] = index
        metadata['IDX-TYPE'] = idx_type
    return lovett.tree.NonTerminal(label, map(lambda x: _postprocess_parsed(x), l[1:]), metadata)


class ParseError(Exception):
    pass


class ParseEOF(ParseError):
    pass


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

    @classmethod
    @abc.abstractmethod
    def read(self, handle):
        pass

    # TODO: override __init__ to forbid class instantiation


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
        if set(tree.metadata.keys()) > {"ID"}:
            yield "(METADATA "
            first = False
            for key, val in tree.metadata.items():
                if key == "ID":
                    continue
                if first:
                    yield "\n" + " " * 12
                yield "(%s %s)" % (key, val)
                first = True
            yield ")\n  "
        yield from cls._do_format(tree, 2)
        if "ID" in tree.metadata:
            yield "\n  (ID %s)" % tree.metadata.id
        yield ")"

    @classmethod
    def corpus(cls, corpus):
        yield from intersperse((cls._do_format_root(tree) for tree in corpus), "\n\n")

    @classmethod
    def _tokens(cls, handle):
        tok = ""
        while True:
            r = handle.read(1)
            if r == "":
                raise ParseEOF()
            elif r in "()":
                if tok != "":
                    yield tok
                    tok = ""
                    yield r
                else:
                    yield r
            elif r in " \n\t":
                if tok != "":
                    yield tok
                    tok = ""
                else:
                    pass  # Keep going
            else:
                tok += r

    @classmethod
    def _postprocess(cls, l):
        return _postprocess_parsed(l)  # TODO: inline the method here

    # TODO: make configurable, e.g. whether to add ids (sequentially or hash
    # based), etc.
    @classmethod
    def read(cls, handle):
        stack = []
        for tok in cls._tokens(handle):
            if tok == "(":
                stack.append([])
            elif tok == ")":
                r = stack.pop()
                try:
                    stack[len(stack) - 1].append(r)
                except IndexError:
                    # the final closing bracket
                    return cls._postprocess(r)
            else:
                try:
                    stack[len(stack) - 1].append(tok)
                except Exception:
                    raise ParseError("error with stack: %s" % stack)


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


class Icepahc(Penn):
    @classmethod
    def leaf(cls, node, indent=0):
        r = "".join(super().leaf(node, indent))
        if "LEMMA" in node.metadata:
            r = r[:-1] + "-" + node.metadata.lemma + ")"
        yield r

    @classmethod
    def read(cls, handle):
        tree = super().read(handle)
        for node in tree.nodes():
            if lovett.util.is_leaf(node):
                parts = node.text.split("-")
                if len(parts) > 1:
                    node.metadata.lemma = parts[-1]
                    node.text = "-".join(parts[:-1])
        return tree


class Deep(Bracketed):
    @classmethod
    def _metadata_items(cls, dic):
        items = sorted(dic.items())
        items = filter(lambda x: x[0] != "ID", items)  # TODO: hack
        return list(items)

    @classmethod
    def _print_metadata(cls, node, indent):
        meta_items = cls._metadata_items(node.metadata)
        if len(meta_items) > 0:
            yield "(META "
            yield from intersperse(("({key} {value})".format(key=key, value=value)
                                    for (key, value) in meta_items),
                                   "\n" + " " * (indent + 6))
            yield ")\n" + " " * indent

    @classmethod
    def leaf(cls, node, indent=0):
        yield "({label} ".format(label=node.label)
        yield from cls._print_metadata(node, indent + len(node.label) + 2)
        yield "(ORTHO {text})".format(text=node.text)
        yield ")"

    @classmethod
    def tree(cls, node, indent=0):
        yield "(" + node.label + " "
        newindent = indent + len(node.label) + 2
        yield from cls._print_metadata(node, newindent)
        yield from intersperse((cls._do_format(child, newindent) for child in node.children),
                               "\n" + " " * newindent)
        yield ")"

    @classmethod
    def _find_meta_node(cls, children):
        meta = None
        rest = []
        for node in children:
            if node.label == "META":
                if meta is None:
                    meta = node
                else:
                    raise Exception("Multiple meta nodes")
            else:
                rest.append(node)
        return meta, rest

    @classmethod
    def _add_metadata(cls, tree, keys):
        for node in keys:
            tree.metadata[node.label] = node.text

    @classmethod
    def _postprocess_deep(cls, tree):
        if lovett.util.is_leaf(tree):
            # Coding node or other degenerate leaf
            return tree
        meta, rest = cls._find_meta_node(tree.children)
        if meta is not None:
            cls._add_metadata(tree, meta)
        if len(rest) == 1 and rest[0].label == "ORTHO":
            l = lovett.tree.Leaf(tree.label, rest[0].text, tree.metadata)
            return l
        tree[:] = list(map(cls._postprocess_deep, rest))
        return tree

    @classmethod
    def read(cls, handle):
        tree = super().read(handle)
        return cls._postprocess_deep(tree)


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
