#!/bin/env python

import sys
import struct
import os.path
import time

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
#print numdb, "databases found"

databases = {}

#find database names
for i in range(0,numdb):
	namelen = struct.unpack("h", file.read(2))
	databases[i] = file.read(namelen[0])[:-1]

print databases

records = ()

while file.tell() < (filesize - 1):
	record = {}
	record['dbid'] = struct.unpack("H", file.read(2))[0]
	rlength = struct.unpack("L", file.read(4))[0]
	temptell = file.tell()
	file.seek(file.tell() + 1)
	record['handle'] = struct.unpack("H", file.read(2))[0]
	record['uid'] = struct.unpack("L", file.read(4))[0]
	record['fields'] = ()
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
				received = 0
				sent = 0
				for i in range(13, 20):
					received += ord(field['data'][i]) << ((i - 13) * 8)
				for i in range(21, 28):
					sent += ord(field['data'][i]) << ((i - 21) * 8)
				#this is really horrible, but for some reason everything is shifted 3 decimals to the left
				received = int(str(received)[:-3])
				sent = int(str(sent)[:-3])
				print 'received:	', time.ctime(received)
				print 'sent:		', time.ctime(sent)
			#contents of the message
			if field['type'] == 4:
				print 'text:		', field['data']
			#phone number either sent to or received from
			if field['type'] == 2:
				print 'number:		', field['data']
			#hack to figure out if it was sent or received
			if field['type'] == 7:
				if ord(field['data'][1]) == 0:
					print 'direction:	out'
				else:
					print 'direction:	in'
	records += ((record,))

for record in records:
	if record['dbid'] == find_key(databases, 'SMS Messages'):
		print databases[record['dbid']]
		print " Handle:", record['handle']
		print " UID:", record['uid']
		for field in record['fields']:
			print "	Type:", field['type']
			print "	Data:", field['data']
			print "		Hex:", print_hex(field['data'])
