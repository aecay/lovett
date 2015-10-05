import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
from sqlalchemy.sql import select

import lovett.util as util
import lovett.corpus as corpus
import lovett.tree as tree


class CorpusDb(corpus.CorpusBase):
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

    # TODO: use triggers instead of _add_child and _add_sibling
    def _add_child(self, parent, child):
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
        c = self.engine.connect()
        # Insert this node's label into the db
        c.execute(self.nodes.insert(), label=node.label)
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
        rowid = self._insert_node(t)
        c = self.engine.connect()
        c.execute(self.roots.insert(), id=rowid)

    def _reconstitute(self, rowid):
        # TODO: handle metadata
        c = self.engine.connect()
        label = c.execute(
            select([self.nodes.c.label]).where(self.nodes.c.rowid == rowid)
        ).fetchone()[0]
        # TODO: possibly bogus optimization assuming that nodes are always
        # inserted into the DB in order.  If we allow mutable databases, this
        # will need to be changed.
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
        c = corpus.Corpus([])
        for t in self:
            c.append(t)
        return c
