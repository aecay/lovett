# Functions for corpus as list of trees

import abc
import collections.abc
import lovett.tree


# TODOs:
# - smart iteration: with corpus.trees() as trees: trees.map(...), trees.filter(...)


class CorpusBase(collections.abc.Sequence, metaclass=abc.ABCMeta):
    # TODO
    # @abc.abstractmethod
    # def matching_trees(query):
    #     pass

    pass


class Corpus(CorpusBase, collections.abc.MutableSequence):
    def __init__(self, trees, metadata=None):
        # TODO: deparent all the trees (make copies first?) -- no
        # TODO: a separate class for a ResultSet? (contains copies of trees
        # from corpora, doesn't care about deparenting/setting ids/etc.)
        self._trees = list(trees)
        self._metadata = lovett.tree.Metadata(metadata)

    # Collection implementation
    def __getitem__(self, i):
        return self._trees[i]

    # TODO: should a Corpus be mutable?  Probably yes, to allow building up of
    # corpora programmatically
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
        # TODO: tree viewer, one by one?
        return """<div class="corpus-repr">A Corpus consisting of %s trees</div>""" % len(self)

    # Instance methods
    def to_db(self):
        import lovett.db as db
        d = db.CorpusDb()
        for t in self._trees:
            d.insert_tree(t)
        return d

    def write_penn_treebank(self, handle):
        # TODO: write the corpus in PTB format to the file or other writable
        # object handle
        pass

    # TODO: need parentindex, or move to doubly linked list structure
    # TODO: function to open read-only annotald window on corpus
    # TODO: allow writeback from annotald?
