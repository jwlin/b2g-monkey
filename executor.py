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
        print '[EVENT] fire_event: id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath())
        #raw_input("enter to click")
        try:
            # id staring with DomAnalyzer.serial_prefix is given by our monkey and should be ignored when locating
            if clickable.get_id() and not clickable.get_id().startswith(DomAnalyzer.serial_prefix):
                el = self.driver.find_element_by_id( clickable.get_id() ).click()
                self.check_after_click()
            elif clickable.get_xpath():
                self.driver.find_element_by_xpath( clickable.get_xpath() ).click()
                self.check_after_click()
            else:
                raise ValueError('No id nor xpath for the clickable: id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath()))
        except Exception as e:
            print 'Unknown Exception: %s in fire_event(): id: %s (xpath: %s)' % (str(e), clickable.get_id(), clickable.get_xpath())

    def fill_form(self, all_inputs):
        state_inputs = all_inputs[0]
        state_selects = all_inputs[1]
        for select_field in state_selects:
            #raw_input("enter to fill")
            try:
                if select_field.get_id() and not select_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    select = Select(self.driver.find_element_by_id(select_field.get_id()))
                    select.select_by_index(select_field.get_value())
                    self.check_after_click()
                elif select_field.get_xpath():
                    select = Select(self.driver.find_element_by_xpath(select_field.get_xpath()))
                    select.select_by_index(select_field.get_value())
                    self.check_after_click()
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                pass
                #print 'Unknown Exception: %s' % (str(e))
        for input_field in state_inputs:
            #raw_input("enter to fill")
            try:
                if input_field.get_type() == 'checkbox':
                    if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                        self.driver.find_element_by_id( input_field.get_id() ).click()
                        self.check_after_click()
                    elif input_field.get_xpath():
                        self.driver.find_element_by_xpath( input_field.get_xpath() ).click()
                        self.check_after_click()
                elif input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    self.driver.find_element_by_id( input_field.get_id() ).send_keys(input_field.get_value())
                    self.check_after_click()
                elif input_field.get_xpath():
                    self.driver.find_element_by_xpath( input_field.get_xpath() ).send_keys(input_field.get_value())
                    self.check_after_click()
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                pass
                #print 'Unknown Exception: %s' % (str(e))


    def empty_form(self, all_inputs):
        state_inputs = all_inputs[0]
        state_selects = all_inputs[1]
        for input_field in state_inputs:
            #raw_input("enter to empty")
            try:
                if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    self.driver.find_element_by_id( input_field.get_id() ).clear()
                    self.check_after_click()
                elif input_field.get_xpath():
                    self.driver.find_element_by_xpath( input_field.get_xpath() ).clear()
                    self.check_after_click()
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                pass
                #print 'Unknown Exception: %s' % (str(e))

    def get_source(self):
        try:
            text = self.driver.page_source
        except Exception as e:
            print "[ERROR] ", e
            self.driver.refresh()
            self.check_after_click()
            self.driver.page_source
        except Exception as e:
            print "[ERROR] ", e
            url = self.driver.current_url
            self.driver.close()
            self.start()
            self.driver.get(url)
            self.driver.page_source
        except Exception as e:
            print "[ERROR] ", e
            text = "ERROR! cannot load file"
        return text.encode('utf-8')

    def switch_iframe_and_get_source(self, iframe_xpath_list=None):
        try:
            self.driver.switch_to_default_content()
            if iframe_xpath_list:
                for xpath in iframe_xpath_list:        
                    iframe = self.driver.find_element_by_xpath(xpath)
                    self.driver.switch_to_frame(iframe)
        except Exception as e:
            print '[ERROR] switch_iframe : %s' % (str(e))
        return self.get_source()

    def get_screenshot(self, file_path):
        return self.driver.get_screenshot_as_file(file_path)

    def start(self):
        '''
        if self.browserID == 1:
            self.driver = webdriver.Firefox();
        elif self.browserID == 2:
            self.driver = webdriver.Chrome(executable_path='/usr/local/share/chromedriver')
        elif self.browserID == 3:
            self.driver = webdriver.PhantomJS()
        '''
        try:
            if self.browserID == 1:
                self.driver = webdriver.Firefox();
            elif self.browserID == 2:
                self.driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
            elif self.browserID == 3:
                self.driver = webdriver.PhantomJS(executable_path='C:/PhantomJS/bin/phantomjs/phantomjs.exe')
            else: #default in firefox
                self.driver = webdriver.Firefox(); 
            self.driver.set_window_size(1280,960)
            self.main_window = self.driver.current_window_handle
        except Exception as e:
            print '[ERROR] start driver : %s' % (str(e))

    def goto_url(self):
        try:
            self.driver.get(self.startUrl)
        except Exception as e:
            print '[ERROR] driver get url : %s' % (str(e))

    def refresh(self):
        try:
            self.driver.refresh()
            self.check_after_click()
        except Exception as e:
            print '[ERROR] refresh : %s' % (str(e))

    def restart_app(self):
        self.close()
        self.start()

    def back_history(self):
        try:
            time.sleep(1)
            self.driver.back()
            self.check_after_click()
        except Exception as e:
            print '[ERROR] back : %s' % (str(e))

    def forward_history(self):
        try:
            time.sleep(1)
            self.driver.forward()
            self.check_after_click()
        except Exception as e:
            print '[ERROR] back : %s' % (str(e))

    def get_url(self):
        try:
            return self.driver.current_url
        except Exception as e:
            print '[ERROR] get url : %s' % (str(e))
            return 'error url'

    #=============================================================================================
    #Diff: check any browser detail after cleck event
    def check_after_click(self):
        time.sleep(1)
        self.check_alert()
        self.check_window()
        self.check_tab()
        time.sleep(1)

    def check_alert(self):
        no_alert = False
        while not no_alert:
            try:
                alert = self.driver.switch_to_alert()
                print "[LOG] click with alert: %s" % alert.text
                alert.dismiss()
            except Exception:
                #print "[LOG] click without alert"
                no_alert = True

    def check_window(self):
        if len(self.driver.window_handles) > 1:
            print "[LOG] more than one window appear"
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
            print '[ERROR] close : %s' % (str(e))        
#==============================================================================================================================