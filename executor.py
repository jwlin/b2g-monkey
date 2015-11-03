#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Test case executor (a.k.a. robot)
"""

import sys, os, time

from abc import ABCMeta, abstractmethod
'''
from marionette import Marionette
from marionette_driver.errors import ElementNotVisibleException, InvalidElementStateException, NoSuchElementException
from marionette_driver import Wait, By
from gaiatest.gaia_test import GaiaApps, GaiaDevice
'''
from dom_analyzer import DomAnalyzer

#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions 
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
#==============================================================================================================================

class Executor():
    __metaclass__ = ABCMeta

    @abstractmethod
    def fire_event(self, clickable):
        pass

    @abstractmethod
    def fill_form(self, clickable):
        pass

    @abstractmethod
    def empty_form(self, clickable):
        pass

    @abstractmethod
    def get_source(self):
        pass

    @abstractmethod
    def get_screenshot(self):
        pass

    @abstractmethod
    def restart_app(self):
        pass

'''
class B2gExecutor(Executor):
    def __init__(self, app_name, app_id):
        self._app_name = app_name
        self._app_id = app_id
        self._marionette = Marionette()
        self._marionette.start_session()

        apps = GaiaApps(self._marionette)
        apps.kill_all()

'''
'''
        # C:\Users\Jun-Wei\Desktop\b2g\battery\manifest.webapp
        #app = GaiaApps(self._marionette).launch(self._app_name)
        #app = GaiaApps(self._marionette).launch('Battery', manifest_url='C:/Users/Jun-Wei/Desktop/b2g/battery/manifest.webapp', entry_point='/index.html')

        app = GaiaApps(self._marionette).launch('Battery')
        print app.frame
        print app.src
        print app.origin
        print app.name
        #print g_app.manifest_url

        #self._app_frame = g_app.frame
        self._app_frame_id = app.frame
        self._app_src = app.src
        self._app_origin = app.origin
        #self.app_manifest_url = g_app.manifest_url

        #self.gaia_apps = GaiaApps(self.__marionette)
        #print self.gaia_apps.displayed_app.name
        #print self.gaia_apps.installed_apps
        #print self.gaia_apps.running_apps()
        #js = os.path.abspath(os.path.join(__file__, os.path.pardir, 'atoms', "gaia_apps.js"))
        #self.__marionette.import_script(js)
'''
'''

    def fire_event(self, clickable):
        print 'fire_event: id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath())
        try:
            # id staring with DomAnalyzer.serial_prefix is given by our monkey and should be ignored when locating
            if clickable.get_id() and not clickable.get_id().startswith(DomAnalyzer.serial_prefix):
                self._marionette.find_element('id', clickable.get_id()).tap()
            elif clickable.get_xpath():
                self._marionette.find_element('xpath', clickable.get_xpath()).tap()
            else:
                raise ValueError('No id nor xpath for the clickable: id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath()))
        except (ElementNotVisibleException, InvalidElementStateException, NoSuchElementException):
            print 'Element is not interactable in fire_event(): id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath())
        except Exception as e:
            print 'Unknown Exception: %s in fire_event(): id: %s (xpath: %s)' % (str(e), clickable.get_id(), clickable.get_xpath())

    def fill_form(self, clickable):
        for f in clickable.get_forms():
            for input_field in f.get_inputs():
                try:
                    if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                        self._marionette.find_element('id', input_field.get_id()).send_keys(input_field.get_value())
                    elif input_field.get_xpath():
                        self._marionette.find_element('xpath', input_field.get_xpath()).send_keys(input_field.get_value())
                    else:
                        raise ValueError('No id nor xpath for an input field in the form id: %s (xpath: %s)' % (f.get_id(), f.get_xpath()))
                except (ElementNotVisibleException, InvalidElementStateException, NoSuchElementException):
                    print 'Element is not interactable in fill_form(): id: %s (xpath: %s)' % (f.get_id(), f.get_xpath())
                except Exception as e:
                    print 'Unknown Exception: %s in fill_form(): id: %s (xpath: %s)' % (str(e), f.get_id(), f.get_xpath())

    def empty_form(self, clickable):
        for f in clickable.get_forms():
            for input_field in f.get_inputs():
                try:
                    if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                        self._marionette.find_element('id', input_field.get_id()).clear()
                    elif input_field.get_xpath():
                        self._marionette.find_element('xpath', input_field.get_xpath()).clear()
                    else:
                        raise ValueError('No id nor xpath for an input field in the form %s (%s)' % (f.get_id(), f.get_xpath()))
                except (ElementNotVisibleException, InvalidElementStateException, NoSuchElementException):
                    print 'Element is not interactable in empty_form(): id: %s (xpath: %s)' % (f.get_id(), f.get_xpath())
                except Exception as e:
                    print 'Unknown Exception: %s in empty_form(): id: %s (xpath: %s)' % (str(e), f.get_id(), f.get_xpath())

    def get_source(self):
        return self._marionette.page_source.encode(sys.stdout.encoding, 'ignore')

    def get_screenshot(self, clickable=None):
        element = None
        if clickable:
            try:
                if clickable.get_id() and not clickable.get_id().startswith(DomAnalyzer.serial_prefix):
                    element = self._marionette.find_element('id', clickable.get_id())
                elif clickable.get_xpath():
                    element = self._marionette.find_element('xpath', clickable.get_xpath())
                else:
                    raise ValueError('No id nor xpath for the clickable: id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath()))
            except (ElementNotVisibleException, InvalidElementStateException, NoSuchElementException):
                print 'Element is not interactable in get_screenshot(): id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath())
            except Exception as e:
                print 'Unknown Exception: %s in get_screenshot(): id: %s (xpath: %s)' % (str(e), clickable.get_id(), clickable.get_xpath())
        return self._marionette.screenshot(element)

    def switch_to_frame(self, by, frame_str):
        """
        :param by: options: "id", "xpath", "link text", "partial link text", "name",
        "tag name", "class name", "css selector", "anon attribute"
        """
        # self.switch_to_top_frame()
        frame = self._marionette.find_element(by, frame_str)
        self._marionette.switch_to_frame(frame)

    def switch_to_top_frame(self):
        self._marionette.switch_to_frame()  # switch to the top-level frame

    def restart_app(self):
        # disable screen timeout and screen lock

        # todo: open b2g simulator, install app,
        # launch the app
        # unlock_screen
        #self._marionette.execute_script('window.wrappedJSObject.lockScreen.unlock();')

        #self._marionette.switch_to_frame()
        #print self.marionette.execute_async_script("GaiaApps.locateWithName('%s')" % app_name)

        # kill all running apps
        apps = GaiaApps(self._marionette)
        apps.kill_all()
        time.sleep(1)
        # todo: clear database (such as established contact)
        self.touch_home_button()
        #home_frame = self.__marionette.find_element('css selector', 'div.homescreen iframe')
        #self.__marionette.switch_to_frame(home_frame)
        icon = self._marionette.find_element('xpath', "//div[contains(@class, 'icon')]//span[contains(text(),'" + self._app_name + "')]")
        icon.tap()
        time.sleep(1)
        self._marionette.switch_to_frame()
        app_frame = self._marionette.find_element('css selector', "iframe[data-url*='" + self._app_id + "']")
        self._marionette.switch_to_frame(app_frame)
        #self._marionette.switch_to_frame(self._app_frame_id)

    def touch_home_button(self):
        # ref: https://github.com/mozilla-b2g/gaia/blob/master/tests/python/gaia-ui-tests/gaiatest/gaia_test.py#L751
        apps = GaiaApps(self._marionette)
        if apps.displayed_app.name.lower() != 'homescreen':
            # touching home button will return to homescreen
            self._dispatch_home_button_event()
            Wait(self._marionette).until(
                lambda m: apps.displayed_app.name.lower() == 'homescreen')
            apps.switch_to_displayed_app()
        else:
            apps.switch_to_displayed_app()
            mode = self._marionette.find_element(By.TAG_NAME, 'body').get_attribute('class')
            self._dispatch_home_button_event()
            apps.switch_to_displayed_app()
            if 'edit-mode' in mode:
                # touching home button will exit edit mode
                Wait(self._marionette).until(lambda m: m.find_element(
                    By.TAG_NAME, 'body').get_attribute('class') != mode)
            else:
                # touching home button inside homescreen will scroll it to the top
                Wait(self._marionette).until(lambda m: m.execute_script(
                    "return window.wrappedJSObject.scrollY") == 0)

    def _dispatch_home_button_event(self):
        self._marionette.switch_to_frame()
        self._marionette.execute_script("window.wrappedJSObject.dispatchEvent(new Event('home'));")
'''

#==============================================================================================================================
#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
class SeleniumExecutor():
    def __init__(self, browserID, url):
        #choose the type of browser
        self.browserID = browserID
        #link to the url
        self.startUrl = url

    def fire_event(self, clickable):
        print 'fire_event: id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath())
        try:
            # id staring with DomAnalyzer.serial_prefix is given by our monkey and should be ignored when locating
            if clickable.get_id() and not clickable.get_id().startswith(DomAnalyzer.serial_prefix):
                self.driver.find_element_by_id( clickable.get_id() ).click()
                self.check_alert()
            elif clickable.get_xpath():
                self.driver.find_element_by_xpath( clickable.get_xpath() ).click()
                self.check_alert()
            else:
                raise ValueError('No id nor xpath for the clickable: id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath()))
        except Exception as e:
            print 'Unknown Exception: %s in fire_event(): id: %s (xpath: %s)' % (str(e), clickable.get_id(), clickable.get_xpath())

    def fill_form(self, all_inputs):
        state_inputs = all_inputs[0]
        sate_selects = all_inputs[1]
        for input_field in state_inputs:
            try:
                if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    self.driver.find_element_by_id( input_field.get_id() ).send_keys(input_field.get_value())
                elif input_field.get_xpath():
                    self.driver.find_element_by_xpath( input_field.get_xpath() ).send_keys(input_field.get_value())
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                print 'Unknown Exception: %s' % (str(e))
        for select_field in sate_selects:
            try:
                if select_field.get_id() and not select_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    select = Select(self.driver.find_element_by_id(select_field.get_id()))
                    select.select_by_index(select_field.get_value())
                elif select_field.get_xpath():
                    select = Select(self.driver.find_element_by_xpath(select_field.get_xpath()))
                    select.select_by_index(select_field.get_value())
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                print 'Unknown Exception: %s' % (str(e))


    def empty_form(self, all_inputs):
        state_inputs = all_inputs[0]
        sate_selects = all_inputs[1]
        for input_field in state_inputs:
            try:
                if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    self.driver.find_element_by_id( input_field.get_id() ).clear()
                elif input_field.get_xpath():
                    self.driver.find_element_by_xpath( input_field.get_xpath() ).clear()
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                print 'Unknown Exception: %s' % (str(e))
        for select_feild in sate_selects:
            try:
                if select_field.get_id() and not select_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    select = Select(self.driver.find_element_by_id(select_field.get_id()))
                    select.select_by_index(0)
                elif select_field.get_xpath():
                    select = Select(self.driver.find_element_by_xpath(select_field.get_xpath()))
                    select.select_by_index(0)
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                print 'Unknown Exception: %s' % (str(e))

    def get_source(self):
        text = self.driver.page_source
        return text.encode('utf-8')

    def get_screenshot(self, file_path):
        return self.driver.get_screenshot_as_file(file_path)

    def start(self):
        if self.browserID == 1:
            self.driver = webdriver.Firefox();
        elif self.browserID == 2:
            self.driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
        elif self.browserID == 3:
            self.driver = webdriver.PhantomJS(executable_path='C:/PhantomJS/bin/phantomjs/phantomjs.exe')
        else:
            self.driver = webdriver.Firefox(); 
        self.driver.get(self.startUrl)

    def restart_app(self):
        self.driver.close()
        self.start()

    def back_history(self):
        self.driver.execute_script("window.history.go(-1)")

    def get_url(self):
        return self.driver.current_url

    def check_alert(self):
        try:
            alert = self.driver.switch_to_alert()
            print "[LOG] click with alert: %s" % alert.text
            alert.accept()
        except Exception:
            print "[LOG] click without alert"

    def close(self):
        self.driver.close()
#==============================================================================================================================