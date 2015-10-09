import unittest
import re

from lovett.tree import parse as T
import lovett.query as Q
import lovett.db as db
from nose.plugins.skip import SkipTest


class QueryTest(unittest.TestCase):
    def do_all(self, query, groups):
        for group in groups:
            self.do_one(query, *group)

    def do_one(self, query, tree_string, result):
        print("%s; %s" % (query, tree_string))
        t = T(tree_string)
        self.assertEqual(query.match_tree(t), result)
        d = db.CorpusDb()
        d.insert_tree(t)
        mt = d.matching_trees(query)
        if result:
            self.assertEqual(len(mt) > 0, result)
            self.assertEqual(t, mt[0])

    def test_label(self):
        l = Q.label("NP")
        self.assertEqual(str(l), "label(\"NP\")")
        tests = (("NP", True),
                 ("NP-FOO", True),
                 ("XNP", False),
                 ("X-NP", False),
                 ("N", False))

        self.do_all(l, map(lambda x: ("(%s foo)" % x[0], x[1]), tests))
        self.do_all(l, map(lambda x: ("(%s (N foo))" % x[0], x[1]), tests))

    def test_label_exact(self):
        l = Q.label("NP", exact=True)
        self.assertEqual(str(l), "label(\"NP\", exact=True)")

        tests = (("NP", True),
                 ("NP-FOO", False),
                 ("XNP", False),
                 ("X-NP", False),
                 ("N", False))

        self.do_all(l, map(lambda x: ("(%s foo)" % x[0], x[1]), tests))
        self.do_all(l, map(lambda x: ("(%s (N foo))" % x[0], x[1]), tests))

    def test_dash_tag(self):
        l = Q.dash_tag("FOO")
        self.assertEqual(str(l), "dash_tag(\"FOO\")")

        tests = (("NP", False),
                 ("NP-FOO", True),
                 ("NP-FOO-BAR", True),
                 ("NP-FOOBAR", False),
                 ("FOO", False))

        self.do_all(l, map(lambda x: ("(%s foo)" % x[0], x[1]), tests))
        self.do_all(l, map(lambda x: ("(%s (N foo))" % x[0], x[1]), tests))

    def test_and(self):
        l = Q.label("NP")
        l2 = Q.dash_tag("FOO")
        a = l & l2
        self.assertEqual(str(a), '(label("NP") & dash_tag("FOO"))')

        tests = (("(NP-FOO (N bar))", True),
                 ("(NP (N bar))", False))
        self.do_all(a, tests)

    def test_or(self):
        l = Q.label("NP")
        l2 = Q.dash_tag("FOO")
        a = l | l2
        self.assertEqual(str(a), '(label("NP") | dash_tag("FOO"))')

        tests = (("(NP-FOO (N bar))", True),
                 ("(NP (N bar))", True),
                 ("(XP-FOO (N bar))", True),
                 ("(XP (N bar))", False))
        self.do_all(a, tests)

    def test_not(self):
        raise SkipTest          # Known broken
        l = ~Q.label("NP")
        self.assertEqual(str(l), "~label(\"NP\")")

        tests = (("(NP (N foo))", False),
                 ("(NP foo)", False),
                 ("(XP foo)", True))
        self.do_all(l, tests)

    def test_text(self):
        q = Q.text("foo")
        self.do_all(q,
                    (("(X foo)", True),
                     ("(X bar)", False)))

    def test_text_complex(self):
        q = Q.label("NP") & Q.idoms(Q.text("foo"))
        self.do_all(q,
                    (("(NP (N foo))", True),
                     ("(NP (N bar))", False),
                     ("(NP foo)", False),
                     ("(XP (N foo))", False)))


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
