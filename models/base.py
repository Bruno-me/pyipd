"""Base class for IPD database records"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

class IPDRecord(object):
	uid = None
	handle = None
	Fields = None

	def __init__(self, fields, uid, handle):
		self.uid = uid
		self.handle = handle
		self.fields = fields
		self.decode()

	def __repr__(self):
		return u'<IPDRecord: uid:%d handle:%d>' % (self.uid, self.handle)

	def decode(self):
		raise NotImplementedError("Subclass must implement abstract method")
