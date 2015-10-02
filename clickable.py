#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Definition of HTML elements: clickables, form and input field
"""


class Clickable:
    def __init__(self, clickable_id=None, xpath=None, tag=None):
        self.__id = clickable_id
        self.__xpath = xpath
        self.__tag = tag
        self.__forms = []

    def get_id(self):
        return self.__id

    def get_xpath(self):
        return self.__xpath

    def get_forms(self):
        return self.__forms

    def add_form(self, form):
        if form.get_id():
            for _form in self.__forms:
                if _form.get_id() == form.get_id():
                    return False
        else:
            for _form in self.__forms:
                if _form.get_xpath() == form.get_xpath():
                    return False
        self.__forms.append(form)
        return True

    def remove_form(self, form):
        if form.get_id():
            for _form in self.__forms:
                if _form.get_id() == form.get_id():
                    self.__forms.remove(_form)
                    return True
        else:
            for _form in self.__forms:
                if _form.get_xpath() == form.get_xpath():
                    self.__forms.remove(_form)
                    return True
        return False

    def __str__(self):
        return 'clickable id: %s (xpath: %s), forms: %s' % (self.__id, self.__xpath, len(self.__forms))


class FormField:
    def __init__(self, form_id=None, xpath=None):
        self.__id = form_id
        self.__xpath = xpath
        self.__inputs = []

    def get_inputs(self):
        return self.__inputs

    def get_id(self):
        return self.__id

    def get_xpath(self):
        return self.__xpath

    def add_input(self, input_field):
        if input_field.get_id():
            for _input in self.__inputs:
                if _input.get_id() == input_field.get_id():
                    return False
        else:
            for _input in self.__inputs:
                if _input.get_xpath() == input_field.get_xpath():
                    return False
        self.__inputs.append(input_field)
        return True

    def remove_input(self, input_field):
        for _input in self.__inputs:
            if _input.get_id() == input_field.get_id():
                self.__inputs.remove(_input)
                return True
        return False

    def __str__(self):
        return 'form id: %s (xpath: %s), inputs: %s' % (self.__id, self.__xpath, len(self.__inputs))


class InputField:
    def __init__(self, input_id=None, xpath=None, input_type=None, value=None):
        self.__id = input_id
        self.__xpath = xpath
        self.__value = value
        self.__type = input_type

    def set_value(self, text):
        self.__value = text

    def get_value(self):
        return self.__value

    def get_id(self):
        return self.__id

    def get_xpath(self):
        return self.__xpath

    def get_type(self):
        return self.__type

    def __str__(self):
        return 'input id: %s (xpath: %s), type: %s, value: %s' % (self.__id, self.__xpath, self.__type, self.__value)