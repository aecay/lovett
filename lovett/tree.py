from __future__ import unicode_literals

import abc
import collections.abc
import re
import unicodedata

from yattag import Doc

import lovett.util as util
import lovett.format


# TODO: make md5 id for trees missing one
ABSENT_ID = "LOVETT_MISSING_ID"

# TODO: need read-only attribute for trees, from indexed corpora


_METADATA_KEY_RX = re.compile("^[A-Z0-9-]+$")


def _check_metadata_name(name):
    if name in util.INTERNAL_METADATA_KEYS:
        return name
    name_t = name.upper().replace("_", "-")
    if (not _METADATA_KEY_RX.match(name_t)) or name.startswith("-") or \
       name.endswith("-") or name == "GET":
        raise ValueError("Illegal metadata key name %s (interpreted as %s)" %
                         (name, name_t))
    return name_t


class LemmaProxy(str):
    # Modeled on https://stackoverflow.com/a/33272874
    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

    def __hash__(self):
        return super().__hash__()

    def __getattribute__(self, name):
        if name == "__eq__":
            return super().__getattribute__(name)
        elif name in dir(str):  # only handle str methods here
            def method(self, *args, **kwargs):
                value = getattr(super(), name)(*args, **kwargs)
                # not every string method returns a str:
                if isinstance(value, str):
                    return type(self)(value)
                elif isinstance(value, list):
                    return [type(self)(i) for i in value]
                elif isinstance(value, tuple):
                    return tuple(type(self)(i) for i in value)
                else:  # dict, bool, or int
                    return value
            return method.__get__(self)  # bound method
        else:  # delegate to parent
            return super().__getattribute__(name)

    def __eq__(self, other):
        return unicodedata.normalize("NFD", str(self)) == \
            unicodedata.normalize("NFD", str(other))


