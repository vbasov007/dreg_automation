import pandas as pd
from miscfuncs import get_value_from_dict_by_key
from miscfuncs import remove_duplicates_and_empty_items
from miscfuncs import is_nan
from miscfuncs import string2datatime


class ColName(object):
    REJECTION_REASON = "Rejection Reason"
    ACTION = "Action"
    CORE_PART = "Core Part"
    CORE_CUST_NAME = "Core Customer Name"
    CORE_SUBCON_NAME = "Core Subcontructor Name"
    ORIGINAL_PART_NAME = "Product Name"
    ORIGINAL_CUSTOMER_NAME = "End Customer Name"
    ORIGINAL_SUBCON_NAME = "Subcontractor"
    COMMENTS = "Comments"
    DISTI_NAME = "Sold-To-Party Name"
    STATUS = "Registration Status"
    DREG_ID = "Design Registration ID"
    PROJ_STAGE = "Project Stage"
    REG_DATE = "Registration Date"
    CLICKER_MESSAGE = "Clicker"


class Action(object):
    APPROVE = "Approve"
    REJECT = "Reject"
    PENDING = "Pending"
    MANUAL_DECISION = "???"


class Reason(object):
    ALREADY_REGISTERED_BY_OTHER = "Already registered by other disti"
    OPEN_FOR_ALL = "Open for all"
    DUPLICATED = "Duplicated"


class Status(object):
    NEW = "New"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PENDING = "Pending"


class Stage(object):
    BW_POS = "Business Win POS"
    BW_MANUAL = "Business Win Manual"


class ClickerResult(object):
    FAIL = "Fail"
    SUCCESS = "Success"


