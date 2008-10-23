#!/bin/env python

import sys
import struct
import os.path

filename = sys.argv[1]
file = open(filename, "rb")
filesize = os.path.getsize(filename)

#data begins 0x28 bytes in
file.seek(0x28)

#figure out the number of databases
numdb = struct.unpack('h', file.read(2))[0]
print numdb, "databases found"

databases = {}

#find database names
for i in range(0,numdb):
	namelen = struct.unpack("h", file.read(2))
	databases[i] = file.read(namelen[0])[:-1]

#print databases

records = ()

while file.tell() < filesize:
	record = {}
	record['dbid'] = struct.unpack("h", file.read(2))[0]
	rlength = struct.unpack("L", file.read(4))[0]
	temptell = file.tell()
	file.seek(file.tell() + 1)
	record['handle'] = struct.unpack("h", file.read(2))[0]
	record['uid'] = struct.unpack("L", file.read(4))[0]
	#fields = file.read(rlength - 7)
	record['fields'] = ()
	while file.tell() < (temptell + rlength):
		field = {}
		flength = struct.unpack("h", file.read(2))[0]
		field['type'] = struct.unpack("b", file.read(1))[0]
		field['data'] = file.read(flength)
		record['fields'] += ((field),)
	records += ((record,))

print records
