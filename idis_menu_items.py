
class RegistrationStatus(object):
    New = 'New'
    Pending = 'Pending'
    Approved = 'Approved'
    Rejected = 'Rejected'
    Closed = 'Closed'


class DesignRegistrationCategory(object):
    Demand_Fulfilment = 'Demand Fulfillment'
    Demand_Creation = 'Demand Creation'
    Opportunity_Tracking = 'Opportunity Tracking'


class ReasonForRejection(object):

    Already_registered_to_another_disti = 'Already registered to another disti'
    Direct_account = 'Direct account'
    Duplicate_Registration = 'Duplicate Registration'
    Additional_Project_Details_Required = 'Additional Project Details Required'
    Incorrect_Assignment = 'Incorrect Assignment'
    Design_registered_on_subcontractor = 'Design registered on subcontractor'
    No_Activity = 'No Activity'
    Replaced_by_new_design = 'Replaced by new design'
    Running_Business = 'Running Business'
    Others = 'Others'
    Design_Loss = 'Design Loss'
    Does_not_meet_minimum_requirement = 'Does not meet minimum requirement'
    Replaced_with_different_IFX_part = 'Replaced with different IFX part'
    Open_for_all = 'Open for all'
