"""Handles Phone Call Logs"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import base

import struct
from datetime import datetime

class Phonecall(base.IPDRecord):
	#Possible attributes; I got a couple of calls without a number
	calltime = None
	number = None
	duration = None
	direction = None
	disposition = None

	def __repr__(self):
		return u'<Phonecall: Direction: %s, Disposition: %s, Number: %s, Timestamp: %s>' % (self.direction, self.disposition, self.number, self.calltime)

	def decode(self):
		self.names = []
		for field in self.fields:
			if field['type'] == 4:
				#timestamp, similar to SMS
				self.calltime = datetime.fromtimestamp(struct.unpack('Q', field['data'])[0] / 1000)
			elif field['type'] == 12:
				#phone number, includes a null at the end
				self.number = field['data'][:-1]
			elif field['type'] == 3:
				#duration (in seconds)
				self.duration = struct.unpack('L', field['data'])[0]
			elif field['type'] == 31:
				#name from address book
				self.names += [field['data'][:-1],]
			elif field['type'] == 2:
				#direction
				direction = ord(field['data'][0])
				if direction == 0:
					self.direction = 'In'
				elif direction == 1:
					self.direction = 'Out'
				elif direction == 2:
					self.direction = 'Missed'
				elif direction == 3:
					self.direction = 'Missed'
				elif direction == 4:
					self.direction = 'Conference'
				else:
					self.direction = 'Unknown - %d' % direction
			elif field['type'] == 6:
				#failure code
				failcode = ord(field['data'][0])
				if failcode == 0:
					self.disposition = 'Success'
				elif failcode == 3:
					self.disposition = 'Radio Path Unavailable'
				elif failcode == 9:
					self.disposition = 'Call Failed'
				else:
					self.disposition = 'Unknown - %d' % failcode

DBRELATION = ('Phone Call Logs', Phonecall)
