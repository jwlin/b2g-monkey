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
        if form.get_id():
            for _form in self._forms:
                if _form.get_id() == form.get_id():
                    return False
        else:
            for _form in self._forms:
                if _form.get_xpath() == form.get_xpath():
                    return False
        self._forms.append(form)
        return True

    def remove_form(self, form):
        if form.get_id():
            for _form in self._forms:
                if _form.get_id() == form.get_id():
                    self._forms.remove(_form)
                    return True
        else:
            for _form in self._forms:
                if _form.get_xpath() == form.get_xpath():
                    self._forms.remove(_form)
                    return True
        return False

    def __str__(self):
        return 'clickable id: %s (xpath: %s), forms: %s' % (self._id, self._xpath, len(self._forms))


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
        if input_field.get_id():
            for _input in self._inputs:
                if _input.get_id() == input_field.get_id():
                    return False
        else:
            for _input in self._inputs:
                if _input.get_xpath() == input_field.get_xpath():
                    return False
        self._inputs.append(input_field)
        return True

    def remove_input(self, input_field):
        for _input in self._inputs:
            if _input.get_id() == input_field.get_id():
                self._inputs.remove(_input)
                return True
        return False

    def __str__(self):
        return 'form id: %s (xpath: %s), inputs: %s' % (self._id, self._xpath, len(self._inputs))


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