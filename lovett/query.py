import abc
import re
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import union, intersect


class QueryFunction(abc.ABC):
    @abc.abstractmethod
    def match_tree(self, tree):
        pass

    # TODO: obviously
    # @abc.abstractmethod
    # def sql(self, corpus):
    #     pass

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)

    @abc.abstractmethod
    def __str__(self):
        pass


class And(QueryFunction):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def match_tree(self, tree):
        # TODO: why do we not use short-circuit evaluation here?  The logic is
        # copied from lovett1
        res = self.left.match_tree(tree)
        if not res:
            return res
        return self.right.match_tree(tree)

    def sql(self, corpus):
        return intersect(self.left.sql(corpus), self.right.sql(corpus))

    def __str__(self):
        # TODO: we add lots of extra parens to make sure we're getting scoping
        # rules right...can we cut down on this? maybe only add parens for or,
        # not and?
        return "(" + str(self.left) + " & " + str(self.right) + ")"


class Or(QueryFunction):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def match_tree(self, tree):
        res = self.left.match_tree(tree)
        if res:
            return res
        return self.right.match_tree(tree)

    def sql(self, corpus):
        return union(self.left.sql(corpus), self.right.sql(corpus))

    def __str__(self):
        return "(" + str(self.left) + " | " + str(self.right) + ")"


class Not(QueryFunction):
    def __init__(self, fn):
        self.fn = fn

    def match_tree(self, tree):
        if self.fn.match_tree(tree):
            return None
        else:
            return tree

    def __str__(self):
        return "~" + str(self.fn)


class daughter(QueryFunction):
    def __init__(self, query):
        self.query = query

    def match_tree(self, tree):
        for daughter in tree:
            if self.query.match_tree(daughter):
                return tree

    def sql(self, corpus):
        s = self.query.sql(corpus)
        return select([corpus.dom.c.parent]).where(
            (corpus.dom.c.depth == 1) &
            (corpus.dom.c.child == s)
        )

    def __str__(self):
        return "daughter(%s)" % str(self.query)

# TODO: convenience functions:
# - daughters(x, y, z) -> daughter(x) & daughter(y) & ...
# - daughters_ordered(x, y, z) -> daughter(x & sprec(y & sprec(z)))


class label(QueryFunction):
    def __init__(self, label, exact=False):
        self.label = label
        self.exact = exact

    def match_tree(self, tree):
        if hasattr(self.label, "search"):
            rx = self.label
        else:
            label = re.escape(self.label)
            if self.exact:
                rx = re.compile("^" + label + "$")
            else:
                rx = re.compile("^" + label + "(-|$)")
        if rx.search(tree.label):
            return tree
        else:
            return None

    def sql(self, corpus):
        if hasattr(self.label, "search"):
            raise Exception("Regular expression label matching not implemented for indexed coropra")
        if "%" in self.label or "_" in self.label:
            # TODO: fix this, ideally by enforcing labels to fall in [A-Z0-9+-]
            raise Exception("Illegal characters in label")
        if self.exact:
            return select([corpus.nodes.c.rowid]).where(
                corpus.nodes.c.label == self.label
            )
        else:
            # Either we match the label exactly, or the label plus one or more
            # dash tags
            return select([corpus.nodes.c.rowid]).where(
                (corpus.nodes.c.label == self.label) |
                corpus.nodes.c.label.like(self.label + "-%")
            )

    def __str__(self):
        return "label(\"%s\"%s)" % (str(self.label),
                                    ", exact=True" if self.exact else "")
        return self._str


class dash_tag(label):
    def __init__(self, tag):
        self.tag = tag
        self.label = re.compile("-" + re.escape(tag) + "(-|$)")

    def __str__(self):
        return "dash_tag(\"%s\")" % self.tag

    def sql(self, corpus):
        return select([corpus.nodes.c.rowid]).where(
            corpus.nodes.c.label.like("%-" + self.tag + "-%") |
            corpus.nodes.c.label.like("%-" + self.tag)
        )


class sprec(QueryFunction):
    pass

# TODO: convenience fns sprec_multiple and sprec_multiple_ordered like for
# daughters
