#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Test case executor (a.k.a. robot)
"""

import sys
import os
import time
import logging
from abc import ABCMeta, abstractmethod
from marionette import Marionette
from marionette_driver.errors import ElementNotVisibleException, InvalidElementStateException, NoSuchElementException
from marionette_driver import Wait, By
from gaiatest.gaia_test import GaiaApps, GaiaData
from dom_analyzer import DomAnalyzer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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


class B2gExecutor(Executor):
    def __init__(self, app_name, app_id):
        self._app_name = app_name
        self._app_id = app_id
        self._marionette = Marionette()
        self._marionette.start_session()

        # https://github.com/mozilla-b2g/gaia/blob/b568b7ae8adb6ee3651bd75acbaaedff86a08912/tests/python/gaia-ui-tests/gaiatest/gaia_test.py
        js = os.path.abspath(os.path.join(__file__, os.path.pardir, 'atoms', "gaia_apps.js"))
        self._marionette.import_script(js)
        js = os.path.abspath(os.path.join(__file__, os.path.pardir, 'atoms', "gaia_data_layer.js"))
        self._marionette.set_context(self._marionette.CONTEXT_CHROME)
        self._marionette.import_script(js)
        self._marionette.set_context(self._marionette.CONTEXT_CONTENT)

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

    def fire_event(self, clickable):
        logger.info('fire_event: id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())
        try:
            # id staring with DomAnalyzer.serial_prefix is given by our monkey and should be ignored when locating
            if clickable.get_id() and not clickable.get_id().startswith(DomAnalyzer.serial_prefix):
                self._marionette.find_element('id', clickable.get_id()).tap()
            elif clickable.get_xpath():
                self._marionette.find_element('xpath', clickable.get_xpath()).tap()
            else:
                logger.error('No id nor xpath for the clickable: id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())
                sys.exit()
        except (ElementNotVisibleException, InvalidElementStateException, NoSuchElementException):
            logger.info('Element is not interactable in fire_event(): id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())
        except Exception as e:
            logger.error('Unknown Exception: %s in fire_event(): id: %s (xpath: %s)', str(e), clickable.get_id(), clickable.get_xpath())
            sys.exit()

    def fill_form(self, clickable):
        for f in clickable.get_forms():
            for input_field in f.get_inputs():
                try:
                    if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                        self._marionette.find_element('id', input_field.get_id()).send_keys(input_field.get_value())
                    elif input_field.get_xpath():
                        self._marionette.find_element('xpath', input_field.get_xpath()).send_keys(input_field.get_value())
                    else:
                        logger.error('No id nor xpath for an input field in the form id: %s (xpath: %s)', f.get_id(), f.get_xpath())
                        sys.exit()
                except (ElementNotVisibleException, InvalidElementStateException, NoSuchElementException):
                    logger.info('Element is not interactable in fill_form(): id: %s (xpath: %s)', f.get_id(), f.get_xpath())
                except Exception as e:
                    logger.error('Unknown Exception: %s in fill_form(): id: %s (xpath: %s)', str(e), f.get_id(), f.get_xpath())
                    sys.exit()

    def empty_form(self, clickable):
        for f in clickable.get_forms():
            for input_field in f.get_inputs():
                try:
                    if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                        self._marionette.find_element('id', input_field.get_id()).clear()
                    elif input_field.get_xpath():
                        self._marionette.find_element('xpath', input_field.get_xpath()).clear()
                    else:
                        logger.error('No id nor xpath for an input field in the form %s (%s)', f.get_id(), f.get_xpath())
                        sys.exit()
                except (ElementNotVisibleException, InvalidElementStateException, NoSuchElementException):
                    logger.info('Element is not interactable in empty_form(): id: %s (xpath: %s)', f.get_id(), f.get_xpath())
                except Exception as e:
                    logger.error('Unknown Exception: %s in empty_form(): id: %s (xpath: %s)', str(e), f.get_id(), f.get_xpath())
                    sys.exit()

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
                    logger.error('No id nor xpath for the clickable: id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())
                    sys.exit()
            except (ElementNotVisibleException, InvalidElementStateException, NoSuchElementException):
                logger.info('Element is not interactable in get_screenshot(): id: %s (xpath: %s)', clickable.get_id(), clickable.get_xpath())
            except Exception as e:
                logger.error('Unknown Exception: %s in get_screenshot(): id: %s (xpath: %s)', str(e), clickable.get_id(), clickable.get_xpath())
                sys.exit()
        if not element:
            # set context to CHROME to capture whole screen
            # system frame e.g. FileNotFound cannot be captured without CONTEXT_CHROME (Don't know why)
            self._marionette.set_context(self._marionette.CONTEXT_CHROME)
        screenshot = self._marionette.screenshot(element)
        self._marionette.set_context(self._marionette.CONTEXT_CONTENT)
        return screenshot

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

        self.kill_all_apps()
        self.clear_data()
        self.touch_home_button()

        icon = self._marionette.find_element('xpath', "//div[contains(@class, 'icon')]//span[contains(text(),'" + self._app_name + "')]")
        icon.tap()
        time.sleep(0.5)
        self._marionette.switch_to_frame()
        app_frame = self._marionette.find_element('css selector', "iframe[data-url*='" + self._app_id + "']")
        self._marionette.switch_to_frame(app_frame)

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

    def clear_data(self):
        # for now, clear contact data
        # https://github.com/mozilla-b2g/gaia/blob/v2.2/tests/python/gaia-ui-tests/gaiatest/gaia_test.py#L208
        self._marionette.set_context(self._marionette.CONTEXT_CHROME)
        result = self._marionette.execute_async_script('return GaiaDataLayer.removeAllContacts();')
        assert result, 'Unable to remove all contacts'
        self._marionette.set_context(self._marionette.CONTEXT_CONTENT)
        time.sleep(0.5)

    def kill_all_apps(self):
        self._marionette.switch_to_frame()
        self._marionette.execute_async_script("""
        // Kills all running apps, except the homescreen.
        function killAll() {
          let manager = window.wrappedJSObject.appWindowManager;

          let apps = manager.getApps();
          for (let id in apps) {
            let origin = apps[id].origin;
            if (origin.indexOf('verticalhome') == -1) {
              manager.kill(origin);
            }
          }
        };
        killAll();
        // return true so execute_async_script knows the script is complete
        marionetteScriptFinished(true);
        """)
        time.sleep(0.5)
