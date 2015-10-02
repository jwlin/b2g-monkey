#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""
import random, string
from bs4 import BeautifulSoup
from clickable import Clickable, FormField, InputField
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
    ]
    _normalizers = [TagNormalizer(['head']), AttributeNormalizer()]
    serial_prefix = 'b2g-monkey-'
    _serial_num = 1  # used to dispatch id to clickables without id

    @classmethod
    def get_clickables(cls, dom):
        # todo: should compare the new dom with the old dom and just return clickables in the diff
        soup = BeautifulSoup(dom, 'html.parser')
        forms = soup.find_all('form')
        clickables = []

        # clickables with forms and inputs attached
        for form in forms:
            form_id = form.get('id')
            if not form_id:
                form_id = cls.serial_prefix + str(cls._serial_num)
                cls._serial_num += 1
            f = FormField(form_id, cls._get_xpath(form))
            input_types = ['text', 'email', 'password']
            for input_type in input_types:
                inputs = form.find_all('input', attrs={'type': input_type})
                for my_input in inputs:
                    data_set = InlineDataBank.get_data(input_type)
                    if data_set:
                        value = random.choice(list(data_set))
                    else:
                        value = ''.join(random.choice(string.lowercase) for i in xrange(8))
                    input_id = my_input.get('id')
                    if not input_id:
                        input_id = cls.serial_prefix + str(cls._serial_num)
                        cls._serial_num += 1
                    f.add_input(InputField(input_id, cls._get_xpath(my_input), input_type, value))
            for tag in cls._clickable_tags:
                if tag.get_attr():
                    for attr, value in tag.get_attr().items():
                        candidate_clickables = form.find_all(tag.get_name(), attrs={attr: value})
                else:
                    candidate_clickables = form.find_all(tag.get_name())
                for candidate_clickable in candidate_clickables:
                    #print candidate_clickable
                    clickable_id = candidate_clickable.get('id')
                    if not clickable_id:
                        clickable_id = cls.serial_prefix + str(cls._serial_num)
                        cls._serial_num += 1
                    c = Clickable(clickable_id, cls._get_xpath(candidate_clickable), tag.get_name())
                    c.add_form(f)
                    clickables.append(c)

        # other clickables
        for tag in cls._clickable_tags:
            if tag.get_attr():
                for attr, value in tag.get_attr().items():
                    candidate_clickables = soup.find_all(tag.get_name(), attrs={attr: value})
            else:
                candidate_clickables = soup.find_all(tag.get_name())
            for candidate_clickable in candidate_clickables:
                #print candidate_clickable
                if not cls._is_duplicate(clickables, candidate_clickable):
                    clickable_id = candidate_clickable.get('id')
                    if not clickable_id:
                        clickable_id = cls.serial_prefix + str(cls._serial_num)
                        cls._serial_num += 1
                    clickables.append(Clickable(clickable_id, cls._get_xpath(candidate_clickable), tag.get_name()))
        #print 'len', len(clickables)
        return clickables

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
        '''
        import difflib
        for i, s in enumerate(difflib.ndiff(dom1, dom2)):
            if s[0]==' ':
                continue
            elif s[0]=='-':
                print 'Delete "{}" from position {}'.format(s[-1],i)
            elif s[0]=='+':
                print 'Add "{}" to position {}'.format(s[-1],i)
        print
        return True
        '''

