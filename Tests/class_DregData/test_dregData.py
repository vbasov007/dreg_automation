import logging

from unittest import TestCase

import pandas as pd

import os

from dregdata import DregData

from dregdata import ColName


class TestDregData(TestCase):

    def test_update(self):
        init_df = pd.read_excel(os.path.join("Tests", "class_DregData", "Data", "test_update_initial_df.xlsx"))
        upd_df = pd.read_excel(os.path.join("Tests", "class_DregData", "Data", "test_update_upd_df.xlsx"))

        # synonyms_df = pd.read_excel(os.path.join("Tests", "class_DregData", "Data", 'synonyms.xlsx'))
        # core_part_name_df = pd.read_excel(os.path.join("Tests", "class_DregData", "Data", "coreproduct.xlsx"))
        # core_part_name_df = core_part_name_df[['Type', 'Core Product']]
        # core_part_name_dict = core_part_name_df.set_index('Type')['Core Product'].to_dict()

        init_dd = DregData(init_df, add_working_columns=False)
        upd_df = DregData(upd_df, add_working_columns=False)

        init_dd.update(upd_df)

        # result_df = init_dd.get_dreg_data()

        # writer = pd.ExcelWriter(os.path.join("Tests", "class_DregData", "Data", "update_result_df.xlsx"),
        #                        engine='xlsxwriter')
        # result_df.to_excel(writer, index=False)
        # writer.save()

        self.assertEqual(len(init_dd.id_list_all), 10)
        self.assertEqual(len(init_dd.column_list_all), 23)
        self.assertEqual(init_dd.get_orig_customer_by_id('20010744'), 'IZEVSKIY RADIOZAVOD')
        self.assertEqual(init_dd.get_orig_part_num_by_id('20013667'), 'FD650R17IE4')
        self.assertEqual(str(init_dd.latest_dreg_date), "2011-03-02")
        self.assertEqual(str(init_dd.earliest_dreg_date), "2008-12-15")

        return

    def test_id_list_by_value_in_col(self):

        init_df = pd.read_excel(os.path.join("Tests", "class_DregData", "Data", "test_id_list_by_val_in_col_df.xlsx"))
        init_dd = DregData(init_df, add_working_columns=False)

        lst1 = init_dd.id_list_by_value_in_col(ColName.ORIGINAL_SUBCON_NAME,"EFO OOO",
                                        ['20009703','20010744', '20012702','20012849','20013651'])

        lst2 = init_dd.id_list_exclude_value_in_col(ColName.ORIGINAL_SUBCON_NAME,"EFO OOO",
                                        ['20009703','20010744', '20012702','20012849','20013651'])

        self.assertEqual(set(lst1), {'20012849', '20013651'})

        self.assertEqual(set(lst2), {'20009703', '20010744', '20012702'})

        return
