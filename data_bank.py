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
        "text":
        {            
            'username': {'user1', 'user2'},
            'password': {'j6j6fu3fu3mp3mp3'},
            'email': {'user1@example.com', 'user2@mailhost.com'},
            'name': {'Ann', 'Bob'},
            'address':{'abc street'},
            'telephone':{'0912345678'},
            'mail':{'louis@gmail.com'},
            'year':{'1999', '2015'},
            'degree2':{'true'},
            'interest':{'true'},
            'city':{'2', '3'},
            'job1':{'1', '3'},
            'uid': {'louisalflame@hotmail.com.tw'},
            'textfield2':{'0911233456'}, #name=tel
            'personal_name':{'Louis','Alice'} ,
            'id': {'1234'}
        },
        "password":
        {
            'password': {'j6j6fu3fu3mp3mp3'}
        },
        "email":
        {          
            'email': {'user1@example.com', 'user2@mailhost.com'}
        },
        "select":
        {
            'city':{2, 3},
            'job1':{1, 3},
            'dist_cd': {0},
            'd_birthday': {70, 80},
            'city_cd': {12, 13},
            'doc_cd': {0}            
        }
    }

    @classmethod
    def get_types(cls):
        return cls.data.keys()

    @classmethod
    def get_data(cls, input_type, data_id):
        if input_type in cls.data.keys():
            if data_id and data_id in cls.data[input_type].keys():
                return cls.data[input_type][data_id]
            else:
                return None
        else:
            return None

    @classmethod
    def add_item(cls, input_type, data_id, value):
        if input_type in cls.data.keys():
            if data_id in cls.data[input_type].keys():
                cls.data[input_type][data_id].add(value)
            else:
                cls.data[input_type] = {}
                cls.data[input_type][data_id] = {value}
        else:
            cls.data[input_type] = {}
            cls.data[input_type][data_id] = {value}


    @classmethod
    def remove_item(cls, input_type, data_id, value):
        if input_type in cls.data.keys():
            if data_id in cls.data[input_type].keys():
                cls.data[input_type][data_id].discard(value)

