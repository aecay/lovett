"""Objects for representing a corpus (list of trees).

TODO: write more here

.. note:: TODO

   - smart iteration::

         with corpus.trees() as trees:
             trees.map(...)
             trees.filter(...)

"""
from IPython.display import display
import abc
import collections.abc
import json

import lovett.tree
import lovett.ilovett
import lovett.widgets
import lovett.format


class CorpusBase(collections.abc.Sequence, metaclass=abc.ABCMeta):
    """A base class for corpora.

    This class defines the (currently rather thin) interface that corpus
    objects must implement.  It inherits from `collections.abc.Sequence`,
    since a corpus is an (ordered) sequence of trees.

    .. note:: TODO

       The ordering over trees in the corpus isn't total, since there's not
       really a well-defined order across texts.  It would be nice to express
       this programmatically somehow.

       On another note, it would be good to use a doubly-linked list structure
       here, to allow fecthing next/previous tree in constant time.  The
       alternative is for trees to know their index within the corpus, which
       is not really what we want if a tree can belong to multiple corpora
       e.g. when a search yields a (sub)corpus as a result.  But see the note
       above about the lack of total ordering...maybe we just have to impose
       one.

       It would be nice to allow a functionality like the ``fix()`` function
       in the R console, which pops up an editor for a piece of data.  We
       could attempt something similar, whereby the IPython console pops up a
       new browser window running an instance of Annotald, which allows you to
       edit and save back a tree.  But this will be a bit tricky...

    """

    @abc.abstractmethod
    def matching_trees(query):
        """Return the trees from this corpus that match a query.

        The query is matched to the trees recursively: if any internal node of
        the tree matches the query, then the whole tree is returned.

        .. note:: TODO

            Currently this function just returns the root trees containing a
            match, not the matched subtrees themselves.  The latter
            functionality might also prove useful...

        Args:
            query (Query): The query to match.

        Returns:
            ResultSet: The matching trees.

        """
        # TODO: use a roots arg to specify a query to bound recursion.  If
        # we get a structure like (IP (NP ...) (VB ...) (NP ... (CP-REL
        # (IP-SUB ...)))), a complicated `query`, and roots=Q.label("IP"), we
        # will only match the query to the (in this case two) nodes that match
        # the root query, and not test every node in the tree.  TODO:
        # implement this in the db backend as well (just AND together the
        # query and the root query?)  TODO: figure out if this would actually
        # be an optimization
        raise NotImplemented

    def to_db(self):
        """Return a `CorpusDb` object containing the trees from the corpus."""
        import lovett.db as db
        if isinstance(self, db.CorpusDb):
            return self
        db = db.CorpusDb()
        db.insert_trees(self)
        return db

    def to_corpus(self):
        """Return a `Corpus` object containing the trees from the corpus."""
        if isinstance(self, Corpus):
            return self
        c = Corpus([], self._metadata)
        # We do this rather than Corpus(self, metadata) in order to get
        # properly mutable trees from a database corpus
        for t in self:
            c.append(t)
        return c

    def write_penn_treebank(self, handle):
        """Write this corpus in Penn Treebank format to a file handle.

        Args:
            handle: an object with a ``write`` method that will handle
                the I/O for writing the trees

        TODO: deprecate

        """
        handle.write(self.format(lovett.format.Penn))

    def write_json(self, handle):  # TODO: no, we actually want a json list
        """Write this corpus in JSON format to a file handle.

        .. note:: TODO

            Document the JSON format, and add a link to that documentation here

        Args:
            handle: an object with a ``write`` method that will handle
                the I/O for writing the trees

        TODO: deprecate

        """
        for t in self:
            handle.write(t.format(lovett.format.Json))
            handle.write("\n")

    def _ipython_display_(self, **kwargs):
        if lovett.ilovett.injected:
            lovett.widgets.TreesView(self)._ipython_display_()
        else:
            display(repr(self))

    def __repr__(self):
        return "<%s of %d trees>" % (type(self), len(self))

    def __str__(self):
        return repr(self)

    def format(self, formatter):
        return "".join(formatter.corpus(self))


class ListCorpus(CorpusBase):
    """This class defines a `CorpusBase` that is backed by a Python list of `Tree` obejcts.

    It exists in order to group common functionality of `Corpus` and
    `ResultSet` objects.

    Args:
        trees (list): List of `Tree` objects.
        metadata (dict): Metadata for this corpus.

    """
    def __init__(self, trees, metadata=None):
        self._trees = list(trees)
        self._metadata = lovett.tree.Metadata(metadata)

    # Collection implementation
    # TODO: make sure that anything which is inserted is actually a Tree.
    def __getitem__(self, i):
        return self._trees[i]

    def __len__(self):
        return len(self._trees)

    def matching_trees(self, query):
        return ResultSet([t for t in self if t.filter_nodes(query.match_tree)],
                         query,
                         metadata=self._metadata)


class Corpus(ListCorpus, collections.abc.MutableSequence):
    """A class representing a (mutable) corpus.

    In addition to the sequence semantics inherited from the `CorpusBase`
    class, this class also implements the `collections.abc.MutableSequence`
    interface, allowing trees to be added and removed.

    .. note::

        This is a different issue than whether trees themselves can be changed;
        the trees are implemented as mutable objects.  The question rather is
        whether the number and sequence of trees in the corpus can be changed.

    Args:
        trees (list of `Tree`): The trees in this corpus.
        metadata (dict): The corpus metadata.

    """

    def __init__(self, trees, metadata=None):
        super().__init__(trees, metadata)

    # Mutable collection implementation
    def __setitem__(self, i, val):
        self._trees[i] = val

    def __delitem__(self, i):
        del self._trees[i]

    def insert(self, i, val):
        self._trees.insert(i, val)


class ResultSet(ListCorpus):
    """This class wraps a list of results from a query.

    It arranges for the original query to be displayed in the IPython
    notebook, and for matching tree nodes to be highlighted.

    """
    def __init__(self, trees, query, metadata=None):
        super().__init__(trees, metadata)
        self._query = query

    def __repr__(self):
        return "%d results of query \"%s\"" % (len(self._trees), self._query)

    def __str__(self):
        return repr(self)

    def _ipython_display_(self):
        if lovett.ilovett.injected:
            lovett.widgets.ResultsView(self, self._query)._ipython_display_()
        else:
            display(repr(self))


# TODO: rename to from_handle to better respect the working...or add
# "from_path" fn for the other case
def from_file(fin, fmt):
    trees = []
    try:
        while True:
            trees.append(fmt.read(fin))
    except lovett.format.ParseEOF:
        pass
    return ListCorpus(trees)


def from_json(str):
    trees = json.loads(str)
    return from_objects(trees)


def from_objects(trees):
    return lovett.format._Object.read(trees)
