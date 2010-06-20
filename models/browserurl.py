"""Handles 'Browser Urls' database, just the url, no timestamp or anything"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import base

import struct
from datetime import datetime

class BrowserURL(base.IPDRecord):
	def __repr__(self):
		return u'<BrowserURL: %s>' % (self.url)

	def decode(self):
		for field in self.fields:
			if field['type'] == 25:
				#memo contents with null at the end
				self.url = field['data'][3:]

DBRELATIONS = [
	('Browser Urls', BrowserURL),
]
