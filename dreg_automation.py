import pandas as pd
import os
from corecustomername import CoreCustomerNameSolver as CustName
from dregdata import DregData
from datetime import datetime
from dregsolver import DregSolver
from idisclicker import IdisClicker

DATA_FOLDER = "datafiles"
SYNONIMS = "synonims"
EXPORTDREG = "exportdreg"
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
    else: ext = spl[-1]

    nm = file_name.split(".")[0]

    if is_timestamp:
        fname = nm + "_" + my_time_stamp() + "." + ext
    else:
        fname = nm + "." + ext

    return os.path.join(folder_name, fname)


def count_synonim_file_questions(synonims_df):
    s_list_of_lists = synonims_df.values.tolist()

    questions_count = 0

    for line in s_list_of_lists:
        questions_count += sum(1 for w in line if str(w)[:1] == '?')

    return questions_count


def run_idis_clicker(dd: DregData, dreg_ids_with_action: list):

    ic = IdisClicker()

    dreg_df = pd.read_excel(wrk_file(DATA_FOLDER, "dreg_analysis.xlsx"))

    dd = DregData(dreg_df)

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

            output_file_name = wrk_file(DATA_FOLDER, "last_clicker_result.xlsx", is_timestamp = True)
            writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
            dreg_df.to_excel(writer, index=False)
            writer.save()


    dreg_df = dd.get_dreg_data()

    output_file_name = wrk_file(DATA_FOLDER, "clicker_result.xlsx", is_timestamp = True)
    writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
    dreg_df.to_excel(writer, index=False)
    writer.save()

    return

def main():


    while True:

        print("1 - Make synonim file")
        print("2 - Process DREGs")
        print("3 - Run Clicker")
        print("4 - Run clicker for failed lines")
        print("5 - Make ''look like'' file")

        answer = input("->")

        if answer == '1':

            synonims_df = pd.read_excel( wrk_file(DATA_FOLDER,'synonims.xlsx') )
            dreg_df = pd.read_excel( wrk_file(DATA_FOLDER,'exportdreg.xlsx') )

            all_customer_names = DregData.customer_name_list_all(dreg_df)
            all_customers_status_new = DregData.customer_name_list_status_new(dreg_df)

            synonims_df = CustName.process(all_customer_names, all_customers_status_new,  synonims_df)

            output_file_name = wrk_file(DATA_FOLDER,'synonims.xlsx', is_timestamp = True)
            writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
            synonims_df.to_excel(writer, index=False)
            writer.save()

            print('{} of ? in synonims'.format(count_synonim_file_questions(synonims_df)))
            print("Open synonim_XXX.xlsx; fix question marks and save as synonim.xlsx")

        elif answer == '2':

            synonims_df = pd.read_excel( wrk_file(DATA_FOLDER,'synonims.xlsx') )
            dreg_df = pd.read_excel( wrk_file(DATA_FOLDER,'exportdreg.xlsx') )

            q = count_synonim_file_questions(synonims_df)
            print('{} of ? in synonims'.format(q))
            if q > 0:
                print("Open synonim_XXX.xlsx; fix question marks and save as synonim.xlsx")
                continue

            core_part_name_df = pd.read_excel( wrk_file(DATA_FOLDER,"coreproduct.xlsx") )
            core_part_name_df = core_part_name_df[['Type', 'Core Product']]
            core_part_name_dict = core_part_name_df.set_index('Type')['Core Product'].to_dict()

            synonims_dict = CustName.get_dict(synonims_df)

            dd = DregData(dreg_df, synonims_dict, core_part_name_dict)

            solver = DregSolver()

            solver.process_all_new(dd)

            dreg_df = dd.get_dreg_data()

            output_file_name =  wrk_file(DATA_FOLDER, "dreg_analysis.xlsx", is_timestamp=True)
            writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
            dreg_df.to_excel(writer, index=False)
            writer.save()

            print("Done!")

            print(solver.get_statistics())

        elif answer == "3":

            dreg_df = pd.read_excel( wrk_file(DATA_FOLDER,'dreg_analysis.xlsx') )
            dd = DregData(dreg_df)
            dreg_ids_with_action = dd.id_list_action_not_empty()
            run_idis_clicker(dd, dreg_ids_with_action)

        elif answer == "4":
            dreg_df = pd.read_excel( wrk_file(DATA_FOLDER,'dreg_analysis.xlsx') )
            dd = DregData(dreg_df)
            dreg_ids_with_action = dd.id_list_clicker_fail()
            run_idis_clicker(dd, dreg_ids_with_action)
        
        elif answer == "5":
            print("Max difference between words in %  [0..100]?")
            answer = input("->")

            lookslike_df = pd.read_excel( wrk_file(DATA_FOLDER,'lookslike.xlsx') )
            dreg_df = pd.read_excel( wrk_file(DATA_FOLDER,'exportdreg.xlsx') )

            all_customer_names = DregData.customer_name_list_all(dreg_df)
            all_customers_status_new = DregData.customer_name_list_status_new(dreg_df)

            lookslike_df = CustName.process_lookslike(all_customer_names, all_customers_status_new,  lookslike_df, float(answer)/100 )

            output_file_name = wrk_file(DATA_FOLDER,'lookslike.xlsx', is_timestamp = True)
            writer = pd.ExcelWriter(output_file_name, engine='xlsxwriter')
            lookslike_df.to_excel(writer, index=False)
            writer.save()

            print("Open lookslike_XXX.xlsx; fix question marks and save as lookslike.xlsx")

            break


if __name__ == "__main__":
    main()
