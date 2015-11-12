#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Definition of HTML elements: clickables, form and input field
"""


class Clickable:
    def __init__(self, clickable_id=None, xpath=None, tag=None):
        self._id = clickable_id
        self._xpath = xpath
        self._tag = tag
        self._forms = []

    def get_id(self):
        return self._id

    def get_xpath(self):
        return self._xpath

    def get_forms(self):
        return self._forms

    def get_tag(self):
        return self._tag

    def add_form(self, form):
        if form in self._forms:
            return False
        self._forms.append(form)
        return True

    def remove_form(self, form):
        if form in self._forms:
            self._forms.remove(form)
            return True
        return False

    def __str__(self):
        return 'clickable id: %s (xpath: %s), forms: %s' % (self._id, self._xpath, len(self._forms))

    def __eq__(self, other):
        if self._id and other.get_id():
            return self._id == other.get_id()
        else:
            return self._xpath == other.get_xpath()


class FormField:
    def __init__(self, form_id=None, xpath=None):
        self._id = form_id
        self._xpath = xpath
        self._inputs = []

    def get_inputs(self):
        return self._inputs

    def get_id(self):
        return self._id

    def get_xpath(self):
        return self._xpath

    def add_input(self, input_field):
        if input_field in self._inputs:
            return False
        self._inputs.append(input_field)
        return True

    def remove_input(self, input_field):
        if input_field in self._inputs:
            self._inputs.remove(input_field)
            return True
        return False

    def __str__(self):
        return 'form id: %s (xpath: %s), inputs: %s' % (self._id, self._xpath, len(self._inputs))

    def __eq__(self, other):
        if self._id and other.get_id():
            return self._id == other.get_id()
        else:
            return self._xpath == other.get_xpath()


class InputField:
    def __init__(self, input_id=None, xpath=None, input_type=None, value=None):
        self._id = input_id
        self._xpath = xpath
        self._value = value
        self._type = input_type

    def set_value(self, text):
        self._value = text

    def get_value(self):
        return self._value

    def get_id(self):
        return self._id

    def get_xpath(self):
        return self._xpath

    def get_type(self):
        return self._type

    def __str__(self):
        return 'input id: %s (xpath: %s), type: %s, value: %s' % (self._id, self._xpath, self._type, self._value)

    def __eq__(self, other):
        if self._id and other.get_id():
            return self._id == other.get_id()
        else:
            return self._xpath == other.get_xpath()