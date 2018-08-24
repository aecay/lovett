from __future__ import unicode_literals

import abc
import collections.abc
import io
import re
import unicodedata

from yattag import Doc

import lovett.util as util
import lovett.format            # TODO: this import is circular


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


class Metadata(collections.abc.MutableMapping):
    """A class that wraps a metadata dict of a py:class:`Tree`.

    Objects of this class support both dict-style (``dict['KEY']``) as well as
    object-style (``dict.key``) lookup.  Key names in the corpus file are all
    uppercase, with words separated by hyphens.  These names are used as-is in
    dict-style lookup.  For object-style lookup, the names are translated to
    lowercase and hyphens are converted to underscores.  Thus both
    ``metadata['OLD-TAG']`` and ``metadata.old_tag`` refer to the same key.

    The key `"LEMMA"` is treated specially: all lemmata are `NFD normalized
    <https://unicode.org/reports/tr15/>`_.

    """
    __slots__ = ("_dict",)

    def __init__(self, dic):
        if dic is None:
            self._dict = {}
        elif isinstance(dic, collections.abc.Mapping):
            if "LEMMA" in dic:
                dic["LEMMA"] = unicodedata.normalize("NFD", dic["LEMMA"])
            self._dict = dict(dic)
        else:
            raise ValueError("Metadata must be initialized with a mapping.")

    def __getitem__(self, name):
        r = self._dict[_check_metadata_name(name)]
        return r

    def __setitem__(self, name, value):
        name = _check_metadata_name(name)
        if name == "LEMMA":
            value = unicodedata.normalize("NFD", value)
        self._dict[name] = value

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
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        name = _check_metadata_name(name)
        self[name] = value

    def __delattr__(self, name):
        name = _check_metadata_name(name)
        try:
            del self[name]
        except KeyError:
            pass

    def __str__(self):
        return str(self._dict)

    def __repr__(self):
        return repr(self._dict)


class Tree(metaclass=abc.ABCMeta):
    __slots__ = ["parent", "_metadata", "_label"]

    def __init__(self, label, metadata=None):
        self.parent = None
        self._metadata = Metadata(metadata or {})
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
    def left_siblings(self):
        parent_index = self._parent_index
        if self.parent and parent_index > 0:
            return self.parent[0:parent_index]
        # TODO: Is this the right thing?  We don't distinguish between the
        # root node and a left-most daughter; both are represented by an empty
        # sequence.  OTOH, if we return None for the root node (as we do in
        # the singular left_sibling case), callers constantly must test our
        # return value for None-ness
        return ()

    @property
    def right_sibling(self):
        parent_index = self._parent_index
        if self.parent and parent_index < len(self.parent) - 1:
            return self.parent[parent_index + 1]
        return None

    @property
    def right_siblings(self):
        parent_index = self._parent_index
        if self.parent and parent_index < len(self.parent) - 1:
            return self.parent[parent_index + 1:]
        return ()

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

    def has_label(self, *args):
        if len(args) > 1:
            return self.has_label(args)
        label = args[0]
        if isinstance(label, str):
            return self.label == label or self.label.startswith(label + "-")
        elif isinstance(label, re._pattern_type):
            return label.match(self.label) is not None
        else:
            return any((self.has_label(l) for l in list(label)))

    def _has_dash_tag_inner(self, tag):
        return self.label.endswith("-" + tag) or ("-" + tag + "-") in self.label

    def has_dash_tag(self, *tags):
        if len(tags) > 1:
            return self.has_dash_tag(tags)
        tag = tags[0]
        if isinstance(tag, str):
            return self._has_dash_tag_inner(tag)
        return any(self._has_dash_tag_inner(t) for t in tag)

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, new_meta):
        self.metadata = Metadata(new_meta)


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
        # TODO: this is quite weird!  But we want to maintain the safety
        # checks and the parent property setting etc.  The alternative is to
        # segregate this stuff into a separate class which is returned from
        # here, and not have the tree class itself be a sequence
        return self
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


def from_object(o):
    return lovett.format._Object.read(o)


def parse(str, format=lovett.format.Penn):
    handle = io.StringIO(str)
    return format.read(handle)
