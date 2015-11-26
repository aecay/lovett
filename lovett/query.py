"""This module contains the Lovett query language.

Query functions are defined as classes which inherit from `QueryFunction`.
Each query function must operate in two modes.  These functions are not
accessed directly, but rather through the `CorpusBase.matching_trees`
method (which dispatches to the appropriate mode).

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
- sisterwise precedence via the ``>`` operator
- immediate sisterwise precedence via the ``>>`` operator
- immediate dominance via the ``^`` operator
- (TODO) ``@`` for metadata

Because the operator precedence rules can sometimes be unexpected (the boolean
operators are originally for bitwise arithmetic in Python, for example),
careful attention to parenthesization is needed.

"""

import abc
import re
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import union, intersect
import itertools
import functools

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

    def _operator(self, other, fn):
        """Generic function implementing operator overloading."""

        if isinstance(other, QueryFunction):
            return And(self, fn(other))
        elif isinstance(other, tuple):
            if len(other) == 1:
                return And(self, fn(other[0]))
            else:
                return And(self, functools.reduce(And, map(fn, other)))
        else:
            raise ValueError("An invalid argument was passed to an operator overload: %s" % other)

    def __gt__(self, other):
        """Sisterwise precedence on the ``>`` operator.

        The RHS can be a `QueryFunction`: ``label("FOO") > label("BAR")`` is
        equivalent to ``label("FOO") & idoms(label("BAR"))``.  Furthermore,
        the RHS can be a tuple: ``label("FOO") > (label("BAR"),
        label("BAZ"))`` is equivalent to ``label("FOO") & idoms(label("BAR"))
        & idoms(label("BAZ"))``.

        """

        return self._operator(other, sprec)

    def __rshift__(self, other):
        """Immediate sisterwise precedence on the ``>>`` operator.

        See `QueryFunction.__gt__` for discussion of the possibilities this
        operator offers.

        """

        return self._operator(other, isprec)

    def __xor__(self, other):
        """Immediate dominance on the ``^`` operator.

        The RHS can be a `QueryFunction`: ``label("FOO") ^ label("BAR")`` is
        equivalent to ``label("FOO") & idoms(label("BAR"))``.  Furthermore,
        the RHS can be a tuple: ``label("FOO") ^ (label("BAR"),
        label("BAZ"))`` is equivalent to ``label("FOO") & idoms(label("BAR"))
        & idoms(label("BAZ"))``.

        Note that this can combine with the ``>`` precedence operator.
        ``label("FOO") ^ (label("BAR") > label("BAZ"))`` matches structures
        like::

                 FOO
                 /\
                /  \
              BAR  BAZ

        Where the ordering between ``BAR`` and ``BAZ`` is important (but other
        elements can intervene).  Compare this to ``label("FOO") ^
        (label("BAR"), label("BAZ"))`` where the greater-than sign is changed
        to a comma inside the parentheses.  This matches similar structures,
        but allows the order of ``BAR`` and ``BAZ`` to be permuted.

        .. note::

            The ``>``, ``>>``, and ``^`` operators are considered
            experimental.  They are included in order to get feedback on how
            they might make it easier to write lovett queries.  But they could
            be removed if they turn out to be difficult to support or
            confusing.

            You can convert from these experimental operators to a
            fully-supported representation by using the `str` function to get
            a representation of the query that does not use these functions::

                TODO: example

        """

        return self._operator(other, idoms)

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
        # Other ideas: filter, join

        # Originally we had this code:
        # return intersect(self.left.sql(corpus), self.right.sql(corpus))

        # The problem with it is that SQLite barfs on parenthesized
        # intersections like SELECT ... INTERSECT (SELECT ... INTERSECT SELECT
        # ...).  See https://www.sqlite.org/lang_select.html.

        # One option would be to figure out how to convert And(x, And(y,z))
        # into intersect(x,y,z) -- but even that might not work if we have
        # nested And's and Or's.  So evidently we need to convert into a
        # JOIN.

        # We need an alias here so we get the two subqueries as anon_1 and
        # anon_2.  Then our ON clause is "ON anon_1.rowid = anon_2.rowid".  If
        # we didn't do this, we'd get "ON rowid = rowid", which SQLite doesn't
        # like very much.
        l = self.left.sql(corpus).alias()
        # TODO: this is a really stupid way of getting the right column to
        # join on.
        lc = l.columns.get("id")
        if lc is None:
            lc = l.columns.get("left")
        if lc is None:
            lc = l.columns.get("parent")
        if lc is None:
            lc = l.columns.get("rowid")
        r = self.right.sql(corpus).alias()
        rc = r.columns.get("id")
        if rc is None:
            rc = r.columns.get("left")
        if rc is None:
            rc = r.columns.get("parent")
        if rc is None:
            rc = r.columns.get("rowid")
        # Select the left column arbitrarily, since it doesn't matter which we
        # use.  One might think we could use l.join(r).select(lc), but that
        # gives an incorrect result.
        return select([lc]).select_from(l.join(r, lc == rc))

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
            (corpus.dom.c.child.in_(s))
        )


