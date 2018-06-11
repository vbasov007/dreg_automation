import logging
import pandas as pd
from customernamedistance import clear_cust_name
from miscfuncs import take_only_not_empty_str


class TxtMark(object):
    DSCRD = "~"
    QUE = "?"


class CustNameDatabaseException(Exception):
    pass


class CustNameDatabase:
    class Row:

        def __init__(self, primary_names: set, discard_names=None, question_names=None):

            self.primary_nm_set = set(primary_names)

            if discard_names:
                self.discard_nm_set = set(discard_names)
            else:
                self.discard_nm_set = set()

            if question_names:
                self.question_nm_set = set(question_names)
            else:
                self.question_nm_set = set()

            self.marked_for_delete = False
            self.marked_conflict = False

            return

        def is_correct(self):

            if self.primary_nm_set & self.discard_nm_set:
                return False

            if self.primary_nm_set & self.question_nm_set:
                return False

            if self.discard_nm_set & self.question_nm_set:
                return False

            return True

        def update(self, other_row):
            self.primary_nm_set.update(other_row.primary_nm_set)
            self.question_nm_set.update(other_row.question_nm_set)
            self.discard_nm_set.update(other_row.discard_nm_set)
            # reduce questions
            self.question_nm_set = self.question_nm_set - self.primary_nm_set - self.discard_nm_set

            if self.primary_nm_set & self.discard_nm_set:
                logging.warning("Conflicting names ''{0}'' in row ''{1}''".format(self.primary_nm_set &
                                                                                  self.discard_nm_set,
                                                                                  self.primary_nm_set))
                return False
                # raise CustNameDatabaseException

            return True

        def totxtlist(self, use_clean_name=True, primary_names_only=False):

            p = list(self.primary_nm_set)
            d = list(self.discard_nm_set)
            q = list(self.question_nm_set)

            if use_clean_name:
                p.sort(key=lambda w: clear_cust_name(w))
                d.sort(key=lambda w: clear_cust_name(w))
                q.sort(key=lambda w: clear_cust_name(w))
            else:
                p.sort()
                d.sort()
                q.sort()

            d = [TxtMark.DSCRD + w for w in d]
            q = [TxtMark.QUE + w for w in q]

            if primary_names_only:
                return list(p)
            else:
                return list(p + q + d)

        def count_primary(self):
            return len(self.primary_nm_set)

        def count_que(self):
            return len(self.question_nm_set)

        def count_discard(self):
            return len(self.discard_nm_set)

    def __init__(self, input_df: pd.DataFrame = None):

        self.rows = list()
        self.all_primary_names_set = set()

        if input_df is not None:
            self.init_with_dataframe(input_df)

        return

    def init_with_dataframe(self, input_df: pd.DataFrame):

        list_of_txt_rows = input_df.values.tolist()
        self.rows = list()
        self.all_primary_names_set = set()

        for txt_row in list_of_txt_rows:
            txt_row = take_only_not_empty_str(txt_row)
            self.rows.append(self.Row(
                primary_names={w for w in txt_row if w[0] != TxtMark.DSCRD and w[0] != TxtMark.QUE},
                discard_names={w[1:] for w in txt_row if w[0] == TxtMark.DSCRD},
                question_names={w[1:] for w in txt_row if w[0] == TxtMark.QUE}
            ))

        self.update_all_primary_names_set()

        return

    def add_all_primary_names_as_new_rows(self, db):
        for row in db.rows:
            for w in row.primary_nm_set:
                if w not in self.all_primary_names_set:
                    self.rows.append(self.Row({w}))

        self.update_all_primary_names_set()

        return

    def update_all_primary_names_set(self):

        self.all_primary_names_set = set()
        for row in self.rows:
            self.all_primary_names_set.update(row.primary_nm_set)

        return

    def add_new_rows_from_list(self, source_list: list):

        for word in source_list:
            if word not in self.all_primary_names_set:
                self.rows.append(self.Row({word}, {}, {}))
                self.all_primary_names_set.update([word])

        return

    def search_indexes_by_primary_name(self, name: str) -> list:
        res = list()
        for i, row in enumerate(self.rows):
            if name in row.primary_nm_set:
                res.append(i)
        return res

    def append_db(self, merging_db):
        self.rows = self.rows + merging_db.rows
        return

    def get_all_duplicated_primary_names_as_list(self) -> list:

        duplicated_names = list()
        seen_names = list()
        for row in self.rows:
            for pn in row.primary_nm_set:
                if pn in seen_names:
                    duplicated_names.append(pn)
                else:
                    seen_names.append(pn)

        return duplicated_names

    def update_question_names_by_index(self, index, new_names):
        self.rows[index].question_nm_set.update(new_names)
        return

    def update_primary_names_by_index(self, index, new_names):
        self.rows[index].primary_nm_set.update(new_names)
        return

    def update_discard_names_by_index(self, index, new_names):
        self.rows[index].discard_nm_set.update(new_names)
        return

    def update_first_row_with_second_row(self, i1, i2):
        return self.rows[i1].update(self.rows[i2])

    def get_primary_names_by_index(self, index) -> set:
        return self.rows[index].primary_nm_set

    def get_discard_names_by_index(self, index) -> set:
        return self.rows[index].discard_nm_set

    def get_question_names_by_index(self, index) -> set:
        return self.rows[index].question_nm_set

    def mark_row_for_deletion(self, index):
        self.rows[index].marked_for_delete = True
        return

    def mark_row_conflict(self, index):
        self.rows[index].marked_conflict = True
        return

    def delete_rows_marked_for_deletion(self):
        self.rows = [r for r in self.rows if not r.marked_for_delete]
        return

    def is_marked_for_deletion(self, index):
        return self.rows[index].marked_for_delete

    def is_market_as_conflict(self, index):
        return self.rows[index].marked_conflict

    def is_intersect_primary_names_in_rows(self, i, j):
        return bool(self.rows[i].primary_nm_set & self.rows[j].primary_nm_set)

    def num_of_rows(self):
        return len(self.rows)

    def todataframe(self, primary_nm_only=False) -> pd.DataFrame:

        checked_names = set()
        for row in self.rows:
            checked_names.update(row.primary_nm_set)

        assemble_list = list()

        for row in self.rows:
            row.question_nm_set = row.question_nm_set - row.primary_nm_set - row.discard_nm_set
            if not row.is_correct():
                # raise CustNameDatabaseException('todataframe: Conflicts in the row:{0}'.format(' '.join(row.primary_nm_set)))
                print('Conflicts in the row:{0}'.format(' '.join(row.primary_nm_set)))
            assemble_list.append(row.totxtlist(primary_names_only=primary_nm_only, use_clean_name=True))

        assemble_list.sort(key=lambda w: clear_cust_name(w[0]))
        max_row_word_count = max(len(r) for r in assemble_list)
        headers = ['Core Name'] + ['name' + str(i) for i in range(max_row_word_count - 1)]
        output_df = pd.DataFrame(columns=headers)

        for row in assemble_list:
            output_df = output_df.append(pd.Series(row, index=headers[:len(row)]), ignore_index=True)

        return output_df

    def count_rows(self):
        return len(self.rows)

    def count_question_names(self):
        return sum(row.count_que() for row in self.rows)

    def count_primary_names(self):
        return sum(row.count_primary() for row in self.rows)

    def count_discard_names(self):
        return sum(row.count_discard() for row in self.rows)

    def log_all(self):
        for row in self.rows:
            logging.debug("{0}, ?{1}, ~{2}".format(row.primary_nm_set, row.question_nm_set, row.discard_nm_set))
