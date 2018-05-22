
import logging
import pandas as pd
from customernamedistance import clear_cust_name
from miscfuncs import take_only_not_empty_str


class TxtMark(object):
    DSCRD = "~"
    QUE = "?"


class CustNameDatabase:

    class CustNameDatabaseException(Exception):
        pass

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
            return

        def reduce_question_nm_set(self, reduce_by_set: set):
            self.question_nm_set = self.question_nm_set - self.primary_nm_set - self.discard_nm_set - reduce_by_set
            return

        def is_correct(self):

            if self.primary_nm_set & self.discard_nm_set:
                return False

            if self.primary_nm_set & self.question_nm_set:
                return False

            if self.discard_nm_set & self.question_nm_set:
                return False

            return True

        def totxtlist(self, use_clean_name=True,  sort_questions=False):

            p = list(self.primary_nm_set)
            d = list(self.discard_nm_set)
            q = list(self.question_nm_set)

            if use_clean_name:
                p.sort(key=lambda w: clear_cust_name(w))
                d.sort(key=lambda w: clear_cust_name(w))
                if sort_questions:
                    q.sort(key=lambda w: clear_cust_name(w))
            else:
                p.sort()
                d.sort()
                if sort_questions:
                    q.sort()

            d = [TxtMark.DSCRD + w for w in d]
            q = [TxtMark.QUE + w for w in q]

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
            #txt_row = [w for w in txt_row if isinstance(w, str)]
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

    def get_primary_names_by_index(self, index) -> set:
            return self.rows[index].primary_nm_set

    def mark_row_for_deletion(self, index):
        self.rows[index].marked_for_delete = True

    def delete_marked_rows(self):
        self.rows = [r for r in self.rows if not r.marked_for_delete]

    def num_of_rows(self):
        return len(self.rows)

    def todataframe(self) -> pd.DataFrame:

        checked_names = set()
        for row in self.rows:
            checked_names.update(row.primary_nm_set)

        assemble_list = list()

        for row in self.rows:
            row.reduce_question_nm_set(checked_names)
            if not row.is_correct():
                raise self.CustNameDatabaseException('todataframe: Conflicts in the row:{0}'.format(' '.join(row.primary_nm_set)))
            assemble_list.append(row.totxtlist())

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