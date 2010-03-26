#!/bin/env python

import sys
import struct
import os.path
import time
from models import addressbook

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
SMSs = ()
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
	if record['dbid'] == find_key(databases, 'SMS Messages'):
		SMS = {'uid': record['uid'], 'handle': record['handle'], 'sent': 0, 'received': 0, 'text': '', 'number': '', 'direction': ''}
	if record['dbid'] == find_key(databases, 'Phone Call Logs'):
		Call = {'uid': record['uid'], 'handle': record['handle'], 'time': 0, 'number': '', 'name': '', 'names': [], 'direction': '', 'duration': 0, 'disposition': ''}
	while file.tell() < (temptell + rlength) and file.tell() < filesize:
		field = {}
		flength = struct.unpack("H", file.read(2))[0]
		field['type'] = struct.unpack("b", file.read(1))[0]
		field['data'] = file.read(flength)
		record['fields'] += ((field),)

		#handle SMS messages
		if record['dbid'] == find_key(databases, 'SMS Messages'):
			#date field, unix timestamp
			if field['type'] == 1:
				received = struct.unpack('Q', field['data'][13:21])[0] / 1000
				sent = struct.unpack('Q', field['data'][21:29])[0] / 1000
				SMS['received'] = received
				SMS['sent'] = sent
			#contents of the message
			if field['type'] == 4:
				SMS['text'] = field['data'].strip("\x00\x03")
			#phone number either sent to or received from
			if field['type'] == 2:
				SMS['number'] = field['data'].strip("\x00\x03")
			#hack to figure out if it was sent or received
			if field['type'] == 7:
				if ord(field['data'][1]) == 0:
					SMS['direction'] = 'out'
				else:
					SMS['direction'] = 'in'
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
	if 'SMS' in globals():
		SMS['uid'] = record['uid']
		SMS['handle'] = record['handle']
		SMSs += (SMS,)
		del SMS
	if 'Call' in globals():
		Call['uid'] = record['uid']
		Call['handle'] = record['handle']
		if not Call['number']:
			Call['number'] = 'restricted'
		Call['name'] = ' '.join(Call['names'])
		Calls += (Call,)
		del Call

#for record in records:
#	if record['dbid'] == find_key(databases, 'Phone Call Logs'):
#		print databases[record['dbid']]
#		print " Handle:", record['handle']
#		print " UID:", record['uid']
#		for field in record['fields']:
#			print "	Type:", field['type']
#			print "	Data:", field['data']
#			if field['type'] == 4:
#				print struct.unpack('Q', field['data'])[0]
#			print "		Hex:", print_hex(field['data'])

for SMS in SMSs:
	print SMS['handle'], '-', SMS['uid']
	print '	Direction:', SMS['direction']
	if SMS['direction'] == 'out':
		print '	To:', SMS['number']
	else:
		print '	From:', SMS['number']
	print '	Sent:', time.ctime(SMS['sent'])
	print '	Text:', SMS['text']

for Call in Calls:
	print Call['handle'], '-', Call['uid']
	print '	Date and Time:	', time.ctime(Call['time'])
	print '	Direction:	', Call['direction']
	print '	Disposition:	', Call['disposition']
	print '	Duration:	', Call['duration']
	print '	Number:		', Call['number']
	print '	Name:		', Call['name']
