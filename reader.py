#!/bin/env python

#Copyright 2010, Logan Rojas
#License: Simplified BSD

from __future__ import division
import sys
import struct
import os.path
import time

import models

def find_key(dic, val):
	try:
		return [k for k, v in dic.iteritems() if v == val][0]
	except IndexError:
		return False

class IPDFileError(Exception):
	pass

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

		identifier = file.read(0x25)
		if identifier != 'Inter@ctive Pager Backup/Restore File':
			raise IPDFileError("Doesn't look like a IPD file")

		#seek past a 0x0A
		file.seek(1,1)

		fileversion = struct.unpack('b', file.read(1))[0]
		if fileversion != 2:
			raise IPDFileError('File version not 2, we only know about version 2')

		file.seek(1,1)

		#figure out the number of databases
		numdb = struct.unpack('h', file.read(2))[0]

		self.databases = {}

		#find database names
		for i in range(0,numdb):
			namelen = struct.unpack("h", file.read(2))[0]
			self.databases[i] = file.read(namelen)[:-1]

		self.records = []
		self.SMSs = []
		self.Calls = []
		self.ABooks = []
		self.Messages = []
		self.Memos = []

		#Go the the file stopping at each record
		while file.tell() < (filesize - 1):
			record = {}
			#database ID, corresponds to self.databases above
			record['dbid'] = struct.unpack("H", file.read(2))[0]

			#record length, and the position of the beginning of the record
			rlength = struct.unpack("L", file.read(4))[0]
			rbeginning = file.tell()

			#record metadata
			record['dbversion'] = struct.unpack('B', file.read(1))[0]
			record['handle'] = struct.unpack("H", file.read(2))[0]
			record['uid'] = struct.unpack("L", file.read(4))[0]
			record['fields'] = []

			#loop through the record and read all of the fields
			while file.tell() < (rbeginning + rlength) and file.tell() < filesize:
				field = {}
				flength = struct.unpack("H", file.read(2))[0]
				field['type'] = struct.unpack("B", file.read(1))[0]
				field['data'] = file.read(flength)
				record['fields'].append(field)

			#orphaned records
			if record['dbid'] == 65535:
				continue

			self.records.append(record)

			#parse out different record types
			#TODO: replace this will some sort of registration system where you
			# specify a database name and class to put it into
			if record['dbid'] == find_key(self.databases, 'Address Book - All'):
				self.ABooks.append(models.addressbook.ABook(record))
			if record['dbid'] == find_key(self.databases, 'Phone Call Logs'):
				self.Calls.append(models.phonecall.Phonecall(record))
			if record['dbid'] == find_key(self.databases, 'SMS Messages'):
				self.SMSs.append(models.sms.SMS(record))
			if record['dbid'] == find_key(self.databases, 'Messages'):
				self.Messages.append(models.message.Message(record))
			if record['dbid'] == find_key(self.databases, 'Memos'):
				self.Memos.append(models.memo.Memo(record))

			#display a nifty progress bar, if they ask for it
			if progress:
				pbar.render(int(file.tell() / filesize * 100), "\nDatabase: %s" % (self.databases[record['dbid']]))

	def __repr__(self):
		return '<Reader %s: "%s">' % (id(self), self.filename)
