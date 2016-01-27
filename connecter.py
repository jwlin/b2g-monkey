#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import logging
from abc import ABCMeta, abstractmethod

class mysqlConnect:
    @classmethod
    def __init__(cls, host, user, password, databank):
        cls.host = host
        cls.user = user
        cls.password = password
        cls.databank = databank
        #logging.info(str(cls))

    @classmethod
    def exec_sql(cls, sql):
        #logging.info(str(cls))
        #logging.info(sql)

        cls.connect = MySQLdb.connect(cls.host, cls.user, cls.password, cls.databank)
        cls.cursor = cls.connect.cursor()
        cls.cursor.execute(sql)
        cls.connect.close()

    @classmethod
    def get_submit_by_id(cls, submit_id):
        sql = "SELECT * FROM webtesting WHERE id = %s" % ( submit_id )
        logging.info(str(cls))
        logging.info(sql)

        cls.exec_sql(sql)
        cls.data = cls.cursor.fetchone()
        #data [0]id, [1]url, [2]deep, [3]time
        return cls.data[1], cls.data[2], cls.data[3]

    @classmethod
    def get_all_inputs_by_id(cls, submit_id):
        sql = "SELECT * FROM inputtable WHERE id = %s" % ( submit_id )
        cls.exec_sql(sql)
        return [ data[0] if type(data)==type(tuple()) else str(data) for data in cls.cursor.fetchall() ]

    @classmethod
    def get_all_table_names(cls):
    	sql = "SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA =  \'test\' "
        cls.exec_sql(sql)
        return [ data[0] if type(data)==type(tuple()) else str(data) for data in cls.cursor.fetchall() ]

    @classmethod
    def get_all_column_names(cls, table):
        sql = "SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = \'%s\'" % (table)
        cls.exec_sql(sql)
        #type = tuple of tuple
        return [ data[0] if type(data)==type(tuple()) else str(data) for data in cls.cursor.fetchall() ]

    @classmethod
    def get_databank_by_column(cls, table, column):
        sql = "SELECT %s FROM %s" % ( column, table )
        cls.exec_sql(sql)
        #type = tuple of tuple
        return [ data[0] if type(data)==type(tuple()) else str(data) for data in cls.cursor.fetchall() ]

    @classmethod
    def get_databank_by_row(cls, table, row_name, row_value ):
        sql = "SELECT * FROM %s WHERE %s = \'%s\' " % ( table, row_name, row_value )
        cls.exec_sql(sql)
        #type = tuple of tuple
        return list( cls.cursor.fetchall()[0] )

    #NOT USE
    @classmethod
    def get_mutation_by_column(cls, table, column, mode):
        sql = "SELECT info, %s FROM %s WHERE MODE = %d " % ( column, table , mode )
        cls.exec_sql(sql)
        #type = tuple of tuple
        return [ [data[0], data[1]] if type(data)==type(tuple()) else str(data) for data in cls.cursor.fetchall() ]

    @classmethod
    def get_mutation_catalog(cls):
        sql = "SELECT name, mutation_table FROM mutation_catalog "
        logging.info(str(cls))
        logging.info(sql)

        cls.exec_sql(sql)
        return [ [data[0], data[1]] if type(data)==type(tuple()) else str(data) for data in cls.cursor.fetchall() ]

    @classmethod
    def get_mutation_values(cls, table):
        sql = "SELECT info, value FROM %s " % ( table )
        logging.info(str(cls))
        logging.info(sql)

        cls.exec_sql(sql)
        return [ [data[0], data[1]] if type(data)==type(tuple()) else str(data) for data in cls.cursor.fetchall() ]

    @classmethod
    def __str__(cls):
        return "connect to Mysql: host(%s) user(%s) password(%s) databank(%s)" % ( cls.host, cls.user, cls.password, cls.databank )


