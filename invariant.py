#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Invariants, a.k.a. rules to verify on each encountered page
After defining a new invariant type, remember to add the corresponding save() and load() in configuration.py
"""

import json
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup


class Invariant:
    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self, dom):
        pass

    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def set(self, obj):
        pass


class StringInvariant(Invariant):
    def __init__(self, str_value):
        self._str_value = str_value

    def get_value(self):
        return {
            'name': 'string',
            'str': self._str_value
        }

    def set(self, str_value):
        self._str_value = str_value

    def check(self, dom):
        return self._str_value in dom

    def __str__(self):
        return json.dumps({
            'name': 'string',
            'str': self._str_value
        })

    def __eq__(self, other):
        if type(self).__name__ == type(other).__name__:
            return self.get_value()['str'] == other.get_value()['str']
        return False


# Invariant is violated if and only if all attributes and corresponding values are matched
# e.g. dom = <a class="sister" href="http://example2.com/anna" id="link2">Anna</a>
# The dom doesn't violate TagInvariant('a',
#                               [{'name': 'class', 'value': 'sister'},
#                                {'name': 'string', 'value': 'Bobby'}])
class TagInvariant(Invariant):
    def __init__(self, tag_name, attr_list=None):
        self._tag_name = tag_name
        self._tag_attr = attr_list
        # e.g. [ {'name': 'class', 'value': 'title'},
        #        {'name': 'class', 'value': 'hide'},
        #        {'name': 'id', 'value': 'error-title'} ]

    def get_value(self):
        return {
            'name': 'tag',
            'tag': self._tag_name,
            'attr': self._tag_attr
        }

    def set(self, tag_name, attr_list=None):
        self._tag_name = tag_name
        self._tag_attr = attr_list

    def check(self, dom):
        soup = BeautifulSoup(dom, 'html.parser')
        for tag in soup.find_all(self._tag_name):
            match_count = 0
            for element in self._tag_attr:
                if element['name'] == 'string':
                    if element['value'] in tag.strings:
                        match_count += 1
                elif element['name'] in tag.attrs and element['value'] in tag[element['name']]:
                    match_count += 1
            if match_count == len(self._tag_attr):
                return True
        return False

    def __str__(self):
        return json.dumps({
            'name': 'tag',
            'tag': self._tag_name,
            'attr': self._tag_attr
        })

    def __eq__(self, other):
        if type(self).__name__ == type(other).__name__:
            lhs = self.get_value()
            rhs = other.get_value()
            if lhs['tag'] == rhs['tag']:
                if (not lhs['attr']) and (not rhs['attr']):
                    return True
                elif (lhs['attr']) and (not rhs['attr']):
                    return False
                elif (not lhs['attr']) and (rhs['attr']):
                    return False
                elif len(lhs['attr']) == len(rhs['attr']):
                    for l_dict in lhs['attr']:
                        if l_dict not in rhs['attr']:
                            return False
                    return True
        return False


# FileNotFoundInvariant is a special case of TagInvariant
# <h1 class="title" id="error-title" data-l10n-id="file-not-found">File not found</h1>
class FileNotFoundInvariant(Invariant):
    def __init__(self):
        pass

    def get_value(self):
        return {
            'name': 'file-not-found'
        }

    def set(self, obj):
        pass

    def check(self, dom):
        invariant = TagInvariant(
            'h1',
            [
                {'name': 'class', 'value': 'title'},
                {'name': 'id', 'value': 'error-title'},
                {'name': 'string', 'value': 'File not found'}
            ])
        return invariant.check(dom)

    def __str__(self):
        return json.dumps({
            'name': 'file-not-found'
        })

    def __eq__(self, other):
        return type(self).__name__ == type(other).__name__
