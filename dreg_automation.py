from mylogger import mylog

import pandas as pd
import os
import corecustomername as ccm

import glob

from dregdata import DregData
from dregdata import latest_and_earliest_dreg_dates_in_df
from dregdata import is_dreg_data_format
from dregdata import count_dreg_lines_in_df

from datetime import datetime
from dregsolver import DregSolver
from idisclicker import IdisClicker

from DregWriter import DregWriter

import os.path

from idis_website_controller import IdisWebController

from configurator import get_config

class FN(object):
    DATA_FOLDER = "datafiles"
    COREPRODUCT = "coreproduct"
    LAST_CLICKER_RESULT = "last_clicker_result"
    CLICKER_RESULT = "clicker_result"
    DREG_ANALYSIS = "dreg_analysis"

def my_time_stamp():
    return datetime.now().strftime('%Y-%m-%d %H_%M_%S')


def wrk_file(folder_name: str, file_name: str, is_timestamp = False):

    spl = file_name.split(".")
    if len(spl) < 2:
        ext = ""
    else:
        ext = spl[-1]

    nm = file_name.split(".")[0]

    if is_timestamp:
        fname = nm + "_" + my_time_stamp() + "." + ext
    else:
        fname = nm + "." + ext

    return os.path.join(folder_name, fname)


def count_synonym_file_questions(synonyms_df):
    s_list_of_lists = synonyms_df.values.tolist()

    questions_count = 0

    for line in s_list_of_lists:
        questions_count += sum(1 for w in line if str(w)[:1] == '?')

    return questions_count


def run_idis_clicker(dd: DregData, dreg_ids_with_action: list):

    ic = IdisClicker()

    restart_browser = True
    for dreg_id in dreg_ids_with_action:

        if restart_browser:
            ic.start_browser()
            restart_browser = False

        idis_success = True
        if dd.is_action_approve(dreg_id):
            idis_success = ic.approve_DREG_by_id(str(dreg_id))
            dd.set_idis_result(dreg_id, idis_success)
        elif dd.is_action_reject(dreg_id) and dd.is_rejection_reason_already_registered_for_other(dreg_id):
            idis_success = ic.reject_DREG_by_id(str(dreg_id))
            dd.set_idis_result(dreg_id, idis_success)

        if not idis_success:
            print("restart!!!")
            ic.try_to_close_current_dreg_page()
            ic.shutdown_browser()
            restart_browser = True
            dreg_df = dd.get_dreg_data()

            output_file_name = wrk_file(FN.DATA_FOLDER, "last_clicker_result.xlsx", is_timestamp = True)
            writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
            dreg_df.to_excel(writer, index=False)
            writer.save()

    dreg_df = dd.get_dreg_data()

    output_file_name = wrk_file(FN.DATA_FOLDER, "clicker_result.xlsx", is_timestamp = True)
    writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
    dreg_df.to_excel(writer, index=False)
    writer.save()

    return


def update_idis(dd: DregData, dreg_id_list: list, config: dict):

    idis = IdisWebController(portal_url=config['portal_url'],
                             idis_url=config['idis_url'],
                             login=config['login'],
                             password=config['password'],
                             browser=config['browser'],
                             browser_binary=config['browser_binary'],
                             profile_path=config['profile_path'],
                             driver_exe_path=config['driver_exe_path'])

    for dreg_id in dreg_id_list:

        mylog.info("Start update: Dreg ID = {0}".format(dreg_id))

        new_status = dd.get_action_value(dreg_id)

        if new_status != 'Approved' and new_status != 'Rejected':
            mylog.info("New Status = {0} - Skipping the DREG".format(new_status))
            continue

        reason = dd.get_reason_value(dreg_id)

        approver = 'Vasily Basov'

        category = dd.get_category_by_id(dreg_id)
        if category == '':
            category = 'Demand Creation'

        res = idis.update_dreg(dreg_id, new_status, reason, approver, category)
        dd.set_idis_result(dreg_id, res)

        mylog.info("{0} finished with result: {1}".format(dreg_id, res))





class Modes(object):
    DREG_FILE = "dreg_file"
    ALIAS_FILE = "alias_file"
    SYN_FILE = "syn_file"
    CORE_PARTS_FILE = "core_parts_file"