# TODO: convenience functions:
# - doms(x, y, z) -> doms(x) & doms(y) & ...
# - doms_ordered(x, y, z) -> doms(x & sprec(y & sprec(z)))

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
            (corpus.dom.c.child.in_(s))
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
                                        for mood  in ("","I","S")]
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


class sprec(WrapperQueryFunction):
    """This class implements sisterwise precedence queries.

    X sisterwise-precedes Y iff X and Y are sisters (have the same parent) and
    X precedes Y.

    """
    def __init__(self, query):
        super().__init__(query)
        self.name = "sprec"

    def match_tree(self, tree):
        parent = tree.parent
        right_siblings = list(itertools.dropwhile(lambda x: x != tree, parent))
        if len(right_siblings) < 2:
            return False
        # tree itself is included in the list; drop it
        right_siblings = right_siblings[1:]
        return any(map(self.query.match_tree, right_siblings))

    def sql(self, corpus):
        return select([corpus.sprec.c.left]).where(
            (corpus.sprec.c.distance > 0) &
            (corpus.sprec.c.right.in_(self.query.sql(corpus)))
        )


class isprec(WrapperQueryFunction):
    """This class implements immediate sisterwise precedence queries.

    X sisterwise-precedes Y iff X and Y are sisters (have the same parent) and
    X immediately precedes Y.

    """
    def __init__(self, query):
        super().__init__(query)
        self.name = "isprec"

    def match_tree(self, tree):
        parent = tree.parent
        right_siblings = list(itertools.dropwhile(lambda x: x != tree, parent))
        if len(right_siblings) < 2:
            return False
        # get the immediate right sibling
        right_sibling = right_siblings[1]
        return self.query.match_tree(right_sibling)

    def sql(self, corpus):
        return select([corpus.sprec.c.left]).where(
            (corpus.sprec.c.distance == 1) &
            (corpus.sprec.c.right.in_(self.query.sql(corpus)))
        )

# TODO: convenience fns sprec_multiple and sprec_multiple_ordered like for
# doms


class text(QueryFunction):
    """This class implements matching text of leaf nodes.

    .. note:: TODO

       matching regexp, set
    """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return "text(\"%s\")" % self.text

    def match_tree(self, tree):
        return util.is_leaf(tree) and tree.text == self.text

    def sql(self, corpus):
        return select([corpus.tree_metadata.c.id]).where(
            (corpus.tree_metadata.c.key == "text") &
            (corpus.tree_metadata.c.value == self.text)
        )


class has_metadata(QueryFunction):
    """Metadata queries.

    .. note:: TODO

       blocked on properly handling metadata in `CorpusDb._insert_node`.
    """
    pass
