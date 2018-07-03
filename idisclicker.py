from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
import threading
import time
import pandas as pd
from XP import XP
from XP import Loc


def thread_sleep(time_sec):
    e = threading.Event()
    e.wait(timeout=time_sec)


class Do(object):
    CLICK = "click"
    CLEAR = "clear"
    SEND_KEYS = "send_keys"


class IdisClicker:
    page_reload_timeout_sec = 1

    def __init__(self, is_threading=False, browser="firefox"):
        self.is_threading = is_threading
        self.browser_type = browser
        self.page_reload_timeout_sec = 5

        return

    def start_browser(self):
        self.open_idis_in_browser(browser_type=self.browser_type)
        self.select_WorkAreaFrame1()
        self.click_SalesCenter_DesignRegistrations()

    def shutdown_browser(self):
        self.driver.stop_client()
        self.driver.close()

    def sleep(self, time_sec):
        if self.is_threading:
            thread_sleep(time_sec)
        else:
            time.sleep(1)

    def execute_command(self, locator: Loc, timeout_sec=10, **kwargs):
        pass

    def do(self, what: str, how: By, path: str, key_send_str='', timeout_sec=30):

        element = None

        for i in range(timeout_sec):
            element = self.get_element(how, path)
            if element is not None:
                print('Element found!')
                break
            else:
                self.sleep(1)
                print('Waiting:', i)

        if element is None:
            print("Timeout")
            return False

        try:
            action = getattr(element, what)
        except AttributeError:
            print("Wrong Action with element: ", what)
            return False

        for i in range(timeout_sec):
            try:
                if what == Do.SEND_KEYS:
                    action(key_send_str)
                else:
                    action()
                return True
            except ElementNotInteractableException:
                self.sleep(1)

        print("Do action failed")
        return False

    def get_element_value(self, how: By, path: str, timeout_sec=30):

        element = None

        for i in range(timeout_sec):
            element = self.get_element(how, path)
            if element is not None:
                print('Element found!')
                break
            else:
                self.sleep(1)
                print('Waiting:', i)

        if element is not None:
            return element.get_attribute('value')
        else:
            return 'Element not found!'

    def open_idis_in_browser(self, browser_type='firefox'):

        if browser_type == 'firefox':
            try:
                profile = webdriver.FirefoxProfile(
                    r'C:\Users\basov\AppData\Roaming\Mozilla\Firefox\Profiles\6ti8l5bx.default')
                self.driver = webdriver.Firefox(firefox_profile=profile,
                                                executable_path=r'C:\Firefox\geckodriver.exe')

                self.driver.get("https://portal.intra.infineon.com/irj/portal")

                # time.sleep(1)

                self.wait_element(By.ID, "logonuidfield", timeout_sec=30)

                self.driver.find_element_by_id("logonuidfield").clear()
                self.driver.find_element_by_id("logonuidfield").send_keys("basov")
                self.driver.find_element_by_id("logonpassfield").clear()
                self.driver.find_element_by_id("logonpassfield").send_keys("Planet%Mars%Flight")
                self.driver.find_element_by_name("uidPasswordLogon").click()

                self.wait_element(By.ID, "urFrames", timeout_sec=30)

                self.driver.get(
                    "https://sappc1lb.eu.infineon.com:8410/sap(bD1lbiZjPTEwMCZkPW1pbg==)/bc/bsp/sap/crm_ui_start/default.htm")

            except Exception as e:
                print(e)
                print("Fail in Opening IDIS with Firefox")

        elif browser_type == 'chrome':
            try:
                self.driver = webdriver.Chrome(executable_path=r'C:\Users\basov\Downloads\chromedriver.exe')
                self.driver.get("https://portal.intra.infineon.com/irj/portal")
                self.wait_element(By.ID, "urFrames", timeout_sec=30)
                self.driver.get(
                    "https://sappc1lb.eu.infineon.com:8410/sap(bD1lbiZjPTEwMCZkPW1pbg==)/bc/bsp/sap/crm_ui_start/default.htm")

            except Exception as e:
                print(e)
                print("Fail in Opening IDIS with Chrome")

    def goto_design_registration_search_page(self):
        return

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_element_ready(self, how, what):

        if self.is_element_present(how, what):
            if self.driver.find_element(by=how, value=what).is_enabled():
                return True

        return False

    def get_element(self, how, what):
        try:
            element = self.driver.find_element(by=how, value=what)
            return element
        except NoSuchElementException as e:
            return None

    def wait_element(self, how: str, what: str, timeout_sec=30):

        for i in range(timeout_sec):
            if self.is_element_ready(how, what):
                print('Element found!')
                return True
            else:
                self.sleep(1)
                print('Waiting:', i)

        print("Timeout")
        return False

    def select_WorkAreaFrame1(self):

        self.sleep(3)

        try:

            id = 'CRMApplicationFrame'
            self.wait_element(By.ID, id)
            frame = self.driver.find_element_by_id(id)
            self.driver.switch_to.frame(frame)

            id = 'WorkAreaFrame1'
            self.wait_element(By.ID, id)
            frame = self.driver.find_element_by_id(id)
            self.driver.switch_to.frame(frame)

            return True

        except NoSuchElementException:
            print("Can't set Frame")
            return False

    def click_SalesCenter_DesignRegistrations(self):

        self.do(Do.CLICK, By.XPATH, XP.PageHome.but_Sales_Center)

        self.do(Do.CLICK, By.XPATH, XP.PageHome.but_Design_Registration)

        return

    def wait_and_click_element_by_xpath(self, xpath):

        self.wait_element(By.XPATH, xpath)

        for i in range(10):
            try:
                self.driver.find_element_by_xpath(xpath).click()
                return True
            except ElementNotInteractableException:
                self.sleep(1)

        return False

    def wait_and_click_element_by_id(self, id):

        self.wait_element(By.ID, id)

        for i in range(10):
            try:
                self.driver.find_element_by_id(id).click()
                return True
            except ElementNotInteractableException:
                self.sleep(1)

        return False



    def wait_and_clear_element_by_xpath(self, xpath):

        self.wait_element(By.XPATH, xpath)
        self.driver.find_element_by_xpath(xpath).clear()

        return

    def wait_and_sendkeys_element_by_xpath(self, xpath, keys):

        self.wait_element(By.XPATH, xpath)
        self.driver.find_element_by_xpath(xpath).send_keys(keys)

        return

    def open_dreg_page_by_registration_id(self, dreg_id):

        self.do(Do.CLICK, By.XPATH, XP.PageSearchDesignRegistrations.ddmenu_Line1_ChooseSearchField)

        self.do(Do.CLICK, By.XPATH, XP.PageSearchDesignRegistrations.ddmenu_Line1_Choose_Value_RegistrationID)

        self.sleep(self.page_reload_timeout_sec)

        self.do(Do.CLEAR, By.XPATH, XP.PageSearchDesignRegistrations.textinput_Line1)

        self.do(Do.SEND_KEYS, By.XPATH, XP.PageSearchDesignRegistrations.textinput_Line1, key_send_str=dreg_id)

        self.do(Do.CLICK, By.XPATH, XP.PageSearchDesignRegistrations.but_Search)

        self.sleep(self.page_reload_timeout_sec)

        if self.do(Do.CLICK, By.LINK_TEXT, dreg_id):
            print("DREG ID=", dreg_id, " found!")
            return True

        print("DREG ID=", dreg_id, " NOT found!")

        return False

    def click_edit_dreg_button(self):
        return self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.but_Edit)

    def select_Approved_in_dropdown_menu(self):

        val = self.get_element_value(By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Status_Read)

        if val != 'New':
            print("DREG is NOT in New Status! Process Manually!")
            return False

        self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Status)

        return self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Status_Item_Approved)

    def select_Rejected_in_dropdown_menu(self):

        val = self.get_element_value(By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Status_Read)

        if val != 'New':
            print("DREG is NOT in New Status! Process Manually!")
            return False

        self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Status)

        return self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Status_Item_Rejected)

    def select_Design_Registration_Category(self):

        v = self.get_element_value(By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Registration_Category)

        if v == 'Opportunity Tracking':
            return True

        if v == 'Demand Creation':
            return True

        if v == 'Element not found!':
            return False

        self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Registration_Category)

        return self.do(Do.CLICK, By.XPATH,
                       XP.PageInsideDesignRegistration.ddmenu_Registration_Category_Is_Demand_Creation)

    def click_Save_and_Back(self):

        if not self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.but_Save):
            return False

        time.sleep(self.page_reload_timeout_sec * 3)

        return self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.but_Back)

    def try_to_close_current_dreg_page(self):
        return self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.but_Back, timeout_sec=3)

    def select_Rejection_Reason(self):

        if self.do(Do.CLICK, By.XPATH, XP.PageInsideDesignRegistration.ddmenu_Rejection_Reason):
            return self.do(Do.CLICK, By.XPATH,
                           XP.PageInsideDesignRegistration.ddmenu_Rejection_Reason_Is_Already_Registered)
        else:
            return False

    def change_DREG_status_by_id(self, dreg_id, new_status, reason=''):

        if new_status == 'approve':
            self.approve_DREG_by_id(dreg_id)
        elif new_status == 'reject':
            self.reject_DREG_by_id(dreg_id)
        else:
            print('Unknown new status DREG:', dreg_id)

    def approve_DREG_by_id(self, dreg_id):

        try:
            if not self.open_dreg_page_by_registration_id(dreg_id):
                print("DREG not found: ", dreg_id)
                return False

            if not self.click_edit_dreg_button():
                print("Cant start edit DREG: ", dreg_id)
                return False

            if not self.select_Approved_in_dropdown_menu():
                print("Cant choose Approved from menu DREG: ", dreg_id)
                return False

            self.sleep(self.page_reload_timeout_sec)

            if not self.select_Design_Registration_Category():
                print("Cant select Design Registration Category DREG: ", dreg_id)
                return False

            self.sleep(self.page_reload_timeout_sec * 2)

            if not self.click_Save_and_Back():
                print("Can't save and go back, close manually! DREG: ", dreg_id)
                return False
        except Exception as e:
            print("Exception in approve_DREG_by_id:", e)
            return False

        return True

    def reject_DREG_by_id(self, dreg_id):

        try:
            if not self.open_dreg_page_by_registration_id(dreg_id):
                print("DREG not found: ", dreg_id)
                return False

            if not self.click_edit_dreg_button():
                print("Cant start edit DREG: ", dreg_id)
                return False

            if not self.select_Rejected_in_dropdown_menu():
                print("Cant choose Approved from menu DREG: ", dreg_id)
                return False

            self.sleep(self.page_reload_timeout_sec)

            if not self.select_Rejection_Reason():
                print("Cant select Regection Reason DREG: ", dreg_id)
                return False

            self.sleep(self.page_reload_timeout_sec * 2)

            if not self.click_Save_and_Back():
                print("Can't save and go back, close manually! DREG: ", dreg_id)
                return False
        except Exception as e:
            print("Exception in reject_DREG_by_id:", e)
            return False

        return True


def main():
    ic = IdisClicker()

    # slow connection
    ic.page_reload_timeout_sec = 5

    ic.open_idis_in_browser(browser_type='firefox')

    ic.select_WorkAreaFrame1()

    ic.click_SalesCenter_DesignRegistrations()

    df_a = pd.read_excel("approved.xlsx")

    approved_dreg_ids = df_a['Approved'].values

    df_r = pd.read_excel("rejected.xlsx")

    rejected_dreg_ids = df_r['Rejected'].values

    print("Start Approvals!")
    for dreg_id in approved_dreg_ids:

        # try 3 times if failed
        res = False
        for attempt in range(3):
            if ic.approve_DREG_by_id(str(dreg_id)):
                res = True
                break

        if res:
            print(dreg_id, " :Success!")
        else:
            print(dreg_id, " :Fail!")

    print("Start Rejects!")
    for dreg_id in rejected_dreg_ids:

        # try 3 times if failed
        res = False
        for attempt in range(3):
            if ic.reject_DREG_by_id(str(dreg_id)):
                res = True
                break

        if res:
            print(dreg_id, " :Success!")
        else:
            print(dreg_id, " :Fail!")

    return


if __name__ == "__main__":
    main()