class DregData:

    class DregDataException(Exception):
        pass

    def __init__(self, dreg_df: pd.DataFrame,
                 core_cust_names: dict = None,
                 core_part_num: dict = None,
                 add_working_columns=True):

        if not is_dreg_data_format(dreg_df):
            raise DregData.DregDataException("DregData.__init__: DREG table format incorrect!")

        self.dreg_df = dreg_df
        self.core_cust_names = core_cust_names

        self.columns_in_original_order = list(self.dreg_df.columns)
        self.subcon_list = list()

        # make sure that DREG_ID is str and not int or float
        self.dreg_df[ColName.DREG_ID] = self.dreg_df[ColName.DREG_ID].apply(str)

        if add_working_columns:
            self.if_not_exist_add_column_comments()
            self.if_not_exist_add_column_reject_reason()
            self.if_not_exist_add_column_action()
            self.renew_column_core_part(core_part_num)
            self.renew_column_core_subcon_name(core_cust_names)
            self.renew_column_core_cust_name(core_cust_names)
            self.if_not_exist_add_column_clicker_message()

        return

    def if_not_exist_add_column_comments(self):
        if not self.is_column_exist(ColName.COMMENTS):
            self.add_left_column(ColName.COMMENTS)

    def if_not_exist_add_column_reject_reason(self):
        if not self.is_column_exist(ColName.REJECTION_REASON):
            self.add_left_column(ColName.REJECTION_REASON)

    def if_not_exist_add_column_action(self):
        if not self.is_column_exist(ColName.ACTION):
            self.add_left_column(ColName.ACTION)

    def if_not_exist_add_column_clicker_message(self):
        if not self.is_column_exist(ColName.CLICKER_MESSAGE):
            self.add_left_column(ColName.CLICKER_MESSAGE)

    def renew_column_core_part(self, core_part_num: dict):

        if not self.is_column_exist(ColName.CORE_PART):
            self.add_left_column(ColName.CORE_PART)

        self.apply_core_values(core_part_num, ColName.ORIGINAL_PART_NAME, ColName.CORE_PART)

        return

    def renew_column_core_subcon_name(self, core_cust_names: dict):
        if not self.is_column_exist(ColName.CORE_SUBCON_NAME):
            self.add_left_column(ColName.CORE_SUBCON_NAME)

        self.apply_core_values(core_cust_names, ColName.ORIGINAL_SUBCON_NAME, ColName.CORE_SUBCON_NAME)

        self.subcon_list = self.dreg_df[ColName.CORE_SUBCON_NAME].tolist()
        self.subcon_list = filter(bool, self.subcon_list)  # remove empty

        return

    def renew_column_core_cust_name(self, core_cust_names: dict):
        if not self.is_column_exist(ColName.CORE_CUST_NAME):
            self.add_left_column(ColName.CORE_CUST_NAME)

        self.apply_core_values(core_cust_names, ColName.ORIGINAL_CUSTOMER_NAME, ColName.CORE_CUST_NAME)

        return

    @property
    def id_list_all(self):
        return self.dreg_df[ColName.DREG_ID].tolist()

    @property
    def column_list_all(self):
        return list(self.dreg_df.columns)

    def add_empty_row_with_dreg_id(self, dreg_id):
        if dreg_id not in self.id_list_all:
            new_row = pd.Series([dreg_id], index=[ColName.DREG_ID])
            self.dreg_df = self.dreg_df.append(new_row, ignore_index=True)
        else:
            raise DregData.DregDataException('add_empty_row_with_dreg_id: dreg_id {0} already exists'.format(dreg_id))

    def update(self, new_dreg_data):
        old_dreg_ids = self.id_list_all
        new_dreg_ids = new_dreg_data.id_list_all

        old_col_list = self.column_list_all
        new_col_list = new_dreg_data.column_list_all

        if old_col_list != new_col_list:
            raise DregData.DregDataException('DregData.update: old_col_list != new_col_list')

        for dreg_id in new_dreg_ids:
            if dreg_id not in old_dreg_ids:
                self.add_empty_row_with_dreg_id(dreg_id)

            for col in old_col_list:
                val = new_dreg_data.get_value_from_col_by_id(col, dreg_id)
                self.setval(dreg_id, col, val)

        return

    @staticmethod
    def customer_name_list_all(dreg_df):
        res = dreg_df[ColName.ORIGINAL_CUSTOMER_NAME].tolist()
        res.extend(dreg_df[ColName.ORIGINAL_SUBCON_NAME].tolist())
        res = remove_duplicates_and_empty_items(res)
        return res

    @staticmethod
    def customer_name_list_status_new(dreg_df):
        df = dreg_df[dreg_df[ColName.STATUS] == Status.NEW]
        res = df[ColName.ORIGINAL_CUSTOMER_NAME].tolist()
        res = remove_duplicates_and_empty_items(res)
        return res

    def list_of_val_by_key_value(self, output_col_name, key_val_name, key_val, lookup_id_list=None, exclude_key_value=False):

        df = self.dreg_df
        if lookup_id_list is not None:
            df = self.dreg_df[self.dreg_df[ColName.DREG_ID].isin(lookup_id_list)]

        if exclude_key_value:
            df = df.loc[df[key_val_name] != key_val]
        else:
            df = df.loc[df[key_val_name] == key_val]

        return df[output_col_name].tolist()

    def id_list_by_value_in_col(self, col_name, value, lookup_id_list=None):
        if lookup_id_list is not None:
            df = self.dreg_df[self.dreg_df[ColName.DREG_ID].isin(lookup_id_list)]
            df = df.loc[df[col_name] == value]
            return df[ColName.DREG_ID].tolist()
        else:
            df = self.dreg_df.loc[self.dreg_df[col_name] == value]
            return df[ColName.DREG_ID].tolist()

    def id_list_exclude_value_in_col(self, col_name, exclude_value, lookup_id_list=None):
        if lookup_id_list is not None:
            df = self.dreg_df[self.dreg_df[ColName.DREG_ID].isin(lookup_id_list)]
            df = df.loc[df[col_name] != exclude_value]
            return df[ColName.DREG_ID].tolist()
        else:
            df = self.dreg_df.loc[self.dreg_df[col_name] != exclude_value]
            return df[ColName.DREG_ID].tolist()

    def setval(self, dreg_id, col_num, value):
        self.dreg_df.loc[self.dreg_df[ColName.DREG_ID] == dreg_id, col_num] = value

    def id_list_by_core_cust(self, customer_name, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.CORE_CUST_NAME, customer_name, lookup_id_list)

    def id_list_by_core_subcon(self, subcon_name, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.CORE_SUBCON_NAME, subcon_name, lookup_id_list)

    def id_list_by_status(self, status, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.STATUS, status, lookup_id_list)

    def id_list_status_new(self, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.STATUS, Status.NEW, lookup_id_list)

    def id_list_status_approved(self, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.STATUS, Status.APPROVED, lookup_id_list)

    def id_list_status_pending(self, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.STATUS, Status.PENDING, lookup_id_list)

    def id_list_proj_stage_bw(self, lookup_id_list=None):
        res = self.id_list_by_value_in_col(ColName.PROJ_STAGE, Stage.BW_POS, lookup_id_list)
        res.extend(self.id_list_by_value_in_col(ColName.PROJ_STAGE, Stage.BW_MANUAL, lookup_id_list))
        return res

    def id_list_open_for_all(self, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.REJECTION_REASON, Reason.OPEN_FOR_ALL, lookup_id_list)

    @property
    def id_list_action_not_empty(self):
        res = self.id_list_by_value_in_col(ColName.ACTION, Action.APPROVE)
        res.extend(self.id_list_by_value_in_col(ColName.ACTION, Action.REJECT))
        return res

    def id_list_by_core_part(self, core_part, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.CORE_PART, core_part, lookup_id_list)

    def id_list_by_orig_part(self, orig_part, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.ORIGINAL_PART_NAME, orig_part, lookup_id_list)

    def id_list_by_distributor(self, disti, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.DISTI_NAME, disti, lookup_id_list)

    def id_list_exclude_distributor(self, exclude_disti, lookup_id_list=None):
        return self.id_list_exclude_value_in_col(ColName.DISTI_NAME, exclude_disti, lookup_id_list)

    def get_value_from_col_by_id(self, col_name, dreg_id):
        data = self.dreg_df.loc[self.dreg_df[ColName.DREG_ID] == dreg_id]
        if data.empty:
            raise DregData.DregDataException('DregData.update: dreg_id {0} doesnt exist'.format(dreg_id))
        else:
            res = data[col_name].tolist()[0]
            if is_nan(res):
                return ''
            else:
                return data[col_name].tolist()[0]

    def get_core_part_num_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.CORE_PART, dreg_id)

    def get_orig_part_num_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.ORIGINAL_PART_NAME, dreg_id)

    def get_disti_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.DISTI_NAME, dreg_id)

    def get_core_customer_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.CORE_CUST_NAME, dreg_id)

    def get_orig_customer_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.ORIGINAL_CUSTOMER_NAME, dreg_id)

    def get_subcon_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.CORE_SUBCON_NAME, dreg_id)

    def get_date_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.REG_DATE, dreg_id)

    def is_customer_in_subcon_list(self, core_cust_name):
        if core_cust_name in self.subcon_list:
            return True
        else:
            return False

    def is_action_approve(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.ACTION, dreg_id) == Action.APPROVE

    def is_action_reject(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.ACTION, dreg_id) == Action.REJECT

    def is_rejection_reason_already_registered_for_other(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.REJECTION_REASON, dreg_id) == Reason.ALREADY_REGISTERED_BY_OTHER

    def approve(self, dreg_id):
        self.setval(dreg_id, ColName.ACTION, Action.APPROVE)

    def reject(self, dreg_id):
        self.setval(dreg_id, ColName.ACTION, Action.REJECT)

    def ask_for_manual_decision(self, dreg_id):
        self.setval(dreg_id, ColName.ACTION, Action.MANUAL_DECISION)

    def set_rejection_reason_already_registered(self, dreg_id):
        self.setval(dreg_id, ColName.REJECTION_REASON, Reason.ALREADY_REGISTERED_BY_OTHER)

    def set_rejection_reason_duplicated(self, dreg_id):
        self.setval(dreg_id, ColName.REJECTION_REASON, Reason.DUPLICATED)

    def set_rejection_reason_open_for_all(self, dreg_id):
        self.setval(dreg_id, ColName.REJECTION_REASON, Reason.OPEN_FOR_ALL)

    def add_comment(self, dreg_id, string, append=True):
        if not append:
            self.setval(dreg_id, ColName.COMMENTS, '')

        s = self.get_value_from_col_by_id(ColName.COMMENTS, dreg_id)
        s = s + string
        self.setval(dreg_id, ColName.COMMENTS, s)

    def add_clicker_comment(self, dreg_id, comment):
        self.setval(dreg_id, ColName.CLICKER_MESSAGE, comment)

    def add_left_column_if_not_exist(self, column_name):
        if column_name not in self.columns_in_original_order:
            self.columns_in_original_order.insert(0, column_name)
            self.dreg_df[column_name] = pd.Series(index=self.dreg_df.index)

    def add_left_column(self, column_name):
        self.columns_in_original_order.insert(0, column_name)
        self.dreg_df[column_name] = pd.Series(index=self.dreg_df.index)

    def is_column_exist(self, column_name):
        return is_column_exist_in_df(self.dreg_df, column_name)

    def apply_core_values(self, replacing_dict: dict, source_col_name: str, destination_col_name: str):

        assert replacing_dict  # assert dict != None

        self.dreg_df[destination_col_name] = self.dreg_df[source_col_name].apply(
            lambda key: get_value_from_dict_by_key(replacing_dict, key))

    def get_dreg_data(self):
        self.dreg_df = self.dreg_df[self.columns_in_original_order]
        return self.dreg_df

    def set_idis_result(self, dreg_id, success: bool):
        if success:
            self.setval(dreg_id, ColName.CLICKER_MESSAGE, ClickerResult.SUCCESS)
        else:
            self.setval(dreg_id, ColName.CLICKER_MESSAGE, ClickerResult.FAIL)

    def is_clicker_result_success(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.CLICKER_MESSAGE, dreg_id) == ClickerResult.SUCCESS

    def id_list_clicker_fail(self):
        return self.id_list_by_value_in_col(ColName.CLICKER_MESSAGE, ClickerResult.FAIL)

    @property
    def latest_dreg_date(self):
        return latest_and_earliest_dreg_dates_in_df(self.dreg_df)[0]

    @property
    def earliest_dreg_date(self):
        return latest_and_earliest_dreg_dates_in_df(self.dreg_df)[1]

    @property
    def count_new_dregs(self):
        return len(self.id_list_by_value_in_col(ColName.STATUS, Status.NEW))

    @property
    def count_all_lines(self):
        return count_dreg_lines_in_df(self.dreg_df)


def latest_and_earliest_dreg_dates_in_df(df):
    lst = df[ColName.REG_DATE].tolist()
    dates = [string2datatime(d) for d in lst]
    return [max(dates), min(dates)]


def is_column_exist_in_df(df, col_name):
    return col_name in df.columns


def count_dreg_lines_in_df(df):
    return len(df[ColName.DREG_ID].tolist())


def is_dreg_data_format(df):

    correct = is_column_exist_in_df(df, ColName.REG_DATE) and \
              is_column_exist_in_df(df, ColName.DREG_ID) and \
              is_column_exist_in_df(df, ColName.ORIGINAL_CUSTOMER_NAME) and \
              is_column_exist_in_df(df, ColName.DISTI_NAME) and \
              is_column_exist_in_df(df, ColName.ORIGINAL_PART_NAME)

    return correct

