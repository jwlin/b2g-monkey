#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""
import random, string, re
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
    _path_ignore_tags = []

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
        cs_candidate_clickables_iframe = cs.get_all_candidate_clickables()
        prev_candidate_clickables_iframe = prev_s.get_all_candidate_clickables() if prev_s else None
        clickables_iframe_list = []

        for cs_candidate_clickables, iframe_path_list in cs_candidate_clickables_iframe:
            #find prev_candidate_clickables if prev_s exists and iframe_path_list same
            prev_candidate_clickables = None
            clickables = []
            if prev_candidate_clickables_iframe:
                for prev_c, prev_i in prev_candidate_clickables_iframe:
                    if iframe_path_list == prev_i:
                        prev_candidate_clickables = prev_c
                        break
            for candidate_clickable, clickable_xpath in cs_candidate_clickables:
                #find if candidate_clickable is same in prev
                if not cls._is_same_soup_in_prev( prev_candidate_clickables, candidate_clickable, clickable_xpath ) \
                        and not cls._is_duplicate(clickables, candidate_clickable):
                    clickable_id = cls.make_id( candidate_clickable.get('id') if candidate_clickable.has_attr('id') else None  )
                    clickable_name = cls.make_id( candidate_clickable.get('name') if candidate_clickable.has_attr('name') else None )
                    clickable_xpath = cls._get_xpath(candidate_clickable)
                    clickable_tag = candidate_clickable.name
                    clickables.append( Clickable(clickable_id, clickable_name, clickable_xpath, clickable_tag) )
            clickables_iframe_list.append( (clickables, iframe_path_list) )
        return clickables_iframe_list
    #=============================================================================================

    #=============================================================================================
    #Diff: clickables, inputs, selects information save in state
    @classmethod
    def get_candidate_clickables_soup(cls, dom):
        clickables = []
        candidate_clickables = []
        soup = BeautifulSoup(dom, 'html.parser')
        soup = cls.soup_visible(soup)
        for tag in cls._clickable_tags:
            if tag.get_attr():
                for attr, value in tag.get_attr().items():
                    candidate_clickables += soup.find_all(tag.get_name(), attrs={attr: value})
            else:
                candidate_clickables += soup.find_all(tag.get_name())
        #find other element with onclick
        for find_onclick in soup.find_all():
            if find_onclick.has_attr('onclick') and not find_onclick in candidate_clickables:
                candidate_clickables.append(find_onclick)
        for candidate_clickable in candidate_clickables:
            clickables.append( (candidate_clickable, cls._get_xpath(candidate_clickable)) )
        return clickables

    @classmethod
    def get_inputs(cls, dom):
        # add inputs in dom
        soup = BeautifulSoup(dom, 'html.parser')
        soup = cls.soup_visible(soup)
        inputs_list = []
        for input_type in cls._input_types:
            inputs = soup.find_all('input', attrs={'type': input_type})
            for my_input in inputs:
                if my_input.has_attr('id'):
                    data_set = InlineDataBank.get_data(input_type, my_input['id']) 
                elif my_input.has_attr('name'):
                    data_set = InlineDataBank.get_data(input_type, my_input['name']) 
                else:
                    data_set = InlineDataBank.get_data(input_type, None)

                if data_set:
                    value = random.choice(list(data_set))
                else:
                    value = ''.join(random.choice(string.lowercase) for i in xrange(8))
                input_id = cls.make_id( my_input.get('id') )
                input_name = cls.make_id( my_input.get('name') if my_input.has_attr('name') else None )
                inputs_list.append( InputField(input_id, input_name, cls._get_xpath(my_input), input_type, value))
        return inputs_list

    @classmethod
    def get_selects(cls, dom):
        soup = BeautifulSoup(dom, 'html.parser')
        soup = cls.soup_visible(soup)
        selects_list = []
        selects = soup.find_all('select')
        for my_select in selects:
            '''TODO: make select value'''
            if my_select.has_attr('id'):
                data_set = InlineDataBank.get_data('select', my_select['id']) 
            elif my_select.has_attr('name'):
                data_set = InlineDataBank.get_data('select', my_select['name'])                    
            else:
                data_set = InlineDataBank.get_data('select', None)

            option_num = len( my_select.find_all('option') )
            if data_set:
                value = random.choice(list(data_set))
                value = min(max(0, value), option_num)
            else:
                value =  min(max(3, option_num/2), option_num)
            select_id = cls.make_id( my_select.get('id') )
            select_name = cls.make_id( my_select.get('name') if my_select.has_attr('name') else None )
            selects_list.append(SelectField(select_id, select_name, cls._get_xpath(my_select), value))
        return selects_list

    @classmethod
    def get_radios(cls, dom):
        soup = BeautifulSoup(dom, 'html.parser')
        soup = cls.soup_visible(soup)
        radios_dict = { 'default': {} }
        radios = soup.find_all('input',{'type' : 'radio'})
        for radio in radios:
            if radio.has_attr('name'):
                pass
            elif radio['name'] in radios_dict.keys():
                radios_dict[ radio['name'] ]
            radio_id = cls.make_id( radio.get('id') )
            radios_list.append(RadioField(radio_id, cls._get_xpath(radio), value))
        return selects_list
        pass

    @classmethod
    def get_checkboxes(cls, dom):
        pass

    @classmethod
    def soup_visible(cls, soup):
        for invisible_tag in ['style', 'script', '[document]', 'head', 'title']:
            for tag in soup.find_all(invisible_tag):
                tag.decompose()
        for element in soup.find_all():
            if element.attrs and element.has_attr('style') and 'display:' in element['style'] and 'none' in element['style']:
                if element.name in cls._clickable_tags or element.name == 'input' or element.name == 'select':
                    element.decompose()
                else:
                    element.clear()
        return soup
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
            elif  parent.name in cls._path_ignore_tags:
                continue
            path.insert(0, cls._get_node(parent))
        return '//html/body/' + '/'.join(path)

    @classmethod
    def _is_same_soup_in_prev(cls, prev_clickables, candidate_clickable, candidate_xpath):
        if not prev_clickables:
            return False
        for prev_clickable, prev_xpath in prev_clickables:
            if candidate_xpath == prev_xpath and candidate_clickable == prev_clickable:
                return True
        return False

    @classmethod
    def _is_duplicate(cls, clickables, candidate_clickable):
        for c in clickables:
            if candidate_clickable.has_attr('id') and candidate_clickable.get('id') == c.get_id():
                return True
            elif cls._get_xpath(candidate_clickable) == c.get_xpath():
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
    #Diff: set config of clickable, inputs, normalizer, ignoreTages
    @classmethod
    def add_path_ignore_tag(cls, tag):
        cls._path_ignore_tags.append(tag)

    @classmethod
    def add_path_ignore_tags(cls, tag_list):
        cls._path_ignore_tags += tag_list

    @classmethod
    def add_normalizer(cls, normalizer):
        cls._normalizers.append(normalizer)

    @classmethod
    def add_clickable_tag(cls, Tag):
        cls._clickable_tags.append(Tag)

    @classmethod
    def add_inputs_tag(cls, tag):
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
        cls._normalizers.append( AttributeNormalizer(['class']) )
        cls._normalizers.append( TagWithAttributeNormalizer(None, "style", "display:none;", 'contains') )
        cls._normalizers.append( TagWithAttributeNormalizer("input", "type", "hidden") )
    #=============================================================================================