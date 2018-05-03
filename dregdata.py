import pandas as pd
from miscfuncs import get_value_from_dict_by_key
from miscfuncs import remove_duplicates_and_empty_items
from miscfuncs import is_nan


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

    def __init__(self, dreg_df: pd.DataFrame, core_cust_names: dict = None, core_part_num: dict = None):

        self.dreg_df = dreg_df
        self.core_cust_names = core_cust_names

        self.columns_in_original_order = list(self.dreg_df.columns)

        if self.is_column_not_exist(ColName.COMMENTS):
            self.add_left_column(ColName.COMMENTS)

        if self.is_column_not_exist(ColName.REJECTION_REASON):
            self.add_left_column(ColName.REJECTION_REASON)

        if self.is_column_not_exist(ColName.ACTION):
            self.add_left_column(ColName.ACTION)

        if self.is_column_not_exist(ColName.CORE_PART):
            self.add_left_column(ColName.CORE_PART)
            self.apply_core_values(core_part_num, ColName.ORIGINAL_PART_NAME, ColName.CORE_PART)

        if self.is_column_not_exist(ColName.CORE_SUBCON_NAME):
            self.add_left_column(ColName.CORE_SUBCON_NAME)
            self.apply_core_values(core_cust_names, ColName.ORIGINAL_SUBCON_NAME, ColName.CORE_SUBCON_NAME)

        if self.is_column_not_exist(ColName.CORE_CUST_NAME):
            self.add_left_column(ColName.CORE_CUST_NAME)
            self.apply_core_values(core_cust_names, ColName.ORIGINAL_CUSTOMER_NAME, ColName.CORE_CUST_NAME)

        if self.is_column_not_exist(ColName.CLICKER_MESSAGE):
            self.add_left_column(ColName.CLICKER_MESSAGE)

        self.subcon_list = self.dreg_df[ColName.CORE_SUBCON_NAME].tolist()
        self.subcon_list = filter(bool, self.subcon_list)  # remove empty

    def id_list_all(self):
        return self.dreg_df[ColName.DREG_ID].tolist()

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

    def id_list_action_not_empty(self):
        res = self.id_list_by_value_in_col(ColName.ACTION, Action.APPROVE)
        res.extend(self.id_list_by_value_in_col(ColName.ACTION, Action.REJECT))
        return res

    def id_list_by_core_part(self, core_part, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.CORE_PART, core_part, lookup_id_list)

    def id_list_by_distributor(self, disti, lookup_id_list=None):
        return self.id_list_by_value_in_col(ColName.DISTI_NAME, disti, lookup_id_list)

    def id_list_exclude_distributor(self, exclude_disti, lookup_id_list=None):
        return self.id_list_exclude_value_in_col(ColName.DISTI_NAME, exclude_disti, lookup_id_list)

    def get_value_from_col_by_id(self, col_name, dreg_id):
        data = self.dreg_df.loc[self.dreg_df[ColName.DREG_ID] == dreg_id]
        if data.empty:
            raise DregData.DregDataException
        else:
            res = data[col_name].tolist()[0]
            if is_nan(res):
                return ''
            else:
                return data[col_name].tolist()[0]

    def get_core_part_num_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.CORE_PART, dreg_id)

    def get_disti_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.DISTI_NAME, dreg_id)

    def get_customer_by_id(self, dreg_id):
        return self.get_value_from_col_by_id(ColName.CORE_CUST_NAME, dreg_id)

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

    def is_column_not_exist(self, column_name):
        return column_name not in list(self.dreg_df.columns)

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

