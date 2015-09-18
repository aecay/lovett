from __future__ import unicode_literals

import abc
import collections.abc

import lovett.util as util


# TODO: make md5 id for trees missing one
ABSENT_ID = "LOVETT_MISSING_ID"


# TODO: add class that lets us do tree.metadata.lemma instead of
# tree.metadata["LEMMA"]


class Tree(abc.ABC):
    __slots__ = ["parent", "metadata", "_label"]

    def __init__(self, label, metadata=None):
        self.parent = None
        # TODO: we might want to parse metadata
        self.metadata = metadata or {}
        label, idxtype, idx = util.label_and_index(label)
        self._label = label
        if idx is not None:
            self.metadata['INDEX'] = idx
            # TODO: what's the standard name
            self.metadata['IDX-TYPE'] = idxtype

    @abc.abstractmethod
    def __eq__(self, other):
        return self.metadata == other.metadata and \
            self._label == other._label

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, new):
        new = new.strip()
        if new == '':
            raise ValueError('Nodes cannot have an empty label.')
        self._label = new

    @property
    def _parent_index(self):
        if self.parent is None:
            return None
        for i, child in enumerate(self.parent):
            if child is self:
                return i
        raise ValueError("Tree not contained in its parent")

    @property
    def left_sibling(self):
        parent_index = self._parent_index
        if self.parent and parent_index > 0:
            return self.parent[parent_index - 1]
        return None

    @property
    def right_sibling(self):
        parent_index = self._parent_index
        if self.parent and parent_index < len(self.parent) - 1:
            return self.parent[parent_index + 1]
        return None

    @property
    def root(self):
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    @property
    def urtext(self):
        r = " ".join(filter(lambda s: s != "", [l.urtext for l in self]))
        # TODO: use metadata instead
        r = r.replace("@ @", "")
        # Hacktacularly delete spaces before punctuation
        r = r.replace(" LOVETT_DEL_SP", "")
        # Also zap space-delete markers at the beginning of the string
        r = r.replace("LOVETT_DEL_SP", "")
        return r.strip()


def _index_string_for_metadata(metadata):
    idx = metadata.get("INDEX")
    idxconn = "=" if metadata.get("IDX-TYPE") == "gap" else "-"
    if idx:
        return idxconn + str(idx)
    return ""


class Leaf(Tree):
    __slots__ = ["text"]

    def __init__(self, label, text, metadata=None):
        super(Leaf, self).__init__(label, metadata)
        self.text = text

    def __str__(self, indent=0):
        idxstr = _index_string_for_metadata(self.metadata)
        text = self.text
        lemma = self.metadata.get("LEMMA")
        if lemma:
            text += "-" + lemma
        if util.is_trace(self):
            return ''.join(['(', self.label, ' ', text, idxstr, ')'])
        else:
            return ''.join(['(', self.label, idxstr, ' ', text, ')'])

    def __repr__(self):
        return "Leaf('%s', '%s', metadata=%r)" % (self.label.replace("'", "\\'"),
                                                  self.text.replace("'", "\\'"),
                                                  self.metadata)

    def __eq__(self, other):
        return super(Leaf, self).__eq__(other) and \
            self.text == other.text

    @property
    def urtext(self):
        # TODO: more excluded node types
        if not util.is_text_leaf(self):
            return ""
        if self.label in [",", "."]:
            # Punctuation: no spaces
            # TODO: grossly hacktacular!
            return "LOVETT_DEL_SP" + self.text
        return self.text

    def _repr_html_(self):
        return """<div class=\"tree-node tree-leaf\">
                  <span class=\"tree-label\">%s</span>
                  <span class=\"tree-text\">%s</span>
                  </div>""" % (self.label, self.text)


