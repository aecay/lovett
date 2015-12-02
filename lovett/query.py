"""This module contains the Lovett query language.

Query functions are defined as classes which inherit from `QueryFunction`.
Each query function must operate in two modes.  These functions are not
accessed directly, but rather through the `CorpusBase.matching_trees`
method (which dispatches to the appropriate mode).

The first mode is *direct mode*, which is accessed through the
`QueryFunction.match_tree` function.  This function receives as an argument a
`Tree` object, and should return ``True`` if the tree matches the query, and
``False`` otherwise.

The second mode is *indexed mode*, accessed via the `QueryFunction.sql`
instance method.  This method receives an instance of `CorpusDb` as an
argument, and should return a SQLAlchemy `sqlalchemy.sql.expression.Select`
object which will match the database ids of the matching nodes.  The function
can access relevant sqlalchemy column objects as fields of the ``corpus``
argument.

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
import collections.abc
import re
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import union
import itertools
import functools
from yattag import Doc
import palettable.colorbrewer.qualitative as Colors

import lovett.util as util


# Node colorization helpers


def _enum(x, idx):
    """Assign a numeric index to a `QueryFunction`.

    This function is designed for use with `QueryFunction.freduce`.

    Args:
        x (QueryFunction): The ``QueryFunction`` to operate on
        idx (int): The next available index

    Returns:
        int

    """
    x.idx = idx
    return idx + 1


def _mark_node(match_nodes, node):
    """A helper function for colorizing tree nodes.

    Reads the ``query_matches`` metadata from a `Tree` node, and adds
    appropriate ``query_match_colors`` metadata.

    Args:
        match_nodes (dict): A dictionary mapping values of ``query_matches``
            to colors those matches should take on.
        node (Tree): The node to operate on.

    """
    mn = node.metadata.get("query_matches", ())
    if len(mn) > 0:
        node.metadata["query_match_colors"] = list(
            filter(lambda x: x is not None,
                   map(lambda x: match_nodes.get(x, None), mn)))


def _clear_color(node):
    """Remove display colorization from a node.

    TODO: does this make more sense in tree.py?

    """
    if "query_matches" in node.metadata:
        del node.metadata["query_matches"]
    if "query_match_colors" in node.metadata:
        del node.metadata["query_match_colors"]


def _colorize_query(x, match_nodes):
    """Add color attribute to a `QueryFunction`.

    This function is designed to be used with `QueryFunction.freduce`.

    Args:
        x (QueryFunction): The function to operate on
        match_nodes (dict): Mapping from numerical query indices to hex colors.

    """
    if x.idx in match_nodes.keys():
        x.color = match_nodes[x.idx]
    return match_nodes


def _freduce_result(x):
    """A helper function for implementing `QueryFunction.freduce`.

    Args:
        x: any value

    Returns:
        A sequence

    """
    if x is None:
        return ()
    elif isinstance(x, collections.abc.Sequence):
        return x
    else:
        return(x,)


def match_function(fn):
    """A helper decorator to implement  marking of search matches for HTML output.

    TODO: more about what this does and why it's needed

    All implementations of `QueryFunction.match_tree` should be prapped with
    this decorator.

    """
    @functools.wraps(fn)
    def _match_function(self, tree, mark=False, **kwargs):
        res = fn(self, tree, mark=mark, **kwargs)
        if res and mark:
            tree.metadata.setdefault("query_matches", set()).update((self.idx,))
        return res
    return _match_function


class QueryFunction(metaclass=abc.ABCMeta):
    """Parent for all query functions in the Lovett query language.

    This class defines the interface that all query functions are expected to
    obey.

    """

    @abc.abstractmethod
    def match_tree(self, tree, mark=False):
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

        The RHS can be a `QueryFunction`::

            label("FOO") > label("BAR")

        is equivalent to::

            label("FOO") & idoms(label("BAR"))

        Furthermore, the RHS can be a tuple::

            label("FOO") > (label("BAR"), label("BAZ"))

        is equivalent to::

            label("FOO") & idoms(label("BAR")) & idoms(label("BAZ"))

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

        The RHS can be a `QueryFunction`::

            label("FOO") ^ label("BAR")

        is equivalent to::

            label("FOO") & idoms(label("BAR"))

        Furthermore, the RHS can be a tuple::

            label("FOO") ^ (label("BAR"), label("BAZ"))

        is equivalent to::

            label("FOO") & idoms(label("BAR")) & idoms(label("BAZ"))

        Note that this can combine with the ``>`` precedence operator::

            label("FOO") ^ (label("BAR") > label("BAZ"))

        matches structures like::

                 FOO
                 /\\
                /  \\
              BAR  BAZ

        Where the ordering between ``BAR`` and ``BAZ`` is important (but other
        elements can intervene).  Compare this to::

            label("FOO") ^ (label("BAR"), label("BAZ"))

        where the greater-than sign is changed to a comma inside the
        parentheses.  This matches similar structures, but allows the order of
        ``BAR`` and ``BAZ`` to be permuted.

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

    def _repr_html_(self):
        """TODO: document

        Including why we call out to a separate method (for the index
        argument).

        """
        doc, tag, txt = Doc().tagtext()
        with tag("pre", style="padding: 2px;"):
            self._to_html(doc, 0)
        return doc.getvalue()

    @abc.abstractmethod
    def _to_html(self, doc, idx):
        """TODO: document.

        Returns a tuple new_idx, string.  Newidx is the new index to be used
        in further computations (if we incremented it.)

        TODO: figure out how to use just one Doc instance, rather than
        creating one per call in the children

        TODO: it's lame to have to put the self.color check in each
        implementation...can we avoid?

        """
        pass

    @property
    def is_marking(self):
        """This property returns true if this is a `QueryFunction` that should
        mark its match in the output.

        This is a little subtle.  Simplex queries (that match the node
        label/text/metadata, and not properties of the node's relatives) are
        marking.  Wrapping queries are not marking.  The negation of a query
        is marking if the query being negated is.  A boolean combination (and
        or or) of two queries is marking if both combined queries are.

        """
        return False

    @abc.abstractmethod
    def freduce(self, fn, *args):
        """This function implements a generic interface for applying a function to all
        sub-predicates in a query.

        The query is traversed in a post-order fashion, calling ``fn`` at each
        step.  The first argument to ``fn`` is the `QueryFunction` object
        itself; the later args are the elements of ``args``.  The return value
        of ``fn`` becomes the next value of ``args``.

        The return value of ``fn`` must be a `collections.abc.Sequence`; the
        `_freduce_result` convenience function is provided as a utility to ensure
        this.

        This is a complicated system, but it enables the result-coloring code
        to be implemented in a simple fashion.

        .. note:: TODO

            It would be good to figure out whether it's possible to simplify
            this whole thing somewhat.

        Args:
            fn (function): The function to call
            args (Sequence): The arguments to pass

        Returns:
            The last value of ``fn`` applied to this `QueryFunction`.

        """
        pass

    def _enumerate(self):
        """This function assigns a unique numeric id to each sub-element of this
        `QueryFunction`.

        """
        self.freduce(_enum, 0)

    @abc.abstractmethod
    def _get_match_nodes(self):
        pass

    def colorize_tree(self, tree):
        self._enumerate()
        tree.map_nodes(_clear_color)
        # TODO: do we need to self.freduce(_uncolorize_query) here?
        tree.map_nodes(lambda node: self.match_tree(node, mark=True))
        mn = self._get_match_nodes()
        if len(mn) > 9:
            raise Exception("Too many match nodes: %s" % len(mn))
        # As it turns out, Set1 is the same no matter how many colors we have
        # (up to 9).  For dynamic palettes, more trickery would be needed.
        palette = Colors.Set1_9.hex_colors
        match_nodes = dict(map(lambda x: (x[1], palette[x[0]]),
                               enumerate(mn)))
        self.freduce(_colorize_query, match_nodes)
        tree.map_nodes(functools.partial(_mark_node, match_nodes))

    def _try_color(self, doc):
        try:
            doc.attr(style="border: 1px solid %s; padding: 2px;" % self.color)
        except AttributeError:
            pass


class BinaryQueryFunction(QueryFunction):
    """TODO: document"""
    def __init__(self, symbol, name, left, right):
        self._symbol = symbol
        self._name = name
        self.left = left
        self.right = right

    def __str__(self):
        # TODO: we add lots of extra parens to make sure we're getting scoping
        # rules right...can we cut down on this? perhaps we only need to add
        # parens for or, but not and
        return "(" + str(self.left) + " " + self._symbol + " " + \
            str(self.right) + ")"

    def _to_html(self, doc, idx):
        doc, tag, txt = doc.tagtext()
        with tag("span", klass="searchnode searchnode-%s" % self._name):
            self._try_color(doc)
            idx = self.left._to_html(doc, idx)
            txt(" " + self._symbol + " ")
            idx = self.right._to_html(doc, idx)
        return idx

    def freduce(self, fn, *args):
        args = self.left.freduce(fn, *args)
        args = self.right.freduce(fn, *args)
        return _freduce_result(fn(self, *args))

    @property
    def is_marking(self):
        return self.left.is_marking and self.right.is_marking


class And(BinaryQueryFunction):
    """This class implements conjunction of query functions."""
    def __init__(self, left, right):
        super().__init__("&", "and", left, right)

    @match_function
    def match_tree(self, tree, mark=False):
        return self.left.match_tree(tree, mark) and self.right.match_tree(tree, mark)

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

    def _get_match_nodes(self):
        if self.left.is_marking and self.right.is_marking:
            # Both halves are marking; so we only mark this node itself as a shortcut
            return (self.idx,)
        else:
            return self.left._get_match_nodes() + self.right._get_match_nodes()


class Or(BinaryQueryFunction):
    """This class implements disjunction of query functions."""
    def __init__(self, left, right):
        super().__init__("|", "or", left, right)

    @match_function
    def match_tree(self, tree, mark=False):
        l = self.left.match_tree(tree, mark)
        if not mark:
            return l or self.right.match_tree(tree, mark)
        else:
            # If we are marking the query, we need to evaluate both branches
            # for their side-effects
            r = self.right.match_tree(tree, mark)
            return l or r

    def sql(self, corpus):
        # TODO: needs the same treatemnt that we gave ``And`` replacing
        # intersect with join (but will it work?!?)
        return union(self.left.sql(corpus), self.right.sql(corpus))

    def _get_match_nodes(self):
        # Mark both halves regardless of whether they are marking, since this
        # is a disjunction
        return self.left._get_match_nodes() + self.right._get_match_nodes()


class Not(QueryFunction):
    """This class implements negation of query functions."""
    def __init__(self, fn):
        self.fn = fn

    @match_function
    def match_tree(self, tree, mark=False):
        return not self.fn.match_tree(tree, mark)

    def sql(self, corpus):
        return select([corpus.nodes.c.rowid]).where(
            corpus.nodes.c.rowid != self.fn.sql(corpus)
        )

    def __str__(self):
        return "~" + str(self.fn)

    def _to_html(self, doc, idx):
        doc, tag, txt = doc.tagtext()
        with tag("span", klass="searchnode searchnode-not"):
            self._try_color(doc)
            txt("~")
            idx = self.fn._to_html(doc, idx)

        return idx

    def freduce(self, fn, *args):
        args = self.fn.freduce(fn, *args)
        return _freduce_result(fn(self, *args))

    @property
    def is_marking(self):
        return self.fn.is_marking

    def _get_match_nodes(self):
        # TODO: what to do about this?  ~dash_tag("FOO") would mark (almost?)
        # every node in a tree.  One idea is to just pass through, returning
        # self.fn._get_match_nodes().
        return ()


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

    def _to_html(self, doc, idx):
        doc, tag, txt = doc.tagtext()
        with tag("span", klass="searchnode searchnode-%s" % self.name):
            self._try_color(doc)
            txt("%s(" % self.name)
            idx = self.query._to_html(doc, idx)
            txt(")")

        return idx

    def _colorize_tree(self, idx, tree):
        return self.query._colorize_tree(idx, tree)

    def sql(self, corpus):
        """TODO: why do we need this?

        If we have something like ``idoms(label("NP"))``, we'll get the same
        result twice for s structure like ``(XP (NP one) (NP two))``

        TODO: how to arrange for this to be called by all subclasses?

        """
        pass

    def freduce(self, fn, *args):
        args = self.query.freduce(fn, *args)
        return _freduce_result(fn(self, *args))

    def _get_match_nodes(self):
        return self.query._get_match_nodes()


class MarkingQueryFunction(abc.ABC, QueryFunction):
    """This class implements common functionality for queries which should mark
    their matching node.

    Attributes: _name (str): the name of this query, for use in string
        representations.

    """
    def __init__(self, name):
        self._name = name

    @abc.abstractmethod
    def _args(self):
        """Return the arguments of this function in a format suitable for use in a
        human-readable representation."""
        pass

    def __str__(self):
        return "%s(%s)" % (self._name, self._args())

    def _to_html(self, doc, idx):
        doc, tag, txt = doc.tagtext()
        with tag("span", klass="searchnode searchnode-%s" % self._name):
            self._try_color(doc)
            txt("%s(" % self._name)
            txt(self._args())
            txt(")")

        return idx + 1

    def freduce(self, fn, *args):
        return _freduce_result(fn(self, *args))

    # @abc.abstractmethod
    def mark_tree(t, idx):
        # TODO: implement marking of trees; relies on generating marks in
        # Tree._repr_html_
        pass

    @property
    def is_marking(self):
        return True

    def _get_match_nodes(self):
        return (self.idx,)


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

    @match_function
    def match_tree(self, tree, mark=False):
        if util.is_leaf(tree):
            return False
        for daughter in tree:
            if self.query.match_tree(daughter, mark):
                return True
        return False

    def sql(self, corpus):
        s = self.query.sql(corpus)
        return select([corpus.dom.c.parent]).where(
            (corpus.dom.c.depth == 1) &
            (corpus.dom.c.child.in_(s))
        ).distinct()


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

    @match_function
    def match_tree(self, tree, mark=False, _nested=False):
        if _nested:
            if self.query.match_tree(tree, mark):
                return True
        if util.is_leaf(tree):
            return False
        for daughter in tree:
            if self.match_tree(daughter, _nested=True, mark=False):
                return True
        return False

    def sql(self, corpus):
        s = self.query.sql(corpus)
        return select([corpus.dom.c.parent]).where(
            (corpus.dom.c.depth > 0) &
            (corpus.dom.c.child.in_(s))
        ).distinct()


class label(MarkingQueryFunction):
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
        super().__init__("label")
        self.label = label
        self.exact = exact

    @match_function
    def match_tree(self, tree, mark=False):
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

    def _args(self):
        return "\"%s\"%s" % (str(self.label),
                             ", exact=True" if self.exact else "")


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
        self._name = "dash_tag"

    def _args(self):
        return "\"%s\"" % self.tag

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

    @match_function
    def match_tree(self, tree, mark=False):
        parent = tree.parent
        right_siblings = list(itertools.dropwhile(lambda x: x != tree, parent))
        if len(right_siblings) < 2:
            return False
        # tree itself is included in the list; drop it
        right_siblings = right_siblings[1:]
        return any(map(lambda x: self.query.match_tree(x, mark), right_siblings))

    def sql(self, corpus):
        return select([corpus.sprec.c.left]).where(
            (corpus.sprec.c.distance > 0) &
            (corpus.sprec.c.right.in_(self.query.sql(corpus)))
        ).distinct()


class isprec(WrapperQueryFunction):
    """This class implements immediate sisterwise precedence queries.

    X sisterwise-precedes Y iff X and Y are sisters (have the same parent) and
    X immediately precedes Y.

    """
    def __init__(self, query):
        super().__init__(query)
        self.name = "isprec"

    @match_function
    def match_tree(self, tree, mark=False):
        parent = tree.parent
        right_siblings = list(itertools.dropwhile(lambda x: x != tree, parent))
        if len(right_siblings) < 2:
            return False
        # get the immediate right sibling
        right_sibling = right_siblings[1]
        return self.query.match_tree(right_sibling, mark)

    def sql(self, corpus):
        return select([corpus.sprec.c.left]).where(
            (corpus.sprec.c.distance == 1) &
            (corpus.sprec.c.right.in_(self.query.sql(corpus)))
        ).distinct()

# TODO: convenience fns sprec_multiple and sprec_multiple_ordered like for
# doms


class text(MarkingQueryFunction):
    """This class implements matching text of leaf nodes.

    .. note:: TODO

       matching regexp, set
    """
    def __init__(self, text):
        super().__init__("text")
        self.text = text

    def _args(self):
        return "\"%s\"" % self.text

    @match_function
    def match_tree(self, tree, mark=False):
        return util.is_leaf(tree) and tree.text == self.text

    def sql(self, corpus):
        return select([corpus.tree_metadata.c.id]).where(
            (corpus.tree_metadata.c.key == "text") &
            (corpus.tree_metadata.c.value == self.text)
        )


class has_metadata(QueryFunction):
    """Metadata queries.

    .. note:: TODO

        - blocked on properly handling metadata in `CorpusDb._insert_node` (can now complete)
        - Should it be marking? Probably yes
    """
    pass
