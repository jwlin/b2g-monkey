#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup


class AbstractNormalizer():
    __metaclass__ = ABCMeta

    @abstractmethod
    def normalize(self, dom):
        pass


class AttributeNormalizer(AbstractNormalizer):
    def __init__(self, attr_list=None, mode='white_list'):
        self.attr_list = attr_list
        self.mode = mode

    def normalize(self, dom):
        soup = BeautifulSoup(dom, 'html.parser')
        for tag in soup.find_all():
            filtered_attrs = {}
            if self.mode == 'white_list':
                for attr in tag.attrs:
                    if self.attr_list and (attr in self.attr_list):
                        filtered_attrs[attr] = tag[attr]
            else:  # black_list
                for attr in tag.attrs:
                    if attr not in self.attr_list:
                        filtered_attrs[attr] = tag[attr]
            tag.attrs = filtered_attrs
        return str(soup)

    def __str__(self):
        return 'AttributeNormalizer: attr_list: %s, mode: %s' % (self.attr_list, self.mode)


class TagContentNormalizer(AbstractNormalizer):
    def __init__(self, tag_list=None):
        self.tag_list = tag_list

    def normalize(self, dom):
        soup = BeautifulSoup(dom, 'html.parser')
        for tag in soup.find_all():
            if self.tag_list and (tag.name in self.tag_list):
                tag.clear()
        return str(soup)

    def __str__(self):
        return 'TagContentNormalizer: tag_list: %s' % self.tag_list

class TagNormalizer(AbstractNormalizer):
    def __init__(self, tag_list=None):
        self.tag_list = tag_list

    def normalize(self, dom):
        soup = BeautifulSoup(dom, 'html.parser')
        for tag in soup.find_all():
            if self.tag_list and (tag.name in self.tag_list):
                tag.decompose()

        return str(soup)

    def __str__(self):
        return 'TagNormalizer: tag_list: %s' % self.tag_list

#=============================================================================================
# remove tag with:
# 1. matched name, attr and startswith value
# 2. matched name, and tag content contains value without given attr
class TagWithAttributeNormalizer(AbstractNormalizer):
    def __init__(self, name, attr, value, mode='startswith'):
        self.name = name
        self.attr = attr
        self.value = value
        self.mode = mode

    def normalize(self, dom):
        soup = BeautifulSoup(dom, 'html.parser')
        for tag in soup.find_all(self.name):
            if self.attr and tag.attrs and (self.attr in tag.attrs):
                if type(tag[self.attr]) == type([]):
                    for attr_value in tag[self.attr]:
                        if self.is_attr_value(attr_value):
                            tag.decompose()
                            break
                elif type(tag[self.attr]) == type('') or type(tag[self.attr]) == type(u'')  :
                    if self.is_attr_value(tag[self.attr]):
                        tag.decompose()

            elif not self.attr:  # self.attr is None
                for string in tag.stripped_strings:
                    if self.is_attr_value(string):
                        tag.decompose()
                        break
        return str(soup)

    def is_attr_value(self, attr_value):
        if self.mode == 'startswith':
            return attr_value.startswith(self.value)
        elif self.mode == 'contains':
            return self.value in attr_value
        elif self.mode == 'attribute':
            attrs = self.value.split(':')
            for attr in attrs:
                if not attr in attr_value:
                    return False
            return True
        else:
            return False

    def __str__(self):
        return 'TagWithAttributeNormalizer: tag: %s, attr: %s, value: %s' % (self.name, self.attr, self.value)
