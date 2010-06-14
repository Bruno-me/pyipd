"""Handles SMS Text messages"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import base

import struct
from datetime import datetime

class SMS(base.IPDRecord):
	def __repr__(self):
		return u'<SMS Message: Direction: %s, Number: %s, Sent: %s Text: %s>' % (self.direction, self.number, self.sent, self.text)

	def decode(self):
		for field in self.fields:
			if field['type'] == 1:
				#date field, stored as unix timestamp
				self.received = datetime.fromtimestamp(struct.unpack('Q', field['data'][13:21])[0] / 1000)
				self.sent = datetime.fromtimestamp(struct.unpack('Q', field['data'][21:29])[0] / 1000)
			if field['type'] == 4:
				#contents of the message
				self.text = field['data'].strip("\x00\x03")
			if field['type'] == 2:
				#phone number either sent to or received from
				self.number = field['data'].strip("\x00\x03")
			if field['type'] == 7:
				#direction
				if ord(field['data'][1]) == 0:
					self.direction = 'out'
				else:
					self.direction = 'in'
