
from dregdata import DregData
import pandas as pd
import os

from dregdata import ColName
from dregdata import Status
from dregdata import Stage

class DregWriter:

    def __init__(self):

        self.format_dict = dict()
        pass

    def set_color(self, col_name, value, bg_color, font_color, range_type='row'):

        self.format_dict.update(
            {(col_name, value):
                 {
                     'format': {'bg_color': bg_color, 'font_color': font_color},
                     'range_type': range_type
                  }
             })

    def save(self, file_name, dd: DregData):

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        dd.get_dreg_data().to_excel(writer, index=False, sheet_name='DREGs')

        workbook = writer.book
        worksheet = writer.sheets['DREGs']

        for key in self.format_dict:
            wb_format = workbook.add_format(self.format_dict[key]['format'])
            self.format_dict[key].update({"wb_format": wb_format})

        for row_count, dreg_id in enumerate(dd.id_list_all):
            for key in self.format_dict:
                if dd.get_value_from_col_by_id(key[0], dreg_id) == key[1]:
                    if self.format_dict[key]['range_type'] == 'row':
                        worksheet.set_row(row_count+1, cell_format=self.format_dict[key]['wb_format'])



        writer.save()

        return

def test_DregWriter():

    df = pd.read_excel(os.path.join("Tests", "class_DregWriter", "Data", "test_dregwriter.xlsx"))
    dd = DregData(df, add_working_columns=False)

    writer = DregWriter()

    writer.set_color(ColName.STATUS, Status.NEW, "#E3CF57", "#000000")
    writer.set_color(ColName.PROJ_STAGE, Stage.BW_POS, "#98F5FF", "#000000")

    writer.save(os.path.join("Tests", "class_DregWriter", "Data", "res.xlsx"), dd)

    return


test_DregWriter()

