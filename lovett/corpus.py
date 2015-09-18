# Functions for corpus as list of trees

import collections.abc


class CorpusBase(collections.abc.Sequence):
    pass


class Corpus(CorpusBase, collections.abc.MutableSequence):
    def __init__(self, trees, metadata=None):
        self._trees = list(trees)
        self._metadata = metadata

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
