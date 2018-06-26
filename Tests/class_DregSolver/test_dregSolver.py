from unittest import TestCase

import corecustomername as ccm

import os
import pandas as pd

from dregsolver import DregSolver
from dregdata import DregData
from dregdata import Action
from dregdata import Reason


class TestDregSolver(TestCase):
    def test_process_dreg_by_id1(self):

        synonyms_df = pd.read_excel(os.path.join("Tests", "class_DregSolver", "Data", "synonyms.xlsx"))
        dreg_df = pd.read_excel(os.path.join("Tests", "class_DregSolver", "Data", "exportdreg.xlsx"))

        core_part_name_df = pd.read_excel(os.path.join("Tests", "class_DregSolver", "Data", "coreproduct.xlsx"))
        core_part_name_df = core_part_name_df[['Type', 'Core Product']]
        core_part_name_dict = core_part_name_df.set_index('Type')['Core Product'].to_dict()

        synonyms_dict = ccm.get_dict(synonyms_df)

        dd = DregData(dreg_df, synonyms_dict, core_part_name_dict)

        solver = DregSolver()

        # Case 1: reject new if already exist for other disti
        dreg_id = '20412507'
        solver.process_dreg_by_id(dd, dreg_id)
        res = dd.get_action_value(dreg_id)
        reason = dd.get_reason_value(dreg_id)
        self.assertEqual(res, Action.REJECT, "New reg, Same part, same customer, diff disti => Reject")
        self.assertEqual(reason, Reason.ALREADY_REGISTERED_BY_OTHER)

        # Case 2: conflict of existing registrations
        dreg_id = '20246272'
        solver.process_dreg_by_id(dd, dreg_id)
        res = dd.get_action_value(dreg_id)
        self.assertEqual(res, Action.CONFLICT, "Approved regs, Same part, same customer, diff disti => Conflict")
        res = dd.get_action_value('20340467')
        self.assertEqual(res, Action.CONFLICT, "Approved regs, Same part, same customer, diff disti => Conflict")

        # Case 3: conflict in subcontructors
        dreg_id = '20244170'
        solver.process_dreg_by_id(dd, dreg_id)
        res = dd.get_action_value(dreg_id)
        self.assertEqual(res, Action.CONFLICT, "Same Subcon 1  => Conflict")
        res = dd.get_action_value('20259923')
        self.assertEqual(res, Action.CONFLICT, "Same subcon 2 => Conflict")

        # Case 4: conflict with BW
        dreg_id = '20208347'
        solver.process_dreg_by_id(dd, dreg_id)
        res = dd.get_action_value(dreg_id)
        self.assertEqual(res, Action.CONFLICT, "Same Subcon 1  => Conflict")
        res = dd.get_action_value('20025746')
        self.assertEqual(res, Action.CONFLICT, "Same subcon 2 => Conflict")

        # Case 5: New from other customer too
        dreg_id = '20412524'
        solver.process_dreg_by_id(dd, dreg_id)
        res = dd.get_action_value(dreg_id)
        self.assertEqual(res, Action.MANUAL_DECISION, "New from other  => Manual Decision")

        dreg_id = '20412557'
        solver.process_dreg_by_id(dd, dreg_id)
        res = dd.get_action_value(dreg_id)
        self.assertEqual(res, Action.APPROVE, "Approve")

        dreg_id = '20081364'
        solver.process_dreg_by_id(dd, dreg_id)
        res = dd.get_action_value(dreg_id)
        self.assertEqual(res, Action.CHECK_OK, "Check Ok")

