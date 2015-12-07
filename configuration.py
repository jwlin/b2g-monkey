#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Configuration needed by controller to run
"""

import os
import time
import datetime
import json
import posixpath
import logging
import invariant
from abc import ABCMeta
from invariant import FileNotFoundInvariant

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Currently, max_states and max_time are not functioning
class Configuration:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._max_depth = 2
        self._max_states = 0
        self._max_time = 0
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
    def __init__(self, app_name, app_id, mkdir=True, fname=None):
        super(B2gConfiguration, self).__init__()
        if not fname:
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
            self._invariants = [FileNotFoundInvariant()]
        else:
            assert os.path.isfile(fname) and os.path.exists(fname)
            t_start = time.time()
            with open(fname) as f:
                data = json.load(f)
                self._app_name = data['app_name']
                self._app_id = data['app_id']
                self._max_depth = int(data['max_depth'])
                self._max_states = int(data['max_states'])
                self._sleep_time = int(data['sleep_time'])
                self._max_time = int(data['max_time'])
                self._automata_fname = data['automata_fname']
                self._file_path = {
                    'root': os.path.join(*(data['root_path'].split('/'))),
                    'dom': os.path.join(*(data['dom_path'].split('/'))),
                    'state': os.path.join(*(data['state_path'].split('/'))),
                    'clickable': os.path.join(*(data['clickable_path'].split('/')))
                }
                self._invariants = []
                for inv in data['invariants']:
                    if inv['name'] == 'string':
                        self._invariants.append(invariant.StringInvariant(inv['str']))
                    elif inv['name'] == 'tag':
                        tag_name = inv['tag']
                        attr = inv['attr']
                        self._invariants.append(invariant.TagInvariant(tag_name, attr))
                    elif inv['name'] == 'file-not-found':
                        self._invariants.append(invariant.FileNotFoundInvariant())
            logger.info('config loaded. loading time: %f sec', time.time() - t_start)
            mkdir = False
        if mkdir:
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

    def set_automata_fname(self, fname):
        self._automata_fname = fname

    def get_abs_path(self, my_type):
        abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self._file_path[my_type])
        return abs_path

    def get_path(self, my_type):
        return self._file_path[my_type]

    def set_path(self, my_type, fpath):
        self._file_path[my_type] = os.path.join(*(fpath.split('/')))  # separate dirs with unix splitter

    def add_invariant(self, invariant):
        if invariant not in self._invariants:
            self._invariants.append(invariant)

    def remove_invariant(self, invariant):
        if invariant in self._invariants:
            self._invariants.remove(invariant)

    def get_invariants(self):
        return self._invariants

    def save(self, fname):
        inv_data = []
        for inv in self._invariants:
            inv_dict = inv.get_value()
            if inv_dict['name'] == 'string':
                inv_data.append({
                    'name': 'string',
                    'str': inv_dict['str']
                })
            elif inv_dict['name'] == 'tag':
                inv_data.append({
                    'name': 'tag',
                    'tag': inv_dict['tag'],
                    'attr': inv_dict['attr']
                })
            elif inv_dict['name'] == 'file-not-found':
                inv_data.append({
                    'name': 'file-not-found'
                })
        config_data = {
            'max_depth': self._max_depth,
            'max_states':  self._max_states,
            'max_time': self._max_time,
            'sleep_time': self._sleep_time,
            'app_name': self._app_name,
            'app_id': self._app_id,
            'automata_fname': self._automata_fname,
            'root_path': posixpath.join(*(self._file_path['root'].split(os.sep))),
            'dom_path': posixpath.join(*(self._file_path['dom'].split(os.sep))),
            'state_path': posixpath.join(*(self._file_path['state'].split(os.sep))),
            'clickable_path': posixpath.join(*(self._file_path['clickable'].split(os.sep))),
            'invariants': inv_data
        }
        with open(os.path.join(self._file_path['root'], fname), 'w') as f:
            json.dump(config_data, f, indent=2, sort_keys=True, ensure_ascii=False)

