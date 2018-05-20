import os

from unittest import TestCase

from corecustomername import process_lookslike
from corecustomername import process_alias

import pandas as pd

from miscfuncs import name_dataframe_to_sets


class TestProcess_names(TestCase):

    def test_process_lookslike(self):
        '''
        process_lookslike(
            lookslike_database_df: pd.DataFrame,
            all_customer_names: list = None,
            new_names: list = None,
            max_dist = 0.0,
            alias_df: pd.DataFrame = None)
        '''

        looklike_df = pd.read_excel(os.path.join("Tests", "test_lookslike1.xlsx"))
        all_customer_names = ["ABIT LTD", "AMBIT OOO", "AMBIT LLC", "AMBIT",
                              "NPF ATI", "ATI NPF", "ATI", "NPFI", "ATIC",
                              "LEDEL", "LEDER", "INKOTEX", "SHTIL", "SCHTYL"]

        new_names = ["ADBIT OOO", "INCOTEX"]
        alias_df = pd.read_excel(os.path.join("Tests", "test_alias.xlsx"))

        output_df = process_lookslike(looklike_df,
                                   all_customer_names,
                                   new_names,
                                   0.3,
                                   alias_df )

        correct_df = pd.read_excel(os.path.join("Tests", "test_lookslike1_result.xlsx"))
        correct_set = name_dataframe_to_sets(correct_df)
        output_set = name_dataframe_to_sets(output_df)


        self.assertEqual(output_set, correct_set)

        return

    def test_process_alias(self):
        self.fail()