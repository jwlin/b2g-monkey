#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""
import random, string, re
from bs4 import BeautifulSoup
from clickable import Clickable, InputField, SelectField, Checkbox, CheckboxField, Radio, RadioField
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
    _attribute_normalizers = []
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
        cs_candidate_clickables_dict = cs.get_all_candidate_clickables()
        prev_candidate_clickables_dict = prev_s.get_all_candidate_clickables() if prev_s else None
        clickables_iframe_list = []

        for iframe_path_key in cs_candidate_clickables_dict.keys():
            #find prev_candidate_clickables if prev_s exists and iframe_path_list same
            cs_candidate_clickables = cs_candidate_clickables_dict[iframe_path_key]
            prev_candidate_clickables = None
            clickables = []
            if prev_candidate_clickables_dict:
                for prev_i in prev_candidate_clickables_dict.keys():
                    if iframe_path_key == prev_i:
                        prev_candidate_clickables = prev_candidate_clickables_dict[prev_i]
                        break
            for candidate_clickable, clickable_xpath in cs_candidate_clickables:
                #find if candidate_clickable is same in prev
                if not cls._is_same_soup_in_prev( prev_candidate_clickables, candidate_clickable, clickable_xpath ) \
                        and not cls._is_duplicate(clickables, candidate_clickable):
                    clickable_id = cls.make_id( candidate_clickable.get('id') if candidate_clickable.has_attr('id') else None  )
                    clickable_name = candidate_clickable.get('name') if candidate_clickable.has_attr('name') else clickable_id
                    clickable_xpath = cls._get_xpath(candidate_clickable)
                    clickable_tag = candidate_clickable.name
                    clickables.append( Clickable(clickable_id, clickable_name, clickable_xpath, clickable_tag) )
            clickables_iframe_list.append( (clickables, iframe_path_key) )
        return clickables_iframe_list
    #=============================================================================================

    #=============================================================================================
    #Diff: clickables, inputs, selects information save in state
    @classmethod
    def get_candidate_clickables_soup(cls, dom):
        clickables = []
        candidate_clickables = []
        soup = BeautifulSoup(dom, 'html5lib')
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
        soup = BeautifulSoup(dom, 'html5lib')
        soup = cls.soup_visible(soup)
        inputs_list = []
        for input_type in cls._input_types:
            inputs = soup.find_all('input', attrs={'type': input_type})
            for my_input in inputs:
                input_id = cls.make_id( my_input.get('id') )
                input_name = my_input.get('name') if my_input.has_attr('name') else input_id
                inputs_list.append( InputField(input_id, input_name, cls._get_xpath(my_input), input_type))
        return inputs_list

    @classmethod
    def get_selects(cls, dom):
        soup = BeautifulSoup(dom, 'html5lib')
        soup = cls.soup_visible(soup)
        selects_list = []
        for my_select in soup.find_all('select'):
            select_id = cls.make_id( my_select.get('id') )
            select_name = my_select.get('name') if my_select.has_attr('name') else select_id
            select_value = []
            for option in my_select.find_all('option'):
                select_value.append( option.get('value') ) if option.has_attr('value') else ''
            selects_list.append(SelectField(select_id, select_name, cls._get_xpath(my_select), select_value) )
        return selects_list

    @classmethod
    def get_radios(cls, dom):
        soup = BeautifulSoup(dom, 'html5lib')
        soup = cls.soup_visible(soup)
        #group radio by name
        radio_dict = {}
        radio_field_list = []
        for my_radio in soup.find_all('input',{'type' : 'radio'}):
            radio_id = cls.make_id( my_radio.get('id') )
            radio_name = my_radio.get('name') if my_radio.has_attr('name') \
                        else cls.make_id(None) if my_radio.has_attr('id') else radio_id
            radio_value = my_radio.get('value') if my_radio.has_attr('value') else ''
            radio =  Radio( radio_id, radio_name, cls._get_xpath(my_radio), radio_value )
            if radio_name in radio_dict.keys():
                radio_dict[ radio_name ].append(radio)
            else:
                radio_dict[ radio_name ] = [radio]
        for radio_name_key in radio_dict.keys():
            radio_field_list.append( RadioField(radio_dict[radio_name_key], radio_name_key ) )
        return radio_field_list

    @classmethod
    def get_checkboxes(cls, dom):
        soup = BeautifulSoup(dom, 'html5lib')
        soup = cls.soup_visible(soup)
        #group radio by name
        checkbox_dict = {}
        checkbox_field_list = []
        for my_checkbox in soup.find_all('input',{'type' : 'checkbox'}):
            checkbox_id = cls.make_id( my_checkbox.get('id') )
            checkbox_name = my_checkbox.get('name') if my_checkbox.has_attr('name') \
                            else cls.make_id(None) if my_checkbox.has_attr('id') else checkbox_id 
            checkbox_value = my_checkbox.get('value') if my_checkbox.has_attr('value') else ''
            checkbox =  Checkbox( checkbox_id, checkbox_name, cls._get_xpath(my_checkbox), checkbox_value )
            if checkbox_name in checkbox_dict.keys():
                checkbox_dict[ checkbox_name ].append(checkbox)
            else:
                checkbox_dict[ checkbox_name ] = [checkbox]
        for checkbox_name_key in checkbox_dict.keys():
            checkbox_field_list.append( CheckboxField(checkbox_dict[checkbox_name_key], checkbox_name_key) )
        return checkbox_field_list
        
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
        for attr_normalizer in cls._attribute_normalizers:
            dom = attr_normalizer.normalize(dom)
        return dom

    @classmethod
    def is_normalize_equal(cls, dom1, dom2):
        return dom1 == dom2
    #=============================================================================================

    #=============================================================================================
    #Diff: set config of clickable, inputs, normalizer, ignoreTages

    @classmethod
    def add_tags_normalizer(cls, tags):
        cls._normalizers.append( TagNormalizer(tags) )

    @classmethod
    def add_attributes_normalizer(cls, attrs):
        cls._normalizers.append( AttributeNormalizer(attrs) )

    @classmethod
    def add_tag_with_attribute_normalizer(cls, tag_name, attr, value, mode):
        if mode:
            cls._normalizers.append( TagWithAttributeNormalizer( tag_name, attr, value, mode ) )
        else:
            cls._normalizers.append( TagWithAttributeNormalizer( tag_name, attr, value ) )

    @classmethod
    def add_clickable_tag(cls, tag_name, attr, value):
        tag = Tag(tag_name, {attr:value}) if attr else Tag(tag_name)
        cls._clickable_tags.append(tag)

    @classmethod
    def add_inputs_tag(cls, tag):
        cls._input_types.append(tag)

    @classmethod
    def set_simple_clickable_tags(cls):
        cls._clickable_tags.append( Tag('a') )
        cls._clickable_tags.append( Tag('li') )
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
        cls._normalizers.append( TagNormalizer(['head', 'canvas']) )
        cls._normalizers.append( TagWithAttributeNormalizer(None, "style", "display:none;", 'contains') )
        cls._normalizers.append( TagWithAttributeNormalizer("input", "type", "hidden") )
        cls._attribute_normalizers.append( AttributeNormalizer(['class']) )
    #=============================================================================================