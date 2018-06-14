
from dregdata import DregData
import pandas as pd
import os

from dregdata import ColName
from dregdata import Status
from dregdata import Stage


class DregWriter:

    def __init__(self):
        self.row_rules = dict()

    def set_row_rule(self, col_name, value, row_format: dict):

        if col_name not in self.row_rules:
            self.row_rules.update({col_name: {value: row_format}})
        else:
            self.row_rules[col_name].update({value: row_format})

        return

    def set_default_rules(self):
        self.set_row_rule(ColName.STATUS, Status.APPROVED, {'bold': True})
        self.set_row_rule(ColName.STATUS, Status.NEW, {'bg_color': "#E3CF57"})
        self.set_row_rule(ColName.STATUS, Status.PENDING, {'bg_color': "#FF6347"})
        self.set_row_rule(ColName.STATUS, Status.REJECTED, {'font_color': "#808A87"})
        self.set_row_rule(ColName.STATUS, Status.CLOSED, {'font_color': "#808A87"})
        self.set_row_rule(ColName.PROJ_STAGE, Stage.BW_POS, {'bg_color': "#98F5FF"})
        self.set_row_rule(ColName.PROJ_STAGE, Stage.BW_MANUAL, {'bg_color': "#8EE5EE"})

    def save_dreg(self, file_name, dd: DregData):

        print('Formatting and saving DREG results...')

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        dd.get_dreg_data().to_excel(writer, index=False, sheet_name='DREGs')
        workbook = writer.book
        worksheet = writer.sheets['DREGs']

        key_names = ['bg_color', 'font_color', 'bold', 'italic']
        wb_format_dict = dict()
        wb_format_dict.update({tuple([False]*4): None})  # default cell format: all val = False => no format

        print('{0} lines in total...'.format(len(dd.id_list_all)))

        for row_count, dreg_id in enumerate(dd.id_list_all):
            f_options = [False] * 4  # [bg_color, font_color, bold, italic]
            for key in self.row_rules:
                val = dd.get_value_from_col_by_id(key, dreg_id)
                if val in self.row_rules[key]:
                    if 'bg_color' in self.row_rules[key][val]:
                        f_options[0] = self.row_rules[key][val]['bg_color']
                    if 'font_color' in self.row_rules[key][val]:
                        f_options[1] = self.row_rules[key][val]['font_color']
                    if 'bold' in self.row_rules[key][val]:
                        f_options[2] = self.row_rules[key][val]['bold']
                    if 'italic' in self.row_rules[key][val]:
                        f_options[3] = self.row_rules[key][val]['italic']

            if tuple(f_options) not in wb_format_dict:
                new_wb_format = workbook.add_format(dict(zip(key_names, f_options)))
                wb_format_dict.update({tuple(f_options): new_wb_format})

            print('Done {0} lines'.format(row_count+1), end='\r')

            worksheet.set_row(row_count + 1, cell_format=wb_format_dict[tuple(f_options)])

        writer.save()

        print('Done! Result saved to {0}'.format(file_name))

        return


def test_dreg_writer():

    df = pd.read_excel(os.path.join("Tests", "class_DregWriter", "Data", "test_dregwriter.xlsx"))
    dd = DregData(df, add_working_columns=False)

    writer = DregWriter()

    writer.set_default_rules()

    writer.save_dreg(os.path.join("Tests", "output", "res.xlsx"), dd)

    return

if __name__ == "__main__":
    test_dreg_writer()