#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
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
        'password': {'j6j6fu3fu3mp3mp3'},
        'email': {'user1@example.com', 'user2@mailhost.com'},
        'name': {'Ann', 'Bob'},
        'address':{'abc street'},
        'telephone':{'0912345678'},
        'mail':{'louis@gmail.com'},
        'year':{'1999', '2015'},
        'city':{'2', '3'},
        'job1':{'1', '3'},
        'degree2':{'true'},
        'interest':{'true'},
        'uid': {'louisalflame@hotmail.com.tw'},
        'textfield2':{'0911233456'}, #name=tel
        'personal_name':{'Louis','Alice'}        
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
