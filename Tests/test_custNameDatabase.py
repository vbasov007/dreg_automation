import os
import unittest
from unittest import TestCase

import pandas as pd

from custnamedatabase import CustNameDatabase


class TestCustNameDatabase(TestCase):

    def test_init_with_dataframe(self):
        df = pd.read_excel(os.path.join("Tests", "test_lookslike.xlsx"))
        database = CustNameDatabase(df)

        self.assertEqual(database.count_rows(), 7)
        self.assertEqual(database.count_question_names(), 3)
        self.assertEqual(database.count_primary_names(), 16)
        self.assertEqual(database.count_discard_names(), 19)

        self.assertEqual(database.get_primary_names_by_index(4), {"ALR LLC", "ALR", "ALR SPB"})

        return

    def test_add_new_rows_from_list(self):

        df = pd.read_excel(os.path.join("Tests", "test_lookslike.xlsx"))
        database = CustNameDatabase(df)

        database.add_new_rows_from_list(["ARGOS-ELECTRON", "NEW CUSTOMER",])

        self.assertEqual(database.count_rows(), 8)
        self.assertEqual(database.count_question_names(), 3)
        self.assertEqual(database.count_primary_names(), 17)
        self.assertEqual(database.count_discard_names(), 19)

        self.assertEqual(database.get_primary_names_by_index(7), {"NEW CUSTOMER"})

        return

    def test_mark_row_for_deletion(self):
        df = pd.read_excel(os.path.join("Tests", "test_lookslike.xlsx"))
        database = CustNameDatabase(df)

        database.mark_row_for_deletion(4)
        database.delete_marked_rows()

        self.assertEqual(database.count_rows(), 6)
        self.assertEqual(database.count_question_names(), 3)
        self.assertEqual(database.count_primary_names(), 13)
        self.assertEqual(database.count_discard_names(), 15)

        self.assertEqual(database.get_primary_names_by_index(4), {"ARGOS ELECTRON","ARGOS-ELECTRON","ARGOS-TRADE"})

        return

if __name__ == '__main__':
    unittest.main()
