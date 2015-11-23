#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""
import random, string
from bs4 import BeautifulSoup
from clickable import Clickable, InputField, SelectField
from data_bank import InlineDataBank
from normalizer import AttributeNormalizer, TagNormalizer, TagWithAttributeNormalizer


class Tag:
    def __init__(self, name, attr=None):
        self.__name = name
        self.__attr = attr

    def get_name(self):
        return self.__name

    def get_attr(self):
        return self.__attr


class DomAnalyzer:
    _clickable_tags = []
    _input_types = []  # type of input fields filled with values
    _normalizers = []
    serial_prefix = 'b2g-monkey-'
    _serial_num = 1  # used to dispatch id to clickables without id

    #=============================================================================================
    @classmethod
    def make_id(cls, _id):
        if not _id:
            _id = cls.serial_prefix + str(cls._serial_num)
            cls._serial_num += 1
        return _id

    #Diff: inputs information save in state, indiviual to clickables
    @classmethod
    def get_clickables(cls, cs, prev_s=None):
        # only return newly discovered clickables, i.e. clickables not in prev_clickables
        cs_dom_list = cs.get_dom_list()
        prev_dom_list = prev_s.get_dom_list() if prev_s else None
        clickables_iframe_list = []

        for i in xrange(len(cs_dom_list)):
            stateDom = cs_dom_list[i]
            prev_stateDom = prev_dom_list[i] if prev_s and prev_dom_list and len(prev_dom_list)>i else None
            prev_clickables = []
            clickables = []

            # if same iframe_path_list => ignore clickables in prev_state
            if prev_stateDom and prev_stateDom.get_iframe_path_list() == stateDom.get_iframe_path_list():
                prev_dom = prev_stateDom.get_dom()
                prev_soup = BeautifulSoup(prev_dom, 'html.parser')
                for tag in cls._clickable_tags:
                    if tag.get_attr():
                        for attr, value in tag.get_attr().items():
                            prev_clickables += prev_soup.find_all(tag.get_name(), attrs={attr: value})
                    else:
                        prev_clickables += prev_soup.find_all(tag.get_name())

            dom = stateDom.get_dom()
            soup = BeautifulSoup(dom, 'html.parser')
            for tag in cls._clickable_tags:
                if tag.get_attr():
                    for attr, value in tag.get_attr().items():
                        candidate_clickables = soup.find_all(tag.get_name(), attrs={attr: value})
                else:
                    candidate_clickables = soup.find_all(tag.get_name())
                for candidate_clickable in candidate_clickables:
                    is_appear_in_prev = False
                    for prev_clickable in prev_clickables:
                        if candidate_clickable == prev_clickable and cls._get_xpath(candidate_clickable) == cls._get_xpath(prev_clickable):                         
                            is_appear_in_prev = True
                            break
                    if not is_appear_in_prev and not cls._is_duplicate(clickables, candidate_clickable):
                        clickable_id = cls.make_id( candidate_clickable.get('id') )
                        clickables.append(Clickable(clickable_id, cls._get_xpath(candidate_clickable), tag.get_name()))

            clickables_iframe_list.append( (clickables, stateDom.get_iframe_path_list()) )
        return clickables_iframe_list
    #=============================================================================================

    #=============================================================================================
    #Diff: inputs information save in state, indiviual to clickables
    @classmethod
    def get_inputs(cls, dom):
        # add inputs in dom
        soup = BeautifulSoup(dom, 'html.parser')
        inputs_list = []
        for input_type in cls._input_types:
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
                inputs_list.append( InputField(input_id, cls._get_xpath(my_input), input_type, value))
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

    #=============================================================================================
    #Diff: normalize dom 
    @classmethod
    def normalize(cls, dom):
        for normalizer in cls._normalizers:
            dom = normalizer.normalize(dom)
        return dom

    @classmethod
    def is_normalize_equal(cls, dom1, dom2):
        return dom1 == dom2
    #=============================================================================================

    #=============================================================================================
    #Diff: set config of clickable, inputs, normalizer
    @classmethod
    def add_normalizer(cls, normalizer):
        cls._normalizers.append(normalizer)

    @classmethod
    def add_clickable_tags(cls, Tag):
        cls._clickable_tags.append(Tag)

    @classmethod
    def add_inputs_tags(cls, tag):
        cls._input_types.append(tag)

    @classmethod
    def set_simple_clickable_tags(cls):
        cls._clickable_tags.append( Tag('a') )
        cls._clickable_tags.append( Tag('button') )
        cls._clickable_tags.append( Tag('input', {'type': 'submit'}) )
        cls._clickable_tags.append( Tag('input', {'type': 'button'}) )

    @classmethod
    def set_simple_inputs_tags(cls):
        cls._input_types.append('text')
        cls._input_types.append('email')
        cls._input_types.append('password')

    @classmethod
    def set_simple_normalizers(cls):
        cls._normalizers.append( TagNormalizer(['head', 'canvas', 'li']) )
        cls._normalizers.append( AttributeNormalizer('class') )
    #=============================================================================================