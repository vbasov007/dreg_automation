from execute_selenium import WebClicker, ClickerException
from selenium.webdriver.common.keys import Keys


class IdisWebController:

    def __init__(self, portal_url, idis_url, login, password, browser, browser_binary, profile_path, driver_exe_path):

        self.portal_url = portal_url
        self.idis_url = idis_url
        self.login = login
        self.password = password
        self.browser = browser
        self.browser_binary = browser_binary
        self.profile_path = profile_path
        self.driver_exe_path = driver_exe_path

        self.wc = WebClicker(self.driver_exe_path, browser=self.browser, profile_path=self.profile_path,
                             browser_binary=self.browser_binary)

    def update_dreg(self, dreg_id, status, reason, approver, category):

        self._open_portal_in_new_window()
        self._open_idis()
        self._open_dreg_search()
        self._open_dreg(dreg_id)
        
        if self._is_dreg_blocked_by_other_user():
            print("#{0} blocked by other user. Can't edit".format(dreg_id))
            self._click_backbutton()
            return False

        self._edit_open_dreg(status, reason, approver, category)

        self._save_dreg()

        self._click_backbutton()

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
        self.wc.get_website(self.portal_url)
        self.wc.wait_element('id', 'logonuidfield', time_sec=10)
        self.wc.click('id', 'logonuidfield')
        self.wc.send_string('id', 'logonuidfield', string=self.login)
        self.wc.click('id', 'logonpassfield')
        self.wc.send_string('id', 'logonpassfield', string=self.password, end=Keys.RETURN)

        return self.wc.wait_element('xpath', r"//*[contains(text(),'PC1 CRM Web Client')]", time_sec=10)


    def _open_idis(self):
        """
        get url="https://sappc1lb.eu.infineon.com:8410/sap(bD1lbiZjPTEwMCZkPW1pbg==)/bc/bsp/sap/crm_ui_start/default.htm"

        :return: True if success, else False
        """
        self.wc.get_website(self.idis_url)
        return self._wait_idis_start_page(time_sec=10)


    def _wait_idis_start_page(self, time_sec=10):
        """
        find_element xpath="//*[contains(text(),'Home - [SAP]')]"
        :param time_sec:
        :return: True if success, else False
        """
        return bool(self.wc.wait_element('xpath', r"//*[contains(text(),'Home - [SAP]')]", time_sec=10))


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
        self.wc.switch_to_frame_by_index(0)
        self.wc.switch_to_frame_by_index(1)
        self.wc.wait_element('xpath', r"//*[contains(text(),'Sales Center')]", time_sec=5)
        self.wc.click('xpath', r"//*[contains(text(),'Sales Center')]")
        self.wc.switch_to_frame_by_index(0)
        self.wc.switch_to_frame_by_index(1)
        self.wc.wait_element('id', r"C19_W49_V50_HT-DR-SR", time_sec=5)
        self.wc.click('id', r"C19_W49_V50_HT-DR-SR")

        return self._wait_dreg_search_page()

    def _wait_dreg_search_page(self):
        """
        wait_element xpath="//*[contains(text(),'Search: Design Registrations - [SAP]')]" time=10
        :return:
        """
        return self.wc.wait_element('xpath', r"//*[contains(text(),'Search: Design Registrations - [SAP]')]", time_sec=5)

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
        self.wc.wait_element('id', r"C22_W66_V67_V68_btqopp_parameters[1].FIELD", time_sec=5)
        self.wc.click('id', r"C22_W66_V67_V68_btqopp_parameters[1].FIELD")
        self.wc.wait_element('link_text', r'Design Registration ID')
        self.wc.click('link_text', r'Design Registration ID')
        self.wc.wait(time_sec=2)
        self.wc.send_string('id', r"C22_W66_V67_V68_btqopp_parameters[1].VALUE1", string=str(dreg_id), end=Keys.RETURN)
        self.wc.wait_element('link_test', str(dreg_id), time_sec=10)
        self.wc.wait_element('link_test', str(dreg_id))

        return self._is_dreg_page()

    def _is_dreg_page(self):
        """
        find_element(xpath, //*[contains(text(),'Design Registration Details')])
        :return:
        """
        return bool(self.wc.wait_element('xpath', r"//*[contains(text(),'Design Registration Details')]", time_sec=10))

    def _is_dreg_blocked_by_other_user(self):
        """
        find_elements xpath="//*[contains(text(),'is being processed')]"
        :return:
        """
        return not bool(self.wc.find_element('xpath', r"//*[contains(text(),'is being processed')]"))

    def _edit_open_dreg(self, status, reason, approver, category):

        self._activate_dreg_edit()

        self._edit_registration_status(status)
        if status == 'Reject':
            self._edit_rejection_reason(reason)
        self._edit_dreg_approver(approver)
        self._edit_dreg_category(category)

    def _activate_dreg_edit(self):
        """
        click xpath="//img[@title='Edit Page']"
        wait time=5
        :return:
        """
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
        self.wc.click('id', r"C24_W74_V76_V80_btstatus_struct.act_status-btn")
        self.wc.wait_element('link_text', status, time_sec=3)
        self.wc.click('link_text', status)

    def _edit_rejection_reason(self, status):
        """
        click id='C24_W74_V76_V80_btsubject_struct.conc_key-btn'
        click link_text="Already registered to another disti"
        :param status:
        :return:
        """
        self.wc.click('id', r'C24_W74_V76_V80_btsubject_struct.conc_key-btn')
        self.wc.wait_element('link_text', status, time_sec=3)
        self.wc.click('link_text', status)

    def _edit_dreg_approver(self, approver):
        """
        clear id=C24_W74_V76_V80_btparterapprover_struct.partner_no
        sendkeys id=C24_W74_V76_V80_btparterapprover_struct.partner_no string='Vasily Basov' -enter
        :param approver:
        :return:
        """
        self.wc.clear('id', r"C24_W74_V76_V80_btparterapprover_struct.partner_no")
        self.wc.send_string('id', r"C24_W74_V76_V80_btparterapprover_struct.partner_no", string=approver, end=Keys.RETURN)


    def _edit_dreg_category(self, category):
        """
        click id=C24_W74_V76_V80_btcustomerh_ext.zzqp_dmnd_flg
        click link_text="Opportunity Tracking"
        :param category:
        :return:
        """
        self.wc.click('id', r"C24_W74_V76_V80_btcustomerh_ext.zzqp_dmnd_flg")
        self.wc.wait_element('link_text', category)
        self.wc.click('link_text', category)

    def _click_backbutton(self):
        self.wc.click('id', 'BackButton')
        self.wc.wait(time_sec=10)

    def _save_dreg(self):
        """
        send_ctrl_key tag=body key=s
        wait 10 sec
        click id=BackButton
        :return:
        """

        self.wc.send_ctrl_key('tag', 'body', 's')
        self.wc.wait(time_sec=10)

