
class XP(object):

    class PageHome:
        header = '''Home'''
        but_Sales_Center = '''//ul[@id='C4_W16_V17_mainmenu']/li[6]/div'''
        but_Design_Registration = '''//ul[@id='C4_W16_V17_mainmenu']/li[6]/ul/li/a'''

    class PageSearchDesignRegistrations:

        ddmenu_Line1_ChooseSearchField = '''//a[@id='C19_W60_V61_V62_btqopp_parameters[1].FIELD-btn']/img'''
        ddmenu_Line1_Choose_Value_RegistrationID = '''//div[@id='C19_W60_V61_V62_btqopp_parameters[1].FIELD__items']/ul/li[16]/a'''
        textinput_Line1 = '''//div[@id='C19_W60_V61_V62_btqopp_parameters[1].OPERATORsf1']/span/input'''
        but_Search = '''//*[@id="C19_W60_V61_SearchBtn"]/span/b'''

    class PageInsideDesignRegistration:
        ddmenu_Status = '''//table[@id='C21_W68_V70_V74_chtmlb_configGrid_40']/tbody/tr/td/table/tbody/tr[17]/td[2]/div/div/div[2]/table/tbody/tr/td[2]/a'''
        ddmenu_Status_Item_Approved = '''//div[@id='C21_W68_V70_V74_btstatus_struct.act_status__items']/ul/li[3]'''
        ddmenu_Status_Item_Rejected = '''//div[@id='C21_W68_V70_V74_btstatus_struct.act_status__items']/ul/li[4]'''
        ddmenu_Rejection_Reason = '''//a[@id='C21_W68_V70_V74_btsubject_struct.conc_key-btn']/img'''
        ddmenu_Rejection_Reason_Is_Already_Registered = '''//div[@id='C21_W68_V70_V74_btsubject_struct.conc_key__items']/ul/li[2]'''
        ddmenu_Registration_Category = '''//table[@id='C21_W68_V70_V74_chtmlb_configGrid_40']/tbody/tr/td/table/tbody/tr[4]/td[2]/div/div/div[2]/table/tbody/tr/td/fieldset/input'''
        ddmenu_Registration_Category_Is_Demand_Creation = '''//div[@id='C21_W68_V70_V74_btcustomerh_ext.zzqp_dmnd_flg__items']/ul/li[3]'''
        but_Edit = '''//a[@id='C21_W68_V70_V74_but1']/img'''
        but_Save = '''//a[@id='C21_W68_V70_thtmlb_button_1']/span/b'''
        but_Back = '''//a[@id='BackButton']/span'''
        ddmenu_Status_Read = '''//table[@id='C21_W68_V70_V74_chtmlb_configGrid_40']/tbody/tr/td/table/tbody/tr[17]/td[2]/div/div/div[2]/table/tbody/tr/td/fieldset/input'''

class ST(object):

    APPROVED = '''Approved'''
    REJECTED = '''Rejected'''
    CLOSED = '''Closed'''
    PENDING = '''Pending'''
    NEW = '''New'''

class RN(object):
    REGISTERED_FOR_OTHER = '''Registered for other distributor'''
    OPEN_FOR_ALL = '''Open for All'''