import os

from unittest import TestCase

from corecustomername import process_lookslike
from corecustomername import process_alias
from corecustomername import ProcessNamesException
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

        lookslike_df = pd.read_excel(os.path.join("Tests", "test_process_lookslike_input.xlsx"))
        all_customer_names = ["ABIT LTD", "AMBIT OOO", "AMBIT LLC", "AMBIT",
                              "NPF ATI", "ATI NPF", "ATI", "NPFI", "ATIC",
                              "LEDEL", "LEDER", "INKOTEX", "SHTIL", "SCHTYL"]

        new_names = ["ADBIT OOO", "INCOTEX"]
        alias_df = pd.read_excel(os.path.join("Tests", "test_process_lookslike_aliasxlsx.xlsx"))

        output_df = process_lookslike(lookslike_df,
                                   all_customer_names,
                                   new_names,
                                   0.3,
                                   alias_df )

        correct_df = pd.read_excel(os.path.join("Tests", "test_process_lookslike_result.xlsx"))
        correct_set = name_dataframe_to_sets(correct_df)
        output_set = name_dataframe_to_sets(output_df)


        self.assertEqual(output_set, correct_set)

        return

    def test_process_alias(self):

        # process_alias(lookslike_database_df: pd.DataFrame, alias_df: pd.DataFrame):

        lookslike_df = pd.read_excel(os.path.join("Tests", "test_process_alias_lookslikexlsx_input.xlsx"))
        alias_df = pd.read_excel(os.path.join("Tests", "test_process_alias_duplicate_error_aliasxlsx.xlsx"))

        with self.assertRaises(ProcessNamesException):
            process_alias(lookslike_df, alias_df)

        alias_df = pd.read_excel(os.path.join("Tests", "test_process_alias_aliasxlsx.xlsx"))

        output_df = process_alias(lookslike_df, alias_df)

        correct_df = pd.read_excel(os.path.join("Tests", "test_process_alias_result.xlsx"))

        correct_set = name_dataframe_to_sets(correct_df)
        output_set = name_dataframe_to_sets(output_df)

        self.assertEqual(output_set, correct_set)

        return