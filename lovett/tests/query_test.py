import unittest
import re

from lovett.tree import parse as T
import lovett.query as Q
import lovett.db as db
from nose.plugins.skip import SkipTest
from doctest import Example
from lxml.doctestcompare import LXMLOutputChecker


class XmlTest(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        checker = LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(Example("", want), got, 0)
            raise AssertionError(message)


def identity(x):
    return x


class QueryTest(XmlTest):
    def do_all(self, query, groups):
        for group in groups:
            self.do_one(query, *group)

    def do_one(self, query, tree_string, result, fn=None):
        print("%s; %s" % (query, tree_string))
        t = T(tree_string)
        if fn is None:
            fn = identity
        self.assertEqual(query.match_tree(fn(t)), result)
        d = db.CorpusDb()
        d.insert_tree(t)
        mt = d.matching_trees(query)
        if result:
            self.assertEqual(len(mt), 1)
            self.assertEqual(fn(t), mt[0])
        else:
            self.assertEqual(len(mt), 0)


class LabelTest(QueryTest):
    def setUp(self):
        self.l = Q.label("NP")

    def test_str(self):
        self.assertEqual(str(self.l), "label(\"NP\")")

    def test_html(self):
        self.assertXmlEqual(self.l._to_html(0)[1],
                            '<span style="border: 1px solid red;" class="searchnode searchnode-label">label("NP")</span>')

    def test_query(self):
        tests = (("NP", True),
                 ("NP-FOO", True),
                 ("XNP", False),
                 ("X-NP", False),
                 ("N", False))

        self.do_all(self.l, map(lambda x: ("(%s foo)" % x[0], x[1]), tests))
        self.do_all(self.l, map(lambda x: ("(%s (N foo))" % x[0], x[1]), tests))


class LabelExactTest(QueryTest):
    def setUp(self):
        self.l = Q.label("NP", exact=True)

    def test_str(self):
        self.assertEqual(str(self.l), "label(\"NP\", exact=True)")

    def test_html(self):
        self.assertXmlEqual(self.l._to_html(0)[1],
                            '<span style="border: 1px solid red;" class="searchnode searchnode-label">label("NP", exact=True)</span>')

    def test_query(self):
        tests = (("NP", True),
                 ("NP-FOO", False),
                 ("XNP", False),
                 ("X-NP", False),
                 ("N", False))

        self.do_all(self.l, map(lambda x: ("(%s foo)" % x[0], x[1]), tests))
        self.do_all(self.l, map(lambda x: ("(%s (N foo))" % x[0], x[1]), tests))


class DashTagTest(QueryTest):
    def setUp(self):
        self.l = Q.dash_tag("FOO")

    def test_str(self):
        self.assertEqual(str(self.l), "dash_tag(\"FOO\")")

    def test_html(self):
        self.assertXmlEqual(self.l._to_html(0)[1],
                            '<span style="border: 1px solid red;" class="searchnode searchnode-dash_tag">dash_tag("FOO")</span>')

    def test_query(self):
        tests = (("NP", False),
                 ("NP-FOO", True),
                 ("NP-FOO-BAR", True),
                 ("NP-FOOBAR", False),
                 ("FOO", False))

        self.do_all(self.l, map(lambda x: ("(%s foo)" % x[0], x[1]), tests))
        self.do_all(self.l, map(lambda x: ("(%s (N foo))" % x[0], x[1]), tests))


class AndTest(QueryTest):
    def setUp(self):
        l = Q.label("NP")
        l2 = Q.dash_tag("FOO")
        self.a = l & l2

    def test_str(self):
        self.assertEqual(str(self.a), '(label("NP") & dash_tag("FOO"))')

    def test_html(self):
        self.assertXmlEqual(self.a._to_html(0)[1],
                         '<span class="searchnode searchnode-and"><span style="border: 1px solid red;" class="searchnode searchnode-label">label("NP")</span> &amp; <span style="border: 1px solid blue;" class="searchnode searchnode-dash_tag">dash_tag("FOO")</span></span>')

    def test_query(self):
        tests = (("(NP-FOO (N bar))", True),
                 ("(NP (N bar))", False))
        self.do_all(self.a, tests)


class OrTest(QueryTest):
    def setUp(self):
        l = Q.label("NP")
        l2 = Q.dash_tag("FOO")
        self.a = l | l2

    def test_str(self):
        self.assertEqual(str(self.a), '(label("NP") | dash_tag("FOO"))')

    def test_html(self):
        self.assertXmlEqual(self.a._to_html(0)[1],
                            '<span class="searchnode searchnode-or"><span style="border: 1px solid red;" class="searchnode searchnode-label">label("NP")</span> | <span style="border: 1px solid blue;" class="searchnode searchnode-dash_tag">dash_tag("FOO")</span></span>')

    def test_query(self):
        tests = (("(NP-FOO (N bar))", True),
                 ("(NP (N bar))", True),
                 ("(XP-FOO (N bar))", True),
                 ("(XP (N bar))", False))
        self.do_all(self.a, tests)


class NotTest(QueryTest):
    def setUp(self):
        self.l = ~Q.label("NP")

    def test_str(self):
        self.assertEqual(str(self.l), "~label(\"NP\")")

    def test_html(self):
        self.assertXmlEqual(self.l._to_html(0)[1],
                            '<span class="searchnode searchnode-not">~<span style="border: 1px solid red;" class="searchnode searchnode-label">label("NP")</span></span>')

    def test_query(self):
        raise SkipTest          # Known broken

        tests = (("(NP (N foo))", False),
                 ("(NP foo)", False),
                 ("(XP foo)", True))
        self.do_all(self.l, tests)


class DomsTest(QueryTest):
    def setUp(self):
        self.l = Q.label("NP") & Q.doms(Q.label("N"))

    def test_str(self):
        self.assertEqual(str(self.l), "(label(\"NP\") & doms(label(\"N\")))")

    def test_html(self):
        self.assertXmlEqual(self.l._to_html(0)[1],
                            '<span class="searchnode searchnode-and"><span style="border: 1px solid red;" class="searchnode searchnode-label">label("NP")</span> &amp; <span class="searchnode searchnode-doms">doms(<span style="border: 1px solid blue;" class="searchnode searchnode-label">label("N")</span>)</span></span>')

    def test_doms(self):
        tests = (("(NP (N foo))", True),
                 ("(NP (XP (N foo)))", True),
                 ("(NP (XP (YP (N foo))))", True),
                 ("(NP (n (YP foo)))", False),
                 ("(NP (n foo))", False))
        self.do_all(self.l, tests)


class IDomsTest(QueryTest):
    def setUp(self):
        self.l = Q.label("NP") & Q.idoms(Q.label("N"))
        self.l_oper = Q.label("NP") ^ Q.label("N")

    idoms_tests = (("(NP (N foo))", True),
                   ("(NP (N (X foo)))", True),
                   ("(NP (XP (N foo)))", False),
                   ("(NP (XP (YP (N foo))))", False),
                   ("(NP (n (YP foo)))", False),
                   ("(NP (n foo))", False))

    def test_str(self):
        self.assertEqual(str(self.l), "(label(\"NP\") & idoms(label(\"N\")))")
        self.assertEqual(str(self.l_oper), "(label(\"NP\") & idoms(label(\"N\")))")

    def test_html(self):
        self.assertXmlEqual(self.l._to_html(0)[1],
                            '<span class="searchnode searchnode-and"><span style="border: 1px solid red;" class="searchnode searchnode-label">label("NP")</span> &amp; <span class="searchnode searchnode-idoms">idoms(<span style="border: 1px solid blue;" class="searchnode searchnode-label">label("N")</span>)</span></span>')
        self.assertXmlEqual(self.l_oper._to_html(0)[1],
                            '<span class="searchnode searchnode-and"><span class="searchnode searchnode-label" style="border: 1px solid red;">label("NP")</span> &amp; <span class="searchnode searchnode-idoms">idoms(<span class="searchnode searchnode-label" style="border: 1px solid blue;">label("N")</span>)</span></span>')

    def test_query(self):
        self.do_all(self.l, type(self).idoms_tests)

    def test_idoms_operator(self):
        self.do_all(self.l_oper, type(self).idoms_tests)


def SprecTest(QueryTest):
    def setUp(self):
        self.l = Q.label("XP") & Q.sprec(Q.label("YP"))
        self.l_oper = Q.label("XP") > Q.label("YP")
        self.l_oper_tuple = Q.label("XP") > (Q.label("YP"), Q.label("ZP"))

    sprec_tests = (("(IP (XP foo) (YP bar))", True, lambda x: x[0]),
                   ("(IP (XP foo) (ZP 123) (YP bar))", True, lambda x: x[0]),
                   ("(IP (XP (ZP 123)) (WP xxx) (YP (ZP 456)))", True, lambda x: x[0]),
                   ("(IP (XP (ZP 123)) (YP (ZP 456)))", True, lambda x: x[0]),
                   ("(IP (ZP (XP foo)) (YP bar))", False, lambda x: x[0]),
                   ("(IP (XP foo) (ZP (YP bar)))", False, lambda x: x[0]),
                   ("(IP (ZP (XP foo) (YP bar)))", True, lambda x: x[0][0]),
                   ("(IP (ZP (XP foo) (ZP xxx) (YP bar)) (XP quux))", True, lambda x: x[0][0]),
                   ("(IP (ZP (XP foo) (YP bar)) (XP quux))", True, lambda x: x[0][0]))

    def test_str(self):
        self.assertEqual(str(self.l), '(label("XP") & sprec(label("YP")))')
        self.assertEqual(str(self.l_oper), '(label("XP") & sprec(label("YP")))')
        self.assertEqual(str(self.l_oper_tuple),
                         '(label("XP") & (sprec(label("YP")) & sprec(label("ZP"))))')

    def test_html(self):
        self.assertXmlEqual(self.l._to_html(0)[1], "")
        self.assertXmlEqual(self.l_oper._to_html(0)[1], "")
        self.assertXmlEqual(self.l_oper_tuple._to_html(0)[1], "")

    def test_sprec(self):
        self.do_all(self.l, type(self).sprec_tests)

    def test_sprec_operator(self):
        self.do_all(self.l_oper, type(self).sprec_tests)

    def test_sprec_operator_tuple(self):
        tests = (("(IP (XP xxx) (YP yyy) (ZP zzz))", True, lambda x: x[0]),
                 ("(IP (XP xxx) (ZP zzz) (YP yyy))", True, lambda x: x[0]),
                 ("(IP (YP yyy) (XP xxx) (ZP zzz))", False, lambda x: x[0]),
                 ("(IP (YP yyy) (ZP zzz) (XP xxx))", False, lambda x: x[0]),
                 ("(IP (ZP zzz) (YP yyy) (XP xxx))", False, lambda x: x[0]))
        self.do_all(self.l_oper_tuple, tests)


class ISprecTest(QueryTest):
    def setUp(self):
        self.l = Q.label("XP") & Q.isprec(Q.label("YP"))
        self.l_oper = Q.label("XP") >> Q.label("YP")

    def test_str(self):
        self.assertEqual(str(self.l), '(label("XP") & isprec(label("YP")))')
        self.assertEqual(str(self.l_oper), '(label("XP") & isprec(label("YP")))')

    def test_html(self):
        self.assertXmlEqual(self.l._to_html(0)[1],
                            '<span class="searchnode searchnode-and"><span style="border: 1px solid red;" class="searchnode searchnode-label">label("XP")</span> &amp; <span class="searchnode searchnode-isprec">isprec(<span style="border: 1px solid blue;" class="searchnode searchnode-label">label("YP")</span>)</span></span>')
        self.assertXmlEqual(self.l_oper._to_html(0)[1],
                            '<span class="searchnode searchnode-and"><span class="searchnode searchnode-label" style="border: 1px solid red;">label("XP")</span> &amp; <span class="searchnode searchnode-isprec">isprec(<span class="searchnode searchnode-label" style="border: 1px solid blue;">label("YP")</span>)</span></span>')

    isprec_tests = (("(IP (XP foo) (YP bar))", True, lambda x: x[0]),
                    ("(IP (XP foo) (ZP 123) (YP bar))", False, lambda x: x[0]),
                    ("(IP (XP (ZP 123)) (YP (ZP 456)))", True, lambda x: x[0]),
                    ("(IP (XP (ZP 123)) (ZP xxx) (YP (ZP 456)))", False, lambda x: x[0]),
                    ("(IP (ZP (XP foo)) (YP bar))", False, lambda x: x[0]),
                    ("(IP (XP foo) (ZP (YP bar)))", False, lambda x: x[0]),
                    ("(IP (ZP (XP foo) (YP bar)))", True, lambda x: x[0][0]),
                    ("(IP (ZP (XP foo) (ZP xxx) (YP bar)) (XP quux))", False, lambda x: x[0][0]),
                    ("(IP (ZP (XP foo) (YP bar)) (XP quux))", True, lambda x: x[0][0]))

    def test_isprec(self):
        self.do_all(self.l, type(self).isprec_tests)

    def test_isprec_operator(self):
        self.do_all(self.l_oper, type(self).isprec_tests)


class TextTest(QueryTest):
    def setUp(self):
        self.q = Q.text("foo")
        self.q_complex = Q.label("NP") & Q.idoms(Q.text("foo"))

    def test_str(self):
        raise SkipTest

    def test_html(self):
        raise SkipTest

    def test_text(self):
        self.do_all(self.q,
                    (("(X foo)", True),
                     ("(X bar)", False)))

    def test_text_complex(self):
        self.do_all(self.q_complex,
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
        res = c.execute(both.sql(self.d)).fetchall()
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
        res = c.execute(dq.sql(self.d)).fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(self.d._reconstitute(res[0][0]), self.d[0])
