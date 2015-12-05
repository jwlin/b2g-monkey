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
    def __init__(self, input_id=None, input_name=None, xpath=None, input_type=None, value=None):
        self._id = input_id
        self._name = input_name
        self._xpath = xpath
        self._value = value
        self._type = input_type

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
#Diff: select, checkbox, radio is an input, too.
class SelectField:
    def __init__(self, select_id=None, select_name=None, xpath=None, value=None):
        self._id = select_id
        self._name = select_name
        self._xpath = xpath
        self._value = value

    def set_value(self, value):
        self._value = value

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

class CheckboxField:
    def __init__(self, checkbox_id=None, checkbox_name=None, xpath=None, value=None):
        self._id = checkbox_id
        self._name = checkbox_name
        self._xpath = xpath
        self._value = value

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_xpath(self):
        return self._xpath

    def __str__(self):
        return 'checkbox id: %s, name: %s, (xpath: %s), value: %s' % (self._id, self._name, self._xpath, self._value)

class Radio:
    def __init__(self, radio_id=None, radio_name=None, xpath=None):
        self._id = radio_id
        self._name = radio_name
        self._xpath = xpath
        self._value = value

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_xpath(self):
        return self._xpath

    def __str__(self):
        return 'radio id: %s, name: %s, (xpath: %s), value: %s' % (self._id, self._name, self._xpath, self._value)

class RadioField:
    def __init__(self, radio_list, radio_name=None, radio_values=None):
        self._radio_list = radio_list
        self._radio_name = radio_name
        self._radio_value = radio_value

    def set_value(self, value_list):
        self._radio_value = value_list

    def get_value(self):
        return self._radio_value

    def get_radio_list(self):
        return self._radio_list

    def get_radio_name(self):
        return self._radio_name
#=============================================================================================