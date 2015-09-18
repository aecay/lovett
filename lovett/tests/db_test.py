from __future__ import unicode_literals

import unittest
# import textwrap
# from nose.plugins.skip import SkipTest

import lovett.tree as T

import lovett.db as db


class CorpusTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.d = db.CorpusDb()
        t = T.parse("(IP (NP (D a) (N dog)) (VBD chased) (NP (D the) (ADJ speedy) (N+N mailman)))")
        cls.d.insert_tree(t)
        # raise Exception(cls.d.conn.cursor().execute("SELECT * FROM nodes").fetchall())
        # raise Exception(fetch_all(cls.d, "SELECT * FROM nodes"))

    def fetch(self, query, args=None):
        if args is not None:
            return self.d.conn.cursor().execute(query, args).fetchone()[0]
        else:
            return self.d.conn.cursor().execute(query).fetchone()[0]

    def fetch_all(self, query, args=None):
        if args is not None:
            return self.d.conn.cursor().execute(query, args).fetchall()
        else:
            return self.d.conn.cursor().execute(query).fetchall()

    def test_basic(self):
        ip = self.fetch("SELECT rowid FROM nodes WHERE label = 'IP'")
        assert isinstance(ip, int)
        assert ip > 0
        nps = self.fetch_all("SELECT rowid FROM nodes WHERE label = 'NP'")
        assert len(nps) == 2

    def test_dom(self):
        ip = self.fetch("SELECT rowid FROM nodes WHERE label = 'IP'")
        nps = self.fetch_all("SELECT rowid FROM nodes WHERE label = 'NP'")
        dom = self.fetch("SELECT depth FROM dom WHERE parent = ? AND child = ?",
                         (ip, nps[0][0]))
        assert dom == 1
        dom = self.fetch("SELECT depth FROM dom WHERE parent = ? AND child = ?",
                         (ip, nps[1][0]))
        assert dom == 1

    def test_sprec(self):
        adj = self.fetch("SELECT rowid FROM nodes WHERE label = 'ADJ'")
        nn = self.fetch("SELECT rowid FROM nodes WHERE label = 'N+N'")
        sprec = self.fetch("SELECT distance FROM sprec WHERE left = ? AND right = ?",
                           (adj, nn))
        assert sprec == 1
