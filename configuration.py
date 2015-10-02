#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import os, datetime
from abc import ABCMeta


class Configuration:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._invariants = []
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
    def __init__(self, app_name, app_id):
        super(B2gConfiguration, self).__init__()
        self._app_name = app_name
        self._app_id = app_id
        self._file_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'trace',
            datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        )
        if not os.path.exists(self._file_dir):
            os.makedirs(self._file_dir)

    def set_app_name(self, app_name):
        self._app_name = app_name

    def get_app_name(self):
        return self._app_name

    def set_app_id(self, app_id):
        self._app_id = app_id

    def get_app_id(self):
        return self._app_id

    def get_file_dir(self):
        return self._file_dir
