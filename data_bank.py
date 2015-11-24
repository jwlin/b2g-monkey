#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Databank
"""

from abc import ABCMeta, abstractmethod


class DataBank():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_types(self):
        """IMPORTANT: this is class method, override it with @classmethod!"""
        pass

    @abstractmethod
    def get_data(self, data_type):
        """IMPORTANT: this is class method, override it with @classmethod!"""
        pass

    @abstractmethod
    def add_item(self, data_type, value):
        """IMPORTANT: this is class method, override it with @classmethod!"""
        pass

    @abstractmethod
    def remove_item(self, data_type, value):
        """IMPORTANT: this is class method, override it with @classmethod!"""
        pass


class InlineDataBank(DataBank):
    # data is a list of types and the corresponding input data (set)
    data = {
        'username': {'user1', 'user2'},
        'password': {'P@ssw0rd', '!qaz2wsX'},
        'email': {'user1@example.com', 'user2@mailhost.com'},
    }

    @classmethod
    def get_types(cls):
        return cls.data.keys()

    @classmethod
    def get_data(cls, data_type):
        if data_type in cls.data.keys():
            return cls.data[data_type]
        else:
            return None

    @classmethod
    def add_item(cls, data_type, value):
        if data_type in cls.data.keys():
            cls.data[data_type].add(value)
        else:
            cls.data[data_type] = {value}

    @classmethod
    def remove_item(cls, data_type, value):
        if data_type in cls.data.keys():
            cls.data[data_type].discard(value)
