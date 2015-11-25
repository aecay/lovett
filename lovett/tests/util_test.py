import unittest
from nose.plugins.skip import SkipTest

import lovett.util
import lovett.tree


class UtilTest(unittest.TestCase):
    def test_label_and_index(self):
        li = lovett.util.label_and_index
        self.assertEqual(li("FOO-1"), ("FOO", lovett.util.IDX_REGULAR, 1))
        self.assertEqual(li("FOO=1"), ("FOO", lovett.util.IDX_GAP, 1))
        self.assertEqual(li("FOO-BAR-1"), ("FOO-BAR", lovett.util.IDX_REGULAR, 1))
        self.assertEqual(li("FOO-BAR=1"), ("FOO-BAR", lovett.util.IDX_GAP, 1))
        self.assertEqual(li("FOO-123"), ("FOO", 'regular', 123))
        self.assertEqual(li("FOO=BAR-1"), ("FOO=BAR", lovett.util.IDX_REGULAR, 1))
        self.assertEqual(li("NP-1"), ("NP", lovett.util.IDX_REGULAR, 1))
        self.assertEqual(li("NP-FOO-1"), ("NP-FOO", lovett.util.IDX_REGULAR, 1))
        self.assertEqual(li("NP=1"), ("NP", lovett.util.IDX_GAP, 1))
        self.assertIsNone(li("NP")[1])
        self.assertIsNone(li("NP")[2])
        self.assertRaises(ValueError, li, "NP=FOO=BAR")

    def test_index(self):
        cases = [("(NP-1 (D foo))", 1, "-", lovett.util.IDX_REGULAR),
                 ("(NP *T*-1)", 1, "-", lovett.util.IDX_REGULAR),
                 ("(XP *ICH*-3)", 3, "-", lovett.util.IDX_REGULAR),
                 ("(XP *-34)", 34, "-", lovett.util.IDX_REGULAR),
                 ("(XP *CL*-1)", 1, "-", lovett.util.IDX_REGULAR),
                 ("(XP=4 (X foo))", 4, "=", lovett.util.IDX_GAP),
                 ("(XP *FOO*-1)", None, None, None),
                 ("(NP (D foo))", None, None, None)]
        for (s, i, ts, t) in cases:
            self.assertEqual(lovett.util.index(lovett.tree.parse(s)), i)
            # self.assertEqual(lovett.util.index_type_short(
            #     lovett.tree.parse(s)), ts)
            self.assertEqual(lovett.util.index_type(lovett.tree.parse(s)),
                             t)

    def test_remove_index(self):
        cases = [("(NP-1 (D foo))", "(NP (D foo))"),
                 ("(NP *T*-1)", "(NP *T*)"),
                 ("(XP *ICH*-3)", "(XP *ICH*)"),
                 ("(XP *-34)", "(XP *)"),
                 ("(XP *CL*-1)", "(XP *CL*)"),
                 ("(XP=4 (X foo))", "(XP (X foo))"),
                 ("(XP *FOO*-1)", "(XP *FOO*-1)"),
                 ("(NP (D foo))", "(NP (D foo))")]
        for (orig, new) in cases:
            ot = lovett.tree.parse(orig)
            lovett.util.remove_index(ot)
            self.assertEqual(ot, lovett.tree.parse(new))

    def test_is_leaf(self):
        self.assertTrue(lovett.util.is_leaf(lovett.tree.parse("(N foo)")))
        self.assertTrue(lovett.util.is_leaf(lovett.tree.parse("(N *T*-1)")))
        self.assertTrue(lovett.util.is_leaf(lovett.tree.parse("(N 0)")))
        self.assertTrue(lovett.util.is_leaf(lovett.tree.parse("(N *con*)")))
        self.assertFalse(lovett.util.is_leaf(lovett.tree.parse("(NP (N foo))")))

    def test_is_trace(self):
        self.assertFalse(lovett.util.is_trace(lovett.tree.parse("(N foo)")))
        self.assertFalse(lovett.util.is_trace(lovett.tree.parse("(N 0)")))
        self.assertFalse(lovett.util.is_trace(lovett.tree.parse("(N *con*)")))
        self.assertFalse(lovett.util.is_trace(lovett.tree.parse("(NP (N foo))")))

        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *T*-1)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *ICH*-1)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *CL*-1)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *-1)")))
        self.assertFalse(lovett.util.is_trace(lovett.tree.parse("(N *FOO*-1)")))

        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *T*)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *ICH*)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *CL*)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *)")))
        self.assertFalse(lovett.util.is_trace(lovett.tree.parse("(N *FOO*)")))

        raise SkipTest
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *T*=1)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *ICH*=1)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *CL*=1)")))
        self.assertTrue(lovett.util.is_trace(lovett.tree.parse("(N *=1)")))
        self.assertFalse(lovett.util.is_trace(lovett.tree.parse("(N *FOO*=1)")))

    def test_is_trace_string(self):
        self.assertTrue(lovett.util.is_trace_string("*T*-1"))
        self.assertTrue(lovett.util.is_trace_string("*ICH*-1"))
        self.assertTrue(lovett.util.is_trace_string("*CL*-1"))
        self.assertTrue(lovett.util.is_trace_string("*-1"))
        self.assertFalse(lovett.util.is_trace_string("*FOO*-1"))

        self.assertTrue(lovett.util.is_trace_string("*T*"))
        self.assertTrue(lovett.util.is_trace_string("*ICH*"))
        self.assertTrue(lovett.util.is_trace_string("*CL*"))
        self.assertTrue(lovett.util.is_trace_string("*"))
        self.assertFalse(lovett.util.is_trace_string("*FOO*"))

    def test_is_silent(self):
        self.assertTrue(lovett.util.is_silent(lovett.tree.parse("(NP *con*)")))
        self.assertTrue(lovett.util.is_silent(lovett.tree.parse("(NP *pro*)")))
        self.assertTrue(lovett.util.is_silent(lovett.tree.parse("(NP *exp*)")))
        self.assertFalse(lovett.util.is_silent(lovett.tree.parse("(NP *foo*)")))
        self.assertFalse(lovett.util.is_silent(lovett.tree.parse("(NP foo)")))
        self.assertFalse(lovett.util.is_silent(lovett.tree.parse("(NP (N *foo*))")))
        self.assertFalse(lovett.util.is_silent(lovett.tree.parse("(NP (N *con*))")))

    def test_is_ec(self):
        raise SkipTest

    def test_is_text_leaf(self):
        raise SkipTest
