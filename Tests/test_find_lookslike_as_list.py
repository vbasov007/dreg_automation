from unittest import TestCase
from customernamedistance import find_lookslike_as_list


class TestFind_lookslike_as_list(TestCase):
    def test_find_lookslike_as_list(self):
        source = ["ADVERS", "LEDEL", "INCOTEX", "ZAO LEDER", "LEDIL", "ARGUS", "LEDEO"]

        res = find_lookslike_as_list("LEDEL", source, 0.3)

        self.assertEqual(res, ["ZAO LEDER", "LEDIL", "LEDEO"])

        return