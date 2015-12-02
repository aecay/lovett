"""Representing a corpus as an indexed database.

This module provides the means for representing a corpus as an indexed
database: the `CorpusDb`.  At a high level, this provides the same interface
as a regular `Corpus` object: a sequence of trees.  There are some differences
however:

* The corpus is immutable.  It is only possible to append new trees to the end
  of the corpus (and in normal use even this should not be done).
* The `CorpusBase.matching_trees` method for searching by evaluating a
  `QueryFunction` against the corpus is significantly optimized by the
  database engine.

"""

import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, Index
from sqlalchemy.sql import select

import lovett.util as util
import lovett.corpus as corpus
import lovett.tree as tree


class CorpusDb(corpus.CorpusBase):
    """A class implementing an indexed corpus.

    In order to operate, this class uses the `SQLite
    <https://www.sqlite.org/>`_ database engine, wrapped by the `SQLAlchemy
    Python library <http://www.sqlalchemy.org/>`_.  Using SQLite brings the
    benefit of a mature and heavily optimized indexing engine.  SQLAlchemy
    provides a flexible programmatic interface for building SQL queries,
    eliminating the need to munge strings manually.

    The storage and indexing strategy is described in the documentation at
    `indexing`.

    .. note:: TODO

       the roots attribute needs more work (is this still true? 12/1/15)

    Attributes:
        engine (`sqlalchemy.engine.Engine`): the database engine (*private*)
        metadata (`sqlalchemy.schema.MetaData`): metadata (*private*)
        nodes (`sqlalchemy.schema.Table`): a table listing each node in
            the corpus.  Columns: ``rowid``, ``label``.
        dom (`sqlalchemy.schema.Table`): reflexive dominance.  Columns:
            ``parent``, ``child``, ``depth``
        sprec (`sqlalchemy.schema.Table`): reflexive sister-precedence.
            Columns: ``left``, ``right``, ``distance``.
        roots (list): the root nodes in the corpus.
        tree_metadata (`sqlalchemy.schema.Table`): metadata for each node.
            Columns: ``id``, ``key``, ``value``.
        id (int): The next id available for inserting a node.  Methods which
            actually use this value to insert a node are responsible for
            incrementing this value.

    """
    def __init__(self, other=None, roots=None):
        """TODO: document"""
        if other is None:
            # Initialize an empty corpus, creating the db from scratch
            self.engine = sqlalchemy.create_engine("sqlite:///:memory:")
            self.metadata = MetaData()
            self.nodes = Table("nodes", self.metadata,
                               Column("rowid", Integer, primary_key=True),
                               Column("label", String),
                               Index("label_idx", "label"))
            self.dom = Table("dom", self.metadata,
                             Column("parent", Integer, ForeignKey("nodes.rowid")),
                             Column("child", Integer, ForeignKey("nodes.rowid")),
                             Column("depth", Integer),
                             Index("child_depth", "child", "depth")
                             #, Index("parent_idx", "parent")
            )
            self.sprec = Table("sprec", self.metadata,
                               Column("left", Integer, ForeignKey("nodes.rowid")),
                               Column("right", Integer, ForeignKey("nodes.rowid")),
                               Column("distance", Integer),
                               Index("right_distance", "right", "distance")
                               #, Index("left_idx", "left")
            )
            self.tree_metadata = Table("metadata", self.metadata,
                                       Column("id", Integer, ForeignKey("nodes.rowid")),
                                       Column("key", String),
                                       Column("value", String),
                                       Index("id_key", "id", "key"))
            self.metadata.create_all(self.engine)
            self.roots = []
            self.id = 1
        else:
            # Create a corpus that is a clone of another corpus
            # TODO: make this a class method, not a variant of init
            self.engine = other.engine
            self.metadata = other.metadata
            self.nodes = other.nodes
            self.dom = other.dom
            self.sprec = other.sprec
            self.tree_metadata = other.tree_metadata

            if roots is None:
                # Make a copy of the roots list, so the corpora can be treated
                # differently.  TODO: requires filtering search results to be
                # in the list of roots.  Would it be better to clone the DB
                # backing this corpus, and then prune it according to roots??
                self.roots = list(other.roots)
            else:
                self.roots = roots

            self.id = other.id

    def _insert_metadata(self, c, node_id, dic, prefix=""):
        """Inner function for inserting metadata into the database.

        Metadata are represented in a table with columns ``id``, ``key``, and
        ``value``.  Nested metadata values are converted into a string key for
        the database by joining their key path with ``:``.  The
        `_metadata_py_to_str` function is used to translate metadata values
        into strings.

        Args:
            c (sqlalchemy.engine.Connection): A connection to the database.
            node_id (int): The database id of the node to which the metadata
                are affiliated.
            dic (Metadata): Metadata to insert.
            prefix (str): The key path at which to insert this metadata.

        """
        for key, val in dic.items():
            if key in util.INTERNAL_METADATA_KEYS:
                continue
            if isinstance(val, tree.Metadata):
                self._insert_metadata(node_id, val, prefix + key + ":")
            else:
                c.execute(self.tree_metadata.insert().values(
                    id=node_id,
                    key=prefix + key,
                    value=util._metadata_py_to_str(val)))

    def _insert_node(self, c, node, parents=(), lefts=()):

        """Insert a node into the database.

        Args:
            c (sqlalchemy.engine.Connection): A connection to the database.
            node (Tree): The node to be inserted.
            parents (tuple): The database ids of the ancestor nodes, if any,
                in ascending order (immediate parent = element 0)
            left (int): The database ids of the left siblings, if any, in
                right-to-left order (the immediate left sibling = element 0)

        Returns:
           int: the database id of the inserted node.

        """

        # Insert this node's label into the db
        rowid = self.id
        self.id += 1
        c.execute(self.nodes.insert(), label=node.label, rowid=rowid)
        # Add it to the dominance_R table
        c.execute(self.dom.insert(),
                  # Insert a depth-0 self-dominance relation...
                  {"parent": rowid, "child": rowid, "depth": 0},
                  # ...as well as dominance relations for all the node's parents
                  *[{"parent": p, "child": rowid,
                     # +1 because enumerate counts from 0
                     "depth": d + 1}
                    for d, p
                    in enumerate(parents)])
        # Add it to the sprecedes_R table; see comments above for explanation
        # of the parts
        c.execute(self.sprec.insert(),
                  {"left": rowid, "right": rowid, "distance": 0},
                  *[{"left": l, "right": rowid, "distance": d + 1}
                    for d, l
                    in enumerate(lefts)])
        if util.is_leaf(node):
            # Add its text to the metadata db...
            c.execute(self.tree_metadata.insert(), id=rowid, key="text", value=node.text)
        else:
            # ...or add its children to the db, as applicable
            p = (rowid,) + parents
            lastchild_rowids = ()
            for child in node:
                tmp = self._insert_node(c, child, p, lastchild_rowids)
                lastchild_rowids = (tmp,) + lastchild_rowids
        self._insert_metadata(c, rowid, node.metadata)
        return rowid

    def _insert_tree(self, conn, t):
        """An inner function to perform insertion of a tree.

        Should not be called directly.  In addition to calling `_insert_node`,
        this function adds the tree's database id to the `roots` attribute of
        the class.

        """
        rowid = self._insert_node(conn, t)
        self.roots.append(rowid)

    def insert_tree(self, t):
        """Insert a single tree into the corpus.

        This method wraps `_insert_tree`.

        """
        with self.engine.begin() as conn:
            self._insert_tree(conn, t)

    def insert_trees(self, trees):
        """Insert a sequence of trees into the corpus.

        This method wraps `_insert_tree`.  It is more efficient than
        `insert_tree` because it uses a single database transaction for the
        whole insertion, rather than committing after each tree is inserted.

        """
        with self.engine.begin() as conn:
            for t in trees:
                self._insert_tree(conn, t)

    def _reconstitute_metadata(self, rowid):
        """TODO: document this function.

        And how it is riddled with inelegant hacks."""
        c = self.engine.connect()
        metadata = c.execute(
            select([self.tree_metadata.c.key, self.tree_metadata.c.value]).
            where(self.tree_metadata.c.id == rowid)
        ).fetchall()
        m = tree.Metadata({})
        for k, v in metadata:
            if k in util.INTERNAL_METADATA_KEYS:
                # Don't process it.
                continue
            # TODO: This is a really inelegant way to do it...
            _m = m
            ks = k.split(":")
            for _k in ks[:-1]:
                _m = _m[_k]
            _m[ks[-1]] = util._metadata_str_to_py(v)
        return m

    def _reconstitute(self, rowid):
        """Create a `Tree` from the database.

        This function takes an entry in the database and constructs a Python
        object containing its structure.

        .. note:: TODO

           This function relies on the assumption that database ids are
           monotonically increasing as trees are added to the database.  This
           is valid as long as `CorpusDb` is not mutable.  However, in the
           (unlikely) event that we decide to make indexed corpora, and the
           trees that are contained therein, mutable, it will be necessary to
           revisit this assumption.

           Finally, to reflect the immutability of the corpus, it would be
           ideal if `Tree` objects returned by this function could arrange to
           raise an exception on attempted modifications.

        """
        c = self.engine.connect()
        label = c.execute(
            select([self.nodes.c.label]).where(self.nodes.c.rowid == rowid)
        ).fetchone()[0]
        children = c.execute(
            select([self.dom.c.child]).
            where((self.dom.c.depth == 1) & (self.dom.c.parent == rowid)).
            order_by(self.dom.c.child)
        ).fetchall()
        if len(children) > 0:
            child_trees = [self._reconstitute(child[0]) for child in children]
            return tree.NonTerminal(label, child_trees, self._reconstitute_metadata(rowid))
        else:
            text = c.execute(
                select([self.tree_metadata.c.value]).
                where((self.tree_metadata.c.id == rowid) & (self.tree_metadata.c.key == "text"))
            ).fetchone()[0]
            return tree.Leaf(label, text, self._reconstitute_metadata(rowid))

    # Corpus abstract methods
    def __getitem__(self, i):
        return self._reconstitute(self.roots[i])

    def __len__(self):
        return len(self.roots)

    def matching_trees(self, query):
        c = self.engine.connect()
        s = query.sql(self)
        r = list(map(lambda x: x[0], c.execute(s).fetchall()))
        return CorpusDb(self, r)

    # Instance methods
    def to_corpus(self):
        """Convert to a `Corpus`."""
        c = corpus.Corpus([])
        for t in self:
            c.append(t)
        return c
