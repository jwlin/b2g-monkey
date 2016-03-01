#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Definition of HTML elements: clickables, form and input field
"""
import dom_analyzer
import logging

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

    def get_copy(self):
        return Clickable(self._id, self._name, self._xpath, self._tag)

    def __str__(self):
        return 'clickable id: %s (xpath: %s) ' % (self._id, self._xpath )
        
class InputField:
    def __init__(self, input_id=None, input_name=None, xpath=None, input_type=None, value=None):
        self._id = input_id
        self._name = input_name
        self._xpath = xpath
        self._value = value
        self._type = input_type
        self._mutation_info = None

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

    def set_mutation_info(self, info):
        self._mutation_info = info

    def get_mutation_info(self):
        return self._mutation_info

    def get_data_set(self, databank):
        if not self._id.startswith(dom_analyzer.DomAnalyzer.serial_prefix):
            data_set = databank.get_data(self._type, self._id)
        elif not self._name.startswith(dom_analyzer.DomAnalyzer.serial_prefix):
            data_set = databank.get_data(self._type, self._name)
        else:
            data_set = databank.get_data(self._type, 'None')

        return data_set

    def get_mutation_data_set(self, databank, modes):
        mutation_type = self._type if self._type else 'text'
        mutation_attr = self._id if not self._id.startswith(dom_analyzer.DomAnalyzer.serial_prefix) \
            else self._name if not self._name.startswith(dom_analyzer.DomAnalyzer.serial_prefix) \
            else 'None'

        data_set = databank.get_mutation_data_set(mutation_type, mutation_attr, modes)
        return data_set

    def get_copy(self):
        return InputField(self._id, self._name, self._xpath, self._type, self._value)

    def __str__(self):
        return 'input id: %s (xpath: %s), type: %s, value: %s' % (self._id, self._xpath, self._type, self._value)

#=============================================================================================
#Diff: select, checkbox, radio is an input, too.
class SelectField:
    def __init__(self, select_id=None, select_name=None, xpath=None, value=None, selected=None):
        self._id = select_id
        self._name = select_name
        self._xpath = xpath
        self._value = value
        self._selected = selected

    #this value is list type
    def get_value(self):
        return self._value

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_xpath(self):
        return self._xpath

    def set_selected(self, selected):
        self._selected = selected

    def get_selected(self):
        return self._selected

    def get_data_set(self, databank ):
        if not self._id.startswith(dom_analyzer.DomAnalyzer.serial_prefix):
            data_set = databank.get_data('select', self._id)
        elif not self._name.startswith(dom_analyzer.DomAnalyzer.serial_prefix):
            data_set = databank.get_data('select', self._name)
        else:
            data_set = databank.get_data('select', 'None')
        return data_set

    def get_copy(self):
        return SelectField(self._id, self._name, self._xpath,
                    [ v for v in self._value ], self._selected)

    def __str__(self):
        return 'select id: %s (xpath: %s), value: %s' % (self._id, self._xpath, self._value)

class Checkbox:
    def __init__(self, checkbox_id=None, checkbox_name=None, xpath=None, value=None):
        self._id = checkbox_id
        self._name = checkbox_name
        self._xpath = xpath
        self._value = value

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_xpath(self):
        return self._xpath

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_copy(self):
        return Checkbox(self._id, self._name, self._xpath, self._value)

    def __str__(self):
        return 'checkbox id: %s, name: %s, (xpath: %s), value: %s' % (self._id, self._name, self._xpath, self._value)

class CheckboxField:
    def __init__(self, checkbox_list=None, checkbox_name=None, checkbox_selected_list=None):
        self._checkbox_list = checkbox_list
        self._checkbox_name = checkbox_name
        self._checkbox_selected_list = checkbox_selected_list

    def set_selected_list(self, selected_list):
        self._checkbox_selected_list = selected_list

    def get_selected_list(self):
        return self._checkbox_selected_list

    def get_checkbox_list(self):
        return self._checkbox_list

    def get_checkbox_by_id(self, list_id):
        return self._checkbox_list[list_id] if len(self._checkbox_list) >= list_id else None

    def get_checkbox_name(self):
        return self._checkbox_name

    def get_data_set(self, databank):
        if not self._checkbox_name.startswith(dom_analyzer.DomAnalyzer.serial_prefix):
            data_set = databank.get_data('checkbox', self._checkbox_name)
        elif not self._checkbox_list[0].get_id().startswith(dom_analyzer.DomAnalyzer.serial_prefix):
            data_set = databank.get_data('checkbox', self._checkbox_list[0].get_id())
        else:
            data_set = databank.get_data('checkbox', 'None')
        return data_set

    def get_copy(self):
        return CheckboxField([ c.get_copy() for c in self._checkbox_list ],
                            self._checkbox_name, self._checkbox_selected_list)

class Radio:
    def __init__(self, radio_id=None, radio_name=None, xpath=None, value=None):
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

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_copy(self):
        return Radio(self._id, self._name, self._xpath, self._value)

    def __str__(self):
        return 'radio id: %s, name: %s, (xpath: %s), value: %s' % (self._id, self._name, self._xpath, self._value)

class RadioField:
    def __init__(self, radio_list, radio_name=None, radio_selected=None):
        self._radio_list = radio_list
        self._radio_name = radio_name
        self._radio_selected = radio_selected

    def set_selected(self, selected):
        self._radio_selected = selected

    def get_selected(self):
        return self._radio_selected

    def get_radio_list(self):
        return self._radio_list

    def get_radio_by_id(self, list_id):
        return self._radio_list[list_id] if len(self._radio_list) >= list_id else None

    def get_radio_name(self):
        return self._radio_name

    def get_data_set(self, databank):
        if not self._radio_name.startswith(dom_analyzer.DomAnalyzer.serial_prefix):
            data_set = databank.get_data('radio', self._radio_name)
        elif not self._radio_list[0].get_id().startswith(dom_analyzer.DomAnalyzer.serial_prefix):
            data_set = databank.get_data('radio', self._radio_list[0].get_id())
        else:
            data_set = databank.get_data('radio', 'None')
        return data_set

    def get_copy(self):
        return RadioField([ r.get_copy() for r in self._radio_list ],
                            self._radio_name, self._radio_selected)
#=============================================================================================