def all_dreg_files_path_in_folder_as_list(folder_path):
    files = glob.glob(os.path.join(folder_path, "*.xlsx"))

    output_lst = list()
    for f in files:
        path = f #os.path.join(folder_path, f)
        df = pd.read_excel(path)
        if is_dreg_data_format(df):
            output_lst.append(path)

    return output_lst


def print_file_info(file_path: str, mode = ''):

    def r_time(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    if not os.path.isfile(file_path):
        print("File {0} doesn't exist".format(file_path))
        return

    print('File: {0}'.format(file_path))
    print('Created: {0}'.format(r_time(os.path.getctime(file_path))))
    print('Modified: {0}'.format(r_time(os.path.getmtime(file_path))))

    if mode == Modes.DREG_FILE:
        try:
            df = pd.read_excel(file_path)
        except PermissionError:
            print("Can't access {0}".format(file_path))
            return

        if is_dreg_data_format(df):
            print("DREG file")
            print("Total number of lines: {0}".format(count_dreg_lines_in_df(df)))
            latest_earliest = latest_and_earliest_dreg_dates_in_df(df)
            print("Latest and earliest DREG date: {0} .. {1}".format(str(latest_earliest[0]), str(latest_earliest[1])))
        else:
            print("The file is not in DREG format")

    return


def main():

   while True:

        print("0 - Show working files info")
        print("1 - Make ''look like'' file")
        print("2 - Make synonym file from alias file and lookslike file")
        print("3 - Process DREGs")
        print("4 - Run Clicker")
        print("5 - Run clicker for failed lines")
        print("6 - Update dreg file")
        print("7 - update one DREG")

        answer = input("->")

        if answer == '0':

            print_file_info(os.path.join(FN.DATA_FOLDER, 'exportdreg.xlsx'), Modes.DREG_FILE)
            print_file_info(os.path.join(FN.DATA_FOLDER, 'updatedreg.xlsx'), Modes.DREG_FILE)
            print_file_info(os.path.join(FN.DATA_FOLDER, 'lookslike.xlsx'))
            print_file_info(os.path.join(FN.DATA_FOLDER, 'alias.xlsx'))
            print_file_info(os.path.join(FN.DATA_FOLDER, 'alias.xlsx'))

        elif answer == '1':

            #print("Max difference between words in %  [0..100]?")
            #answer = input("->")
            answer = 0.35

            lookslike_df = pd.read_excel(wrk_file(FN.DATA_FOLDER, 'lookslike.xlsx'))
            alias_df = pd.read_excel(wrk_file(FN.DATA_FOLDER, 'alias.xlsx'))
            dreg_df = pd.read_excel(wrk_file(FN.DATA_FOLDER, 'exportdreg.xlsx'))

            all_customer_names = DregData.customer_name_list_all(dreg_df)
            all_customers_status_new = DregData.customer_name_list_status_new(dreg_df)

            lookslike_df = ccm.process_lookslike(lookslike_df,
                                                 all_customer_names,
                                                 all_customers_status_new,
                                                 float(answer) / 100,
                                                 alias_df)

            output_file_name = wrk_file(FN.DATA_FOLDER, 'lookslike.xlsx', is_timestamp=True)
            writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
            lookslike_df.to_excel(writer, index=False)
            writer.save()

            print("Open lookslike_XXX.xlsx; fix question marks and save as lookslike.xlsx")

        elif answer == "2":

            lookslike_df = pd.read_excel(wrk_file(FN.DATA_FOLDER, 'lookslike.xlsx'))
            alias_df = pd.read_excel(wrk_file(FN.DATA_FOLDER, 'alias.xlsx'))

            #try:
            synonyms_df = ccm.process_alias(lookslike_df, alias_df)
            #except Exception as e:
            #    print(e)

            output_file_name = wrk_file(FN.DATA_FOLDER, 'synonyms.xlsx', is_timestamp=True)
            writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
            synonyms_df.to_excel(writer, index=False)
            writer.save()

            print("Check latest synonym_XXX")

        elif answer == '3':

            synonyms_df = pd.read_excel( wrk_file(FN.DATA_FOLDER,'synonyms.xlsx') )
            dreg_df = pd.read_excel( wrk_file(FN.DATA_FOLDER,'exportdreg.xlsx') )

            q = count_synonym_file_questions(synonyms_df)
            print('{} of ? in synonyms'.format(q))
            if q > 0:
                print("Open synonym_XXX.xlsx; fix question marks and save as synonym.xlsx")
                continue

            core_part_name_df = pd.read_excel( wrk_file(FN.DATA_FOLDER, "coreproduct.xlsx") )
            core_part_name_df = core_part_name_df[['Type', 'Core Product']]
            core_product_list = core_part_name_df['Core Product'].tolist()
            core_part_name_dict = core_part_name_df.set_index('Type')['Core Product'].to_dict()
            for cp in core_product_list:
                if cp not in core_part_name_dict:
                    core_part_name_dict.update({cp: cp})

            synonyms_dict = ccm.get_dict(synonyms_df)

            dd = DregData(dreg_df, synonyms_dict, core_part_name_dict)

            solver = DregSolver()

            solver.process_all_new(dd)

            solver.process_duplication_check(dd)

            writer = DregWriter()
            writer.set_default_rules()

            output_file_name = wrk_file(FN.DATA_FOLDER, "dreg_analysis.xlsx", is_timestamp=True)
            writer.save_dreg(output_file_name, dd)

            print("Done!")

            print(solver.get_statistics())

        elif answer == "4":

            mylog.info('Starting update IDIS...')

            mylog.debug("Reading 'dreg_analysis.xlsx' file")
            dreg_df = pd.read_excel( wrk_file(FN.DATA_FOLDER,'dreg_analysis.xlsx') )

            mylog.debug("Init DregData database...")
            dd = DregData(dreg_df, add_working_columns=False)

            dreg_ids_with_action = dd.id_list_action_not_empty

            #dreg_ids_with_action = ['20408789']
            mylog.debug("Staring IDIS update with {0} registrations...".format(len(dreg_ids_with_action)))
            update_idis(dd, dreg_ids_with_action, get_config('idis'))

            output_file_name = wrk_file(FN.DATA_FOLDER, "last_clicker_result.xlsx", is_timestamp=True)
            writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
            dreg_df.to_excel(writer, index=False)
            writer.save()
            # run_idis_clicker(dd, dreg_ids_with_action)

        elif answer == "5":
            dreg_df = pd.read_excel( wrk_file(FN.DATA_FOLDER,'dreg_analysis.xlsx') )
            dd = DregData(dreg_df)
            dreg_ids_with_action = dd.id_list_clicker_fail()
            run_idis_clicker(dd, dreg_ids_with_action)

        elif answer == "6":

            p_old_file = os.path.join(FN.DATA_FOLDER, 'exportdreg.xlsx')
            p_new_file = os.path.join(FN.DATA_FOLDER, 'updatedreg.xlsx')

            print_file_info(p_old_file, mode=Modes.DREG_FILE)
            print_file_info(p_new_file, mode=Modes.DREG_FILE)

            print("Result will be saved in exportdreg.xlsx")
            is_yes = input("Continue y/n?")
            if is_yes == 'y':
                init = pd.read_excel(p_old_file)
                upd = pd.read_excel(p_new_file)

                init_dd = DregData(init, add_working_columns=False)
                upd_dd = DregData(upd, add_working_columns=False)

                init_dd.update(upd_dd)

                output_df = init_dd.get_dreg_data()

                output_file_name = wrk_file(FN.DATA_FOLDER, "exportdreg.xlsx")
                writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
                output_df.to_excel(writer, index=False)
                writer.save()

                print("Done!")

                print_file_info(p_old_file, mode=Modes.DREG_FILE)
        elif answer == "7":
            mylog.info('Starting update one DREG...')
            dreg_id = str(input("DREG ID:"))

            mylog.debug("Reading 'dreg_analysis.xlsx' file")
            dreg_df = pd.read_excel(wrk_file(FN.DATA_FOLDER, 'dreg_analysis.xlsx'))

            mylog.debug("Init DregData database...")
            dd = DregData(dreg_df, add_working_columns=False)

            dreg_ids_with_action = [dreg_id]
            mylog.debug("Staring IDIS update with {0} registrations...".format(len(dreg_ids_with_action)))
            update_idis(dd, dreg_ids_with_action, get_config('idis'))

        elif answer == "q":
            break


if __name__ == "__main__":

    main()
