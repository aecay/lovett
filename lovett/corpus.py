"""Objects for representing a corpus (list of trees).

TODO: write more here

.. note:: TODO

   - smart iteration::

         with corpus.trees() as trees:
             trees.map(...)
             trees.filter(...)

"""

import abc
import collections.abc
import lovett.tree


class CorpusBase(collections.abc.Sequence, metaclass=abc.ABCMeta):
    """A base class for corpora.

    This class defines the (currently rather thin) interface that corpus
    objects must implement.  It inherits from `Sequence`, since a corpus is an
    (ordered) sequence of trees.

    .. note:: TODO

       The ordering over trees in the corpus isn't total, since there's not
       really a well-defined order across texts.  It would be nice to express
       this programmatically somehow.

       It would be good to use a doubly-linked list structure here, to allow
       fecthing next/previous tree in constant time.  The alternative is for
       trees to know their index within the corpus, which is not really what
       we want if a tree can belong to multiple corpora e.g. when a search
       yields a (sub)corpus as a result.  But see the note above about the
       lack of total ordering...maybe we just have to impose one.

       It would be nice to allow a functionality like the ``fix()`` function
       in the R console, which pops up an editor for a piece of data.  We
       could attempt something similar, whereby the IPython console pops up a
       new browser window running an instance of Annotald, which allows you to
       edit and save back a tree.  But this will be a bit tricky...

    """

    # TODO @abc.abstractmethod
    def matching_trees(query):
        pass


class Corpus(CorpusBase, collections.abc.MutableSequence):
    """A class representing a corpus.

    In addition to the sequence semantics inherited from the `CorpusBase`
    class, this class also implements the `MutableSequence` interface,
    allowing trees to be added and removed.

    .. note::

       This is a different issue than whether trees themselves can be changed;
       the trees are implemented as mutable objects.  The question rather is
       whether the number and sequence of trees in the corpus can be changed.

    Args:
        trees (list of `Tree`): the trees in this corpus.
        metadata (dict): the corpus metadata.

    """
    def __init__(self, trees, metadata=None):
        self._trees = list(trees)
        self._metadata = lovett.tree.Metadata(metadata)

    # Collection implementation
    def __getitem__(self, i):
        return self._trees[i]

    def __setitem__(self, i, val):
        self._trees[i] = val

    def __delitem__(self, i):
        del self._trees[i]

    def __len__(self):
        return len(self._trees)

    def insert(self, i, val):
        self._trees.insert(i, val)

    # Special methods
    def __str__(self):
        return "<Corpus of %s trees>" % len(self)

    def __repr__(self):
        # TODO: is this correct?
        return str(self)

    def _repr_html_(self):
        # TODO: link the word "Corpus" to the documentation?
        # TODO: tree viewer, one by one (for first 10 trees)?
        return """<div class="corpus-repr">A Corpus consisting of %s trees</div>""" % len(self)

    # Instance methods
    def to_db(self):
        """Return a `CorpusDB` object containing the trees from the corpus."""
        import lovett.db as db
        d = db.CorpusDb()
        for t in self._trees:
            d.insert_tree(t)
        return d

    def write_penn_treebank(self, handle):
        """Write the tree in Penn Historical Corpus format to a file.

        .. note:: TODO

           implement this.

        Args:
            handle (writable): an object with a ``write`` method where the
                trees should be written

        """
        pass
