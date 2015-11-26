#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Definition of HTML elements: clickables, form and input field
"""
"""
2015/11/03 => remove form class
"""

class Clickable:
    def __init__(self, clickable_id=None, clickable_name=None, xpath=None, tag=None):
        self._id = clickable_id
        self._name = clickable_name
        self._xpath = xpath
        self._tag = tag
        #self._forms = []

    def get_id(self):
        return self._id
        
    def get_name(self):
        return self._name

    def get_xpath(self):
        return self._xpath

    def get_tag(self):
        return self._tag
    def __str__(self):
        return 'clickable id: %s (xpath: %s) ' % (self._id, self._xpath )
        
class InputField:
    def __init__(self, input_id=None, input_name=None, xpath=None, input_type=None, value=None, iframe_path_list=None):
        self._id = input_id
        self._name = input_name
        self._xpath = xpath
        self._value = value
        self._type = input_type
        self.iframe_path_list = iframe_path_list

    def set_value(self, text):
        self._value = text

    def get_value(self):
        return self._value

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_xpath(self):
        return self._xpath

    def get_type(self):
        return self._type

    def __str__(self):
        return 'input id: %s (xpath: %s), type: %s, value: %s' % (self._id, self._xpath, self._type, self._value)

#=============================================================================================
#Diff: select is an input, too.
class SelectField:
    def __init__(self, select_id=None, select_name=None, xpath=None, value=None, iframe_path_list=None):
        self._id = select_id
        self._name = select_name
        self._xpath = xpath
        self._value = value
        self.iframe_path_list = iframe_path_list

    def set_value(self, text):
        self._value = text

    def get_value(self):
        return self._value

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_xpath(self):
        return self._xpath

    def __str__(self):
        return 'select id: %s (xpath: %s), value: %s' % (self._id, self._xpath, self._value)
#=============================================================================================