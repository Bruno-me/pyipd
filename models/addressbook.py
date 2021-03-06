"""Handles importing Address Book records"""

#Copyright 2010, Logan Rojas
#License: Simplified BSD

import base

import cStringIO
import struct

fieldtypes = {
	0x37: 'title',
	0x21: 'company',
	0x2a: 'job_title',
	0x01: 'email',
	0x06: 'work',
	0x10: 'work2',
	0x07: 'home',
	0x11: 'home2',
	0x08: 'mobile',
	0x09: 'pager',
	0x03: 'fax',
	0x12: 'other',
	0x0a: 'pin',
	0x23: 'work_address_1',
	0x24: 'work_address_2',
	0x26: 'work_city',
	0x27: 'work_state',
	0x28: 'work_zip',
	0x29: 'work_country',
	0x3d: 'home_address_1',
	0x3e: 'home_address_2',
	0x45: 'home_city',
	0x46: 'home_state',
	0x47: 'home_zip',
	0x48: 'home_country',
	0x52: 'birthday',
	0x53: 'anniversary',
	0x36: 'web_site',
	0x41: 'user_1',
	0x42: 'user_2',
	0x43: 'user_3',
	0x44: 'user_4',
	0x40: 'notes',
	0x4d: 'picture',
	0x64: 'facebook',
	0x3b: 'categories',
}

class ABook(base.IPDRecord):
	def __repr__(self):
		return u'<ABook: "%s %s">' % (self.first_name, self.last_name)

	def decode(self):
		"""Pull out the data and decode it using the decodeabook() method"""
		try:
			data = [field['data'] for field in self.fields if field['type'] == 10][0]
		except IndexError:
			return False
		self.data = cStringIO.StringIO(data)
		self.datalen = len(data)
		self.decodeabook()

	def decodeabook(self):
		"""Read through the data and extract the fields listed above"""
		#ensure the cursor is at the beginning of the data
		self.data.seek(0)
		#First name first
		#length of first name, plus 0x20 at beginning
		length = ord(self.data.read(1))
		#advance past a null
		self.data.seek(1,1)
		self.first_name = self.data.read(length).strip()
		#when the field is empty it's 0xFF 7 times
		if self.first_name == (chr(0xff) * 7):
			self.first_name = ''
		self.data.seek(1,1)

		#length of last name, plus 0x20 at beginning
		length = ord(self.data.read(1))
		self.data.seek(1,1)
		self.last_name = self.data.read(length).strip()
		#when last name is empty it's 0xFF 7 times
		if self.last_name == 'T' + (chr(0xff) * 7):
			#blank lastname
			self.last_name = ''
		if self.last_name and self.last_name[0] == '7':
			#for whatever reason when the first character of the last name is '7', the names are reversed
			first_temp = self.first_name
			self.first_name = self.last_name[1:]
			self.last_name = first_temp

		self.data.seek(1,1)

		while self.data.tell() < self.datalen - 1:
			length = struct.unpack('H', self.data.read(2))[0]
			field = ord(self.data.read(1))
			data = self.data.read(length)[:-1]
			if field in fieldtypes:
				setattr(self, fieldtypes[field], data)

class OldABook(base.IPDRecord):
	"""Address book format for pre-os 4.5 (?)"""
	def __repr__(self):
		return u'<OldABook: "%s">' % ' '.join(self.names)

	def decode(self):
		self.names = []
		for field in self.fields:
			if field['type'] == 32:
				self.names.append(field['data'][:-1])
			if field['type'] == 6:
				self.work = field['data'][:-1]
			if field['type'] == 7:
				self.home = field['data'][:-1]
			if field['type'] == 8:
				self.mobile = field['data'][:-1]
			if field['type'] == 33:
				self.company = field['data'][:-1]
			if field['type'] == 1:
				self.email = field['data'][:-1]
			if field['type'] == 42:
				self.title = field['data'][:-1]
			if field['type'] == 61:
				self.home_address_1 = field['data'][:-1]
			if field['type'] == 69:
				self.home_city = field['data'][:-1]
			if field['type'] == 70:
				self.home_state = field['data'][:-1]
			if field['type'] == 71:
				self.home_zip = field['data'][:-1]
			if field['type'] == 54:
				self.web_site = field['data'][:-1]

DBRELATIONS = [
	('Address Book - All', ABook),
	('Address Book', OldABook),
]
