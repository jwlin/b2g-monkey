import MySQLdb

class mysqlConnect:
	def __init__(self, host, user, password, databank):
		self.host = host
		self.user = user
		self.password = password
		self.databank = databank

	def get_submit_by_id(self, _id):
		self.connect = MySQLdb.connect(self.host, self.user, self.password, self.databank)
		self.cursor = self.connect.cursor()
		self.cursor.execute("SELECT * FROM webtesting WHERE id="+_id)
		self.connect.close()
		self.data = self.cursor.fetchone()
		#data [0]id, [1]url, [2]deep, [3]time
		return self.data[1], self.data[2], self.data[3]

	def get_all_inputs_by_id(self, _id):
		self.connect = MySQLdb.connect(self.host, self.user, self.password, self.databank)
		self.cursor = self.connect.cursor()
		self.cursor.execute("SELECT * FROM inputtable WHERE id="+_id)
		self.connect.close()
		return self.cursor.fetchall()
