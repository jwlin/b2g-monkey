#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Invariants, a.k.a. rules to verify on each encountered page
"""

from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup


class Invariant:
    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self, dom):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def set(self, obj):
        pass


class StringInvariant(Invariant):
    def __init__(self, str_value):
        self._str_value = str_value

    def get(self):
        return self._str_value

    def set(self, str_value):
        self._str_value = str_value

    def check(self, dom):
        return self._str_value in dom

    def __str__(self):
        return 'StringInvariant:', self._str_value


class TagInvariant(Invariant):
    def __init__(self, tag_name, attr_list=None):
        self._tag_name = tag_name
        # e.g. [ {'name': 'class', 'value': 'title'},
        #        {'name': 'class', 'value': 'hide'},
        #        {'name': 'id', 'value': 'error-title'} ]
        self._tag_attr = attr_list

    def get(self):
        return self._tag_name, self._tag_attr

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
        return 'TagInvariant:', self._tag_name, ', '.join(str(self._tag_attr))


# FileNotFoundInvariant is a special case of TagInvariant
# <h1 class="title" id="error-title" data-l10n-id="file-not-found">File not found</h1>
class FileNotFoundInvariant(Invariant):
    def __init__(self):
        pass

    def get(self):
        pass

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
        return 'FileNotFoundInvariant'
