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
        print 'fire_event: id: %s (xpath: %s)' % (clickable.get_id(), clickable.get_xpath())
        try:
            # id staring with DomAnalyzer.serial_prefix is given by our monkey and should be ignored when locating
            if clickable.get_id() and not clickable.get_id().startswith(DomAnalyzer.serial_prefix):
                el = self.driver.find_element_by_id( clickable.get_id() )
                if el.text == "登出":
                    raise ValueError('not to log out!')
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
        sate_selects = all_inputs[1]
        for input_field in state_inputs:
            #print "[DEBUG] fill: ",input_field.__str__()
            try:
                if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    self.driver.find_element_by_id( input_field.get_id() ).send_keys(input_field.get_value())
                elif input_field.get_xpath():
                    self.driver.find_element_by_xpath( input_field.get_xpath() ).send_keys(input_field.get_value())
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                pass
                #print 'Unknown Exception: %s' % (str(e))
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
                pass
                #print 'Unknown Exception: %s' % (str(e))


    def empty_form(self, all_inputs):
        state_inputs = all_inputs[0]
        sate_selects = all_inputs[1]
        for input_field in state_inputs:
            #print "[DEBUG] empty: ",input_field.__str__()
            try:
                if input_field.get_id() and not input_field.get_id().startswith(DomAnalyzer.serial_prefix):
                    self.driver.find_element_by_id( input_field.get_id() ).clear()
                elif input_field.get_xpath():
                    self.driver.find_element_by_xpath( input_field.get_xpath() ).clear()
                else:
                    raise ValueError('No id nor xpath for an input field')
            except Exception as e:
                pass
                #print 'Unknown Exception: %s' % (str(e))
        for select_field in sate_selects:
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
                pass
                #print 'Unknown Exception: %s' % (str(e))

    def get_source(self):
        try:
            text = self.driver.page_source
        except Exception as e:
            print "[ERROR] ", e
            self.driver.refresh()
            text = "ERROR! cannot load file"
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
            self.driver.set_window_size(1120, 550)
        self.driver.get(self.startUrl)
        self.main_window = self.driver.current_window_handle

    def restart_app(self):
        self.driver.close()
        self.start()

    def back_history(self):
        try:
            time.sleep(0.5)
            self.driver.back()
        except Exception as e:
            print '[ERROR] back : %s' % (str(e))

    def get_url(self):
        return self.driver.current_url

    #=============================================================================================
    #Diff: check any browser detail after cleck event
    def check_after_click(self):
        print "[LOG] sleep after click event"
        time.sleep(0.5)
        self.check_alert()
        self.check_window()
        self.check_tab()

    def check_alert(self):
        try:
            alert = self.driver.switch_to_alert()
            print "[LOG] click with alert: %s" % alert.text
            alert.accept()
        except Exception:
            print "[LOG] click without alert"

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
        self.driver.close()
#==============================================================================================================================