import pandas as pd
import customernamedistance as dist
from miscfuncs import take_only_not_empty_str
from custnamedatabase import CustNameDatabase as cndb

import logging

class ProcessNamesException(Exception):
    pass

def get_dict(data_df):

    list_of_rows = data_df.values.tolist()

    dct = {}
    for row in list_of_rows:
        row = take_only_not_empty_str(row)
        row = [w for w in row if w[:1] != '~' and w[:1] != '?']
        for w in row:
            dct[w] = row[0]

    return dct


def assemble_df(input_list_of_rows: list):

    assemble_list = list()
    q_count = 0
    for row in input_list_of_rows:

        row[2] = row[2] - row[0] - row[1] # - checked_names

        if row[0] & row[1]:
            raise Exception('assemble_df: Conflicts in the row:{0}'.format(' '.join(row[0])))

        ok = list(row[0])
        ok.sort(key=lambda w: dist.clear_cust_name(w))

        no = list(row[1])
        no.sort(key=lambda w: dist.clear_cust_name(w))
        no = ["~" + w for w in no]

        q = list(row[2])
        #q.sort(key=lambda w: cnd.clear_cust_name(w))
        q = ["?" + w for w in q]

        q_count = q_count + len(q)

        assemble_list.append(list(ok + q + no))

        assemble_list.sort(key=lambda w: dist.clear_cust_name(w[0]))

    #logging.debug("**************************** assemble_df  ********************************")
    #for row in assemble_list:
        #logging.debug("assemble_df.assemble_list:{0}".format(', '.join(row)))

    max_row_word_count = max(len(r) for r in assemble_list)

    headers = ['Core Name'] + ['name' + str(i) for i in range(max_row_word_count - 1)]

    output_df = pd.DataFrame(columns=headers)

    for row in assemble_list:
        output_df = output_df.append(pd.Series(row, index=headers[:len(row)]), ignore_index=True)

    print(q_count)

    return output_df


def convert_db_to_list_of_rows_of_sets(input_df: pd.DataFrame):
    list_of_rows = input_df.values.tolist()
    output = list()
    for row in list_of_rows:
        row = take_only_not_empty_str(row)
        r = list()
        r.append({w for w in row if w[0] != '~' and w[0] != '?'})  # r[0] = "ok"
        r.append({w[1:] for w in row if w[0] == '~'})  # r[1] = rejected
        r.append({w[1:] for w in row if w[0] == '?'})  # r[2] = question
        output.append(r)

    return output


def process_alias(lookslike_database_df: pd.DataFrame, alias_df: pd.DataFrame):

    lookslike_data = convert_db_to_list_of_rows_of_sets(lookslike_database_df)
    alias_data = convert_db_to_list_of_rows_of_sets(alias_df)

    output = list()
    all_used_names = set()
    for alias_row in alias_data:

        r0 = alias_row[0]
        if r0 & all_used_names:
            raise ProcessNamesException('process_alias: Duplicates:{0}'.format(' '.join(r0)))

        all_used_names.update(r0)
        for i, lookslike_row in enumerate(lookslike_data):
            if alias_row[0] & lookslike_row[0]:
                r0.update(lookslike_row[0])
                lookslike_data[i][0] = set()  # Mark line for deletion

        output.append([r0, set(), set()])

    for row in lookslike_data:
        if row[0]:
            output.append([row[0], set(), set()]) # add not modified lines from lookslike

    output_df = assemble_df(output)

    return output_df


def process_lookslike(
    lookslike_database_df: pd.DataFrame,
    all_customer_names: list = None,
    new_names: list = None,
    max_dist=0.0,
    alias_df: pd.DataFrame = None
):


    lookslike_db_as_list_of_rows = lookslike_database_df.values.tolist()
    #lookslike_database = cndb(lookslike_database_df)



    # add new lines of similar lookslike words
    if new_names:
        for name in new_names:
            lookslike_db_as_list_of_rows.append([name])

    #if new_names:
     #   lookslike_database.add_new_rows_from_list(new_names)

    if alias_df is not None:
        alias_db_as_list_of_rows = alias_df.values.tolist()
        for row in alias_db_as_list_of_rows:
            for name in row:
                lookslike_db_as_list_of_rows.append([name])

    #if alias_df is not None:
    #    alias_database = cnd(alias_df)



    # convert to sets
    work_db = list()
    for row in lookslike_db_as_list_of_rows:
        row = take_only_not_empty_str(row)
        r = list()
        r.append({w for w in row if w[0] != '~' and w[0] != '?'}) #r[0] = "ok"
        r.append({w[1:] for w in row if w[0] == '~'}) #r[1] = rejected
        r.append({w[1:] for w in row if w[0] == '?'}) #r[2] = question
        work_db.append(list(r))

    for row in work_db:
        for name in row[0]:
            row[2].update(dist.find_lookslike_as_list(name, all_customer_names, max_dist))

    for row in work_db:
        logging.debug("process_lookslike.work_db:{0} ?{1} ~{2}".format(row[0], row[2], row[1]))

    while True:
        row_index_for_deletion = []
        num_of_rows = len(work_db)
        for i in range(num_of_rows-1):
            if i not in row_index_for_deletion:
                row_i = work_db[i]
                updated = False
                for j in range(i + 1, num_of_rows):
                    row_j = work_db[j]
                    if j not in row_index_for_deletion:
                        if row_j[0] & row_i[0]:
                            row_i[0].update(row_j[0])
                            row_i[1].update(row_j[1])
                            row_i[2].update(row_j[2])
                            row_index_for_deletion.append(j)
                            updated = True

                if updated:
                    work_db[i] = row_i

        if row_index_for_deletion:
            for i in row_index_for_deletion:
                work_db[i] = None
            work_db = [w for w in work_db if w]
            # work_db = [w for w in work_db if w[0]]

        else:
            work_db = [w for w in work_db if w[0]]
            break

    logging.debug("**********************************************************************")
    for row in work_db:
        logging.debug("process_lookslike.work_db:{0} ?{1} ~{2}".format(row[0], row[2], row[1]))


    output_df = assemble_df(work_db)

    return output_df


