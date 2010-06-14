"""Handles Memos"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import base

import struct
from datetime import datetime

class Memo(base.IPDRecord):
	def __repr__(self):
		return u'<Memo: %s>' % (self.title)

	def decode(self):
		for field in self.fields:
			if field['type'] == 1:
				#memo title with a null at the end
				self.title = field['data'][:-1]
			elif field['type'] == 2:
				#memo contents with null at the end
				self.text = field['data'][:-1]
