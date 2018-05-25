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

    ll_db = cndb(lookslike_database_df)
    al_db = cndb(alias_df)

    duplicated_list = al_db.get_all_duplicated_primary_names_as_list()
    if duplicated_list:
        raise ProcessNamesException('process_alias: Duplicates in alias file:{0}'.format(', '.join(duplicated_list)))

    duplicated_list = ll_db.get_all_duplicated_primary_names_as_list()
    if duplicated_list:
        raise ProcessNamesException('process_alias: Duplicates in lookslike file:{0}'.format(', '.join(duplicated_list)))

    num_of_rows = al_db.num_of_rows()
    for i in range(num_of_rows):
        alias_names = list(al_db.get_primary_names_by_index(i))
        for name in alias_names:
            found_rows_indexes = ll_db.search_indexes_by_primary_name(name)
            if len(found_rows_indexes) == 1:
                al_db.update_primary_names_by_index(i, ll_db.get_primary_names_by_index(found_rows_indexes[0]))
                ll_db.mark_row_for_deletion(found_rows_indexes[0])
            elif len(found_rows_indexes) > 1:
                raise ProcessNamesException("Duplicated name in lookslike_db: {0}".format(name))

    ll_db.delete_marked_rows()
    al_db.append_db(ll_db)

    output_df = al_db.todataframe(primary_nm_only=True)

    return output_df


def process_lookslike(
    lookslike_database_df: pd.DataFrame,
    all_customer_names: list = None,
    new_names: list = None,
    max_dist=0.0,
    alias_df: pd.DataFrame = None
):

    ll_db = cndb(lookslike_database_df)

    if new_names:
        ll_db.add_new_rows_from_list(new_names)

    if alias_df is not None:
        alias_database = cndb(alias_df)
        ll_db.add_all_primary_names_as_new_rows(alias_database)

    for i in range(ll_db.num_of_rows()):
        for name in ll_db.get_primary_names_by_index(i):
            ll_db.update_question_names_by_index(i,
                                                 dist.find_lookslike_as_list(name,
                                                                             all_customer_names,
                                                                             max_dist))

    for i in range(ll_db.num_of_rows()):
        logging.debug("process_lookslike.ll_db:{0} ?{1} ~{2}".format(ll_db.get_primary_names_by_index(i),
                                                                     ll_db.get_question_names_by_index(i),
                                                                     ll_db.get_discard_names_by_index(i)))

    updated_some_row = True
    while updated_some_row:
        updated_some_row = False
        for i in range(ll_db.num_of_rows()-1):
            if not ll_db.is_marked_for_deletion(i):
                for j in range(i+1, ll_db.num_of_rows()):
                    if not ll_db.is_marked_for_deletion(j):
                        if ll_db.is_intersect_primary_names_in_rows(i, j):
                            ll_db.update_first_row_with_second_row(i, j)
                            ll_db.mark_row_for_deletion(j)
                            updated_some_row = True

    ll_db.delete_marked_rows()

    logging.debug("**********************************************************************")
    for i in range(ll_db.num_of_rows()):
        logging.debug("process_lookslike.ll_db:{0} ?{1} ~{2}".format(ll_db.get_primary_names_by_index(i),
                                                                     ll_db.get_question_names_by_index(i),
                                                                     ll_db.get_discard_names_by_index(i)))

    output_df = ll_db.todataframe()

    return output_df