class NonTerminal(Tree, collections.abc.MutableSequence):
    __slots__ = ["_children"]

    def __init__(self, label, children, metadata=None):
        # TODO: use *args magic to not need the list brax around children?
        super(NonTerminal, self).__init__(label, metadata)
        # coerce to a list; we don't want any generators to sneak in
        self._children = list(children)
        for child in self._children:  # pragma: no branch
            child.parent = self

    # Abstract methods

    # Equality

    def __eq__(self, other):
        return super(NonTerminal, self).__eq__(other) and \
            len(self) == len(other) and \
            all((x == y for x, y in zip(self, other)))

    # For Container
    def __contains__(self, obj):
        return self._children.__contains__(obj)

    # For Iterable
    def __iter__(self):
        return self._children.__iter__()

    # For Sized
    def __len__(self):
        return len(self._children)

    # For Sequence
    def __getitem__(self, index):
        return self._children[index]

    # For MutableSequence
    def __setitem__(self, index, value):
        value.parent = self
        self._children[index] = value
        # TODO: what should be returned???
        return self._children[index]

    def __delitem__(self, index):
        # TODO: is there a better way to do this?
        if isinstance(index, int):
            self._children[index].parent = None
        else:
            # index is a slice
            for child in self._children[index]:  # pragma: no branch
                child.parent = None
        # TODO: should something be returned?
        del self._children[index]

    def insert(self, index, value):
        value.parent = self
        return self._children.insert(index, value)

    # Properties
    @property
    def children(self):
        return self.__iter__()

    # Methods
    def __repr__(self):
        childstr = ", ".join(repr(c) for c in self)
        return '%s(%r, [%s], metadata=%r)' % (type(self).__name__, self.label,
                                              childstr, self.metadata)

    def __str__(self, indent=0):
        idxstr = _index_string_for_metadata(self.metadata)
        s = "(%s%s " % (self.label, idxstr)
        id = self.metadata.get("ID")
        if id is not None:
            s = "( " + s
        l = len(s)
        leaves = list(map(lambda x: x.__str__(indent + l), self))
        leaves = ("\n" + " " * (indent + l)).join(leaves)
        if id is not None:
            if id == ABSENT_ID:
                leaves += ")"
            else:
                leaves += ")\n  (ID %s)" % self.metadata.get("ID")
        return "".join([s, leaves, ")"])

    def _repr_html_(self):
        return """<div class=\"tree-node\">
                  <span class=\"tree-label\">%s</span>
                  %s
                  </div>""" % (self.label,
                               "".join(map(lambda x: x._repr_html_(), self)))


class ParseError(Exception):
    pass


def _tokenize(string):
    # TODO: corpussearch comments
    tok = ''
    for char in string:
        if char == '(' or char == ')':
            if tok != '':
                yield tok
                tok = ''
            yield char
        elif char in ' \n\t':
            if tok != '':
                yield tok
                tok = ''
            continue
        else:
            tok += char


def _postprocess_parsed(l):
    if not isinstance(l[0], str):
        # Root node
        tree = None
        id = None
        try:
            while True:
                v = l.pop()
                if v[0] == 'ID':
                    id = v[1]
                else:
                    if tree:
                        raise ParseError("Too many children of root node (or label-less node)")
                    tree = v
        except IndexError:
            pass
        try:
            r = _postprocess_parsed(tree)
            r.metadata["ID"] = id or ABSENT_ID
            return r
        except ParseError as e:
            print("error in id: %s" % id)
            raise e
    if len(l) < 2:
        raise ParseError("malformed tree: node has too few children: %s" % l)
    if isinstance(l[1], str):
        m = {}
        # Simple leaf
        if len(l) != 2:
            raise ParseError("malformed tree: leaf has too many children: %s" % l)
        label = l[0]
        text = l[1]
        if util.is_trace_string(l[1]):
            text, idx_type, index = util.label_and_index(text)
            if index is not None:
                m['INDEX'] = index
                m['IDX-TYPE'] = idx_type
        else:
            label, idx_type, index = util.label_and_index(label)
            if index is not None:
                m['INDEX'] = index
                m['IDX-TYPE'] = idx_type
        return Leaf(label, text, m)
    # Regular node
    m = {}
    label, idx_type, index = util.label_and_index(l[0])
    if index is not None:
        m['INDEX'] = index
        m['IDX-TYPE'] = idx_type
    return NonTerminal(label, map(lambda x: _postprocess_parsed(x), l[1:]), m)


# TODO: better parse errors
def parse(string):
    stack = []
    stream = _tokenize(string)
    r = None
    for token in stream:
        if token == '(':
            stack.append([])
        elif token == ')':
            r = stack.pop()
            try:
                stack[len(stack) - 1].append(r)
            except IndexError:
                # the final closing bracket
                break
        else:
            try:
                stack[len(stack) - 1].append(token)
            except Exception:
                raise ParseError("error with stack: %s; string = %s" % (stack, string))

    n = next(stream, None)
    if n is not None:
        raise ParseError("unmatched closing bracket: %s" % r)
    if not len(stack) == 0:
        raise ParseError("unmatched opening bracket: %s" % stack)

    return r and _postprocess_parsed(r)
