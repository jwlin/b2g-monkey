#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import os, sys, json, posixpath, time, datetime
from os.path import relpath
from abc import ABCMeta

from dom_analyzer import DomAnalyzer
from clickable import Clickable, InputField, SelectField


class Configuration:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._invariants = []
        self._max_depth = 3
        self._max_states = 10
        self._max_time = 2000
        self._sleep_time = 2

    def set_max_depth(self, depth):
        self._max_depth = depth

    def get_max_depth(self):
        return self._max_depth

    def set_max_states(self, state_num):
        self._max_states = state_num

    def get_max_states(self):
        return self._max_states

    def set_max_time(self, time_in_second):
        self._max_time = time_in_second

    def get_max_time(self):
        return self._max_time

    def set_sleep_time(self, time_in_second):
        self._sleep_time = time_in_second

    def get_sleep_time(self):
        return self._sleep_time


class B2gConfiguration(Configuration):
    def __init__(self, app_name, app_id):
        super(B2gConfiguration, self).__init__()
        self._app_name = app_name
        self._app_id = app_id
        self._automata_fname = 'automata.json'
        self._root_path = os.path.join('trace', datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        self._file_path = {
            'root': self._root_path,
            'dom': os.path.join(self._root_path, 'dom'),
            'state': os.path.join(self._root_path, 'screenshot', 'state'),
            'clickable': os.path.join(self._root_path, 'screenshot', 'clickable'),
        }
        for key, value in self._file_path.iteritems():
            abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), value)
            if not os.path.exists(abs_path):
                os.makedirs(abs_path)

    def set_app_name(self, app_name):
        self._app_name = app_name

    def get_app_name(self):
        return self._app_name

    def set_app_id(self, app_id):
        self._app_id = app_id

    def get_app_id(self):
        return self._app_id

    def get_automata_fname(self):
        return self._automata_fname

    def get_abs_path(self, my_type):
        abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self._file_path[my_type])
        return abs_path

    def get_path(self, my_type):
        return self._file_path[my_type]


#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
class SeleniumConfiguration(Configuration):
    def __init__(self, browserID, url, dirname=None, folderpath=None ):
        super(SeleniumConfiguration, self).__init__()
        self._browserID = browserID
        self._url = url
        self._dirname = dirname
        self._folderpath = folderpath
        dirname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') if not dirname else dirname
        self._root_path = os.path.join('trace', dirname ) if not folderpath else os.path.join( folderpath, dirname )
        self._file_path = {
            'root': self._root_path,
            'dom': os.path.join(self._root_path, 'dom'),
            'state': os.path.join(self._root_path, 'screenshot', 'state'),
            'clickable': os.path.join(self._root_path, 'screenshot', 'clickable'),
        }
        for key, value in self._file_path.iteritems():
            abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), value)
            if not os.path.exists(abs_path):
                os.makedirs(abs_path)

        self._automata_fname = ''
        self._dom_inside_iframe = True
        self._domains = []
        self._scripts = []
        self._frame_tags = []

    def set_automata_fname(self, automata_fname):
        self._automata_fname = automata_fname

    def get_automata_fname(self):
        return self._automata_fname

    def get_abs_path(self, my_type):
        abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self._file_path[my_type])
        return abs_path

    def get_path(self, my_type):
        return self._file_path[my_type]

    #=============================================================================================
    #Diff: browser use url & browserID not app
    def set_browserID(self, app_name):
        self._browserID = browserID

    def get_browserID(self):
        return self._browserID

    def set_url(self, app_id):
        self._url = _url

    def get_url(self):
        return self._url

    def set_domains(self, domains):
        self._domains = domains

    def get_domains(self):
        return self._domains

    def set_clickable_tag(self, tag):
        DomAnalyzer.add_clickable_tag(tag)

    def set_inputs_tag(self, tag):
        DomAnalyzer.add_inputs_tag(tag)

    def set_path_ignore_tag(self, tag):
        DomAnalyzer.add_path_ignore_tag(tag)

    def set_path_ignore_tags(self, tag):
        DomAnalyzer.add_path_ignore_tags(tag)

    def set_normalizer(self, normalizer):
        DomAnalyzer.add_normalizer(normalizer)

    def set_simple_clickable_tags(self):
        DomAnalyzer.set_simple_clickable_tags()

    def set_simple_inputs_tags(self):
        DomAnalyzer.set_simple_inputs_tags()

    def set_simple_normalizers(self):
        DomAnalyzer.set_simple_normalizers()

    def set_dom_inside_iframe(self, is_inside):
        self._dom_inside_iframe = is_inside

    def is_dom_inside_iframe(self):
        return self._dom_inside_iframe

    def set_frame_tags(self, tag_list):
        self._frame_tags += tag_list

    def get_frame_tags(self):
        return self._frame_tags

    def get_before_script(self):
        return self._scripts

    def set_before_script(self, scripts):
        for edge in scripts:
            inputs = []
            for _input in edge['inputs']:
                inputs.append( InputField(_input['id'], _input['name'], _input['xpath'], _input['type'], _input['value']) )
            selects = []
            for _select in edge['selects']:
                selects.append( SelectField(_select['id'], _select['name'], _select['xpath'], _select['value']) )
            c = edge['clickable']
            clickable = Clickable(c['id'], c['name'], c['xpath'], c['tag'])
            self._scripts.append( ( inputs, selects, clickable, edge['iframe_list'] ) )

    def save_config(self, fname):
        config_data = {}
        config_data['max_depth'] = self._max_depth
        config_data['max_states'] = self._max_states
        config_data['max_time'] = self._max_time
        config_data['sleep_time'] = self._sleep_time
        #=============================================================================================
        #Diff: browser use url & browserID not app
        '''
        config_data['app_name'] = self.get_app_name()
        config_data['app_id'] = self.get_app_id()
        '''
        config_data['url'] = self._url
        config_data['browser_id'] = self._browserID
        config_data['dirname'] = self._dirname
        config_data['folderpath'] = self._folderpath
        #=============================================================================================
        config_data['automata_fname'] = self._automata_fname
        config_data['root_path'] = posixpath.join(
            posixpath.join(*(self.get_path('root').split(os.sep)))
        )
        config_data['dom_path'] = posixpath.join(
            posixpath.join(*(self.get_path('dom').split(os.sep)))
        )
        config_data['state_path'] = posixpath.join(
            posixpath.join(*(self.get_path('state').split(os.sep)))
        )
        config_data['clickable_path'] = posixpath.join(
            posixpath.join(*(self.get_path('clickable').split(os.sep)))
        )
        with open(os.path.join(self.get_abs_path('root'), fname), 'w') as f:
            json.dump(config_data, f, indent=2, sort_keys=True, ensure_ascii=False)
#==============================================================================================================================