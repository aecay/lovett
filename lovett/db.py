"""Representing a corpus as an indexed database.

This module provides the means for representing a corpus as an indexed
database: the `CorpusDb`.  At a high level, this provides the same interface
as a regular `Corpus` object: a sequence of trees.  There are some differences
however:

* The corpus is immutable.  It is only possible to append new trees to the end
  of the corpus (and in normal use even this should not be done).
* The `matching_trees` methods for searching by evaluating a `Query` against
  the corpus is significantly optimized by the database engine.

"""

import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
from sqlalchemy.sql import select

import lovett.util as util
import lovett.corpus as corpus
import lovett.tree as tree


class CorpusDb(corpus.CorpusBase):
    """A class implementing an indexed corpus.

    In order to operate, this class uses the `SQLite
    <https://www.sqlite.org/>`_ database engine, wrapped by the `sqlalchemy
    Python library <http://www.sqlalchemy.org/>`_ (except for a few raw SQL
    statements, which in principle should be removed to the extent possible).
    Using SQLite brings the benefit of a mature and heavily optimized indexing
    engine.  SQLAlchemy provides a flexible programmatic interface for
    building SQL queries, eliminating the need to munge strings manually.

    The indexing strategy is described in the documentation at `indexing`.

    Attributes:
        engine (`sqlalchemy.engine.Engine`): the database engine (*private*)
        metadata (`sqlalchemy.schema.MetaData`): metadata (*private*)
        nodes (`sqlalchemy.schema.Table`): a table listing each node in
            the corpus.  Columns: ``rowid``, ``label``.
        dom (`sqlalchemy.schema.Table`): reflexive dominance.  Columns:
            ``parent``, ``child``, ``depth``
        sprec (`sqlalchemy.schema.Table`): reflexive sister-precedence.
            Columns: ``left``, ``right``, ``distance``.
        roots (`sqlalchemy.schema.Table`): the root nodes in the corpus.
            Columns: ``id``.
        metadata (`sqlalchemy.schema.Table`): metadata for each node.
            Columns: ``id``, ``key``, ``value``.

    """
    def __init__(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:")
        self.metadata = MetaData()
        self.nodes = Table("nodes", self.metadata,
                           Column("rowid", Integer, primary_key=True),
                           Column("label", String))
        self.dom = Table("dom", self.metadata,
                         Column("parent", Integer, ForeignKey("nodes.rowid")),
                         Column("child", Integer, ForeignKey("nodes.rowid")),
                         Column("depth", Integer))
        self.sprec = Table("sprec", self.metadata,
                           Column("left", Integer, ForeignKey("nodes.rowid")),
                           Column("right", Integer, ForeignKey("nodes.rowid")),
                           Column("distance", Integer))
        self.roots = Table("roots", self.metadata,
                           Column("id", Integer, ForeignKey("nodes.rowid")))
        self.tree_metadata = Table("metadata", self.metadata,
                                   Column("id", Integer, ForeignKey("nodes.rowid")),
                                   Column("key", String),
                                   Column("value", String))
        self.metadata.create_all(self.engine)

    def _add_child(self, parent, child):
        """Add a parent-child relationship to the database.

        This method and `_add_sibling` are responsible for maintaining the
        dominance and sister-precendece tables.

        .. note:: TODO

           We should use SQL triggers for this, instead of explicit method calls.

        Args:
            parent (int): database id of the parent node.
            child (int): database id of the child node.

        """
        c = self.engine.connect()
        update = sqlalchemy.sql.text(
            """INSERT INTO dom (parent, child, depth)
            SELECT p.parent, c.child, p.depth+c.depth+1
            FROM dom p, dom c
            WHERE p.child = :parent AND c.parent = :child""")
        c.execute(update, parent=parent, child=child)

    def _add_sibling(self, left, right):
        c = self.engine.connect()
        update = sqlalchemy.sql.text(
            """INSERT INTO sprec (left, right, distance)
            SELECT l.left, r.right, l.distance+r.distance+1
            FROM sprec l, sprec r
            WHERE l.right = :left AND r.left = :right""")
        c.execute(update, left=left, right=right)

    def _insert_node(self, node, parent=None, left=None):
        """Insert a node into the database.

        Args:
            node (Tree): the node to be inserted.
            parent (int): the database id of the parent node, if any.
                Will be passed to `_add_child`.
            left (int): the database id of the left sibling, if any.
                Will be passed to `_add_sibling`.

        Returns:
            int: the database id of the inserted node.

        """
        c = self.engine.connect()
        # Insert this node's label into the db
        c.execute(self.nodes.insert(), label=node.label)
        # Get the database id.
        rowid = c.execute(sqlalchemy.sql.text("SELECT last_insert_rowid()")).fetchone()[0]
        # Add it to the dominance_R table
        c.execute(self.dom.insert(), parent=rowid, child=rowid, depth=0)
        # Add it to the sprecedes_R table
        c.execute(self.sprec.insert(), left=rowid, right=rowid, distance=0)
        # Make it a child of its parent, if applicable
        if parent:
            self._add_child(parent, rowid)
        if left:
            self._add_sibling(left, rowid)
        # Add its text to the metadata db...
        if util.is_leaf(node):
            c.execute(self.tree_metadata.insert(), id=rowid, key="text", value=node.text)
        # ...or add its children to the db, as applicable
        if util.is_nonterminal(node):
            lastchild_rowid = None
            for child in node:
                lastchild_rowid = self._insert_node(child, rowid, lastchild_rowid)
        return rowid

    def insert_tree(self, t):
        """Insert a tree into the corpus.

        This method wraps `_insert_node`, and also handles adding the root to
        the appropriate table.

        """
        rowid = self._insert_node(t)
        c = self.engine.connect()
        c.execute(self.roots.insert(), id=rowid)

    def _reconstitute(self, rowid):
        """Create a `Tree` from the database.

        This function takes an entry in the database and constructs a Python
        object containing its structure.

        .. note:: TODO

           This function does not handle metadata yet (other than the "text"
           metadata which is used to store the text of leaf nodes).

           It also relies on the assumption that database ids are
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
            return tree.NonTerminal(label, child_trees)
        else:
            text = c.execute(
                select([self.tree_metadata.c.value]).
                where((self.tree_metadata.c.id == rowid) & (self.tree_metadata.c.key == "text"))
            ).fetchone()[0]
            return tree.Leaf(label, text)

    # Corpus abstract methods
    def __getitem__(self, i):
        c = self.engine.connect()
        return self._reconstitute(
            c.execute(
                sqlalchemy.sql.text("SELECT rowid FROM roots ORDER BY rowid")
            ).fetchall()[i][0])

    def __len__(self):
        c = self.conn.cursor()
        return len(c.execute(sqlalchemy.sql.text("SELECT * FROM roots")).fetchall())

    # Instance methods
    def to_corpus(self):
        """Convert to a `Corpus`."""
        c = corpus.Corpus([])
        for t in self:
            c.append(t)
        return c