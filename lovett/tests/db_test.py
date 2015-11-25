from __future__ import unicode_literals

import unittest
import sqlalchemy
# import textwrap
# from nose.plugins.skip import SkipTest

import lovett.tree as T

import lovett.db as db
import lovett.transform as transform


class CorpusTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.d = db.CorpusDb()
        t = T.parse("(IP (NP (D a) (N dog)) (VBD chased) (NP (D the) (ADJ speedy) (N+N mailman)))")
        cls.d.insert_tree(t)
        # raise Exception(cls.d.conn.cursor().execute("SELECT * FROM nodes").fetchall())
        # raise Exception(fetch_all(cls.d, "SELECT * FROM nodes"))

    def fetch(self, query, **kwargs):
        return self.d.engine.connect().execute(sqlalchemy.sql.text(query), **kwargs).fetchone()[0]

    def fetch_all(self, query, **kwargs):
        return self.d.engine.connect().execute(sqlalchemy.sql.text(query), **kwargs).fetchall()

    def test_basic(self):
        ip = self.fetch("SELECT rowid FROM nodes WHERE label = 'IP'")
        assert isinstance(ip, int)
        assert ip > 0
        nps = self.fetch_all("SELECT rowid FROM nodes WHERE label = 'NP'")
        assert len(nps) == 2

    def test_dom(self):
        ip = self.fetch("SELECT rowid FROM nodes WHERE label = 'IP'")
        nps = self.fetch_all("SELECT rowid FROM nodes WHERE label = 'NP'")
        dom = self.fetch("SELECT depth FROM dom WHERE parent = :parent AND child = :child",
                         parent=ip,
                         child=nps[0][0])
        assert dom == 1
        dom = self.fetch("SELECT depth FROM dom WHERE parent = :parent AND child = :child",
                         parent=ip,
                         child=nps[1][0])
        assert dom == 1

    def test_sprec(self):
        adj = self.fetch("SELECT rowid FROM nodes WHERE label = 'ADJ'")
        nn = self.fetch("SELECT rowid FROM nodes WHERE label = 'N+N'")
        sprec = self.fetch("SELECT distance FROM sprec WHERE left = :left AND right = :right",
                           left=adj,
                           right=nn)
        assert sprec == 1

    def test_reconstitute(self):
        t = T.parse("(IP (NP (D a) (N dog)) (VBD chased) (NP (D the) (ADJ speedy) (N+N mailman)))")
        self.assertEqual(self.d[0], t)

    def test_reconstitute_metadata(self):
        d = db.CorpusDb()
        t = T.parse("(IP (NP (D a-a) (N dog-dog)) (VBD chased-chase) (NP (D the-the) (ADJ speedy-speedy) (N+N mailman-mailman)))")
        transform.icepahc_lemma(t)
        d.insert_tree(t)
        self.assertEqual(d[0], t)
        self.assertEqual(d[0][0][0].metadata.lemma, "a")
