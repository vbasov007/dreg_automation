from dregdata import DregData
from dregdata import Status

class DregSolver:

    def __init__(self):

        self.count_processed_lines = 0
        self.count_approved = 0
        self.count_rejected = 0
        self.count_question = 0
        self.count_conflicts = 0


    def get_statistics(self):
        return {
            "Processed lines": self.count_processed_lines,
            "Approved": self.count_approved,
            "Rejected": self.count_rejected,
            "Manual decision": self.count_question,
        }

    def process_dregs_id_list(self, dd: DregData, dreg_id_list):

        print("Processing {0} lines...".format(len(dreg_id_list)))
        self.count_processed_lines = 0

        for dreg_id in dreg_id_list:
            print("Line {0}: DREG ID: {1}".format(self.count_processed_lines, str(dreg_id)), end='\r')
            self.process_dreg_by_id1(dd, dreg_id)
            self.count_processed_lines += 1

        print("Done!                                                                      ")
        return

    def process_all_new(self, dd: DregData):

        dreg_id_status_new = dd.id_list_status_new()
        dreg_id_status_pending = dd.id_list_status_pending()

        print("{0} NEW design registrations".format(len(dreg_id_status_new)))
        print("{0} PENDING design registrations".format(len(dreg_id_status_pending)))

        self.process_dregs_id_list(dd, dreg_id_status_new+dreg_id_status_pending)

        return

    def process_duplication_check(self, dd: DregData):

        id_list = dd.id_list_by_status(Status.APPROVED)
        print("Duplication check {0} lines".format(len(id_list)))
        for i, dreg_id in enumerate(id_list):
            if len(dd.get_core_customer_by_id(dreg_id)) > 1:
                self.process_dreg_by_id1(dd, dreg_id)
            print("{0} {1}".format(i, dreg_id), end='\r')

        print("Duplication check done!")

    def process_dreg_by_id(self, dd: DregData, dreg_id):

        dreg_status = dd.get_status_by_id(dreg_id)
        core_part = dd.get_core_part_num_by_id(dreg_id)
        orig_part = dd.get_orig_part_num_by_id(dreg_id)

        customer = dd.get_core_customer_by_id(dreg_id)
        disti = dd.get_disti_by_id(dreg_id)
        # subcon = dd.get_subcon_by_id(dreg_id)

        dreg_id_all_exclude_current = dd.id_list_all
        dreg_id_all_exclude_current.remove(dreg_id)

        # customer is in sub-contructor list: warning
        if dd.is_customer_in_subcon_list(customer):
            dd.add_comment(dreg_id, "Customer is in subcon list")

        # different dreg id but the same core_part and customer
        lst = dd.id_list_by_core_part(core_part, dreg_id_all_exclude_current)
        dreg_id_with_same_core_part_and_customers = dd.id_list_by_core_cust(customer, lst)

        # different dreg_id but the same original part (needed for duplication reject)
        lst = dd.id_list_by_orig_part(orig_part, dreg_id_all_exclude_current)
        dreg_id_with_same_orig_part_and_customers = dd.id_list_by_core_cust(customer, lst)

        # Valid approved registration for other disti: reject
        check_list = dd.id_list_exclude_distributor(disti, dreg_id_with_same_core_part_and_customers)
        check_list = dd.id_list_status_approved(check_list)
        if check_list:
            if dreg_status == Status.NEW:
                dd.reject(dreg_id)
                self.count_rejected += 1
                dd.set_rejection_reason_already_registered(dreg_id)
                comment = "Registered: {0}-{1}:{2}".format(dd.get_disti_by_id(check_list[0])[:3],
                                                           check_list[0],
                                                           dd.get_date_by_id(dreg_id))
                dd.add_comment(dreg_id, comment)
            elif dreg_status == Status.APPROVED:
                self.count_conflicts += 1
                comment = "Conflict: {0}, {1}".format(dreg_id, ", ".join(check_list))
                dd.add_comment(dreg_id, comment)
                dd.mark_dreg_conflict(dreg_id)

                for d_id in check_list:
                    if not dd.is_marked_conflict(d_id):
                        dd.mark_dreg_conflict(d_id)
                        dd.add_comment(dreg_id, comment)

            return

        # Duplicated registration for the same disti: reject
        check_list = dd.id_list_by_distributor(disti, dreg_id_with_same_orig_part_and_customers)
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
        check_list = dd.id_list_exclude_distributor(disti, dreg_id_with_same_core_part_and_customers)
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
        check_list = dd.id_list_status_pending(dreg_id_with_same_core_part_and_customers)
        if check_list:
            dd.ask_for_manual_decision(dreg_id)
            self.count_question += 1
            comment = "Pending: "
            for i in check_list:
                comment += dd.get_disti_by_id(i)[:3] + ":" + dd.get_date_by_id(i) + ";"
            dd.add_comment(dreg_id, comment)
            return

        # Other disti has no open registration but business win: reject
        check_list = dd.id_list_exclude_distributor(disti, dreg_id_with_same_core_part_and_customers)
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
        if core_part != '':
            li = dd.customers_which_use_the_part(core_part, dd.id_list_status_approved(dreg_id_all_exclude_current))
            comment = ", ".join(li)
            dd.add_comment(dreg_id, comment)
        if dreg_status == Status.NEW:
            dd.approve(dreg_id)
            self.count_approved += 1
        elif dreg_status == Status.APPROVED:
            dd.mark_conflict_check_ok(dreg_id)
        return

    def if_new_reject_if_approved_conflict(self, dreg_id_list: list, dreg_status, comment, dd: DregData):

        if dreg_status == Status.NEW:
            dd.add_comment(dreg_id_list[0], comment)
            dd.reject(dreg_id_list[0])
            dd.set_rejection_reason_already_registered(dreg_id_list[0])
        elif dreg_status == Status.APPROVED:
            for dreg_id in dreg_id_list:
                if not dd.is_marked_conflict(dreg_id):
                    dd.mark_dreg_conflict(dreg_id)
                    dd.add_comment(dreg_id, comment)

        return

    def get_intersection_in_cust_and_subcon(self, customer, subcon, exclude_disti, dd: DregData, lookup_id_list=None):

        output = set(dd.id_list_filter(core_cust=customer,
                                       exclude_disti=exclude_disti,
                                       lookup_id_list=lookup_id_list))
        output.update(dd.id_list_filter(core_subcon=customer,
                                        exclude_disti=exclude_disti,
                                        lookup_id_list=lookup_id_list))
        if len(subcon) > 0:
            output.update(dd.id_list_filter(core_cust=subcon,
                                            exclude_disti=exclude_disti,
                                            lookup_id_list=lookup_id_list))
            output.update(dd.id_list_filter(core_subcon=subcon,
                                            exclude_disti=exclude_disti,
                                            lookup_id_list=lookup_id_list))
        return list(output)

    def format_comment(self, say, dreg_id_list, dd: DregData):
        def is_not_approved(st):
            if not st == Status.APPROVED:
                return ' '+st
            else:
                return ''

        if len(dreg_id_list) > 0:
            output = say+' '
            for dreg_id in dreg_id_list:
                output += '{0}-{1}:{2}{3}; '.format(dd.get_disti_by_id(dreg_id)[:3],
                                                    dreg_id,
                                                    dd.get_date_by_id(dreg_id),
                                                    is_not_approved(dd.get_status_by_id(dreg_id)))

        return output

    def process_dreg_by_id1(self, dd: DregData, dreg_id):

        dreg_status = dd.get_status_by_id(dreg_id)
        core_part = dd.get_core_part_num_by_id(dreg_id)
        orig_part = dd.get_orig_part_num_by_id(dreg_id)

        if not dd.is_part_in_pricelist(orig_part):
            dd.add_comment(dreg_id, "{0} not found;".format(orig_part))

        customer = dd.get_core_customer_by_id(dreg_id)
        disti = dd.get_disti_by_id(dreg_id)
        subcon = dd.get_subcon_by_id(dreg_id)

        base_list = dd.id_list_filter(core_part=core_part,
                                      status=Status.APPROVED,
                                      exclude_dreg_id=dreg_id)

        # Case 1&2: same customer, same part, different disti
        same_cust_diff_disti = dd.id_list_filter(core_cust=customer,
                                                 exclude_disti=disti,
                                                 lookup_id_list=base_list)

        if not len(same_cust_diff_disti) == 0:
            comment = self.format_comment('Customer conflict:', [dreg_id] + same_cust_diff_disti, dd)
            self.if_new_reject_if_approved_conflict([dreg_id] + same_cust_diff_disti,
                                                    dreg_status,
                                                    comment,
                                                    dd)
            return

        # check subcontructor intersection
        subcon_conflict_dreg_id_list = self.get_intersection_in_cust_and_subcon(customer, subcon, disti, dd, base_list)

        if not len(subcon_conflict_dreg_id_list) == 0:
            comment = self.format_comment('Subcon conflict:', [dreg_id] + subcon_conflict_dreg_id_list, dd)
            self.if_new_reject_if_approved_conflict([dreg_id] + subcon_conflict_dreg_id_list,
                                                    dreg_status,
                                                    comment,
                                                    dd)
            return

        # check BW in the same customer
        bw_with_same_part_list = dd.id_list_filter(core_part=core_part,
                                                   stage='BW')
        bw_list = self.get_intersection_in_cust_and_subcon(customer, subcon, disti, dd, bw_with_same_part_list)
        if not len(bw_list) == 0:
            comment = self.format_comment('BW conflict: ', [dreg_id]+bw_list, dd)
            self.if_new_reject_if_approved_conflict([dreg_id] + bw_list,
                                                    dreg_status,
                                                    comment,
                                                    dd)
            return

        # check if more than one "New" -> Manual decision
        if dreg_status == Status.NEW:
            status_new_list = dd.id_list_filter(core_part=core_part,
                                                core_cust=customer,
                                                status=Status.NEW,
                                                exclude_disti=disti,
                                                exclude_dreg_id=dreg_id)
            if not len(status_new_list) == 0:
                comment = self.format_comment('NEW from other disti too: ', [dreg_id] + status_new_list, dd)
                dd.ask_for_manual_decision(dreg_id)
                dd.add_comment(dreg_id, comment)

                return

        # Approve if nothing from above
        li = dd.customers_which_use_the_part(core_part, base_list, except_customer=customer)
        if li:
            comment = "Same part in: {0};".format(", ".join(li))
            dd.add_comment(dreg_id, comment)

        if dreg_status == Status.NEW:
            dd.approve(dreg_id)
        elif dreg_status == Status.APPROVED:
            dd.mark_conflict_check_ok(dreg_id)
        return
