"""This module contains the Lovett query language.

Query functions are defined as classes which inherit from `QueryFunction`.
Each query function must operate in two modes.  These functions are not
accessed directly, but rather through the `matching_trees`
method of `Corpus` objects (which dispatches to the appropriate mode).

The first mode is *direct mode*, which is accessed through the
`QueryFunction.match_tree` function.  This function receives as an argument a
`Tree` object, and should return ``True`` if the tree matches the query.

The second mode is *indexed mode*, accessed via the `QueryFunction.sql`
instance method.  This method receives an instance of `CorpusDb` as an
argument, and should return a SQLAlchemy `sqlalchemy.sql.expression.Select`
object which will match the database ids of the matching nodes.  The function
can access relevant sqlalchemy objects as fields of the ``corpus`` argument.

``QueryFunction`` objects support a variety of combinatorics through
overloading of python operators.  The following are supported:

- conjunction via the ``&`` operator
- disjunction via the ``|`` operator
- negation via the ``~`` operator
- (TODO) ``^`` for dominance, ``>`` for precedence

Because the operator precedence rules can sometimes be unexpected (the boolean
operators are originally for bitwise arithmetic in Python, for example),
careful attention to parenthesization is needed.

"""

import abc
import re
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import union, intersect

import lovett.util as util

# TODO: label("FOO") ^ label("BAR") -> foo idoms bar
# label("FOO") ^ (label("BAR") > label("BAZ")) -> foo idoms bar, foo idoms
# baz, bar (s)precedes baz
# label("FOO") ^ (label("BAR"), label("BAZ")) -> foo idoms bar, foo idoms baz,
# no ordering between bar and baz


class QueryFunction(metaclass=abc.ABCMeta):
    """Parent for all query functions in the Lovett query language.

    This class defines the interface that all query functions are expected to
    obey.

    """

    @abc.abstractmethod
    def match_tree(self, tree):
        """Return ``True`` if a tree matches this query.

        Args:
            tree (`lovett.tree.Tree`): The tree to match against.

        Returns:
            bool: True iff this query matches the tree argument.

        """
        pass

    @abc.abstractmethod
    def sql(self, corpus):
        """Return a SQLAlchemy select implementing the query.

        Args:
            corpus (CorpusDb): The corpus against which
                the query will be evaluated.

        Returns:
            sqlalchemy.sql.expression.Select: An expression implementing the query.

        """
        pass

    def __and__(self, other):
        """Conjunction.

        Args:
            other (QueryFunction): the second query.

        Returns:
            QueryFunction: the conjunctuion of the two queries.

        """
        return And(self, other)

    def __or__(self, other):
        """Disjunction.

        Args:
            other (QueryFunction): the second query.

        Returns:
            QueryFunction: the disjunctuion of the two queries.

        """
        return Or(self, other)

    def __invert__(self):
        """Negation.

        Returns:
            QueryFunction: the negation of the query.

        """
        return Not(self)

    @abc.abstractmethod
    def __str__(self):
        """Return the string representation of this query.

        It should be capable of being read by the python interpreter to
        reconstitute the QueryFunction object.

        """
        pass


