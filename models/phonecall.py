"""Handles Phone Call Logs"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import struct
from datetime import datetime

class Phonecall(object):
	def __init__(self, fields, uid, handle):

		self.uid = uid
		self.handle = handle
		self.fields = fields
		self.decode()

	def decode(self):
		self.names = []
		for field in self.fields:
			if field['type'] == 4:
				#timestamp, similar to SMS
				self.calltime = datetime.fromtimestamp(struct.unpack('Q', field['data'])[0] / 1000)
			if field['type'] == 12:
				#phone number, includes a null at the end
				self.number = field['data'][:-1]
			if field['type'] == 31:
				#name from address book
				self.names += [field['data'][:-1],]
			if field['type'] == 2:
				#direction
				direction = ord(field['data'][0])
				if direction == 0:
					self.direction = 'in'
				elif direction == 1:
					self.direction = 'out'
				elif direction == 2:
					self.direction = 'missed'
				elif direction == 3:
					self.direction = 'missed'
				elif direction == 4:
					self.direction = 'conference'
				else:
					self.direction = 'unknown - %d' % direction
			if field['type'] == 3:
				#duration (in seconds)
				self.duration = struct.unpack('L', field['data'])[0]
			if field['type'] == 6:
				#failure code
				failcode = ord(field['data'][0])
				if failcode == 0:
					self.disposition = 'Success'
				elif failcode == 3:
					self.disposition = 'Radio Path Unavailable'
				elif failcode == 9:
					self.disposition = 'Call Failed'
				else:
					self.disposition = 'unknown - %d' % failcode
