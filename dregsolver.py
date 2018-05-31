from dregdata import DregData


class DregSolver:

    def __init__(self):

        self.count_processed_lines = 0
        self.count_approved = 0
        self.count_rejected = 0
        self.count_question = 0

    def get_statistics(self):
        return {
            "Processed lines": self.count_processed_lines,
            "Approved": self.count_approved,
            "Rejected": self.count_rejected,
            "Manual decision": self.count_question,
        }

    def process_all_new(self, dd: DregData):

        dreg_id_status_new = dd.id_list_status_new()

        print(str(len(dreg_id_status_new)) + " New design registrations")

        for dreg_id in dreg_id_status_new:
            print("Processing: " + str(dreg_id) + " ")
            self.process_dreg_by_id(dd, dreg_id)
            self.count_processed_lines += 1
            print("\rDone!")

    def process_dreg_by_id(self, dd: DregData, dreg_id):

        part = dd.get_core_part_num_by_id(dreg_id)
        customer = dd.get_core_customer_by_id(dreg_id)
        disti = dd.get_disti_by_id(dreg_id)
        # subcon = dd.get_subcon_by_id(dreg_id)

        dreg_id_all_exclude_current = dd.id_list_all()
        dreg_id_all_exclude_current.remove(dreg_id)

        # customer is in sub-contructor list: warning
        if dd.is_customer_in_subcon_list(customer):
            dd.add_comment(dreg_id, "Customer is in subcon list")

        # different dreg id but the same part and customer
        lst = dd.id_list_by_core_part(part, dreg_id_all_exclude_current)
        dreg_id_with_same_part_and_customers = dd.id_list_by_core_cust(customer, lst)

        # Other registrations rejected with "open for all"
        #check_list = dd.id_list_open_for_all(dreg_id_with_same_part_and_customers)
        #if check_list:
        #    dd.ask_for_manual_decision(dreg_id)
        #    dd.add_comment(dreg_id, "Open for All")
        #   return

        # Valid approved registration for other disti: reject
        check_list = dd.id_list_exclude_distributor(disti, dreg_id_with_same_part_and_customers)
        check_list = dd.id_list_status_approved(check_list)
        if check_list:
            dd.reject(dreg_id)
            self.count_rejected += 1
            dd.set_rejection_reason_already_registered(dreg_id)
            comment = "Registered:"+dd.get_disti_by_id(check_list[0])[:3]+"-"+str(check_list[0])+":" \
                      + dd.get_date_by_id(dreg_id)
            dd.add_comment(dreg_id, comment)
            return

        # Duplicated registration for the same disti: reject
        check_list = dd.id_list_by_distributor(disti, dreg_id_with_same_part_and_customers)
        check_list = dd.id_list_status_approved(check_list)
        if check_list:
            dd.reject(dreg_id)
            self.count_rejected += 1
            dd.set_rejection_reason_duplicated(dreg_id)
            comment = "Duplicated: "+str(check_list[0])+":" \
                      + dd.get_date_by_id(check_list[0])
            dd.add_comment(dreg_id, comment)
            return

        # New registrations for more than one distri: Action = '???'
        check_list = dd.id_list_exclude_distributor(disti, dreg_id_with_same_part_and_customers)
        check_list = dd.id_list_status_new(check_list)
        if check_list:
            dd.ask_for_manual_decision(dreg_id)
            self.count_question += 1
            comment = "New from others too:"
            for i in check_list:
                comment += dd.get_disti_by_id(i)[:3] + ":" + dd.get_date_by_id(i) + ";"
            dd.add_comment(dreg_id, comment)
            return

        # someone has pending: manual decision
        check_list = dd.id_list_status_pending(dreg_id_with_same_part_and_customers)
        if check_list:
            dd.ask_for_manual_decision(dreg_id)
            self.count_question += 1
            comment = "Pending: "
            for i in check_list:
                comment += dd.get_disti_by_id(i)[:3] + ":" + dd.get_date_by_id(i) + ";"
            dd.add_comment(dreg_id, comment)
            return

        # Other disti has no open registration but business win: reject
        check_list = dd.id_list_exclude_distributor(disti, dreg_id_with_same_part_and_customers)
        check_list = dd.id_list_proj_stage_bw(check_list)
        if check_list:
            dd.reject(dreg_id)
            self.count_rejected += 1
            dd.set_rejection_reason_already_registered(dreg_id)
            comment = "BW with other disti:"+dd.get_disti_by_id(check_list[0])[:3]+"-"+str(check_list[0])+":" \
                      + dd.get_date_by_id(dreg_id)
            dd.add_comment(dreg_id, comment)
            return

        # Approve if nothing from above
        dd.approve(dreg_id)
        self.count_approved += 1
