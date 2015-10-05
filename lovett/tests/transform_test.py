import unittest

import lovett.transform as trans
import lovett.tree
T = lovett.tree.parse


class TransformTest(unittest.TestCase):
    def test_icepahc_case(self):
        t = T("(N-N foo)")
        trans.icepahc_case(t)
        self.assertEqual(t.metadata.case, "nominative")

        t = T("(N-A foo)")
        trans.icepahc_case(t)
        self.assertEqual(t.metadata.case, "accusative")

        t = T("(N-G foo)")
        trans.icepahc_case(t)
        self.assertEqual(t.metadata.case, "genitive")

        t = T("(N-D foo)")
        trans.icepahc_case(t)
        self.assertEqual(t.metadata.case, "dative")

        t = T("(N-X foo)")
        trans.icepahc_case(t)
        self.assertIsNone(t.metadata.case)
