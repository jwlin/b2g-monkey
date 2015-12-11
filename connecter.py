import MySQLdb
import logging

class mysqlConnect:
	def __init__(self, host, user, password, databank):
		self.host = host
		self.user = user
		self.password = password
		self.databank = databank

	def get_submit_by_id(self, submit_id):
		sql = "SELECT * FROM webtesting WHERE id = %s" % ( submit_id )
		logging.info(str(self))
		logging.info(sql)

		self.connect = MySQLdb.connect(self.host, self.user, self.password, self.databank)
		self.cursor = self.connect.cursor()
		self.cursor.execute(sql)
		self.connect.close()
		self.data = self.cursor.fetchone()
		#data [0]id, [1]url, [2]deep, [3]time
		return self.data[1], self.data[2], self.data[3]

	def get_all_inputs_by_id(self, submit_id):
		sql = "SELECT * FROM inputtable WHERE id = %s" % ( submit_id )
		logging.info(str(self))
		logging.info(sql)

		self.connect = MySQLdb.connect(self.host, self.user, self.password, self.databank)
		self.cursor = self.connect.cursor()
		self.cursor.execute(sql)
		self.connect.close()
		return self.cursor.fetchall()

	def get_all_column_names(self, table):
		sql = "SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = %s" % (table)
		logging.info(str(self))
		logging.info(sql)

		self.connect = MySQLdb.connect(self.host, self.user, self.password, self.databank)
		self.cursor = self.connect.cursor()
		self.cursor.execute(sql)
		self.connect.close()
		#type = tuple of tuple
		return [ data[0] if type(data)==type(tuple()) else str(data) for data in self.cursor.fetchall() ]


	def get_databank_by_column(self, table, column, mode=0):
		sql = "SELECT %s FROM %s WHERE MODE = %d" % ( colmun, table , mode)
		logging.info(str(self))
		logging.info(sql)

		self.connect = MySQLdb.connect(self.host, self.user, self.password, self.databank)
		self.cursor = self.connect.cursor()
		self.cursor.execute(sql)
		self.connect.close()
		#type = tuple of tuple
		return [ data[0] if type(data)==type(tuple()) else str(data) for data in self.cursor.fetchall() ]

	def __str__(self):
		return "connect to Mysql: host(%s) user(%s) password(%s) databank(%s)" % ( self.host, self.user, self.password, self.databank )


