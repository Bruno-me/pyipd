"""Base class for IPD database records"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

class IPDRecord(object):
	def __init__(self, record):
		self.record = record
		self.uid = record['uid']
		self.handle = record['handle']
		self.fields = record['fields']
		self.decode()

	def __repr__(self):
		return u'<IPDRecord: uid:%d handle:%d>' % (self.uid, self.handle)

	def decode(self):
		raise NotImplementedError("Subclass must implement abstract method")