class And(QueryFunction):
    """This class implements conjunction of query functions."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def match_tree(self, tree):
        return self.left.match_tree(tree) and self.right.match_tree(tree)

    def sql(self, corpus):
        return intersect(self.left.sql(corpus), self.right.sql(corpus))

    def __str__(self):
        # TODO: we add lots of extra parens to make sure we're getting scoping
        # rules right...can we cut down on this? perhaps we only need to add
        # parens for or, but not and
        return "(" + str(self.left) + " & " + str(self.right) + ")"


class Or(QueryFunction):
    """This class implements disjunction of query functions."""
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
    """This class implements negation of query functions."""
    def __init__(self, fn):
        self.fn = fn

    def match_tree(self, tree):
        if self.fn.match_tree(tree):
            return False
        else:
            return True

    def sql(self, corpus):
        return select([corpus.nodes.c.rowid]).where(
            corpus.nodes.c.rowid != self.fn.sql(corpus)
        )

    def __str__(self):
        return "~" + str(self.fn)


class WrapperQueryFunction(QueryFunction):
    """This class implements common functionality for queries which wrap another
    query.

    Attributes:
        name (str): the name of this query, for use in the string representation.

    """
    def __init__(self, query):
        self.query = query

    def __str__(self):
        return "%s(%s)" % (self.name, str(self.query))


class idoms(WrapperQueryFunction):
    """This class implements immediate-dominance queries.

    This is roughly equivalent to the ``idoms`` function in CorpusSearch.
    Thus the following query::

        idoms(label("NP-SBJ"))

    is approximately equivalent in CorpusSearch to::

        ___ idoms NP-SBJ

    The blank in the CorpusSearch query is not specified by Lovett.  It is
    typical to specify this by conjoining another ``label`` invocation::

        label("IP-MAT") & idoms(label("NP-SBJ"))

    """
    def __init__(self, query):
        super().__init__(query)
        self.name = "idoms"

    def match_tree(self, tree):
        if util.is_leaf(tree):
            return False
        for daughter in tree:
            if self.query.match_tree(daughter):
                return True
        return False

    def sql(self, corpus):
        s = self.query.sql(corpus)
        return select([corpus.dom.c.parent]).where(
            (corpus.dom.c.depth == 1) &
            (corpus.dom.c.child == s)
        )


# TODO: convenience functions:
# - daughters(x, y, z) -> daughter(x) & daughter(y) & ...
# - daughters_ordered(x, y, z) -> daughter(x & sprec(y & sprec(z)))

class doms(WrapperQueryFunction):
    """This class implements dominance queries at arbitrary depth.

    Its usage is very similar to that of the `idoms` class, which see.
    Naturally, the analogous CorpusSearch function in this case is ``doms``
    and not ``idoms``.

    """
    def __init__(self, query):
        super().__init__(query)
        self.name = "doms"

    def match_tree(self, tree, _nested=False):
        if _nested:
            if self.query.match_tree(tree):
                return True
        if util.is_leaf(tree):
            return False
        for daughter in tree:
            if self.match_tree(daughter, True):
                return True
        return False

    def sql(self, corpus):
        s = self.query.sql(corpus)
        return select([corpus.dom.c.parent]).where(
            (corpus.dom.c.depth > 0) &
            (corpus.dom.c.child == s)
        )


class label(QueryFunction):
    """This class implements matching tree node labels.

    The ``label`` slot (and argument to the initializer function) provides
    several ways of specifying the label to match.  If label is a string, it
    will be matched as either the entire label, or a prefix of the label
    followed by one or more trailing dashtags.  The default matching behavior
    for ``label("NP")`` is as follows:

    ====== ========
    string matches?
    ====== ========
    NP     yes
    NP-SBJ yes
    NPX    no
    ====== ========

    The argument ``exact`` can be used to require exact matching, which
    changes the matching behavior to the following:

    ====== ========
    string matches?
    ====== ========
    NP     yes
    NP-SBJ no
    NPX    no
    ====== ========

    The bias towards prefix matching is intentional -- the indexed query
    engine can implement prefix searches in a fast way, whereas non-prefix
    matches are slower.  In cases where you need a non-prefix match, you
    should look at whether the other label matching functions are a better
    fit.  (Currently this encompasses only `dash_tag`).

    .. note:: TODO

       It would probably be a good idea to add more label matching functions
       with optimized SQL implementations.  What would be good candidates?
       One idea would be to allow this function to take a set of strings as an
       argument, and match whether the label is a member of the set.  This
       could then be turned into a massive disjunction in SQL, which is
       (probably) not too slow.  This would also allow the set to be generated
       programmatically in python, like this example common in Old English
       queries::

           conjugations = [tense + mood for tense in ("P", "D")
                                        for mood in ("","I","S")]
           conjugations.append("I")  ## imperative
           conjugations.append("")   ## infinitive -- if not restricted to tensed vbs
           verbs = [type + conjugation for type in ("VB","MD","HV", ...)
                                       for conjugation in conjugations]
           all_verbs = set([x + y for x in ("", "NEG+", "RP+") for y in verbs])

    The ``label`` argument can also be a regular expression object (or indeed
    any object with a ``search`` method).  In this case, the regular
    expression is matched against the label.  In this case the ``exact``
    parameter is ignored.

    .. caution:: Indexed mode operation

       Note that regular expression matching is not yet implemented in indexed
       (SQL) mode.  It might be possible to implement this, but it will be
       slow.  It is better to use one of the specialized label matching
       functions.  If you find a common use case for which a label matching
       function does not exist, please open an issue report.  (TODO: link to
       github issues page)

    Attributes:
        label: the label to match
        exact (bool): whether to require an exact match; otherwise
            prefix matching is allowed.

    """
    def __init__(self, label, exact=False):
        """Initializer.

        Args:
            label: the label to match; see the class docstring for details
            exact (bool): whether to require an exact match

        """
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
            return True
        else:
            return False

    def sql(self, corpus):
        if hasattr(self.label, "search"):
            raise Exception("Regular expression label matching not implemented for indexed corpora")
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
    """This class implements matching a dash tag against a node label.

    The dash tag can either be in the middle of the label as in ``*-TAG-*`` or
    at the end as in ``*-TAG``, where ``*`` represents an arbitrary
    (non-empty) string.  Does not support the matching of partial dash tags,
    i.e. the use of ``dash_tag("FOO")`` to match ``XP-FOOBAR``.

    Attributes:
        tag (str): the dash tag to search for.

    """
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
    # TODO!
    pass

# TODO: convenience fns sprec_multiple and sprec_multiple_ordered like for
# daughters
