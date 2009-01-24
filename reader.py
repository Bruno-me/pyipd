#!/bin/env python

import sys
import struct
import os.path
import time

def find_key(dic, val):
	return [k for k, v in dic.iteritems() if v == val][0]

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
		if record['dbid'] == find_key(databases, 'SMS Messages') and field['type'] == 1:
			received = 0
			sent = 0
			for i in range(13, 20):
				temp = ord(field['data'][i])
				received += temp << ((i - 13) * 8)
			for i in range(21, 28):
				temp = ord(field['data'][i])
				#print 'Temp:	', temp
				sent += temp << ((i - 21) * 8)
			received = int(str(received)[:-3])
			sent = int(str(sent)[:-3])
			print 'received:	', time.ctime(received)
			print 'sent:		', time.ctime(sent)
		if record['dbid'] == find_key(databases, 'SMS Messages') and field['type'] == 4:
			print 'text:		', field['data']
	records += ((record,))

for record in records:
	print databases[record['dbid']]
	print " Handle:", record['handle']
	print " UID:", record['uid']
	for field in record['fields']:
		print "	Type:", field['type']
		print "	Data:", field['data']
