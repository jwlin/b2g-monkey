#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Test case executor (a.k.a. robot)
"""

import sys, os, time

from abc import ABCMeta, abstractmethod
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
        self.main_window = None

    def fire_event(self, clickable):
        logging.info(' fire_event: id(%s) xpath(%s)', clickable.get_id(), clickable.get_xpath())
        try:
            element = self.get_element_by_tag(clickable)
            if not element:
                raise ValueError('No id nor xpath for an clickable')
            element.click()
            self.check_after_click()
        except Exception as e:
            logging.error(' Unknown Exception: %s in fire_event: id(%s) xpath(%s) \t\t__from executor.py fire_event()',str(e), clickable.get_id(), clickable.get_xpath())
                
    def fill_inputs_text(self, inputs):
        for input_field in inputs:
            try:
                element = self.get_element_by_tag(input_field)
                if not element:
                    raise ValueError('No id nor xpath for an input field')
                element.clear()
                element.send_keys(input_field.get_value())
                self.check_after_click()
            except Exception as e:
                logging.error(' Unknown Exception: %s in input: id(%s) xpath(%s) \t\t__from executor.py fill_inputs_text()',str(e), input_field.get_id(), input_field.get_xpath())
                
    def fill_selects(self, selects):
        for select_field in selects:
            try:
                element =  Select( self.get_element_by_tag(select_field) )
                if not element:
                    raise ValueError('No id nor xpath for an select field')
                element.select_by_index( int(select_field.get_value()) )
                self.check_after_click()
            except Exception as e:
                logging.error(' Unknown Exception: %s in select: id(%s) xpath(%s) \t\t__from executor.py fire_event()',str(e), select_field.get_id(), select_field.get_xpath())
                
    def fill_checkboxes(self, checkboxes):
        for checkbox_field in checkboxes:
            try:
                checkbox_list = checkbox_field.get_checkbox_list()
                #clear all
                for checkbox in checkbox_list:
                    element = self.get_element_by_tag(checkbox)
                    if not element:
                        raise ValueError('No id nor xpath for an checkbox')
                    if element.is_selected():
                        element.click()
                        self.check_after_click()
                for selected_id in checkbox_field.get_value():
                    selected_element = self.get_element_by_tag( checkbox_list[int(selected_id)] )
                    if not selected_element:
                        raise ValueError('No id nor xpath for an checkbox')
                    selected_element.click()
                    self.check_after_click()
            except Exception as e:
                logging.error(' Unknown Exception: %s in checkbox: id(%s) xpath(%s) \t\t__from executor.py fire_event()',str(e), checkbox_field.get_id(), checkbox_field.get_xpath())
                
    def fill_radios(self, radios):
        for radio_field in radios:
            try:
                selected_id = int(radio_field.get_value())
                radio_list = radio_field.get_radio_list()
                element = self.get_element_by_tag( radio_list[selected_id] )
                if not element:
                    raise ValueError('No id nor xpath for an radio')
                if not element.is_selected():
                    element.click()
                self.check_after_click()
            except Exception as e:
                logging.error(' Unknown Exception: %s in radio: id(%s) xpath(%s) \t\t__from executor.py fire_event()',str(e), radio_field.get_id(), radio_field.get_xpath())
                
    def get_element_by_tag(self, element):
        if element.get_id() and not element.get_id().startswith(DomAnalyzer.serial_prefix):
            return self.driver.find_element_by_id( element.get_id() )
        elif element.get_xpath():
            return self.driver.find_element_by_xpath( element.get_xpath() )
        else:
            return None

    def get_source(self):
        try:
            text = self.driver.page_source
        except Exception as e:
            logging.error(' %s \t\t__from executor.py get_source()', str(e))
            print "[ERROR] ", e
            self.driver.refresh()
            self.check_after_click()
            self.driver.page_source
        except Exception as e:
            logging.error(' %s \t\t__from executor.py get_source()', str(e))
            url = self.driver.current_url
            self.driver.close()
            self.start()
            self.driver.get(url)
            self.driver.page_source
        except Exception as e:
            logging.error(' %s \t\t__from executor.py get_source()', str(e))
            text = "ERROR! cannot load file"
        return text.encode('utf-8')

    def switch_iframe_and_get_source(self, iframe_xpath_list=None):
        try:
            self.driver.switch_to_default_content()
            if iframe_xpath_list and iframe_xpath_list[0] != 'None':
                for xpath in iframe_xpath_list:        
                    iframe = self.driver.find_element_by_xpath(xpath)
                    self.driver.switch_to_frame(iframe)
        except Exception as e:
            logging.error(' switch_iframe : %s \t\t__from executor.py switch_iframe_and_get_source()', str(e))
        return self.get_source()

    def get_screenshot(self, file_path):
        return self.driver.get_screenshot_as_file(file_path)

    def start(self):
        '''
            if self.browserID == 1:
                self.driver = webdriver.Firefox();
            elif self.browserID == 2:
                self.driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
            elif self.browserID == 3:
                self.driver = webdriver.PhantomJS(executable_path='C:/PhantomJS/bin/phantomjs/phantomjs.exe')
        '''
        try:
            if self.browserID == 1:
                self.driver = webdriver.Firefox();
            elif self.browserID == 2:
                self.driver = webdriver.Chrome(executable_path='/usr/local/share/chromedriver')
            elif self.browserID == 3:
                self.driver = webdriver.PhantomJS()
            else: #default in firefox
                self.driver = webdriver.Firefox(); 
            self.driver.set_window_size(1280,960)
            self.main_window = self.driver.current_window_handle
        except Exception as e:
            logging.error(' start driver : %s \t\t__from executor.py start()', str(e))

    def goto_url(self):
        try:
            self.driver.get(self.startUrl)
        except Exception as e:
            logging.error(' driver get url : %s \t\t__from executor.py goto_url()', str(e))

    def refresh(self):
        try:
            self.driver.refresh()
            self.check_after_click()
        except Exception as e:
            logging.error(' refresh : %s \t\t__from executor.py refresh()', str(e))

    def restart_app(self):
        self.close()
        self.start()

    def back_history(self):
        try:
            time.sleep(1)
            self.driver.back()
            self.check_after_click()
        except Exception as e:
            logging.error(' back : %s \t\t__from executor.py back_history()', str(e))

    def forward_history(self):
        try:
            time.sleep(1)
            self.driver.forward()
            self.check_after_click()
        except Exception as e:
            logging.error(' forward : %s \t\t__from executor.py forward_history()', str(e))

    def get_url(self):
        try:
            return self.driver.current_url
        except Exception as e:
            logging.error(' get url : %s \t\t__from executor.py get_url()', str(e))
            return 'error url'

    #=============================================================================================
    #Diff: check any browser detail after cleck event
    def check_after_click(self):
        time.sleep(1)
        self.check_alert()
        self.check_window()
        self.check_tab()
        time.sleep(0.1)

    def check_alert(self):
        no_alert = False
        while not no_alert:
            try:
                alert = self.driver.switch_to_alert()
                logging.info(' click with alert: %s ', alert.text)
                alert.dismiss()
            except Exception:
                no_alert = True

    def check_window(self):
        if len(self.driver.window_handles) > 1:
            logging.info(' more than one window appear')
            for handle in self.driver.window_handles:
                if handle != self.main_window:
                    self.driver.switch_to_window(handle)
                    self.driver.close()
            self.driver.switch_to_window(self.main_window)

    def check_tab(self):
        pass
    #=============================================================================================

    def close(self):
        try:
            self.driver.close()
        except Exception as e:
            logging.error(' close : %s \t\t__from executor.py close()', str(e))
#==============================================================================================================================