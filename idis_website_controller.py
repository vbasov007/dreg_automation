from execute_selenium import WebClicker, ClickerException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from mylogger import mylog

class IdisWebControllerException(Exception):
    pass

class IdisWebController:

    def __init__(self, portal_url, idis_url, login, password, browser, browser_binary, profile_path, driver_exe_path):

        mylog.debug("Start IdisWebController")

        self.portal_url = portal_url
        self.idis_url = idis_url
        self.login = login
        self.password = password
        self.browser = browser
        self.browser_binary = browser_binary
        self.profile_path = profile_path
        self.driver_exe_path = driver_exe_path

        self.first_run = True

        self.wc = WebClicker(self.driver_exe_path, browser=self.browser, profile_path=self.profile_path,
                             browser_binary=self.browser_binary)

    def update_dreg(self, dreg_id, status, reason, approver, category):

        mylog.info("Updating dreg id = {0}".format(dreg_id))
        mylog.info("New status='{0}'; Reason='{1}'; Approver='{2}'; Category='{3}'".format(status, reason,
                                                                                             approver, category))

        try:
            if self.first_run:
                self._open_portal_in_new_window()
                self._open_idis()
                self._open_dreg_search()
                self.first_run = False

            self._open_dreg(dreg_id)

            self._activate_dreg_edit()

            dreg_blocked_message = self._read_dreg_blocked_by_other_user()
            if dreg_blocked_message:
                mylog.info("{0}".format(dreg_blocked_message))
                self._click_backbutton()
                return False

            self._edit_open_dreg(status, reason, approver, category)

            self._save_dreg()

            self._click_backbutton()
        except (IdisWebControllerException, WebDriverException) as e:
            self._click_backbutton()
            mylog.exception(e)
            self.shutdown_browser()
            return False

        return True

    def shutdown_browser(self):
        mylog.debug("Browser shutdown")
        self.first_run = True
        self.wc.shutdown()

    def _open_portal_in_new_window(self):
        """
        start url=https://portal.intra.infineon.com/irj/portal
        wait id=logonuidfield
        click id=logonuidfield
        sendkeys id=logonuidfield string=basov
        click id=logonuidfield
        sendkeys id=logonpassfield string=Planet%Mars%Flight -enter
        wait xpath="//*[contains(text(),'PC1 CRM Web Client')]" time=10


        :return: True if success, else False
        """

        mylog.debug("Opening portal in new window and entering login/password...")
        success = self.wc.get_website(self.portal_url)
        if not success:
            raise IdisWebControllerException("Can't open portal '{0}'".format(self.portal_url))
        self.wc.wait_element('id', 'logonuidfield', time_sec=10)
        self.wc.click('id', 'logonuidfield')
        self.wc.send_string('id', 'logonuidfield', string=self.login)
        self.wc.click('id', 'logonpassfield')
        self.wc.send_string('id', 'logonpassfield', string=self.password, end=Keys.RETURN)

        success = self.wc.wait_element('xpath', r"//*[contains(text(),'PC1 CRM Web Client')]", time_sec=20)

        if not success:
            raise IdisWebControllerException("Can't see 'PC1 CRM Web Client' link on the resulting page")


    def _open_idis(self):
        """
        get url="https://sappc1lb.eu.infineon.com:8410/sap(bD1lbiZjPTEwMCZkPW1pbg==)/bc/bsp/sap/crm_ui_start/default.htm"

        :return: True if success, else False
        """
        mylog.debug("Open IDIS website url ='{0}'".format(self.idis_url))
        self.wc.get_website(self.idis_url)

        success = self.wc.wait_element('xpath', r"//*[contains(text(),'Home - [SAP]')]", time_sec=10)

        if not success:
            raise IdisWebControllerException("Can't see 'Home - [SAP]' link on the resulting page.")


    def _open_dreg_search(self):
        """
        switch_to_frame index=0
        switch_to_frame index=1
        click xpath="//*[contains(text(),'Sales Center')]"
        switch_to_frame index=0
        switch_to_frame index=1
        wait id="C19_W49_V50_HT-DR-SR"
        click id="C19_W49_V50_HT-DR-SR"
        :return: True if success, else False
        """

        mylog.debug("Open DREG search page...")
        self.wc.wait(10)
        self.wc.switch_to_frame_by_index(0)
        self.wc.switch_to_frame_by_index(1)
        self.wc.wait_element('xpath', r"//*[contains(text(),'Sales Center')]", time_sec=5)
        self.wc.click('xpath', r"//*[contains(text(),'Sales Center')]", time_sec=5)
        self.wc.wait_element('id', r"C19_W49_V50_HT-DR-SR", time_sec=5)
        self.wc.click('id', r"C19_W49_V50_HT-DR-SR", time_sec=5)

        success = self.wc.wait_element('xpath', r"//*[contains(text(),'Search: Design Registrations - [SAP]')]",
                                       time_sec=5)

        if not success:
            raise IdisWebControllerException("Can't see 'Search: Design Registrations - [SAP]' "
                                             "link on the resulting page.")


    def _open_dreg(self, dreg_id):
        """
        # change first line in the form to "Design Registration ID"
        wait id="C22_W66_V67_V68_btqopp_parameters[1].FIELD" time=5
        click id="C22_W66_V67_V68_btqopp_parameters[1].FIELD"
        wait link_text='Design Registration ID' time=5
        click link_text='Design Registration ID'
        wait time=3
        # type DREG ID and "enter" instead of search button
        sendkeys id=C22_W66_V67_V68_btqopp_parameters[1].VALUE1 string=20279935 -enter
        # wait search results and click on DREG ID
        wait link_text=20279935
        click link_text=20279935
        :param dreg_id:
        :return:
        """
        mylog.debug("Open design registration id = {0} details page...".format(dreg_id))
        self.wc.wait_element('id', r"C22_W66_V67_V68_btqopp_parameters[1].FIELD", time_sec=5)
        self.wc.click('id', r"C22_W66_V67_V68_btqopp_parameters[1].FIELD")
        self.wc.wait_element('link_text', r'Design Registration ID')
        self.wc.click('link_text', r'Design Registration ID')
        self.wc.wait(time_sec=2)
        self.wc.clear('id', r"C22_W66_V67_V68_btqopp_parameters[1].VALUE1")
        self.wc.send_string('id', r"C22_W66_V67_V68_btqopp_parameters[1].VALUE1", string=str(dreg_id), end=Keys.RETURN)
        self.wc.wait_element('link_text', str(dreg_id), time_sec=10)
        self.wc.click('link_text', str(dreg_id))

        success = self.wc.wait_element('xpath', r"//*[contains(text(),'Design Registration Details')]", time_sec=10)

        if not success:
            raise IdisWebControllerException("Can't see 'Design Registration Details' on the page")

    def _read_dreg_blocked_by_other_user(self):
        """
        find_elements xpath="//*[contains(text(),'is being processed')]"
        :return:
        """
        message = None

        element = self.wc.find_element('xpath', r"//*[contains(text(),'is being processed')]")
        if element:
            message = element.get_attribute('title')

        return message


    def _edit_open_dreg(self, status, reason, approver, category):

        mylog.debug("Start edit current dreg")

        self._edit_registration_status(status)
        if status == 'Rejected':
            self._edit_rejection_reason(reason)
        self._edit_dreg_approver(approver)
        self._edit_dreg_category(category)

    def _activate_dreg_edit(self):
        """
        click xpath="//img[@title='Edit Page']"
        wait time=5
        :return:
        """
        mylog.debug("Press Edit button")
        self.wc.click('xpath', r"//img[@title='Edit Page']")
        self.wc.wait(time_sec=5)


    def _edit_registration_status(self, status):
        """
        click id='C24_W74_V76_V80_btstatus_struct.act_status-btn'
        wait link_text=Approved time=5
        click link_text=Approved
        :param status:
        :return:
        """
        mylog.debug("Edit registration status")

        if(not self.wc.drop_down('id', r"C24_W74_V76_V80_btstatus_struct.act_status-btn", status,
                                 time_sec=5, repeat_if_fail=3)):
            raise IdisWebControllerException("Can't change on '{0}' in Registration Status".format(status))


    def _edit_rejection_reason(self, reason):
        """
        click id='C24_W74_V76_V80_btsubject_struct.conc_key-btn'
        click link_text="Already registered to another disti"
        :param status:
        :return:
        """
        mylog.debug("Edit rejection reason")

        if (not self.wc.drop_down('id', r'C24_W74_V76_V80_btsubject_struct.conc_key-btn', reason,
                                  time_sec=5, repeat_if_fail=3)):
            raise IdisWebControllerException("Can't change on '{0}' in Rejection Reason".format(reason))

    def _edit_dreg_approver(self, approver):
        """
        clear id=C24_W74_V76_V80_btparterapprover_struct.partner_no
        sendkeys id=C24_W74_V76_V80_btparterapprover_struct.partner_no string='Vasily Basov' -enter
        :param approver:
        :return:
        """
        mylog.debug("Edit DREG approver: '{0}'".format(approver))
        self.wc.clear('id', r"C24_W74_V76_V80_btparterapprover_struct.partner_no")
        self.wc.send_string('id', r"C24_W74_V76_V80_btparterapprover_struct.partner_no", string=approver, end=Keys.RETURN)
        self.wc.wait(1)
        check = self.wc.get_attribute('id', r"C24_W74_V76_V80_btparterapprover_struct.partner_no",attribute_name='value')

        if not check == approver:
            raise IdisWebControllerException("Read approver fail!")

    def _edit_dreg_category(self, category):
        """
        click id=C24_W74_V76_V80_btcustomerh_ext.zzqp_dmnd_flg
        click link_text="Opportunity Tracking"
        :param category:
        :return:
        """
        mylog.debug("Edit dreg category: '{0}'".format(category))

        if (not self.wc.drop_down('id', r"C24_W74_V76_V80_btcustomerh_ext.zzqp_dmnd_flg", category,
                                  time_sec=5, repeat_if_fail=3)):
            raise IdisWebControllerException("Can't change on '{0}' in Category".format(category))

    def _click_backbutton(self):
        mylog.debug("Click Back")
        self.wc.click('id', 'BackButton')
        self.wc.wait(time_sec=10)

    def _save_dreg(self):
        """
        send_ctrl_key tag=body key=s
        wait 10 sec
        click id=BackButton
        :return:
        """

        mylog.debug("Pressing save button...")
        self.wc.click('xpath', '//*[@title="Save (Ctrl+S)" and @alt="Save"]', time_sec=10)
        self.wc.wait(time_sec=10)

