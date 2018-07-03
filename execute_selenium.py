import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver as wd
from selenium.common.exceptions import NoSuchElementException


class ClickerException(Exception):
    pass


def get_html_by_element(element, inner=True):
    if inner:
        return element.get_attribute('innerHTML')
    else:
        return element.get_attribute('outerHTML')


class WebClicker:
    def __init__(self, driver_exe_path, browser='firefox', profile_path='', browser_binary=None):

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
            print(e)
            print('Fail to initialize {0}'.format(browser))

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
                print('Element found!')
                return True
            else:
                self.sleep(1)
                print('Waiting: {0}'.format(i), end='\r')

        print("Timeout")
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

    def is_element_present(self, how, what):
        try:
            self.webdriver.find_element(by=how, value=what)
        except NoSuchElementException as e:
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

        print('find_elements({0}, {1})'.format(by, value))
        return self.webdriver.find_elements(by, value)

    def find_element(self, name, value, partial=False):
        out = self.find_elements(name, value, partial)
        if len(out) > 0:
            print('{0} element(s) found'.format(len(out)))
            return out[0]
        else:
            return None

    def get_html(self, name, value, inner=True):
        elem = self.find_element(name, value)
        get_html_by_element(elem, inner)

    def get_full_html(self):
        return self.webdriver.page_source

    def click(self, name, value, partial = False):
        elem = self.find_element(name, value, partial)
        elem.click()

    def clear(self, name, value, partial = False):
        elem = self.find_element(name, value, partial)
        elem.clear()

    def send_string(self, name, value, string: str, end='', partial=False):
        elements = self.find_elements(name, value, partial)
        if len(elements)>1:
            print('{0} elements found, use first found'.format(len(elements)))
        elements[0].send_keys(string + end)


    def send_ctrl_key(self, name, value, key):
        self.find_element(name, value).send_keys(Keys.CONTROL+key+Keys.NULL)

    def shutdown(self):
        self.webdriver.stop_client()
        self.webdriver.close()

    def get_website(self, url):
        if not url.startswith(r'https://'):
            url = r'https://' + url
        self.webdriver.get(url)

    def switch_to_frame(self, name, value):
        element = self.find_element(name, value)
        self.webdriver.switch_to.frame(element)

    def switch_to_frame_by_index(self, index):
        self.webdriver.switch_to.frame(index)

    def get_attribute(self, name, value, attribute_name):
        return self.find_element(name, value).get_attribute(attribute_name)

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
