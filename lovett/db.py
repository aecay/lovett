import apsw

import lovett.util as util
import lovett.corpus as corpus
import lovett.tree as tree


class CorpusDb(corpus.CorpusBase):
    def __init__(self):
        self.conn = apsw.Connection(":memory:")
        c = self.conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("CREATE TABLE nodes (rowid INTEGER PRIMARY KEY, label STRING)")
        c.execute("""CREATE TABLE dom (parent INT, child INT, depth INT,
                                       FOREIGN KEY(parent) REFERENCES nodes(rowid),
                                       FOREIGN KEY(child) REFERENCES nodes(rowid))""")
        c.execute("""CREATE TABLE sprec (left INT, right INT, distance INT,
                                         FOREIGN KEY(left) REFERENCES nodes(rowid),
                                         FOREIGN KEY(right) REFERENCES nodes(rowid))""")
        c.execute("CREATE TABLE roots (id INT, FOREIGN KEY(id) REFERENCES nodes(rowid))")
        c.execute("""CREATE TABLE metadata (id INT, key STRING, value STRING,
                                            FOREIGN KEY(id) REFERENCES nodes(rowid))""")
        # TODO: need triggers, or to break out add_child, add_sibling, and
        # remove_ variants

    def _add_child(self, parent, child):
        c = self.conn.cursor()
        c.execute("""INSERT INTO dom (parent, child, depth)
                     SELECT p.parent, c.child, p.depth+c.depth+1
                     FROM dom p, dom c
                     WHERE p.child = ? AND c.parent = ?""", (parent, child))

    def _add_sibling(self, left, right):
        c = self.conn.cursor()
        c.execute("""INSERT INTO sprec (left, right, distance)
                     SELECT l.left, r.right, l.distance+r.distance+1
                     FROM sprec l, sprec r
                     WHERE l.right = ? AND r.left = ?""", (left, right))

    def _insert_node(self, node, parent=None, left=None):
        c = self.conn.cursor()
        # Insert this node's label into the db
        c.execute("INSERT INTO nodes VALUES (NULL, ?)", (node.label,))
        rowid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Add it to the dominance_R table
        c.execute("INSERT INTO dom VALUES (?,?,0)", (rowid, rowid))
        # Add it to the sprecedes_R table
        c.execute("INSERT INTO sprec VALUES (?,?,0)", (rowid, rowid))
        # Make it a child of its parent, if applicable
        if parent:
            self._add_child(parent, rowid)
        if left:
            self._add_sibling(left, rowid)
        # Add its text to the metadata db...
        if util.is_leaf(node):
            c.execute("INSERT INTO metadata VALUES (?,'text',?)", (rowid, node.text))
        # ...or add its children to the db, as applicable
        if util.is_nonterminal(node):
            lastchild_rowid = None
            for child in node:
                lastchild_rowid = self._insert_node(child, rowid, lastchild_rowid)
        return rowid

    def insert_tree(self, t):
        rowid = self._insert_node(t)
        c = self.conn.cursor()
        c.execute("INSERT INTO roots VALUES (?)", (rowid,))

    def _reconstitute(self, rowid):
        # TODO: handle metadata
        c = self.conn.cursor()
        label = c.execute("SELECT label FROM nodes WHERE rowid = ?", (rowid,)).fetchone()[0]
        # TODO: possibly bogus optimization assuming that nodes are always
        # inserted into the DB in order.  If we allow mutable databases, this
        # will need to be changed.
        children = c.execute("SELECT child FROM dom WHERE depth = 1 AND parent = ? ORDER BY child",
                             (rowid,)).fetchall()
        if len(children) > 0:
            child_trees = [self._reconstitute(child[0]) for child in children]
            return tree.NonTerminal(label, child_trees)
        else:
            text = c.execute("SELECT value FROM metadata WHERE id = ? AND key = 'text'",
                             (rowid,)).fetchone()[0]
            return tree.Leaf(label, text)

    # Corpus abstract methods
    def __getitem__(self, i):
        c = self.conn.cursor()
        return self._reconstitute(
            c.execute("SELECT rowid FROM roots ORDER BY rowid").fetchall()[i][0])

    def __len__(self):
        c = self.conn.cursor()
        return len(c.execute("SELECT * FROM roots").fetchall())

    # Instance methods

    def to_corpus(self):
        c = corpus.Corpus([])
        for t in self:
            c.append(t)
        return c
