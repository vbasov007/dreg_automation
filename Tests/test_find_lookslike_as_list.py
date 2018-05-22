from unittest import TestCase
from customernamedistance import find_lookslike_as_list

import logging


class TestFind_lookslike_as_list(TestCase):
    def test_find_lookslike_as_list(self):
        source = ["ADVERS", "LEDEL", "INCOTEX", "ZAO LEDER", "LEDIL", "ARGUS", "LEDEO"]

        res = find_lookslike_as_list("LEDEL", source, 0.3)

        self.assertEqual(set(res), {"ZAO LEDER", "LEDIL", "LEDEO"})

        source = ["ABIT LTD", "AMBIT OOO", "AMBIT LLC", "AMBIT",
                              "NPF ATI", "ATI NPF", "ATI", "NPFI", "ATIC",
                              "LEDEL", "LEDER", "INKOTEX", "SHTIL", "SCHTYL"]

        res = find_lookslike_as_list("NPF ATI", source, 0.3)

        logging.debug("res = {0}".format(', '.join(res)))

        self.assertEqual(set(res), {"ATI", "ATI NPF", "ATIC"})

        return