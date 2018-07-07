from mylogger import mylog

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver as wd
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException

class ClickerException(Exception):
    pass


def get_html_by_element(element, inner=True):
    if inner:
        return element.get_attribute('innerHTML')
    else:
        return element.get_attribute('outerHTML')


class WebClicker:
    def __init__(self, driver_exe_path, browser='firefox', profile_path='', browser_binary=None):

        mylog.debug("Init WebClicker")

        self.webdriver = None
        self.profile = None
        try:
            if browser == 'firefox':
                if profile_path:
                    self.profile = wd.FirefoxProfile(profile_path)
                else:
                    self.profile = None
                self.webdriver = wd.Firefox(firefox_profile=self.profile, executable_path=driver_exe_path,
                                            firefox_binary=browser_binary)
            else:
                raise ClickerException('Not supported browser {0}'.format(browser))
        except Exception as e:
            mylog.error(e)
            mylog.error('Fail to initialize {0}'.format(browser))

    def get_element(self, how, what):
        try:
            element = self.webdriver.find_element(by=how, value=what)
            return element
        except NoSuchElementException as e:
            return None

    def wait(self, time_sec):
        self.sleep(time_sec)

    def wait_element(self, name, value, time_sec=10):
        how = self.get_by(name)
        return self._wait_element(how, value, time_sec)

    def _wait_element(self, how: str, what: str, timeout_sec=1):

        for i in range(timeout_sec):
            if self.is_element_ready(how, what):
                mylog.debug('Element {0}: {1} found. Waiting time is {2} sec'.format(how, what, i))
                return True
            else:
                self.sleep(1)
                mylog.debug('Waiting element {0}: {1} {2} sec'.format(how, what, i))

        mylog.error("Element {0}: {1} NOT found. Timeout = {2} sec".format(how, what, timeout_sec))
        return False

    def get_element_value(self, how: By, path: str, timeout_sec=30):

        for i in range(timeout_sec):
            element = self.get_element(how, path)
            if element is not None:
                mylog.debug('Element {0}: {1} found. Waiting time is {2} sec'.format(how, path, i))
                return element.get_attribute('value')
            else:
                self.sleep(1)
                mylog.debug('Waiting element {0}: {1} {2} sec'.format(how, path, i))

        mylog.error("Element {0}: {1} NOT found. Timeout = {2} sec".format(how, path, timeout_sec))
        return ''

    def is_element_present(self, how, what):
        try:
            self.webdriver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def is_element_ready(self, how, what):
        if self.is_element_present(how, what):
            return self.webdriver.find_element(by=how, value=what).is_enabled()
        else:
            return False

    def find_elements(self, name, value, partial=False):
        by = self.get_by(name)
        if partial and by == By.LINK_TEXT:
            by = By.PARTIAL_LINK_TEXT

        return self.webdriver.find_elements(by, value)

    def find_element(self, name, value, partial=False):
        out = self.find_elements(name, value, partial)
        if len(out) > 0:
            mylog.debug('{0}: {1} - {2} element(s) found'.format(name, value, len(out)))
            return out[0]
        else:
            return None

    def get_html(self, name, value, inner=True):
        elem = self.find_element(name, value)
        get_html_by_element(elem, inner)

    def get_full_html(self):
        return self.webdriver.page_source

    def click(self, name, value, partial=False, time_sec=1):
        element = self.find_element(name, value, partial)
        if element:
            mylog.debug("Click element {0}={1}".format(name, value))
            t = 0
            while t < time_sec:
                try:
                    element.click()
                    return True
                except WebDriverException:
                    self.wait(1)
                    t += 1
        else:
            mylog.error("Can't click element {0}={1}".format(name, value))

        return False

    def drop_down(self, by_name, how_value, set_value, time_sec=1, repeat_if_fail=0):

        for repeat in range(repeat_if_fail+1):
            success = self.click(by_name, how_value, time_sec=time_sec)
            if success:
                success = self.click('link_text', set_value, time_sec=time_sec)
                if success:
                    mylog.debug("Dropdown {0}='{1}' selected '{2}'".format(by_name, how_value, set_value))
                    return True

        mylog.error("Dropdown {0}='{1}' FAIL to select '{2}'".format(by_name, how_value, set_value))
        return False

    def clear(self, name, value, partial=False):
        element = self.find_element(name, value, partial)
        if element:
            mylog.debug("Clear element {0}={1}".format(name, value))
            element.clear()
        else:
            mylog.error("Can't clear element {0}={1}".format(name, value))

    def send_string(self, name, value, string: str, end='', partial=False):
        element = self.find_element(name, value, partial)
        if not element:
            mylog.error("Element {0}: {1} NOT found. String '{2}' NOT sent".format(name, value, string))
            return False
        else:
            element.send_keys(string + end)
            mylog.debug("Sent string '{0}' to element {1} {2}".format(string, name, value))
            return True


    def send_ctrl_key(self, name, value, key):
        element = self.find_element(name, value)
        if element:
            element.send_keys(Keys.CONTROL+key+Keys.NULL)
            mylog.debug("Sent Ctrl-{0} to element {1} {2}".format(key, name, value))
            return True
        else:
            mylog.error("Can't send Ctrl-{0} to element {1} {2}".format(key, name, value))
            return False


    def shutdown(self):
        self.webdriver.stop_client()
        self.webdriver.close()
        mylog.debug("Shutdown webdriver")

    def get_website(self, url):
        if not url.startswith(r'https://'):
            url = r'https://' + url
        mylog.debug("Trying load '{0}'".format(url))
        try:
            self.webdriver.get(url)
            return True
        except WebDriverException:
            mylog.error("Can't open page: '{0}'".format(url))
            return False

    def switch_to_frame(self, name, value):
        element = self.find_element(name, value)
        if element:
            self.webdriver.switch_to.frame(element)
            mylog.debug('Switching to frame {0}={1}'.format(name, value))
            return True
        else:
            mylog.error("Can't switch to frame {0}={1}".format(name, value))
            return False

    def switch_to_frame_by_index(self, index, time_sec=10):
        t = 0
        while t < time_sec:
            try:
                self.webdriver.switch_to.frame(index)
                mylog.debug('Switching to frame index={0}; time={1}'.format(index, t))
                return True
            except NoSuchFrameException:
                self.wait(1)
                t += 1
                mylog.debug('Waiting frame index={0}; time={1}'.format(index, t))

        mylog.error("Can't switch to frame index = {0}; time = time_sec")
        return False


    def get_attribute(self, name, value, attribute_name):
        element = self.find_element(name, value)
        if element:
            attribute = element.get_attribute(attribute_name)
            mylog.debug("Element {0} = '{1}' attribute {2}={3}".format(name, value, attribute_name, attribute))
            return attribute
        else:
            mylog.error("Can't read attribute {2}: Element {0}: {1} NOT found.".format(name, value, attribute_name))
            return ''

    def switch_to_window(self, window_name):
        self.webdriver.switch_to.window(window_name)

    @staticmethod
    def get_by(name):
        if name == 'id':
            by = By.ID
        elif name == 'name':
            by = By.NAME
        elif name == 'xpath':
            by = By.XPATH
        elif name == 'link_text':
            by = By.LINK_TEXT
        elif name == 'tag':
            by = By.TAG_NAME
        elif name == 'class':
            by = By.CLASS_NAME
        elif name == 'css':
            by = By.CSS_SELECTOR
        elif name == 'partial_link_text':
            by = By.PARTIAL_LINK_TEXT
        else:
            by = ''
        return by

    @staticmethod
    def sleep(time_sec):
            time.sleep(time_sec)
