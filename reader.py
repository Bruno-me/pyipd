#!/bin/env python

import sys
import struct
import os.path
import time
from models import addressbook, sms

def find_key(dic, val):
	return [k for k, v in dic.iteritems() if v == val][0]

def print_hex(str):
	hexd = ''
	for char in str:
		hexd += "%#x " % ord(char)
	return hexd

filename = sys.argv[1]
file = open(filename, "rb")
filesize = os.path.getsize(filename)

#data begins 0x28 bytes in
file.seek(0x28)

#figure out the number of databases
numdb = struct.unpack('h', file.read(2))[0]

databases = {}

#find database names
for i in range(0,numdb):
	namelen = struct.unpack("h", file.read(2))
	databases[i] = file.read(namelen[0])[:-1]

print databases

records = ()
SMSs = []
Calls = ()
ABooks = []

#Go the the file stopping at each record
while file.tell() < (filesize - 1):
	record = {}
	record['dbid'] = struct.unpack("H", file.read(2))[0]
	rlength = struct.unpack("L", file.read(4))[0]
	temptell = file.tell()
	file.seek(file.tell() + 1)
	record['handle'] = struct.unpack("H", file.read(2))[0]
	record['uid'] = struct.unpack("L", file.read(4))[0]
	record['fields'] = ()
	if record['dbid'] == find_key(databases, 'Phone Call Logs'):
		Call = {'uid': record['uid'], 'handle': record['handle'], 'time': 0, 'number': '', 'name': '', 'names': [], 'direction': '', 'duration': 0, 'disposition': ''}
	while file.tell() < (temptell + rlength) and file.tell() < filesize:
		field = {}
		flength = struct.unpack("H", file.read(2))[0]
		field['type'] = struct.unpack("b", file.read(1))[0]
		field['data'] = file.read(flength)
		record['fields'] += ((field),)

		if record['dbid'] == find_key(databases, 'Phone Call Logs'):
			#timestamp, similar to SMS
			if field['type'] == 4:
				calltime = struct.unpack('Q', field['data'])[0]
				Call['time'] = int(str(calltime)[:-3])
			#phone number
			if field['type'] == 12:
				Call['number'] = field['data'][:-1]
			#name from address book
			if field['type'] == 31:
				Call['names'] += [field['data'][:-1],]
			#direction
			if field['type'] == 2:
				direction = ord(field['data'][0])
				if direction == 0:
					Call['direction'] = 'in'
				elif direction == 1:
					Call['direction'] = 'out'
				elif direction == 2:
					Call['direction'] = 'missed'
				elif direction == 3:
					Call['direction'] = 'missed'
				elif direction == 4:
					Call['direction'] = 'conference'
				else:
					Call['direction'] = 'unknown - %d' % direction
			#duration (in seconds)
			if field['type'] == 3:
				Call['duration'] = struct.unpack('L', field['data'])[0]
			#failure code
			if field['type'] == 6:
				failcode = ord(field['data'][0])
				if failcode == 0:
					Call['disposition'] = 'Success'
				elif failcode == 3:
					Call['disposition'] = 'Radio Path Unavailable'
				elif failcode == 9:
					Call['disposition'] = 'Call Failed'
				else:
					Call['disposition'] = 'unknown - %d' % failcode
		if record['dbid'] == find_key(databases, 'Address Book - All') and field['type'] == 10:
			#luckily, this is the only field type we're concerned with
			ABooks.append(addressbook.ABook(field['data'], record['uid'], record['handle']))
	records += (record,)
	if record['dbid'] == find_key(databases, 'SMS Messages'):
		SMSs.append(sms.SMS(record['fields'], record['uid'], record['handle']))
	if 'Call' in globals():
		Call['uid'] = record['uid']
		Call['handle'] = record['handle']
		if not Call['number']:
			Call['number'] = 'restricted'
		Call['name'] = ' '.join(Call['names'])
		Calls += (Call,)
		del Call
