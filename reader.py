#!/bin/env python

#Copyright 2010, Logan Rojas
#License: Simplified BSD

from __future__ import division
import sys
import struct
import os.path
import time
from models import addressbook, sms, phonecall, message

def find_key(dic, val):
	try:
		return [k for k, v in dic.iteritems() if v == val][0]
	except IndexError:
		return False

def print_hex(str):
	hexd = ''
	for char in str:
		hexd += "%#x " % ord(char)
	return hexd

class Reader(object):
	"""Makes a Reader object

	whatever = Reader(<file object>, <progress bool>)

	file is a file object, obviously
	progress is a bool that tells it whether or not to draw a progress bar"""

	def __init__(self, file, progress):
		print 'Processing file:', file.name
		self.filename = file.name
		filesize = os.path.getsize(file.name)

		if progress:
			from progressbar import progressbar
			pbar = progressbar.ProgressBar()

		#data begins 0x28 bytes in
		file.seek(0x28)

		#figure out the number of databases
		numdb = struct.unpack('h', file.read(2))[0]

		self.databases = {}

		#find database names
		for i in range(0,numdb):
			namelen = struct.unpack("h", file.read(2))
			self.databases[i] = file.read(namelen[0])[:-1]

		self.records = ()
		self.SMSs = []
		self.Calls = []
		self.ABooks = []
		self.Messages = []

		#Go the the file stopping at each record
		while file.tell() < (filesize - 1):
			record = {}
			record['dbid'] = struct.unpack("H", file.read(2))[0]
			rlength = struct.unpack("L", file.read(4))[0]
			temptell = file.tell()
			file.seek(1,1)
			record['handle'] = struct.unpack("H", file.read(2))[0]
			record['uid'] = struct.unpack("L", file.read(4))[0]
			record['fields'] = ()
			while file.tell() < (temptell + rlength) and file.tell() < filesize:
				field = {}
				flength = struct.unpack("H", file.read(2))[0]
				field['type'] = struct.unpack("b", file.read(1))[0]
				field['data'] = file.read(flength)
				record['fields'] += ((field),)

				if record['dbid'] == find_key(self.databases, 'Address Book - All') and field['type'] == 10:
					#luckily, this is the only field type we're concerned with
					self.ABooks.append(addressbook.ABook(field['data'], record['uid'], record['handle']))

			#orphaned records
			if record['dbid'] == 65535:
				continue

			self.records += (record,)
			if record['dbid'] == find_key(self.databases, 'Phone Call Logs'):
				self.Calls.append(phonecall.Phonecall(record['fields'], record['uid'], record['handle']))
			if record['dbid'] == find_key(self.databases, 'SMS Messages'):
				self.SMSs.append(sms.SMS(record['fields'], record['uid'], record['handle']))
			if record['dbid'] == find_key(self.databases, 'Messages'):
				self.Messages.append(message.Message(record['fields'], record['uid'], record['handle']))

			#display a nifty progress bar, if they ask for it
			if progress:
				pbar.render(int(file.tell() / filesize * 100), "\nDatabase: %s" % (self.databases[record['dbid']]))

	def __repr__(self):
		return '<Reader %s: "%s">' % (id(self), self.filename)