class Metadata(collections.abc.MutableMapping):
    """A class that wraps a metadata dict of a py:class:`Tree`.

    Objects of this class support both dict-style (``dict['KEY']``) as well as
    object-style (``dict.key``) lookup.  Key names in the corpus file are all
    uppercase, with words separated by hyphens.  These names are used as-is in
    dict-style lookup.  For object-style lookup, the names are translated to
    lowercase and hyphens are converted to underscores.  Thus both
    ``metadata['OLD-TAG']`` and ``metadata.old_tag`` refer to the same key.

    """
    __slots__ = ("_dict",)

    def __init__(self, dic):
        if dic is None:
            self._dict = {}
        elif isinstance(dic, collections.abc.Mapping):
            self._dict = dict(dic)
        else:
            raise ValueError("Metadata must be initialized with a mapping.")

    def __getitem__(self, name):
        r = self._dict[_check_metadata_name(name)]
        if name == "LEMMA":
            return LemmaProxy(r)
        return r

    def __setitem__(self, name, value):
        self._dict[_check_metadata_name(name)] = value

    def __delitem__(self, name):
        del self._dict[_check_metadata_name(name)]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __getattr__(self, name):
        if name == "get":
            return self._dict.get
        if name.startswith("_"):
            return super().__getitem__(name)
        name = _check_metadata_name(name)
        try:
            if name == "LEMMA":
                return LemmaProxy(self._dict[name])
            return self._dict[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        name = _check_metadata_name(name)
        self._dict[name] = value

    def __delattr__(self, name):
        name = _check_metadata_name(name)
        try:
            del self._dict[name]
        except KeyError:
            pass

    def __str__(self):
        return str(self._dict)

    def __repr__(self):
        return repr(self._dict)


class Tree(metaclass=abc.ABCMeta):
    __slots__ = ["parent", "metadata", "_label"]

    def __init__(self, label, metadata=None):
        self.parent = None
        self.metadata = Metadata(metadata or {})
        label, idxtype, idx = util.label_and_index(label)
        self._label = label
        if idx is not None:
            self.metadata.index = idx
            # TODO: what's the standard name
            self.metadata.idx_type = idxtype

    @abc.abstractmethod
    def __eq__(self, other):
        return self.metadata == other.metadata and \
            self._label == other._label

    def __str__(self):
        return self.format(lovett.format.Penn)

    @abc.abstractmethod
    def __repr__(self):
        pass

    def format(self, formatter):
        return "".join((x for x in formatter.node(self, indent=0)))

    @abc.abstractmethod
    def _repr_html_(self):
        pass

    def _label_html(self, doc):
        doc, tag, txt = doc.tagtext()
        with tag("span", klass="tree-label"):
            colors = self.metadata.get("query_match_colors", ())
            if len(colors) > 0:
                doc.attr(style="color: %s;" % colors[0])
            txt(self.label)
            if len(colors) > 1:
                for color in colors[1:]:
                    with tag("span", style="color: %s;" % color):
                        txt("✓")

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

    @property
    def id(self):
        return self.root.metadata.id

    @abc.abstractmethod
    def nodes(self):
        pass

    def has_label(self, label):
        if isinstance(label, str):
            return self.label == label or self.label.startswith(label + "-")
        elif isinstance(label, re._pattern_type):
            return label.match(self.label) is not None
        else:
            # Use sorted to linearize a set
            return any((self.has_label(l) for l in sorted(label)))

    def has_dash_tag(self, tag):
        return self.label.endswith("-" + tag) or ("-" + tag + "-") in self.label


def _index_string_for_metadata(metadata):
    idx = metadata.index
    idxconn = "=" if metadata.idx_type == util.IDX_GAP else "-"
    if idx:
        return idxconn + str(idx)
    return ""


class Leaf(Tree):
    __slots__ = ["text"]

    def __init__(self, label, text, metadata=None):
        super(Leaf, self).__init__(label, metadata)
        self.text = text

    def __repr__(self):
        return "Leaf('%s', '%s'%s)" % (self.label.replace("'", "\\'"),
                                       self.text.replace("'", "\\'"),
                                       ", metadata=%r" % self.metadata if self.metadata != {} else "")

    def __eq__(self, other):
        return super(Leaf, self).__eq__(other) and \
            self.text == other.text

    @property
    def urtext(self):
        # TODO: more excluded node types
        if not util.means_leaf(self):
            return ""
        if self.label in [",", "."]:
            # Punctuation: no spaces
            # TODO: grossly hacktacular!
            return "LOVETT_DEL_SP" + self.text
        return self.text

    def _repr_html_(self):
        doc, tag, txt = Doc().tagtext()
        with tag("div", klass="tree-node tree-leaf"):
            self._label_html(doc)
            with tag("span", klass="tree-text"):
                txt(self.text)
        return doc.getvalue()

    def nodes(self):
        yield self


class NonTerminal(Tree, collections.abc.MutableSequence):
    __slots__ = ["_children"]

    def __init__(self, label, children, metadata=None):
        super(NonTerminal, self).__init__(label, metadata)
        # Coerce to a list; we don't want any generators to sneak in
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
        # TODO: remove parent ref on old child(ren)
        if isinstance(index, int):
            if not isinstance(value, Tree):
                raise ValueError("Can't place a non-Tree into a Tree: %s" % value)
            value.parent = self
        else:
            # index is a slice
            for child in value:
                if not isinstance(child, Tree):
                    raise ValueError("Can't place a non-Tree into a Tree: %s" % value)
                child.parent = self

        self._children[index] = value

    def __delitem__(self, index):
        # TODO: is there a better way to do this?
        if isinstance(index, int):
            self._children[index].parent = None
        else:
            # index is a slice
            for child in self._children[index]:  # pragma: no branch
                child.parent = None
        del self._children[index]

    def insert(self, index, value):
        if not isinstance(value, Tree):
            raise ValueError("Can't place a non-Tree into a Tree: %s" % value)
        value.parent = self
        return self._children.insert(index, value)

    # Properties
    @property
    def children(self):
        return self.__iter__()
    # TODO: setter

    # Methods
    def __repr__(self):
        childstr = ", ".join(repr(c) for c in self)
        return '%s(%r, [%s]%s)' % (type(self).__name__,
                                   self.label,
                                   childstr,
                                   ", metadata=%r" % self.metadata if self.metadata != {} else "")

    def _repr_html_(self):
        doc, tag, txt = Doc().tagtext()
        with tag("div", klass="tree-node"):
            self._label_html(doc)
            doc.asis("".join(map(lambda x: x._repr_html_(), self)))
        return doc.getvalue()

    def nodes(self):
        yield self
        for child in self:
            yield from child.nodes()


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
            r.metadata.id = id or ABSENT_ID
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
        if util.is_trace_string(l[1]):
            text, idx_type, index = util.label_and_index(text)
            if index is not None:
                metadata['INDEX'] = index
                metadata['IDX-TYPE'] = idx_type
        else:
            label, idx_type, index = util.label_and_index(label)
            if index is not None:
                metadata['INDEX'] = index
                metadata['IDX-TYPE'] = idx_type
        return Leaf(label, text, metadata)
    # Regular node
    label, idx_type, index = util.label_and_index(l[0])
    if index is not None:
        metadata['INDEX'] = index
        metadata['IDX-TYPE'] = idx_type
    return NonTerminal(label, map(lambda x: _postprocess_parsed(x), l[1:]), metadata)


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


def from_object(o):
    return lovett.format._Object.read(o)
