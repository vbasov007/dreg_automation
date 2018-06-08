import pandas as pd
import datetime

# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 14:44:47 2017

@author: basov
"""
import sys


def input_number_in_range(question, minimum, maximum):
    while True:
        try:
            print('range = ', minimum, maximum)
            user_input = int(input(question))
        except ValueError:
            continue
        else:
            if user_input == 666:
                print("Abort!")
                return -1
            elif user_input < minimum or user_input > maximum:
                print("Out of range!")
                continue
            else:
                return user_input


def choose_file(filelist):
    i = 1
    for f in filelist:
        print(i, end='\t')
        print(f, end='\n')
        i = i + 1

    index = input_number_in_range('enter file index -->', 1, len(filelist))

    if index == -1:
        return None
    else:
        return filelist[index - 1]


def format_float(value, decimals_separator, num_of_decimals):
    return "%s%s%0*u" % (
    int(value), decimals_separator, num_of_decimals, (10 ** num_of_decimals) * (value - int(value)))


class CSVWriter:
    def __init__(self, delim_col=";", delim_row="\n", num_of_decimals=2, decimals_separator='.',
                 file_output=sys.stdout):

        self.delimCol = delim_col
        self.delimRow = delim_row
        self.numOfDecimals = num_of_decimals
        self.decimalsSeparator = decimals_separator
        self.fileOutput = file_output
        self.colHeaders = list()

    def print_float(self, value, end_of_line=False):
        if end_of_line:
            return print(format_float(value, self.numOfDecimals, self.decimalsSeparator), end=self.delimRow,
                         file=self.fileOutput)
        else:
            return print(format_float(value, self.numOfDecimals, self.decimalsSeparator), end=self.delimCol,
                         file=self.fileOutput)

    def print_string(self, string, end_of_line=False):
        if end_of_line:
            return print(string, end=self.delimRow, file=self.fileOutput)
        else:
            return print(string, end=self.delimCol, file=self.fileOutput)

    def print_list_of_strings_and_finish_line(self, string_list: list):

        if len(string_list) > 1:
            for string in string_list[:-1]:
                self.print_string(string)

        self.print_string(string_list[-1], end_of_line=True)

    def set_column_headers(self, *headers):
        self.colHeaders = headers
        return

    def print_column_headers(self, *headers):

        if len(headers) == 0:
            return

        col_count = 0
        for s in headers:
            col_count = col_count + 1
            if col_count < len(headers):
                self.print_string(s)
            else:
                self.print_string(s, end_of_line=True)

        return


def convert_sap_num_to_float(sap_str):
    s = sap_str.replace('.', '')
    s = s.replace(',', '.')
    return float(s)


def remove_duplicates(list_with_duplicates: list) -> list:
    seen = set()
    list_without_duplicates = []
    for x in list_with_duplicates:
        if x in seen:
            continue
        seen.add(x)
        list_without_duplicates.append(x)

    return list_without_duplicates


def remove_duplicates_and_empty_items(list_with_duplicates: list) -> list:
    res = remove_duplicates(list_with_duplicates)
    res = [item for item in res if item]  # remove empty

    return res


def get_value_from_dict_by_key(dct, key, return_if_not_found=""):
    if key in dct:
        n = dct[key]
        return n
    else:
        return return_if_not_found


def is_nan(num):
    return num != num


def name_dataframe_to_sets(df: pd.DataFrame):
    df_rows = df.values.tolist()
    return set(frozenset(filter(lambda r: isinstance(r, str), row)) for row in df_rows)


def take_only_not_empty_str(input_list):
    return list(filter(lambda w: isinstance(w, str) and w != '', input_list))


def string2datatime(d: str):
    """
    :param s: date in format dd.mm.yyyy
    :return: datatime.date
    """
    return datetime.date(int(d[6:10]), int(d[3:5]), int(d[0:2]))

