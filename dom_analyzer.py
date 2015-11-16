#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""
import random, string
from bs4 import BeautifulSoup
from clickable import Clickable, InputField, SelectField
from data_bank import InlineDataBank
from normalizer import AttributeNormalizer, TagNormalizer


class Tag:
    def __init__(self, name, attr=None):
        self.__name = name
        self.__attr = attr

    def get_name(self):
        return self.__name

    def get_attr(self):
        return self.__attr


class DomAnalyzer:
    _clickable_tags = [
        Tag('a'),
        Tag('button'),
        Tag('input', {'type': 'submit'}),
        Tag('input', {'type': 'button'})
    ]
    input_types = ['text', 'email', 'password']  # type of input fields filled with values
    _normalizers = [TagNormalizer(['head', 'canvas', 'li']), AttributeNormalizer('class')]
    serial_prefix = 'b2g-monkey-'
    _serial_num = 1  # used to dispatch id to clickables without id

    @classmethod
    def make_id(cls, _id):
        if not _id:
            _id = cls.serial_prefix + str(cls._serial_num)
            cls._serial_num += 1
        return _id

    #=============================================================================================
    #Diff: inputs information save in state, indiviual to clickbles
    @classmethod
    def get_clickables(cls, dom, prev_dom=None):
        # only return newly discovered clickables, i.e. clickables not in prev_clickables
        prev_clickables = []
        if prev_dom:
            prev_soup = BeautifulSoup(prev_dom, 'html.parser')
            for tag in cls._clickable_tags:
                if tag.get_attr():
                    for attr, value in tag.get_attr().items():
                        prev_clickables += prev_soup.find_all(tag.get_name(), attrs={attr: value})
                else:
                    prev_clickables += prev_soup.find_all(tag.get_name())

        soup = BeautifulSoup(dom, 'html.parser')
        clickables = []
        
        for tag in cls._clickable_tags:
            if tag.get_attr():
                for attr, value in tag.get_attr().items():
                    candidate_clickables = soup.find_all(tag.get_name(), attrs={attr: value})
            else:
                candidate_clickables = soup.find_all(tag.get_name())
            for candidate_clickable in candidate_clickables:
                if candidate_clickable in prev_clickables:   
                    continue
                if not cls._is_duplicate(clickables, candidate_clickable):
                    clickable_id = cls.make_id( candidate_clickable.get('id') )
                    clickables.append(Clickable(clickable_id, cls._get_xpath(candidate_clickable), tag.get_name()))
        return clickables
    #=============================================================================================

    #=============================================================================================
    #Diff: inputs information save in state, indiviual to clickbles
    @classmethod
    def get_inputs(cls, dom):
        # add inputs in dom
        soup = BeautifulSoup(dom, 'html.parser')
        inputs_list = []
        for input_type in cls.input_types:
            inputs = soup.find_all('input', attrs={'type': input_type})
            for my_input in inputs:
                if input_type == "text" and my_input.has_attr('id'):
                    data_set = InlineDataBank.get_data(my_input['id'])
                else:
                    data_set = InlineDataBank.get_data(input_type)

                if data_set:
                    value = random.choice(list(data_set))
                else:
                    value = ''.join(random.choice(string.lowercase) for i in xrange(8))
                input_id = cls.make_id( my_input.get('id') )
                inputs_list.append(InputField(input_id, cls._get_xpath(my_input), input_type, value))
        return inputs_list

    @classmethod
    def get_selects(cls, dom):
        # add selects in dom
        soup = BeautifulSoup(dom, 'html.parser')
        selects_list = []
        selects = soup.find_all('select')
        for my_select in selects:
            '''TODO: make select value'''
            value = 1
            select_id = cls.make_id( my_select.get('id') )
            selects_list.append(SelectField(select_id, cls._get_xpath(my_select), value))
        return selects_list
    #=============================================================================================

    @classmethod
    def _get_node(cls, node):
        # for XPATH we only count for nodes with same type
        l = len(node.find_previous_siblings(node.name)) + 1
        return '%s[%s]' % (node.name, l)

    @classmethod
    def _get_xpath(cls, node):
        path = [cls._get_node(node)]
        for parent in node.parents:
            if parent.name == 'body':
                break
            path.insert(0, cls._get_node(parent))
        return '//html/body/' + '/'.join(path)

    @classmethod
    def _is_duplicate(cls, clickables, candidate_clickable):
        if candidate_clickable.get('id'):
            for c in clickables:
                if candidate_clickable.get('id') == c.get_id():
                    return True
        else:
            for c in clickables:
                if cls._get_xpath(candidate_clickable) == c.get_xpath():
                    return True
        return False

    @classmethod
    def is_equal(cls, dom1, dom2):
        for normalizer in cls._normalizers:
            dom1 = normalizer.normalize(dom1)
            dom2 = normalizer.normalize(dom2)

        if dom1 == dom2:
            return True
        else:
            return False

    @classmethod
    def normalize(cls, dom):
        for normalizer in cls._normalizers:
            dom = normalizer.normalize(dom)
        return dom

    @classmethod
    def is_normalize_equal(cls, dom1, dom2):
        return dom1 == dom2