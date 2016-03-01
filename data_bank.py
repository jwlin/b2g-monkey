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

#=============================================================================================================
# Get data set from mysqldb
#=============================================================================================================
class MysqlDataBank(DataBank):
    @classmethod
    def __init__(cls, host, user, password, db):
        cls._connect = mysqlConnect(host, user, password, db)

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
    def get_data(cls, data_type, data_id):
        if not ('data_'+data_type) in cls._connect.get_all_table_names():
            return None

        data_name = ''
        columns = cls._connect.get_databank_by_column('data_'+data_type, 'name')
        for column in columns:
            if column and u''.join(data_id.lower().split()) == u''.join(column.lower().split()):
                data_name = column
                break
        else :
            for column in columns:
                if column and u''.join(data_id.lower().split()) in u''.join(column.lower().split()):
                    data_name = column
                    break
            else :
                for column in columns:  
                    if column and u''.join(column.lower().split()) in u''.join(data_id.lower().split()):
                        data_name = column
                        break
                else :
                    return None

        datas = cls._connect.get_databank_by_row('data_'+data_type, 'name', data_name )
        return datas[1:]

    @classmethod
    def get_mutation_data_set(cls, data_type, data_id, modes):
        columns = cls._connect.get_mutation_catalog()

        table_name = ''
        for row in columns:
            if row[0] and row[1] and u''.join(data_id.lower().split()) == u''.join(row[0].lower().split()):
                table_name = row[1]
                break
        else:
            for row in columns:
                if row[0] and row[1] and u''.join(data_id.lower().split()) in u''.join(row[0].lower().split()):
                    table_name = row[1]
                    break
            else:
                for row in columns:
                    if row[0] and row[1] and u''.join(row[0].lower().split()) in u''.join(data_id.lower().split()):
                        table_name = row[1]
                        break
                else:
                    for row in columns:
                        if row[0] and row[1] and u''.join(data_type.lower().split()) == u''.join(row[0].lower().split()):
                            table_name = row[1]
                            break
                    else:
                        table_name = "mutation_text"

        mutation_values = cls._connect.get_mutation_values(table_name, modes)
        return mutation_values

