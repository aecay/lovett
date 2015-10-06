import unittest
import re

from lovett.tree import parse as T
import lovett.query as Q
import lovett.db as db


class QueryTest(unittest.TestCase):
    def test_label(self):
        l = Q.label("NP")
        self.assertEqual(str(l), "label(\"NP\")")
        tests = (("NP", True),
                 ("NP-FOO", True),
                 ("XNP", False),
                 ("X-NP", False),
                 ("N", False))

        for pat, passes in tests:
            t = T("(%s foo)" % pat)
            t2 = T("(%s (N foo))" % pat)
            if passes:
                self.assertTrue(l.match_tree(t))
                self.assertTrue(l.match_tree(t2))
            else:
                self.assertFalse(l.match_tree(t))
                self.assertFalse(l.match_tree(t2))

    def test_label_exact(self):
        l = Q.label("NP", exact=True)
        self.assertEqual(str(l), "label(\"NP\", exact=True)")

        tests = (("NP", True),
                 ("NP-FOO", False),
                 ("XNP", False),
                 ("X-NP", False),
                 ("N", False))

        for pat, passes in tests:
            t = T("(%s foo)" % pat)
            t2 = T("(%s (N foo))" % pat)
            if passes:
                self.assertTrue(l.match_tree(t))
                self.assertTrue(l.match_tree(t2))
            else:
                self.assertFalse(l.match_tree(t))
                self.assertFalse(l.match_tree(t2))

    def test_dash_tag(self):
        l = Q.dash_tag("FOO")
        self.assertEqual(str(l), "dash_tag(\"FOO\")")

        tests = (("NP", False),
                 ("NP-FOO", True),
                 ("NP-FOO-BAR", True),
                 ("NP-FOOBAR", False),
                 ("FOO", False))

        for pat, passes in tests:
            t = T("(%s foo)" % pat)
            t2 = T("(%s (N foo))" % pat)
            if passes:
                self.assertTrue(l.match_tree(t))
                self.assertTrue(l.match_tree(t2))
            else:
                self.assertFalse(l.match_tree(t))
                self.assertFalse(l.match_tree(t2))

    def test_and(self):
        l = Q.label("NP")
        l2 = Q.dash_tag("FOO")
        a = l & l2
        self.assertEqual(str(a), '(label("NP") & dash_tag("FOO"))')
        t = T("(NP-FOO (N bar))")
        self.assertTrue(a.match_tree(t))

        t = T("(NP (N bar))")
        self.assertFalse(a.match_tree(t))

    def test_or(self):
        l = Q.label("NP")
        l2 = Q.dash_tag("FOO")
        a = l | l2
        self.assertEqual(str(a), '(label("NP") | dash_tag("FOO"))')
        t = T("(NP-FOO (N bar))")
        self.assertTrue(a.match_tree(t))

        t = T("(NP (N bar))")
        self.assertTrue(a.match_tree(t))

        t = T("(XP-FOO (N bar))")
        self.assertTrue(a.match_tree(t))

    def test_not(self):
        l = ~Q.label("NP")
        self.assertEqual(str(l), "~label(\"NP\")")

        t = T("(NP (N foo))")
        self.assertFalse(l.match_tree(t))

        t = T("(NP foo)")
        self.assertFalse(l.match_tree(t))

        t = T("(XP foo)")
        self.assertTrue(l.match_tree(t), t)


class QueryDbTest(unittest.TestCase):
    def setUp(cls):
        cls.d = db.CorpusDb()
        t = T("(IP (NP (D a) (N dog)) (VBD chased) (NP-ACC (D the) (ADJ speedy) (N+N mailman)) (PP-X-Y (P over) (NP-XY (D the) (N fence))))")
        cls.d.insert_tree(t)

    def test_label(self):
        l = Q.label("NP")
        c = self.d.engine.connect()
        res = c.execute(l.sql(self.d).order_by(self.d.nodes.c.rowid)).fetchall()
        self.assertEqual(len(res), 3)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0][0])
        self.assertEqual(self.d._reconstitute(res[1][0]), self.d[0][2])
        self.assertEqual(self.d._reconstitute(res[2][0]), self.d[0][3][1])

    def test_label_exact(self):
        l = Q.label("NP", exact=True)
        c = self.d.engine.connect()
        res = c.execute(l.sql(self.d).order_by(self.d.nodes.c.rowid)).fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0][0])

    def test_label_misc(self):
        l = Q.label(re.compile("foo"))
        self.assertRaises(Exception, lambda: l.sql(None))

        l = Q.label("NP%")
        self.assertRaises(Exception, lambda: l.sql(None))

    def test_dash_tag(self):
        l = Q.dash_tag("ACC")
        c = self.d.engine.connect()
        res = c.execute(l.sql(self.d).order_by(self.d.nodes.c.rowid)).fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0][2])

        l = Q.dash_tag("X")
        c = self.d.engine.connect()
        res = c.execute(l.sql(self.d).order_by(self.d.nodes.c.rowid)).fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0][3])

        l = Q.dash_tag("Y")
        c = self.d.engine.connect()
        res = c.execute(l.sql(self.d).order_by(self.d.nodes.c.rowid)).fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0][3])

    def test_and(self):
        l = Q.dash_tag("ACC")
        l2 = Q.label("NP")
        both = l & l2

        c = self.d.engine.connect()
        res = c.execute(both.sql(self.d).order_by(self.d.nodes.c.rowid)).fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0][2])

    def test_or(self):
        l = Q.dash_tag("X")
        l2 = Q.label("NP")
        both = l | l2

        c = self.d.engine.connect()
        res = c.execute(both.sql(self.d).order_by(self.d.nodes.c.rowid)).fetchall()
        self.assertEqual(len(res), 4)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0][0])
        self.assertEqual(self.d._reconstitute(res[1][0]), self.d[0][2])
        self.assertEqual(self.d._reconstitute(res[2][0]), self.d[0][3])
        self.assertEqual(self.d._reconstitute(res[3][0]), self.d[0][3][1])

    def test_daugher(self):
        dq = Q.idoms(Q.label("ADJ"))
        c = self.d.engine.connect()
        res = c.execute(dq.sql(self.d).order_by(self.d.dom.c.parent)).fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0][2])

    def test_daughter_and(self):
        dq = Q.idoms(Q.label("NP")) & Q.idoms(Q.label("VBD"))
        c = self.d.engine.connect()
        res = c.execute(dq.sql(self.d).order_by(self.d.dom.c.parent)).fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0])
