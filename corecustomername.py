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
                raise ProcessNamesException("Duplicated name in lookslike file: {0}".format(name))

    ll_db.delete_rows_marked_for_deletion()
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
            if (not ll_db.is_market_as_conflict(i)) and (not ll_db.is_marked_for_deletion(i)):
                for j in range(i+1, ll_db.num_of_rows()):
                    if (not ll_db.is_marked_for_deletion(j)) and (not ll_db.is_marked_for_deletion(j)):
                        if ll_db.is_intersect_primary_names_in_rows(i, j):
                            if ll_db.update_first_row_with_second_row(i, j):  # check if no conflicts in the lines
                                ll_db.mark_row_for_deletion(j)
                            else:
                                ll_db.mark_row_conflict(i)
                                ll_db.mark_row_conflict(j)
                                updated_some_row = True

    ll_db.delete_rows_marked_for_deletion()

    logging.debug("**********************************************************************")
    for i in range(ll_db.num_of_rows()):
        logging.debug("process_lookslike.ll_db:{0} ?{1} ~{2}".format(ll_db.get_primary_names_by_index(i),
                                                                     ll_db.get_question_names_by_index(i),
                                                                     ll_db.get_discard_names_by_index(i)))

    output_df = ll_db.todataframe()

    return output_df


