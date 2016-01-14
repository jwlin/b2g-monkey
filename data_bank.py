#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

from abc import ABCMeta, abstractmethod
from connecter import mysqlConnect

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
            'degree2':{'true'},
            'interest':{'true'},
            'job1':{'1', '3'},
            #ups.moe.edu
            'uid': {'louisalflame@hotmail.com.tw'},
            'textfield2':{'0911233456'}, #name=tel
            'personal_name':{'Louis','Alice'} ,
            'id': {'1234'},
            #jibako
            'user_user_profile_attributes_name':{'louis'},
            #member.cht.com.tw
            'birthday':{'2000/10/22', '2000/11/22'},
            #www.cloudopenlab.org.tw
            'chnlastname':{'wu', 'wang', 'lin', 'li'},
            'chnname':{'Cindy', 'Duck', 'Ellen'},
            'engname':{'Ann', 'Bob'},
            'companyname':{'bl618', },
            'phone':{'1234567','000000'},
            'applynote':{'***','<!---->'},
        },
        "password":
        {
            'password': {'j6j6fu3fu3mp3mp3'},
            #jibako
            'user_password':{'j6j6fu3fu3mp3mp3'},
            'user_password_confirmation':{'j6j6fu3fu3mp3mp3'},
            #member.cht.com.tw
            'password1':{'1apple2bee'},
            'password2':{'1apple2bee'}
        },
        "email":
        {          
            'email': {'user1@example.com', 'user2@mailhost.com'},
            #jibako
            'user_email':{'taadoopswow@gmail.com','bluehouseeverywhere@yahoo.com.tw'},
        },
        "select":
        {
            'city':{'2', '3'},
            'year':{'3', '5'},
            'job1':{'1', '3'},
            #ups.moe.edu
            'dist_cd': {'0'},
            'd_birthday': {'70', '80'},
            'city_cd': {'12', '13'},
            'doc_cd': {'0'},
            #member.cht.com.tw
            'gender':{'1','2'},
            #www.cloudopenlab.org.tw
            'industry':{'13','16','23'},
        },
        "radio":{
            'job':{'0','1','2'},
            'degree':{'0','1','2'}
        },
        "checkbox":{
            'interest':{'0/1/2','0/2/3','1/2/3'},
            'agreement':{'True'},
            'private_date1':{'True'},
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

#=============================================================================================================
# Get data set from mysqldb
#=============================================================================================================
class MysqlDataBank(DataBank):
    _connect = mysqlConnect("localhost", "jeff", "zj4bj3jo37788", "test")

    @classmethod
    def get_types(cls):
        pass

    @classmethod
    def add_item(cls, data_type, value):
        pass

    @classmethod
    def remove_item(cls, data_type, value):
        pass

    @classmethod
    def get_websubmit(cls, web_submit_id):        
        url, deep, time = cls._connect.get_submit_by_id(web_submit_id)
        web_inputs = cls._connect.get_all_inputs_by_id(web_submit_id)
        return url, deep, time

    @classmethod
    def get_data(cls, data_type, data_id, mutation):
        data_name = ''
        columns = cls._connect.get_all_column_names('databank_'+data_type)
        # col[0], col[1] are uni, mode
        columns = columns[2:]
        for method in [cls.find_similar_equal_name, cls.find_similar_contain_name, cls.find_similar_belong_name]:
            data_name = method( columns, data_id )
            if data_name:
                datas = cls._connect.get_databank_by_column('databank_'+data_type, data_name)
                if mutation:
                    datas += cls._connect.get_databank_by_column('databank_'+data_type, data_name, 1)
                return datas
        return None

    @classmethod
    def find_similar_equal_name(cls, columns, data_id):
        for column in columns:
            if column and u''.join(data_id.lower().split()) == u''.join(column.lower().split()):
                return column
        return ''

    @classmethod
    def find_similar_contain_name(cls, columns, data_id):
        for column in columns:
            if column and u''.join(data_id.lower().split()) in u''.join(column.lower().split()):
                return column
        return ''

    @classmethod
    def find_similar_belong_name(cls, columns, data_id):
        for column in columns:
            if column and u''.join(column.lower().split()) in u''.join(data_id.lower().split()):
                return column
        return ''

    @classmethod
    def get_mutation_data_set(cls, data_type, mode):
        for table in ['value_mutation', 'number_mutation']:
            columns = cls._connect.get_all_column_names(table)
            type_column = cls.find_similar_equal_name(columns, data_type)
            if type_column:
                #list of (info, value)
                datas = cls._connect.get_mutation_by_column(table, data_type, mode)
                return datas
        return None


