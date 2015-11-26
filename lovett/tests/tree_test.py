from __future__ import unicode_literals

import unittest
import textwrap
import json
from nose.plugins.skip import SkipTest

import lovett.tree as T
from lovett.tree import NonTerminal as NT
from lovett.tree import Leaf as L


class UtilFnsTest(unittest.TestCase):
    def test_parse(self):
        self.assertIsNone(T.parse(""))
        self.assertIsNone(T.parse("  \n  "))
        self.assertRaises(T.ParseError, lambda: T.parse("(FOO"))
        self.assertRaises(T.ParseError, lambda: T.parse("(FOO))"))
        self.assertRaises(T.ParseError, lambda: T.parse("(FOO bar))"))
        self.assertRaises(T.ParseError, lambda: T.parse("(FOO)"))
        self.assertRaises(T.ParseError, lambda: T.parse("(FOO bar baz)"))


class IndexTest(unittest.TestCase):
    def test_movement_index(self):
        for tracetype in ["T", "ICH", "CL"]:
            print(tracetype)
            # Regular trace
            t = T.parse("(NP *%s*-1)" % (tracetype,))
            self.assertEqual(t.metadata.index, 1)
            self.assertEqual(t.metadata.idx_type, "regular")
            self.assertEqual(t.text, "*%s*" % (tracetype,))
            self.assertEqual(t.label, "NP")

            # NB: traces cannot be gaps!
            t = T.parse("(NP *%s*=1)" % (tracetype,))
            self.assertIsNone(t.metadata.index)
            self.assertIsNone(t.metadata.idx_type)
            self.assertEqual(t.text, "*%s*=1" % (tracetype,))
            self.assertEqual(t.label, "NP")

            # Invalid trace
            t = T.parse("(NP *%s*-X)" % (tracetype,))
            self.assertIsNone(t.metadata.index)
            self.assertIsNone(t.metadata.idx_type)
            self.assertEqual(t.text, "*%s*-X" % (tracetype,))
            self.assertEqual(t.label, "NP")

            # Invalid trace (gap)
            t = T.parse("(NP *%s*=X)" % (tracetype,))
            self.assertIsNone(t.metadata.index)
            self.assertIsNone(t.metadata.idx_type)
            self.assertEqual(t.text, "*%s*=X" % (tracetype,))
            self.assertEqual(t.label, "NP")


class TreeTest(unittest.TestCase):
    def test_label(self):
        t = L("foo", "bar")
        self.assertEqual(t.label, "foo")
        t.label = "baz"
        self.assertEqual(t.label, "baz")

        def foo(x):
            x.label = ''

        self.assertRaises(ValueError, foo, t)

    def test_parent_index(self):
        t = NT("foo", [L("bar", "BAR"), L("baz", "BAZ")])
        for i, v in enumerate(t):
            self.assertEqual(v._parent_index, i)
            self.assertEqual(t[v._parent_index], v)
        self.assertIsNone(t._parent_index)

    def test_siblings(self):
        l1 = L("bar", "BAR")
        l2 = L("baz", "BAZ")
        t = NT("foo", [l1, l2])
        self.assertIs(l1.right_sibling, l2)
        self.assertIs(l2.left_sibling, l1)
        self.assertIsNone(l1.left_sibling)
        self.assertIsNone(l2.right_sibling)

    def test_root(self):
        l = L("a", "b")
        t = NT("foo", [NT("bar", [l])])
        self.assertIs(l.root, t)

    def test_str_indices(self):
        t = T.parse("( (IP=1 (FOO bar)))")
        self.assertEqual(str(t), "( (IP=1 (FOO bar)))")
        t = T.parse("( (IP (NP-SBJ *T*-1)))")
        self.assertEqual(str(t), "( (IP (NP-SBJ *T*-1)))")
        # TODO: the below is a real issue...what to do about leaves at the top
        # level???
        raise SkipTest
        t = T.parse("( (IP=1 foo))")
        self.assertEqual(str(t), "( (IP=1 foo))")


class NonTerminalTest(unittest.TestCase):
    def test_parse_1(self):
        t = T.parse("( (ID foo) (IP (NP (PRO it)) (VBP works)))")
        self.assertIsInstance(t, T.NonTerminal)
        self.assertEqual(t.metadata.id, 'foo')
        self.assertEqual(t, NT("IP", [NT("NP", [L("PRO", "it")]), L("VBP", "works")], {"ID": "foo"}))

    def test_str(self):
        t = T.parse("""( (IP (NP (D I)) (VBP love) (NP (NPR Python) (NPR programming))))""")
        s = str(t)
        self.assertIsInstance(s, str)
        self.assertMultiLineEqual(s, textwrap.dedent(
            """
            ( (IP (NP (D I))
                  (VBP love)
                  (NP (NPR Python)
                      (NPR programming))))
            """).strip())

    def test_id(self):
        t = T.parse("""( (IP (NP (D I)) (VBP love)
        (NP (NPR Python) (NPR programming)))(ID foo))""")
        # Test that ID is parsed
        self.assertEqual(t.metadata["ID"], "foo")
        # Test that str works
        s = str(t)
        self.assertIsInstance(s, str)
        self.assertMultiLineEqual(s, textwrap.dedent(
            """
            ( (IP (NP (D I))
                  (VBP love)
                  (NP (NPR Python)
                      (NPR programming)))
              (ID foo))
            """).strip())
        t2 = T.parse("""( (ID foo)(IP (NP (D I)) (VBP love)
        (NP (NPR Python) (NPR programming))))""")
        # Test that the order of the ID node doesn't matter to parsing
        self.assertEqual(t2.metadata.id, "foo")
        self.assertEqual(t, t2)
        self.assertEqual(s, str(t2))

    def test_eq(self):
        t = T.parse("(NP (N foo))")
        t2 = T.parse("(NP (N foo))")
        self.assertEqual(t, t2)

    def test_to_json(self):
        raise SkipTest


class LeafTest(unittest.TestCase):
    def assertStr(self, leaf, s):
        self.assertEqual(str(leaf), s)

    def test_str(self):
        l = L("FOO", "bar")
        self.assertStr(l, "(FOO bar)")

    def test_str_idx(self):
        l = L("FOO-1", "bar")
        self.assertStr(l, "(FOO-1 bar)")

    def test_str_lemma(self):
        raise SkipTest
        l = L("FOO", "bar")
        l.metadata.lemma = "baz"
        self.assertStr(l, "(FOO bar-baz)")

    def test_str_trace(self):
        l = L("FOO", "*T*-1")
        self.assertStr(l, "(FOO *T*-1)")

    def test_mult_daughters(self):
        anomalous = "(FOO (BAR baz quux))"
        self.assertRaises(T.ParseError, T.parse, anomalous)

    def test_urtext(self):
        # TODO: woefully incomplete
        tree = "( (IP-MAT (X *T*) (X FOO) (X *con*) (XP (X bar) (X BAZ) (. .)) (CODE dddd)))"
        self.assertEqual(T.parse(tree).urtext, "FOO bar BAZ.")

    def test_to_json(self):
        l = L("FOO", "bar")
        self.assertEqual(l.to_json(),
                         json.dumps({"label": "FOO", "metadata": {"TEXT": "bar"}}))
        self.assertIsNone(l.metadata.text)
